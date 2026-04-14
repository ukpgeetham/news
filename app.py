import os
import json
import requests
from datetime import datetime
from typing import List, Dict

# ============================================================================
# 1. CONFIGURATION
# ============================================================================

SITE_URL       = "https://happytools.site"
LOGO_URL       = "https://raw.githubusercontent.com/ukpgeetham/news/main/logo.png"
ADSENSE_ID     = "ca-pub-2241812164647663"
FALLBACK_IMAGE = "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800"
USER_AGENT     = "Mozilla/5.0 (compatible; HappyToolsBot/1.0)"
TIMEOUT        = 15

# ============================================================================
# 2. LIVE DATA SOURCES
# ============================================================================

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


def get_all_tools() -> List[Dict]:
    """Merge all sources and deduplicate by name. Falls back to built-in list if all fetches fail."""
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


# Built-in fallback — always shown when live sources are unavailable
TOOLS_FALLBACK: List[Dict] = [
    {"name": "ChatGPT",            "category": "Chatbot",           "pricing": "freemium", "description": "OpenAI's conversational AI for writing, coding, Q&A and brainstorming. The most widely used AI assistant in the world.",                              "url": "https://chat.openai.com",                     "tags": ["text", "coding", "writing"],           "image": FALLBACK_IMAGE},
    {"name": "Claude",             "category": "Chatbot",           "pricing": "freemium", "description": "Anthropic's AI assistant known for thoughtful, nuanced responses. Excellent for long documents, analysis and coding tasks.",                          "url": "https://claude.ai",                           "tags": ["text", "analysis", "coding"],          "image": FALLBACK_IMAGE},
    {"name": "Gemini",             "category": "Chatbot",           "pricing": "freemium", "description": "Google's multimodal AI that integrates with Google Workspace. Understands text, images, audio and video natively.",                                   "url": "https://gemini.google.com",                   "tags": ["text", "multimodal", "google"],         "image": FALLBACK_IMAGE},
    {"name": "Perplexity AI",      "category": "Search",            "pricing": "freemium", "description": "AI-powered search engine that answers questions with cited sources in real time. A smarter alternative to traditional search.",                        "url": "https://perplexity.ai",                       "tags": ["search", "research", "citations"],      "image": FALLBACK_IMAGE},
    {"name": "Midjourney",         "category": "Image Generation",  "pricing": "paid",     "description": "Generate stunning photorealistic and artistic images from text prompts. The gold standard for AI art and design work.",                               "url": "https://midjourney.com",                      "tags": ["image", "design", "art"],              "image": FALLBACK_IMAGE},
    {"name": "DALL·E 3",           "category": "Image Generation",  "pricing": "freemium", "description": "OpenAI's image generator built into ChatGPT. Creates accurate, detailed images from natural language descriptions.",                                  "url": "https://openai.com/dall-e-3",                 "tags": ["image", "openai", "art"],              "image": FALLBACK_IMAGE},
    {"name": "Stable Diffusion",   "category": "Image Generation",  "pricing": "free",     "description": "Open-source image generation model you can run locally or via web UIs. Highly customisable with thousands of community models.",                     "url": "https://stability.ai",                        "tags": ["image", "open-source", "local"],       "image": FALLBACK_IMAGE},
    {"name": "GitHub Copilot",     "category": "Coding",            "pricing": "paid",     "description": "AI pair programmer that autocompletes code, explains functions and generates entire files directly inside your code editor.",                          "url": "https://github.com/features/copilot",         "tags": ["coding", "github", "autocomplete"],    "image": FALLBACK_IMAGE},
    {"name": "Cursor",             "category": "Coding",            "pricing": "freemium", "description": "AI-first code editor built on VS Code. Chat with your codebase, generate features and fix bugs with natural language.",                               "url": "https://cursor.sh",                           "tags": ["coding", "editor", "vscode"],          "image": FALLBACK_IMAGE},
    {"name": "Claude Code",        "category": "Coding",            "pricing": "freemium", "description": "Anthropic's agentic coding tool that runs in your terminal. Understands entire codebases and executes multi-step engineering tasks.",                 "url": "https://claude.ai/code",                      "tags": ["coding", "terminal", "agentic"],       "image": FALLBACK_IMAGE},
    {"name": "Replit AI",          "category": "Coding",            "pricing": "freemium", "description": "AI coding assistant inside Replit's browser IDE. Write, run and deploy code entirely in the cloud with AI assistance.",                              "url": "https://replit.com/ai",                       "tags": ["coding", "browser", "deployment"],     "image": FALLBACK_IMAGE},
    {"name": "v0 by Vercel",       "category": "Coding",            "pricing": "freemium", "description": "Generate React UI components from a text prompt. Paste the code directly into your project — zero setup required.",                                  "url": "https://v0.dev",                              "tags": ["coding", "ui", "react"],               "image": FALLBACK_IMAGE},
    {"name": "Jasper",             "category": "Writing",           "pricing": "paid",     "description": "AI writing platform for marketing teams. Creates blog posts, ad copy, emails and social content at scale with brand voice controls.",                 "url": "https://jasper.ai",                           "tags": ["writing", "marketing", "copywriting"], "image": FALLBACK_IMAGE},
    {"name": "Grammarly",          "category": "Writing",           "pricing": "freemium", "description": "AI writing assistant that checks grammar, tone, clarity and style. Works across browsers, Google Docs and email clients.",                            "url": "https://grammarly.com",                       "tags": ["writing", "grammar", "editing"],       "image": FALLBACK_IMAGE},
    {"name": "Copy.ai",            "category": "Writing",           "pricing": "freemium", "description": "Generate marketing copy, product descriptions, email sequences and blog content in seconds with AI-powered templates.",                               "url": "https://copy.ai",                             "tags": ["writing", "marketing", "copywriting"], "image": FALLBACK_IMAGE},
    {"name": "Runway",             "category": "Video",             "pricing": "freemium", "description": "AI video generation and editing suite. Generate videos from text, remove backgrounds and apply cinematic effects with ease.",                          "url": "https://runwayml.com",                        "tags": ["video", "editing", "generation"],      "image": FALLBACK_IMAGE},
    {"name": "Sora",               "category": "Video",             "pricing": "freemium", "description": "OpenAI's text-to-video model that generates realistic scenes from prompts up to a minute long. Cinematic quality output.",                           "url": "https://sora.com",                            "tags": ["video", "openai", "generation"],       "image": FALLBACK_IMAGE},
    {"name": "Pika",               "category": "Video",             "pricing": "freemium", "description": "Generate and edit videos with AI. Animate images, modify existing clips and create cinematic scenes from a text description.",                        "url": "https://pika.art",                            "tags": ["video", "animation", "generation"],    "image": FALLBACK_IMAGE},
    {"name": "ElevenLabs",         "category": "Audio",             "pricing": "freemium", "description": "AI voice synthesis and cloning. Generate natural-sounding speech in any voice or language for podcasts, videos and apps.",                            "url": "https://elevenlabs.io",                       "tags": ["audio", "voice", "tts"],               "image": FALLBACK_IMAGE},
    {"name": "Suno",               "category": "Audio",             "pricing": "freemium", "description": "Generate full songs with vocals and instruments from a text prompt. Create original music in any genre in seconds.",                                  "url": "https://suno.ai",                             "tags": ["audio", "music", "generation"],        "image": FALLBACK_IMAGE},
    {"name": "Notion AI",          "category": "Productivity",      "pricing": "paid",     "description": "AI built into Notion that summarises pages, drafts content, translates text and answers questions about your workspace.",                             "url": "https://notion.so/product/ai",                "tags": ["productivity", "notes", "workspace"],  "image": FALLBACK_IMAGE},
    {"name": "Otter.ai",           "category": "Productivity",      "pricing": "freemium", "description": "AI meeting assistant that transcribes, summarises and captures action items from meetings in real time across Zoom, Meet and Teams.",                 "url": "https://otter.ai",                            "tags": ["productivity", "transcription", "meetings"], "image": FALLBACK_IMAGE},
    {"name": "Gamma",              "category": "Productivity",      "pricing": "freemium", "description": "Create beautiful presentations, documents and websites with AI. Just describe what you want and Gamma generates a polished deck instantly.",           "url": "https://gamma.app",                           "tags": ["productivity", "presentations", "design"], "image": FALLBACK_IMAGE},
    {"name": "Whisper",            "category": "Audio",             "pricing": "free",     "description": "OpenAI's open-source speech recognition model. Transcribes audio in 99 languages with impressive accuracy. Free to run locally.",                    "url": "https://openai.com/research/whisper",          "tags": ["audio", "transcription", "open-source"], "image": FALLBACK_IMAGE},
    {"name": "Hugging Face",       "category": "Open-Source LLM",  "pricing": "free",     "description": "The hub for open-source AI models, datasets and demos. Home to thousands of community models for every AI task imaginable.",                         "url": "https://huggingface.co",                      "tags": ["open-source", "models", "hub"],        "image": FALLBACK_IMAGE},
    {"name": "Ollama",             "category": "Open-Source LLM",  "pricing": "free",     "description": "Run large language models locally on your own machine with one command. Supports Llama, Mistral, Gemma, Phi and dozens more.",                      "url": "https://ollama.ai",                           "tags": ["open-source", "local", "llm"],         "image": FALLBACK_IMAGE},
    {"name": "LM Studio",          "category": "Open-Source LLM",  "pricing": "free",     "description": "Desktop app for discovering, downloading and running local LLMs. Clean UI, no command line needed, runs fully offline.",                             "url": "https://lmstudio.ai",                         "tags": ["open-source", "local", "desktop"],     "image": FALLBACK_IMAGE},
    {"name": "Mistral AI",         "category": "Open-Source LLM",  "pricing": "freemium", "description": "French AI lab behind the Mistral and Mixtral open-weight models. Offers both open-source models and a fast API.",                                    "url": "https://mistral.ai",                          "tags": ["open-source", "llm", "api"],           "image": FALLBACK_IMAGE},
    {"name": "Meta Llama",         "category": "Open-Source LLM",  "pricing": "free",     "description": "Meta's family of open-weight large language models. Llama 3 rivals closed models on many benchmarks and is free to download and run.",               "url": "https://llama.meta.com",                      "tags": ["open-source", "meta", "llm"],          "image": FALLBACK_IMAGE},
    {"name": "Canva AI",           "category": "Design",            "pricing": "freemium", "description": "AI-powered design tools inside Canva — generate images, remove backgrounds, write copy and auto-resize designs for any format.",                     "url": "https://canva.com/ai-image-generator",        "tags": ["design", "image", "canva"],            "image": FALLBACK_IMAGE},
    {"name": "Adobe Firefly",      "category": "Design",            "pricing": "freemium", "description": "Adobe's family of creative AI tools for generating images, vectors and text effects. Trained on licensed content for commercial safety.",             "url": "https://firefly.adobe.com",                   "tags": ["design", "image", "adobe"],            "image": FALLBACK_IMAGE},
    {"name": "Ideogram",           "category": "Image Generation",  "pricing": "freemium", "description": "AI image generator that excels at generating text inside images accurately — great for logos, posters and social media graphics.",                   "url": "https://ideogram.ai",                         "tags": ["image", "text", "design"],             "image": FALLBACK_IMAGE},
]


