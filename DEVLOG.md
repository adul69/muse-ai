# 🛠️ MuseAI — Dev Log: Building with AI

> Documenting the collaborative AI-driven development process behind MuseAI.

---

## 📋 Project Overview

| Attribute | Detail |
|-----------|--------|
| **Project** | MuseAI — AI Music Recommendation Assistant |
| **Duration** | ~3 days |
| **Collaboration** | Human (Adul69) + AI Agent (Hermes) |
| **Approach** | Iterative coding, debugging, and deployment via conversational AI |
| **Live Demo** | https://adul69.pythonanywhere.com |
| **GitHub** | https://github.com/adul69/muse-ai |

---

## 🗓️ Build Timeline

### Day 1: Core Architecture & Spotify Integration

**Goal:** Build Flask app with Spotify OAuth + LLM integration.

**Key Actions:**
- Initialized Flask project with Spotify API (spotipy)
- Implemented OAuth 2.0 login flow
- Created LLM provider abstraction (MiMo, OpenRouter, Mock fallback)
- Built structured JSON extraction prompt for mood analysis
- Added playlist generation via Spotify Recommendations API

**Code Iteration:**
```bash
# First prototype — basic auth + LLM chat
$ git log --oneline
f5d6014 feat: initial release of MuseAI
```

---

### Day 2: Demo Mode & Deployment Challenges

**Goal:** Make the app runnable without Spotify API credentials for showcases.

**Key Actions:**
- Added `DEMO_MODE` environment variable
- Built mock track database (60+ tracks, 8 mood categories)
- Implemented mood auto-detection from LLM analysis
- Created new landing page with "Try Demo" button
- Attempted deployment on multiple platforms (localtunnel, serveo, cloudflared)

**Challenges Faced:**
| Challenge | Solution |
|-----------|----------|
| No Spotify dev account for reviewers | Built demo mode with curated mock tracks |
| Tunnel services blocked by ISP | Migrated to PythonAnywhere (free, no CC) |
| `spotipy` import failing on PA | Made spotipy optional — only loads in production mode |

**Commits:**
```
7c060f6 feat: add Demo Mode — run without Spotify API
d2db47a feat: add production deployment config for Render
1817a9c feat: add 30s track preview playback in browser
```

---

### Day 3: PythonAnywhere Deployment & Bug Fixes

**Goal:** Get stable live demo running on free hosting.

**Key Actions:**
- Fixed WSGI config for PythonAnywhere (`/home/Adul69/muse-ai` path)
- Debugged `ModuleNotFoundError` — found username case sensitivity issue
- Made `spotipy` import optional with try/except wrapper
- Fixed template folder path to absolute for WSGI compatibility

**Debug Session (Excerpt):**
```python
# Initial WSGI — failed with ModuleNotFoundError
from app import app as application  # ❌ spotipy not installed

# Fixed — made imports optional
import os
os.environ['DEMO_MODE'] = 'true'

try:
    import spotipy
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False  # ✅ Demo mode works without spotipy
```

**Commits:**
```
f941ff8 fix: PythonAnywhere WSGI compat
3e3e5a8 fix: make spotipy optional for DEMO_MODE
7b7399e fix: chat network error + GitHub link + mock keywords
```

---

## 🧠 AI Collaboration Highlights

### 1. Long-Chain Reasoning Implementation
The AI helped architect a 4-stage pipeline:
1. **Semantic Understanding** — LLM parses natural language mood
2. **Structured Extraction** — JSON with audio features (energy, valence, etc.)
3. **Mood Classification** — Custom `_detect_mood_key()` maps to 8 categories
4. **Track Retrieval** — Demo DB or Spotify API based on classified mood

### 2. Iterative Debugging
Multiple rounds of debugging via conversation:
- WSGI path issues → Fixed absolute paths
- Missing dependencies → Made imports optional
- JavaScript null references → Fresh DOM queries on each call
- Keyword matching gaps → Expanded from 5 to 80+ keywords

### 3. Deployment Strategy
Evaluated 5+ hosting options collaboratively:
- Render (needs CC for Blueprint)
- Koyeb (CLI install blocked)
- Cloudflare Tunnel (download timeout)
- Localtunnel/Serveo (blocked by ISP)
- ✅ **PythonAnywhere** (free, no CC, always-on)

---

## 📸 Screenshots

### 1. Terminal — Git Clone & Dependencies
![Terminal showing git clone and pip install](docs/screenshots/terminal-setup.png)

### 2. PythonAnywhere Bash Console
![PA console showing successful deployment](docs/screenshots/pa-console.png)

### 3. Live Demo — Chat Interface
![MuseAI chat with playlist generation](docs/screenshots/demo-chat.png)

### 4. GitHub Repository
![GitHub repo with README and commits](docs/screenshots/github-repo.png)

---

## 🏗️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10, Flask |
| AI/LLM | OpenRouter (Claude), MiMo, MockProvider |
| Music API | Spotify Web API (spotipy) — optional |
| Frontend | Vanilla JS, HTML5, CSS3 |
| Deployment | PythonAnywhere (WSGI) |
| Version Control | Git + GitHub |

---

## ✅ Final Checklist

- [x] Natural language mood analysis
- [x] Structured audio feature extraction
- [x] Mock track database (8 moods, 60+ tracks)
- [x] Spotify integration (optional)
- [x] Live demo deployment
- [x] Demo mode (no API keys needed)
- [x] Mobile-responsive UI
- [x] GitHub repository with documentation

---

*Built collaboratively with AI assistance. All commits, fixes, and deployment configurations were planned and executed through conversational AI-driven workflow.*
