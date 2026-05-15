import streamlit as st
from groq import Groq
import secrets
import hashlib
import requests
from datetime import datetime, timedelta
from supabase import create_client, Client

# ── Optional packages (install via requirements.txt) ──────────────────────────
try:
    from extra_streamlit_components import CookieManager
    _COOKIES_OK = True
except ImportError:
    _COOKIES_OK = False

try:
    from streamlit_js_eval import get_geolocation
    _GEO_OK = True
except ImportError:
    _GEO_OK = False
# ──────────────────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────
# 1. PAGE CONFIG & STYLING
# ─────────────────────────────────────────
st.set_page_config(page_title="Lakshmeeyam AI", page_icon="🚀", layout="wide")

# ── Google Analytics 4 via streamlit-analytics2 ───────────────────────────────
# Injects GA4 into the real page <head> (not an iframe) so Google detects it.
# Add to requirements.txt: streamlit-analytics2
try:
    import streamlit_analytics2 as streamlit_analytics
    streamlit_analytics.start_tracking(
        ga4_id="G-98JQK90KWX",
        verbose=False,
        unsafe_password=""
    )
    _ANALYTICS_OK = True
except Exception:
    _ANALYTICS_OK = False
# ──────────────────────────────────────────────────────────────────────────────

# ── Theme init (must be before CSS render) ───────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
_DARK = st.session_state.theme == "dark"

# CSS variables resolved by Python so the markdown block stays static
_T = {
    "bg"       : "#0a0a1a" if _DARK else "#ffffff",
    "bg2"      : "#0d1b2a" if _DARK else "#f8f8f8",
    "sidebar"  : "rgba(5,10,25,0.97)" if _DARK else "#f0f0f0",
    "card"     : "rgba(255,255,255,0.04)" if _DARK else "rgba(0,0,0,0.04)",
    "card_b"   : "rgba(0,212,255,0.25)" if _DARK else "rgba(0,0,0,0.12)",
    "txt"      : "#ffffff" if _DARK else "#111111",
    "txt2"     : "rgba(255,255,255,0.55)" if _DARK else "rgba(0,0,0,0.55)",
    "txt3"     : "rgba(255,255,255,0.3)"  if _DARK else "rgba(0,0,0,0.3)",
    "accent"   : "#00d4ff",
    "accent2"  : "#7b2fff",
    "red"      : "#ff4444",
    "green"    : "#00ff88",
    "inp_bg"   : "rgba(0,0,0,0.45)" if _DARK else "#ffffff",
    "inp_txt"  : "#ffffff" if _DARK else "#111111",
    "inp_b"    : "rgba(0,212,255,0.3)" if _DARK else "rgba(0,0,0,0.2)",
    "tab_bg"   : "rgba(0,212,255,0.05)" if _DARK else "rgba(0,0,0,0.05)",
    "tab_sel"  : "rgba(0,212,255,0.18)" if _DARK else "rgba(0,0,0,0.12)",
    "weather_bg": "linear-gradient(135deg,rgba(0,100,200,0.2),rgba(0,50,100,0.3))" if _DARK else "linear-gradient(135deg,#e8f4ff,#c8e8ff)",
    "weather_txt": "white" if _DARK else "#003366",
    # YouTube Music theme vars
    "ytm_bg"   : "#0f0f0f" if _DARK else "#ffffff",
    "ytm_card" : "#1a1a1a" if _DARK else "#f2f2f2",
    "ytm_card2": "#212121" if _DARK else "#e8e8e8",
    "ytm_txt"  : "#ffffff" if _DARK else "#030303",
    "ytm_txt2" : "#aaaaaa" if _DARK else "#606060",
    "ytm_red"  : "#ff0000",
    "ytm_bar"  : "#1f1f1f" if _DARK else "#f8f8f8",
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&family=Roboto:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {{ font-family: "Rajdhani", sans-serif; }}

.stApp {{
    background: {_T["bg"]};
    min-height: 100vh;
    transition: background 0.3s;
}}

/* ── Main card ── */
.main-box {{
    background: {_T["card"]};
    padding: 25px;
    border-radius: 16px;
    border: 1px solid {_T["card_b"]};
    color: {_T["txt"]};
    margin-bottom: 20px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.18);
    backdrop-filter: blur(10px);
}}

/* ── Hero title ── */
.hero-title {{
    font-family: "Orbitron", sans-serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #7b2fff, #00d4ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    animation: shimmer 3s infinite;
    margin-bottom: 0.2rem;
}}
.hero-sub {{
    text-align: center;
    color: rgba(0,212,255,0.6);
    font-size: 1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}}
@keyframes shimmer {{ 0%{{background-position:0%}} 50%{{background-position:100%}} 100%{{background-position:0%}} }}

