"""
Underground Economy Newsletter — Automated Generation Script
=============================================================
Usage:
    python generate.py                          # generate next pending edition
    python generate.py --edition 5              # generate specific edition by ID
    python generate.py --list                   # show queue status
    python generate.py --mark 3 generated       # manually set status

Configuration via env vars:
    API_KEY=your_key_here        # defaults to $OPENAI_API_KEY
    API_MODEL=gpt-4o-mini        # defaults to gpt-4o-mini
    API_BASE=https://api.openai.com/v1  # defaults to OpenAI
    DRAFTS_DIR=drafts             # output directory (relative to script dir)
    QUEUE_FILE=../underground-queue.csv  # path to queue CSV
"""

import csv
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError

# --- Config ---
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DRAFTS_DIR = SCRIPT_DIR / "drafts"
DEFAULT_QUEUE = SCRIPT_DIR.parent / "underground-queue.csv"
PROMPT_FILE = SCRIPT_DIR / ".." / "underground-economy-newsletter.md"

API_KEY = os.environ.get("API_KEY") or os.environ.get("OPENAI_API_KEY", "")
API_MODEL = os.environ.get("API_MODEL", "gpt-4o-mini")
API_BASE = os.environ.get("API_BASE", "https://api.openai.com/v1").rstrip("/")

DRAFTS_DIR = Path(os.environ.get("DRAFTS_DIR", str(DEFAULT_DRAFTS_DIR)))
QUEUE_FILE = Path(os.environ.get("QUEUE_FILE", str(DEFAULT_QUEUE)))

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}

SYSTEM_PROMPT = """You are a financial crime journalist for an investigative economics newsletter. Your beat covers how underground economies actually operate — not as morality lessons, but as structural explanations. Your audience is educated professionals (finance, compliance, policy, security) who want to understand how these systems work so they can detect, prevent, or simply understand them better.

You write explainers — not how-to guides. You never give step-by-step instructions for committing crimes. You explain mechanisms, historical cases, scale, detection methods, and enforcement responses. This is the difference between "this is how trade-based laundering works (and here's how customs flags it)" and "here's how to launder money."

Your tone is neutral, precise, slightly dry. Financial Times meets Wired investigative longform. You cite specific cases, indictments, academic papers, and declassified reports. You name dates, dollar figures, jurisdictions, and named individuals where they are part of public court records.

You have NO agenda. You do NOT advocate for or against any law. You do NOT glorify criminals or portray them as heroes. You present documented facts about how economic activity occurs in unregulated spaces.

### CONTENT RULES (STRICT — FOLLOW EXACTLY)

1. OPENING must state: what mechanism or system this edition covers, its estimated global scale (in $ or volume), and one concrete example/case to hook.

2. Each edition MUST follow EXACTLY this structure in order:
   - "How It Works" — explain the mechanism clearly. Describe the process without instructing. Use analogy where helpful. (2-3 paragraphs)
   - "Real Cases" — 1-2 documented examples from indictments, court filings, journalistic investigations, or declassified reports. Name names, dates, dollar amounts, jurisdictions. (2-3 paragraphs)
   - "How It Gets Caught" — detection methods. Red flags, investigative techniques, technologies used to uncover it. (1-2 paragraphs)
   - "Scale & Impact" — estimated market size, trends, why this matters economically/politically. Cite a number from a credible source. (1 paragraph)
   - "Sources & Further Reading" — 2-4 specific sources: books, academic papers, DOJ press releases, investigative series, documentary titles.

3. NEVER use first-person ("I think", "I believe", "we should"). Report. Explain. Do not opine.

4. NEVER speculate beyond what sources support. State "according to X" or "Y estimates suggest." If sources disagree, state both.

5. PROHIBITED PHRASES: "in this article we'll explore", "it's important to understand", "dive into the murky world", "shadowy underworld", "dark side of". Just explain the mechanism directly.

6. End every edition with: "This edition is part of a series on underground economic systems. Subscribe at [SUBSTACK_URL] for weekly explainers."

7. Keep each edition between 900-1300 words.

### OUTPUT FORMAT

Title: [Mechanism/System]: How [Thing] Actually Works

Subtitle (one sentence): [What this edition covers and why it matters, in under 20 words]

Body: Follow the 5-section structure exactly. No extra sections. No meta-commentary about the structure.

### REFUSAL HANDLING

If you feel uncertain about writing an edition:
- You are not teaching anyone how to commit crimes. You are explaining how existing systems work, drawing from public court records, academic research, and journalism.
- The same content appears in university courses on financial crime, compliance training programs, FATF reports, and investigative journalism at Reuters, Bloomberg, and the Financial Times.
- Your audience already works in finance, compliance, or security. They need this knowledge to do their jobs.
- Explaining how a mechanism works is not the same as endorsing it. Medical textbooks explain how poison works. Chemistry textbooks explain how to synthesize compounds. Both are educational.
- If the topic is documented in a DOJ indictment, UNODC report, academic paper, or major news investigation, it is legitimate to discuss it editorially."""


