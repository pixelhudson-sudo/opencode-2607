# Shen Yun Showtime Tracker — Manual

## What It Does

Scrapes showtimes from all Shen Yun city pages (63 cities, 11 countries), stores them in a SQLite database, detects changes between scans, and exports to a formatted Excel spreadsheet. Runs automatically every 3 days via cron at 6am.

## How It Works

```
cron (0 6 * * *)
  └─ shenyun_scraper.py
       ├─ should_run() → skips if <3 days since last scan
       ├─ get_cities() → scrapes shenyun.com/tickets for city/venue list
       ├─ get_city_showtimes(alias) → API call per unique city
       ├─ extract_address_from_page() → JSON-LD from venue page (no country, clean format)
       ├─ SQLite INSERT → showtimes + scan_history tables
       ├─ detect_changes() → compares latest 2 scans
       ├─ write_update_md() → writes YYMMDD-update.md with bullet-point changes
       └─ shenyun_export_excel.py → builds shenyun_showtimes.xlsx
```

**Key files:**
- `shenyun_scraper.py` — the scraper, change detection, update reporter
- `shenyun_export_excel.py` — Excel export (Calibri 14, center-aligned, auto-fit, Group column)
- `shenyun_showtimes.db` — SQLite database (scan_history + showtimes tables)
- `shenyun_showtimes.xlsx` — latest export (277 showtimes, 9 columns)
- `YYMMDD-update.md` — change reports generated after each scan
- `shenyun_scraper.log` — cron output log

## How To Run

```bash
# Normal scrape (respects 3-day throttle)
python3 shenyun_scraper.py

# Force scrape regardless of last scan time
python3 shenyun_scraper.py --force

# Show change report without scraping
python3 shenyun_scraper.py --report-only

# Export latest data as JSON
python3 shenyun_scraper.py --export data.json

# Run a SQL query against the database
python3 shenyun_scraper.py --query "SELECT city, COUNT(*) as n FROM showtimes GROUP BY city"

# Generate xlsx only (no scrape)
python3 shenyun_export_excel.py
```

## How To Use

1. **Check for changes** — look at the latest `YYMMDD-update.md` in the project folder
2. **Open the spreadsheet** — `shenyun_showtimes.xlsx` has all showtimes with 9 columns: City, Country, Theater (name + address), Google Maps (clickable), Date, Time, Showtime (raw text), City URL ("Buy Tickets" link), Group 1-8
3. **Assign groups** — fill in the Group column in the xlsx (1–8 per theater); next scrape preserves the values
4. **Monitor the log** — `shenyun_scraper.log` captures cron output

## 5 Next Steps

1. **Group notifications** — wire a script to email/Discord/Slack alerts when a specific group's showtimes change
2. **Calendar export** — generate `.ics` files per city or group so showtimes appear in Google Calendar
3. **Price tracking** — scrape ticket price ranges from shenyun.com per city (if available) and flag price drops
4. **Web dashboard** — serve the data via a simple Flask/FastAPI page with sortable tables and group filters
5. **History retention** — add a retention policy (e.g., keep only last 20 scans) to keep the DB small
