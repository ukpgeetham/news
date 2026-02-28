import feedparser
import google.generativeai as genai
import os
import re
from datetime import datetime

# 1. SETUP & CONFIGURATION
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')

# Update these with your info
SITE_URL = "https://happytools.site" # No trailing slash
LOGO_URL = "https://raw.githubusercontent.com/ukpgeetham/news/main/logoht.png"
ADSENSE_ID = "ca-pub-2241812164647663" 

# 2. TOPICS & FEEDS
TOPICS = {
    "Science & Nature": "https://www.sciencedaily.com/rss/top/environment.xml",
    "Travel & Culture": "https://travel.economictimes.indiatimes.com/rss/recentstories",
    "Hollywood & Entertainment": "https://www.hollywoodreporter.com/feed/",
    "Fitness & Health": "https://www.health.com/rss",
    "Positive News": "https://www.goodnewsnetwork.org/feed/"
}

def get_image(entry):
    """Extracts image URL from RSS entry tags."""
    if 'enclosures' in entry and len(entry.enclosures) > 0:
        return entry.enclosures[0].href
    if 'media_content' in entry:
        return entry.media_content[0]['url']
    img_match = re.search(r'<img src="([^"]+)"', entry.get('description', ''))
    if img_match:
        return img_match.group(1)
    return "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800&q=80"

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
all_news_cards = ""
for category, url in TOPICS.items():
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]: # Takes top 3 from each category (Total 15)
        img_url = get_image(entry)
        
        # SEO-friendly Summarization
        prompt = f"Rewrite this news headline into a hopeful, engaging 2-sentence summary. Category: {category}. Title: {entry.title}"
        try:
            summary = model.generate_content(prompt).text
            all_news_cards += f"""
            <div class="card">
                <img src="{img_url}" alt="{entry.title}">
                <div class="card-content">
                    <span class="category">{category}</span>
                    <h3>{entry.title}</h3>
                    <p>{summary}</p>
                    <a href="{entry.link}" target="_blank" class="btn">Read Source &rarr;</a>
                </div>
            </div>
            """
        except: continue

# 5. ASSEMBLE PAGES
index_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>The Happy Tools | Daily Uplifting News Summaries</title>
    <meta name="description" content="AI-summarized positive news from Hollywood, Science, Travel, and Health.">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
    {style}
</head>
<body>
    <div class="container">
        <header>
            <img src="{LOGO_URL}" class="logo" alt="Logo">
            <h1>Happy Tools</h1>
            <p>Your daily dose of AI-curated breakthroughs and kindness.</p>
        </header>
        
        <div class="ad-space">ADVERTISEMENT</div>
        
        <div class="news-grid">
            {all_news_cards}
        </div>

        <footer>
            <p>&copy; 2026 The Happy Tools | <a href="about.html">About</a> | <a href="privacy.html">Privacy</a></p>
        </footer>
    </div>
</body>
</html>
"""

# Legal Pages
about_html = f"<!DOCTYPE html><html><head><title>About Us</title>{style}</head><body><div class='container'><h1>About Us</h1><p>We use AI to summarize positive news.</p><a href='index.html'>Back Home</a></div></body></html>"
privacy_html = f"<!DOCTYPE html><html><head><title>Privacy Policy</title>{style}</head><body><div class='container'><h1>Privacy Policy</h1><p>We use Google AdSense cookies for ads.</p><a href='index.html'>Back Home</a></div></body></html>"

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
