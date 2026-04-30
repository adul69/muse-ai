<div align="center">

# 🎵 MuseAI — AI Music Recommendation Assistant

**Your personal AI curator that transforms how you feel into the perfect Spotify playlist.**

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Spotify](https://img.shields.io/badge/Spotify-Web_API-1DB954?logo=spotify&logoColor=white)](https://developer.spotify.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<p align="center">
  <img src="https://via.placeholder.com/800x400/0f0f1a/1db954?text=MuseAI+Demo+Screenshot" alt="MuseAI Demo" width="700">
</p>

</div>

---

## 🎯 Overview

**MuseAI** is an intelligent music recommendation assistant powered by **Large Language Models (LLM)** and the **Spotify Web API**. Instead of manually browsing genres or predefined moods, you simply **chat naturally** with the AI about how you feel, what you're doing, or what vibe you want — and MuseAI generates a curated Spotify playlist instantly.

> "I just broke up, want something like Coldplay but more depressing and acoustic"
>
> → MuseAI analyzes intent → Maps to audio features → Creates **"Midnight Tears 🌙"** playlist on your Spotify

### ✨ Key Differentiators

- 🧠 **Natural Language Understanding** — No rigid mood categories; talk to it like a friend
- 🎛️ **Audio Feature Mapping** — LLM extracts energy, valence, danceability, tempo, acousticness, instrumentalness
- 🎵 **Spotify Integration** — Auto-creates playlists directly in your account
- 🤖 **Multi-LLM Support** — Works with Xiaomi MiMo, OpenRouter, or demo mode without any API key
- 💬 **Chat-First UX** — Modern, real-time chat interface inspired by ChatGPT & Claude

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 💬 **Conversational AI** | Describe your mood in natural language — no forms, no dropdowns |
| 🎛️ **Smart Audio Feature Extraction** | AI maps your words to Spotify's audio analysis dimensions |
| 🎧 **One-Click Playlist Creation** | Generated playlists appear instantly in your Spotify library |
| 🎨 **Modern Dark UI** | Clean, responsive chat interface with real-time typing indicators |
| 🔄 **Multi-Provider LLM** | Switch between MiMo, OpenRouter, or mock mode via env config |
| 📊 **AI Analysis Sidebar** | See exactly how the AI interpreted your request |
| 🎶 **30s Track Previews** | Listen to song previews directly in the browser before opening Spotify |
| 🔗 **Direct Track Links** | Every track links directly to Spotify |
| 📱 **Responsive Design** | Works seamlessly on desktop and mobile |

---

## 🏗️ Architecture

```
┌─────────────────┐     Natural Language      ┌──────────────┐
│   User Chat     │ ────────────────────────► │  LLM Engine  │
│   (Frontend)    │                           │ (MiMo/Claude)│
└─────────────────┘                           └──────┬───────┘
                                                     │
                                                     ▼
                                            ┌─────────────────┐
                                            │ Intent Analysis │
                                            │ • Mood          │
                                            │ • Energy        │
                                            │ • Valence       │
                                            │ • Genres        │
                                            │ • Artists       │
                                            └────────┬────────┘
                                                     │
                                                     ▼
┌─────────────────┐     Track Recommendations     ┌──────────────┐
│  Spotify API    │ ◄──────────────────────────── │  Audio Map   │
│  (Playlist)     │                               └──────────────┘
└─────────────────┘
```

### Data Flow

1. **User Input** → Natural language description of desired vibe
2. **LLM Analysis** → Extracts structured audio features & metadata
3. **Spotify Recommendations** → Query Spotify with seed genres, artists, and target features
4. **Playlist Creation** → Auto-create and populate playlist in user's Spotify account
5. **Result Display** → Show AI reasoning, track list, and direct Spotify link

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.9+, Flask 3.x |
| **AI/LLM** | Xiaomi MiMo V2.5 / OpenRouter (Claude, GPT, etc.) |
| **Music API** | Spotify Web API (via Spotipy) |
| **Frontend** | Vanilla JS, CSS3, Font Awesome |
| **Styling** | Custom CSS with CSS Variables, Flexbox, Grid |
| **Auth** | OAuth 2.0 (Spotify) |

---

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- A Spotify account (Free or Premium)
- (Optional) LLM API key — MiMo or OpenRouter

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/muse-ai.git
cd muse-ai
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# ─── Spotify ─────────────────────────────────────────
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:5000/callback

# ─── LLM Provider ────────────────────────────────────
# Options: mimoo | openrouter | mock
LLM_PROVIDER=mock

# MiMo (Xiaomi MiMo Orbit)
MIMO_API_KEY=your_mimo_api_key
MIMO_API_URL=https://api.xiaomimimo.com/v1/chat/completions

# OpenRouter (Fallback)
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=anthropic/claude-sonnet-4

# ─── Flask ───────────────────────────────────────────
FLASK_SECRET_KEY=your_random_secret_key
FLASK_DEBUG=true
```

> 💡 **Tip:** Start with `LLM_PROVIDER=mock` to test the app without any LLM API key!

### 5. Set Up Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **"Create App"**
3. Fill in:
   - **App name**: `MuseAI`
   - **Redirect URI**: `http://localhost:5000/callback`
4. Copy **Client ID** and **Client Secret** to your `.env`

### 6. Run the Application

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## 🤖 LLM Provider Configuration

### Option A: Xiaomi MiMo (Recommended for MiMo Orbit Program)

```env
LLM_PROVIDER=mimoo
MIMO_API_KEY=sk-xxxxxxxxxxxxxxxx
MIMO_API_URL=https://api.xiaomimimo.com/v1/chat/completions
```

**Why MiMo?**
- Optimized for Chinese & English multilingual tasks
- V2.5 series supports advanced reasoning and structured output
- Direct integration with Xiaomi AI ecosystem

### Option B: OpenRouter (Universal Access)

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-xxxxxxxxxxxxxxxx
OPENROUTER_MODEL=anthropic/claude-sonnet-4
```

**Supported Models via OpenRouter:**
- `anthropic/claude-sonnet-4` — Best reasoning for complex mood analysis
- `anthropic/claude-opus-4` — Highest quality, slower
- `openai/gpt-4o` — Fast and reliable
- `google/gemini-pro-1.5` — Great multilingual support

### Option C: Mock Mode (Zero API Key)

```env
LLM_PROVIDER=mock
```

Pre-configured responses for demo/testing without any external API costs.

---

## 📸 Usage Examples

### Example 1: Post-Breakup Melancholy

**User:**
> "I just broke up with my girlfriend. I want something sad like Coldplay but more acoustic and quiet. Around 20 songs."

**MuseAI Response:**
- **Detected Mood**: Melancholic and heartbroken
- **Energy**: 25% | **Valence**: 15% | **Acousticness**: 70%
- **Genres**: acoustic, indie, piano, alternative
- **Playlist**: 🌙 *Midnight Tears* — 20 tracks

### Example 2: Coding Focus Session

**User:**
> "I'm coding a complex backend system. Need instrumental music with no vocals, something that helps deep focus for 2 hours."

**MuseAI Response:**
- **Detected Mood**: Deep focus and concentration
- **Energy**: 30% | **Instrumentalness**: 85% | **Valence**: 50%
- **Genres**: ambient, classical, study, piano
- **Playlist**: 🧠 *Deep Focus Mode* — 30 tracks

### Example 3: Friday Night Party

**User:**
> "It's Friday night and I'm hosting a party! Need high energy dance music, something that makes people move!"

**MuseAI Response:**
- **Detected Mood**: High-energy party vibes
- **Energy**: 95% | **Danceability**: 90% | **Valence**: 85%
- **Genres**: edm, dance, pop, house
- **Playlist**: 🎉 *Party All Night* — 25 tracks

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main application (chat UI) |
| `GET` | `/login` | Initiate Spotify OAuth flow |
| `GET` | `/callback` | Spotify OAuth callback handler |
| `GET` | `/logout` | Clear session and logout |
| `POST` | `/chat` | **Main API** — Send user message, returns playlist data |
| `GET` | `/health` | Health check + LLM provider info |

### POST `/chat` Request/Response

**Request:**
```json
{
  "message": "I want chill acoustic music for a rainy Sunday"
}
```

**Response:**
```json
{
  "success": true,
  "llm_analysis": {
    "mood": "Relaxed and contemplative",
    "reasoning": "Low energy with acoustic focus matches rainy day introspection",
    "energy": 0.3,
    "valence": 0.45,
    "genres": ["acoustic", "indie", "folk"]
  },
  "playlist": {
    "name": "Rainy Sunday 🌧️",
    "url": "https://open.spotify.com/playlist/xxxxx",
    "id": "xxxxx"
  },
  "tracks": [
    {
      "name": "Holocene",
      "artists": "Bon Iver",
      "image": "https://i.scdn.co/image/...",
      "preview_url": "https://p.scdn.co/mp3-preview/...",
      "spotify_url": "https://open.spotify.com/track/..."
    }
  ]
}
```

---

## 🧠 How It Works

### 1. Intent Extraction via LLM

The system sends a carefully engineered prompt to the LLM:

```
You are MuseAI, an expert AI music curator.
Analyze the user's request and extract structured data...

Return ONLY a valid JSON object with:
- mood_description
- target_energy (0.0-1.0)
- target_valence (0.0-1.0)
- target_danceability (0.0-1.0)
- target_tempo (BPM)
- target_acousticness (0.0-1.0)
- target_instrumentalness (0.0-1.0)
- genres (Spotify genre seeds)
- artist_references
- track_count
- playlist_name_suggestion
- reasoning
```

### 2. Spotify Audio Features Mapping

The extracted values map directly to [Spotify's Audio Features](https://developer.spotify.com/documentation/web-api/reference/get-audio-features):

| Feature | Range | Description |
|---------|-------|-------------|
| `energy` | 0.0 – 1.0 | Perceptual measure of intensity and power |
| `valence` | 0.0 – 1.0 | Musical positiveness (sad → happy) |
| `danceability` | 0.0 – 1.0 | How suitable for dancing |
| `tempo` | 60 – 200 | Overall BPM |
| `acousticness` | 0.0 – 1.0 | Confidence track is acoustic |
| `instrumentalness` | 0.0 – 1.0 | Likelihood of no vocals |

### 3. Recommendation Engine

Uses Spotify's [`/recommendations`](https://developer.spotify.com/documentation/web-api/reference/get-recommendations) endpoint with:
- **Seed genres** (up to 5) — primary taste anchors
- **Seed artists** (optional) — artist similarity matching
- **Target audio features** — fine-tuned mood alignment

---

## 🗺️ Roadmap

- [x] Core chat-based playlist generation
- [x] Multi-LLM provider support (MiMo, OpenRouter, Mock)
- [x] Real-time chat UI with typing indicators
- [x] AI analysis sidebar
- [x] 🎶 In-browser track previews (30s Spotify clips)
- [ ] 📜 Conversation history & playlist archive
- [ ] 🎯 Mood-based playlist covers (AI-generated images)
- [x] 🌐 Deploy to Render / Railway
- [ ] 📱 PWA support for mobile app-like experience
- [ ] 🔗 Share generated playlists via unique URLs

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug fixes, new features, or documentation improvements.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Ideas for Contributors

- Add more LLM providers (OpenAI, Anthropic direct, local LLMs via Ollama)
- Implement playlist history database (SQLite/PostgreSQL)
- Create a "Vibe Roulette" random playlist feature
- Build a Discord/Telegram bot version
- Add multilingual support (Chinese, Japanese, Indonesian, etc.)

---

## 🚀 Deployment

Deploy MuseAI to the cloud for free using **Render**.

### Option 1: Deploy to Render (Recommended)

Render offers a **free tier** for Python web services with automatic HTTPS.

#### Step 1: Prepare Your Repo

Your repo should already contain:
- `requirements.txt` ✅
- `Procfile` ✅
- `render.yaml` (optional, for infrastructure-as-code) ✅

#### Step 2: Update Spotify Redirect URI

Before deploying, update your Spotify App's redirect URI:

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Open your MuseAI app
3. Click **"Edit Settings"**
4. Add this Redirect URI:
   ```
   https://muse-ai.onrender.com/callback
   ```
5. Click **"Save"**

> ⚠️ **Important:** The redirect URI must match exactly — including `https` and trailing slashes.

#### Step 3: Create Render Account

1. Go to [render.com](https://render.com) and sign up (free)
2. Connect your GitHub account

#### Step 4: Deploy

**Option A: One-Click Deploy (Blueprints)**

If you have `render.yaml` in your repo:

1. In Render dashboard, click **"Blueprints"**
2. Connect your GitHub repo
3. Render will auto-detect `render.yaml` and configure everything
4. Click **"Apply"**

**Option B: Manual Web Service**

1. Click **"New +"** → **"Web Service"**
2. Connect your `muse-ai` GitHub repo
3. Configure:
   | Setting | Value |
   |---------|-------|
   | **Name** | `muse-ai` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 60 app:app` |
   | **Plan** | `Free` |

4. Add **Environment Variables**:

   | Key | Value |
   |-----|-------|
   | `SPOTIFY_CLIENT_ID` | (from Spotify Dashboard) |
   | `SPOTIFY_CLIENT_SECRET` | (from Spotify Dashboard) |
   | `SPOTIFY_REDIRECT_URI` | `https://muse-ai.onrender.com/callback` |
   | `FLASK_SECRET_KEY` | (random 32+ char string) |
   | `FLASK_DEBUG` | `false` |
   | `LLM_PROVIDER` | `mock` (or `openrouter` / `mimoo`) |

5. Click **"Create Web Service"**
6. Wait for build (~2-3 minutes)
7. Your app will be live at: `https://muse-ai.onrender.com`

#### Step 5: Verify

1. Open your deployed URL
2. Click **"Connect with Spotify"**
3. Try generating a playlist!

> 💡 **Free Tier Limitations:** Render free tier spins down after 15 min of inactivity. First request after idle may take 30-60 seconds to wake up.

---

### Option 2: Deploy to Railway

Railway also offers generous free tiers.

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Init project
railway init

# Deploy
railway up
```

Set environment variables in Railway dashboard.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Spotify Web API](https://developer.spotify.com) for music data and recommendations
- [Spotipy](https://spotipy.readthedocs.io) for the excellent Python Spotify library
- [Xiaomi MiMo](https://mimo.xiaomi.com) for the LLM powering intelligent music curation
- [OpenRouter](https://openrouter.ai) for universal LLM API access

---

## 👨‍💻 Author

Built with 🎧 by someone who believes music should find you, not the other way around.

**GitHub:** [@yourusername](https://github.com/yourusername)

---

<div align="center">

⭐ **Star this repo if you found it useful!**

🎵 *"Music is the closest thing we have to a time machine."*

</div>
