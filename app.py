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

# API Keys - Get yours from:
# NewsAPI: https://newsapi.org/
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")  # REQUIRED for newsapi.org
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY", "")  # Optional backup

# Configuration Constants
SITE_URL = "https://happytools.site"
LOGO_URL = "https://raw.githubusercontent.com/ukpgeetham/news/main/logo.png"
ADSENSE_ID = "ca-pub-2241812164647663"
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

# Request & Processing Configuration
REQUEST_TIMEOUT = 15
API_CALL_DELAY = 0.5  # Reduced delay between Gemini API calls
MAX_CARDS = 12
TARGET_ENTRIES_COUNT = 20  # Increased for better filtering
TICKER_ITEMS_COUNT = 10

# ============================================================================
# 2. NEWS SOURCES & CATEGORIES
# ============================================================================
NEWS_CATEGORIES = [
    "technology",
    "science", 
    "business",
    "health",
    "general"
]

# Keywords to prioritize positive stories
POSITIVE_KEYWORDS = [
    "breakthrough", "success", "innovation", "recovery", "progress",
    "achievement", "award", "discovery", "new", "improvement",
    "green energy", "sustainability", "conservation", "medical breakthrough"
]

# Keywords to avoid negative stories
NEGATIVE_KEYWORDS = [
    "death", "killed", "accident", "disaster", "crash", "shooting",
    "war", "conflict", "crisis", "emergency", "attack", "scandal"
]

# ============================================================================
# 3. STYLING (CSS) - Extracted to constant
# ============================================================================
STYLE = """
<style>
    :root { --primary: #2ecc71; --dark: #2c3e50; --bg: #f8f9fa; }
    body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; background: var(--bg); color: var(--dark); margin: 0; }
    .container { max-width: 1000px; margin: auto; padding: 20px; }
    
    /* Live Ticker Styling */
    .ticker-wrap { width: 100%; overflow: hidden; background: var(--dark); color: white; padding: 10px 0; position: sticky; top: 0; z-index: 1000; }
    .ticker { white-space: nowrap; display: inline-block; animation: marquee 40s linear infinite; font-weight: bold; font-size: 0.9rem; }
    @keyframes marquee { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
    
    /* Logo and Title */
    header { 
        display: flex; 
        align-items: center; 
        justify-content: center; 
        gap: 20px; 
        padding: 40px 0; 
        border-bottom: 1px solid #ddd; 
        margin-bottom: 40px; 
    }
    .logo { width: 80px; height: 80px; border-radius: 60%; object-fit: cover; }
    .header-text { text-align: left; }
    h1 { font-size: 2.2rem; margin: 0; color: var(--primary); line-height: 1; }
    .tagline { margin: 5px 0 0 0; font-size: 1rem; color: #666; }

    .news-grid { display: grid; grid-row-gap: 30px; }
    .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); display: flex; transition: 0.3s; }
    .card:hover { box-shadow: 0 8px 25px rgba(0,0,0,0.1); transform: translateY(-2px); }
    
    @media (max-width: 768px) { 
        header { flex-direction: column; text-align: center; } 
        .header-text { text-align: center; }
        .card { flex-direction: column; } 
        .card img { width: 100% !important; height: 200px !important; } 
    }
    
    .card img { width: 300px; height: auto; object-fit: cover; flex-shrink: 0; }
    .card-content { padding: 25px; flex: 1; display: flex; flex-direction: column; }
    .category { font-size: 0.75rem; font-weight: bold; color: var(--primary); text-transform: uppercase; letter-spacing: 0.5px; }
    .card h3 { margin: 12px 0 10px; font-size: 1.3rem; line-height: 1.4; }
    .card p { margin: 0 0 15px; color: #555; line-height: 1.6; flex-grow: 1; }
    .source { font-size: 0.8rem; color: #999; margin-top: 10px; }
    .btn { display: inline-block; color: var(--primary); text-decoration: none; font-weight: bold; border: 2px solid var(--primary); padding: 8px 18px; border-radius: 20px; transition: 0.3s; }
    .btn:hover { background: var(--primary); color: white; }
    footer { text-align: center; padding: 40px; font-size: 0.8rem; border-top: 1px solid #ddd; color: #666; }
</style>
"""

# Schema Data for SEO
SCHEMA_DATA = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "The Happy Tools: Uplifting AI Summaries",
    "description": "Daily positive news and breakthroughs summarized by Gemini AI.",
    "publisher": {
        "@type": "Organization",
        "name": "Happy Tools",
        "logo": {"@type": "ImageObject", "url": LOGO_URL}
    }
}

