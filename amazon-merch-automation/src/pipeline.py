"""
Pipeline Orchestrator — runs the full Amazon Merch automation pipeline end-to-end.

Flow:
  1. [AI] Find niches           → 01-niche-finder.txt
  2. [Scrape] Get competitor data → scraper.py
  3. [AI] Parse scraped data    → 02-scraper-parser.txt
  4. [AI] Generate keywords     → 03-keyword-generator.txt
  5. [AI] Validate niche        → 06-niche-validator.txt
  6. [AI] Generate designs      → 04-design-prompt.txt
  7. [Manual] Create images     → Midjourney / DALL-E / Canva
  8. [AI] Write listings        → 05-listing-writer.txt
  9. [Semi-auto] Upload         → upload_helper.py
  10. [Track] Monitor sales     → tracker.py

Each AI step produces a prompt. You feed it to your cheap model, paste the
response back, and the pipeline parses it and moves forward.
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from keyword_engine import PromptBuilder, KeywordParser
from tracker import Tracker


class Pipeline:
    def __init__(self):
        self.builder = PromptBuilder()
        self.parser = KeywordParser()
        self.tracker = Tracker()
        self.state = {}  # carries data between steps

    def step_1_find_niches(self) -> str:
        """Generate the niche-finding prompt for AI."""
        prompt = self.builder.build_niche_finder_prompt()
        print("\n" + "=" * 60)
        print("STEP 1: FIND NICHES")
        print("=" * 60)
        print("\nSend this prompt to your AI model:\n")
        print(prompt)

        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        prompt_path = output_dir / "01-niche-finder-prompt.txt"
        prompt_path.write_text(prompt)
        print(f"\n[SAVED] Prompt saved to {prompt_path}")
        print(f"[ACTION] Feed this to your AI, paste response to {output_dir / '01-niche-response.txt'}")
        return prompt

    def step_2_parse_niches(self, response: str = None) -> list[dict]:
        """Parse AI response into niche dicts and save to tracker."""
        if response is None:
            response_path = Path(__file__).parent.parent / "output" / "01-niche-response.txt"
            if not response_path.exists():
                print("[ERROR] No response file found. Run step 1 first and save AI response.")
                return []
            response = response_path.read_text()

        niches = self.parser.parse_niche_output(response)
        print(f"\n[PARSED] {len(niches)} niches found.")

        for n in niches:
            niche_id = self.tracker.add_niche(
                name=n.get("NAME", "Unknown"),
                audience=n.get("AUDIENCE", ""),
                competition=n.get("COMPETITION", ""),
                season=n.get("SEASON", ""),
            )
            n["_db_id"] = niche_id
            print(f"  -> Saved: {n.get('NAME')} (ID #{niche_id})")

        self.state["niches"] = niches
        return niches

    def step_3_generate_keywords(self, niche: dict) -> str:
        """Generate keyword prompt for a single niche."""
        prompt = self.builder.build_keyword_prompt(
            niche=niche.get("NAME", ""),
            audience=niche.get("AUDIENCE", ""),
            competitor_keywords=niche.get("TOP_KEYWORDS", []),
            top_titles=[niche.get("BESTSELLER_EXAMPLE", "")],
        )

        output_dir = Path(__file__).parent.parent / "output"
        safe_name = niche.get("NAME", "unknown").replace(" ", "-").lower()
        prompt_path = output_dir / f"03-keywords-{safe_name}.txt"
        prompt_path.write_text(prompt)

        print(f"\n[KEYWORD PROMPT] Saved to {prompt_path}")
        return prompt

    def step_4_generate_designs(self, niche: dict, keywords: list[str],
                                 top_designs: str = "") -> str:
        """Generate design prompt for a niche."""
        prompt = self.builder.build_design_prompt(
            niche=niche.get("NAME", ""),
            audience=niche.get("AUDIENCE", ""),
            top_designs_summary=top_designs or niche.get("BESTSELLER_EXAMPLE", ""),
            popular_keywords=keywords,
        )

        output_dir = Path(__file__).parent.parent / "output"
        safe_name = niche.get("NAME", "unknown").replace(" ", "-").lower()
        prompt_path = output_dir / f"04-designs-{safe_name}.txt"
        prompt_path.write_text(prompt)

        print(f"\n[DESIGN PROMPT] Saved to {prompt_path}")
        return prompt

    def step_5_save_designs(self, niche: dict, response: str):
        """Parse design response and save to tracker."""
        designs = self.parser.parse_design_output(response)
        niche_id = niche.get("_db_id", 0)

        for d in designs:
            self.tracker.add_design(
                niche_id=niche_id,
                design_id=d.get("ID", ""),
                style=d.get("STYLE", ""),
                concept=d.get("CONCEPT", ""),
                color_palette=d.get("COLOR_PALETTE", ""),
                placement=d.get("PLACEMENT", ""),
                ai_prompt=d.get("AI_IMAGE_PROMPT", ""),
                text_overlay=d.get("TEXT_OVERLAY", ""),
                target_demo=d.get("TARGET_DEMOGRAPHIC", ""),
                estimated_ctr=d.get("ESTIMATED_CTR", ""),
            )

        print(f"[SAVED] {len(designs)} designs added to tracker for niche '{niche.get('NAME')}'")
        return designs

    def step_6_generate_listing(self, niche: dict, design: dict,
                                  keywords: list[str], price: float = 19.99) -> str:
        """Generate listing prompt for a single design."""
        prompt = self.builder.build_listing_prompt(
            niche=niche.get("NAME", ""),
            design_description=design.get("CONCEPT", ""),
            primary_keywords=keywords[:10],
            audience=niche.get("AUDIENCE", ""),
            price=price,
        )

        output_dir = Path(__file__).parent.parent / "output"
        safe_name = design.get("ID", "unknown")
        prompt_path = output_dir / f"05-listing-{safe_name}.txt"
        prompt_path.write_text(prompt)

        print(f"[LISTING PROMPT] Saved to {prompt_path}")
        return prompt

    def step_7_save_listing(self, design_id: str, response: str, price: float = 19.99):
        """Parse listing response and save to tracker."""
        listing = self.parser.parse_listing_output(response)
        if not listing:
            print("[ERROR] Could not parse listing output.")
            return

        self.tracker.add_listing(
            design_id=design_id,
            title=listing.get("TITLE", ""),
            bullets=listing.get("BULLET_1", "") + "|" +
                    listing.get("BULLET_2", "") + "|" +
                    listing.get("BULLET_3", "") + "|" +
                    listing.get("BULLET_4", ""),
            description=listing.get("DESCRIPTION", ""),
            backend_terms=listing.get("BACKEND_SEARCH_TERMS", ""),
            price=price,
        )

        print(f"[SAVED] Listing for design '{design_id}' added to tracker.")
        return listing

    def run_full(self):
        """Interactive full pipeline run."""
        print("\n" + "=" * 60)
        print("AMAZON MERCH AUTOMATION PIPELINE")
        print("=" * 60)
        print("\nThis pipeline will guide you through each step.")
        print("At each AI step, you paste the response back.\n")

        # Step 1: Find niches
        self.step_1_find_niches()
        input("\n[PASTE AI RESPONSE to output/01-niche-response.txt, then press ENTER]")

        # Step 2: Parse niches
        niches = self.step_2_parse_niches()
        if not niches:
            print("[STOP] No niches found. Check your AI response.")
            return

        # Step 3-7: For each ENTER/WATCH niche, process through
        for niche in niches[:3]:  # Start with top 3
            print(f"\n{'~'*60}")
            print(f"PROCESSING NICHE: {niche.get('NAME')}")
            print(f"{'~'*60}")

            # Generate keywords
            self.step_3_generate_keywords(niche)
            kw_file = Path(__file__).parent.parent / "output" / f"03-keywords-{niche.get('NAME', '').replace(' ', '-').lower()}.txt"
            print(f"\n-> Keyword prompt at: {kw_file}")

            # Generate designs
            self.step_4_generate_designs(niche, niche.get("TOP_KEYWORDS", []))
            design_file = Path(__file__).parent.parent / "output" / f"04-designs-{niche.get('NAME', '').replace(' ', '-').lower()}.txt"
            print(f"-> Design prompt at: {design_file}")

        # Export dashboard data
        json_path = self.tracker.export_json_file()
        print(f"\n[DONE] Full pipeline complete.")
        print(f"[DATA] Dashboard JSON: {json_path}")
        print(f"[NEXT] 1. Send design prompts to AI image generator")
        print(f"[NEXT] 2. Send listing prompts to AI model")
        print(f"[NEXT] 3. Use upload_helper.py to publish")
        print(f"[NEXT] 4. Open tracker/dashboard.html to monitor sales")


if __name__ == "__main__":
    Pipeline().run_full()