/* ── Buttons ── */
.stButton > button {{
    background: linear-gradient(135deg, rgba(0,212,255,0.12), rgba(123,47,255,0.12));
    color: {_T["accent"]};
    border: 1px solid rgba(0,212,255,0.35);
    border-radius: 8px;
    font-family: "Rajdhani", sans-serif;
    font-weight: 600;
    letter-spacing: 0.8px;
    transition: all 0.25s;
}}
.stButton > button:hover {{
    background: linear-gradient(135deg, rgba(0,212,255,0.28), rgba(123,47,255,0.28));
    border-color: {_T["accent"]};
    box-shadow: 0 0 14px rgba(0,212,255,0.35);
    transform: translateY(-1px);
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {{
    background: {_T["inp_bg"]} !important;
    color: {_T["inp_txt"]} !important;
    border: 1px solid {_T["inp_b"]} !important;
    border-radius: 8px !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: transparent; }}
.stTabs [data-baseweb="tab"] {{
    background: {_T["tab_bg"]};
    border: 1px solid rgba(0,212,255,0.18);
    border-radius: 8px;
    color: {_T["txt2"]};
    font-family: "Rajdhani", sans-serif;
    font-weight: 600;
}}
.stTabs [aria-selected="true"] {{
    background: {_T["tab_sel"]} !important;
    border-color: {_T["accent"]} !important;
    color: {_T["accent"]} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {_T["sidebar"]} !important;
    border-right: 1px solid rgba(0,212,255,0.18);
}}
.sidebar-logo {{
    font-family: "Orbitron", sans-serif;
    font-size: 1.05rem;
    color: {_T["accent"]};
    text-align: center;
    padding: 10px;
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 8px;
    margin-bottom: 14px;
}}

/* ── Misc ── */
.stAppDeployButton {{ display: none !important; }}
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
.online-dot {{
    display: inline-block; width: 8px; height: 8px;
    background: #00ff88; border-radius: 50%; margin-right: 6px;
    animation: pulse 2s infinite;
}}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}

/* ── Weather card ── */
.weather-card {{
    background: {_T["weather_bg"]};
    border: 1px solid rgba(0,150,255,0.4);
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    color: {_T["weather_txt"]};
}}

/* ═══════════════════════════════════════
   YOUTUBE MUSIC UI STYLES
   ═══════════════════════════════════════ */
.ytm-page {{
    background: {_T["ytm_bg"]};
    min-height: 100vh;
    font-family: "Roboto", sans-serif;
    color: {_T["ytm_txt"]};
    padding: 0;
}}
.ytm-header {{
    background: {_T["ytm_bar"]};
    padding: 12px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    position: sticky;
    top: 0;
    z-index: 100;
}}
.ytm-logo {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 700;
    font-size: 1.1rem;
    color: {_T["ytm_txt"]};
    text-decoration: none;
}}
.ytm-logo-icon {{
    width: 36px; height: 36px;
    background: {_T["ytm_red"]};
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.2rem;
}}
.ytm-chip-row {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}}
.ytm-chip {{
    background: {_T["ytm_card2"]};
    color: {_T["ytm_txt"]};
    border: none;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 0.85rem;
    cursor: pointer;
    font-family: "Roboto", sans-serif;
    transition: background 0.2s;
}}
.ytm-chip:hover {{ background: #333; }}
.ytm-chip.active {{ background: {_T["ytm_txt"]}; color: {_T["ytm_bg"]}; }}

.ytm-card {{
    background: {_T["ytm_card"]};
    border-radius: 8px;
    overflow: hidden;
    transition: background 0.2s;
    cursor: pointer;
}}
.ytm-card:hover {{ background: {_T["ytm_card2"]}; }}
.ytm-thumb {{
    width: 100%;
    aspect-ratio: 16/9;
    object-fit: cover;
    display: block;
}}
.ytm-card-info {{
    padding: 8px 10px 12px;
}}
.ytm-card-title {{
    color: {_T["ytm_txt"]};
    font-size: 0.85rem;
    font-weight: 500;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.3;
    margin-bottom: 4px;
}}
.ytm-card-sub {{
    color: {_T["ytm_txt2"]};
    font-size: 0.75rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.ytm-section-title {{
    font-size: 1.1rem;
    font-weight: 700;
    color: {_T["ytm_txt"]};
    margin: 20px 0 12px;
    font-family: "Roboto", sans-serif;
}}
.ytm-now-playing {{
    background: {_T["ytm_bar"]};
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 10px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    border-radius: 12px;
    margin-bottom: 16px;
}}
.ytm-np-thumb {{
    width: 52px; height: 52px;
    border-radius: 6px;
    object-fit: cover;
    flex-shrink: 0;
}}
.ytm-np-info {{ flex: 1; min-width: 0; }}
.ytm-np-title {{
    color: {_T["ytm_txt"]};
    font-weight: 600;
    font-size: 0.9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}
.ytm-np-artist {{
    color: {_T["ytm_txt2"]};
    font-size: 0.78rem;
}}
.ytm-np-badge {{
    background: {_T["ytm_red"]};
    color: white;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.5px;
    flex-shrink: 0;
}}
.ytm-play-btn {{
    background: {_T["ytm_red"]} !important;
    color: white !important;
    border: none !important;
    border-radius: 20px !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
}}
.ytm-play-btn:hover {{
    background: #cc0000 !important;
    box-shadow: 0 4px 16px rgba(255,0,0,0.4) !important;
    transform: translateY(-1px) !important;
}}
.ytm-queue-btn {{
    background: transparent !important;
    color: {_T["ytm_txt2"]} !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 20px !important;
}}
.ytm-search-bar input {{
    background: {_T["ytm_card"]} !important;
    color: {_T["ytm_txt"]} !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 24px !important;
    padding: 10px 18px !important;
    font-family: "Roboto", sans-serif !important;
}}
.ytm-pill {{
    display: inline-block;
    background: {_T["ytm_card2"]};
    color: {_T["ytm_txt"]};
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    margin: 3px;
    cursor: pointer;
    border: 1px solid rgba(255,255,255,0.1);
}}
.ytm-playlist-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 10px;
    border-radius: 8px;
    background: {_T["ytm_card"]};
    margin-bottom: 6px;
    cursor: pointer;
    transition: background 0.2s;
}}
.ytm-playlist-row:hover {{ background: {_T["ytm_card2"]}; }}
.ytm-playlist-thumb {{
    width: 48px; height: 48px;
    border-radius: 4px;
    object-fit: cover;
    flex-shrink: 0;
    background: #333;
}}
.ytm-track-row {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 8px;
    border-radius: 6px;
    transition: background 0.15s;
    cursor: pointer;
}}
.ytm-track-row:hover {{ background: {_T["ytm_card2"]}; }}

/* ── Messaging UI ── */
.msg-bubble-me {{
    background: linear-gradient(135deg, #1a1a3e, #2a1a5e);
    border: 1px solid rgba(123,47,255,0.35);
    border-radius: 16px 16px 4px 16px;
    padding: 10px 14px;
    max-width: 72%;
    margin-left: auto;
    margin-bottom: 6px;
    color: white;
    font-size: 0.92rem;
}}
.msg-bubble-them {{
    background: {"rgba(30,30,50,0.9)" if _DARK else "rgba(230,230,240,0.9)"};
    border: 1px solid {"rgba(0,212,255,0.2)" if _DARK else "rgba(0,0,0,0.1)"};
    border-radius: 16px 16px 16px 4px;
    padding: 10px 14px;
    max-width: 72%;
    margin-right: auto;
    margin-bottom: 6px;
    color: {_T["txt"]};
    font-size: 0.92rem;
}}
.msg-ts {{
    font-size: 0.68rem;
    color: {_T["txt3"]};
    margin-top: 3px;
}}
.conv-item {{
    background: {_T["card"]};
    border: 1px solid {_T["card_b"]};
    border-radius: 10px;
    padding: 10px 12px;
    margin-bottom: 6px;
    cursor: pointer;
    transition: background 0.2s;
}}
.conv-item:hover {{ background: rgba(0,212,255,0.08); }}
.conv-item.active {{ border-color: {_T["accent"]}; background: rgba(0,212,255,0.1); }}
.req-card {{
    background: {"rgba(123,47,255,0.08)" if _DARK else "rgba(123,47,255,0.06)"};
    border: 1px solid rgba(123,47,255,0.3);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
}}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 2. SUPABASE CONNECTION
# ─────────────────────────────────────────
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Could not connect to database. Please check your Supabase secrets (URL and anon key).")
    st.code(str(e))
    st.stop()


# ─────────────────────────────────────────
# 3. COOKIE MANAGER (persistent login)
# ─────────────────────────────────────────
_cookie_manager = None
if _COOKIES_OK:
    try:
        _cookie_manager = CookieManager(key="lakshmeeyam_cookies")
    except Exception:
        _cookie_manager = None

def _get_cookie(name: str):
    if _cookie_manager:
        try:
            return _cookie_manager.get(name)
        except Exception:
            return None
    return None

def _set_cookie(name: str, value: str, days: int = 30):
    if _cookie_manager:
        try:
            _cookie_manager.set(
                name, value,
                expires_at=datetime.now() + timedelta(days=days),
                key=f"set_{name}_{value[:8]}"
            )
        except Exception:
            pass

def _delete_cookie(name: str):
    if _cookie_manager:
        try:
            _cookie_manager.delete(name, key=f"del_{name}")
        except Exception:
            pass


# ─────────────────────────────────────────
# 4. DB HELPER FUNCTIONS
# ─────────────────────────────────────────
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username: str):
    try:
        res = supabase.table("users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"DB read error: {e}")
        return None

def save_user(username: str, data: dict):
    try:
        supabase.table("users").upsert({
            "username": username,
            "password": data["password"],
            "token": data.get("token", ""),
            "friends": data.get("friends", []),
            "requests": data.get("requests", [])
        }).execute()
        return True
    except Exception as e:
        st.error(f"DB save error: {e}")
        return False

def get_ai_chats(username: str) -> dict:
    try:
        res = supabase.table("ai_chats").select("*").eq("username", username).execute()
        return {row["chat_title"]: row["messages"] for row in res.data} if res.data else {}
    except:
        return {}

def save_ai_chat(username: str, title: str, messages: list):
    try:
        supabase.table("ai_chats").upsert(
            {"username": username, "chat_title": title, "messages": messages},
            on_conflict="username,chat_title"
        ).execute()
    except Exception as e:
        st.error(f"Chat save error: {e}")

def delete_ai_chat(username: str, title: str):
    try:
        supabase.table("ai_chats").delete().eq("username", username).eq("chat_title", title).execute()
    except:
        pass

def get_messages(chat_id: str) -> list:
    try:
        res = supabase.table("user_messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
        return res.data or []
    except:
        return []

def send_message(chat_id: str, sender: str, text: str):
    try:
        supabase.table("user_messages").insert({
            "chat_id": chat_id, "sender": sender, "text": text
        }).execute()
    except Exception as e:
        st.error(f"Message error: {e}")

# ── Music DB helpers ──────────────────────────────────────────────────────────
def get_liked_songs(username: str) -> list:
    try:
        res = supabase.table("liked_songs").select("*").eq("username", username).order("created_at", desc=True).execute()
        return res.data or []
    except:
        return []

def like_song(username: str, video_id: str, title: str, artist: str, thumbnail: str):
    try:
        supabase.table("liked_songs").upsert(
            {"username": username, "video_id": video_id, "title": title, "artist": artist, "thumbnail": thumbnail},
            on_conflict="username,video_id"
        ).execute()
    except:
        pass

def unlike_song(username: str, video_id: str):
    try:
        supabase.table("liked_songs").delete().eq("username", username).eq("video_id", video_id).execute()
    except:
        pass

def get_playlists(username: str) -> list:
    try:
        res = supabase.table("playlists").select("*").eq("username", username).execute()
        return res.data or []
    except:
        return []

def save_playlist(username: str, name: str, songs: list):
    try:
        supabase.table("playlists").upsert(
            {"username": username, "name": name, "songs": songs},
            on_conflict="username,name"
        ).execute()
    except:
        pass

def delete_playlist(username: str, name: str):
    try:
        supabase.table("playlists").delete().eq("username", username).eq("name", name).execute()
    except:
        pass

def get_jam(username: str) -> dict:
    """Get active jam sent TO this user."""
    try:
        res = supabase.table("jams").select("*").eq("guest", username).eq("active", True).order("created_at", desc=True).limit(1).execute()
        return res.data[0] if res.data else {}
    except:
        return {}

def send_jam(host: str, guest: str, video_id: str, title: str, thumbnail: str):
    try:
        # Deactivate old jams from this host to this guest
        supabase.table("jams").update({"active": False}).eq("host", host).eq("guest", guest).execute()
        supabase.table("jams").insert({
            "host": host, "guest": guest,
            "video_id": video_id, "title": title,
            "thumbnail": thumbnail, "active": True
        }).execute()
    except:
        pass

def youtube_search(query: str, max_results: int = 12) -> list:
    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet", "q": query + " music",
                "type": "video", "videoCategoryId": "10",
                "maxResults": max_results, "key": api_key,
                "safeSearch": "moderate"
            },
            timeout=10
        ).json()
        return resp.get("items", [])
    except:
        return []

def youtube_trending(max_results: int = 12, access_token: str = "") -> list:
    try:
        params = {
            "part": "snippet", "chart": "mostPopular",
            "videoCategoryId": "10", "maxResults": max_results,
            "regionCode": "IN"
        }
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        else:
            params["key"] = st.secrets.get("YOUTUBE_API_KEY", "")
            if not params["key"]:
                return []
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params=params, headers=headers, timeout=10
        ).json()
        items = []
        for item in resp.get("items", []):
            items.append({
                "id": {"videoId": item["id"]},
                "snippet": item["snippet"]
            })
        return items
    except:
        return []

# ── Google OAuth helpers ───────────────────────────────────────────────────────
import urllib.parse

GOOGLE_AUTH_URL  = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_REVOKE_URL = "https://oauth2.googleapis.com/revoke"
YT_API_BASE      = "https://www.googleapis.com/youtube/v3"
REDIRECT_URI     = "https://lakshmeeyamai.streamlit.app"
SCOPES = " ".join([
    "https://www.googleapis.com/auth/youtube.readonly",
    "openid", "email", "profile"
])

def get_google_auth_url() -> str:
    client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": st.session_state.user
    }
    return GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)

def exchange_code_for_tokens(code: str) -> dict:
    client_id     = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }, timeout=10)
    return resp.json()

def refresh_google_token(refresh_token: str) -> str:
    client_id     = st.secrets.get("GOOGLE_CLIENT_ID", "")
    client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
    resp = requests.post(GOOGLE_TOKEN_URL, data={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token"
    }, timeout=10)
    data = resp.json()
    return data.get("access_token", "")

def save_google_tokens(username: str, access_token: str, refresh_token: str, email: str = ""):
    try:
        supabase.table("google_tokens").upsert({
            "username": username,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "email": email
        }, on_conflict="username").execute()
    except:
        pass

def get_google_tokens(username: str) -> dict:
    try:
        res = supabase.table("google_tokens").select("*").eq("username", username).execute()
        return res.data[0] if res.data else {}
    except:
        return {}

def delete_google_tokens(username: str):
    try:
        supabase.table("google_tokens").delete().eq("username", username).execute()
    except:
        pass