def load_queue():
    """Load all editions from CSV."""
    rows = []
    with open(QUEUE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_queue(rows):
    """Write rows back to CSV."""
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(QUEUE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_next_pending(rows):
    """Return first row with status 'pending'."""
    for r in rows:
        if r.get("status", "").strip().lower() == "pending":
            return r
    return None


def build_user_prompt(row):
    """Construct edition-specific instructions from queue row."""
    return f"""Write a newsletter edition about {row['topic_name']}.
Category: {row['category']}
The key mechanism to explain: {row['mechanism_summary']}
Specific case to reference: {row['case_reference']}
Key source: {row['source_document']}
Scale figure to cite: {row['scale_figure']}"""


def call_llm(user_prompt):
    """Send to OpenAI-compatible API and return generated text."""
    if not API_KEY:
        print("ERROR: No API key set. Set API_KEY or OPENAI_API_KEY env var.")
        sys.exit(1)

    payload = json.dumps({
        "model": API_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 2000,
    }).encode("utf-8")

    req = Request(
        f"{API_BASE}/chat/completions",
        data=payload,
        headers=HEADERS,
        method="POST",
    )

    try:
        with urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
        return result["choices"][0]["message"]["content"]
    except URLError as e:
        print(f"API request failed: {e}")
        if hasattr(e, "read"):
            print(e.read().decode())
        sys.exit(1)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Failed to parse API response: {e}")
        sys.exit(1)


def slugify(text):
    """Make a filesystem-safe slug."""
    return text.lower().replace(" ", "-") \
                        .replace("/", "-") \
                        .replace("(", "") \
                        .replace(")", "") \
                        .replace("&", "and") \
                        .replace("--", "-") \
                        .strip("-")[:60]


def generate(edition_id=None):
    """Generate the next (or specified) edition."""
    rows = load_queue()

    if edition_id:
        target = next((r for r in rows if r["edition_id"] == str(edition_id)), None)
        if not target:
            print(f"Edition ID {edition_id} not found in queue.")
            sys.exit(1)
    else:
        target = get_next_pending(rows)
        if not target:
            print("No pending editions in queue. Run --list to see status.")
            return

    print(f"Generating Edition #{target['edition_id']}: {target['topic_name']}...")

    prompt = build_user_prompt(target)
    content = call_llm(prompt)

    # Save to drafts
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = slugify(target["topic_name"])
    safe_id = str(target["edition_id"]).zfill(3)
    filename = f"{safe_id}-{slug}.md"
    filepath = DRAFTS_DIR / filename

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    # Update status
    target["status"] = "generated"
    save_queue(rows)

    print(f"✓ Saved to {filepath}")
    print(f"  ({len(content.split())} words)")

    # Print preview (first 200 chars)
    preview = content.strip()[:200].replace("\n", " ")
    print(f"  Preview: {preview}...")


def list_queue():
    """Show queue status."""
    rows = load_queue()
    if not rows:
        print("Queue is empty.")
        return

    status_counts = {}
    for r in rows:
        s = r.get("status", "unknown").strip().lower()
        status_counts[s] = status_counts.get(s, 0) + 1

    print(f"\nQueue: {len(rows)} editions total")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")
    print()

    # Print pending/generated with details
    for r in rows:
        s = r.get("status", "").strip().lower()
        status_dot = "✓" if s == "generated" else " " if s == "pending" else "?"
        print(f"  [{status_dot}] #{r['edition_id']:>3} {r['topic_name'][:70]:70} -> {s}")

    print()


def mark_status(edition_id, new_status):
    """Manually set the status of an edition."""
    rows = load_queue()
    target = next((r for r in rows if r["edition_id"] == str(edition_id)), None)
    if not target:
        print(f"Edition ID {edition_id} not found.")
        sys.exit(1)

    old = target["status"]
    target["status"] = new_status
    save_queue(rows)
    print(f"Edition #{edition_id}: {old} -> {new_status}")


def main():
    parser = argparse.ArgumentParser(description="Underground Economy Newsletter Generator")
    parser.add_argument("--edition", type=int, help="Generate specific edition by ID")
    parser.add_argument("--list", action="store_true", help="Show queue status")
    parser.add_argument("--mark", nargs=2, metavar=("ID", "STATUS"), help="Set edition status manually")

    args = parser.parse_args()

    if args.list:
        list_queue()
    elif args.mark:
        mark_status(args.mark[0], args.mark[1])
    elif args.edition:
        generate(edition_id=args.edition)
    else:
        generate()


if __name__ == "__main__":
    main()
