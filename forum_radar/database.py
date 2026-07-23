import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id INTEGER UNIQUE NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    course_creator TEXT,
    uploader TEXT,
    uploader_url TEXT,
    uploader_posts INTEGER DEFAULT 0,
    uploader_joined TEXT,
    uploader_reputation INTEGER DEFAULT 0,
    uploader_group TEXT,
    replies INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    rating REAL DEFAULT 0.0,
    rating_votes INTEGER DEFAULT 0,
    size TEXT,
    last_post_date TEXT,
    first_seen_date TEXT,
    date_detected TEXT NOT NULL,
    date_updated TEXT NOT NULL,

    post_content TEXT,
    description TEXT,
    homepage_url TEXT,
    download_links TEXT,
    advertised_price REAL DEFAULT 0.0,
    online_price TEXT DEFAULT 'NA',
    online_price_url TEXT,
    description_bullets TEXT,

    project_label TEXT,
    categories TEXT,
    value_tier TEXT DEFAULT 'unscored',
    value_score REAL DEFAULT 0.0,
    popularity_score REAL DEFAULT 0.0,
    edge_notes TEXT,
    recommendation TEXT,

    downloaded INTEGER DEFAULT 0,
    dismissed INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS scan_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_date TEXT NOT NULL,
    pages_scanned INTEGER DEFAULT 0,
    threads_found INTEGER DEFAULT 0,
    new_threads INTEGER DEFAULT 0,
    errors TEXT
);
"""


class CourseDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.executescript(SCHEMA)
        new_cols = ["course_creator", "uploader", "uploader_url", "uploader_posts",
                     "uploader_joined", "uploader_reputation", "uploader_group",
                     "online_price", "online_price_url", "description_bullets"]
        for col in new_cols:
            try:
                self.conn.execute(f"ALTER TABLE courses ADD COLUMN {col} TEXT")
            except sqlite3.OperationalError:
                pass
        try:
            self.conn.execute("ALTER TABLE courses ADD COLUMN online_price TEXT DEFAULT 'NA'")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def upsert_course(self, course: dict) -> bool:
        now = datetime.now().isoformat()
        existing = self.conn.execute(
            "SELECT id FROM courses WHERE thread_id = ?", (course["thread_id"],)
        ).fetchone()

        if existing:
            self.conn.execute(
                """UPDATE courses SET
                   title=?, url=?, course_creator=?, uploader=?, uploader_url=?,
                   uploader_posts=?, uploader_joined=?, uploader_reputation=?,
                   uploader_group=?, replies=?, views=?, rating=?, rating_votes=?,
                   size=?, last_post_date=?, first_seen_date=?, date_updated=?,
                   post_content=?, description=?, homepage_url=?, download_links=?,
                   advertised_price=?, online_price=?, online_price_url=?,
                   description_bullets=?, categories=?
                   WHERE thread_id=?""",
                (
                    course.get("title"), course.get("url"),
                    course.get("course_creator"),
                    course.get("uploader"), course.get("uploader_url"),
                    course.get("uploader_posts", 0), course.get("uploader_joined"),
                    course.get("uploader_reputation", 0), course.get("uploader_group"),
                    course.get("replies", 0), course.get("views", 0),
                    course.get("rating", 0.0), course.get("rating_votes", 0),
                    course.get("size"), course.get("last_post_date"),
                    course.get("first_seen_date"), now,
                    course.get("post_content"), course.get("description"),
                    course.get("homepage_url"), course.get("download_links"),
                    course.get("advertised_price", 0.0),
                    course.get("online_price", "NA"),
                    course.get("online_price_url"),
                    course.get("description_bullets"),
                    course.get("categories"),
                    course["thread_id"],
                ),
            )
            return False
        else:
            self.conn.execute(
                """INSERT INTO courses (
                   thread_id, title, url, course_creator, uploader, uploader_url,
                   uploader_posts, uploader_joined, uploader_reputation,
                   uploader_group, replies, views, rating, rating_votes, size,
                   last_post_date, first_seen_date, date_detected, date_updated,
                   post_content, description, homepage_url, download_links,
                   advertised_price, online_price, online_price_url,
                   description_bullets, categories
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    course["thread_id"], course.get("title"), course.get("url"),
                    course.get("course_creator"),
                    course.get("uploader"), course.get("uploader_url"),
                    course.get("uploader_posts", 0), course.get("uploader_joined"),
                    course.get("uploader_reputation", 0), course.get("uploader_group"),
                    course.get("replies", 0), course.get("views", 0),
                    course.get("rating", 0.0), course.get("rating_votes", 0),
                    course.get("size"), course.get("last_post_date"),
                    course.get("first_seen_date"), now, now,
                    course.get("post_content"), course.get("description"),
                    course.get("homepage_url"), course.get("download_links"),
                    course.get("advertised_price", 0.0),
                    course.get("online_price", "NA"),
                    course.get("online_price_url"),
                    course.get("description_bullets"),
                    course.get("categories"),
                ),
            )
            return True

    def update_enrichment(self, thread_id: int, data: dict):
        sets = []
        vals = []
        for key in ("project_label", "categories", "value_tier", "value_score",
                    "popularity_score", "edge_notes", "recommendation",
                    "description_bullets", "notes", "online_price", "online_price_url",
                    "course_creator"):
            if key in data:
                sets.append(f"{key}=?")
                vals.append(data[key])
        if sets:
            vals.append(thread_id)
            self.conn.execute(
                f"UPDATE courses SET {', '.join(sets)} WHERE thread_id=?",
                vals,
            )

    def get_active(self) -> list:
        return self.conn.execute(
            "SELECT * FROM courses WHERE downloaded=0 AND dismissed=0 ORDER BY value_score DESC"
        ).fetchall()

    def get_summary_stats(self) -> dict:
        total = self.conn.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        active = self.conn.execute("SELECT COUNT(*) FROM courses WHERE downloaded=0 AND dismissed=0").fetchone()[0]
        downloads = self.conn.execute("SELECT COUNT(*) FROM courses WHERE recommendation='download' AND downloaded=0 AND dismissed=0").fetchone()[0]
        high = self.conn.execute("SELECT COUNT(*) FROM courses WHERE value_tier='high' AND downloaded=0 AND dismissed=0").fetchone()[0]
        return {"total": total, "active": active, "downloads": downloads, "high_value": high}

    def log_scan(self, pages: int, total: int, new: int, errors: str = ""):
        self.conn.execute(
            "INSERT INTO scan_log (scan_date, pages_scanned, threads_found, new_threads, errors) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), pages, total, new, errors),
        )
        self.conn.commit()

    def get_recent_scans(self, limit: int = 10) -> list:
        return self.conn.execute(
            "SELECT * FROM scan_log ORDER BY scan_date DESC LIMIT ?", (limit,),
        ).fetchall()

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()
