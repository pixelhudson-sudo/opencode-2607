# Play 1: Local Competitive Intelligence Newsletter

## What It Is

A weekly email newsletter delivered to a local business owner that contains:
- Competitor price changes (scraped from their websites)
- Competitor Google Review trajectory (chart over time)
- Their own keyword rankings in local search (chart over time)
- Local industry news / regulatory changes
- Cross-promotion opportunities with nearby related businesses

## Real Deliverable Example

**Subject:** Your Market Intel — Plumbers in Austin, TX | Week of Jul 20

---

### Price Changes This Week

| Competitor | Service | Old Price | New Price | Change |
|---|---|---|---|---|
| Bob's Plumbing | Water heater install | $1,200 | $1,350 | +$150 |
| FastFlow Services | Drain cleaning | $185 | $175 | -$10 |
| Austin Rooter | Sewer line inspection | $350 | $350 | — |
| Green Planet Plumbing | TANKLESS water heater | — | $1,890 | NEW |

*Your price: $1,250 for water heater install — you're now $100 below Bob's.*

---

### Google Review Tracking (30-day trend)

```
Stars
5.0 ║
4.8 ║                    ┌──┐
4.6 ║             ┌──┐    │  │
4.4 ║      ┌──┐   │  │    │  │
4.2 ║  ┌──┐│  │   │  │    │  │
4.0 ║──┘  └──┘───└──┘────┘  └──
     Jun 21  Jun 28  Jul 5  Jul 12  Jul 19
     ── You (4.3)    ── Bob's (4.6)    ── FastFlow (4.1)
```

**Review count this month:** You: +7 | Bob's: +3 | FastFlow: +1

**New review this week you should respond to:**
> *"Patrick showed up on time and fixed the issue quickly. Fair price."* — Sarah M. (5★, Jul 18)
> → Response drafted for you.

---

### Keyword Rankings — Local Pack (Map Results)

| Keyword | Your Rank | Last Month | Bob's | FastFlow |
|---|---|---|---|---|
| plumber austin tx | 3 | 4 | 2 | 5 |
| emergency plumber austin | 5 | 5 | 1 | 6 |
| water heater repair austin | 2 | 3 | 4 | 3 |
| drain cleaning austin | 4 | 6 | 7 | 1 |
| sewer line repair austin | 6 | — | 3 | — |

**Winners:** Up 1 position on "water heater repair" — your new blog post helped.

**Losers:** Dropped off "sewer line repair" entirely. Bob's published 2 new articles on this topic this month.

---

### Industry News

- **New Texas law (SB 1245, eff. Sep 1):** All plumbing contractors must include warranty language in written estimates or default to a 2-year implied warranty.
- **Austin water utility rebate:** Smart water shutoff valve installations now qualify for $250 rebate through Aug 2027 — mention this in estimates.
- **City permit fee increase:** Building permit fees for water heater replacements going up 12% Aug 1.

---

### Related Business Spotlight

> **Austin Green Remodeling** — Kitchen & bath remodeler
> They serve homeowners who just bought a house (all built before 1980 — likely old pipes).
> Cross-promotion: You refer them on repipe jobs, they refer you on full remodels.
> Their Google rating: 4.7 (182 reviews). Phone: (512) 555-0192.

---

## Tech Stack to Build It

| Component | Tool | Cost |
|---|---|---|
| Web scraper (competitor prices) | Playwright + Node/Python | $0 |
| Google Reviews API | Google Business Profile API (free tier) | $0 |
| Keyword rank tracker | keyword.com API ($26/mo) or DIY scrape | $0-26 |
| Email delivery | Resend / SendGrid / AWS SES | $10-50/mo |
| Newsletter template | HTML email template (MJML) | $0 |
| Scheduling | cron job on cheap VPS ($5-10/mo) | $5-10 |

**Total infra cost: ~$15-85/mo**

## Pricing

| Tier | What They Get | Price |
|---|---|---|
| **Starter** | Weekly newsletter only (no custom scraper) | $200/mo |
| **Pro** | Newsletter + price scraper + rank tracker | $400/mo |
| **Agency** | Pro + review response automation + cross-promo matching | $700/mo |

## First Sale

Pick one vertical (plumbers, dentists, roofers — whichever you know). Find 3 competitors per client. Manually build the first newsletter by hand for 3 weeks to prove the format. Automate in week 4. First client: a business owner you already know. Show them the first issue for free. Ask for $200/mo.

## Legal Boundary

- Scraping public-facing price pages: legal per hiQ v. LinkedIn (9th Cir 2022) — publicly accessible data is not "unauthorized access" under CFAA
- ToS violations are civil contract disputes, not criminal
- Scraping Google review data: Google Business Profile API is sanctioned and free
- Keyword rank tracking: legal — you're checking your own client's rankings using public search results
- The line you don't cross: republishing competitor content, scraping data behind login/paywall, DoS-level rate limiting

**Risk: Very low.**