ADSENSE_CODE = f"""
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}"
     crossorigin="anonymous"></script>
"""

# ============================================================================
# 4. HELPER FUNCTIONS - FETCH NEWS
# ============================================================================

def fetch_newsapi_articles() -> List[Dict]:
    """
    Fetch news from NewsAPI.org - PRIMARY SOURCE
    Reliable, well-structured, covers many sources
    """
    if not NEWSAPI_KEY:
        print("❌ NEWSAPI_KEY not set! Get it from https://newsapi.org/")
        return []
    
    all_articles = []
    headers = {"User-Agent": USER_AGENT}
    
    for category in NEWS_CATEGORIES:
        try:
            url = "https://newsapi.org/v2/top-headlines"
            params = {
                "category": category,
                "language": "en",
                "apiKey": NEWSAPI_KEY,
                "pageSize": 15,
                "sortBy": "publishedAt"
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if data.get("status") == "ok":
                for article in data.get("articles", []):
                    # Add category metadata
                    article["news_category"] = category.title()
                    article["source_type"] = "NewsAPI"
                    all_articles.append(article)
                    print(f"✓ NewsAPI [{category}]: {article['title'][:50]}...")
            else:
                print(f"⚠️ NewsAPI returned status: {data.get('status')}")
        
        except requests.exceptions.RequestException as e:
            print(f"⚠️ NewsAPI error for {category}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error fetching {category}: {e}")
    
    return all_articles


def fetch_newsapi_search(query: str, limit: int = 15) -> List[Dict]:
    """Search for specific positive news topics via NewsAPI"""
    if not NEWSAPI_KEY:
        return []
    
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": "en",
            "apiKey": NEWSAPI_KEY,
            "pageSize": limit,
            "sortBy": "publishedAt",
            "from": (datetime.now().strftime('%Y-%m-%d'))
        }
        
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        data = response.json()
        if data.get("status") == "ok":
            for article in data.get("articles", []):
                article["news_category"] = f"Search: {query.title()}"
                article["source_type"] = "NewsAPI"
            print(f"✓ Found {len(data.get('articles', []))} articles for '{query}'")
            return data.get("articles", [])
    
    except Exception as e:
        print(f"⚠️ NewsAPI search error: {e}")
    
    return []


def filter_positive_news(articles: List[Dict]) -> List[Dict]:
    """Filter articles to prioritize positive stories and remove negative ones"""
    filtered = []
    
    for article in articles:
        title = article.get("title", "").lower()
        description = (article.get("description") or "").lower()
        combined = f"{title} {description}"
        
        # Check for negative keywords
        has_negative = any(keyword in combined for keyword in NEGATIVE_KEYWORDS)
        if has_negative:
            continue
        
        # Bonus points for positive keywords
        score = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in combined)
        article["positivity_score"] = score
        filtered.append(article)
    
    # Sort by positivity score, then by published date
    filtered.sort(key=lambda x: (-x.get("positivity_score", 0), x.get("publishedAt", "")), reverse=True)
    
    return filtered


# ============================================================================
# 5. HELPER FUNCTIONS - GENERATE SUMMARIES
# ============================================================================

def generate_ai_summary(article: Dict, retry_count: int = 2) -> Optional[str]:
    """
    Generate an engaging, uplifting summary using Gemini
    Better error handling with retries
    """
    title = article.get("title", "")
    description = article.get("description", "") or ""
    category = article.get("news_category", "General")
    
    if not title:
        return None
    
    # Combine title and description for better context
    content = f"{title}. {description}" if description else title
    
    prompt = f"""You are a positive news curator for "The Happy Tools" - a website celebrating human progress and positivity.

Given this news article, write a 2-3 sentence UPLIFTING summary that:
1. Highlights the positive impact or progress
2. Uses hopeful, engaging language
3. Focuses on solutions and achievements
4. Avoids fear-mongering or negativity

Article:
{content}

Category: {category}

Write ONLY the summary, nothing else:"""
    
    for attempt in range(retry_count):
        try:
            response = model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": 150,
                    "temperature": 0.7
                }
            )
            
            if response and response.text:
                summary = response.text.strip()
                if len(summary) > 20:  # Ensure we got actual content
                    return summary
        
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"  ⟳ Retry {attempt + 1} for summary...")
                time.sleep(1)
            else:
                print(f"  ❌ Summary generation failed: {e}")
    
    return None


def get_article_image(article: Dict) -> str:
    """Get image URL from article with fallback"""
    image_url = article.get("urlToImage") or ""
    
    # Validate URL is not empty and doesn't contain error patterns
    if image_url and "http" in image_url and "null" not in image_url.lower():
        return image_url
    
    return FALLBACK_IMAGE


