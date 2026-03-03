import feedparser
import google.generativeai as genai
import os
import re
import random
import requests
import time
from datetime import datetime

# 1. SETUP & CONFIGURATION
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')

# Update these with your info
SITE_URL = "https://happytools.site" # No trailing slash
LOGO_URL = "https://raw.githubusercontent.com/ukpgeetham/news/main/logo.png"
ADSENSE_ID = "ca-pub-2241812164647663" 
# Create a JSON-LD structured data block for the whole site
schema_data = {
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
adsense_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}"
     crossorigin="anonymous"></script>
"""
# 2. TOPICS & FEEDS
TOPICS = {
    "Global News": "https://www.reutersagency.com/feed/",
    "Science": "https://www.sciencedaily.com/rss/top/science.xml",
    "Nature": "https://www.sciencedaily.com/rss/top/environment.xml",
    "Travel": "https://travel.economictimes.indiatimes.com/rss/recentstories",
    "Hollywood": "https://www.hollywoodreporter.com/feed/",
    "Entertainment": "https://variety.com/feed/",
    "Health": "https://www.health.com/rss",
    "Fitness": "https://www.outsideonline.com/health/fitness/feed/",
    "Good News": "https://www.goodnewsnetwork.org/feed/"
}

def fetch_feed_safely(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(response.content)
    except Exception as e:
        print(f"⚠️ Error fetching {url}: {e}")
        return None

def get_image(entry):
    # Fallback image if none found
    img = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800"
    if 'enclosures' in entry and entry.enclosures:
        img = entry.enclosures[0].href
    elif 'media_content' in entry:
        img = entry.media_content[0]['url']
    return img

all_entries = []
for category, url in TOPICS.items():
    print(f"Checking {category}...")
    feed = fetch_feed_safely(url)
    if feed and feed.entries[:5]:
        for entry in feed.entries:
            entry['site_category'] = category
            all_entries.append(entry)

random.shuffle(all_entries)
target_entries = all_entries[:15] 

# 3. STYLING (CSS)
style = """
<style>
    :root { --primary: #2ecc71; --dark: #2c3e50; --bg: #f8f9fa; }
    body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--dark); margin: 0; }
    .container { max-width: 1000px; margin: auto; padding: 20px; }
    
    /* Logo and Title in one line */
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
    @media (max-width: 768px) { 
        header { flex-direction: column; text-align: center; } 
        .header-text { text-align: center; }
        .card { flex-direction: column; } 
        .card img { width: 100% !important; height: 200px !important; } 
    }
    .card img { width: 300px; height: auto; object-fit: cover; }
    .card-content { padding: 25px; flex: 1; }
    .category { font-size: 0.7rem; font-weight: bold; color: var(--primary); text-transform: uppercase; }
    .btn { display: inline-block; margin-top: 15px; color: var(--primary); text-decoration: none; font-weight: bold; border: 2px solid var(--primary); padding: 6px 15px; border-radius: 20px; }
    footer { text-align: center; padding: 40px; font-size: 0.8rem; border-top: 1px solid #ddd; }
</style>
"""

# 4. FETCH AND GENERATE CONTENT
cards_html = ""
success_count = 0

for entry in target_entries:
    if success_count >= 12: break
    
    prompt = f"Rewrite this news headline into 2 hopeful sentences. Category: {entry['site_category']}. Title: {entry.title}"
    try:
        time.sleep(2)
        response = model.generate_content(prompt)
        summary = response.text
        img = get_image(entry)
        
        cards_html += f"""
        <div class="card">
            <img src="{img}" alt="news">
            <div class="card-content">
                <span class="category">{entry['site_category']}</span>
                <h3>{entry.title}</h3>
                <p>{summary}</p>
                <a href="{entry.link}" target="_blank" class="btn">Read More &rarr;</a>
            </div>
        </div>
        """
        success_count += 1
    except Exception as e:
       print(f"Skipping: {e}")
       continue
       
if success_count == 0:
    cards_html = "<div class='card'><div class='card-content'><h3>No news found today.</h3><p>Please check back later!</p></div></div>"

# 5. ASSEMBLE PAGES
index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Happy Tools</title>
    <link rel="icon" type="image/png" href="{LOGO_URL}">

    <meta name="description" content="Get your daily dose of hope. AI-summarized positive news and global breakthroughs.">
    <meta name="news_keywords" content="positive news, hope, breakthroughs, AI news summaries, uplifting stories">
    <meta property="og:title" content="Happy Tools | AI News">
    <meta property="og:description" content="Uplifting news summaries, delivered daily by AI.">
    <meta property="og:image" content="{LOGO_URL}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary_large_image">

    <script type="application/ld+json">
    {str(schema_data).replace("'", '"')}
    </script>

    {adsense_code}
    {style}
</head>
<body>
    <div class="container">
        <header>
            <img src="{LOGO_URL}" alt="Logo">
            <div class="header-text">
                <h1>The Happy Tools</h1>
                <p class="tagline">Your daily dose of AI-curated breakthroughs and kindness.</p>
            </div>
        </header>
        
        <div class="ad-space">ADVERTISEMENT</div>
        
        <div class="news-grid">
            {cards_html}
        </div>

        <footer>
            <p>&copy; 2026 The Happy Tools | <a href="about.html">About</a> | <a href="privacy.html">Privacy</a></p>
        </footer>
    </div>
</body>
</html>
"""

# Legal Pages
# 1. About Page Content
about_html = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>About Us - HappyTools</title>{style}</head>
<body><div class="container">
    <h1>About The Happy Tools</h1>
    <p>In a world often filled with heavy news, <strong>The Happy Tools</strong> was created to shine a light on human progress, scientific breakthroughs, and acts of kindness.</p>
    <p>Our mission is to provide a calm space for readers to stay informed about the positive changes happening globally. We use AI technology to curate and summarize uplifting stories from trusted sources, ensuring you get the heart of the story in seconds.</p>
    <p><a href="index.html" class="btn">Back to Home</a></p>
</div></body></html>
"""

# 2. Privacy Policy Content (Required by AdSense)
privacy_html = f"""
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Privacy Policy - The Happy Tools</title>{style}</head>
<body><div class="container">
    <h1>Privacy Policy</h1>
    <p>Your privacy is important to us. This website does not directly collect personal information from its visitors.</p>
    <h3>Cookies and Advertisements</h3>
    <p>We use Google AdSense to serve ads. Google uses cookies to serve ads based on a user's prior visits to your website or other websites. Google's use of advertising cookies enables it and its partners to serve ads to your users based on their visit to your sites and/or other sites on the Internet.</p>
    <p>Users may opt out of personalized advertising by visiting <a href="https://www.google.com/settings/ads">Google Ad Settings</a>.</p>
    <p><a href="index.html" class="btn">Back to Home</a></p>
</div></body></html>
"""

# 6. SAVE EVERYTHING
if not os.path.exists("public"): os.makedirs("public")

files = {
    "index.html": index_html,
    "about.html": about_html,
    "privacy.html": privacy_html,
    "sitemap.xml": f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{SITE_URL}/</loc></url></urlset>'
}

for filename, content in files.items():
    with open(f"public/{filename}", "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Site generated successfully in /public folder!")
