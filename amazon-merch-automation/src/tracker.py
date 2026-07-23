"""
Tracker — SQLite-based sales + listing tracker with JSON export for dashboard.
Tracks every design from idea through listing to sales, so you know what converts.
"""

import sqlite3
import json
from datetime import datetime, date
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


DB_PATH = Path(__file__).parent.parent / "tracker" / "merch_tracker.db"


def get_db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS niches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            audience TEXT,
            competition TEXT,
            season TEXT,
            verdict TEXT,
            score INTEGER,
            discovered_at TEXT DEFAULT (datetime('now')),
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS designs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niche_id INTEGER REFERENCES niches(id),
            design_id TEXT UNIQUE,
            style TEXT,
            concept TEXT,
            color_palette TEXT,
            placement TEXT,
            ai_prompt TEXT,
            text_overlay TEXT,
            target_demo TEXT,
            estimated_ctr TEXT,
            image_path TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            design_id TEXT REFERENCES designs(design_id),
            asin TEXT UNIQUE,
            title TEXT,
            bullets TEXT,
            description TEXT,
            backend_terms TEXT,
            price REAL,
            status TEXT DEFAULT 'draft',
            published_at TEXT,
            url TEXT
        );

        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER REFERENCES listings(id),
            sale_date DATE NOT NULL,
            units INTEGER DEFAULT 1,
            revenue REAL,
            royalty REAL,
            source TEXT DEFAULT 'manual'
        );

        CREATE TABLE IF NOT EXISTS daily_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id INTEGER REFERENCES listings(id),
            snapshot_date DATE NOT NULL,
            bsr TEXT,
            rating REAL,
            review_count INTEGER,
            price REAL
        );

        CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date);
        CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status);
        CREATE INDEX IF NOT EXISTS idx_designs_niche ON designs(niche_id);
    """)
    conn.commit()
    conn.close()


class Tracker:
    def __init__(self):
        init_db()

    # --- NICHES ---

    def add_niche(self, name: str, audience: str = "", competition: str = "",
                  season: str = "", verdict: str = "", score: int = 0, notes: str = "") -> int:
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO niches (name, audience, competition, season, verdict, score, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (name, audience, competition, season, verdict, score, notes),
            )
            conn.commit()
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        except sqlite3.IntegrityError:
            return conn.execute("SELECT id FROM niches WHERE name = ?", (name,)).fetchone()[0]
        finally:
            conn.close()

    def update_niche_verdict(self, niche_id: int, verdict: str, score: int):
        conn = get_db()
        conn.execute("UPDATE niches SET verdict = ?, score = ? WHERE id = ?", (verdict, score, niche_id))
        conn.commit()
        conn.close()

    def get_active_niches(self) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM niches WHERE verdict IN ('ENTER', 'WATCH') ORDER BY score DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- DESIGNS ---

    def add_design(self, niche_id: int, design_id: str, style: str, concept: str,
                   color_palette: str, placement: str, ai_prompt: str,
                   text_overlay: str, target_demo: str, estimated_ctr: str,
                   image_path: str = "") -> int:
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO designs (niche_id, design_id, style, concept, color_palette,
                   placement, ai_prompt, text_overlay, target_demo, estimated_ctr, image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (niche_id, design_id, style, concept, color_palette, placement,
                 ai_prompt, text_overlay, target_demo, estimated_ctr, image_path),
            )
            conn.commit()
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        except sqlite3.IntegrityError:
            return conn.execute(
                "SELECT id FROM designs WHERE design_id = ?", (design_id,)
            ).fetchone()[0]
        finally:
            conn.close()

    # --- LISTINGS ---

    def add_listing(self, design_id: str, asin: str = "", title: str = "",
                    bullets: str = "", description: str = "", backend_terms: str = "",
                    price: float = 19.99, url: str = "") -> int:
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO listings (design_id, asin, title, bullets, description,
                   backend_terms, price, url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (design_id, asin, title, bullets, description, backend_terms, price, url),
            )
            conn.commit()
            return conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        except sqlite3.IntegrityError:
            return conn.execute(
                "SELECT id FROM listings WHERE asin = ?", (asin,)
            ).fetchone()[0]
        finally:
            conn.close()

    def publish_listing(self, listing_id: int, asin: str, url: str):
        conn = get_db()
        conn.execute(
            """UPDATE listings SET status = 'published', asin = ?, url = ?,
               published_at = datetime('now') WHERE id = ?""",
            (asin, url, listing_id),
        )
        conn.commit()
        conn.close()

    def get_draft_listings(self) -> list[dict]:
        conn = get_db()
        rows = conn.execute("SELECT * FROM listings WHERE status = 'draft'").fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # --- SALES ---

    def record_sale(self, listing_id: int, units: int = 1, revenue: float = 0,
                    royalty: float = 0, sale_date: str = ""):
        if not sale_date:
            sale_date = date.today().isoformat()
        conn = get_db()
        conn.execute(
            """INSERT INTO sales (listing_id, sale_date, units, revenue, royalty)
               VALUES (?, ?, ?, ?, ?)""",
            (listing_id, sale_date, units, revenue, royalty),
        )
        conn.commit()
        conn.close()

    # --- SNAPSHOTS ---

    def take_snapshot(self, listing_id: int, bsr: str = "", rating: float = 0,
                      review_count: int = 0, price: float = 0):
        conn = get_db()
        conn.execute(
            """INSERT INTO daily_snapshots (listing_id, snapshot_date, bsr, rating, review_count, price)
               VALUES (?, date('now'), ?, ?, ?, ?)""",
            (listing_id, bsr, rating, review_count, price),
        )
        conn.commit()
        conn.close()

    # --- REPORTS ---

    def sales_summary(self, days: int = 30) -> dict:
        conn = get_db()
        row = conn.execute("""
            SELECT COUNT(*) as total_orders, COALESCE(SUM(units), 0) as total_units,
                   COALESCE(SUM(revenue), 0) as total_revenue,
                   COALESCE(SUM(royalty), 0) as total_royalty
            FROM sales WHERE sale_date >= date('now', ? || ' days')
        """, (f"-{days}",)).fetchone()
        conn.close()
        return dict(row)

    def sales_by_design(self, days: int = 30) -> list[dict]:
        conn = get_db()
        rows = conn.execute("""
            SELECT d.design_id, d.style, d.concept, d.estimated_ctr,
                   l.title, l.price, l.status,
                   COUNT(s.id) as orders, COALESCE(SUM(s.units), 0) as units_sold,
                   COALESCE(SUM(s.revenue), 0) as revenue,
                   COALESCE(SUM(s.royalty), 0) as royalty
            FROM designs d
            LEFT JOIN listings l ON l.design_id = d.design_id
            LEFT JOIN sales s ON s.listing_id = l.id
                AND s.sale_date >= date('now', ? || ' days')
            GROUP BY d.design_id
            ORDER BY revenue DESC
        """, (f"-{days}",)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def niche_performance(self) -> list[dict]:
        conn = get_db()
        rows = conn.execute("""
            SELECT n.name as niche, n.verdict, n.score,
                   COUNT(DISTINCT d.id) as designs,
                   COUNT(DISTINCT l.id) as listings,
                   COALESCE(SUM(s.units), 0) as total_units,
                   COALESCE(SUM(s.royalty), 0) as total_royalty
            FROM niches n
            LEFT JOIN designs d ON d.niche_id = n.id
            LEFT JOIN listings l ON l.design_id = d.design_id
            LEFT JOIN sales s ON s.listing_id = l.id
            GROUP BY n.id
            ORDER BY total_royalty DESC
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def export_dashboard_json(self) -> dict:
        """Export all data needed by the HTML dashboard as one JSON blob."""
        return {
            "generated_at": datetime.now().isoformat(),
            "sales_summary_30d": self.sales_summary(30),
            "sales_by_design": self.sales_by_design(30),
            "niche_performance": self.niche_performance(),
            "active_niches": self.get_active_niches(),
            "draft_listings": self.get_draft_listings(),
        }

    def export_json_file(self, filepath: str = ""):
        if not filepath:
            filepath = str(Path(__file__).parent.parent / "tracker" / "dashboard_data.json")
        data = self.export_dashboard_json()
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath


