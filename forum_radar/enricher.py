import re
import logging

logger = logging.getLogger(__name__)


class CourseEnricher:
    def __init__(self, config):
        self.config = config
        self.value_keywords = config.get_value_keywords()
        self.fluff = config.MARKETING_FLUFF
        self.cat_labels = config.PROJECT_CATEGORIES

    def classify_category(self, title: str, content: str = "") -> tuple[list[str], str]:
        text = (title + " " + content).lower()
        matched_ids = []
        best_count = 0
        best_label = "Other"

        for pid, project in self.config.PROJECT_KEYWORDS.items():
            count = sum(1 for kw in project["keywords"] if kw.lower() in text)
            if count > 0:
                matched_ids.append(pid)
                if count > best_count:
                    best_count = count
                    best_label = project["label"]

        return matched_ids, best_label

    def extract_bullets(self, content: str) -> str:
        if not content:
            return ""
        lines = content.split("\n")
        bullets = []
        for line in lines:
            stripped = line.strip()
            if not stripped or len(stripped) < 15:
                continue

            lower = stripped.lower()
            if any(kw in lower for kw in ["codeblock", "http", "https://", "download", "rapidgator",
                                           "uploadgig", "nitroflare", ".png", ".jpg", ".jpeg",
                                           ".gif", "screenshot", "password", "extract", "winrar",
                                           "interchangeable", "no password", "single extraction"]):
                continue
            if any(fluff in lower for fluff in self.fluff):
                continue

            if re.match(r'^[\d]+[\.\)]\s', stripped):
                bullets.append(stripped)
            elif stripped.startswith(("•", "-", "*", "‣", "⁃")):
                bullets.append(stripped.lstrip("•-*‣⁃ ").strip())
            elif re.match(r'^(Value|Price|Cost|Bonus|Module|Lesson|Chapter|Section|Week|Step)\b',
                          stripped, re.IGNORECASE):
                bullets.append(stripped)
            elif ":" in stripped and len(stripped.split(":")[0]) < 40:
                bullets.append(stripped)

        if len(bullets) < 3:
            sentences = re.split(r'[.!?]\s+', content)
            for s in sentences:
                s = s.strip()
                if len(s) > 20 and not any(kw in s.lower() for kw in
                                           ["codeblock", "http", "download", "rapidgator"]):
                    if not any(fluff in s.lower() for fluff in self.fluff):
                        bullets.append(s)

        seen = set()
        unique = []
        for b in bullets:
            key = b.lower()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(b)

        return "\n".join(unique[:8])

    def compute_value_tier(self, title: str, content: str, advertised_price: float) -> tuple[str, float]:
        text = (title + " " + (content or "")).lower()
        score = 0.0

        for kw in self.value_keywords["high"]:
            if kw.lower() in text:
                score += 15
        for kw in self.value_keywords["medium"]:
            if kw.lower() in text:
                score += 8
        for kw in self.value_keywords["low"]:
            if kw.lower() in text:
                score += 2

        if advertised_price > 0:
            score += min(advertised_price / 100, 50)

        content_len = len(content or "")
        if content_len > 2000:
            score += 10
        elif content_len > 1000:
            score += 5
        elif content_len > 500:
            score += 2

        if score >= 30:
            tier = "high"
        elif score >= 15:
            tier = "medium"
        elif score >= 5:
            tier = "low"
        else:
            tier = "unscored"

        return tier, round(score, 1)

    def compute_popularity(self, views: int, replies: int, rating: float, rating_votes: int) -> float:
        score = 0.0
        score += min(views / 100, 40)
        score += min(replies * 3, 20)
        if rating_votes > 0:
            score += (rating / 5) * 20
        return round(min(score, 80), 1)

    def compute_edge(self, title: str, content: str, categories: list[str]) -> str:
        text = (title + " " + (content or "")).lower()
        notes = []

        if "updated" in text or "2026" in text or "2025" in text:
            notes.append("Recently updated")
        if "bonus" in text:
            notes.append("Includes bonuses")
        if "live" in text and ("call" in text or "coaching" in text or "qa" in text):
            notes.append("Live coaching included")
        if "certification" in text or "certificate" in text:
            notes.append("Certification track")
        if "community" in text or "facebook group" in text or "private" in text:
            notes.append("Community access")
        if "template" in text:
            notes.append("Includes templates")
        if "done with you" in text or "dwy" in text:
            notes.append("Done-with-you format")

        cat_labels = [self.cat_labels.get(c, c) for c in categories]
        for cl in cat_labels:
            if cl.lower() in text:
                notes.append(f"Aligns with {cl}")
                break

        return "; ".join(notes[:5]) if notes else ""

    def generate_recommendation(self, value_tier: str, popularity: float,
                                 value_score: float, categories: list[str]) -> str:
        if not categories or "im_course" in categories:
            if value_score >= 20:
                return "download"
            return "skip"

        if value_tier == "high" and popularity >= 20:
            return "download"
        if value_tier == "high":
            return "consider"
        if value_tier == "medium" and popularity >= 30:
            return "consider"
        return "skip"

    def enricher(self, course: dict) -> dict:
        title = course.get("title", "")
        content = course.get("post_content", "")
        advertised_price = course.get("advertised_price", 0.0)
        views = course.get("views", 0)
        replies = course.get("replies", 0)
        rating = course.get("rating", 0.0)
        rating_votes = course.get("rating_votes", 0)

        categories, project_label = self.classify_category(title, content)
        value_tier, value_score = self.compute_value_tier(title, content, advertised_price)
        popularity_score = self.compute_popularity(views, replies, rating, rating_votes)
        edge_notes = self.compute_edge(title, content, categories)
        recommendation = self.generate_recommendation(
            value_tier, popularity_score, value_score, categories
        )
        description_bullets = self.extract_bullets(content)

        return {
            "project_label": project_label,
            "categories": ",".join(categories),
            "value_tier": value_tier,
            "value_score": value_score,
            "popularity_score": popularity_score,
            "edge_notes": edge_notes,
            "recommendation": recommendation,
            "description_bullets": description_bullets,
        }
