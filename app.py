import google.generativeai as genai
import os
import random
import requests
import time
from datetime import datetime
import json
from typing import List, Dict, Optional

# ============================================================================
# 1. SETUP & CONFIGURATION
# ============================================================================
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')

NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")

SITE_URL = "https://happytools.site"
LOGO_URL = "https://raw.githubusercontent.com/ukpgeetham/news/main/logo.png"
ADSENSE_ID = "ca-pub-2241812164647663"
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

REQUEST_TIMEOUT = 15
API_CALL_DELAY = 0.2  # Reduced delay
MAX_CARDS = 12
TARGET_ENTRIES_COUNT = 20
TICKER_ITEMS_COUNT = 10

NEWS_CATEGORIES = ["technology", "science", "business", "health", "general"]

# ============================================================================
# 2. FETCH NEWS
# ============================================================================

def fetch_newsapi_articles() -> List[Dict]:
    """Fetch news from NewsAPI"""
    print("\n📰 Fetching news from NewsAPI...")
    
    if not NEWSAPI_KEY:
        print("❌ NEWSAPI_KEY not found!")
        return []
    
    all_articles = []
    headers = {"User-Agent": USER_AGENT}
    
    for category in NEWS_CATEGORIES:
        try:
            print(f"  ✓ {category.title()}", end=" ")
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "category": category,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
                "pageSize": 15,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    articles = data.get("articles", [])
                    for article in articles:
                        article["news_category"] = category.title()
                        all_articles.append(article)
                    print(f"({len(articles)} articles)")
                else:
                    print(f"(Error: {data.get('message', 'Unknown')})")
            else:
                print(f"(HTTP {response.status_code})")
        
        except Exception as e:
            print(f"(Failed: {str(e)[:30]})")
    
    print(f"\n✓ Total: {len(all_articles)} articles fetched")
    return all_articles


def filter_positive_news(articles: List[Dict]) -> List[Dict]:
    """Filter for positive stories - NO AI CALLS"""
    POSITIVE_KEYWORDS = [
        "breakthrough", "success", "innovation", "recovery", "progress",
        "achievement", "award", "discovery", "new", "improvement",
        "green", "sustainable", "recovery", "wins", "achieves"
    ]
    
    NEGATIVE_KEYWORDS = [
        "death", "killed", "accident", "disaster", "crash", "shooting",
        "war", "conflict", "crisis", "attack", "died", "tragedy"
    ]
    
    print(f"\n⭐ Filtering {len(articles)} for positive stories...")
    filtered = []
    
    for article in articles:
        title = (article.get("title") or "").lower()
        description = (article.get("description") or "").lower()
        combined = f"{title} {description}"
        
        # Skip if has negative keywords
        if any(kw in combined for kw in NEGATIVE_KEYWORDS):
            continue
        
        # Score positive keywords
        score = sum(1 for kw in POSITIVE_KEYWORDS if kw in combined)
        
        # Only include if description exists
        if description and len(description) > 30:
            article["positivity_score"] = score
            filtered.append(article)
    
    filtered.sort(key=lambda x: (-x.get("positivity_score", 0)), reverse=True)
    print(f"✓ Found {len(filtered)} positive articles")
    
    return filtered


def get_article_image(article: Dict) -> str:
    """Get image with validation"""
    image_url = article.get("urlToImage") or ""
    if image_url and "http" in image_url and "null" not in image_url.lower():
        return image_url
    return FALLBACK_IMAGE


def clean_summary(text: str) -> str:
    """Clean and truncate summary"""
    # Remove extra whitespace
    text = " ".join(text.split())
    # Truncate to ~200 chars
    if len(text) > 200:
        text = text[:200] + "..."
    return text.replace('"', '&quot;')


# ============================================================================
# 3. HTML GENERATION
# ============================================================================

