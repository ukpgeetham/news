"""
Data fetching functions for tools and agents
"""
import os
import json
import requests
from typing import List, Dict
from config import USER_AGENT, TIMEOUT, FALLBACK_IMAGE


def load_curated_tools() -> List[Dict]:
    """Source A: your own tools.json in the repo root."""
    path = "tools.json"
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            print(f"  ✓ tools.json       → {len(data)} tools")
            return data
        except Exception as e:
            print(f"  ⚠ tools.json error: {e}")
    return []


def fetch_huggingface_models() -> List[Dict]:
    """Source B: Hugging Face public model API — no key needed."""
    print("  ↻ Hugging Face models...")
    try:
        r = requests.get(
            "https://huggingface.co/api/models",
            params={"pipeline_tag": "text-generation", "sort": "downloads",
                    "direction": "-1", "limit": 30},
            headers={"User-Agent": USER_AGENT},
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        tools = []
        for m in r.json():
            mid    = m.get("modelId") or m.get("id", "")
            author = mid.split("/")[0] if "/" in mid else "HuggingFace"
            name   = mid.split("/")[-1] if "/" in mid else mid
            dl     = m.get("downloads", 0)
            tools.append({
                "name":        name,
                "category":    "Open-Source LLM",
                "pricing":     "free",
                "description": f"Open-source text-generation model by {author}. {dl:,} downloads on Hugging Face.",
                "url":         f"https://huggingface.co/{mid}",
                "tags":        ["open-source", "llm", "huggingface"],
                "image":       FALLBACK_IMAGE,
            })
        print(f"  ✓ Hugging Face     → {len(tools)} models")
        return tools
    except Exception as e:
        print(f"  ⚠ Hugging Face failed: {e}")
        return []


def fetch_github_awesome_list() -> List[Dict]:
    """Source C: community awesome-ai-tools markdown list on GitHub."""
    print("  ↻ GitHub awesome list...")
    url = ("https://raw.githubusercontent.com/"
           "mahseema/awesome-ai-tools/main/README.md")
    try:
        import re
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        r.raise_for_status()
        tools = []
        for line in r.text.splitlines():
            m = re.search(r"\[([^\]]+)\]\((https?://[^\)]+)\)", line)
            if not m:
                continue
            name = m.group(1).strip()
            link = m.group(2).strip()
            parts = [p.strip() for p in line.split("|") if p.strip()]
            desc  = parts[1] if len(parts) > 1 else ""
            desc  = re.sub(r"\[.*?\]\(.*?\)", "", desc).strip(" |-")
            if name.lower() in ("name", "tool", "---", "") or not desc or desc.startswith("---"):
                continue
            tools.append({
                "name":        name,
                "category":    "AI Tool",
                "pricing":     "freemium",
                "description": desc[:200],
                "url":         link,
                "tags":        ["ai", "tool"],
                "image":       FALLBACK_IMAGE,
            })
        print(f"  ✓ GitHub awesome   → {len(tools)} tools")
        return tools[:40]
    except Exception as e:
        print(f"  ⚠ GitHub awesome failed: {e}")
        return []


def fetch_agents() -> List[Dict]:
    """Fetch AI agents from awesome-ai-agents GitHub repo."""
    from fallback_data import AGENTS_FALLBACK
    
    print("  ↻ AI Agents data...")
    url = ("https://raw.githubusercontent.com/"
           "e2b-dev/awesome-ai-agents/main/README.md")
    try:
        import re
        r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT)
        r.raise_for_status()
        agents = []
        for line in r.text.splitlines():
            m = re.search(r"\[([^\]]+)\]\((https?://[^\)]+)\)", line)
            if not m:
                continue
            name  = m.group(1).strip()
            link  = m.group(2).strip()
            after = line[m.end():].strip(" |-:")
            desc  = re.sub(r"\[.*?\]\(.*?\)", "", after).strip(" |-:")
            if not name or name.lower() in ("name", "agent", "---") or len(desc) < 10:
                continue
            agents.append({"name": name, "type": "AI Agent", "status": "Available",
                           "description": desc[:220], "url": link, "tags": ["agent", "ai"]})
        if agents:
            existing = {a["name"].lower() for a in agents}
            for fb in AGENTS_FALLBACK:
                if fb["name"].lower() not in existing:
                    agents.append(fb)
            print(f"  ✓ Agents (live)    → {len(agents)}")
            return agents[:50]
    except Exception as e:
        print(f"  ⚠ Agents live fetch failed: {e}")
    print(f"  ✓ Agents (fallback) → {len(AGENTS_FALLBACK)}")
    return AGENTS_FALLBACK


def get_all_tools() -> List[Dict]:
    """Merge all sources and deduplicate by name."""
    from fallback_data import TOOLS_FALLBACK
    
    print("\n🔄 Fetching tools from all sources...")
    all_tools: List[Dict] = []
    seen: set = set()

    def add(batch: List[Dict]):
        for t in batch:
            key = t.get("name", "").lower().strip()
            if key and key not in seen:
                seen.add(key)
                all_tools.append(t)

    add(load_curated_tools())
    add(fetch_huggingface_models())
    add(fetch_github_awesome_list())

    # If all live sources failed and no local tools.json exists, use built-in fallback
    if not all_tools:
        print("  ⚠ No live data — using built-in fallback tools")
        add(TOOLS_FALLBACK)

    print(f"\n  ✓ Total unique tools: {len(all_tools)}")
    return all_tools