# ============================================================================
# 3. AGENTS DATA
# ============================================================================

AGENTS_FALLBACK: List[Dict] = [
    {"name": "AutoGPT",                 "type": "General agent",         "status": "Open-source", "description": "One of the first autonomous AI agents. Chains GPT-4 calls to complete long-horizon tasks without human input.",                                             "url": "https://github.com/Significant-Gravitas/AutoGPT",  "tags": ["autonomous", "gpt-4", "open-source"]},
    {"name": "Claude Computer Use",     "type": "Computer agent",        "status": "Beta",        "description": "Anthropic's agent that controls a computer — clicks buttons, types text and navigates browsers to complete tasks.",                                         "url": "https://docs.anthropic.com/computer-use",          "tags": ["anthropic", "desktop", "browser"]},
    {"name": "OpenAI Operator",         "type": "Web agent",             "status": "Available",   "description": "OpenAI's agent that navigates websites and completes multi-step tasks like booking, shopping and form filling.",                                             "url": "https://openai.com/operator",                      "tags": ["openai", "web", "automation"]},
    {"name": "LangChain Agents",        "type": "Framework",             "status": "Open-source", "description": "The most popular framework for building LLM agents with tool use, memory and multi-step reasoning chains.",                                                 "url": "https://www.langchain.com",                        "tags": ["framework", "python", "tool-use"]},
    {"name": "CrewAI",                  "type": "Multi-agent",           "status": "Open-source", "description": "Orchestrate multiple AI agents with distinct roles to collaborate on complex tasks like a real crew.",                                                      "url": "https://crewai.com",                               "tags": ["multi-agent", "python", "collaboration"]},
    {"name": "Microsoft Copilot Studio","type": "No-code agent builder", "status": "Available",   "description": "Build, configure and deploy AI agents without code inside Microsoft 365 and Power Platform ecosystems.",                                                    "url": "https://copilotstudio.microsoft.com",              "tags": ["microsoft", "no-code", "enterprise"]},
    {"name": "AgentGPT",                "type": "Browser agent",         "status": "Free",        "description": "Run autonomous AI agents in your browser. Define a goal and watch the agent break it into tasks and execute them.",                                         "url": "https://agentgpt.reworkd.ai",                      "tags": ["browser", "autonomous", "no-install"]},
    {"name": "Devin",                   "type": "Coding agent",          "status": "Available",   "description": "The first AI software engineer. Devin plans, codes, debugs and deploys software autonomously end-to-end.",                                                 "url": "https://devin.ai",                                 "tags": ["coding", "autonomous", "software-engineer"]},
    {"name": "BabyAGI",                 "type": "Task agent",            "status": "Open-source", "description": "A Python script that uses GPT-4 and vector DBs to autonomously create and execute a task list to achieve a goal.",                                         "url": "https://github.com/yoheinakajima/babyagi",         "tags": ["autonomous", "python", "open-source"]},
    {"name": "AutoGen",                 "type": "Multi-agent framework", "status": "Open-source", "description": "Microsoft Research framework where multiple agents converse to collaboratively solve tasks.",                                                               "url": "https://microsoft.github.io/autogen",              "tags": ["microsoft", "multi-agent", "framework"]},
    {"name": "Google Gemini Agents",    "type": "General agent",         "status": "Available",   "description": "Google Gemini-powered agents with access to Search, Maps, Gmail and Workspace tools.",                                                                     "url": "https://deepmind.google/technologies/gemini",      "tags": ["google", "multimodal", "search"]},
    {"name": "Phidata",                 "type": "Agent framework",       "status": "Open-source", "description": "Build AI agents with memory, knowledge and tools using a clean Python API. Supports any LLM provider.",                                                    "url": "https://phidata.com",                              "tags": ["python", "framework", "memory"]},
    {"name": "Claude Code",             "type": "Coding agent",          "status": "Available",   "description": "Anthropic agentic coding tool in your terminal. Understands entire codebases and executes multi-step engineering tasks.",                                   "url": "https://claude.ai/code",                           "tags": ["anthropic", "coding", "terminal"]},
    {"name": "Cursor Agent",            "type": "Coding agent",          "status": "Available",   "description": "Cursor built-in agent mode that autonomously writes, runs and debugs code across your entire project.",                                                    "url": "https://cursor.sh",                                "tags": ["coding", "vscode", "autonomous"]},
    {"name": "n8n AI Agents",           "type": "Workflow agent",        "status": "Open-source", "description": "Build visual AI agent workflows with open-source automation. Connect any tool, API or model with no code.",                                                "url": "https://n8n.io",                                   "tags": ["workflow", "automation", "no-code"]},
    {"name": "Zapier AI Agents",        "type": "Workflow agent",        "status": "Available",   "description": "Zapier AI agents connect your apps and automate complex multi-step workflows using natural language instructions.",                                         "url": "https://zapier.com/ai",                            "tags": ["workflow", "automation", "no-code"]},
]


def fetch_agents() -> List[Dict]:
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


# ============================================================================
# 4. SHARED HTML
# ============================================================================