STYLE = """
<style>
    :root { --primary: #2ecc71; --dark: #2c3e50; --bg: #f8f9fa; }
    * { box-sizing: border-box; }
    body { font-family: 'Inter', -apple-system, sans-serif; background: var(--bg); color: var(--dark); margin: 0; }
    .container { max-width: 1000px; margin: auto; padding: 20px; }
    
    .ticker-wrap { width: 100%; overflow: hidden; background: var(--dark); color: white; padding: 10px 0; position: sticky; top: 0; z-index: 1000; }
    .ticker { white-space: nowrap; display: inline-block; animation: marquee 50s linear infinite; font-weight: bold; font-size: 0.9rem; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    header { display: flex; align-items: center; justify-content: center; gap: 20px; padding: 40px 0; border-bottom: 1px solid #ddd; margin-bottom: 40px; }
    .logo { width: 80px; height: 80px; border-radius: 50%; object-fit: cover; }
    h1 { font-size: 2.2rem; margin: 0; color: var(--primary); }
    .tagline { margin: 5px 0 0; font-size: 1rem; color: #666; }

    .news-grid { display: grid; gap: 30px; }
    .card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); display: flex; transition: all 0.3s; }
    .card:hover { box-shadow: 0 8px 20px rgba(0,0,0,0.12); transform: translateY(-2px); }
    
    .card img { width: 280px; height: auto; object-fit: cover; flex-shrink: 0; }
    .card-content { padding: 20px; flex: 1; display: flex; flex-direction: column; }
    .category { font-size: 0.75rem; font-weight: bold; color: var(--primary); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; }
    .card h3 { margin: 0 0 10px; font-size: 1.2rem; line-height: 1.3; }
    .card p { margin: 0 0 12px; color: #555; line-height: 1.5; flex-grow: 1; font-size: 0.95rem; }
    .source { font-size: 0.8rem; color: #999; margin-bottom: 10px; }
    .btn { display: inline-block; color: var(--primary); text-decoration: none; font-weight: 600; border: 2px solid var(--primary); padding: 6px 14px; border-radius: 20px; }
    .btn:hover { background: var(--primary); color: white; }
    
    @media (max-width: 768px) { 
        header { flex-direction: column; gap: 15px; }
        .card { flex-direction: column; } 
        .card img { width: 100%; height: 200px; } 
    }
    
    footer { text-align: center; padding: 30px; font-size: 0.85rem; border-top: 1px solid #ddd; color: #999; }
    .ad-space { text-align: center; padding: 20px; background: #f0f0f0; border-radius: 8px; margin: 20px 0; }
</style>
"""

ADSENSE_CODE = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}"
     crossorigin="anonymous"></script>