if __name__ == "__main__":
    t = Tracker()

    niche_id = t.add_niche("Funny Nurse Life", "Nurses 25-45", "medium", "evergreen", score=72)
    print(f"Added niche #{niche_id}")

    design_id = t.add_design(
        niche_id, "D001", "typography",
        "Bold distressed text 'Caffeine & Chaos' with stethoscope graphic",
        "#E74C3C #2C3E50 #FFFFFF", "center chest",
        "t-shirt design, bold typography, distressed text 'Caffeine & Chaos'",
        "Caffeine & Chaos", "Nurses, 25-45, female", "high",
    )
    print(f"Added design #{design_id}")

    listing_id = t.add_listing(
        "D001", "", "Caffeine & Chaos Funny Nurse T-Shirt - RN Life Tee",
        "Premium ringspun cotton|Bold distressed design|Perfect gift for nurses",
        "The perfect tee for the nurse who runs on espresso and determination.",
        "funny nurse gift rn life hospital humor medical field night shift",
        19.99,
    )
    print(f"Added listing #{listing_id}")

    t.record_sale(listing_id, units=2, revenue=39.98, royalty=7.96)
    print("Recorded sale")

    path = t.export_json_file()
    print(f"\nDashboard data exported to {path}")
    print(f"\n30-day summary: {json.dumps(t.sales_summary(30), indent=2)}")
