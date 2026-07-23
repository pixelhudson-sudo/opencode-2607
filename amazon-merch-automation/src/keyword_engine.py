"""
Keyword Engine — feeds niche + competitor data into cheap AI models
and parses the structured output back into usable keyword lists.
"""

import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


@dataclass
class KeywordSet:
    niche: str
    short_tail: list[str] = field(default_factory=list)
    long_tail: list[str] = field(default_factory=list)
    occasion: list[str] = field(default_factory=list)
    trending: list[str] = field(default_factory=list)
    title_starters: list[str] = field(default_factory=list)
    bullet_phrases: list[str] = field(default_factory=list)
    backend_keywords: list[str] = field(default_factory=list)
    flagged_terms: list[str] = field(default_factory=list)
    generated_at: str = ""


class PromptBuilder:
    """Builds the filled prompt by injecting data into template files."""

    PROMPT_DIR = Path(__file__).parent.parent / "prompts"

    @staticmethod
    def load_template(name: str) -> str:
        path = PromptBuilder.PROMPT_DIR / name
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")
        return path.read_text()

    @classmethod
    def build_keyword_prompt(
        cls,
        niche: str,
        audience: str,
        competitor_keywords: list[str],
        top_titles: list[str],
    ) -> str:
        template = cls.load_template("03-keyword-generator.txt")
        return (
            template.replace("{niche_name}", niche)
            .replace("{audience_description}", audience)
            .replace("{competitor_keywords}", ", ".join(competitor_keywords))
            .replace("{top_titles}", "\n".join(f"- {t}" for t in top_titles))
        )

    @classmethod
    def build_design_prompt(
        cls,
        niche: str,
        audience: str,
        top_designs_summary: str,
        popular_keywords: list[str],
        color_trends: str = "current trending: earth tones, pastels, neon accents",
    ) -> str:
        template = cls.load_template("04-design-prompt.txt")
        return (
            template.replace("{niche_name}", niche)
            .replace("{audience}", audience)
            .replace("{top_designs_summary}", top_designs_summary)
            .replace("{popular_keywords}", ", ".join(popular_keywords))
            .replace("{current_color_trends}", color_trends)
        )

    @classmethod
    def build_listing_prompt(
        cls,
        niche: str,
        design_description: str,
        primary_keywords: list[str],
        audience: str,
        price: float,
    ) -> str:
        template = cls.load_template("05-listing-writer.txt")
        return (
            template.replace("{niche_name}", niche)
            .replace("{design_brief}", design_description)
            .replace("{primary_keywords}", ", ".join(primary_keywords))
            .replace("{audience}", audience)
            .replace("{price}", f"${price:.2f}")
        )

    @classmethod
    def build_niche_finder_prompt(cls) -> str:
        return cls.load_template("01-niche-finder.txt")

    @classmethod
    def build_scraper_parser_prompt(cls, raw_text: str) -> str:
        template = cls.load_template("02-scraper-parser.txt")
        return template.replace("{scraped_text}", raw_text[:15000])

    @classmethod
    def build_niche_validator_prompt(
        cls,
        niche: str,
        competitor_summary: str,
        estimated_search_volume: str,
        avg_price: float,
        avg_bsr: str,
        avg_review_count: int,
    ) -> str:
        template = cls.load_template("06-niche-validator.txt")
        return (
            template.replace("{niche}", niche)
            .replace("{competitor_summary}", competitor_summary)
            .replace("{estimated_search_volume}", estimated_search_volume)
            .replace("{avg_price}", f"${avg_price:.2f}")
            .replace("{avg_bsr}", avg_bsr)
            .replace("{average_review_count}", str(avg_review_count))
        )


