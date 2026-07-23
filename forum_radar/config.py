FORUM_URL = "https://kraftymarketingprofits.com/internetmarketingforum/Forum-internet-marketing-special-downloads--53"
BASE_URL = "https://kraftymarketingprofits.com/internetmarketingforum/"

DB_PATH = "forum_radar/courses.db"
REPORT_PATH = "forum_radar/daily_report.html"

REQUEST_DELAY = 1
MAX_PAGES_PER_SCAN = 2
DAYS_BACK_NEW = 7

CATEGORY_GROUPS = {
    "Marketing & Sales": {
        "icon": "📈",
        "categories": ["IM Course", "Lead Generation", "GMB & Local SEO", "Ecommerce"],
    },
    "AI & Automation": {
        "icon": "🤖",
        "categories": ["AI & Automation", "Content Creation"],
    },
    "Finance & Crypto": {
        "icon": "💰",
        "categories": ["Trading & Alpha", "Crypto", "Domain Flipping"],
    },
    "Design & Branding": {
        "icon": "🎨",
        "categories": ["Design & Branding", "Amazon Merch"],
    },
    "Niche & Research": {
        "icon": "🔍",
        "categories": ["Medical / Alt Health", "Underground Economy", "Controversial History",
                       "Privacy & OPSEC"],
    },
}

PROJECT_CATEGORIES = {
    "amazon_merch":     "Amazon Merch",
    "medical_content":  "Medical / Alt Health",
    "newsletter":       "Underground Economy",
    "trading_alpha":    "Trading & Alpha",
    "history_content":  "Controversial History",
    "privacy_guide":    "Privacy & OPSEC",
    "im_course":        "IM Course",
    "ai_automation":    "AI & Automation",
    "gmb_seo":          "GMB & Local SEO",
    "domain_flipping":  "Domain Flipping",
    "ecommerce":        "Ecommerce",
    "crypto":           "Crypto",
    "content_creation": "Content Creation",
    "lead_gen":         "Lead Generation",
    "design_branding":  "Design & Branding",
}

PROJECT_KEYWORDS = {
    "amazon_merch": {
        "keywords": ["amazon merch", "merch by amazon", "t-shirt", "pod", "print on demand",
                     "kdp", "kindle", "redbubble", "teespring"],
        "label": "Amazon Merch",
    },
    "medical_content": {
        "keywords": ["medical", "health", "cancer", "fenbendazole", "disulfiram", "suppressed cure",
                     "alternative medicine", "fda", "pharma", "treatment protocol"],
        "label": "Medical / Alt Health",
    },
    "newsletter": {
        "keywords": ["newsletter", "substack", "underground economy", "money laundering",
                     "darknet", "financial crime", "sanctions"],
        "label": "Underground Economy",
    },
    "trading_alpha": {
        "keywords": ["trading", "stocks", "options", "short selling", "fraud detection",
                     "sec", "edgar", "financial research", "alpha"],
        "label": "Trading & Alpha",
    },
    "history_content": {
        "keywords": ["history", "controversial", "conspiracy", "unit 731", "mkultra",
                     "colonial", "atrocity", "sanitized", "hidden history"],
        "label": "Controversial History",
    },
    "privacy_guide": {
        "keywords": ["privacy", "disappear", "anonymous", "burner", "off-grid",
                     "pseudonym", "data broker", "opsec", "osint"],
        "label": "Privacy & OPSEC",
    },
    "im_course": {
        "keywords": ["internet marketing", "affiliate", "funnel", "clickfunnels", "email marketing",
                     "copywriting", "sales page", "conversion", "seo", "ads", "ppc"],
        "label": "IM Course",
    },
    "ai_automation": {
        "keywords": ["ai", "automation", "gpt", "chatbot", "make.com", "zapier", "n8n",
                     "workflow", "bot", "agent", "faceless"],
        "label": "AI & Automation",
    },
    "gmb_seo": {
        "keywords": ["gmb", "google business", "local seo", "maps ranking", "google maps",
                     "citation", "review", "google my business"],
        "label": "GMB & Local SEO",
    },
    "domain_flipping": {
        "keywords": ["domain", "dropcatch", "expired domain", "backlink", "sedo",
                     "afternic", "domain flipping"],
        "label": "Domain Flipping",
    },
    "ecommerce": {
        "keywords": ["ecommerce", "shopify", "dropshipping", "woocommerce", "product research",
                     "aliexpress", "amazon fba"],
        "label": "Ecommerce",
    },
    "crypto": {
        "keywords": ["crypto", "bitcoin", "defi", "nft", "blockchain", "memecoin",
                     "trading bot", "arbitrage", "forex"],
        "label": "Crypto",
    },
    "content_creation": {
        "keywords": ["content", "writing", "blog", "youtube", "tiktok", "instagram",
                     "social media", "growth", "viral", "video", "faceless"],
        "label": "Content Creation",
    },
    "lead_gen": {
        "keywords": ["lead generation", "lead gen", "cold email", "outreach", "sales pipeline",
                     "prospecting", "list building"],
        "label": "Lead Generation",
    },
    "design_branding": {
        "keywords": ["design", "branding", "logo", "canva", "photoshop", "figma",
                     "template", "showit", "wordpress theme"],
        "label": "Design & Branding",
    },
}

MARKETING_FLUFF = [
    "game-changing", "game changer", "revolutionary", "cutting-edge", "breakthrough",
    "mind-blowing", "life-changing", "secret sauce", "insane", "crush it", "killing it",
    "never before seen", "exclusive", "proven", "battle-tested", "jaw-dropping",
    "world-class", "next level", "take your", "to the next level", "skyrocket",
    "explode your", "massive", "ultimate", "foolproof", "guaranteed",
]

def get_value_keywords():
    return {
        "high": ["masterclass", "certification", "certificate", "coaching", "mentorship",
                 "complete", "all-access", "annual", "lifetime", "done with you"],
        "medium": ["course", "training", "program", "system", "blueprint", "academy",
                   "workshop", "bootcamp"],
        "low": ["ebook", "pdf", "report", "guide", "cheat sheet", "template"],
    }
