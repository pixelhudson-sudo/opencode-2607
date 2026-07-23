# Amazon Merch Automation Pipeline

AI-powered T-shirt business engine. Find niches, scrape competitors, generate copyright-safe keywords, produce design briefs, write listings, semi-auto upload, and track conversions — all driven by cheap AI model prompts that won't hallucinate.

## Architecture

```
Niche Discovery        Scrape + Parse       Keyword Engine       Design Briefs
[AI: 01-niche-]  -->  [scraper.py +    -->  [AI: 03-keyword-]  [AI: 04-design-]
 finder.txt]          02-scraper-           generator.txt]       prompt.txt]
                       parser.txt]
                                                                    |
                                                                    v
Tracker Dashboard  <--  Upload           <--  Listing Writer   <--  Image Gen
[dashboard.html]       [upload_helper.py]     [AI: 05-listing-]     [Midjourney/
                                               writer.txt]           DALL-E]
```

## Quick Start

```bash
cd amazon-merch-automation

# 1. Install dependencies
pip install requests beautifulsoup4 playwright
playwright install chromium

# 2. Initialize the tracker database
python src/tracker.py

# 3. Run the full interactive pipeline
python src/pipeline.py

# 4. Open the dashboard
open tracker/dashboard.html
```

## Step-by-Step Workflow

Every AI step outputs a prompt file to `output/`. Feed it to your cheap model (GPT-3.5, Claude Haiku, Gemini Flash, any local model), paste the response into the matching `-response.txt` file, and the pipeline picks it up.

### Step 1 — Find Niches
- **Prompt:** `output/01-niche-finder-prompt.txt`
- **Response file:** `output/01-niche-response.txt`
- **What it does:** Generates 15 niche ideas with audience, competition level, season, and starter keywords. No trademarked names anywhere.

### Step 2 — Scrape Competitors
- **Script:** `src/scraper.py`
- **What it does:** Scrapes Amazon Merch search results for a keyword. Outputs `scraped_raw.txt` which you feed into the scraper-parser prompt.
- **Usage:**
  ```python
  from scraper import AmazonMerchScraper
  s = AmazonMerchScraper()
  listings = s.search("funny nurse", pages=3)
  s.to_raw_text(listings)  # feed this to step 3
  ```

### Step 3 — Parse & Generate Keywords
- **Prompt template:** `prompts/03-keyword-generator.txt`
- **Python helper:** `src/keyword_engine.py` fills the template with your niche data
- **What you get:** Short-tail, long-tail, occasion, and trending keywords — all copyright-safe with a self-check section that flags anything risky.

### Step 4 — Generate Design Briefs
- **Prompt template:** `prompts/04-design-prompt.txt`
- **What you get:** 8 unique T-shirt design concepts per niche, each with color palette, placement, AI image prompt (under 300 chars for DALL-E/Midjourney), target demographic, and estimated CTR.

### Step 5 — Write Listings
- **Prompt template:** `prompts/05-listing-writer.txt`
- **What you get:** Full Amazon listing — title (80-120 chars), 4 bullets, description, backend search terms. Everything copy-paste ready.

### Step 6 — Create Images
Feed the `AI_IMAGE_PROMPT` from each design brief into Midjourney, DALL-E 3, or Stable Diffusion. Save images to an `images/` folder with the design ID as filename.

### Step 7 — Upload (Semi-Auto)
- **Script:** `src/upload_helper.py`
- **What it does:** Opens Chromium via Playwright, navigates to Amazon Merch create page, fills every text field, checks the right boxes. You handle: login, image upload (drag & drop), captcha, final submit.
- **Usage:**
  ```bash
  python src/upload_helper.py
  ```
- After publishing, grab the ASIN from your Merch dashboard and update the tracker:
  ```python
  from tracker import Tracker
  t = Tracker()
  t.publish_listing(listing_id=1, asin='B0XXXXXXX', url='https://...')
  ```

### Step 8 — Track Sales
- **Dashboard:** Open `tracker/dashboard.html` in any browser, load `tracker/dashboard_data.json`
- **Manually record sales:**
  ```python
  from tracker import Tracker
  t = Tracker()
  t.record_sale(listing_id=1, units=1, revenue=19.99, royalty=3.80)
  t.export_json_file()  # update the dashboard
  ```

## File Map

```
amazon-merch-automation/
├── prompts/
│   ├── 01-niche-finder.txt         # Discover 15 niches
│   ├── 02-scraper-parser.txt       # Parse raw scraped listings
│   ├── 03-keyword-generator.txt    # Copyright-safe keywords
│   ├── 04-design-prompt.txt        # 8 design briefs per niche
│   ├── 05-listing-writer.txt       # Full Amazon listing copy
│   └── 06-niche-validator.txt      # Score + verdict per niche
├── src/
│   ├── scraper.py                  # Amazon Merch listing scraper
│   ├── keyword_engine.py           # Prompt builder + AI output parser
│   ├── tracker.py                  # SQLite tracker + reports
│   ├── upload_helper.py            # Playwright semi-auto upload
│   └── pipeline.py                 # Full pipeline orchestrator
├── tracker/
│   ├── merch_tracker.db            # SQLite database (auto-created)
│   ├── dashboard.html              # Self-contained performance dashboard
│   └── dashboard_data.json         # JSON export for dashboard
├── output/                         # Generated prompts + AI responses
├── images/                         # Your T-shirt design PNGs
├── config.json                     # API keys and settings
└── README.md
```

## Prompts Are Model-Agnostic

All 6 prompt templates use `{placeholder}` syntax. The `keyword_engine.py` `PromptBuilder` class fills them. Output format uses strict delimiters (`---SECTION_START---` / `---SECTION_END---`) so regex parsing works reliably even with cheap models. No model-specific system prompts — everything is one-shot instruction + format.

## Making the AI Calls

You can wire any model. Example with OpenAI (GPT-3.5-turbo is $0.50/M tokens):

```python
import openai
from src.keyword_engine import PromptBuilder

prompt = PromptBuilder.build_niche_finder_prompt()
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.7,
    max_tokens=2000,
)
print(response.choices[0].message.content)
```

Or with a local model via Ollama:
```bash
ollama run llama3 < output/01-niche-finder-prompt.txt > output/01-niche-response.txt
```

## Tips

- **Start with 3 niches, 8 designs each** — 24 shirts is enough to test what converts
- **Price at $19.99** for standard tees, $24.99 for premium — undercuts the premium brands while leaving room for royalties (~$4-6 per sale)
- **Run the scraper once a week** on your active niches to track competitor movement
- **Rotate through all 8 design styles** per niche — typography might flop but the retro version sells
- **The keyword safety check is crucial** — Amazon will terminate your Merch account for trademark violations. The `FLAGGED_TERMS` section in the keyword prompt self-audits every output.
