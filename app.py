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
import requests

# Optional spotipy import — not needed in DEMO mode
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    spotipy = None
    SpotifyOAuth = None

load_dotenv()

# Ensure template folder is absolute path (for WSGI compatibility)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
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

# Demo Mode — runs without Spotify API
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# ─── Mock Track Database ───────────────────────────────────────────

MOCK_TRACKS_DB = {
    "sad": [
        {"name": "Fix You", "artists": "Coldplay", "image": "https://i.scdn.co/image/ab67616d0000b273de09e02aa7febf30b7c02d82", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7LVHVU3tWfcxj5aiPFEW4Q"},
        {"name": "Someone Like You", "artists": "Adele", "image": "https://i.scdn.co/image/ab67616d0000b2732118bf9b198b05a9ded327da", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4kflIGfjdZJW4ot2ioixTB"},
        {"name": "The Night We Met", "artists": "Lord Huron", "image": "https://i.scdn.co/image/ab67616d0000b2739d27034e6dd21760d14f06ab", "preview_url": None, "spotify_url": "https://open.spotify.com/track/0dA2Mk56wEzDgegdC6R17g"},
        {"name": "Skinny Love", "artists": "Bon Iver", "image": "https://i.scdn.co/image/ab67616d0000b273b4b0539c141c5b4c9e89c5c6", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7D5fogC3ffO6iOQy3vPt0W"},
        {"name": "Holocene", "artists": "Bon Iver", "image": "https://i.scdn.co/image/ab67616d0000b273ba71c95ad3c5a6e3f9827f96", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1XQnZTR0ER8y5fGO17uX1R"},
        {"name": "I Will Always Love You", "artists": "Whitney Houston", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4eHbdreAnGOrL27ESd2V8A"},
        {"name": "Creep", "artists": "Radiohead", "image": "https://i.scdn.co/image/ab67616d0000b273df84e1933e2d23dcb0b6ed5a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/70LcF31zb1H0PyJoS1Sx1r"},
        {"name": "Breathe Me", "artists": "Sia", "image": "https://i.scdn.co/image/ab67616d0000b273aa02e77d825e1cddb8ac5ac8", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7JqPM78Bp91VoLqNnlI61F"},
    ],
    "chill": [
        {"name": "Chamber of Reflection", "artists": "Mac DeMarco", "image": "https://i.scdn.co/image/ab67616d0000b273e12fad2b5e5e9e7d1e40d649", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4iv9MM7jTXy2ZfI0yXY83G"},
        {"name": "Pink + White", "artists": "Frank Ocean", "image": "https://i.scdn.co/image/ab67616d0000b273c5649add07ed3720be9d5526", "preview_url": None, "spotify_url": "https://open.spotify.com/track/3xKsf9qdS1CyvXSMEid6g8"},
        {"name": "Sunflower", "artists": "Rex Orange County", "image": "https://i.scdn.co/image/ab67616d0000b273b7e3e7e3e7e3e7e3e7e3e7e3", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4FpD1X7YdZxeHSLIooIrzC"},
        {"name": "Location", "artists": "Khalid", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/152lZdxL1OR0ZMW6Ojm0lr"},
        {"name": "Beside You", "artists": "keshi", "image": "https://i.scdn.co/image/ab67616d0000b2736f6c9e0c6c6c6c6c6c6c6c6c6", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7iN1s77v4J1M2sUEqI6fK0"},
        {"name": "After The Storm", "artists": "Kali Uchis", "image": "https://i.scdn.co/image/ab67616d0000b273b4b0539c141c5b4c9e89c5c6", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1dQOMZz9SkT7ig0w65lQWC"},
        {"name": "Weightless", "artists": "Marconi Union", "image": "https://i.scdn.co/image/ab67616d0000b273c6b4b9e6e6e6e6e6e6e6e6e6", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7k9T7lLGlMQEVg0cS8tze8"},
        {"name": "Space Song", "artists": "Beach House", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1JWC0LZkHV8qGin6MqkS5k"},
    ],
    "energetic": [
        {"name": "Blinding Lights", "artists": "The Weeknd", "image": "https://i.scdn.co/image/ab67616d0000b2738863bc11d2aa12b54f5aeb36", "preview_url": None, "spotify_url": "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"},
        {"name": "Levitating", "artists": "Dua Lipa", "image": "https://i.scdn.co/image/ab67616d0000b273bd26ede1ae69327010d49946", "preview_url": None, "spotify_url": "https://open.spotify.com/track/39LLxExYz6ewLAcYrzQQyP"},
        {"name": "Don't Start Now", "artists": "Dua Lipa", "image": "https://i.scdn.co/image/ab67616d0000b273bd26ede1ae69327010d49946", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6WrI0LAC5M1Rw2MnX2ZvEg"},
        {"name": "Uptown Funk", "artists": "Mark Ronson", "image": "https://i.scdn.co/image/ab67616d0000b273e419ccba0baa8bd3f3d7dcd2", "preview_url": None, "spotify_url": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"},
        {"name": "Shut Up and Dance", "artists": "WALK THE MOON", "image": "https://i.scdn.co/image/ab67616d0000b27343294cfa8d5dc1743e149993", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4kbj5MwxO1bq9wjT5g9HaA"},
        {"name": "Can't Hold Us", "artists": "Macklemore", "image": "https://i.scdn.co/image/ab67616d0000b273c6b4b9e6e6e6e6e6e6e6e6c6", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1mKzBjDMlR3BNOd9r0nQZf"},
        {"name": "Good 4 U", "artists": "Olivia Rodrigo", "image": "https://i.scdn.co/image/ab67616d0000b273a91c10fe9472d9bd89802e5a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4xqrdfXkTW4T0RauPLv3WA"},
        {"name": "Stronger", "artists": "Kanye West", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
    ],
    "focus": [
        {"name": "Experience", "artists": "Ludovico Einaudi", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/3qoftcRxhdRAGh4yXW4j2O"},
        {"name": "Nuvole Bianche", "artists": "Ludovico Einaudi", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6Uq8BnOxvXJsQiFNlTNgE9"},
        {"name": "Time", "artists": "Hans Zimmer", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6ZFbXIJxaIAVAeR6XN4eSF"},
        {"name": "Gymnopédie No. 1", "artists": "Erik Satie", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/2BSEdtXMG2TM4QcuL5MF7x"},
        {"name": "Clair de Lune", "artists": "Claude Debussy", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6CeC7jogx2VEVK9XtZa8bL"},
        {"name": "Weightless", "artists": "Marconi Union", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7k9T7lLGlMQEVg0cS8tze8"},
        {"name": "River Flows in You", "artists": "Yiruma", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/7qiZfU4dY9lQabv8lsDsK7"},
        {"name": "Comptine d'un autre été", "artists": "Yann Tiersen", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1M2l9ReoabUnR6aC0jsyb1"},
    ],
    "party": [
        {"name": "Titanium", "artists": "David Guetta", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/2oEIMSJrDtJnkA5t6544b4"},
        {"name": "Summer", "artists": "Calvin Harris", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/0u2P5u6lvoDfwTw7a5NdaG"},
        {"name": "Don't You Worry Child", "artists": "Swedish House Mafia", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1hER8h0MaXHy1hIecT4Bhh"},
        {"name": "Wake Me Up", "artists": "Avicii", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/0nrRP2bk19rYNIgUMYL78i"},
        {"name": "One Dance", "artists": "Drake", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1zi7xx7UVEFkmKfv06H8x0"},
        {"name": "SexyBack", "artists": "Justin Timberlake", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/0O45fw2L5vs9ks7tZelV0A"},
        {"name": "Sorry", "artists": "Justin Bieber", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/09CtPGIpYB4BrO8qb1RGsF"},
        {"name": "Despacito", "artists": "Luis Fonsi", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6habFhsOp2NvshLv26DqMb"},
    ],
    "sleepy": [
        {"name": "Spiegel im Spiegel", "artists": "Arvo Pärt", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Nocturne Op. 9 No. 2", "artists": "Frédéric Chopin", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Gymnopédie No. 1", "artists": "Erik Satie", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/2BSEdtXMG2TM4QcuL5MF7x"},
        {"name": "Clair de Lune", "artists": "Claude Debussy", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6CeC7jogx2VEVK9XtZa8bL"},
        {"name": "Aqueous Transmission", "artists": "Incubus", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Holocene", "artists": "Bon Iver", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1XQnZTR0ER8y5fGO17uX1R"},
        {"name": "Blackbird", "artists": "The Beatles", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Mad World", "artists": "Gary Jules", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
    ],
    "happy": [
        {"name": "Happy", "artists": "Pharrell Williams", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/60nZcImufyMA1MKQY3dcCH"},
        {"name": "Good as Hell", "artists": "Lizzo", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/1Ax2UChgGRJO6jGX7KlQtY"},
        {"name": "Walking on Sunshine", "artists": "Katrina & The Waves", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Best Day of My Life", "artists": "American Authors", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Can't Stop the Feeling", "artists": "Justin Timberlake", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6RUKPb4LETWmmr3iAEQktW"},
        {"name": "Treasure", "artists": "Bruno Mars", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/4I1CDkCscjT9K7I3KbZmPu"},
        {"name": "Uptown Funk", "artists": "Mark Ronson", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/32OlwWuMpZ6b0aN2RZOeMS"},
        {"name": "September", "artists": "Earth, Wind & Fire", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
    ],
    "angry": [
        {"name": "Break Stuff", "artists": "Limp Bizkit", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Given Up", "artists": "Linkin Park", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Bodies", "artists": "Drowning Pool", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Down with the Sickness", "artists": "Disturbed", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Chop Suey!", "artists": "System of a Down", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Killing in the Name", "artists": "Rage Against The Machine", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Psychosocial", "artists": "Slipknot", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
        {"name": "Before I Forget", "artists": "Slipknot", "image": "https://i.scdn.co/image/ab67616d0000b273e18d217a8b659eaa818a6a9a", "preview_url": None, "spotify_url": "https://open.spotify.com/track/6pWq8TIWJQAAf9oHPjJWgW"},
    ],
}


def get_mock_tracks(mood_key: str, limit: int = 20) -> List[Dict]:
    """Return mock tracks based on detected mood."""
    tracks = MOCK_TRACKS_DB.get(mood_key, MOCK_TRACKS_DB["chill"])
    # Shuffle-ish selection
    import random
    random.seed(mood_key + str(limit))
    selected = random.sample(tracks, min(limit, len(tracks)))
    random.seed()
    return selected


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

        if any(w in msg for w in ["sad", "breakup", "break up", "broke up", "cry", "crying", "heartbreak", "heart broken", "heartbroken", "depressed", "depressing", "depression", "upset", "lonely", "miss her", "miss him", "missing you", "melancholy", "gloomy", "somber", "sorrow", "grief", "mourning", "tear", "tears", "weep"]):
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

        if any(w in msg for w in ["party", "dance", "club", "hype", "turn up", "lit", "turnup", "celebrate", "celebration", "birthday", "weekend vibes", "night out"]):
            return json.dumps({
                "mood_description": "High-energy party vibes",
                "target_energy": 0.95,
                "target_valence": 0.85,
                "target_danceability": 0.9,
                "target_tempo": 130,
                "target_acousticness": 0.1,
                "target_instrumentalness": 0.0,
                "genres": ["edm", "dance", "house", "pop", "party"],
                "artist_references": ["David Guetta", "Calvin Harris"],
                "track_count": 25,
                "playlist_name_suggestion": "Neon Nights 🎉",
                "reasoning": "High energy, valence, and danceability for an electrifying party atmosphere."
            })

        if any(w in msg for w in ["focus", "concentrat", "study", "work", "deep", "coding", "programming", "productive", "productivity", "revision", "exam", "homework", "reading", "writing", "essay", "thesis"]):
            return json.dumps({
                "mood_description": "Deep focus and concentration",
                "target_energy": 0.35,
                "target_valence": 0.5,
                "target_danceability": 0.2,
                "target_tempo": 90,
                "target_acousticness": 0.6,
                "target_instrumentalness": 0.85,
                "genres": ["classical", "ambient", "piano", "study", "lo-fi"],
                "artist_references": ["Ludovico Einaudi", "Hans Zimmer"],
                "track_count": 20,
                "playlist_name_suggestion": "Flow State 🧠",
                "reasoning": "Low danceability, high instrumentalness, moderate energy for sustained focus."
            })

        if any(w in msg for w in ["sleep", "sleepy", "tired", "bed", "rest", "dream", "dreaming", "nap", "rainy", "cozy", "lo-fi", "chill", "relax", "relaxing", "calm", "peaceful", "tranquil", "meditation", "yoga", "spa", "ambient"]):
            return json.dumps({
                "mood_description": "Relaxed and chill",
                "target_energy": 0.2,
                "target_valence": 0.55,
                "target_danceability": 0.2,
                "target_tempo": 70,
                "target_acousticness": 0.8,
                "target_instrumentalness": 0.6,
                "genres": ["ambient", "sleep", "piano", "lo-fi", "chill"],
                "artist_references": ["Nujabes", "J Dilla"],
                "track_count": 15,
                "playlist_name_suggestion": "Cozy Corners 🌧️",
                "reasoning": "Very low energy with high acousticness for a peaceful, relaxing vibe."
            })

        if any(w in msg for w in ["happy", "joy", "joyful", "cheerful", "uplift", "uplifting", "smile", "smiling", "good mood", "feel great", "feeling good", "blessed", "grateful", "excited", "enthusiastic", "optimistic", "positive", "sunny"]):
            return json.dumps({
                "mood_description": "Happy and uplifting",
                "target_energy": 0.75,
                "target_valence": 0.9,
                "target_danceability": 0.7,
                "target_tempo": 120,
                "target_acousticness": 0.3,
                "target_instrumentalness": 0.1,
                "genres": ["pop", "funk", "disco", "happy", "soul"],
                "artist_references": ["Pharrell Williams", "Bruno Mars"],
                "track_count": 20,
                "playlist_name_suggestion": "Sunshine Vibes ☀️",
                "reasoning": "High valence and energy with danceable pop-funk for a feel-good mood."
            })

        if any(w in msg for w in ["angry", "mad", "anger", "rage", "raging", "furious", "aggressive", "aggression", "hate", "hatred", "frustrated", "frustration", "annoyed", "irritated", "pissed", "revenge", "resentment", "bitter"]):
            return json.dumps({
                "mood_description": "Intense and aggressive",
                "target_energy": 0.9,
                "target_valence": 0.2,
                "target_danceability": 0.5,
                "target_tempo": 150,
                "target_acousticness": 0.1,
                "target_instrumentalness": 0.3,
                "genres": ["metal", "rock", "hardcore", "industrial", "alternative"],
                "artist_references": ["Rage Against the Machine", "Metallica"],
                "track_count": 20,
                "playlist_name_suggestion": "Rage Room 🔥",
                "reasoning": "Very high energy, low valence, aggressive genres to channel intense emotions."
            })

        if any(w in msg for w in ["energetic", "energy", "pump", "pumped", "workout", "gym", "power", "powerful", "run", "running", "exercise", "fitness", "training", "cardio", "lift", "lifting", "weights", "motivation", "motivated", "hype", "amped", "fired up"]):
            return json.dumps({
                "mood_description": "Energetic and motivating",
                "target_energy": 0.92,
                "target_valence": 0.7,
                "target_danceability": 0.75,
                "target_tempo": 140,
                "target_acousticness": 0.1,
                "target_instrumentalness": 0.2,
                "genres": ["edm", "hip-hop", "rock", "work-out", "pop"],
                "artist_references": ["Eminem", "The Weeknd"],
                "track_count": 25,
                "playlist_name_suggestion": "Beast Mode 💪",
                "reasoning": "High tempo and energy with motivating genres for peak performance."
            })

        # Default fallback
        return json.dumps({
            "mood_description": "Balanced and versatile",
            "target_energy": 0.5,
            "target_valence": 0.5,
            "target_danceability": 0.5,
            "target_tempo": 100,
            "target_acousticness": 0.5,
            "target_instrumentalness": 0.3,
            "genres": ["pop", "indie", "alternative"],
            "artist_references": [],
            "track_count": 20,
            "playlist_name_suggestion": "MuseAI Mix ✨",
            "reasoning": "Balanced profile that works across moods and activities."
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

def get_spotify_oauth():
    if not SPOTIPY_AVAILABLE:
        return None
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_path=None,
        show_dialog=True,
    )


def get_spotify():
    if not SPOTIPY_AVAILABLE:
        return None
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
    return render_template("index.html", user=user, provider=LLM_PROVIDER, DEMO_MODE=DEMO_MODE)


@app.route("/login")
def login():
    if DEMO_MODE:
        return redirect(url_for("index"))
    sp_oauth = get_spotify_oauth()
    if not sp_oauth:
        return "Spotify not available", 503
    auth_url = sp_oauth.get_authorize_url()
    session["state"] = str(uuid.uuid4())
    return redirect(auth_url)


@app.route("/callback")
def callback():
    if DEMO_MODE:
        return redirect(url_for("index"))
    sp_oauth = get_spotify_oauth()
    if not sp_oauth:
        return "Spotify not available", 503
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
    
    # Check auth unless in demo mode
    if not DEMO_MODE and not sp:
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
        
        # Detect mood key from parsed genres/energy/valence
        mood_key = _detect_mood_key(parsed)
        track_count = min(max(parsed.get("track_count", 20), 5), 50)

        # ─── DEMO MODE: Return mock tracks ─────────────────────
        if DEMO_MODE:
            tracks = get_mock_tracks(mood_key, track_count)
            
            track_info = []
            for t in tracks:
                track_info.append({
                    "name": t["name"],
                    "artists": t["artists"],
                    "image": t["image"],
                    "preview_url": t.get("preview_url"),
                    "spotify_url": t["spotify_url"],
                })

            playlist_name = parsed.get("playlist_name_suggestion", "MuseAI Playlist ✨")
            
            return jsonify({
                "success": True,
                "demo": True,
                "llm_analysis": {
                    "mood": parsed.get("mood_description"),
                    "reasoning": parsed.get("reasoning"),
                    "energy": parsed.get("target_energy"),
                    "valence": parsed.get("target_valence"),
                    "genres": parsed.get("genres", []),
                },
                "playlist": {
                    "name": playlist_name,
                    "url": f"https://open.spotify.com/search/{playlist_name.replace(' ', '%20')}",
                    "id": "demo-mode",
                },
                "tracks": track_info,
            })

        # ─── SPOTIFY MODE: Real integration ────────────────────
        rec_params = {
            "limit": track_count,
            "target_energy": parsed.get("target_energy", 0.5),
            "target_valence": parsed.get("target_valence", 0.5),
            "target_danceability": parsed.get("target_danceability", 0.5),
            "target_tempo": parsed.get("target_tempo", 120),
        }

        for key in ["target_acousticness", "target_instrumentalness"]:
            if key in parsed:
                rec_params[key] = parsed[key]

        genres = parsed.get("genres", ["pop"])[:5]
        rec_params["seed_genres"] = genres

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
            max_genres = 5 - len(artist_ids)
            rec_params["seed_genres"] = genres[:max_genres]

        recs = sp.recommendations(**rec_params)
        tracks = recs.get("tracks", [])
        if not tracks:
            return jsonify({"error": "No tracks found for this vibe. Try rephrasing!"}), 404

        track_uris = [t["uri"] for t in tracks]

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


def _detect_mood_key(parsed: dict) -> str:
    """Map LLM output to a mood key for mock track selection."""
    mood = parsed.get("mood_description", "").lower()
    genres = [g.lower() for g in parsed.get("genres", [])]
    energy = parsed.get("target_energy", 0.5)
    valence = parsed.get("target_valence", 0.5)
    
    # Check explicit mood words
    if any(w in mood for w in ["sad", "melancholic", "heartbroken", "depress", "cry", "tear"]):
        return "sad"
    if any(w in mood for w in ["focus", "study", "concentrat", "work", "deep"]):
        return "focus"
    if any(w in mood for w in ["party", "dance", "club", "hype", "celebrat"]):
        return "party"
    if any(w in mood for w in ["sleep", "tired", "bed", "rest", "dream"]):
        return "sleepy"
    if any(w in mood for w in ["happy", "joy", "cheerful", "uplift", "smile"]):
        return "happy"
    if any(w in mood for w in ["angry", "mad", "rage", "furious", "aggressive"]):
        return "angry"
    if any(w in mood for w in ["energetic", "pump", "workout", "gym", "power"]):
        return "energetic"
    
    # Fallback based on features
    if energy < 0.3 and valence < 0.3:
        return "sad"
    if energy < 0.3 and valence >= 0.3:
        return "sleepy"
    if energy > 0.8:
        return "party" if valence > 0.5 else "angry"
    if valence > 0.7:
        return "happy"
    
    return "chill"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "llm_provider": LLM_PROVIDER})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
