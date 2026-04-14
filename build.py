#!/usr/bin/env python3
"""
Main build script for Happy Tools website
Refactored from monolithic app.py
"""
import os
from data_sources import get_all_tools, fetch_agents
from fallback_data import COURSES
from templates import (
    generate_index_html,
    generate_agents_html,
    generate_courses_html,
    generate_devtools_html,
    generate_about_html,
    generate_privacy_html,
    generate_scaniq_privacy_html,
    generate_scaniq_delete_html,
    generate_sitemap,
    generate_ads_txt
)


def save_files(files: dict) -> None:
    """Save generated HTML files to public directory"""
    os.makedirs("public", exist_ok=True)
    for name, content in files.items():
        with open(f"public/{name}", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ public/{name}")


def main():
    print("\n" + "=" * 60)
    print("  HAPPY TOOLS — LIVE AI DIRECTORY BUILDER")
    print("=" * 60)

    # Fetch data
    tools  = get_all_tools()
    agents = fetch_agents()

    cats = sorted(set(t.get("category", "?") for t in tools))
    print(f"\n  {len(tools)} tools across {len(cats)} categories")
    print(f"  {len(agents)} AI agents")
    print(f"  {len(COURSES)} AI courses")

    # Generate pages
    print("\n  Generating pages...")
    
    # Import robots.txt generator
    from robots_txt import generate_robots_txt
    
    save_files({
        "index.html":          generate_index_html(tools),
        "agents.html":         generate_agents_html(agents),
        "courses.html":        generate_courses_html(),
        "devtools.html":       generate_devtools_html(),
        "about.html":          generate_about_html(),
        "privacy.html":        generate_privacy_html(),
        "scaniq-privacy.html": generate_scaniq_privacy_html(),
        "scaniq-delete.html":  generate_scaniq_delete_html(),
        "sitemap.xml":         generate_sitemap(),
        "robots.txt":          generate_robots_txt(),
        "ads.txt":             generate_ads_txt(),
    })

    print("\n" + "=" * 60)
    print("  Done! Preview with:")
    print("  python3 -m http.server 8080 --directory public")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
