import feedparser
import google.generativeai as genai
import os

# 1. Setup Gemini
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Fetch News (Change the URL for your niche)
RSS_URL = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
feed = feedparser.parse(RSS_URL)

html_content = "<html><head><title>AI Daily News</title></head><body>"
html_content += "<h1>AI Summarized Daily News</h1>"

# 3. Process the top 5 articles
for entry in feed.entries[:5]:
    prompt = f"Summarize this news headline and link in 2 punchy sentences for a news site. Headline: {entry.title} Link: {entry.link}"
    response = model.generate_content(prompt)
    
    html_content += f"<h3>{entry.title}</h3>"
    html_content += f"<p>{response.text}</p>"
    html_content += f"<a href='{entry.link}'>Read original source</a><hr>"

html_content += "</body></html>"

# 4. Save to a folder named 'public'
if not os.path.exists('public'): os.makedirs('public')
with open("public/index.html", "w") as f:
    f.write(html_content)
