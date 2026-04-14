"""
HTML template generation functions
Imports from original app.py with ad divs removed
"""
import json
import re
from datetime import datetime
from typing import List, Dict
from config import SITE_URL, LOGO_URL
from fallback_data import COURSES

# Import functions from original app.py
import sys
import importlib.util

# Load app module
spec = importlib.util.spec_from_file_location("app_module", "app.py")
app_module = importlib.util.module_from_spec(spec)
sys.modules["app_module"] = app_module
spec.loader.exec_module(app_module)

# Wrapper functions that remove ad divs
def _remove_ad_divs(html: str) -> str:
    """Remove advertisement div placeholders from HTML"""
    # Remove ad-space divs
    html = re.sub(r'<div class="ad-space">.*?</div>\s*', '', html, flags=re.DOTALL)
    html = re.sub(r'\s*<div class="ad-space">.*?</div>', '', html, flags=re.DOTALL)
    return html

def generate_index_html(tools: List[Dict]) -> str:
    """Generate index.html without ad divs"""
    html = app_module.generate_index_html(tools)
    return _remove_ad_divs(html)

def generate_agents_html(agents: List[Dict]) -> str:
    """Generate agents.html without ad divs"""
    html = app_module.generate_agents_html(agents)
    return _remove_ad_divs(html)

def generate_courses_html() -> str:
    """Generate courses.html without ad divs"""
    html = app_module.generate_courses_html()
    return _remove_ad_divs(html)

def generate_devtools_html() -> str:
    """Generate devtools.html without ad divs"""
    html = app_module.generate_devtools_html()
    return _remove_ad_divs(html)

def generate_about_html() -> str:
    """Generate about.html"""
    return app_module.generate_about_html()

def generate_privacy_html() -> str:
    """Generate privacy.html"""
    return app_module.generate_privacy_html()

def generate_scaniq_privacy_html() -> str:
    """Generate scaniq-privacy.html"""
    return app_module.generate_scaniq_privacy_html()

def generate_scaniq_delete_html() -> str:
    """Generate scaniq-delete.html"""
    return app_module.generate_scaniq_delete_html()

def generate_sitemap() -> str:
    """Generate sitemap.xml"""
    pages = ["", "agents.html", "courses.html", "devtools.html", "about.html", "privacy.html", "scaniq-privacy.html"]
    urls  = "\n".join(f"  <url><loc>{SITE_URL}/{p}</loc><changefreq>weekly</changefreq></url>" for p in pages)
    return f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>"""

def generate_ads_txt() -> str:
    """Generate ads.txt for AdSense"""
    adsense_id = "ca-pub-2241812164647663"
    return f"google.com, {adsense_id}, DIRECT, f08c47fec0942fa0\n"