"""

def generate_card_html(article: Dict) -> str:
    """Generate card using NewsAPI description (NO AI)"""
    title = article.get("title", "Untitled")
    description = article.get("description") or article.get("content", "")
    
    # Use description as summary
    summary = clean_summary(description)
    
    if not summary or len(summary) < 20:
        return ""
    
    image_url = get_article_image(article)
    article_url = article.get("url", "#")
    category = article.get("news_category", "News")
    source = article.get("source", {}).get("name", "News")
    
    return f"""
    <div class="card">
        <img src="{image_url}" alt="{title}" loading="lazy" onerror="this.src='{FALLBACK_IMAGE}'">
        <div class="card-content">
            <span class="category">{category}</span>
            <h3>{title}</h3>
            <p>{summary}</p>
            <div class="source">📰 {source}</div>
            <a href="{article_url}" target="_blank" rel="noopener noreferrer" class="btn">Read More →</a>
        </div>
    </div>"""


def generate_cards_html(articles: List[Dict]) -> str:
    """Generate all cards quickly (NO AI RATE LIMITS)"""
    print(f"\n🎨 Generating {min(MAX_CARDS, len(articles))} cards...")
    cards = []
    
    for i, article in enumerate(articles):
        if len(cards) >= MAX_CARDS:
            break
        
        card = generate_card_html(article)
        if card:
            cards.append(card)
            print(f"  ✓ Card {len(cards)}: {article['title'][:50]}...")
    
    if not cards:
        return '<div style="padding:20px; text-align:center;"><h3>📭 No articles available today</h3></div>'
    
    print(f"✓ Generated {len(cards)} cards")
    return "".join(cards)


def generate_index_html(cards_html: str, ticker_text: str) -> str:
    """Generate index.html"""
    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": "The Happy Tools",
        "description": "Positive news updates daily",
    })
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Daily positive news and breakthroughs.">
    <title>The Happy Tools - Positive News</title>
    <link rel="icon" type="image/png" href="{LOGO_URL}">
    {ADSENSE_CODE}
    {STYLE}
    <script type="application/ld+json">{schema}</script>
</head>
<body>
    <div class="ticker-wrap">
        <div class="ticker">🌟 {ticker_text} 🌟</div>
    </div>
    <div class="container">
        <header>
            <img src="{LOGO_URL}" alt="Logo" class="logo">
            <div>
                <h1>The Happy Tools</h1>
                <p class="tagline">Your daily dose of positive news</p>
            </div>
        </header>
        
        <div class="ad-space">ADVERTISEMENT</div>
        
        <div class="news-grid">
            {cards_html}
        </div>

        <footer>
            <p>&copy; 2026 The Happy Tools | <a href="about.html">About</a> | <a href="privacy.html">Privacy</a></p>
            <p>Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </footer>
    </div>
</body>
</html>"""


def generate_about_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>About - The Happy Tools</title>{STYLE}</head>
<body><div class="container">
<h1>About The Happy Tools</h1>
<p>In a world filled with heavy news, we celebrate progress and positive change. All stories curated from trusted news sources and presented to you daily.</p>
<p><a href="index.html" class="btn">← Back to Home</a></p>
</div></body></html>"""


def generate_privacy_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Privacy - The Happy Tools</title>{STYLE}</head>
<body><div class="container">
<h1>Privacy Policy</h1>
<p>We don't collect personal information. We use Google AdSense for ads, which may use cookies.</p>
<p><a href="https://www.google.com/settings/ads">Manage Google Ads</a></p>
<p><a href="index.html" class="btn">← Back to Home</a></p>
</div></body></html>"""


def generate_sitemap() -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
<url><loc>{SITE_URL}/</loc><changefreq>daily</changefreq></url>
</urlset>"""


def save_files(files_dict: Dict[str, str]) -> None:
    """Save to public directory"""
    os.makedirs("public", exist_ok=True)
    
    for filename, content in files_dict.items():
        with open(f"public/{filename}", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ Saved {filename}")


# ============================================================================
# 4. MAIN
# ============================================================================

def main():
    print("\n" + "="*70)
    print("🚀 THE HAPPY TOOLS - NEWS GENERATOR")
    print("="*70)
    
    # Fetch
    articles = fetch_newsapi_articles()
    if not articles:
        print("❌ No articles fetched. Check NEWSAPI_KEY.")
        return
    
    # Filter
    positive = filter_positive_news(articles)
    if not positive:
        print("⚠️ No positive articles found.")
        return
    
    # Shuffle and select
    random.shuffle(positive)
    selected = positive[:TARGET_ENTRIES_COUNT]
    
    # Ticker
    ticker = " • ".join([a['title'][:35] for a in selected[:TICKER_ITEMS_COUNT]])
    
    # Generate HTML (NO AI CALLS!)
    cards = generate_cards_html(selected)
    
    # Save
    print("\n💾 Saving files...")
    save_files({
        "index.html": generate_index_html(cards, ticker),
        "about.html": generate_about_html(),
        "privacy.html": generate_privacy_html(),
        "sitemap.xml": generate_sitemap()
    })
    
    print("\n" + "="*70)
    print("✅ SUCCESS! Site generated and ready to deploy.")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
