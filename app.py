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

  @media (max-width: 768px) {
    header { flex-direction: column; gap: 14px; text-align: center; }
    .filters input[type=text] { width: 100%; }
    .tools-grid, .agents-grid { grid-template-columns: 1fr; }
  }
</style>
"""

ADSENSE_CODE = f"""<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>"""


def nav_html(active: str = "") -> str:
    pages = [("tools","index.html","AI Tools"), ("agents","agents.html","AI Agents"), ("courses","courses.html","AI Courses"), ("about","about.html","About")]
    items = "".join(f'<li><a href="{h}" class="{"active" if k==active else ""}">{l}</a></li>' for k,h,l in pages)
    return f"""<nav><div class="nav-container">
  <a class="nav-brand" href="index.html"><img src="{LOGO_URL}" style="width:30px;height:30px;border-radius:50%;" alt="logo"> HAPPY TOOLS</a>
  <ul class="nav-links">{items}</ul>
</div></nav>"""


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
    categories  = sorted(set(t.get("category", "Other") for t in tools))
    tools_json  = _safe_json(tools)
    total       = len(tools)

    cat_btns = '<button class="filter-btn active" onclick="setCategory(this,\'all\')">All</button>'
    for c in categories:
        safe = c.replace("'", "\\'")
        cat_btns += f'<button class="filter-btn" onclick="setCategory(this,\'{safe}\')">{c}</button>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Discover the best AI tools — curated and live-updated daily.">
  <title>Happy Tools — AI Tools Directory</title>
  <link rel="icon" type="image/png" href="{LOGO_URL}">
  {ADSENSE_CODE}
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


def generate_about_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>About — Happy Tools</title>{STYLE}</head>
<body>
{nav_html("about")}
<div class="container" style="max-width:700px;padding-top:40px;">
  <h1 style="color:var(--primary);margin-bottom:16px;">About Happy Tools</h1>
  <p style="line-height:1.7;color:#555;margin-bottom:12px;">Happy Tools is a live-updated directory of the best AI tools and agents. Data is pulled at build time from Hugging Face's public model API, community GitHub awesome lists.</p>
  <p style="line-height:1.7;color:#555;margin-bottom:24px;">Use search and filters to find what you need, or browse the AI Agents section for autonomous systems.</p>
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
    pages = ["", "agents.html", "courses.html", "about.html", "privacy.html"]
    urls  = "\n".join(f"  <url><loc>{SITE_URL}/{p}</loc><changefreq>weekly</changefreq></url>" for p in pages)
    return f"""<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}\n</urlset>"""


# ============================================================================
# 6. SAVE & MAIN
# ============================================================================

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
        "index.html":   generate_index_html(tools),
        "agents.html":  generate_agents_html(agents),
        "courses.html": generate_courses_html(),
        "about.html":   generate_about_html(),
        "privacy.html": generate_privacy_html(),
        "sitemap.xml":  generate_sitemap(),
    })

    print("\n" + "=" * 60)
    print("  Done! Preview with:")
    print("  python -m http.server 8080 --directory public")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()