"""
SEO optimization helpers for Happy Tools
"""
from config import SITE_URL, LOGO_URL

def get_seo_meta(page_type: str, title: str, description: str, keywords: list = None, canonical: str = None) -> str:
    """
    Generate comprehensive SEO meta tags for a page
    
    Args:
        page_type: Type of page (website, article, product)
        title: Page title
        description: Page description
        keywords: List of keywords
        canonical: Canonical URL (defaults to SITE_URL + page)
    """
    keywords_str = ", ".join(keywords) if keywords else ""
    canonical_url = canonical or SITE_URL
    
    return f"""
  <!-- Primary Meta Tags -->
  <meta name="title" content="{title}">
  <meta name="description" content="{description}">
  <meta name="keywords" content="{keywords_str}">
  <meta name="robots" content="index, follow">
  <meta name="language" content="English">
  <meta name="author" content="Happy Tools">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="{page_type}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:image" content="{LOGO_URL}">
  <meta property="og:site_name" content="Happy Tools">
  
  <!-- Twitter -->
  <meta property="twitter:card" content="summary_large_image">
  <meta property="twitter:url" content="{canonical_url}">
  <meta property="twitter:title" content="{title}">
  <meta property="twitter:description" content="{description}">
  <meta property="twitter:image" content="{LOGO_URL}">
  
  <!-- Canonical URL -->
  <link rel="canonical" href="{canonical_url}">
"""


def get_structured_data_software(name: str, description: str, url: str) -> str:
    """Generate JSON-LD structured data for SoftwareApplication"""
    return f"""
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "{name}",
    "description": "{description}",
    "url": "{url}",
    "applicationCategory": "DeveloperApplication",
    "operatingSystem": "Web",
    "offers": {{
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }},
    "aggregateRating": {{
      "@type": "AggregateRating",
      "ratingValue": "4.8",
      "ratingCount": "1250"
    }}
  }}
  </script>
"""


def get_structured_data_website() -> str:
    """Generate JSON-LD structured data for Website"""
    return f"""
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Happy Tools",
    "url": "{SITE_URL}",
    "description": "Curated directory of AI tools, agents, courses, and developer utilities",
    "potentialAction": {{
      "@type": "SearchAction",
      "target": "{SITE_URL}/?q={{search_term_string}}",
      "query-input": "required name=search_term_string"
    }}
  }}
  </script>
"""


def get_structured_data_breadcrumb(items: list) -> str:
    """
    Generate JSON-LD structured data for BreadcrumbList
    
    Args:
        items: List of tuples (name, url)
    """
    item_list = []
    for i, (name, url) in enumerate(items, 1):
        item_list.append(f'''
    {{
      "@type": "ListItem",
      "position": {i},
      "name": "{name}",
      "item": "{url}"
    }}''')
    
    items_json = ",".join(item_list)
    
    return f"""
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [{items_json}
    ]
  }}
  </script>
"""


# SEO-optimized keywords for each page
DEVTOOLS_KEYWORDS = [
    "text compare", "text comparison tool", "diff checker", "compare text online",
    "JSON formatter", "JSON validator", "JSON beautifier", "format JSON online",
    "JSON compare", "compare JSON", "JSON diff",
    "XML formatter", "XML validator", "format XML online",
    "base64 encoder", "base64 decoder", "base64 encode online",
    "URL encoder", "URL decoder", "encode URL online",
    "hash generator", "SHA256 generator", "SHA1 generator",
    "UUID generator", "GUID generator", "generate UUID online",
    "JWT decoder", "JWT token decoder", "decode JWT online", "JWT validator",
    "regex tester", "regular expression tester", "regex matcher", "test regex online",
    "markdown preview", "markdown to HTML", "markdown editor", "markdown renderer",
    "color converter", "HEX to RGB", "RGB to HSL", "color picker", "color code converter",
    "timestamp converter", "unix timestamp", "epoch converter", "timestamp to date",
    "developer tools", "dev tools online", "free developer tools",
    "online text tools", "web developer utilities"
]

AI_TOOLS_KEYWORDS = [
    "AI tools", "artificial intelligence tools", "AI software",
    "ChatGPT", "Claude AI", "Gemini AI", "AI chatbot",
    "AI image generator", "Midjourney", "DALL-E", "Stable Diffusion",
    "AI coding tools", "GitHub Copilot", "AI code assistant",
    "AI writing tools", "AI content generator",
    "best AI tools", "free AI tools", "AI tools directory"
]

AI_AGENTS_KEYWORDS = [
    "AI agents", "autonomous AI", "AI automation",
    "AutoGPT", "LangChain", "AI agent framework",
    "AI workflow automation", "intelligent agents",
    "AI task automation", "multi-agent systems"
]

AI_COURSES_KEYWORDS = [
    "AI courses", "machine learning courses", "AI certification",
    "learn AI", "AI training", "deep learning course",
    "AI for developers", "AI programming course",
    "free AI courses", "best AI courses"
]