# ============================================================================
# 6. HTML GENERATION
# ============================================================================

def generate_card_html(article: Dict) -> Optional[str]:
    """Generate a single news card HTML with complete error handling"""
    try:
        # Generate summary
        summary = generate_ai_summary(article)
        if not summary:
            print(f"  ⊘ Skipped (no summary): {article['title'][:40]}...")
            return None
        
        # Get article data
        title = article.get("title", "Untitled")[:150]  # Limit title length
        image_url = get_article_image(article)
        article_url = article.get("url", "#")
        category = article.get("news_category", "News")
        source = article.get("source", {}).get("name", "Source")
        
        # Sanitize summary
        summary = summary.replace('"', '&quot;').replace('\n', ' ')
        
        card_html = f"""
        <div class="card">
            <img src="{image_url}" alt="{title}" loading="lazy" onerror="this.src='{FALLBACK_IMAGE}'">
            <div class="card-content">
                <span class="category">{category}</span>
                <h3>{title}</h3>
                <p>{summary}</p>
                <div class="source">Source: {source}</div>
                <a href="{article_url}" target="_blank" rel="noopener noreferrer" class="btn">Read Full Story →</a>
            </div>
        </div>"""
        
        return card_html
    
    except Exception as e:
        print(f"  ❌ Card generation failed: {e}")
        return None


def generate_cards_html(articles: List[Dict]) -> str:
    """Generate HTML for all news cards with progress tracking"""
    cards_html_list = []
    success_count = 0
    
    print(f"\n📝 Generating {min(MAX_CARDS, len(articles))} cards...")
    
    for i, article in enumerate(articles):
        if success_count >= MAX_CARDS:
            break
        
        print(f"  [{i+1}/{len(articles)}] Processing: {article['title'][:45]}...")
        
        card_html = generate_card_html(article)
        if card_html:
            cards_html_list.append(card_html)
            success_count += 1
            print(f"    ✓ Card #{success_count} generated")
        
        # Rate limiting - be respectful to Gemini API
        time.sleep(API_CALL_DELAY)
    
    if not cards_html_list:
        return """<div class='card'><div class='card-content'>
                    <h3>📭 No news found today</h3>
                    <p>We couldn't find enough positive stories today. Please check back later!</p>
                  </div></div>"""
    
    print(f"✅ Generated {success_count} cards successfully\n")
    return "".join(cards_html_list)


def generate_meta_tags() -> str:
    """Generate meta tags for SEO"""
    schema_json = json.dumps(SCHEMA_DATA)
    return f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Get your daily dose of hope. AI-summarized positive news and global breakthroughs.">
    <meta name="keywords" content="positive news, hope, breakthroughs, AI summaries, uplifting stories, good news">
    <meta property="og:title" content="The Happy Tools | AI News">
    <meta property="og:description" content="Uplifting news summaries, delivered daily by AI.">
    <meta property="og:image" content="{LOGO_URL}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">
    
    <script type="application/ld+json">
    {schema_json}
    </script>
    """


def generate_index_html(cards_html: str, ticker_text: str) -> str:
    """Generate index.html content"""
    meta_tags = generate_meta_tags()
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    {meta_tags}
    <title>The Happy Tools | Positive News Summaries</title>
    <link rel="icon" type="image/png" href="{LOGO_URL}">
    {ADSENSE_CODE}
    {STYLE}
</head>
<body>
    <div class="ticker-wrap">
        <div class="ticker">🌟 {ticker_text} 🌟</div>
    </div>
    <div class="container">
        <header>
            <img src="{LOGO_URL}" alt="Logo" class="logo">
            <div class="header-text">
                <h1>The Happy Tools</h1>
                <p class="tagline">Your daily dose of breakthroughs and kindness.</p>
            </div>
        </header>
        
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
    """Generate about.html content"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About Us - The Happy Tools</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <h1>About The Happy Tools</h1>
        <p>In a world often filled with heavy news, <strong>The Happy Tools</strong> was created to shine a light on human progress, scientific breakthroughs, and acts of kindness.</p>
        <p><strong>Our mission</strong> is to provide a calm, uplifting space for readers to stay informed about positive changes happening globally. We use AI technology to curate and summarize stories that inspire hope and demonstrate human achievement.</p>
        
        <h2>How It Works</h2>
        <ul>
            <li>🔍 We source news from trusted outlets using NewsAPI</li>
            <li>✨ We filter for positive, constructive stories</li>
            <li>🤖 Our Gemini AI generates hopeful, engaging summaries</li>
            <li>📱 We deliver clean, beautiful articles you can read in seconds</li>
        </ul>
        
        <h2>Why We Started This</h2>
        <p>News fatigue is real. While it's important to stay informed, constant exposure to negative headlines can affect mental health. The Happy Tools offers an alternative—a space where progress, innovation, and kindness are celebrated.</p>
        
        <p><a href="index.html" class="btn">← Back to Home</a></p>
    </div>
