#!/usr/bin/env python3
"""
Forum Radar — scans Krafty IM Special Downloads, enriches courses with
value scoring, and generates a Notion-style interactive report.

Usage:
    python -m forum_radar.main              # scan + enrich + report
    python -m forum_radar.main --scan-only   # just scrape the forum
    python -m forum_radar.main --enrich-all  # re-enrich all unprocessed courses
    python -m forum_radar.main --prices      # lookup online prices for all courses
    python -m forum_radar.main --report      # generate report from existing data only
    python -m forum_radar.main --serve       # scan + report + open in browser
"""

import argparse
import logging
import webbrowser
from datetime import datetime, timedelta

from forum_radar.config import DB_PATH, REPORT_PATH
from forum_radar.database import CourseDB
from forum_radar.scraper import ForumScraper
from forum_radar.enricher import CourseEnricher
from forum_radar.reporter import build_report, write_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_scan(config):
    db = CourseDB(config.DB_PATH)
    scraper = ForumScraper(config)
    enricher = CourseEnricher(config)
    errors = []

    logger.info("Scanning forum listing...")
    threads = scraper.scan()
    logger.info(f"Found {len(threads)} threads across {config.MAX_PAGES_PER_SCAN} pages")

    new_count = 0
    enriched = []
    for thread in threads:
        if thread["is_sticky"]:
            continue

        thread["course_creator"] = ForumScraper.extract_creator(
            thread["title"]
        )

        is_new = db.upsert_course(thread)
        if is_new:
            new_count += 1
            try:
                logger.info(f"  + {thread['title'][:70]}")
                detail = scraper.scrape_thread(thread["url"])
                merged = {**thread, **detail}

                if not merged.get("course_creator"):
                    merged["course_creator"] = ForumScraper.extract_creator(
                        merged.get("title", ""),
                        merged.get("post_content", ""),
                        merged.get("homepage_url", ""),
                    )

                if thread.get("uploader_url"):
                    profile = scraper.scrape_author_profile(thread["uploader_url"])
                    merged.update(profile)

                db.upsert_course(merged)
                enrichment = enricher.enricher(merged)

                if enrichment.get("description_bullets"):
                    merged["description_bullets"] = enrichment["description_bullets"]

                db.update_enrichment(thread["thread_id"], enrichment)
                db.commit()
                enriched.append({**merged, **enrichment})
            except Exception as e:
                logger.warning(f"  ! Failed: {thread['title'][:50]}: {e}")
                errors.append(str(e))
        else:
            logger.debug(f"  - Skipping (seen): {thread['title'][:50]}")

    logger.info(f"New courses: {new_count}")
    db.log_scan(config.MAX_PAGES_PER_SCAN, len(threads), new_count,
                "; ".join(errors[:5]))
    db.commit()
    scraper.close()
    db.close()
    return enriched, new_count


def enrich_all(config):
    db = CourseDB(config.DB_PATH)
    enricher = CourseEnricher(config)

    courses = db.conn.execute(
        "SELECT * FROM courses WHERE value_tier = 'unscored' OR value_score = 0"
    ).fetchall()

    logger.info(f"Re-enriching {len(courses)} courses...")
    for course in courses:
        merged = dict(course)
        merged["course_creator"] = ForumScraper.extract_creator(
            merged.get("title", ""),
            merged.get("post_content", ""),
            merged.get("homepage_url", ""),
        )
        enrichment = enricher.enricher(merged)
        enrichment["course_creator"] = merged["course_creator"]
        db.update_enrichment(course["thread_id"], enrichment)
    db.commit()
    db.close()
    logger.info("Done.")


def lookup_prices(config):
    db = CourseDB(config.DB_PATH)
    scraper = ForumScraper(config)

    courses = [dict(r) for r in db.conn.execute(
        "SELECT * FROM courses WHERE online_price IS NULL OR online_price = 'NA'"
    ).fetchall()]

    logger.info(f"Looking up online prices for {len(courses)} courses...")
    for course in courses:
        title = course["title"]
        homepage = course.get("homepage_url", "") or ""

        result = scraper.lookup_online_price(title, homepage)
        if result.get("online_price") and result["online_price"] != "NA":
            db.update_enrichment(course["thread_id"], {
                "online_price": result["online_price"],
                "online_price_url": result.get("online_price_url", ""),
            })
            db.commit()
            logger.info(f"  ${result['online_price']}: {title[:60]}")
        else:
            db.update_enrichment(course["thread_id"], {
                "online_price": "NA",
                "online_price_url": "",
            })
            db.commit()

    scraper.close()
    db.close()
    logger.info("Price lookup complete.")


def build_report_from_db(config):
    db = CourseDB(config.DB_PATH)
    recent_scans = [dict(r) for r in db.get_recent_scans(3)]
    courses = [dict(r) for r in db.get_active()]
    stats = db.get_summary_stats()

    report = build_report(config, db, recent_scans, courses, stats)
    path = write_report(report, config.REPORT_PATH)
    logger.info(f"Report written: {path}")
    db.close()
    return path


def main():
    from forum_radar import config as cfg

    parser = argparse.ArgumentParser(description="Forum Radar Scanner")
    parser.add_argument("--scan-only", action="store_true", help="Only scrape listing")
    parser.add_argument("--enrich-all", action="store_true", help="Re-enrich unscored courses")
    parser.add_argument("--prices", action="store_true", help="Lookup online prices for all courses")
    parser.add_argument("--report", action="store_true", help="Generate report from existing data")
    parser.add_argument("--serve", action="store_true", help="Scan, report, open in browser")
    args = parser.parse_args()

    if args.scan_only:
        run_scan(cfg)
    elif args.enrich_all:
        enrich_all(cfg)
    elif args.prices:
        lookup_prices(cfg)
    elif args.report:
        path = build_report_from_db(cfg)
        print(f"\nReport: file://{path}")
    elif args.serve:
        run_scan(cfg)
        path = build_report_from_db(cfg)
        webbrowser.open(f"file://{path}")
        print(f"\nReport opened: file://{path}")
    else:
        run_scan(cfg)
        path = build_report_from_db(cfg)
        print(f"\nReport: file://{path}")


if __name__ == "__main__":
    main()
