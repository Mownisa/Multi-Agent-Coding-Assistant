<div align="center">

# ✨ Multi-Agent Coding Assistant
### Chibi Squad Edition 🪆

*A multi-agent AI coding pipeline with a big, bouncy chibi-doll UI — powered by Gemini Flash, Groq, and friends.*

[![Made with LangGraph](https://img.shields.io/badge/orchestration-LangGraph-1C3C3C?style=flat-square)](https://github.com/langchain-ai/langgraph)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB?style=flat-square)](https://vitejs.dev/)
[![Free Tier Friendly](https://img.shields.io/badge/cost-%240%2Fmo-brightgreen?style=flat-square)]()

<p>
  <a href="https://multi-agent-coding-assistant-ueq9.vercel.app/"><img src="https://img.shields.io/badge/%F0%9F%8C%90_LIVE_DEMO-blue?style=for-the-badge" alt="Live Demo" /></a>
  <a href="https://multi-agent-coding-assistant-ueq9.vercel.app/"><img src="https://img.shields.io/badge/VISIT_CHIBI_SQUAD-orange?style=for-the-badge" alt="Visit" /></a>
  <a href="https://github.com/Mownisa/Multi-Agent-Coding-Assistant"><img src="https://img.shields.io/badge/GITHUB-black?style=for-the-badge&logo=github" alt="GitHub" /></a>
</p>

</div>

---

## 🌸 What is this?

Send it a message. A little squad of AI agents decides what you actually need, then goes to work — live, in front of you, one stage card at a time.

- Say **"hi"** → it just chats back. No wasted pipeline.
- Ask it to **write code** → a coder agent writes it, a reviewer agent actually *executes and lints* it, and if it fails, a researcher agent gathers fix guidance and sends it back for a real retry — not just a comment saying what *should* be fixed.
- Paste code and ask for a **review** → straight to the reviewer, no detour.
- Ask it to **research** something → straight to the researcher, clean answer, no code agents involved.

Every stage streams to the UI in real time over Server-Sent Events, so you watch the squad think instead of staring at a spinner.

## 🤖 Meet the Squad

| Agent | Vibe | What it actually does |
|---|---|---|
| 🔍 **Classifier** | *"Hmm, let me think~"* | Sorts your message into `general_chat`, `write_code`, `review_code`, or `do_research` — so trivial messages never touch the heavy pipeline |
| 💬 **General Chat** | *"Just here to talk!"* | Handles greetings and small talk directly, no agents wasted |
| 💻 **Coder** | *"I'll write the best code!"* | Writes the solution — and on a retry, gets the original task **plus** the exact review failure and research guidance, with explicit instructions to fix the code, not narrate the fix in a comment |
| 📋 **Reviewer** | *"Checking carefully…"* | Actually **executes** the code in a sandboxed subprocess and runs it through `pycodestyle` + `pyflakes` — real PASS/FAIL, not a guess |
| 📚 **Researcher** | *"Searching the web!"* | Pulled in when review fails, to gather concrete fix context before the coder tries again (capped at 2 retries) |
| ⭐ **Finalize** | *"Your magical code is ready~"* | Hands back the real, working artifact — never a stale failure message left over from a bad loop |

## 🛣️ How a message actually flows

```
                    ┌─────────────┐
   your message ──► │  Classifier │
                    └──────┬──────┘
              ┌────────────┼────────────┬─────────────┐
              ▼            ▼            ▼              ▼
       general_chat     Coder       Reviewer       Researcher
            │              │            │  ▲            │
            │              └───────►Reviewer  │          │
            │                          │      └──────────┘
            │                     PASS │  FAIL  (retry, max 2x)
            │                          ▼
            └─────────────────────► Finalize ──► you
```

## 🔋 Built to survive free-tier rate limits

LLM free tiers are stingy and they *will* run out mid-demo. So every call goes through a fallback chain instead of hitting one provider and hoping:

```
Google Gemini Flash → Groq (Llama) → Anthropic Claude Haiku → Together AI → Ollama (local, optional)
```

If one provider is rate-limited, billing-blocked, or just unreachable, the next one picks up the request automatically — and the error you'd see if *all* of them fail tells you exactly which provider failed for which reason (quota / billing / bad key / connection / timeout), instead of one generic, misleading message.

## 🚀 Quick Start

### 1. Grab free API keys (no credit card needed for any of these)

| Provider | Get a key | Why it's in the chain |
|---|---|---|
| **Google Gemini Flash** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) | Primary — generous daily free tier |
| **Groq** | [console.groq.com](https://console.groq.com) | Fast, independent quota pool, great safety net |
| **Anthropic Claude Haiku** *(optional)* | [console.anthropic.com](https://console.anthropic.com/) | Optional fallback — needs a funded account to actually work |
| **Together AI** *(optional)* | [api.together.xyz](https://api.together.xyz/) | Optional fallback |

You only strictly need **one** key (Google or Groq) to run this. More keys = more resilience.

### 2. Configure the backend

```bash
cd backend
cp .env.example .env
# open .env and paste in your key(s)
```

```env
# Primary
GOOGLE_API_KEY=your_key_here
GOOGLE_MODEL_ID=gemini-2.5-flash

# Recommended fallback (fast, generous free tier)
GROQ_API_KEY=your_key_here
GROQ_MODEL_ID=llama-3.3-70b-versatile

# Optional extra fallbacks
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL_ID=claude-haiku-4-5-20251001
TOGETHER_API_KEY=
TOGETHER_MODEL_ID=meta-llama/Llama-3-8b-chat-hf

# Local-only, last resort — leave disabled unless you run Ollama yourself
USE_OLLAMA_FALLBACK=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_ID=llama3.1
```

> ⚠️ **Never commit `.env`.** It's already in `.gitignore` — keep it that way.

### 3. Run it

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173** and say hi to the squad. 🪆

> 🪟 **Windows users:** code execution during review relies on `asyncio` subprocess support, which needs the Proactor event loop policy on Windows. This is already handled at backend startup — if you ever see every review fail with a mysterious exit code `-1`, that policy is the first thing to check.

## 📦 Tech Stack

| Layer | Stack |
|---|---|
| **Frontend** | React + Vite, stage-card UI, live SSE updates |
| **Backend** | FastAPI + LangGraph + LangChain |
| **Orchestration** | LangGraph `StateGraph` with conditional routing and bounded retries |
| **LLMs** | Gemini Flash, Groq (Llama), Claude Haiku, Together AI — automatic fallback |
| **Code review** | `pycodestyle` + `pyflakes` (style/lint) + real sandboxed subprocess execution |

## 🩹 Known quirks worth knowing about

- **Free tiers spin down.** If you deploy on a free hosting tier, the backend may sleep after inactivity and take ~30-50s to wake on the first request. That's the host, not a bug.
- **Daily quotas are real.** Gemini's free tier in particular has a small daily request cap — the fallback chain exists specifically so one provider running dry doesn't take the whole app down.
- **Retries are capped at 2.** If the reviewer keeps failing past that, the pipeline returns the best code it has rather than looping forever.

## 🗺️ Roadmap ideas

- [ ] Persist conversation history per thread
- [ ] Streaming token-by-token output instead of stage-by-stage
- [ ] Pluggable linters beyond Python (currently Python-only review)
- [ ] Per-agent model selection (e.g. cheap model for classify, stronger model for coder)

---

<div align="center">

Made with 🌟 sparkles, ⭐ retries, and a healthy respect for rate limits.

</div>