</body>
</html>"""


def generate_privacy_html() -> str:
    """Generate privacy.html content"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Privacy Policy - The Happy Tools</title>
    {STYLE}
</head>
<body>
    <div class="container">
        <h1>Privacy Policy</h1>
        <p>Your privacy is important to us. This website does not directly collect personal information from its visitors.</p>
        
        <h3>Cookies and Advertisements</h3>
        <p>We use Google AdSense to serve ads. Google uses cookies to serve relevant ads based on your browsing history. You can manage your ad preferences through Google Ad Settings.</p>
        <p><a href="https://www.google.com/settings/ads" target="_blank">Manage your Google Ad Settings</a></p>
        
        <h3>External Services</h3>
        <p>This website uses:</p>
        <ul>
            <li><strong>NewsAPI.org</strong> - for news data</li>
            <li><strong>Google Gemini AI</strong> - for content summarization</li>
            <li><strong>Google AdSense</strong> - for advertising</li>
        </ul>
        
        <p><a href="index.html" class="btn">← Back to Home</a></p>
    </div>
</body>
</html>"""


def generate_sitemap() -> str:
    """Generate sitemap.xml content"""
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{SITE_URL}/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url>
        <loc>{SITE_URL}/about.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
    <url>
        <loc>{SITE_URL}/privacy.html</loc>
        <changefreq>monthly</changefreq>
        <priority>0.8</priority>
    </url>
</urlset>"""


def save_files(files_dict: Dict[str, str]) -> None:
    """Save all generated files to disk"""
    if not os.path.exists("public"):
        os.makedirs("public")
        print("📁 Created 'public' directory")
    
    for filename, content in files_dict.items():
        try:
            with open(f"public/{filename}", "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Saved: public/{filename}")
        except Exception as e:
            print(f"❌ Error saving {filename}: {e}")


# ============================================================================
# 7. MAIN EXECUTION
# ============================================================================

def main():
    """Main orchestration function"""
    print("=" * 60)
    print("🚀 THE HAPPY TOOLS - AI NEWS GENERATOR")
    print("=" * 60)
    
    # Fetch news from primary source
    print("\n📰 Fetching news...")
    articles = fetch_newsapi_articles()
    
    # Add positive search results
    print("\n🔍 Searching for positive news keywords...")
    positive_searches = fetch_newsapi_search("breakthrough discovery innovation", limit=10)
    articles.extend(positive_searches)
    
    # Remove duplicates by URL
    seen_urls = set()
    unique_articles = []
    for article in articles:
        url = article.get("url")
        if url and url not in seen_urls:
            unique_articles.append(article)
            seen_urls.add(url)
    
    print(f"\n✓ Fetched {len(unique_articles)} articles")
    
    if not unique_articles:
        print("❌ No articles fetched! Check your NEWSAPI_KEY")
        return
    
    # Filter for positive stories
    print("\n⭐ Filtering for positive stories...")
    positive_articles = filter_positive_news(unique_articles)
    print(f"✓ Found {len(positive_articles)} positive articles")
    
    # Shuffle and select
    random.shuffle(positive_articles)
    target_articles = positive_articles[:TARGET_ENTRIES_COUNT]
    
    # Create ticker text
    ticker_items = [
        f"{article['title'][:40]}..." 
        for article in target_articles[:TICKER_ITEMS_COUNT]
    ]
    ticker_text = "  •  ".join(ticker_items)
    
    # Generate cards HTML
    cards_html = generate_cards_html(target_articles)
    
    # Generate all pages
    print("\n🎨 Generating HTML pages...")
    files_to_save = {
        "index.html": generate_index_html(cards_html, ticker_text),
        "about.html": generate_about_html(),
        "privacy.html": generate_privacy_html(),
        "sitemap.xml": generate_sitemap()
    }
    
    # Save files
    print("\n💾 Saving files...")
    save_files(files_to_save)
    
    print("\n" + "=" * 60)
    print("✅ SITE GENERATED SUCCESSFULLY!")
    print("📁 Files saved to: /public folder")
    print("=" * 60)


if __name__ == "__main__":
    main()
