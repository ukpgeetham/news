import feedparser
import google.generativeai as genai
import os

# 1. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-flash-latest')
# --- Update these variables ---
LOGO_URL = "https://github.com/ukpgeetham/news/blob/main/logoht.png"
# Create a JSON-LD structured data block for the whole site
schema_data = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "The Happy Tools: Uplifting AI Summaries",
    "description": "Daily positive news and breakthroughs summarized by Gemini AI.",
    "publisher": {
        "@type": "Organization",
        "name": "The Happy Toolse",
        "logo": {"@type": "ImageObject", "url": LOGO_URL}
    }
}
# 2. Fetch News (Using "Good News" and "Science/Progress" feeds)
# You can add multiple feeds here
RSS_FEEDS = [
    "https://www.goodnewsnetwork.org/feed/",
    "https://news.google.com/rss/search?q=uplifting+news+OR+scientific+breakthrough+OR+positive+news&hl=en-US&gl=US&ceid=US:en"
]

all_entries = []
for url in RSS_FEEDS:
    feed = feedparser.parse(url)
    all_entries.extend(feed.entries)

# Sort by date to get newest first
all_entries.sort(key=lambda x: x.get('published_parsed', 0), reverse=True)

# Generate a simple XML sitemap
sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://happytools.site/</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
    <url><loc>https://happytools.site/about.html</loc></url>
    <url><loc>https://happytools.site/privacy.html</loc></url>
</urlset>"""

with open("public/sitemap.xml", "w") as f:
    f.write(sitemap_xml)

# 3. Enhanced "Uplifting" CSS
style = """
<style>
    :root { --primary: #2ecc71; --secondary: #27ae60; --bg: #f0f9f4; --text: #2c3e50; }
    body { font-family: 'Inter', sans-serif; background-color: var(--bg); color: var(--text); line-height: 1.6; margin: 0; padding: 0; }
    .container { max-width: 850px; margin: 40px auto; padding: 20px; }
    
    /* Header & Logo Styling */
    header { text-align: center; padding-bottom: 50px; border-bottom: 2px solid #d4ede0; margin-bottom: 40px; }
    .logo-img { width: 80px; height: 80px; border-radius: 50%; margin-bottom: 15px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    h1 { color: var(--primary); font-size: 3rem; margin: 0; letter-spacing: -1px; }
    
    .subtitle { font-size: 1.2rem; color: #7f8c8d; margin-top: 10px; }
    .news-card { background: white; border-radius: 15px; border-left: 5px solid var(--primary); box-shadow: 0 10px 20px rgba(46, 204, 113, 0.1); padding: 30px; margin-bottom: 30px; transition: 0.3s; }
    .news-card:hover { transform: scale(1.02); }
    .btn { display: inline-block; background: var(--primary); color: white; padding: 10px 20px; border-radius: 25px; text-decoration: none; font-weight: 600; margin-top: 15px; }
</style>
"""

# 4. Building HTML with AdSense
adsense_code = """
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2241812164647663"
     crossorigin="anonymous"></script>
"""

# 2. Build the HTML Header (Inside a Python String)
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Happy Tools | AI News</title>
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
            <img src="{LOGO_URL}" alt="Logo" class="logo-img">
            <h1>The Happy Tools</h1>
            <p class="subtitle">Your daily dose of happiness, breakthroughs, and kindness.</p>
        </header>
"""

# 5. Filter and Summarize (Top 12 items)
for entry in all_entries[:12]:
    # Custom Prompt to ensure positive framing
    prompt = (f"Rewrite this news headline into a very hopeful and inspiring 2-sentence summary. "
              f"Focus on the progress and positive impact. Headline: {entry.title}")
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except:
        continue # Skip if AI fails

    html_content += f"""
    <div class="news-card">
        <h3>{entry.title}</h3>
        <p>{summary}</p>
        <a href="{entry.link}" target="_blank" class="btn">Full Heartwarming Story &rarr;</a>
    </div>
    """

html_content += """
        <footer>
            <p>&copy; 2026 The Happy Tools.</p>
            <p><a href="about.html">About Us</a> | <a href="privacy.html">Privacy Policy</a></p>
        </footer>
    </div>
</body>
</html>
"""

# 6. Save to public folder
if not os.path.exists('public'): os.makedirs('public')
with open("public/index.html", "w", encoding='utf-8') as f:
    f.write(html_content)

# --- GENERATING LEGAL PAGES FOR ADSENSE ---

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

# Save the extra pages
with open("public/about.html", "w", encoding='utf-8') as f: f.write(about_html)
with open("public/privacy.html", "w", encoding='utf-8') as f: f.write(privacy_html)