STYLE = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --primary:    #7c6af7;
    --primary-lt: #ede9ff;
    --primary-dk: #5b4de0;
    --accent:     #34d399;
    --accent-lt:  #d1fae5;
    --dark:       #1e1b3a;
    --mid:        #4b4869;
    --muted:      #8b87a8;
    --bg:         #f5f4fb;
    --surface:    #ffffff;
    --border:     #e5e2f5;
    --radius-sm:  10px;
    --radius-md:  16px;
    --radius-lg:  22px;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', -apple-system, sans-serif;
    background: var(--bg);
    color: var(--dark);
    line-height: 1.6;
  }
  h1, h2, h3, .nav-brand {
    font-family: 'Plus Jakarta Sans', sans-serif;
  }
  .container { max-width: 1120px; margin: auto; padding: 24px 20px; }

  /* ---- NAV ---- */
  nav {
    background: var(--dark);
    padding: 14px 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 2px solid var(--primary);
  }
  .nav-container { max-width: 1120px; margin: auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; }
  .nav-brand { display: flex; align-items: center; gap: 10px; color: white; font-weight: 700; font-size: 1.05rem; text-decoration: none; letter-spacing: .3px; }
  .nav-links { list-style: none; display: flex; gap: 8px; }
  .nav-links a {
    color: rgba(255,255,255,0.75);
    text-decoration: none;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 0.83rem;
    text-transform: uppercase;
    letter-spacing: .6px;
    padding: 6px 14px;
    border-radius: 20px;
    transition: all .2s;
  }
  .nav-links a:hover { color: white; background: rgba(255,255,255,0.1); }
  .nav-links a.active { color: white; background: var(--primary); }

  /* ---- HEADER ---- */
  header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 22px;
    padding: 44px 0 28px;
    margin-bottom: 32px;
    border-bottom: 1px solid var(--border);
  }
  .logo { width: 76px; height: 76px; border-radius: 50%; object-fit: cover; border: 3px solid var(--primary-lt); }
  header h1 {
    font-size: 2.1rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  .tagline { font-size: 0.95rem; color: var(--muted); margin-top: 5px; }

  /* ---- FILTERS ---- */
  .filters { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; align-items: center; }
  .filters input[type=text] {
    padding: 10px 18px;
    border-radius: 28px;
    border: 1.5px solid var(--border);
    background: var(--surface);
    font-size: 0.92rem;
    font-family: 'DM Sans', sans-serif;
    width: 240px;
    outline: none;
    color: var(--dark);
    transition: border .2s, box-shadow .2s;
  }
  .filters input[type=text]::placeholder { color: var(--muted); }
  .filters input[type=text]:focus { border-color: var(--primary); box-shadow: 0 0 0 3px var(--primary-lt); }
  .filter-group { display: flex; flex-wrap: wrap; gap: 6px; }
  .filter-btn {
    padding: 6px 14px;
    border-radius: 20px;
    border: 1.5px solid var(--border);
    background: var(--surface);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.76rem;
    font-weight: 600;
    cursor: pointer;
    transition: all .2s;
    color: var(--mid);
  }
  .filter-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-lt); }
  .filter-btn.active { background: var(--primary); color: white; border-color: var(--primary); }

  .stats-bar { font-size: 0.84rem; color: var(--muted); margin-bottom: 18px; }
  .stats-bar b { color: var(--dark); }

  /* ---- TOOL CARDS ---- */
  .tools-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(295px, 1fr)); gap: 24px; }
  .tool-card {
    background: var(--surface);
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 1.5px solid var(--border);
    display: flex;
    flex-direction: column;
    transition: transform .22s, box-shadow .22s, border-color .22s;
    cursor: pointer;
  }
  .tool-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(124,106,247,0.13);
    border-color: var(--primary);
  }
  .tool-card-img { width: 100%; height: 150px; object-fit: cover; display: block; }
  .tool-card-body { padding: 16px 18px 18px; flex: 1; display: flex; flex-direction: column; gap: 9px; }
  .tool-meta { display: flex; gap: 6px; flex-wrap: wrap; }

  .badge {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.67rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: .5px;
    white-space: nowrap;
  }
  .badge-category { background: var(--primary-lt); color: var(--primary-dk); }
  .badge-free     { background: #d1fae5; color: #065f46; }
  .badge-freemium { background: #fef3c7; color: #92400e; }
  .badge-paid     { background: #fce7f3; color: #9d174d; }

  .tool-card h3 { font-size: 1.05rem; font-weight: 600; line-height: 1.35; color: var(--dark); }
  .tool-card-desc { color: var(--mid); line-height: 1.58; font-size: 0.88rem; flex-grow: 1; }
  .tool-tags { display: flex; flex-wrap: wrap; gap: 5px; }
  .tag {
    font-size: 0.67rem;
    background: var(--bg);
    color: var(--muted);
    padding: 2px 9px;
    border-radius: 10px;
    border: 1px solid var(--border);
  }
  .btn {
    display: inline-block;
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 600;
    font-size: 0.84rem;
    color: var(--primary);
    text-decoration: none;
    border: 2px solid var(--primary);
    padding: 7px 16px;
    border-radius: 22px;
    transition: all .2s;
    text-align: center;
  }
  .btn:hover { background: var(--primary); color: white; }

  /* ---- AGENT CARDS ---- */
  .agents-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 24px; }
  .agent-card {
    background: var(--surface);
    border-radius: var(--radius-md);
    padding: 22px;
    border: 1.5px solid var(--border);
    border-left: 4px solid var(--primary);
    display: flex;
    flex-direction: column;
    gap: 11px;
    transition: transform .22s, box-shadow .22s;
  }
  .agent-card:hover { transform: translateY(-3px); box-shadow: 0 10px 28px rgba(124,106,247,0.12); }
  .agent-card h3 { font-size: 1.1rem; font-weight: 600; color: var(--dark); }
  .agent-card-desc { color: var(--mid); font-size: 0.9rem; line-height: 1.58; flex-grow: 1; }
  .agent-type   { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.68rem; font-weight: 700; color: var(--primary-dk); background: var(--primary-lt); padding: 3px 11px; border-radius: 12px; }
  .agent-status { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.68rem; font-weight: 700; color: #065f46; background: #d1fae5; padding: 3px 11px; border-radius: 12px; }

  /* ---- MODAL ---- */
  .modal-overlay { display: none; position: fixed; inset: 0; background: rgba(30,27,58,0.6); z-index: 2000; align-items: center; justify-content: center; padding: 20px; backdrop-filter: blur(2px); }
  .modal-overlay.open { display: flex; }
  .modal { background: var(--surface); border-radius: var(--radius-lg); max-width: 540px; width: 100%; overflow: hidden; border: 1.5px solid var(--border); }
  .modal-img { width: 100%; height: 200px; object-fit: cover; display: block; }
  .modal-body { padding: 24px; }
  .modal-title { font-size: 1.45rem; font-weight: 700; margin: 10px 0 9px; color: var(--dark); }
  .modal-desc { color: var(--mid); line-height: 1.65; margin-bottom: 18px; font-size: 0.95rem; }
  .modal-actions { display: flex; gap: 10px; align-items: center; }
  .modal-close { margin-left: auto; background: var(--bg); border: 1.5px solid var(--border); border-radius: 50%; width: 34px; height: 34px; font-size: 1rem; cursor: pointer; color: var(--muted); transition: .2s; display: flex; align-items: center; justify-content: center; }
  .modal-close:hover { background: var(--primary-lt); color: var(--primary); border-color: var(--primary); }

  /* ---- MISC ---- */
  .no-results { text-align: center; padding: 64px 20px; color: var(--muted); grid-column: 1 / -1; }
  .no-results h3 { font-size: 1.2rem; margin-bottom: 6px; color: var(--mid); }

  .ad-space {
    text-align: center;
    padding: 16px;
    background: var(--primary-lt);
    border: 1px dashed var(--primary);
    border-radius: var(--radius-sm);
    margin: 20px 0;
    font-size: 0.82rem;
    color: var(--primary-dk);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-weight: 500;
  }
  footer {
    text-align: center;
    padding: 30px 20px;
    font-size: 0.82rem;
    border-top: 1px solid var(--border);
    color: var(--muted);
    margin-top: 48px;
  }
  footer a { color: var(--primary); text-decoration: none; }
  footer a:hover { text-decoration: underline; }

  /* ---- HAMBURGER BUTTON ---- */
  .nav-toggle {
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
  }
  .nav-toggle span {
    display: block;
    width: 24px;
    height: 2px;
    background: white;
    border-radius: 2px;
    transition: all .3s;
  }
  .nav-toggle.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
  .nav-toggle.open span:nth-child(2) { opacity: 0; }
  .nav-toggle.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

  /* ---- RESPONSIVE ---- */
  @media (max-width: 768px) {
    header { flex-direction: column; gap: 14px; text-align: center; }
    .filters input[type=text] { width: 100%; }
    .tools-grid, .agents-grid { grid-template-columns: 1fr; }

    .nav-toggle { display: flex; }

    .nav-links {
      display: none;
      flex-direction: column;
      gap: 4px;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: var(--dark);
      padding: 12px 16px 16px;
      border-top: 1px solid rgba(255,255,255,0.1);
      z-index: 999;
    }
    .nav-links.open { display: flex; }
    .nav-links a {
      font-size: 0.95rem;
      padding: 10px 14px;
      border-radius: 10px;
      letter-spacing: 0;
      text-transform: none;
    }
    nav { position: sticky; top: 0; }
    .nav-container { position: relative; }
  }

  @media (max-width: 480px) {
    .container { padding: 16px 14px; }
    header h1 { font-size: 1.6rem; }
    .tagline { font-size: 0.85rem; }
    .filter-btn { font-size: 0.72rem; padding: 5px 10px; }
    .filters input[type=text] { font-size: 0.88rem; }
    .tool-card h3 { font-size: 0.98rem; }
    .tool-card-desc { font-size: 0.84rem; }
    .modal-body { padding: 16px; }
    .modal-title { font-size: 1.2rem; }
  }
</style>
"""

ADSENSE_CODE = f"""<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>"""


def nav_html(active: str = "") -> str:
    pages = [("tools","index.html","AI Tools"), ("agents","agents.html","AI Agents"), ("courses","courses.html","AI Courses"), ("devtools","devtools.html","Dev Tools"), ("about","about.html","About")]
    items = "".join(f'<li><a href="{h}" class="{"active" if k==active else ""}">{l}</a></li>' for k,h,l in pages)
    return f"""<nav>
  <div class="nav-container">
    <a class="nav-brand" href="index.html">
      <img src="{LOGO_URL}" style="width:28px;height:28px;border-radius:50%;flex-shrink:0;" alt="logo">
      HAPPY TOOLS
    </a>
    <button class="nav-toggle" id="nav-toggle" aria-label="Toggle menu">
      <span></span><span></span><span></span>
    </button>
    <ul class="nav-links" id="nav-links">{items}</ul>
  </div>
</nav>
<script>
(function(){{
  var btn   = document.getElementById('nav-toggle');
  var links = document.getElementById('nav-links');
  if (!btn) return;
  btn.addEventListener('click', function(){{
    btn.classList.toggle('open');
    links.classList.toggle('open');
  }});
  links.querySelectorAll('a').forEach(function(a){{
    a.addEventListener('click', function(){{
      btn.classList.remove('open');
      links.classList.remove('open');
    }});
  }});
}})();
</script>"""


def footer_html() -> str:
    ts = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    return f"""<footer><p>&copy; 2026 Happy Tools &nbsp;|&nbsp; <a href="about.html">About</a> &nbsp;|&nbsp; <a href="privacy.html">Privacy</a></p><p>Updated: {ts}</p></footer>"""


# ============================================================================
# 5. PAGE GENERATORS
# ============================================================================

def _safe_json(data) -> str:
    """
    Serialise to JSON and escape </script> so it's safe inside a <script> tag.
    This prevents any tool description containing '</script>' from breaking the page.
    """
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def generate_index_html(tools: List[Dict]) -> str:
    from seo import get_seo_meta, get_structured_data_website, AI_TOOLS_KEYWORDS
    
    categories  = sorted(set(t.get("category", "Other") for t in tools))
    tools_json  = _safe_json(tools)
    total       = len(tools)

    cat_btns = '<button class="filter-btn active" onclick="setCategory(this,\'all\')">All</button>'
    for c in categories:
        safe = c.replace("'", "\\'")
        cat_btns += f'<button class="filter-btn" onclick="setCategory(this,\'{safe}\')">{c}</button>'

    seo_meta = get_seo_meta(
        page_type="website",
        title="Happy Tools — Best AI Tools Directory 2026 | ChatGPT, Claude, Midjourney & More",
        description="Discover 50+ best AI tools for 2026. Curated directory of ChatGPT, Claude, Midjourney, DALL-E, GitHub Copilot, and more. Live-updated daily with free and paid AI software.",
        keywords=AI_TOOLS_KEYWORDS,
        canonical=SITE_URL
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {seo_meta}
  <title>Happy Tools — Best AI Tools Directory 2026</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {ADSENSE_CODE}
  {get_structured_data_website()}
  {STYLE}
</head>
<body>
{nav_html("tools")}
<div class="container">
  <header>
    <img src="{LOGO_URL}" class="logo" alt="Happy Tools">
    <div>
      <h1>Happy Tools</h1>
      <p class="tagline">Discover the best AI tools — curated &amp; live-updated</p>
    </div>
  </header>

  <div class="ad-space">ADVERTISEMENT</div>

  <div class="filters">
    <input type="text" id="q" placeholder="Search tools..." oninput="applyFilters()">
    <div class="filter-group" id="cat-btns">{cat_btns}</div>
    <div class="filter-group" id="price-btns">
      <button class="filter-btn active" onclick="setPrice(this,'all')">All pricing</button>
      <button class="filter-btn" onclick="setPrice(this,'free')">Free</button>
      <button class="filter-btn" onclick="setPrice(this,'freemium')">Freemium</button>
      <button class="filter-btn" onclick="setPrice(this,'paid')">Paid</button>
    </div>
  </div>

  <p class="stats-bar">Showing <b id="count">{total}</b> of {total} tools</p>
  <div class="tools-grid" id="grid"></div>

  <div class="modal-overlay" id="modal">
    <div class="modal">
      <img class="modal-img" id="m-img" src="" alt="">
      <div class="modal-body">
        <div id="m-meta" style="display:flex;gap:6px;flex-wrap:wrap;"></div>
        <h2 class="modal-title" id="m-name"></h2>
        <p class="modal-desc" id="m-desc"></p>
        <div class="modal-actions">
          <a id="m-link" href="#" target="_blank" rel="noopener" class="btn">Visit Tool &#8594;</a>
          <button class="modal-close" id="m-close">&#x2715;</button>
        </div>
      </div>
    </div>
  </div>

  {footer_html()}
</div>

<!-- Data embedded safely — no inline string concatenation issues -->
<script id="tools-data" type="application/json">{tools_json}</script>
<script>
(function () {{
  var TOOLS = JSON.parse(document.getElementById('tools-data').textContent);
  var FB    = '{FALLBACK_IMAGE}';
  window._FB = FB;
  var activeCat   = 'all';
  var activePrice = 'all';

  function badge(p) {{
    return '<span class="badge badge-' + p + '">' + p + '</span>';
  }}

  function escAttr(s) {{
    return String(s).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;');
  }}

  function renderCards(list) {{
    document.getElementById('count').textContent = list.length;
    var grid = document.getElementById('grid');
    if (!list.length) {{
      grid.innerHTML = '<div class="no-results"><h3>No tools found</h3><p>Try a different search or filter.</p></div>';
      return;
    }}
    var html = '';
    for (var i = 0; i < list.length; i++) {{
      var t    = list[i];
      var idx  = TOOLS.indexOf(t);
      var img  = escAttr(t.image || FB);
      var tags = (t.tags || []).map(function(x) {{ return '<span class="tag">' + x + '</span>'; }}).join('');
      html +=
        '<div class="tool-card" onclick="openModal(' + idx + ')">' +
          '<img class="tool-card-img" src="' + img + '" alt="' + escAttr(t.name) + '" loading="lazy" onerror="this.src=window._FB">' +
          '<div class="tool-card-body">' +
            '<div class="tool-meta"><span class="badge badge-category">' + t.category + '</span>' + badge(t.pricing) + '</div>' +
            '<h3>' + t.name + '</h3>' +
            '<p class="tool-card-desc">' + t.description + '</p>' +
            '<div class="tool-tags">' + tags + '</div>' +
            '<a href="' + escAttr(t.url) + '" target="_blank" rel="noopener" class="btn" onclick="event.stopPropagation()">Visit Tool &#8594;</a>' +
          '</div>' +
        '</div>';
    }}
    grid.innerHTML = html;
  }}

  function applyFilters() {{
    var q = document.getElementById('q').value.toLowerCase();
    var filtered = TOOLS.filter(function(t) {{
      var matchQ = !q
        || t.name.toLowerCase().indexOf(q) !== -1
        || t.description.toLowerCase().indexOf(q) !== -1
        || (t.tags || []).some(function(x) {{ return x.indexOf(q) !== -1; }});
      var matchCat   = activeCat   === 'all' || t.category === activeCat;
      var matchPrice = activePrice === 'all' || t.pricing  === activePrice;
      return matchQ && matchCat && matchPrice;
    }});
    renderCards(filtered);
  }}

  window.setCategory = function(btn, v) {{
    activeCat = v;
    document.querySelectorAll('#cat-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active');
    applyFilters();
  }};

  window.setPrice = function(btn, v) {{
    activePrice = v;
    document.querySelectorAll('#price-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active');
    applyFilters();
  }};

  window.openModal = function(i) {{
    var t = TOOLS[i];
    if (!t) return;
    document.getElementById('m-img').src          = t.image || FB;
    document.getElementById('m-name').textContent = t.name;
    document.getElementById('m-desc').textContent = t.description;
    document.getElementById('m-link').href         = t.url;
    document.getElementById('m-meta').innerHTML   =
      '<span class="badge badge-category">' + t.category + '</span> ' + badge(t.pricing);
    document.getElementById('modal').classList.add('open');
  }};

  function closeModal() {{
    document.getElementById('modal').classList.remove('open');
  }}

  document.getElementById('m-close').addEventListener('click', closeModal);
  document.getElementById('modal').addEventListener('click', function(e) {{
    if (e.target === this) closeModal();
  }});
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeModal();
  }});

  // Kick off initial render
  window.applyFilters = applyFilters;
  renderCards(TOOLS);
}})();
</script>
</body>
</html>"""


def generate_agents_html(agents: List[Dict]) -> str:
    agent_types = sorted(set(a.get("type", "AI Agent") for a in agents))
    agents_json = _safe_json(agents)
    total       = len(agents)

    type_btns = '<button class="filter-btn active" onclick="setType(this,\'all\')">All</button>'
    for t in agent_types:
        safe = t.replace("'", "\\'")
        type_btns += f'<button class="filter-btn" onclick="setType(this,\'{safe}\')">{t}</button>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Discover the best AI agents — autonomous systems that plan, act and execute tasks.">
  <title>AI Agents — Happy Tools</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {ADSENSE_CODE}
  {STYLE}
</head>
<body>
{nav_html("agents")}
<div class="container">
  <header>
    <img src="{LOGO_URL}" class="logo" alt="Happy Tools">
    <div>
      <h1>AI Agents</h1>
      <p class="tagline">Autonomous AI systems that plan, act and get things done</p>
    </div>
  </header>

  <div class="ad-space">ADVERTISEMENT</div>

  <div class="filters">
    <input type="text" id="q" placeholder="Search agents..." oninput="applyFilters()">
    <div class="filter-group" id="type-btns">{type_btns}</div>
  </div>

  <p class="stats-bar">Showing <b id="count">{total}</b> of {total} agents</p>
  <div class="agents-grid" id="grid"></div>

  {footer_html()}
</div>

<script id="agents-data" type="application/json">{agents_json}</script>
<script>
(function () {{
  var AGENTS    = JSON.parse(document.getElementById('agents-data').textContent);
  var activeType = 'all';

  function renderAgents(list) {{
    document.getElementById('count').textContent = list.length;
    var grid = document.getElementById('grid');
    if (!list.length) {{
      grid.innerHTML = '<div class="no-results"><h3>No agents found</h3><p>Try a different search.</p></div>';
      return;
    }}
    var html = '';
    for (var i = 0; i < list.length; i++) {{
      var a    = list[i];
      var tags = (a.tags || []).map(function(x) {{ return '<span class="tag">' + x + '</span>'; }}).join('');
      html +=
        '<div class="agent-card">' +
          '<div style="display:flex;gap:8px;flex-wrap:wrap;">' +
            '<span class="agent-type">'   + (a.type   || 'AI Agent')  + '</span>' +
            '<span class="agent-status">' + (a.status || 'Available') + '</span>' +
          '</div>' +
          '<h3>' + a.name + '</h3>' +
          '<p class="agent-card-desc">' + a.description + '</p>' +
          '<div class="tool-tags">' + tags + '</div>' +
          '<a href="' + a.url + '" target="_blank" rel="noopener" class="btn" style="align-self:flex-start;">Learn More &#8594;</a>' +
        '</div>';
    }}
    grid.innerHTML = html;
  }}

  function applyFilters() {{
    var q = document.getElementById('q').value.toLowerCase();
    var filtered = AGENTS.filter(function(a) {{
      var matchQ = !q
        || a.name.toLowerCase().indexOf(q) !== -1
        || a.description.toLowerCase().indexOf(q) !== -1;
      return matchQ && (activeType === 'all' || a.type === activeType);
    }});
    renderAgents(filtered);
  }}

  window.setType = function(btn, v) {{
    activeType = v;
    document.querySelectorAll('#type-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active');
    applyFilters();
  }};

  window.applyFilters = applyFilters;
  renderAgents(AGENTS);
}})();
</script>
</body>
</html>"""


# ============================================================================
# COURSES DATA
# ============================================================================

COURSES: List[Dict] = [
    # ---- Free / Freemium ----
    {
        "title":    "Generative AI for Everyone",
        "provider": "DeepLearning.AI",
        "platform": "Coursera",
        "level":    "Beginner",
        "pricing":  "free",
        "duration": "6 hrs",
        "tags":     ["genai", "beginner", "no-code"],
        "description": "Andrew Ng's non-technical intro to generative AI — how it works, where it can be applied, and how to use it in your own projects.",
        "url":      "https://www.coursera.org/learn/generative-ai-for-everyone",
        "cert":     True,
    },
    {
        "title":    "Introduction to Large Language Models",
        "provider": "Google Cloud",
        "platform": "Google Cloud Skills Boost",
        "level":    "Beginner",
        "pricing":  "free",
        "duration": "1 hr",
        "tags":     ["llm", "google", "beginner"],
        "description": "Quick but solid overview of LLMs — what they are, use cases, and how prompt tuning works. Part of Google's Generative AI learning path.",
        "url":      "https://cloudskillsboost.google/course_templates/539",
        "cert":     True,
    },
    {
        "title":    "ChatGPT Prompt Engineering for Developers",
        "provider": "DeepLearning.AI + OpenAI",
        "platform": "DeepLearning.AI",
        "level":    "Beginner",
        "pricing":  "free",
        "duration": "1 hr",
        "tags":     ["prompt-engineering", "openai", "python"],
        "description": "Hands-on short course by Isa Fulford and Andrew Ng. Learn prompt engineering best practices for building LLM-powered applications.",
        "url":      "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/",
        "cert":     False,
    },
    {
        "title":    "LangChain for LLM Application Development",
        "provider": "DeepLearning.AI",
        "platform": "DeepLearning.AI",
        "level":    "Intermediate",
        "pricing":  "free",
        "duration": "1 hr",
        "tags":     ["langchain", "python", "llm"],
        "description": "Build LLM-powered apps using LangChain — covers chains, agents, memory and tools with Python code walkthroughs.",
        "url":      "https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/",
        "cert":     False,
    },
    {
        "title":    "Hugging Face NLP Course",
        "provider": "Hugging Face",
        "platform": "Hugging Face",
        "level":    "Intermediate",
        "pricing":  "free",
        "duration": "Self-paced",
        "tags":     ["nlp", "transformers", "python", "huggingface"],
        "description": "The definitive free course on Transformers and the Hugging Face ecosystem — fine-tuning, tokenizers, datasets and deployment.",
        "url":      "https://huggingface.co/learn/nlp-course",
        "cert":     False,
    },
    {
        "title":    "Elements of AI",
        "provider": "University of Helsinki",
        "platform": "elementsofai.com",
        "level":    "Beginner",
        "pricing":  "free",
        "duration": "30 hrs",
        "tags":     ["ai-fundamentals", "beginner", "no-code"],
        "description": "Finland's famous open online course covering AI fundamentals, machine learning basics and societal implications. No coding needed.",
        "url":      "https://www.elementsofai.com",
        "cert":     True,
    },
    {
        "title":    "Fast.ai — Practical Deep Learning for Coders",
        "provider": "fast.ai",
        "platform": "fast.ai",
        "level":    "Intermediate",
        "pricing":  "free",
        "duration": "Self-paced",
        "tags":     ["deep-learning", "python", "pytorch"],
        "description": "Top-down, code-first approach to deep learning. Covers vision, NLP and tabular models using PyTorch and the fastai library.",
        "url":      "https://course.fast.ai",
        "cert":     False,
    },
    {
        "title":    "CS50's Introduction to AI with Python",
        "provider": "Harvard University",
        "platform": "edX",
        "level":    "Intermediate",
        "pricing":  "free",
        "duration": "7 weeks",
        "tags":     ["python", "algorithms", "harvard"],
        "description": "Harvard's intro to AI concepts — search, knowledge, uncertainty, optimisation, machine learning, neural networks and NLP with Python.",
        "url":      "https://cs50.harvard.edu/ai/",
        "cert":     True,
    },
    # ---- Paid / Certification ----
    {
        "title":    "AWS Certified AI Practitioner",
        "provider": "Amazon Web Services",
        "platform": "AWS Training",
        "level":    "Beginner",
        "pricing":  "paid",
        "duration": "Self-paced",
        "tags":     ["aws", "cloud", "certification"],
        "description": "AWS's foundational AI/ML certification. Covers AI/ML concepts, AWS AI services (Bedrock, SageMaker, Rekognition) and responsible AI.",
        "url":      "https://aws.amazon.com/certification/certified-ai-practitioner/",
        "cert":     True,
    },
    {
        "title":    "Google Professional Machine Learning Engineer",
        "provider": "Google Cloud",
        "platform": "Google Cloud",
        "level":    "Advanced",
        "pricing":  "paid",
        "duration": "Self-paced",
        "tags":     ["google-cloud", "mlops", "certification"],
        "description": "Professional-level cert for designing, building and productionising ML models on Google Cloud. Highly respected in the industry.",
        "url":      "https://cloud.google.com/learn/certification/machine-learning-engineer",
        "cert":     True,
    },
    {
        "title":    "Microsoft Azure AI Engineer Associate",
        "provider": "Microsoft",
        "platform": "Microsoft Learn",
        "level":    "Intermediate",
        "pricing":  "paid",
        "duration": "Self-paced",
        "tags":     ["azure", "microsoft", "certification"],
        "description": "Build and deploy AI solutions using Azure Cognitive Services, Azure OpenAI, and Azure ML. Leads to the AI-102 certification.",
        "url":      "https://learn.microsoft.com/en-us/credentials/certifications/azure-ai-engineer/",
        "cert":     True,
    },
    {
        "title":    "Deep Learning Specialization",
        "provider": "DeepLearning.AI",
        "platform": "Coursera",
        "level":    "Intermediate",
        "pricing":  "paid",
        "duration": "5 months",
        "tags":     ["deep-learning", "python", "tensorflow"],
        "description": "Andrew Ng's landmark 5-course series. Covers neural networks, CNNs, RNNs, LSTMs, transformers and practical ML projects.",
        "url":      "https://www.coursera.org/specializations/deep-learning",
        "cert":     True,
    },
    {
        "title":    "Machine Learning Specialization",
        "provider": "Stanford + DeepLearning.AI",
        "platform": "Coursera",
        "level":    "Beginner",
        "pricing":  "paid",
        "duration": "3 months",
        "tags":     ["ml", "python", "stanford"],
        "description": "Updated Andrew Ng ML course — supervised learning, unsupervised learning and best practices for building real ML systems.",
        "url":      "https://www.coursera.org/specializations/machine-learning-introduction",
        "cert":     True,
    },
    {
        "title":    "LLMOps: Building Real-World Applications",
        "provider": "DeepLearning.AI",
        "platform": "DeepLearning.AI",
        "level":    "Advanced",
        "pricing":  "free",
        "duration": "1 hr",
        "tags":     ["llmops", "mlops", "production"],
        "description": "Short course on deploying LLMs to production — data pipelines, model evaluation, monitoring and CI/CD for LLM-based applications.",
        "url":      "https://www.deeplearning.ai/short-courses/llmops/",
        "cert":     False,
    },
    {
        "title":    "AI Agents in LangGraph",
        "provider": "DeepLearning.AI",
        "platform": "DeepLearning.AI",
        "level":    "Intermediate",
        "pricing":  "free",
        "duration": "1 hr",
        "tags":     ["agents", "langgraph", "python"],
        "description": "Build agentic AI applications using LangGraph — covers state machines, tool use, human-in-the-loop and multi-agent systems.",
        "url":      "https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/",
        "cert":     False,
    },
    {
        "title":    "Prompt Engineering for Generative AI",
        "provider": "Vanderbilt University",
        "platform": "Coursera",
        "level":    "Beginner",
        "pricing":  "paid",
        "duration": "3 weeks",
        "tags":     ["prompt-engineering", "genai", "beginner"],
        "description": "Comprehensive prompt engineering course covering zero-shot, few-shot, chain-of-thought, ReAct and multimodal prompting techniques.",
        "url":      "https://www.coursera.org/learn/prompt-engineering",
        "cert":     True,
    },
    {
        "title":    "Databricks Generative AI Fundamentals",
        "provider": "Databricks",
        "platform": "Databricks Academy",
        "level":    "Beginner",
        "pricing":  "free",
        "duration": "2 hrs",
        "tags":     ["genai", "databricks", "certification"],
        "description": "Free accreditation from Databricks covering generative AI fundamentals, LLMs, RAG and responsible AI practices.",
        "url":      "https://www.databricks.com/learn/training/generative-ai-fundamentals-accreditation",
        "cert":     True,
    },
    {
        "title":    "Building RAG Agents with LLMs",
        "provider": "NVIDIA",
        "platform": "NVIDIA Deep Learning Institute",
        "level":    "Advanced",
        "pricing":  "paid",
        "duration": "1 day",
        "tags":     ["rag", "nvidia", "agents"],
        "description": "Hands-on workshop from NVIDIA on building retrieval-augmented generation systems and LLM-powered agents at scale.",
        "url":      "https://learn.nvidia.com/courses/course-detail?course_id=course-v1:DLI+S-FX-15+V1",
        "cert":     True,
    },
]


def generate_courses_html() -> str:
    total        = len(COURSES)
    courses_json = _safe_json(COURSES)
    levels       = sorted(set(c["level"] for c in COURSES))

    level_btns = '<button class="filter-btn active" onclick="setLevel(this,\'all\')">All levels</button>'
    for lv in levels:
        safe = lv.replace("'", "\\'")
        level_btns += f'<button class="filter-btn" onclick="setLevel(this,\'{safe}\')">{lv}</button>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Best AI courses and certifications for developers in 2026 — curated and ranked.">
  <title>AI Courses — Happy Tools</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {ADSENSE_CODE}
  {STYLE}
  <style>
    /* ---- COURSE-SPECIFIC STYLES ---- */
    .courses-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 24px;
    }}
    .course-card {{
      background: var(--surface);
      border-radius: var(--radius-md);
      padding: 22px;
      border: 1.5px solid var(--border);
      display: flex;
      flex-direction: column;
      gap: 12px;
      transition: transform .22s, box-shadow .22s, border-color .22s;
    }}
    .course-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(124,106,247,0.13);
      border-color: var(--primary);
    }}
    .course-header {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 10px; }}
    .course-title {{ font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; font-weight: 700; color: var(--dark); line-height: 1.35; flex: 1; }}
    .cert-badge {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.65rem;
      font-weight: 700;
      background: #fef3c7;
      color: #92400e;
      padding: 3px 9px;
      border-radius: 12px;
      white-space: nowrap;
      border: 1px solid #fde68a;
    }}
    .course-meta {{ display: flex; flex-wrap: wrap; gap: 7px; align-items: center; }}
    .badge-provider {{ background: var(--primary-lt); color: var(--primary-dk); }}
    .badge-platform {{ background: #f0fdf4; color: #166534; }}
    .badge-beginner  {{ background: #d1fae5; color: #065f46; }}
    .badge-intermediate {{ background: #fef3c7; color: #92400e; }}
    .badge-advanced  {{ background: #fce7f3; color: #9d174d; }}
    .badge-free2     {{ background: #e0f2fe; color: #075985; }}
    .badge-paid2     {{ background: #fce7f3; color: #9d174d; }}
    .course-desc {{ color: var(--mid); font-size: 0.89rem; line-height: 1.58; flex-grow: 1; }}
    .course-footer {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 4px; }}
    .course-duration {{ font-size: 0.78rem; color: var(--muted); font-family: 'Plus Jakarta Sans', sans-serif; }}

    .platform-section {{ margin-bottom: 36px; }}
    .platform-heading {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--dark);
      margin-bottom: 18px;
      padding-bottom: 10px;
      border-bottom: 2px solid var(--border);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .platform-dot {{
      width: 10px; height: 10px;
      border-radius: 50%;
      background: var(--primary);
      display: inline-block;
    }}
  </style>
</head>
<body>
{nav_html("courses")}
<div class="container">
  <header>
    <img src="{LOGO_URL}" class="logo" alt="Happy Tools">
    <div>
      <h1>AI Courses</h1>
      <p class="tagline">Trending certifications &amp; courses for developers in 2026</p>
    </div>
  </header>

  <div class="ad-space">ADVERTISEMENT</div>

  <div class="filters">
    <input type="text" id="q" placeholder="Search courses..." oninput="applyFilters()">
    <div class="filter-group" id="level-btns">{level_btns}</div>
    <div class="filter-group" id="price-btns">
      <button class="filter-btn active" onclick="setPrice(this,'all')">All pricing</button>
      <button class="filter-btn" onclick="setPrice(this,'free')">Free</button>
      <button class="filter-btn" onclick="setPrice(this,'paid')">Paid</button>
    </div>
    <div class="filter-group" id="cert-btns">
      <button class="filter-btn active" onclick="setCert(this,'all')">All</button>
      <button class="filter-btn" onclick="setCert(this,'yes')">With certificate</button>
    </div>
  </div>

  <p class="stats-bar">Showing <b id="count">{total}</b> of {total} courses</p>
  <div class="courses-grid" id="grid"></div>

  {footer_html()}
</div>

<script id="courses-data" type="application/json">{courses_json}</script>
<script>
(function () {{
  var COURSES     = JSON.parse(document.getElementById('courses-data').textContent);
  var activeLevel = 'all';
  var activePrice = 'all';
  var activeCert  = 'all';

  function levelClass(l) {{
    var m = {{ 'Beginner':'beginner', 'Intermediate':'intermediate', 'Advanced':'advanced' }};
    return 'badge badge-' + (m[l] || 'beginner');
  }}

  function renderCourses(list) {{
    document.getElementById('count').textContent = list.length;
    var grid = document.getElementById('grid');
    if (!list.length) {{
      grid.innerHTML = '<div class="no-results"><h3>No courses found</h3><p>Try different filters.</p></div>';
      return;
    }}
    var html = '';
    for (var i = 0; i < list.length; i++) {{
      var c    = list[i];
      var tags = (c.tags || []).map(function(x) {{ return '<span class="tag">' + x + '</span>'; }}).join('');
      var cert = c.cert ? '<span class="cert-badge">Certificate</span>' : '';
      html +=
        '<div class="course-card">' +
          '<div class="course-header">' +
            '<span class="course-title">' + c.title + '</span>' +
            cert +
          '</div>' +
          '<div class="course-meta">' +
            '<span class="badge badge-provider">' + c.provider + '</span>' +
            '<span class="badge badge-platform">' + c.platform + '</span>' +
            '<span class="' + levelClass(c.level) + '">' + c.level + '</span>' +
            '<span class="badge ' + (c.pricing==="free" ? "badge-free2" : "badge-paid2") + '">' + c.pricing + '</span>' +
          '</div>' +
          '<p class="course-desc">' + c.description + '</p>' +
          '<div class="tool-tags">' + tags + '</div>' +
          '<div class="course-footer">' +
            '<span class="course-duration">&#128336; ' + c.duration + '</span>' +
            '<a href="' + c.url + '" target="_blank" rel="noopener" class="btn">View Course &#8594;</a>' +
          '</div>' +
        '</div>';
    }}
    grid.innerHTML = html;
  }}

  function applyFilters() {{
    var q = document.getElementById('q').value.toLowerCase();
    var filtered = COURSES.filter(function(c) {{
      var mq = !q
        || c.title.toLowerCase().indexOf(q) !== -1
        || c.provider.toLowerCase().indexOf(q) !== -1
        || c.platform.toLowerCase().indexOf(q) !== -1
        || c.description.toLowerCase().indexOf(q) !== -1
        || (c.tags || []).some(function(x) {{ return x.indexOf(q) !== -1; }});
      var ml = activeLevel === 'all' || c.level === activeLevel;
      var mp = activePrice === 'all' || c.pricing === activePrice;
      var mc = activeCert  === 'all' || (activeCert === 'yes' && c.cert);
      return mq && ml && mp && mc;
    }});
    renderCourses(filtered);
  }}

  window.setLevel = function(btn, v) {{
    activeLevel = v;
    document.querySelectorAll('#level-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active'); applyFilters();
  }};
  window.setPrice = function(btn, v) {{
    activePrice = v;
    document.querySelectorAll('#price-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active'); applyFilters();
  }};
  window.setCert = function(btn, v) {{
    activeCert = v;
    document.querySelectorAll('#cert-btns .filter-btn').forEach(function(b) {{ b.classList.remove('active'); }});
    btn.classList.add('active'); applyFilters();
  }};
  window.applyFilters = applyFilters;
  renderCourses(COURSES);
}})();
</script>
</body>
</html>"""


def generate_devtools_html() -> str:
    """Generate Dev Tools page with comprehensive SEO"""
    from seo import get_seo_meta, get_structured_data_software, get_structured_data_breadcrumb, DEVTOOLS_KEYWORDS
    
    seo_meta = get_seo_meta(
        page_type="website",
        title="Free Developer Tools Online — Text Compare, JSON Formatter, XML Validator | Happy Tools",
        description="Free online developer tools: Text Compare & Diff Checker, JSON Formatter & Validator, JSON Compare, XML Formatter, Base64 Encoder/Decoder, URL Encoder, Hash Generator (SHA256, SHA1), UUID Generator. No signup required.",
        keywords=DEVTOOLS_KEYWORDS,
        canonical=f"{SITE_URL}/devtools.html"
    )
    
    breadcrumb = get_structured_data_breadcrumb([
        ("Home", SITE_URL),
        ("Dev Tools", f"{SITE_URL}/devtools.html")
    ])
    
    structured_data = get_structured_data_software(
        name="Happy Tools - Developer Utilities",
        description="Free online developer tools including text compare, JSON formatter, XML validator, and more",
        url=f"{SITE_URL}/devtools.html"
    )
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  {seo_meta}
  <title>Free Developer Tools Online — Text Compare, JSON Formatter, XML Validator</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {ADSENSE_CODE}
  {structured_data}
  {breadcrumb}
  {STYLE}
  <style>
    /* Dev Tools specific styles */
    .tools-nav {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      margin-bottom: 24px;
      padding: 16px;
      background: var(--surface);
      border-radius: var(--radius-md);
      border: 1.5px solid var(--border);
    }}
    .tool-nav-btn {{
      padding: 8px 16px;
      border-radius: 20px;
      border: 1.5px solid var(--border);
      background: var(--surface);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.82rem;
      font-weight: 600;
      cursor: pointer;
      transition: all .2s;
      color: var(--mid);
    }}
    .tool-nav-btn:hover {{ border-color: var(--primary); color: var(--primary); background: var(--primary-lt); }}
    .tool-nav-btn.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
    
    .tool-section {{
      display: none;
      background: var(--surface);
      border-radius: var(--radius-md);
      padding: 24px;
      border: 1.5px solid var(--border);
    }}
    .tool-section.active {{ display: block; }}
    .tool-section h2 {{
      font-size: 1.3rem;
      margin-bottom: 8px;
      color: var(--dark);
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .tool-section p {{ color: var(--muted); margin-bottom: 20px; font-size: 0.9rem; }}
    
    .input-group {{
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 16px;
    }}
    .input-group label {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 600;
      font-size: 0.88rem;
      color: var(--dark);
    }}
    .code-editor {{
      width: 100%;
      min-height: 200px;
      padding: 14px;
      border: 1.5px solid var(--border);
      border-radius: var(--radius-sm);
      font-family: 'Courier New', monospace;
      font-size: 0.88rem;
      background: var(--bg);
      color: var(--dark);
      resize: vertical;
      outline: none;
      transition: border .2s;
    }}
    .code-editor:focus {{ border-color: var(--primary); }}
    
    .two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    @media (max-width: 768px) {{ .two-col {{ grid-template-columns: 1fr; }} }}
    
    .action-bar {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin: 16px 0;
    }}
    .action-btn {{
      padding: 10px 20px;
      border-radius: 22px;
      border: 2px solid var(--primary);
      background: var(--primary);
      color: white;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 600;
      font-size: 0.88rem;
      cursor: pointer;
      transition: all .2s;
    }}
    .action-btn:hover {{ background: var(--primary-dk); border-color: var(--primary-dk); }}
    .action-btn.secondary {{
      background: var(--surface);
      color: var(--primary);
    }}
    .action-btn.secondary:hover {{ background: var(--primary-lt); }}
    
    .result-box {{
      padding: 14px;
      background: var(--bg);
      border: 1.5px solid var(--border);
      border-radius: var(--radius-sm);
      font-family: 'Courier New', monospace;
      font-size: 0.88rem;
      color: var(--dark);
      white-space: pre-wrap;
      word-break: break-all;
      max-height: 400px;
      overflow-y: auto;
    }}
    .diff-line {{ padding: 2px 4px; }}
    .diff-add {{ background: #d1fae5; color: #065f46; }}
    .diff-remove {{ background: #fee2e2; color: #991b1b; }}
    .diff-same {{ color: var(--muted); }}
    
    .error-msg {{ color: #dc2626; background: #fee2e2; padding: 10px 14px; border-radius: var(--radius-sm); margin-top: 12px; }}
    .success-msg {{ color: #065f46; background: #d1fae5; padding: 10px 14px; border-radius: var(--radius-sm); margin-top: 12px; }}
  </style>
</head>
<body>
{nav_html("devtools")}
<div class="container">
  <header>
    <img src="{LOGO_URL}" class="logo" alt="Happy Tools">
    <div>
      <h1>Developer Tools</h1>
      <p class="tagline">Free online utilities — compare, format, encode &amp; validate</p>
    </div>
  </header>

  <div class="ad-space">ADVERTISEMENT</div>

  <div class="tools-nav">
    <button class="tool-nav-btn active" onclick="showTool('text-compare')">Text Compare</button>
    <button class="tool-nav-btn" onclick="showTool('json-formatter')">JSON Formatter</button>
    <button class="tool-nav-btn" onclick="showTool('json-compare')">JSON Compare</button>
    <button class="tool-nav-btn" onclick="showTool('xml-formatter')">XML Formatter</button>
    <button class="tool-nav-btn" onclick="showTool('base64')">Base64 Encode/Decode</button>
    <button class="tool-nav-btn" onclick="showTool('url-encoder')">URL Encoder</button>
    <button class="tool-nav-btn" onclick="showTool('hash')">Hash Generator</button>
    <button class="tool-nav-btn" onclick="showTool('uuid')">UUID Generator</button>
  </div>

  <!-- TEXT COMPARE -->
  <div class="tool-section active" id="text-compare">
    <h2>Text Compare & Diff Checker</h2>
    <p>Compare two text blocks line by line. Perfect for code review, document comparison, and finding differences.</p>
    <div class="two-col">
      <div class="input-group">
        <label>Text 1</label>
        <textarea class="code-editor" id="text1" placeholder="Paste first text here..." aria-label="First text input"></textarea>
      </div>
      <div class="input-group">
        <label>Text 2</label>
        <textarea class="code-editor" id="text2" placeholder="Paste second text here..." aria-label="Second text input"></textarea>
      </div>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="compareText()">Compare</button>
      <button class="action-btn secondary" onclick="clearFields('text1','text2','text-result')">Clear</button>
    </div>
    <div id="text-result"></div>
  </div>

  <!-- JSON FORMATTER -->
  <div class="tool-section" id="json-formatter">
    <h2>JSON Formatter & Validator</h2>
    <p>Format, validate, and beautify JSON with proper indentation. Minify JSON to single line.</p>
    <div class="input-group">
      <label>Input JSON</label>
      <textarea class="code-editor" id="json-input" placeholder='{{"key":"value"}}' aria-label="JSON input"></textarea>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="formatJSON()">Format & Validate</button>
      <button class="action-btn secondary" onclick="minifyJSON()">Minify</button>
      <button class="action-btn secondary" onclick="copyResult('json-output')">Copy</button>
      <button class="action-btn secondary" onclick="clearFields('json-input','json-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Formatted JSON</label>
      <div class="result-box" id="json-output"></div>
    </div>
  </div>

  <!-- JSON COMPARE -->
  <div class="tool-section" id="json-compare">
    <h2>JSON Compare & Diff</h2>
    <p>Compare two JSON objects and highlight differences at the key level.</p>
    <div class="two-col">
      <div class="input-group">
        <label>JSON 1</label>
        <textarea class="code-editor" id="json1" placeholder='{{"key":"value"}}' aria-label="First JSON input"></textarea>
      </div>
      <div class="input-group">
        <label>JSON 2</label>
        <textarea class="code-editor" id="json2" placeholder='{{"key":"value"}}' aria-label="Second JSON input"></textarea>
      </div>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="compareJSON()">Compare JSON</button>
      <button class="action-btn secondary" onclick="clearFields('json1','json2','json-compare-result')">Clear</button>
    </div>
    <div id="json-compare-result"></div>
  </div>

  <!-- XML FORMATTER -->
  <div class="tool-section" id="xml-formatter">
    <h2>XML Formatter & Validator</h2>
    <p>Format and validate XML with proper indentation and structure.</p>
    <div class="input-group">
      <label>Input XML</label>
      <textarea class="code-editor" id="xml-input" placeholder='<root><item>value</item></root>' aria-label="XML input"></textarea>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="formatXML()">Format & Validate</button>
      <button class="action-btn secondary" onclick="copyResult('xml-output')">Copy</button>
      <button class="action-btn secondary" onclick="clearFields('xml-input','xml-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Formatted XML</label>
      <div class="result-box" id="xml-output"></div>
    </div>
  </div>

  <!-- BASE64 -->
  <div class="tool-section" id="base64">
    <h2>Base64 Encoder & Decoder</h2>
    <p>Encode text to Base64 or decode Base64 strings. Supports UTF-8 encoding.</p>
    <div class="input-group">
      <label>Input</label>
      <textarea class="code-editor" id="base64-input" placeholder="Enter text or Base64 string..." aria-label="Base64 input"></textarea>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="encodeBase64()">Encode to Base64</button>
      <button class="action-btn" onclick="decodeBase64()">Decode from Base64</button>
      <button class="action-btn secondary" onclick="copyResult('base64-output')">Copy</button>
      <button class="action-btn secondary" onclick="clearFields('base64-input','base64-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Output</label>
      <div class="result-box" id="base64-output"></div>
    </div>
  </div>

  <!-- URL ENCODER -->
  <div class="tool-section" id="url-encoder">
    <h2>URL Encoder & Decoder</h2>
    <p>Encode or decode URL strings for safe transmission in web applications.</p>
    <div class="input-group">
      <label>Input</label>
      <textarea class="code-editor" id="url-input" placeholder="Enter URL or encoded string..." aria-label="URL input"></textarea>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="encodeURL()">Encode URL</button>
      <button class="action-btn" onclick="decodeURL()">Decode URL</button>
      <button class="action-btn secondary" onclick="copyResult('url-output')">Copy</button>
      <button class="action-btn secondary" onclick="clearFields('url-input','url-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Output</label>
      <div class="result-box" id="url-output"></div>
    </div>
  </div>

  <!-- HASH GENERATOR -->
  <div class="tool-section" id="hash">
    <h2>Hash Generator (SHA-256, SHA-1)</h2>
    <p>Generate cryptographic hashes from text. Client-side processing for security.</p>
    <div class="input-group">
      <label>Input Text</label>
      <textarea class="code-editor" id="hash-input" placeholder="Enter text to hash..." aria-label="Hash input"></textarea>
    </div>
    <div class="action-bar">
      <button class="action-btn" onclick="generateHashes()">Generate Hashes</button>
      <button class="action-btn secondary" onclick="clearFields('hash-input','hash-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Generated Hashes</label>
      <div class="result-box" id="hash-output"></div>
    </div>
  </div>

  <!-- UUID GENERATOR -->
  <div class="tool-section" id="uuid">
    <h2>UUID Generator (v4)</h2>
    <p>Generate random UUIDs (Universally Unique Identifiers) for your projects.</p>
    <div class="action-bar">
      <button class="action-btn" onclick="generateUUID()">Generate 1 UUID</button>
      <button class="action-btn" onclick="generateMultipleUUIDs()">Generate 10 UUIDs</button>
      <button class="action-btn secondary" onclick="copyResult('uuid-output')">Copy</button>
      <button class="action-btn secondary" onclick="clearFields('uuid-output')">Clear</button>
    </div>
    <div class="input-group">
      <label>Generated UUIDs</label>
      <div class="result-box" id="uuid-output"></div>
    </div>
  </div>

  {footer_html()}
</div>

<script>
// Navigation
function showTool(toolId) {{
  document.querySelectorAll('.tool-section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.tool-nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(toolId).classList.add('active');
  event.target.classList.add('active');
}}

// Utilities
function clearFields(...ids) {{
  ids.forEach(id => {{
    const el = document.getElementById(id);
    if (el) el.value = '' || (el.innerHTML = '');
  }});
}}

function copyResult(id) {{
  const el = document.getElementById(id);
  const text = el.textContent || el.value;
  navigator.clipboard.writeText(text).then(() => {{
    showMessage(id, 'Copied to clipboard!', 'success');
  }});
}}

function showMessage(afterId, msg, type) {{
  const existing = document.querySelector('.error-msg, .success-msg');
  if (existing) existing.remove();
  const div = document.createElement('div');
  div.className = type === 'error' ? 'error-msg' : 'success-msg';
  div.textContent = msg;
  document.getElementById(afterId).parentNode.appendChild(div);
  setTimeout(() => div.remove(), 3000);
}}

// TEXT COMPARE
function compareText() {{
  const t1 = document.getElementById('text1').value.split('\\n');
  const t2 = document.getElementById('text2').value.split('\\n');
  const maxLen = Math.max(t1.length, t2.length);
  let html = '<div class="result-box">';
  for (let i = 0; i < maxLen; i++) {{
    const line1 = t1[i] || '';
    const line2 = t2[i] || '';
    if (line1 === line2) {{
      html += `<div class="diff-line diff-same">${{escapeHtml(line1) || '(empty)'}}</div>`;
    }} else {{
      if (line1) html += `<div class="diff-line diff-remove">- ${{escapeHtml(line1)}}</div>`;
      if (line2) html += `<div class="diff-line diff-add">+ ${{escapeHtml(line2)}}</div>`;
    }}
  }}
  html += '</div>';
  document.getElementById('text-result').innerHTML = html;
}}

// JSON FORMATTER
function formatJSON() {{
  try {{
    const input = document.getElementById('json-input').value;
    const parsed = JSON.parse(input);
    document.getElementById('json-output').textContent = JSON.stringify(parsed, null, 2);
  }} catch (e) {{
    showMessage('json-output', 'Invalid JSON: ' + e.message, 'error');
  }}
}}

function minifyJSON() {{
  try {{
    const input = document.getElementById('json-input').value;
    const parsed = JSON.parse(input);
    document.getElementById('json-output').textContent = JSON.stringify(parsed);
  }} catch (e) {{
    showMessage('json-output', 'Invalid JSON: ' + e.message, 'error');
  }}
}}

// JSON COMPARE
function compareJSON() {{
  try {{
    const j1 = JSON.parse(document.getElementById('json1').value);
    const j2 = JSON.parse(document.getElementById('json2').value);
    const diff = jsonDiff(j1, j2);
    document.getElementById('json-compare-result').innerHTML = 
      '<div class="result-box">' + diff + '</div>';
  }} catch (e) {{
    showMessage('json-compare-result', 'Invalid JSON: ' + e.message, 'error');
  }}
}}

function jsonDiff(obj1, obj2, path = '') {{
  let result = '';
  const keys = new Set([...Object.keys(obj1 || {{}}), ...Object.keys(obj2 || {{}})]);
  keys.forEach(key => {{
    const p = path ? `${{path}}.${{key}}` : key;
    const v1 = obj1?.[key];
    const v2 = obj2?.[key];
    if (JSON.stringify(v1) !== JSON.stringify(v2)) {{
      result += `<div class="diff-line diff-remove">- ${{p}}: ${{JSON.stringify(v1)}}</div>`;
      result += `<div class="diff-line diff-add">+ ${{p}}: ${{JSON.stringify(v2)}}</div>`;
    }}
  }});
  return result || '<div class="success-msg">JSON objects are identical!</div>';
}}

// XML FORMATTER
function formatXML() {{
  try {{
    const input = document.getElementById('xml-input').value;
    const parser = new DOMParser();
    const xml = parser.parseFromString(input, 'text/xml');
    const error = xml.querySelector('parsererror');
    if (error) throw new Error('Invalid XML');
    const formatted = new XMLSerializer().serializeToString(xml);
    document.getElementById('xml-output').textContent = formatXMLString(formatted);
  }} catch (e) {{
    showMessage('xml-output', 'Invalid XML: ' + e.message, 'error');
  }}
}}

function formatXMLString(xml) {{
  let formatted = '';
  let indent = 0;
  xml.split(/>\s*</).forEach(node => {{
    if (node.match(/^\\/\\w/)) indent--;
    formatted += '  '.repeat(indent) + '<' + node + '>\\n';
    if (node.match(/^<?\w[^>]*[^\\/]$/)) indent++;
  }});
  return formatted.substring(1, formatted.length - 2);
}}

// BASE64
function encodeBase64() {{
  const input = document.getElementById('base64-input').value;
  document.getElementById('base64-output').textContent = btoa(unescape(encodeURIComponent(input)));
}}

function decodeBase64() {{
  try {{
    const input = document.getElementById('base64-input').value;
    document.getElementById('base64-output').textContent = decodeURIComponent(escape(atob(input)));
  }} catch (e) {{
    showMessage('base64-output', 'Invalid Base64 string', 'error');
  }}
}}

// URL ENCODER
function encodeURL() {{
  const input = document.getElementById('url-input').value;
  document.getElementById('url-output').textContent = encodeURIComponent(input);
}}

function decodeURL() {{
  try {{
    const input = document.getElementById('url-input').value;
    document.getElementById('url-output').textContent = decodeURIComponent(input);
  }} catch (e) {{
    showMessage('url-output', 'Invalid URL encoding', 'error');
  }}
}}

// HASH GENERATOR
async function generateHashes() {{
  const input = document.getElementById('hash-input').value;
  if (!input) return;
  const encoder = new TextEncoder();
  const data = encoder.encode(input);
  
  try {{
    const sha256 = await crypto.subtle.digest('SHA-256', data);
    const sha1 = await crypto.subtle.digest('SHA-1', data);
    
    const output = `SHA-256: ${{arrayToHex(sha256)}}\\n\\nSHA-1: ${{arrayToHex(sha1)}}\\n\\nMD5: (not available in browser - use server-side)`;
    document.getElementById('hash-output').textContent = output;
  }} catch (e) {{
    showMessage('hash-output', 'Error generating hashes', 'error');
  }}
}}

function arrayToHex(buffer) {{
  return Array.from(new Uint8Array(buffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}}

// UUID GENERATOR
function generateUUID() {{
  const uuid = crypto.randomUUID();
  document.getElementById('uuid-output').textContent = uuid;
}}

function generateMultipleUUIDs() {{
  const uuids = Array.from({{length: 10}}, () => crypto.randomUUID()).join('\\n');
  document.getElementById('uuid-output').textContent = uuids;
}}

function escapeHtml(text) {{
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}}
</script>
</body>
</html>"""


def generate_about_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>About — Happy Tools</title>{STYLE}</head>
<body>
{nav_html("about")}
<div class="container" style="max-width:700px;padding-top:40px;">
  <h1 style="color:var(--primary);margin-bottom:16px;">About Happy Tools</h1>
  <p style="line-height:1.7;color:var(--mid);margin-bottom:12px;">
    Happy Tools is a curated directory of the best AI tools, agents and courses available today.
    Our goal is to help developers, creators and teams discover the right AI tool for the job — fast.
  </p>
  <p style="line-height:1.7;color:var(--mid);margin-bottom:12px;">
    The directory is refreshed regularly from live sources including the Hugging Face model hub
    and community-maintained lists, combined with our own hand-picked selections across
    categories like coding, writing, image generation, audio, video and productivity.
  </p>
  <p style="line-height:1.7;color:var(--mid);margin-bottom:28px;">
    Use the search and filters on each page to find what you need, or explore the
    <a href="agents.html" style="color:var(--primary);">AI Agents</a> and
    <a href="courses.html" style="color:var(--primary);">AI Courses</a> sections
    to go deeper.
  </p>
  <a href="index.html" class="btn">&#8592; Browse Tools</a>
</div>
{footer_html()}
</body></html>"""


def generate_privacy_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Privacy — Happy Tools</title>{STYLE}</head>
<body>
{nav_html()}
<div class="container" style="max-width:700px;padding-top:40px;">
  <h1 style="color:var(--primary);margin-bottom:16px;">Privacy Policy</h1>
  <p style="line-height:1.7;color:#555;margin-bottom:12px;">Happy Tools does not collect personal information. We use Google AdSense for advertising, which may use cookies.</p>
  <p style="margin-bottom:24px;"><a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Manage Google Ad settings &#8594;</a></p>
  <a href="index.html" class="btn">&#8592; Back to Home</a>
</div>
{footer_html()}
</body></html>"""


def generate_sitemap() -> str:
    pages = ["", "agents.html", "courses.html", "devtools.html", "about.html", "privacy.html", "scaniq-privacy.html"]
    urls  = "\n".join(f"  <url><loc>{SITE_URL}/{p}</loc><changefreq>weekly</changefreq></url>" for p in pages)
    return f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>"""


# ============================================================================
# 6. SAVE & MAIN
# ============================================================================

def generate_ads_txt() -> str:
    """
    ads.txt tells Google (and other ad networks) which sellers are authorised
    to sell ad inventory for this domain. Required by AdSense to serve ads.
    Format: <ad-system-domain>, <publisher-id>, <account-type>
    """
    return f"google.com, {ADSENSE_ID}, DIRECT, f08c47fec0942fa0\n"


def generate_scaniq_privacy_html() -> str:
    updated = datetime.now().strftime('%B %d, %Y')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="ScanIQ Privacy Policy — how we collect, use and protect your data.">
  <title>ScanIQ — Privacy Policy</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {STYLE}
  <style>
    .policy-wrap {{
      max-width: 760px;
      margin: 0 auto;
      padding: 40px 20px 60px;
    }}
    .policy-wrap h1 {{
      font-size: 2rem;
      margin-bottom: 6px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .policy-meta {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 36px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}
    .policy-wrap h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--dark);
      margin: 32px 0 10px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .policy-wrap p, .policy-wrap li {{
      font-size: 0.95rem;
      color: var(--mid);
      line-height: 1.75;
      margin-bottom: 10px;
    }}
    .policy-wrap ul {{
      padding-left: 20px;
      margin-bottom: 10px;
    }}
    .policy-wrap ul li {{ margin-bottom: 6px; }}
    .highlight-box {{
      background: var(--primary-lt);
      border-left: 4px solid var(--primary);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      padding: 14px 18px;
      margin: 20px 0;
      font-size: 0.92rem;
      color: var(--primary-dk);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 500;
    }}
    .contact-card {{
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px 24px;
      margin-top: 32px;
    }}
    .contact-card h3 {{
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 8px;
      color: var(--dark);
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .contact-card a {{ color: var(--primary); text-decoration: none; }}
    .contact-card a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
{nav_html()}
<div class="policy-wrap">

  <h1>Privacy Policy</h1>
  <p class="policy-meta">
    Applies to: <strong>ScanIQ</strong> Android App &nbsp;·&nbsp;
    Last updated: <strong>{updated}</strong>
  </p>

  <div class="highlight-box">
    ScanIQ is committed to protecting your privacy. This policy explains exactly
    what data we collect, why we collect it, and how you can control it.
  </div>

  <h2>1. Who we are</h2>
  <p>
    ScanIQ is an AI-powered product analyser app for Android, published under the
    Happy Tools umbrella. When you use ScanIQ, you are agreeing to the terms
    described in this Privacy Policy. If you do not agree, please uninstall the app.
  </p>

  <h2>2. Information we collect</h2>

  <p><strong>a) Account information</strong></p>
  <p>
    When you sign in with Google, we receive your <strong>name</strong> and
    <strong>email address</strong> from Google. We use this solely to identify
    your account and personalise your experience. We do not share this with
    any third parties.
  </p>

  <p><strong>b) Camera access</strong></p>
  <p>
    ScanIQ requests access to your device camera so you can scan and photograph
    products for AI analysis. <strong>Images are processed to generate product
    insights and are not stored on our servers beyond the duration of your
    analysis session</strong> unless you explicitly save a result.
    We never use your camera without your active initiation.
  </p>

  <p><strong>c) Product scan data</strong></p>
  <p>
    When you scan a product, the image or barcode is sent to our AI analysis
    service to generate a result. This data may be temporarily cached to
    improve response speed but is not linked to your identity.
  </p>

  <p><strong>d) Data we do NOT collect</strong></p>
  <ul>
    <li>Precise or approximate location</li>
    <li>Contacts or call logs</li>
    <li>Financial or payment information</li>
    <li>Any data while the app is in the background</li>
  </ul>

  <h2>3. How we use your information</h2>
  <ul>
    <li>To authenticate you securely via Google Sign-In</li>
    <li>To process product images and return AI-generated analysis</li>
    <li>To improve the accuracy of our AI model over time (anonymised only)</li>
    <li>To send important app updates or security notices (via your email)</li>
  </ul>
  <p>We will never sell, rent or trade your personal information to third parties.</p>

  <h2>4. Google Sign-In</h2>
  <p>
    ScanIQ uses <strong>Google Sign-In</strong> for authentication. By signing in
    with Google you are also subject to
    <a href="https://policies.google.com/privacy" target="_blank" rel="noopener"
       style="color:var(--primary);">Google's Privacy Policy</a>.
    You can revoke ScanIQ's access to your Google account at any time by visiting
    <a href="https://myaccount.google.com/permissions" target="_blank" rel="noopener"
       style="color:var(--primary);">myaccount.google.com/permissions</a>.
  </p>

  <h2>5. Camera permission</h2>
  <p>
    ScanIQ requests <code>android.permission.CAMERA</code> at runtime.
    You can revoke this permission at any time through your device's
    <strong>Settings → Apps → ScanIQ → Permissions</strong>.
    Revoking camera access will disable the scanning feature but will not
    affect your account or saved results.
  </p>

  <h2>6. Data storage and security</h2>
  <p>
    Your account information is stored securely using industry-standard encryption.
    Product scan images are transmitted over HTTPS and are not permanently stored
    on our servers. We apply appropriate technical and organisational measures to
    protect your data against unauthorised access, loss or misuse.
  </p>

  <h2>7. Data retention</h2>
  <p>
    We retain your account information for as long as your account is active.
    If you delete your account, all associated personal data is permanently
    removed within 30 days. Anonymised, aggregated scan data (with no link
    to your identity) may be retained for model improvement purposes.
  </p>

  <h2>8. Children's privacy</h2>
  <p>
    ScanIQ is not directed at children under the age of 13. We do not knowingly
    collect personal information from children. If you believe a child has
    provided us with personal data, please contact us and we will delete it promptly.
  </p>

  <h2>9. Your rights</h2>
  <p>Depending on your location, you may have the right to:</p>
  <ul>
    <li>Access the personal data we hold about you</li>
    <li>Request correction of inaccurate data</li>
    <li>Request deletion of your account and associated data</li>
    <li>Withdraw consent for data processing at any time</li>
  </ul>
  <p>To exercise any of these rights, please contact us using the details below.</p>

  <h2>10. Changes to this policy</h2>
  <p>
    We may update this Privacy Policy from time to time. When we do, we will
    update the "Last updated" date at the top of this page and notify you via
    the app if the changes are material. Continued use of ScanIQ after any
    changes constitutes acceptance of the updated policy.
  </p>

  <div class="contact-card">
    <h3>Contact us</h3>
    <p style="margin-bottom:6px;">
      If you have any questions, requests or concerns about this Privacy Policy
      or how ScanIQ handles your data, please reach out:
    </p>
    <p style="margin:0;">
      Website: <a href="{SITE_URL}">{SITE_URL}</a>
    </p>
  </div>

  <p style="margin-top:28px;">
    <a href="index.html" class="btn">&#8592; Back to Happy Tools</a>
  </p>

</div>
{footer_html()}
</body>
</html>"""
#====================================================

def generate_scaniq_delete_html() -> str:
    updated = datetime.now().strftime('%B %d, %Y')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="ScanIQ Data Delete Request">
  <title>ScanIQ — Privacy Policy</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {STYLE}
  <style>
    .policy-wrap {{
      max-width: 760px;
      margin: 0 auto;
      padding: 40px 20px 60px;
    }}
    .policy-wrap h1 {{
      font-size: 2rem;
      margin-bottom: 6px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}
    .policy-meta {{
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 36px;
      padding-bottom: 20px;
      border-bottom: 1px solid var(--border);
    }}
    .policy-wrap h2 {{
      font-size: 1.15rem;
      font-weight: 700;
      color: var(--dark);
      margin: 32px 0 10px;
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .policy-wrap p, .policy-wrap li {{
      font-size: 0.95rem;
      color: var(--mid);
      line-height: 1.75;
      margin-bottom: 10px;
    }}
    .policy-wrap ul {{
      padding-left: 20px;
      margin-bottom: 10px;
    }}
    .policy-wrap ul li {{ margin-bottom: 6px; }}
    .highlight-box {{
      background: var(--primary-lt);
      border-left: 4px solid var(--primary);
      border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
      padding: 14px 18px;
      margin: 20px 0;
      font-size: 0.92rem;
      color: var(--primary-dk);
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-weight: 500;
    }}
    .contact-card {{
      background: var(--surface);
      border: 1.5px solid var(--border);
      border-radius: var(--radius-md);
      padding: 20px 24px;
      margin-top: 32px;
    }}
    .contact-card h3 {{
      font-size: 1rem;
      font-weight: 700;
      margin-bottom: 8px;
      color: var(--dark);
      font-family: 'Plus Jakarta Sans', sans-serif;
    }}
    .contact-card a {{ color: var(--primary); text-decoration: none; }}
    .contact-card a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
{nav_html()}
<div class="policy-wrap">

  <h1>Data Delete Policy</h1>
  <p class="policy-meta">
    Applies to: <strong>ScanIQ</strong> Android App &nbsp;·&nbsp;
    Last updated: <strong>{updated}</strong>
  </p>

  <div class="highlight-box">
    ScanIQ is committed to protecting your privacy. This policy explains exactly
    what data we collect, why we collect it, and how you can control it.
  </div>

  <h2>1. How to delete</h2>
  <p>
    If you want to delete the data associated with your account permenantly from our database please send an email from your registered email.
    The topic should be "Delete ScanIQ Account" to happytools@happytools.site
  </p>

  
  <p>
    We may update this Privacy Policy from time to time. When we do, we will
    update the "Last updated" date at the top of this page and notify you via
    the app if the changes are material. Continued use of ScanIQ after any
    changes constitutes acceptance of the updated policy.
  </p>

  <div class="contact-card">
    <h3>Contact us</h3>
    <p style="margin-bottom:6px;">
      If you have any questions, requests or concerns about this Privacy Policy
      or how ScanIQ handles your data, please reach out:
    </p>
    <p style="margin:0;">
      Website: <a href="{SITE_URL}">{SITE_URL}</a>
    </p>
  </div>

  <p style="margin-top:28px;">
    <a href="index.html" class="btn">&#8592; Back to Happy Tools</a>
  </p>

</div>
{footer_html()}
</body>
</html>"""

def save_files(files: Dict[str, str]) -> None:
    os.makedirs("public", exist_ok=True)
    for name, content in files.items():
        with open(f"public/{name}", "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  ✓ public/{name}")


def main():
    print("\n" + "=" * 60)
    print("  HAPPY TOOLS — LIVE AI DIRECTORY BUILDER")
    print("=" * 60)

    tools  = get_all_tools()
    agents = fetch_agents()

    cats = sorted(set(t.get("category", "?") for t in tools))
    print(f"\n  {len(tools)} tools across {len(cats)} categories")
    print(f"  {len(agents)} AI agents")

    print("\n  Generating pages...")
    save_files({
        "index.html":          generate_index_html(tools),
        "agents.html":         generate_agents_html(agents),
        "courses.html":        generate_courses_html(),
        "about.html":          generate_about_html(),
        "privacy.html":        generate_privacy_html(),
        "scaniq-privacy.html": generate_scaniq_privacy_html(),
        "scaniq-delete.html": generate_scaniq_delete_html(),
        "sitemap.xml":         generate_sitemap(),
        "ads.txt":             generate_ads_txt(),
    })

    print("\n" + "=" * 60)
    print("  Done! Preview with:")
    print("  python -m http.server 8080 --directory public")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