def yt_get(endpoint: str, params: dict, access_token: str) -> dict:
    """Make an authenticated YouTube Data API call."""
    try:
        resp = requests.get(
            YT_API_BASE + endpoint,
            params=params,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        return resp.json()
    except:
        return {}

def get_yt_liked_songs(access_token: str, max_results: int = 50) -> list:
    data = yt_get("/videos", {
        "part": "snippet,contentDetails",
        "myRating": "like",
        "maxResults": max_results,
        "videoCategoryId": "10"
    }, access_token)
    items = []
    for item in data.get("items", []):
        items.append({
            "id": {"videoId": item["id"]},
            "snippet": item["snippet"]
        })
    return items

def get_yt_playlists(access_token: str) -> list:
    data = yt_get("/playlists", {
        "part": "snippet,contentDetails",
        "mine": "true",
        "maxResults": 50
    }, access_token)
    return data.get("items", [])

def get_yt_playlist_items(access_token: str, playlist_id: str, max_results: int = 50) -> list:
    data = yt_get("/playlistItems", {
        "part": "snippet",
        "playlistId": playlist_id,
        "maxResults": max_results
    }, access_token)
    items = []
    for item in data.get("items", []):
        vid_id = item["snippet"].get("resourceId", {}).get("videoId", "")
        if vid_id:
            items.append({
                "id": {"videoId": vid_id},
                "snippet": item["snippet"]
            })
    return items

def get_yt_subscriptions(access_token: str, max_results: int = 20) -> list:
    data = yt_get("/subscriptions", {
        "part": "snippet",
        "mine": "true",
        "maxResults": max_results,
        "order": "relevance"
    }, access_token)
    return data.get("items", [])

def get_yt_recommendations(access_token: str, max_results: int = 12) -> list:
    """Get personalized feed — activities from subscribed channels."""
    data = yt_get("/activities", {
        "part": "snippet,contentDetails",
        "home": "true",
        "maxResults": max_results
    }, access_token)
    items = []
    for item in data.get("items", []):
        cd = item.get("contentDetails", {})
        if "upload" in cd:
            vid_id = cd["upload"].get("videoId", "")
            if vid_id:
                items.append({
                    "id": {"videoId": vid_id},
                    "snippet": item["snippet"]
                })
    return items

def yt_search_authed(query: str, access_token: str, max_results: int = 12) -> list:
    data = yt_get("/search", {
        "part": "snippet",
        "q": query,
        "type": "video",
        "videoCategoryId": "10",
        "maxResults": max_results
    }, access_token)
    return data.get("items", [])

def get_yt_user_info(access_token: str) -> dict:
    try:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        return resp.json()
    except:
        return {}
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────
# 5. SESSION STATE DEFAULTS
# ─────────────────────────────────────────
defaults = {
    "logged_in": False,
    "user": "",
    "current_page": "home",
    "active_chat": "New Chat",
    "processing": False,
    "msg_target": None,
    "theme": "cyan",
    "gps_lat": None,
    "gps_lon": None,
    "gps_city": None,
    "gps_country": None,
    "weather_fetched": False,
    # Music player state
    "music_tab": "home",
    "now_playing_id": None,
    "now_playing_title": "",
    "now_playing_artist": "",
    "now_playing_thumb": "",
    "queue": [],
    "music_search_results": [],
    "music_search_query": "",
    "active_playlist_name": None,
    "playlist_add_target": None,
    # Google / YouTube OAuth
    "yt_access_token": "",
    "yt_refresh_token": "",
    "yt_email": "",
    "yt_connected": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────
# 6. PERSISTENT LOGIN CHECK
#    Priority: session → cookie → query param
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    # 6a. Try cookie first (survives tab close)
    cookie_token = _get_cookie("auth_token")
    if cookie_token:
        try:
            res = supabase.table("users").select("*").eq("token", cookie_token).execute()
            if res.data:
                st.session_state.logged_in = True
                st.session_state.user = res.data[0]["username"]
        except:
            pass

    # 6b. Fallback: URL query param (backward compat)
    if not st.session_state.logged_in:
        url_token = st.query_params.get("token")
        if url_token:
            try:
                res = supabase.table("users").select("*").eq("token", url_token).execute()
                if res.data:
                    st.session_state.logged_in = True
                    st.session_state.user = res.data[0]["username"]
                    # Upgrade: also write to cookie so future visits work without URL param
                    _set_cookie("auth_token", url_token)
            except:
                pass


# ─────────────────────────────────────────
# 6c. GOOGLE OAUTH CALLBACK HANDLER
#     Runs on every page load — picks up ?code= from Google redirect
# ─────────────────────────────────────────
_oauth_code = st.query_params.get("code", "")
_oauth_state = st.query_params.get("state", "")
if _oauth_code and st.session_state.logged_in:
    # Exchange the auth code for tokens (only once)
    if not st.session_state.yt_connected:
        with st.spinner("🔗 Connecting your Google account…"):
            token_data = exchange_code_for_tokens(_oauth_code)
            if "access_token" in token_data:
                access_token  = token_data["access_token"]
                refresh_token = token_data.get("refresh_token", "")
                user_info = get_yt_user_info(access_token)
                email = user_info.get("email", "")
                save_google_tokens(st.session_state.user, access_token, refresh_token, email)
                st.session_state.yt_access_token  = access_token
                st.session_state.yt_refresh_token = refresh_token
                st.session_state.yt_email         = email
                st.session_state.yt_connected     = True
                # Clean URL — remove code & state params
                st.query_params.clear()
                if st.session_state.get("auth_token_val"):
                    st.query_params["token"] = st.session_state.auth_token_val
                st.session_state.current_page = "Music"
                st.rerun()

# If already logged in, try to restore YT tokens from Supabase
if st.session_state.logged_in and not st.session_state.yt_connected:
    _saved = get_google_tokens(st.session_state.user)
    if _saved and _saved.get("access_token"):
        # Try refreshing the token in case it expired
        new_at = refresh_google_token(_saved.get("refresh_token", ""))
        if new_at:
            _saved["access_token"] = new_at
            save_google_tokens(
                st.session_state.user,
                new_at, _saved.get("refresh_token",""), _saved.get("email","")
            )
        st.session_state.yt_access_token  = _saved.get("access_token", "")
        st.session_state.yt_refresh_token = _saved.get("refresh_token", "")
        st.session_state.yt_email         = _saved.get("email", "")
        st.session_state.yt_connected     = bool(st.session_state.yt_access_token)

# ─────────────────────────────────────────
# 7. LOGIN / SIGNUP PAGE
# ─────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown("<div class='hero-title'>🚀 LAKSHMEEYAM AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='hero-sub'>Next-Gen AI Platform by Sreenand</div>", unsafe_allow_html=True)

    col_l, spacer, col_r = st.columns([1.4, 0.1, 1])

    with col_l:
        st.markdown("""
        <div class='main-box'>
            <h2 style='color:#00d4ff; font-family:Orbitron,sans-serif;'>👨‍💻 About</h2>
            <p style='color:rgba(255,255,255,0.8);'>
                <b>Lakshmeeyam AI</b> is a full-stack AI ecosystem built by 
                <span style='color:#00d4ff;'><b>Sreenand</b></span>, a 14-year-old developer from India.
            </p>
            <p style='color:rgba(255,255,255,0.6); font-size:0.9rem;'>
                A hobby project combining AI, social networking, and real-time data.
            </p>
            <hr style='border-color: rgba(0,212,255,0.2); margin: 15px 0;'>
            <div style='display:grid; grid-template-columns:1fr 1fr; gap:12px;'>
                <div style='background:rgba(0,212,255,0.08); padding:12px; border-radius:8px; border:1px solid rgba(0,212,255,0.2);'>
                    <div style='color:#00d4ff; font-size:1.4rem;'>🤖</div>
                    <div style='color:white; font-weight:600;'>AI Chat</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Llama 3.1 via Groq</div>
                </div>
                <div style='background:rgba(123,47,255,0.08); padding:12px; border-radius:8px; border:1px solid rgba(123,47,255,0.2);'>
                    <div style='color:#7b2fff; font-size:1.4rem;'>💬</div>
                    <div style='color:white; font-weight:600;'>Messaging</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Real-time DMs</div>
                </div>
                <div style='background:rgba(0,255,136,0.08); padding:12px; border-radius:8px; border:1px solid rgba(0,255,136,0.2);'>
                    <div style='color:#00ff88; font-size:1.4rem;'>🌤️</div>
                    <div style='color:white; font-weight:600;'>Weather</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>GPS + live forecasts</div>
                </div>
                <div style='background:rgba(255,165,0,0.08); padding:12px; border-radius:8px; border:1px solid rgba(255,165,0,0.2);'>
                    <div style='color:#ffa500; font-size:1.4rem;'>🔐</div>
                    <div style='color:white; font-weight:600;'>Secure</div>
                    <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>Hashed passwords</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_r:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#00d4ff; font-family:Orbitron,sans-serif;'>🔐 Access Portal</h3>", unsafe_allow_html=True)

        t1, t2 = st.tabs(["🔑 Login", "✨ Sign Up"])

        with t1:
            u_in = st.text_input("Username", key="login_user", placeholder="Enter username")
            p_in = st.text_input("Password", type="password", key="login_pass", placeholder="Enter password")
            remember = st.checkbox("Stay logged in (persists after closing tab)", value=True)

            if st.button("LOGIN →", use_container_width=True, key="login_btn"):
                if u_in and p_in:
                    user_data = get_user(u_in)
                    if user_data:
                        stored = user_data["password"]
                        if stored == p_in or stored == hash_password(p_in):
                            new_token = secrets.token_hex(16) if remember else ""
                            user_data["token"] = new_token
                            save_user(u_in, user_data)
                            st.session_state.logged_in = True
                            st.session_state.user = u_in
                            if remember:
                                # ✅ Save to COOKIE (survives tab close)
                                _set_cookie("auth_token", new_token, days=30)
                                # Also set query param for backward compat
                                st.query_params["token"] = new_token
                            st.success("✅ Welcome back!")
                            st.rerun()
                        else:
                            st.error("❌ Wrong password")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Please fill in both fields")

        with t2:
            nu = st.text_input("Choose Username", key="reg_user", placeholder="Pick a username")
            np = st.text_input("Choose Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            np2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Repeat password")

            if st.button("CREATE ACCOUNT →", use_container_width=True, key="reg_btn"):
                if nu and np and np2:
                    if np != np2:
                        st.error("❌ Passwords don't match")
                    elif len(np) < 6:
                        st.error("❌ Password too short (min 6 chars)")
                    elif get_user(nu):
                        st.error("❌ Username already taken")
                    else:
                        new_user = {
                            "password": hash_password(np),
                            "friends": [], "requests": [], "token": ""
                        }
                        if save_user(nu, new_user):
                            st.success("🎉 Account created! Please login.")
                        else:
                            st.error("Failed to create account. Check Supabase connection.")
                else:
                    st.warning("Please fill all fields")

        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────
# 8. SIDEBAR (logged in)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div class='sidebar-logo'>⚡ LAKSHMEEYAM AI</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:rgba(255,255,255,0.5); text-align:center; font-size:0.85rem;'><span class='online-dot'></span>{st.session_state.user}</p>", unsafe_allow_html=True)

    pages = [
        ("🏠", "Home", "home"),
        ("🤖", "AI Chat", "AI Chat"),
        ("💬", "Messages", "Messages"),
        ("🎵", "Music", "Music"),
        ("🌤️", "Weather", "Weather"),
    ]

    for icon, label, page_key in pages:
        if st.button(f"{icon}  {label}", use_container_width=True, key=f"nav_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()

    st.markdown("---")

    # AI Chat history in sidebar
    if st.session_state.current_page == "AI Chat":
        if st.button("➕  New Chat", use_container_width=True):
            st.session_state.active_chat = "New Chat"
            st.rerun()

        chats = get_ai_chats(st.session_state.user)
        if chats:
            st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;'>Chat History</p>", unsafe_allow_html=True)
            for title in reversed(list(chats.keys())):
                col_a, col_b = st.columns([4, 1])
                with col_a:
                    if st.button(f"💬 {title[:18]}{'…' if len(title)>18 else ''}", use_container_width=True, key=f"ch_{title}"):
                        st.session_state.active_chat = title
                        st.rerun()
                with col_b:
                    if st.button("🗑", key=f"del_{title}"):
                        delete_ai_chat(st.session_state.user, title)
                        if st.session_state.active_chat == title:
                            st.session_state.active_chat = "New Chat"
                        st.rerun()

    st.markdown("---")
    # ── Theme toggle ─────────────────────────────────────────────────────────
    current_theme = st.session_state.get("theme", "dark")
    theme_label = "☀️  Light Mode" if current_theme == "dark" else "🌙  Dark Mode"
    if st.button(theme_label, use_container_width=True, key="theme_toggle"):
        st.session_state.theme = "light" if current_theme == "dark" else "dark"
        st.rerun()
    st.markdown("---")
    if st.button("🔐  Logout", use_container_width=True):
        user_data = get_user(st.session_state.user)
        if user_data:
            user_data["token"] = ""
            save_user(st.session_state.user, user_data)
        # ✅ Clear cookie on logout
        _delete_cookie("auth_token")
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.query_params.clear()
        st.rerun()


# ─────────────────────────────────────────
# 9. HOME PAGE
# ─────────────────────────────────────────
if st.session_state.current_page == "home":
    st.markdown("<div class='hero-title' style='font-size:2rem;'>🏠 Dashboard</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center; color:rgba(255,255,255,0.5);'>Welcome back, <span style='color:#00d4ff;'>{st.session_state.user}</span></p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        (c1, "🤖", "AI Lab", "Llama 3.1 • Multi-session chat • Auto-titled history", "#00d4ff", "Open AI", "AI Chat"),
        (c2, "💬", "Messaging", "DMs • Friends • Music Jam sharing", "#7b2fff", "Open Messages", "Messages"),
        (c3, "🎵", "Music", "YouTube Music • Search • Playlists • Jam", "#ff4444", "Open Music", "Music"),
        (c4, "🌤️", "SkyView", "GPS live weather • Temperature • 7-Day Forecast", "#00ff88", "Open Weather", "Weather"),
    ]

    for col, icon, title, desc, color, btn, page in cards:
        with col:
            st.markdown(f"""
            <div class='main-box' style='border-color:{color}40; text-align:center; min-height:160px;'>
                <div style='font-size:2.5rem;'>{icon}</div>
                <h3 style='color:{color}; font-family:Orbitron,sans-serif; margin:8px 0;'>{title}</h3>
                <p style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>{desc}</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button(btn, use_container_width=True, key=f"home_{page}"):
                st.session_state.current_page = page
                st.rerun()


# ─────────────────────────────────────────
# 10. AI CHAT PAGE
# ─────────────────────────────────────────
elif st.session_state.current_page == "AI Chat":
    try:
        groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    except Exception:
        st.error("❌ Groq API key missing. Add GROQ_API_KEY to your Streamlit secrets.")
        st.stop()

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>🤖 AI Chat</div>", unsafe_allow_html=True)

    col_m1, col_m2 = st.columns([3, 1])
    with col_m2:
        model_choice = st.selectbox("Model", [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ], label_visibility="collapsed")
    with col_m1:
        st.markdown(f"<p style='color:rgba(255,255,255,0.4); padding-top:8px;'>Active model: <span style='color:#00d4ff;'>{model_choice}</span></p>", unsafe_allow_html=True)

    user_history = get_ai_chats(st.session_state.user)
    current_msgs = user_history.get(st.session_state.active_chat, [])

    chat_container = st.container()
    with chat_container:
        if not current_msgs:
            st.markdown("""
            <div style='text-align:center; padding:60px 20px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>🤖</div>
                <p>Start a conversation with Lakshmeeyam AI</p>
                <p style='font-size:0.8rem;'>Powered by Groq • Ultra-fast inference</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for m in current_msgs:
                with st.chat_message(m["role"]):
                    st.write(m["content"])

    prompt = st.chat_input("Ask me anything...")
    if prompt:
        current_msgs.append({"role": "user", "content": prompt})
        st.session_state.processing = True
        save_ai_chat(st.session_state.user, st.session_state.active_chat, current_msgs)
        st.rerun()

    if st.session_state.processing and current_msgs:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # ✅ UPDATED SYSTEM PROMPT — Sreenand identity baked in
                system_prompt = {
                    "role": "system",
                    "content": (
                        "You are Lakshmeeyam AI, a helpful and intelligent assistant. "
                        "You were created by Sreenand. "
                        "If anyone asks who created you, who made you, or who your creator is, "
                        "you must answer: 'I was created by Sreenand.' "
                        "If anyone asks who Sreenand is, you must answer: "
                        "'Sreenand is a 14-year-old boy and a brilliant young developer from India "
                        "who built Lakshmeeyam AI as a passion project.' "
                        "Be concise, friendly, and insightful. "
                        "Format responses with markdown when helpful."
                    )
                }
                try:
                    response = groq_client.chat.completions.create(
                        model=model_choice,
                        messages=[system_prompt] + current_msgs,
                        temperature=0.7,
                        max_tokens=1024
                    )
                    answer = response.choices[0].message.content
                except Exception as e:
                    answer = f"⚠️ Error: {e}"

                current_msgs.append({"role": "assistant", "content": answer})

                active_title = st.session_state.active_chat
                if active_title == "New Chat" and len(current_msgs) >= 2:
                    try:
                        title_res = groq_client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": "Generate a very short 2-3 word title for this conversation. Reply with ONLY the title, nothing else."},
                                {"role": "user", "content": current_msgs[0]["content"]}
                            ],
                            max_tokens=20
                        )
                        new_title = title_res.choices[0].message.content.strip().strip('"').strip("'")
                        if new_title:
                            delete_ai_chat(st.session_state.user, "New Chat")
                            active_title = new_title
                            st.session_state.active_chat = new_title
                    except:
                        pass

                save_ai_chat(st.session_state.user, active_title, current_msgs)
                st.session_state.processing = False
                st.rerun()


# ─────────────────────────────────────────
# 11. MESSAGES PAGE (upgraded)
# ─────────────────────────────────────────
elif st.session_state.current_page == "Messages":
    import streamlit.components.v1 as _comp

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>💬 Messaging</div>", unsafe_allow_html=True)

    u_data = get_user(st.session_state.user)
    if not u_data:
        st.error("Could not load user data.")
        st.stop()

    friends_list = u_data.get("friends") or []

    # ── Check for incoming jams ───────────────────────────────────────────────
    incoming_jam = get_jam(st.session_state.user)
    if incoming_jam:
        host = incoming_jam.get("host", "")
        jam_vid = incoming_jam.get("video_id", "")
        jam_title = incoming_jam.get("title", "Unknown")
        jam_thumb = incoming_jam.get("thumbnail", "")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,rgba(255,68,68,0.15),rgba(123,47,255,0.15));
        border:1px solid rgba(255,68,68,0.5); border-radius:14px; padding:16px;
        display:flex; align-items:center; gap:14px; margin-bottom:18px;'>
            <img src='{jam_thumb}' style='width:60px; height:45px; border-radius:6px; object-fit:cover;'/>
            <div>
                <div style='color:#ff4444; font-weight:700; font-size:0.9rem;'>🎵 {host} is jamming with you!</div>
                <div style='color:white; font-size:0.85rem;'>{jam_title}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🎵 Join Jam → Open Music", key="join_jam_btn"):
            st.session_state.now_playing_id = jam_vid
            st.session_state.now_playing_title = jam_title
            st.session_state.now_playing_thumb = jam_thumb
            st.session_state.current_page = "Music"
            st.session_state.music_tab = "jam"
            st.rerun()

    t_chat, t_friends, t_requests = st.tabs(["💬 Chats", "👥 Friends", "📨 Requests"])

    # ── CHATS TAB ─────────────────────────────────────────────────────────────
    with t_chat:
        if not friends_list:
            st.markdown("""
            <div style='text-align:center; padding:60px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>💬</div>
                <p>Add friends first to start chatting</p>
            </div>""", unsafe_allow_html=True)
        else:
            left, right = st.columns([1, 3])
            with left:
                st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;'>Conversations</p>", unsafe_allow_html=True)
                for f in friends_list:
                    active = st.session_state.get("msg_target") == f
                    cid = "_".join(sorted([st.session_state.user, f]))
                    msgs = get_messages(cid)
                    last_msg = msgs[-1]["text"][:20] + "…" if msgs else "Say hi! 👋"
                    badge_color = "#00d4ff" if active else "rgba(255,255,255,0.15)"
                    border_color = "#00d4ff" if active else "rgba(255,255,255,0.1)"
                    st.markdown(f"""
                    <div style='background:{badge_color}20; border:1px solid {border_color};
                    border-radius:10px; padding:10px 12px; margin-bottom:6px; cursor:pointer;'>
                        <div style='color:white; font-weight:600;'>{"🟢" if active else "👤"} {f}</div>
                        <div style='color:rgba(255,255,255,0.4); font-size:0.75rem; margin-top:2px;'>{last_msg}</div>
                    </div>""", unsafe_allow_html=True)
                    if st.button(f"Open chat", key=f"dm_{f}", use_container_width=True):
                        st.session_state.msg_target = f
                        st.rerun()

            with right:
                dest = st.session_state.get("msg_target")
                if dest:
                    cid = "_".join(sorted([st.session_state.user, dest]))
                    # Header with jam button
                    hcol1, hcol2 = st.columns([3, 1])
                    with hcol1:
                        st.markdown(f"<h4 style='color:#00d4ff; margin:0;'>💬 {dest}</h4>", unsafe_allow_html=True)
                    with hcol2:
                        if st.session_state.now_playing_id:
                            if st.button("🎵 Share Jam", use_container_width=True, key="share_jam_msg"):
                                send_jam(
                                    st.session_state.user, dest,
                                    st.session_state.now_playing_id,
                                    st.session_state.now_playing_title,
                                    st.session_state.now_playing_thumb
                                )
                                st.success(f"🎵 Jam shared with {dest}!")

                    # Messages
                    messages = get_messages(cid)
                    msg_box = st.container()
                    with msg_box:
                        if not messages:
                            st.markdown(f"<div style='text-align:center; padding:40px; color:rgba(255,255,255,0.3);'>"
                                        f"<div style='font-size:2rem;'>👋</div>"
                                        f"<p>Start your conversation with {dest}</p></div>",
                                        unsafe_allow_html=True)
                        else:
                            for m in messages:
                                is_me = m["sender"] == st.session_state.user
                                ts = m.get("created_at", "")[:16].replace("T", " ") if m.get("created_at") else ""
                                align = "flex-end" if is_me else "flex-start"
                                bubble_bg = "linear-gradient(135deg,#1a1a3e,#2a1a5e)" if is_me else "linear-gradient(135deg,#0a2a3a,#0a1a2e)"
                                border = "rgba(123,47,255,0.4)" if is_me else "rgba(0,212,255,0.3)"
                                radius = "12px 12px 2px 12px" if is_me else "12px 12px 12px 2px"
                                st.markdown(f"""
                                <div style='display:flex; justify-content:{align}; margin:6px 0;'>
                                    <div style='background:{bubble_bg}; border:1px solid {border};
                                    border-radius:{radius}; padding:10px 14px; max-width:70%;'>
                                        <div style='color:white; font-size:0.95rem;'>{m["text"]}</div>
                                        <div style='color:rgba(255,255,255,0.3); font-size:0.7rem; margin-top:4px; text-align:{"right" if is_me else "left"};'>{ts}</div>
                                    </div>
                                </div>""", unsafe_allow_html=True)

                    txt = st.chat_input(f"Message {dest}…")
                    if txt:
                        send_message(cid, st.session_state.user, txt)
                        st.rerun()
                else:
                    st.markdown("""
                    <div style='text-align:center; padding:80px; color:rgba(255,255,255,0.2);'>
                        <div style='font-size:3rem;'>💬</div>
                        <p>Select a conversation on the left</p>
                    </div>""", unsafe_allow_html=True)

    # ── FRIENDS TAB ───────────────────────────────────────────────────────────
    with t_friends:
        add_col, list_col = st.columns([1, 1])
        with add_col:
            st.markdown("<h4 style='color:#00d4ff;'>➕ Add Friend</h4>", unsafe_allow_html=True)
            target = st.text_input("Username to add", placeholder="Enter exact username", key="friend_search")
            if st.button("Send Request →", use_container_width=True, key="send_req_btn"):
                if target and target != st.session_state.user:
                    target_data = get_user(target)
                    if target_data:
                        reqs = target_data.get("requests", [])
                        friends = target_data.get("friends", [])
                        if st.session_state.user in friends:
                            st.info("Already friends!")
                        elif st.session_state.user in reqs:
                            st.info("Request already sent.")
                        else:
                            reqs.append(st.session_state.user)
                            target_data["requests"] = reqs
                            save_user(target, target_data)
                            st.success(f"✅ Request sent to {target}!")
                    else:
                        st.error("❌ User not found")
                else:
                    st.warning("Enter a valid username")

        with list_col:
            st.markdown("<h4 style='color:#00ff88;'>👥 Your Friends</h4>", unsafe_allow_html=True)
            if not friends_list:
                st.markdown("<p style='color:rgba(255,255,255,0.4);'>No friends yet.</p>", unsafe_allow_html=True)
            else:
                for f in friends_list:
                    fc1, fc2 = st.columns([3, 1])
                    with fc1:
                        st.markdown(f"""
                        <div style='background:rgba(0,255,136,0.08); border:1px solid rgba(0,255,136,0.2);
                        border-radius:8px; padding:10px 12px;'>
                            <span style='color:white; font-weight:600;'>👤 {f}</span>
                        </div>""", unsafe_allow_html=True)
                    with fc2:
                        if st.button("Chat", key=f"goto_{f}", use_container_width=True):
                            st.session_state.msg_target = f
                            st.session_state.current_page = "Messages"
                            st.rerun()

    # ── REQUESTS TAB ──────────────────────────────────────────────────────────
    with t_requests:
        st.markdown("<h4 style='color:#7b2fff;'>📨 Incoming Friend Requests</h4>", unsafe_allow_html=True)
        # Re-fetch to get latest state; use copy so iteration is safe
        u_data_fresh = get_user(st.session_state.user) or u_data
        incoming_reqs = list(u_data_fresh.get("requests") or [])
        if not incoming_reqs:
            st.markdown("<p style='color:rgba(255,255,255,0.4);'>No pending requests.</p>", unsafe_allow_html=True)
        else:
            for r in incoming_reqs:
                rc1, rc2, rc3 = st.columns([3, 1, 1])
                with rc1:
                    st.markdown(f"""
                    <div style='background:rgba(123,47,255,0.1); border:1px solid rgba(123,47,255,0.3);
                    border-radius:8px; padding:10px 14px;'>
                        <b style='color:white;'>{r}</b>
                        <span style='color:rgba(255,255,255,0.5); margin-left:8px;'>wants to connect</span>
                    </div>""", unsafe_allow_html=True)
                with rc2:
                    if st.button("✅ Accept", key=f"acc_{r}", use_container_width=True):
                        ud = get_user(st.session_state.user)
                        if ud:
                            my_friends  = list(ud.get("friends")  or [])
                            my_requests = list(ud.get("requests") or [])
                            if r in my_requests:
                                my_requests.remove(r)
                            if r not in my_friends:
                                my_friends.append(r)
                            ud["friends"]  = my_friends
                            ud["requests"] = my_requests
                            save_user(st.session_state.user, ud)
                            # Add back-link to sender
                            r_data = get_user(r)
                            if r_data:
                                rf = list(r_data.get("friends") or [])
                                if st.session_state.user not in rf:
                                    rf.append(st.session_state.user)
                                r_data["friends"] = rf
                                save_user(r, r_data)
                        st.success(f"✅ You and {r} are now friends!")
                        st.rerun()
                with rc3:
                    if st.button("❌ Decline", key=f"dec_{r}", use_container_width=True):
                        ud = get_user(st.session_state.user)
                        if ud:
                            my_requests = list(ud.get("requests") or [])
                            if r in my_requests:
                                my_requests.remove(r)
                            ud["requests"] = my_requests
                            save_user(st.session_state.user, ud)
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 11b. MUSIC PAGE  — YouTube Music UI
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "Music":
    import streamlit.components.v1 as _comp

    # ── Google OAuth setup ────────────────────────────────────────────────────
    _OAUTH_OK = False
    try:
        from streamlit_oauth import OAuth2Component
        GCLIENT_ID     = st.secrets.get("GOOGLE_CLIENT_ID", "")
        GCLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
        REDIRECT_URI   = st.secrets.get("OAUTH_REDIRECT_URI", "https://lakshmeeyamai.streamlit.app")
        if GCLIENT_ID and GCLIENT_SECRET:
            _oauth2 = OAuth2Component(
                GCLIENT_ID, GCLIENT_SECRET,
                "https://accounts.google.com/o/oauth2/auth",
                "https://accounts.google.com/o/oauth2/token",
                "https://accounts.google.com/o/oauth2/token",
                "https://oauth2.googleapis.com/revoke"
            )
            _OAUTH_OK = True
    except Exception:
        pass

    HAS_YT_KEY     = bool(st.secrets.get("YOUTUBE_API_KEY", ""))
    is_yt_connected = bool(st.session_state.get("yt_token"))

    def yt_headers():
        tok = st.session_state.get("yt_token", {})
        return {"Authorization": f"Bearer {tok.get('access_token', '')}"}

    def yt_api(endpoint, params):
        try:
            r = requests.get(endpoint, params=params, headers=yt_headers(), timeout=10)
            return r.json()
        except:
            return {}

    def yt_search_auth(q, n=16):
        d = yt_api("https://www.googleapis.com/youtube/v3/search",
                   {"part":"snippet","q":q+" music","type":"video","videoCategoryId":"10","maxResults":n})
        return d.get("items",[])

    def yt_trending_auth(n=24):
        d = yt_api("https://www.googleapis.com/youtube/v3/videos",
                   {"part":"snippet","chart":"mostPopular","videoCategoryId":"10","maxResults":n,"regionCode":"IN"})
        return [{"id":{"videoId":i["id"]},"snippet":i["snippet"]} for i in d.get("items",[])]

    def yt_liked(n=50):
        d = yt_api("https://www.googleapis.com/youtube/v3/videos",
                   {"part":"snippet","myRating":"like","maxResults":n,"videoCategoryId":"10"})
        return [{"id":{"videoId":i["id"]},"snippet":i["snippet"]} for i in d.get("items",[])]

    def yt_playlists(n=50):
        d = yt_api("https://www.googleapis.com/youtube/v3/playlists",
                   {"part":"snippet,contentDetails","mine":"true","maxResults":n})
        return d.get("items",[])

    def yt_pl_items(pl_id, n=50):
        d = yt_api("https://www.googleapis.com/youtube/v3/playlistItems",
                   {"part":"snippet","playlistId":pl_id,"maxResults":n})
        return [{"id":{"videoId":i["snippet"].get("resourceId",{}).get("videoId","")},
                 "snippet":i["snippet"]} for i in d.get("items",[])]

    def yt_subs(n=50):
        d = yt_api("https://www.googleapis.com/youtube/v3/subscriptions",
                   {"part":"snippet","mine":"true","maxResults":n})
        return d.get("items",[])

    def yt_search_key(q, n=16):
        key = st.secrets.get("YOUTUBE_API_KEY","")
        if not key: return []
        try:
            d = requests.get("https://www.googleapis.com/youtube/v3/search",
                params={"part":"snippet","q":q+" music","type":"video",
                        "videoCategoryId":"10","maxResults":n,"key":key},
                timeout=10).json()
            return d.get("items",[])
        except: return []

    def yt_trending_key(n=24):
        key = st.secrets.get("YOUTUBE_API_KEY","")
        if not key: return []
        try:
            d = requests.get("https://www.googleapis.com/youtube/v3/videos",
                params={"part":"snippet","chart":"mostPopular","videoCategoryId":"10",
                        "maxResults":n,"regionCode":"IN","key":key},
                timeout=10).json()
            return [{"id":{"videoId":i["id"]},"snippet":i["snippet"]} for i in d.get("items",[])]
        except: return []

    def do_search(q, n=16):
        return yt_search_auth(q, n) if is_yt_connected else yt_search_key(q, n)

    def do_trending(n=24):
        return yt_trending_auth(n) if is_yt_connected else yt_trending_key(n)

    def _play(vid_id, title, artist, thumb):
        st.session_state.now_playing_id     = vid_id
        st.session_state.now_playing_title  = title
        st.session_state.now_playing_artist = artist
        st.session_state.now_playing_thumb  = thumb

    # ── YTM-style card grid renderer ─────────────────────────────────────────
    def render_ytm_grid(items, cols=4, prefix="g"):
        if not items:
            st.markdown(
                "<p style='color:#aaa; text-align:center; padding:40px;'>No results.</p>",
                unsafe_allow_html=True)
            return
        rows = [items[i:i+cols] for i in range(0, len(items), cols)]
        for ri, row in enumerate(rows):
            grid_cols = st.columns(cols)
            for gi, item in enumerate(row):
                vid_id = item["id"]["videoId"]
                snip   = item["snippet"]
                title  = snip.get("title","Unknown")[:52]
                artist = snip.get("channelTitle","")[:30]
                thumb  = (snip.get("thumbnails",{}).get("medium",{}) or
                          snip.get("thumbnails",{}).get("default",{})).get("url","")
                with grid_cols[gi]:
                    card_html = f"""
<div class="ytm-card">
  {"<img src='" + thumb + "' class='ytm-thumb'/>" if thumb else "<div style='aspect-ratio:16/9;background:#333;width:100%;display:block;'></div>"}
  <div class="ytm-card-info">
    <div class="ytm-card-title">{title}</div>
    <div class="ytm-card-sub">{artist}</div>
  </div>
</div>"""
                    st.markdown(card_html, unsafe_allow_html=True)
                    b1, b2 = st.columns([3,2])
                    with b1:
                        if st.button("▶ Play", key=f"{prefix}_{ri}_{gi}_p",
                                     use_container_width=True):
                            _play(vid_id, title, artist, thumb)
                            st.rerun()
                    with b2:
                        if st.button("＋Queue", key=f"{prefix}_{ri}_{gi}_q",
                                     use_container_width=True):
                            st.session_state.queue.append(
                                {"id":vid_id,"title":title,"artist":artist,"thumb":thumb})
                            st.toast(f"Queued: {title[:28]}")

    # ── YTM track-row renderer (for playlists / liked) ────────────────────────
    def render_ytm_tracklist(items, prefix="tl"):
        if not items:
            st.markdown("<p style='color:#aaa;'>No tracks.</p>", unsafe_allow_html=True)
            return
        for i, item in enumerate(items):
            vid_id = item["id"]["videoId"]
            snip   = item["snippet"]
            title  = snip.get("title","Unknown")[:55]
            artist = snip.get("channelTitle","")[:30]
            thumb  = (snip.get("thumbnails",{}).get("medium",{}) or
                      snip.get("thumbnails",{}).get("default",{})).get("url","")
            c1, c2, c3, c4 = st.columns([0.8, 5, 1.5, 1.5])
            with c1:
                if thumb:
                    st.image(thumb, width=48)
                else:
                    st.markdown("<div style='width:48px;height:48px;background:#333;border-radius:4px;'></div>",
                                unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div style='color:{_T['ytm_txt']};font-size:.88rem;font-weight:500;margin-top:4px;'>{title}</div>"
                            f"<div style='color:{_T['ytm_txt2']};font-size:.76rem;'>{artist}</div>",
                            unsafe_allow_html=True)
            with c3:
                if st.button("▶", key=f"{prefix}_{i}_p", use_container_width=True):
                    _play(vid_id, title, artist, thumb)
                    # remaining tracks → queue
                    remaining = []
                    for j, it in enumerate(items):
                        if j > i:
                            v2 = it["id"]["videoId"]
                            s2 = it["snippet"]
                            t2 = (s2.get("thumbnails",{}).get("medium",{}) or
                                  s2.get("thumbnails",{}).get("default",{})).get("url","")
                            remaining.append({"id":v2,"title":s2.get("title",""),
                                              "artist":s2.get("channelTitle",""),"thumb":t2})
                    st.session_state.queue = remaining
                    st.rerun()
            with c4:
                if st.button("＋", key=f"{prefix}_{i}_q", use_container_width=True):
                    st.session_state.queue.append(
                        {"id":vid_id,"title":title,"artist":artist,"thumb":thumb})
                    st.toast(f"Queued: {title[:25]}")
            st.markdown(f"<hr style='border:none;border-top:1px solid {_T['ytm_card2']};margin:2px 0;'>",
                        unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # YTM HEADER (logo + search + Google connect)
    # ════════════════════════════════════════════════════════════════════
    st.markdown(f"""
<div class="ytm-header">
  <div class="ytm-logo">
    <div class="ytm-logo-icon">🎵</div>
    <span style="font-family:Roboto,sans-serif;font-weight:700;color:{_T['ytm_txt']};">
      Lakshmeeyam<span style="color:{_T['ytm_red']};"> Music</span>
    </span>
  </div>
</div>""", unsafe_allow_html=True)

    # Google connect bar
    gc1, gc2, gc3 = st.columns([4, 2, 1])
    with gc1:
        if is_yt_connected:
            yt_email = st.session_state.get("yt_email","Your Google Account")
            st.markdown(
                f"<div style='background:rgba(0,200,80,0.1);border:1px solid rgba(0,200,80,0.35);"
                f"border-radius:8px;padding:7px 14px;color:#00c850;font-size:.85rem;'>"
                f"✅ <b>{yt_email}</b> connected</div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background:{_T['ytm_card']};border:1px solid rgba(255,255,255,0.1);"
                f"border-radius:8px;padding:7px 14px;color:{_T['ytm_txt2']};font-size:.85rem;'>"
                f"🔗 Connect Google to access your real YouTube Music library</div>",
                unsafe_allow_html=True)
    with gc2:
        if not is_yt_connected and _OAUTH_OK:
            result = _oauth2.authorize_button(
                name="🎵 Connect Google",
                redirect_uri=REDIRECT_URI,
                scope="openid email profile https://www.googleapis.com/auth/youtube.readonly",
                key="yt_google_oauth", use_container_width=True,
                icon="https://www.google.com/favicon.ico"
            )
            if result and "token" in result:
                st.session_state.yt_token = result["token"]
                try:
                    info = requests.get(
                        "https://www.googleapis.com/oauth2/v3/userinfo",
                        headers={"Authorization": f"Bearer {result['token']['access_token']}"},
                        timeout=8).json()
                    st.session_state.yt_email = info.get("email","")
                except Exception:
                    pass
                st.rerun()
        elif not is_yt_connected and not _OAUTH_OK:
            st.info("Add GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET to secrets.")
    with gc3:
        if is_yt_connected:
            if st.button("Disconnect", key="yt_disconnect", use_container_width=True):
                st.session_state.yt_token = None
                st.session_state.yt_email = ""
                for k in ["yt_liked_cache","yt_playlists_cache","yt_pl_items_cache",
                          "yt_subs_cache","home_trending"]:
                    st.session_state.pop(k, None)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # NOW PLAYING BAR
    # ════════════════════════════════════════════════════════════════════
    if st.session_state.now_playing_id:
        vid_id    = st.session_state.now_playing_id
        vid_title = st.session_state.now_playing_title
        vid_thumb = st.session_state.now_playing_thumb
        vid_artist= st.session_state.now_playing_artist

        st.markdown(f"""
<div class="ytm-now-playing">
  {"<img src='" + vid_thumb + "' class='ytm-np-thumb'/>" if vid_thumb else ""}
  <div class="ytm-np-info">
    <div class="ytm-np-title">{vid_title}</div>
    <div class="ytm-np-artist">{vid_artist}</div>
  </div>
  <div class="ytm-np-badge">▶ PLAYING</div>
</div>""", unsafe_allow_html=True)

        _comp.html(
            f"<div style='background:#0f0f0f;border-radius:10px;overflow:hidden;'>"
            f"<iframe width='100%' height='80' frameborder='0' allow='autoplay;encrypted-media'"
            f" src='https://www.youtube-nocookie.com/embed/{vid_id}"
            f"?autoplay=1&modestbranding=1&rel=0&iv_load_policy=3'></iframe></div>",
            height=88)

        np1, np2, np3 = st.columns([1, 2, 1])
        with np2:
            if st.session_state.queue:
                nxt = st.session_state.queue[0]
                if st.button(f"⏭  {nxt['title'][:38]}",
                             use_container_width=True, key="ytm_next"):
                    _play(nxt["id"], nxt["title"], nxt.get("artist",""), nxt.get("thumb",""))
                    st.session_state.queue = st.session_state.queue[1:]
                    st.rerun()
        with np3:
            if st.button("⏹ Stop", key="ytm_stop", use_container_width=True):
                st.session_state.now_playing_id = None
                st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # GENRE CHIPS ROW
    # ════════════════════════════════════════════════════════════════════
    GENRES = ["Trending🔥","Pop","Hip-Hop","Lo-fi","Tamil","Malayalam","Bollywood","K-Pop","Jazz","Rock","EDM","Classical"]
    st.markdown('<div class="ytm-chip-row">' +
        "".join(f'<span class="ytm-chip">{g}</span>' for g in GENRES) +
        "</div>", unsafe_allow_html=True)

    chip_cols = st.columns(len(GENRES))
    for ci, genre in enumerate(GENRES):
        with chip_cols[ci]:
            if st.button(genre, key=f"chip_{genre}", use_container_width=True):
                q = "trending music india" if genre.startswith("Trending") else genre
                with st.spinner(f"Loading {genre}…"):
                    st.session_state.music_search_results = do_search(q, 16)
                    st.session_state.music_search_query   = genre
                st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # MAIN TABS — YTM style
    # ════════════════════════════════════════════════════════════════════
    music_tabs = st.tabs([
        "🏠 Home", "🔍 Search", "❤️ Liked", "📚 Playlists",
        "📺 Subscriptions", "🎵 Jam", "🔢 Queue"
    ])

    # ══ HOME ══════════════════════════════════════════════════════════════════
    with music_tabs[0]:
        rh1, rh2 = st.columns([5,1])
        with rh1:
            st.markdown(f"<div class='ytm-section-title'>🔥 Trending Music</div>",
                        unsafe_allow_html=True)
        with rh2:
            if st.button("🔄 Refresh", key="ytm_refresh_home"):
                st.session_state.pop("home_trending", None)
                st.rerun()
        if not is_yt_connected and not HAS_YT_KEY:
            st.markdown(f"""
<div style='background:{_T['ytm_card']};border:1px solid rgba(255,0,0,0.25);border-radius:12px;
padding:24px;text-align:center;'>
  <div style='font-size:3rem;'>🎵</div>
  <div style='color:{_T['ytm_txt']};font-size:1.1rem;font-weight:600;margin:10px 0;'>Connect to start listening</div>
  <div style='color:{_T['ytm_txt2']};font-size:.9rem;'>Connect your Google account above, or add a YOUTUBE_API_KEY to Streamlit secrets.</div>
</div>""", unsafe_allow_html=True)
        else:
            if "home_trending" not in st.session_state:
                with st.spinner("Loading trending…"):
                    st.session_state.home_trending = do_trending(24)
            render_ytm_grid(st.session_state.home_trending, cols=4, prefix="home")

    # ══ SEARCH ════════════════════════════════════════════════════════════════
    with music_tabs[1]:
        sq1, sq2 = st.columns([5, 1])
        with sq1:
            st.markdown('<div class="ytm-search-bar">', unsafe_allow_html=True)
            search_q = st.text_input(
                "", placeholder="🔍  Search songs, artists, albums…",
                label_visibility="collapsed", key="ytm_search_input",
                value=st.session_state.music_search_query)
            st.markdown("</div>", unsafe_allow_html=True)
        with sq2:
            go = st.button("Search", use_container_width=True, key="ytm_search_go")

        if go and search_q:
            st.session_state.music_search_query = search_q
            with st.spinner("Searching…"):
                st.session_state.music_search_results = do_search(search_q, 16)

        if st.session_state.music_search_results:
            q_label = st.session_state.music_search_query
            st.markdown(f"<div class='ytm-section-title'>Results for {q_label}</div>",
                        unsafe_allow_html=True)
            render_ytm_grid(st.session_state.music_search_results, cols=4, prefix="sr")
        elif not go:
            st.markdown(f"""
<div style='text-align:center;padding:80px 20px;color:{_T['ytm_txt2']};'>
  <div style='font-size:4rem;'>🔍</div>
  <p style='font-size:1.1rem;'>Search for any song, artist or album</p>
</div>""", unsafe_allow_html=True)

    # ══ LIKED ═════════════════════════════════════════════════════════════════
    with music_tabs[2]:
        if is_yt_connected:
            lh1, lh2 = st.columns([5,1])
            with lh1:
                st.markdown("<div class='ytm-section-title'>❤️ Your Liked Songs</div>",
                            unsafe_allow_html=True)
            with lh2:
                if st.button("🔄", key="ytm_refresh_liked"):
                    st.session_state.pop("yt_liked_cache", None)
                    st.rerun()
            if "yt_liked_cache" not in st.session_state:
                with st.spinner("Fetching liked songs…"):
                    st.session_state.yt_liked_cache = yt_liked(50)
            render_ytm_tracklist(st.session_state.yt_liked_cache, prefix="lk")
        else:
            st.markdown("<div class='ytm-section-title'>❤️ Saved Songs</div>",
                        unsafe_allow_html=True)
            st.info("Connect Google to see your real YouTube liked songs.")
            liked_local = get_liked_songs(st.session_state.user)
            if liked_local:
                items_local = [{"id":{"videoId":s["video_id"]},
                                "snippet":{"title":s["title"],"channelTitle":s["artist"],
                                           "thumbnails":{"medium":{"url":s.get("thumbnail","")}}}}
                               for s in liked_local]
                render_ytm_tracklist(items_local, prefix="lk_local")
            else:
                st.markdown(f"<p style='color:{_T['ytm_txt2']};'>No saved songs yet.</p>",
                            unsafe_allow_html=True)
            if st.session_state.now_playing_id:
                if st.button(f"❤️  Save: {st.session_state.now_playing_title[:40]}",
                             use_container_width=True, key="ytm_like_current"):
                    like_song(st.session_state.user,
                              st.session_state.now_playing_id,
                              st.session_state.now_playing_title,
                              st.session_state.now_playing_artist,
                              st.session_state.now_playing_thumb)
                    st.success("❤️ Saved!")
                    st.rerun()

    # ══ PLAYLISTS ═════════════════════════════════════════════════════════════
    with music_tabs[3]:
        if is_yt_connected:
            ph1, ph2 = st.columns([5,1])
            with ph1:
                st.markdown("<div class='ytm-section-title'>📚 Your YouTube Playlists</div>",
                            unsafe_allow_html=True)
            with ph2:
                if st.button("🔄", key="ytm_refresh_pl"):
                    st.session_state.pop("yt_playlists_cache", None)
                    st.session_state.pop("yt_pl_items_cache", None)
                    st.rerun()
            if "yt_playlists_cache" not in st.session_state:
                with st.spinner("Loading playlists…"):
                    st.session_state.yt_playlists_cache = yt_playlists(50)
            pls = st.session_state.yt_playlists_cache
            if not pls:
                st.markdown(f"<p style='color:{_T['ytm_txt2']};'>No playlists found.</p>",
                            unsafe_allow_html=True)
            else:
                pl_left, pl_right = st.columns([1, 2])
                with pl_left:
                    for pl in pls:
                        pl_id    = pl["id"]
                        pl_title = pl["snippet"]["title"]
                        pl_thumb = pl["snippet"].get("thumbnails",{}).get("medium",{}).get("url","")
                        pl_count = pl.get("contentDetails",{}).get("itemCount","?")
                        row_html = f"""
<div class="ytm-playlist-row">
  {"<img src='" + pl_thumb + "' class='ytm-playlist-thumb'/>" if pl_thumb else "<div class='ytm-playlist-thumb'></div>"}
  <div>
    <div style="color:{_T['ytm_txt']};font-size:.88rem;font-weight:600;">{pl_title[:28]}</div>
    <div style="color:{_T['ytm_txt2']};font-size:.76rem;">{pl_count} tracks</div>
  </div>
</div>"""
                        st.markdown(row_html, unsafe_allow_html=True)
                        if st.button("Open", key=f"yt_pl_{pl_id}", use_container_width=True):
                            with st.spinner("Loading…"):
                                st.session_state.yt_pl_items_cache = yt_pl_items(pl_id, 50)
                                st.session_state.active_yt_pl_name = pl_title
                            st.rerun()

                with pl_right:
                    if st.session_state.get("yt_pl_items_cache") is not None:
                        pl_name  = st.session_state.get("active_yt_pl_name","Playlist")
                        pl_items = st.session_state.yt_pl_items_cache
                        st.markdown(f"<div class='ytm-section-title'>📀 {pl_name}</div>",
                                    unsafe_allow_html=True)
                        if st.button("▶ Play All", use_container_width=True, key="ytm_play_all_pl"):
                            if pl_items:
                                first = pl_items[0]
                                _play(first["id"]["videoId"],
                                      first["snippet"].get("title",""),
                                      first["snippet"].get("channelTitle",""),
                                      (first["snippet"].get("thumbnails",{})
                                       .get("medium",{}).get("url","")))
                                st.session_state.queue = [
                                    {"id":i["id"]["videoId"],
                                     "title":i["snippet"].get("title",""),
                                     "artist":i["snippet"].get("channelTitle",""),
                                     "thumb":(i["snippet"].get("thumbnails",{})
                                              .get("medium",{}).get("url",""))}
                                    for i in pl_items[1:]]
                                st.rerun()
                        render_ytm_tracklist(pl_items, prefix="ytpl")
                    else:
                        st.markdown(f"""
<div style='text-align:center;padding:60px;color:{_T['ytm_txt2']};'>
  <div style='font-size:3rem;'>📀</div>
  <p>Select a playlist to view tracks</p>
</div>""", unsafe_allow_html=True)
        else:
            # In-app playlists
            st.markdown("<div class='ytm-section-title'>📀 My Playlists</div>",
                        unsafe_allow_html=True)
            st.info("Connect Google for real YouTube playlists.")
            iap_left, iap_right = st.columns([1, 2])
            with iap_left:
                npn = st.text_input("New playlist name", key="new_pl_input",
                                    placeholder="e.g. Chill Vibes")
                if st.button("➕ Create", key="create_pl", use_container_width=True):
                    if npn.strip():
                        save_playlist(st.session_state.user, npn.strip(), [])
                        st.success("Created!")
                        st.rerun()
                st.markdown("---")
                for pl in get_playlists(st.session_state.user):
                    pc1, pc2 = st.columns([3,1])
                    with pc1:
                        if st.button(f"📀 {pl['name']}", key=f"open_pl_{pl['name']}",
                                     use_container_width=True):
                            st.session_state.active_playlist_name = pl["name"]
                            st.rerun()
                    with pc2:
                        if st.button("🗑", key=f"del_pl_{pl['name']}",
                                     use_container_width=True):
                            delete_playlist(st.session_state.user, pl["name"])
                            st.rerun()
            with iap_right:
                act = st.session_state.active_playlist_name
                if act:
                    playlists_local = get_playlists(st.session_state.user)
                    pl_data = next((p for p in playlists_local if p["name"] == act), None)
                    if pl_data:
                        songs = pl_data.get("songs",[])
                        st.markdown(f"<div class='ytm-section-title'>📀 {act} ({len(songs)})</div>",
                                    unsafe_allow_html=True)
                        if st.session_state.now_playing_id:
                            if st.button("➕ Add current track",
                                         use_container_width=True, key="add_to_pl"):
                                ns = {"id":st.session_state.now_playing_id,
                                      "title":st.session_state.now_playing_title,
                                      "artist":st.session_state.now_playing_artist,
                                      "thumb":st.session_state.now_playing_thumb}
                                if not any(s["id"]==ns["id"] for s in songs):
                                    songs.append(ns)
                                    save_playlist(st.session_state.user, act, songs)
                                    st.success("Added!")
                                    st.rerun()
                        if songs:
                            if st.button("▶ Play All", use_container_width=True,
                                         key="play_all_iap"):
                                _play(songs[0]["id"],songs[0]["title"],
                                      songs[0].get("artist",""),songs[0].get("thumb",""))
                                st.session_state.queue = songs[1:]
                                st.rerun()
                            items_iap = [{"id":{"videoId":s["id"]},
                                          "snippet":{"title":s["title"],
                                                     "channelTitle":s.get("artist",""),
                                                     "thumbnails":{"medium":{"url":s.get("thumb","")}}}}
                                         for s in songs]
                            render_ytm_tracklist(items_iap, prefix="iap")

    # ══ SUBSCRIPTIONS ═════════════════════════════════════════════════════════
    with music_tabs[4]:
        if is_yt_connected:
            sh1, sh2 = st.columns([5,1])
            with sh1:
                st.markdown("<div class='ytm-section-title'>📺 Your Subscriptions</div>",
                            unsafe_allow_html=True)
            with sh2:
                if st.button("🔄", key="ytm_refresh_subs"):
                    st.session_state.pop("yt_subs_cache", None)
                    st.rerun()
            if "yt_subs_cache" not in st.session_state:
                with st.spinner("Loading subscriptions…"):
                    st.session_state.yt_subs_cache = yt_subs(50)
            subs = st.session_state.yt_subs_cache
            if not subs:
                st.markdown(f"<p style='color:{_T['ytm_txt2']};'>No subscriptions found.</p>",
                            unsafe_allow_html=True)
            else:
                sub_cols = st.columns(5)
                for si, sub in enumerate(subs):
                    snip     = sub["snippet"]
                    ch_title = snip.get("title","")
                    ch_thumb = snip.get("thumbnails",{}).get("medium",{}).get("url","")
                    with sub_cols[si % 5]:
                        if ch_thumb:
                            st.image(ch_thumb, width=70)
                        st.markdown(
                            f"<div style='color:{_T['ytm_txt']};font-size:.76rem;text-align:center;"
                            f"overflow:hidden;text-overflow:ellipsis;white-space:nowrap;'>{ch_title}</div>",
                            unsafe_allow_html=True)
                        if st.button("▶", key=f"sub_{si}", use_container_width=True):
                            st.session_state.music_search_query = ch_title
                            st.session_state.music_search_results = do_search(ch_title, 16)
                            st.rerun()
        else:
            st.info("Connect your Google account to see your YouTube subscriptions.")

    # ══ JAM ═══════════════════════════════════════════════════════════════════
    with music_tabs[5]:
        st.markdown("<div class='ytm-section-title'>🎵 Music Jam — Listen Together</div>",
                    unsafe_allow_html=True)
        st.markdown(f"<p style='color:{_T['ytm_txt2']};'>Share what you're playing with a friend in real time.</p>",
                    unsafe_allow_html=True)
        if st.session_state.now_playing_id:
            st.markdown(f"""
<div style='background:{_T['ytm_card']};border:1px solid rgba(255,0,0,0.25);
border-radius:12px;padding:16px;margin-bottom:16px;'>
  <div style='color:{_T['ytm_red']};font-weight:700;margin-bottom:6px;'>🎵 Now Playing</div>
  <div style='color:{_T['ytm_txt']};font-size:.95rem;font-weight:600;'>
      {st.session_state.now_playing_title}</div>
  <div style='color:{_T['ytm_txt2']};font-size:.82rem;'>
      {st.session_state.now_playing_artist}</div>
</div>""", unsafe_allow_html=True)
            my_u = get_user(st.session_state.user)
            jam_friends = list(my_u.get("friends") or []) if my_u else []
            if not jam_friends:
                st.info("Add friends to jam with them.")
            else:
                jam_cols = st.columns(min(len(jam_friends), 4))
                for ji, f in enumerate(jam_friends):
                    with jam_cols[ji % 4]:
                        if st.button(f"🎵 Jam: {f}", key=f"jam_{f}",
                                     use_container_width=True):
                            send_jam(st.session_state.user, f,
                                     st.session_state.now_playing_id,
                                     st.session_state.now_playing_title,
                                     st.session_state.now_playing_thumb)
                            st.success(f"Sent jam to {f}!")
        else:
            st.markdown(f"""
<div style='text-align:center;padding:60px;color:{_T['ytm_txt2']};'>
  <div style='font-size:3rem;'>🎵</div>
  <p>Play a song first, then share the jam here</p>
</div>""", unsafe_allow_html=True)

        inc_jam = get_jam(st.session_state.user)
        if inc_jam:
            st.markdown("---")
            st.markdown(
                f"<h5 style='color:#00c850;'>📨 {inc_jam['host']} invited you to jam!</h5>",
                unsafe_allow_html=True)
            if st.button(f"▶ Play: {inc_jam['title']}", key="join_jam_music",
                         use_container_width=True):
                _play(inc_jam["video_id"], inc_jam["title"],
                      inc_jam["host"], inc_jam["thumbnail"])
                st.rerun()

    # ══ QUEUE ═════════════════════════════════════════════════════════════════
    with music_tabs[6]:
        q_count = len(st.session_state.queue)
        st.markdown(f"<div class='ytm-section-title'>🔢 Queue ({q_count} tracks)</div>",
                    unsafe_allow_html=True)
        if not st.session_state.queue:
            st.markdown(f"""
<div style='text-align:center;padding:60px;color:{_T['ytm_txt2']};'>
  <div style='font-size:3rem;'>📋</div>
  <p>Queue is empty — hit ＋Queue on any track</p>
</div>""", unsafe_allow_html=True)
        else:
            if st.button("🗑  Clear Queue", key="ytm_clear_q"):
                st.session_state.queue = []
                st.rerun()
            for qi, track in enumerate(st.session_state.queue):
                qc1, qc2, qc3, qc4 = st.columns([0.8, 5, 1.5, 1])
                with qc1:
                    if track.get("thumb"):
                        st.image(track["thumb"], width=48)
                    st.markdown(
                        f"<div style='color:{_T['ytm_txt2']};text-align:center;'>{qi+1}</div>",
                        unsafe_allow_html=True)
                with qc2:
                    st.markdown(
                        f"<div style='color:{_T['ytm_txt']};font-weight:500;'>{track['title']}</div>"
                        f"<div style='color:{_T['ytm_txt2']};font-size:.78rem;'>{track.get('artist','')}</div>",
                        unsafe_allow_html=True)
                with qc3:
                    if st.button("▶ Now", key=f"q_now_{qi}", use_container_width=True):
                        _play(track["id"], track["title"],
                              track.get("artist",""), track.get("thumb",""))
                        st.session_state.queue.pop(qi)
                        st.rerun()
                with qc4:
                    if st.button("✕", key=f"q_rm_{qi}", use_container_width=True):
                        st.session_state.queue.pop(qi)
                        st.rerun()
                st.markdown(
                    f"<hr style='border:none;border-top:1px solid {_T['ytm_card2']};margin:2px 0;'>",
                    unsafe_allow_html=True)



# ─────────────────────────────────────────
# 12. WEATHER PAGE — GPS only + Charts
# ─────────────────────────────────────────
elif st.session_state.current_page == "Weather":
    import json
    import pandas as pd

    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>🌤️ SkyView Weather</div>", unsafe_allow_html=True)

    WMO_CODES = {
        0: ("Clear sky", "☀️"), 1: ("Mainly clear", "🌤️"), 2: ("Partly cloudy", "⛅"),
        3: ("Overcast", "☁️"), 45: ("Foggy", "🌫️"), 48: ("Icy fog", "🌫️"),
        51: ("Light drizzle", "🌦️"), 53: ("Drizzle", "🌦️"), 55: ("Heavy drizzle", "🌧️"),
        61: ("Slight rain", "🌧️"), 63: ("Moderate rain", "🌧️"), 65: ("Heavy rain", "🌧️"),
        71: ("Slight snow", "🌨️"), 73: ("Moderate snow", "❄️"), 75: ("Heavy snow", "❄️"),
        80: ("Rain showers", "🌦️"), 81: ("Heavy showers", "⛈️"), 95: ("Thunderstorm", "⛈️"),
    }

    # ── GPS Button ────────────────────────────────────────────────────────────
    col_btn, col_refresh, _ = st.columns([2, 1, 2])
    with col_btn:
        if _GEO_OK:
            gps_btn = st.button("📍 Detect My Location", use_container_width=True, key="gps_btn")
        else:
            gps_btn = False
            st.error("⚠️ Install streamlit-js-eval for GPS support")
    with col_refresh:
        if st.session_state.weather_fetched:
            if st.button("🔄 Refresh", use_container_width=True, key="refresh_btn"):
                st.session_state.weather_fetched = False
                st.session_state.gps_lat = None
                st.session_state.gps_lon = None
                st.rerun()

    # ── GPS fetch ─────────────────────────────────────────────────────────────
    if gps_btn and _GEO_OK:
        with st.spinner("📍 Getting your location... (allow access if prompted)"):
            try:
                geo_data = get_geolocation()
                if geo_data and "coords" in geo_data:
                    gps_lat = geo_data["coords"]["latitude"]
                    gps_lon = geo_data["coords"]["longitude"]
                    # Reverse geocode — free, no API key
                    rev = requests.get(
                        "https://nominatim.openstreetmap.org/reverse",
                        params={"lat": gps_lat, "lon": gps_lon, "format": "json"},
                        headers={"User-Agent": "LakshmeeyamAI/1.0"},
                        timeout=10
                    ).json()
                    addr = rev.get("address", {})
                    city_name = (
                        addr.get("city") or addr.get("town")
                        or addr.get("village") or addr.get("county")
                        or "Your Location"
                    )
                    country = addr.get("country", "")
                    st.session_state.gps_lat     = gps_lat
                    st.session_state.gps_lon     = gps_lon
                    st.session_state.gps_city    = city_name
                    st.session_state.gps_country = country
                    st.session_state.weather_fetched = True
                    st.rerun()
                else:
                    st.warning("⚠️ Location not received. Please allow location access in your browser and try again.")
            except Exception as e:
                st.error(f"❌ GPS error: {e}")

    # ── Render weather if GPS data available ──────────────────────────────────
    if st.session_state.weather_fetched and st.session_state.gps_lat:
        lat       = st.session_state.gps_lat
        lon       = st.session_state.gps_lon
        city_name = st.session_state.gps_city
        country   = st.session_state.gps_country

        try:
            with st.spinner("⛅ Loading weather data..."):
                weather = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current_weather": "true",
                        "hourly": "temperature_2m,apparent_temperature,relativehumidity_2m,precipitation_probability,windspeed_10m,weathercode",
                        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode",
                        "forecast_days": 7,
                        "timezone": "auto"
                    },
                    timeout=10
                ).json()

            curr      = weather["current_weather"]
            temp      = curr["temperature"]
            wind      = curr["windspeed"]
            wcode     = int(curr.get("weathercode", 0))
            is_day    = curr.get("is_day", 1)
            condition, w_icon = WMO_CODES.get(wcode, ("Unknown", "🌡️"))

            # ── Current weather card ──────────────────────────────────────────
            st.markdown(f"""
            <div class='weather-card'>
                <div style='display:inline-block; background:rgba(0,255,136,0.15);
                border:1px solid #00ff88; border-radius:20px; padding:2px 12px;
                font-size:0.8rem; color:#00ff88; margin-bottom:10px;'>
                📍 GPS · {city_name}, {country}
                </div>
                <div style='font-size:5rem; line-height:1;'>{w_icon}</div>
                <div style='font-size:4rem; color:#00d4ff;
                font-family:Orbitron,sans-serif; margin:10px 0;'>{temp}°C</div>
                <div style='color:rgba(255,255,255,0.7); font-size:1.1rem;'>
                {'☀️ Daytime' if is_day else '🌙 Nighttime'} · {condition}
                </div>
                <div style='display:flex; justify-content:center; gap:40px;
                margin-top:20px; flex-wrap:wrap;'>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>💨 Wind</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>{wind} km/h</div></div>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>🌡️ Feels Like</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>
                         {weather["hourly"]["apparent_temperature"][0]}°C</div></div>
                    <div><div style='color:rgba(255,255,255,0.5); font-size:0.85rem;'>💧 Humidity</div>
                         <div style='color:white; font-size:1.3rem;font-weight:600;'>
                         {weather["hourly"]["relativehumidity_2m"][0]}%</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ── Hourly charts (next 24 hours) ─────────────────────────────────
            hourly   = weather["hourly"]
            # Find index of current hour
            curr_time_str = curr.get("time", "")
            all_times = hourly["time"]
            try:
                start_idx = next(
                    (i for i, t in enumerate(all_times) if t >= curr_time_str), 0
                )
            except Exception:
                start_idx = 0
            end_idx = min(start_idx + 24, len(all_times))

            hours_labels = [t[11:16] for t in all_times[start_idx:end_idx]]
            temps_24     = hourly["temperature_2m"][start_idx:end_idx]
            humidity_24  = hourly["relativehumidity_2m"][start_idx:end_idx]
            precip_24    = hourly["precipitation_probability"][start_idx:end_idx]
            wind_24      = hourly["windspeed_10m"][start_idx:end_idx]

            df_hourly = pd.DataFrame({
                "Hour":        hours_labels,
                "Temp (°C)":   temps_24,
                "Humidity (%)":humidity_24,
                "Rain chance (%)": precip_24,
                "Wind (km/h)": wind_24,
            })

            st.markdown("<h4 style='color:#00d4ff;'>📈 Next 24 Hours</h4>", unsafe_allow_html=True)

            tab_temp, tab_rain, tab_wind, tab_humid = st.tabs([
                "🌡️ Temperature", "🌧️ Rain Chance", "💨 Wind Speed", "💧 Humidity"
            ])

            chart_config = {"displayModeBar": False}

            with tab_temp:
                st.line_chart(
                    df_hourly.set_index("Hour")["Temp (°C)"],
                    color="#00d4ff",
                    use_container_width=True,
                    height=220
                )

            with tab_rain:
                st.bar_chart(
                    df_hourly.set_index("Hour")["Rain chance (%)"],
                    color="#7b2fff",
                    use_container_width=True,
                    height=220
                )

            with tab_wind:
                st.line_chart(
                    df_hourly.set_index("Hour")["Wind (km/h)"],
                    color="#00ff88",
                    use_container_width=True,
                    height=220
                )

            with tab_humid:
                st.area_chart(
                    df_hourly.set_index("Hour")["Humidity (%)"],
                    color="#ffa500",
                    use_container_width=True,
                    height=220
                )

            # ── 7-day forecast cards ──────────────────────────────────────────
            st.markdown("<br><h4 style='color:#00d4ff;'>📅 7-Day Forecast</h4>", unsafe_allow_html=True)
            daily   = weather["daily"]
            d_dates = daily.get("time", [])
            d_max   = daily.get("temperature_2m_max", [])
            d_min   = daily.get("temperature_2m_min", [])
            d_prec  = daily.get("precipitation_sum", [])
            d_codes = daily.get("weathercode", [])

            d_cols = st.columns(len(d_dates))
            for i in range(len(d_dates)):
                dc, dicon = WMO_CODES.get(int(d_codes[i]) if i < len(d_codes) else 0, ("?", "🌡️"))
                day_name  = datetime.strptime(d_dates[i], "%Y-%m-%d").strftime("%a %d")
                prec_val  = round(d_prec[i], 1) if i < len(d_prec) and d_prec[i] else 0
                with d_cols[i]:
                    st.markdown(f"""
                    <div style='background:rgba(0,100,150,0.2);
                    border:1px solid rgba(0,150,255,0.3); border-radius:12px;
                    padding:14px 6px; text-align:center; color:white;'>
                        <div style='color:rgba(255,255,255,0.6); font-size:0.75rem;'>{day_name}</div>
                        <div style='font-size:2rem; margin:6px 0;'>{dicon}</div>
                        <div style='color:#ff6b6b; font-weight:700;'>
                            {d_max[i] if i < len(d_max) else '-'}°</div>
                        <div style='color:#74b9ff; font-size:0.85rem;'>
                            {d_min[i] if i < len(d_min) else '-'}°</div>
                        <div style='color:rgba(150,200,255,0.7); font-size:0.72rem; margin-top:4px;'>
                            💧{prec_val}mm</div>
                    </div>
                    """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error("❌ No internet connection.")
        except Exception as e:
            st.error(f"❌ Error loading weather: {e}")

    # ── Empty state ───────────────────────────────────────────────────────────
    else:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:rgba(255,255,255,0.3);'>
            <div style='font-size:5rem;'>🌍</div>
            <p style='font-size:1.3rem; color:rgba(255,255,255,0.5);'>
                Tap <b style='color:#00ff88;'>📍 Detect My Location</b> above
            </p>
            <p style='font-size:0.85rem;'>
                Uses your device GPS · No typing needed<br>
                Temperature · Rain · Wind · Humidity · 7-Day Forecast
            </p>
        </div>
        """, unsafe_allow_html=True)

# ── End analytics tracking ────────────────────────────────────────────────────
if _ANALYTICS_OK:
    try:
        streamlit_analytics.stop_tracking(
            ga4_id="G-98JQK90KWX",
            unsafe_password=""
        )
    except Exception:
        pass