class KeywordParser:
    """Parses AI output back into structured keyword data."""

    @staticmethod
    def parse_keyword_output(raw_output: str, niche: str) -> KeywordSet:
        ks = KeywordSet(niche=niche)

        def extract_section(label: str, text: str) -> list[str]:
            pattern = rf"{label}:\s*\[(.*?)\]"
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                return []
            items = match.group(1).strip()
            return [i.strip().strip("'\"") for i in items.split(",") if i.strip()]

        ks.short_tail = extract_section("SHORT_TAIL", raw_output)
        ks.long_tail = extract_section("LONG_TAIL", raw_output)
        ks.occasion = extract_section("OCCASION", raw_output)
        ks.trending = extract_section("TRENDING", raw_output)
        ks.title_starters = extract_section("TITLE_STARTERS", raw_output)
        ks.bullet_phrases = extract_section("BULLET_PHRASES", raw_output)
        ks.backend_keywords = extract_section("BACKEND_KEYWORDS", raw_output)
        ks.flagged_terms = extract_section("FLAGGED_TERMS", raw_output)

        return ks

    @staticmethod
    def parse_listing_output(raw_output: str) -> dict:
        """Parse listing writer output into structured dict for upload."""
        result = {}

        patterns = {
            "TITLE": r"TITLE:\s*(.+?)(?=\nBULLET|\nDESCRIPTION|\nBACKEND|\Z)",
            "BULLET_1": r"BULLET_1:\s*(.+?)(?=\nBULLET_2|\Z)",
            "BULLET_2": r"BULLET_2:\s*(.+?)(?=\nBULLET_3|\Z)",
            "BULLET_3": r"BULLET_3:\s*(.+?)(?=\nBULLET_4|\Z)",
            "BULLET_4": r"BULLET_4:\s*(.+?)(?=\nDESCRIPTION|\Z)",
            "DESCRIPTION": r"DESCRIPTION:\s*(.+?)(?=\nBACKEND|\Z)",
            "BACKEND_SEARCH_TERMS": r"BACKEND_SEARCH_TERMS:\s*(.+?)(?=\nKEYWORDS|\Z)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, raw_output, re.DOTALL)
            if match:
                result[key] = match.group(1).strip()

        return result

    @staticmethod
    def parse_design_output(raw_output: str) -> list[dict]:
        """Parse design prompt output into list of design briefs."""
        designs = []
        blocks = re.split(r"---DESIGN_START---|---DESIGN_END---", raw_output)

        for i in range(1, len(blocks) - 1, 2):
            design = {}
            block = blocks[i]

            field_patterns = {
                "ID": r"ID:\s*(\S+)",
                "STYLE": r"STYLE:\s*(\S+)",
                "CONCEPT": r"CONCEPT:\s*(.+?)(?=\nCOLOR|\Z)",
                "COLOR_PALETTE": r"COLOR_PALETTE:\s*(.+?)(?=\nPLACEMENT|\Z)",
                "PLACEMENT": r"PLACEMENT:\s*(.+?)(?=\nAI_IMAGE|\Z)",
                "AI_IMAGE_PROMPT": r"AI_IMAGE_PROMPT:\s*(.+?)(?=\nTEXT_OVERLAY|\Z)",
                "TEXT_OVERLAY": r"TEXT_OVERLAY:\s*(.+?)(?=\nTARGET_DEMO|\Z)",
                "TARGET_DEMOGRAPHIC": r"TARGET_DEMOGRAPHIC:\s*(.+?)(?=\nESTIMATED|\Z)",
                "ESTIMATED_CTR": r"ESTIMATED_CTR:\s*(\S+)",
            }

            for key, pattern in field_patterns.items():
                match = re.search(pattern, block, re.DOTALL)
                if match:
                    design[key] = match.group(1).strip()

            if design:
                designs.append(design)

        return designs

    @staticmethod
    def parse_niche_output(raw_output: str) -> list[dict]:
        """Parse niche finder output into list of niche dicts."""
        niches = []
        blocks = re.split(r"---NICHE_START---|---NICHE_END---", raw_output)

        for i in range(1, len(blocks) - 1, 2):
            niche = {}
            block = blocks[i]

            field_patterns = {
                "NAME": r"NAME:\s*(.+?)(?=\nAUDIENCE|\Z)",
                "AUDIENCE": r"AUDIENCE:\s*(.+?)(?=\nBESTSELLER|\Z)",
                "BESTSELLER_EXAMPLE": r"BESTSELLER_EXAMPLE:\s*(.+?)(?=\nSEASON|\Z)",
                "SEASON": r"SEASON:\s*(.+?)(?=\nCOMPETITION|\Z)",
                "COMPETITION": r"COMPETITION:\s*(.+?)(?=\nWHY_NOW|\Z)",
                "WHY_NOW": r"WHY_NOW:\s*(.+?)(?=\nTOP_KEYWORDS|\Z)",
                "TOP_KEYWORDS": r"TOP_KEYWORDS:\s*(.+?)(?=\n---|\Z)",
            }

            for key, pattern in field_patterns.items():
                match = re.search(pattern, block, re.DOTALL)
                if match:
                    value = match.group(1).strip()
                    if key == "TOP_KEYWORDS":
                        niche[key] = [k.strip() for k in value.split(",") if k.strip()]
                    else:
                        niche[key] = value

            if niche:
                niches.append(niche)

        return niches

    @staticmethod
    def parse_validation_output(raw_output: str) -> dict:
        """Parse niche validator output."""
        result = {}
        patterns = {
            "SCORE": r"SCORE:\s*(\d+)",
            "VERDICT": r"VERDICT:\s*(\w+)",
            "DEMAND_SCORE": r"DEMAND_SCORE:\s*(\d+)",
            "COMPETITION_SCORE": r"COMPETITION_SCORE:\s*(\d+)",
            "PROFIT_MARGIN_POTENTIAL": r"PROFIT_MARGIN_POTENTIAL:\s*(\d+)",
            "TREND_DIRECTION": r"TREND_DIRECTION:\s*(\w+)",
            "DIFFERENTIATION_EASE": r"DIFFERENTIATION_EASE:\s*(\d+)",
            "RECOMMENDED_ENTRY_ANGLE": r"RECOMMENDED_ENTRY_ANGLE:\s*(.+?)(?=\nRECOMMENDED_DESIGNS|\Z)",
            "RECOMMENDED_DESIGNS_TO_START": r"RECOMMENDED_DESIGNS_TO_START:\s*(\d+)",
            "RECOMMENDED_PRICE_ENTRY": r"RECOMMENDED_PRICE_ENTRY:\s*\$?(\d+\.?\d*)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, raw_output)
            if match:
                val = match.group(1).strip()
                if key.endswith("_SCORE") or key == "SCORE":
                    result[key] = int(val)
                elif key.endswith("_TO_START"):
                    result[key] = int(val)
                elif key == "RECOMMENDED_PRICE_ENTRY":
                    result[key] = float(val)
                else:
                    result[key] = val

        return result


if __name__ == "__main__":
    builder = PromptBuilder()
    parser = KeywordParser()

    prompt = builder.build_keyword_prompt(
        niche="Funny Nurse Life",
        audience="Nurses, ages 25-45, female-skewed, gift-givers",
        competitor_keywords=[
            "nurse shirt", "funny nursing", "rn life", "night shift",
            "caffeine and chaos", "nurse humor", "healthcare hero",
        ],
        top_titles=[
            "Funny Nurse T-Shirt - Caffeine and Chaos RN Life Tee",
            "Nurse Life Shirt - Running on Coffee and Dry Shampoo",
            "Night Shift Nurse T-Shirt - I Save Lives What's Your Superpower",
        ],
    )

    print("=== GENERATED KEYWORD PROMPT ===\n")
    print(prompt)
    print("\n=== SEND THIS TO YOUR AI MODEL ===")
