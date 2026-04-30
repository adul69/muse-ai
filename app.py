"""
MuseAI — AI Music Recommendation Assistant
Powered by LLM + Spotify Web API
"""

import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from flask import (
    Flask, request, redirect, session, url_for,
    render_template, jsonify
)
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")

# ─── Config ────────────────────────────────────────────────────────

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:5000/callback")
SPOTIFY_SCOPE = "playlist-modify-public playlist-modify-private user-read-private"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_API_URL = os.getenv("MIMO_API_URL", "https://api.xiaomimimo.com/v1/chat/completions")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4")


# ─── LLM Provider Abstraction ──────────────────────────────────────

class LLMProvider:
    def chat(self, system_prompt: str, user_message: str) -> str:
        raise NotImplementedError


class MiMoProvider(LLMProvider):
    def chat(self, system_prompt: str, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {MIMO_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "mimo-v2.5",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        resp = requests.post(MIMO_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class OpenRouterProvider(LLMProvider):
    def chat(self, system_prompt: str, user_message: str) -> str:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/muse-ai-playlist",
            "X-Title": "MuseAI",
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 1000,
        }
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


class MockProvider(LLMProvider):
    """Fallback: simulates LLM without API key (demo mode)."""

    def chat(self, system_prompt: str, user_message: str) -> str:
        msg = user_message.lower()

        if any(w in msg for w in ["sad", "breakup", "cry", "heartbreak", "depressed"]):
            return json.dumps({
                "mood_description": "Melancholic and heartbroken",
                "target_energy": 0.25,
                "target_valence": 0.15,
                "target_danceability": 0.3,
                "target_tempo": 75,
                "target_acousticness": 0.7,
                "target_instrumentalness": 0.4,
                "genres": ["acoustic", "indie", "piano", "alternative"],
                "artist_references": ["Coldplay", "Adele"],
                "track_count": 20,
                "playlist_name_suggestion": "Midnight Tears 🌙",
                "reasoning": "Low energy and valence with acoustic focus matches the melancholic mood."
            })

        if any(w in msg for w in ["party", "dance", "club", "hype"]):
            return json.dumps({
                "mood_description": "High-energy party vibes",
                "target_energy": 0.95,
                "target_valence": 0.85,
                "target_danceability": 0.9,
                "target_tempo": 130,
                "target_acousticness": 0.1,
                "target_instrumentalness": 0.1,
                "genres": ["edm", "dance", "pop", "house"],
                "artist_references": ["David Guetta", "Calvin Harris"],
                "track_count": 25,
                "playlist_name_suggestion": "Party All Night 🎉",
                "reasoning": "Maximum energy and danceability for a party atmosphere."
            })

        if any(w in msg for w in ["focus", "study", "work", "concentrate", "coding"]):
            return json.dumps({
                "mood_description": "Deep focus and concentration",
                "target_energy": 0.3,
                "target_valence": 0.5,
                "target_danceability": 0.2,
                "target_tempo": 90,
                "target_acousticness": 0.6,
                "target_instrumentalness": 0.85,
                "genres": ["ambient", "classical", "study", "piano"],
                "artist_references": ["Ludovico Einaudi", "Hans Zimmer"],
                "track_count": 30,
                "playlist_name_suggestion": "Deep Focus Mode 🧠",
                "reasoning": "Low energy, high instrumentalness, and calm genres support concentration."
            })

        # Default: chill
        return json.dumps({
            "mood_description": "Relaxed and chill",
            "target_energy": 0.4,
            "target_valence": 0.55,
            "target_danceability": 0.45,
            "target_tempo": 100,
            "target_acousticness": 0.5,
            "target_instrumentalness": 0.3,
            "genres": ["chill", "indie", "acoustic", "lo-fi"],
            "artist_references": ["Mac DeMarco", "Frank Ocean"],
            "track_count": 20,
            "playlist_name_suggestion": "Chill Vibes Only 😌",
            "reasoning": "Balanced energy and valence with chill genres for relaxation."
        })


def get_llm_provider() -> LLMProvider:
    provider = LLM_PROVIDER.lower()
    if provider == "mimo":
        if not MIMO_API_KEY:
            raise ValueError("MIMO_API_KEY not set")
        return MiMoProvider()
    if provider == "openrouter":
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not set")
        return OpenRouterProvider()
    return MockProvider()


# ─── Spotify Helpers ───────────────────────────────────────────────

def get_spotify_oauth() -> SpotifyOAuth:
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=None,
        show_dialog=True,
    )


def get_spotify() -> Optional[spotipy.Spotify]:
    token_info = session.get("token_info")
    if not token_info:
        return None
    sp_oauth = get_spotify_oauth()
    if sp_oauth.is_token_expired(token_info):
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
        session["token_info"] = token_info
    return spotipy.Spotify(auth=token_info["access_token"])


# ─── System Prompt for LLM ─────────────────────────────────────────

MUSIC_CURATOR_PROMPT = """You are MuseAI, an expert AI music curator.
Analyze the user's request and extract structured data for generating a Spotify playlist.

Return ONLY a valid JSON object with this exact structure:
{
  "mood_description": "Brief description of the detected mood",
  "target_energy": 0.0,
  "target_valence": 0.0,
  "target_danceability": 0.0,
  "target_tempo": 120,
  "target_acousticness": 0.5,
  "target_instrumentalness": 0.0,
  "genres": ["genre1", "genre2", "genre3"],
  "artist_references": ["artist1", "artist2"],
  "track_count": 20,
  "playlist_name_suggestion": "Creative Playlist Name with Emoji",
  "reasoning": "Explain why these choices fit the user's request"
}

Guidelines:
- target_energy (0.0-1.0): 0 = calm/sleepy, 1 = energetic/intense
- target_valence (0.0-1.0): 0 = sad/angry/melancholic, 1 = happy/joyful
- target_danceability (0.0-1.0): 0 = not danceable, 1 = very danceable
- target_tempo (60-200): BPM (beats per minute)
- target_acousticness (0.0-1.0): 0 = electronic/produced, 1 = acoustic
- target_instrumentalness (0.0-1.0): 0 = vocal-heavy, 1 = instrumental
- genres: Use Spotify genre seeds (pop, rock, indie, acoustic, edm, classical, jazz, hip-hop, metal, blues, country, folk, electronic, house, techno, r-n-b, soul, funk, reggae, latin, k-pop, lo-fi, ambient, piano, study, sleep)
- artist_references: Artists mentioned by user or similar artists
- track_count: 5-50, default 20
- playlist_name_suggestion: Creative, mood-reflecting, include an emoji
- reasoning: Brief explanation of your choices

IMPORTANT: Respond with ONLY the JSON object, no markdown, no backticks, no extra text."""


# ─── Routes ────────────────────────────────────────────────────────

@app.route("/")
def index():
    sp = get_spotify()
    user = None
    if sp:
        try:
            user = sp.current_user()
        except Exception:
            session.clear()
    return render_template("index.html", user=user, provider=LLM_PROVIDER)


@app.route("/login")
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    session["state"] = str(uuid.uuid4())
    return redirect(auth_url)


@app.route("/callback")
def callback():
    sp_oauth = get_spotify_oauth()
    code = request.args.get("code")
    error = request.args.get("error")
    if error:
        return f"Auth error: {error}", 400
    if not code:
        return "Missing code", 400
    try:
        token_info = sp_oauth.get_access_token(code, check_cache=False)
        session["token_info"] = token_info
        return redirect(url_for("index"))
    except Exception as e:
        return f"Auth failed: {e}", 400


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/chat", methods=["POST"])
def chat():
    """Main chat endpoint: receives user message, calls LLM, generates playlist."""
    sp = get_spotify()
    if not sp:
        return jsonify({"error": "Not authenticated with Spotify"}), 401

    data = request.get_json(force=True)
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        # 1. Call LLM to analyze intent
        llm = get_llm_provider()
        llm_response = llm.chat(MUSIC_CURATOR_PROMPT, user_message)

        # Clean response (remove markdown code fences if any)
        cleaned = llm_response.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned.rsplit("\n", 1)[0]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)

        # 2. Build Spotify recommendation params
        rec_params = {
            "limit": min(max(parsed.get("track_count", 20), 5), 50),
            "target_energy": parsed.get("target_energy", 0.5),
            "target_valence": parsed.get("target_valence", 0.5),
            "target_danceability": parsed.get("target_danceability", 0.5),
            "target_tempo": parsed.get("target_tempo", 120),
        }

        # Optional audio features
        for key in ["target_acousticness", "target_instrumentalness"]:
            if key in parsed:
                rec_params[key] = parsed[key]

        # Seed genres (max 5)
        genres = parsed.get("genres", ["pop"])[:5]
        rec_params["seed_genres"] = genres

        # Seed artists (max 5 total seeds)
        artist_refs = parsed.get("artist_references", [])
        artist_ids = []
        if artist_refs:
            for name in artist_refs[:5]:
                try:
                    result = sp.search(q=f"artist:{name}", type="artist", limit=1)
                    items = result.get("artists", {}).get("items", [])
                    if items:
                        artist_ids.append(items[0]["id"])
                except Exception:
                    continue
                if len(artist_ids) + len(genres) >= 5:
                    break

        if artist_ids:
            rec_params["seed_artists"] = artist_ids
            # Adjust genres if total seeds > 5
            max_genres = 5 - len(artist_ids)
            rec_params["seed_genres"] = genres[:max_genres]

        # 3. Get recommendations
        recs = sp.recommendations(**rec_params)
        tracks = recs.get("tracks", [])
        if not tracks:
            return jsonify({"error": "No tracks found for this vibe. Try rephrasing!"}), 404

        track_uris = [t["uri"] for t in tracks]

        # 4. Create playlist
        user = sp.current_user()
        user_id = user["id"]
        playlist_name = parsed.get("playlist_name_suggestion", "MuseAI Playlist ✨")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        description = (
            f"Generated by MuseAI at {timestamp} | Mood: {parsed.get('mood_description', 'Unknown')} | "
            f"{parsed.get('reasoning', '')[:100]}"
        )

        playlist = sp.user_playlist_create(
            user=user_id,
            name=playlist_name,
            public=False,
            description=description,
        )
        sp.playlist_add_items(playlist["id"], track_uris)

        # 5. Prepare response
        track_info = []
        for t in tracks:
            artists = ", ".join(a["name"] for a in t["artists"])
            track_info.append({
                "name": t["name"],
                "artists": artists,
                "image": t["album"]["images"][0]["url"] if t["album"]["images"] else None,
                "preview_url": t.get("preview_url"),
                "spotify_url": t["external_urls"]["spotify"],
            })

        return jsonify({
            "success": True,
            "llm_analysis": {
                "mood": parsed.get("mood_description"),
                "reasoning": parsed.get("reasoning"),
                "energy": parsed.get("target_energy"),
                "valence": parsed.get("target_valence"),
                "genres": genres,
            },
            "playlist": {
                "name": playlist["name"],
                "url": playlist["external_urls"]["spotify"],
                "id": playlist["id"],
            },
            "tracks": track_info,
        })

    except json.JSONDecodeError as e:
        return jsonify({"error": f"Failed to parse AI response: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "llm_provider": LLM_PROVIDER})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
