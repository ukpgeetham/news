"""
Generate robots.txt for SEO
"""
from config import SITE_URL

def generate_robots_txt() -> str:
    """Generate robots.txt to help search engines crawl the site"""
    return f"""# Happy Tools - Robots.txt
User-agent: *
Allow: /

# Sitemaps
Sitemap: {SITE_URL}/sitemap.xml

# Crawl-delay (optional, helps prevent overload)
Crawl-delay: 1
"""
