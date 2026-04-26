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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Rajdhani', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0a0a1a 0%, #0d1b2a 50%, #0a0a1a 100%);
    min-height: 100vh;
}

.main-box {
    background: rgba(0, 212, 255, 0.05);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: white;
    margin-bottom: 20px;
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.1), inset 0 0 20px rgba(0,0,0,0.3);
    backdrop-filter: blur(10px);
}

.hero-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #7b2fff, #00d4ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    animation: shimmer 3s infinite;
    margin-bottom: 0.2rem;
}

.hero-sub {
    text-align: center;
    color: rgba(0,212,255,0.6);
    font-size: 1rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

@keyframes shimmer { 0%{background-position:0%} 50%{background-position:100%} 100%{background-position:0%} }

.stat-card {
    background: rgba(0,212,255,0.07);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    color: white;
}

.stat-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem;
    color: #00d4ff;
}

.chat-bubble-user {
    background: linear-gradient(135deg, #1a1a3e, #2a1a5e);
    border: 1px solid rgba(123,47,255,0.4);
    border-radius: 12px 12px 2px 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: white;
    max-width: 80%;
    margin-left: auto;
}

.chat-bubble-ai {
    background: linear-gradient(135deg, #0a2a3a, #0a1a2e);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 12px 12px 12px 2px;
    padding: 12px 16px;
    margin: 8px 0;
    color: white;
    max-width: 80%;
}

.stButton > button {
    background: linear-gradient(135deg, rgba(0,212,255,0.15), rgba(123,47,255,0.15));
    color: #00d4ff;
    border: 1px solid rgba(0,212,255,0.4);
    border-radius: 8px;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    transition: all 0.3s;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(0,212,255,0.3), rgba(123,47,255,0.3));
    border-color: #00d4ff;
    box-shadow: 0 0 15px rgba(0,212,255,0.4);
    transform: translateY(-1px);
}

.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: rgba(0,0,0,0.4) !important;
    color: white !important;
    border: 1px solid rgba(0,212,255,0.3) !important;
    border-radius: 8px !important;
}

.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background: rgba(0,212,255,0.05);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 8px;
    color: rgba(255,255,255,0.7);
    font-family: 'Rajdhani', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,212,255,0.15) !important;
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}

[data-testid="stSidebar"] {
    background: rgba(5, 10, 25, 0.95);
    border-right: 1px solid rgba(0,212,255,0.2);
}

.sidebar-logo {
    font-family: 'Orbitron', sans-serif;
    font-size: 1.1rem;
    color: #00d4ff;
    text-align: center;
    padding: 10px;
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 8px;
    margin-bottom: 15px;
}

.stAppDeployButton { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.weather-card {
    background: linear-gradient(135deg, rgba(0,100,200,0.2), rgba(0,50,100,0.3));
    border: 1px solid rgba(0,150,255,0.4);
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    color: white;
}

.online-dot {
    display: inline-block;
    width: 8px; height: 8px;
    background: #00ff88;
    border-radius: 50%;
    margin-right: 6px;
    animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

.gps-btn {
    background: linear-gradient(135deg, rgba(0,255,136,0.15), rgba(0,212,100,0.15)) !important;
    color: #00ff88 !important;
    border: 1px solid rgba(0,255,136,0.4) !important;
}
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

def youtube_trending(max_results: int = 12) -> list:
    try:
        api_key = st.secrets.get("YOUTUBE_API_KEY", "")
        if not api_key:
            return []
        resp = requests.get(
            "https://www.googleapis.com/youtube/v3/videos",
            params={
                "part": "snippet", "chart": "mostPopular",
                "videoCategoryId": "10", "maxResults": max_results,
                "regionCode": "IN", "key": api_key
            },
            timeout=10
        ).json()
        # Normalize to same shape as search results
        items = []
        for item in resp.get("items", []):
            items.append({
                "id": {"videoId": item["id"]},
                "snippet": item["snippet"]
            })
        return items
    except:
        return []
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

    friends_list = u_data.get("friends", [])

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
        incoming_reqs = u_data.get("requests", [])
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
                        u_data["friends"].append(r)
                        u_data["requests"].remove(r)
                        save_user(st.session_state.user, u_data)
                        r_data = get_user(r)
                        if r_data and st.session_state.user not in r_data.get("friends", []):
                            r_data["friends"].append(st.session_state.user)
                            save_user(r, r_data)
                        st.rerun()
                with rc3:
                    if st.button("❌ Decline", key=f"dec_{r}", use_container_width=True):
                        u_data["requests"].remove(r)
                        save_user(st.session_state.user, u_data)
                        st.rerun()


# ═══════════════════════════════════════════════════════════════════════════════
# 11b. MUSIC PAGE — Full YouTube Music-style
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.current_page == "Music":
    import streamlit.components.v1 as _comp

    HAS_YT_KEY = bool(st.secrets.get("YOUTUBE_API_KEY", ""))

    # ── Sticky Now Playing bar ────────────────────────────────────────────────
    if st.session_state.now_playing_id:
        vid_id = st.session_state.now_playing_id
        vid_title = st.session_state.now_playing_title
        vid_thumb = st.session_state.now_playing_thumb
        vid_artist = st.session_state.now_playing_artist

        st.markdown(f"""
        <div style='background:linear-gradient(90deg,#1a0a2e,#0a1a2e);
        border:1px solid rgba(255,68,68,0.4); border-radius:14px;
        padding:14px 20px; display:flex; align-items:center; gap:16px; margin-bottom:16px;'>
            <img src='{vid_thumb}' style='width:56px; height:42px; border-radius:6px; object-fit:cover;'/>
            <div style='flex:1;'>
                <div style='color:white; font-weight:700; font-size:0.95rem;'>{vid_title}</div>
                <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>{vid_artist}</div>
            </div>
            <div style='color:#ff4444; font-size:0.8rem; letter-spacing:1px;'>▶ NOW PLAYING</div>
        </div>""", unsafe_allow_html=True)

        _comp.html(f"""
        <div style="background:#0a0a1a; border-radius:10px; overflow:hidden;">
        <iframe
            width="100%" height="90"
            src="https://www.youtube-nocookie.com/embed/{vid_id}?autoplay=1&modestbranding=1&rel=0&iv_load_policy=3"
            frameborder="0"
            allow="autoplay; encrypted-media"
            allowfullscreen>
        </iframe>
        </div>""", height=100)

        # Queue next
        if st.session_state.queue:
            next_track = st.session_state.queue[0]
            nq1, nq2, nq3 = st.columns([1, 3, 1])
            with nq2:
                if st.button(f"⏭ Next: {next_track['title'][:35]}…", use_container_width=True, key="next_track_btn"):
                    st.session_state.now_playing_id     = next_track["id"]
                    st.session_state.now_playing_title  = next_track["title"]
                    st.session_state.now_playing_artist = next_track.get("artist", "")
                    st.session_state.now_playing_thumb  = next_track.get("thumb", "")
                    st.session_state.queue = st.session_state.queue[1:]
                    st.rerun()

    # ── Music sub-navigation ──────────────────────────────────────────────────
    st.markdown("<div class='hero-title' style='font-size:1.8rem;'>🎵 Lakshmeeyam Music</div>", unsafe_allow_html=True)

    music_tabs = st.tabs([
        "🏠 Home", "🔍 Search", "📚 Library", "➕ Playlists", "🎵 Jam", "📋 Queue"
    ])

    # ── helper to render a video card grid ────────────────────────────────────
    def render_video_grid(items, cols=4, prefix="vg"):
        if not items:
            st.markdown("<p style='color:rgba(255,255,255,0.4); text-align:center;'>No results.</p>", unsafe_allow_html=True)
            return
        rows = [items[i:i+cols] for i in range(0, len(items), cols)]
        for row in rows:
            grid = st.columns(cols)
            for gi, item in enumerate(row):
                vid_id   = item["id"]["videoId"]
                snip     = item["snippet"]
                title    = snip.get("title", "Unknown")[:50]
                artist   = snip.get("channelTitle", "")[:30]
                thumb    = snip.get("thumbnails", {}).get("medium", {}).get("url", "")
                with grid[gi]:
                    st.markdown(f"""
                    <div style='background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.1);
                    border-radius:10px; overflow:hidden; cursor:pointer; transition:all 0.2s;'>
                        <img src='{thumb}' style='width:100%; aspect-ratio:16/9; object-fit:cover;'/>
                        <div style='padding:8px 10px;'>
                            <div style='color:white; font-size:0.82rem; font-weight:600;
                            white-space:nowrap; overflow:hidden; text-overflow:ellipsis;'>{title}</div>
                            <div style='color:rgba(255,255,255,0.45); font-size:0.74rem;'>{artist}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                    pc1, pc2 = st.columns(2)
                    with pc1:
                        if st.button("▶ Play", key=f"{prefix}_play_{vid_id}_{gi}", use_container_width=True):
                            st.session_state.now_playing_id     = vid_id
                            st.session_state.now_playing_title  = title
                            st.session_state.now_playing_artist = artist
                            st.session_state.now_playing_thumb  = thumb
                            st.rerun()
                    with pc2:
                        if st.button("+ Queue", key=f"{prefix}_q_{vid_id}_{gi}", use_container_width=True):
                            st.session_state.queue.append({"id": vid_id, "title": title, "artist": artist, "thumb": thumb})
                            st.toast(f"Added to queue: {title[:25]}")

    # ══ HOME TAB ══════════════════════════════════════════════════════════════
    with music_tabs[0]:
        if not HAS_YT_KEY:
            st.warning("⚠️ Add YOUTUBE_API_KEY to Streamlit secrets to enable music search & trending.")
            st.code("YOUTUBE_API_KEY = \"YOUR_KEY_HERE\"", language="toml")
            st.markdown("[Get a free YouTube Data API v3 key →](https://console.cloud.google.com/apis/library/youtube.googleapis.com)", unsafe_allow_html=False)
        else:
            st.markdown("<h4 style='color:#ff4444;'>🔥 Trending in India</h4>", unsafe_allow_html=True)
            if "trending_cache" not in st.session_state:
                with st.spinner("Loading trending music…"):
                    st.session_state.trending_cache = youtube_trending(12)
            render_video_grid(st.session_state.trending_cache, cols=4, prefix="tr")

            if st.button("🔄 Refresh Trending", key="refresh_trending"):
                if "trending_cache" in st.session_state:
                    del st.session_state["trending_cache"]
                st.rerun()

    # ══ SEARCH TAB ════════════════════════════════════════════════════════════
    with music_tabs[1]:
        sq1, sq2 = st.columns([4, 1])
        with sq1:
            search_q = st.text_input(
                "", placeholder="🔍 Search songs, artists, albums…",
                label_visibility="collapsed", key="music_search_box",
                value=st.session_state.music_search_query
            )
        with sq2:
            search_go = st.button("Search →", use_container_width=True, key="music_search_go")

        # Genre quick-search chips
        st.markdown("<p style='color:rgba(255,255,255,0.4); font-size:0.8rem;'>Quick search:</p>", unsafe_allow_html=True)
        genre_cols = st.columns(8)
        genres = ["Pop", "Hip-Hop", "Lo-fi", "Tamil", "Malayalam", "Bollywood", "K-Pop", "Jazz"]
        for gi, genre in enumerate(genres):
            with genre_cols[gi]:
                if st.button(genre, key=f"genre_{genre}", use_container_width=True):
                    st.session_state.music_search_query = genre
                    results = youtube_search(genre, 12)
                    st.session_state.music_search_results = results
                    st.rerun()

        if search_go and search_q:
            st.session_state.music_search_query = search_q
            with st.spinner("Searching…"):
                results = youtube_search(search_q, 12)
                st.session_state.music_search_results = results

        if st.session_state.music_search_results:
            q_display = st.session_state.music_search_query
            st.markdown(f"<h4 style='color:#00d4ff;'>Results for {q_display}</h4>", unsafe_allow_html=True)
            render_video_grid(st.session_state.music_search_results, cols=4, prefix="sr")
        elif not HAS_YT_KEY:
            st.warning("⚠️ Add YOUTUBE_API_KEY to Streamlit secrets.")
        else:
            st.markdown("""
            <div style='text-align:center; padding:60px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>🎵</div>
                <p>Search for any song, artist or album</p>
            </div>""", unsafe_allow_html=True)

    # ══ LIBRARY TAB ═══════════════════════════════════════════════════════════
    with music_tabs[2]:
        liked = get_liked_songs(st.session_state.user)
        st.markdown(f"<h4 style='color:#ff4444;'>❤️ Liked Songs ({len(liked)})</h4>", unsafe_allow_html=True)
        if not liked:
            st.markdown("<p style='color:rgba(255,255,255,0.4);'>No liked songs yet. Hit ❤️ on any track.</p>", unsafe_allow_html=True)
        else:
            for song in liked:
                lc1, lc2, lc3, lc4 = st.columns([1, 4, 1, 1])
                with lc1:
                    if song.get("thumbnail"):
                        st.image(song["thumbnail"], width=60)
                with lc2:
                    st.markdown(f"<div style='color:white; font-weight:600;'>{song['title']}</div>"
                                f"<div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>{song['artist']}</div>",
                                unsafe_allow_html=True)
                with lc3:
                    if st.button("▶", key=f"lib_play_{song['video_id']}", use_container_width=True):
                        st.session_state.now_playing_id     = song["video_id"]
                        st.session_state.now_playing_title  = song["title"]
                        st.session_state.now_playing_artist = song["artist"]
                        st.session_state.now_playing_thumb  = song.get("thumbnail", "")
                        st.rerun()
                with lc4:
                    if st.button("🗑", key=f"lib_del_{song['video_id']}", use_container_width=True):
                        unlike_song(st.session_state.user, song["video_id"])
                        st.rerun()
                st.markdown("<hr style='border-color:rgba(255,255,255,0.06); margin:4px 0;'>", unsafe_allow_html=True)

        # Like currently playing
        if st.session_state.now_playing_id:
            st.markdown("---")
            if st.button(f"❤️ Like current: {st.session_state.now_playing_title[:40]}", use_container_width=True, key="like_current"):
                like_song(
                    st.session_state.user,
                    st.session_state.now_playing_id,
                    st.session_state.now_playing_title,
                    st.session_state.now_playing_artist,
                    st.session_state.now_playing_thumb
                )
                st.success("❤️ Liked!")
                st.rerun()

    # ══ PLAYLISTS TAB ═════════════════════════════════════════════════════════
    with music_tabs[3]:
        playlists = get_playlists(st.session_state.user)
        pl_left, pl_right = st.columns([1, 2])

        with pl_left:
            st.markdown("<h4 style='color:#7b2fff;'>Your Playlists</h4>", unsafe_allow_html=True)
            new_pl_name = st.text_input("New playlist name", placeholder="e.g. Chill Vibes", key="new_pl_input")
            if st.button("➕ Create Playlist", use_container_width=True, key="create_pl"):
                if new_pl_name.strip():
                    save_playlist(st.session_state.user, new_pl_name.strip(), [])
                    st.success(f"Playlist {new_pl_name} created!")
                    st.rerun()

            st.markdown("---")
            for pl in playlists:
                pcol1, pcol2 = st.columns([3, 1])
                with pcol1:
                    if st.button(f"📀 {pl['name']}", key=f"open_pl_{pl['name']}", use_container_width=True):
                        st.session_state.active_playlist_name = pl["name"]
                        st.rerun()
                with pcol2:
                    if st.button("🗑", key=f"del_pl_{pl['name']}", use_container_width=True):
                        delete_playlist(st.session_state.user, pl["name"])
                        if st.session_state.active_playlist_name == pl["name"]:
                            st.session_state.active_playlist_name = None
                        st.rerun()

        with pl_right:
            active_pl = st.session_state.active_playlist_name
            if active_pl:
                pl_data = next((p for p in playlists if p["name"] == active_pl), None)
                if pl_data:
                    songs = pl_data.get("songs", [])
                    st.markdown(f"<h4 style='color:#00d4ff;'>📀 {active_pl} ({len(songs)} tracks)</h4>", unsafe_allow_html=True)

                    # Add currently playing to playlist
                    if st.session_state.now_playing_id:
                        if st.button(f"➕ Add playing track to this playlist", use_container_width=True, key="add_to_pl"):
                            new_song = {
                                "id": st.session_state.now_playing_id,
                                "title": st.session_state.now_playing_title,
                                "artist": st.session_state.now_playing_artist,
                                "thumb": st.session_state.now_playing_thumb
                            }
                            if not any(s["id"] == new_song["id"] for s in songs):
                                songs.append(new_song)
                                save_playlist(st.session_state.user, active_pl, songs)
                                st.success("✅ Added!")
                                st.rerun()
                            else:
                                st.info("Already in playlist.")

                    if not songs:
                        st.markdown("<p style='color:rgba(255,255,255,0.4);'>Empty playlist. Play a track and add it here.</p>", unsafe_allow_html=True)
                    else:
                        # Play all button
                        if st.button("▶ Play All", use_container_width=True, key="play_all_pl"):
                            st.session_state.now_playing_id     = songs[0]["id"]
                            st.session_state.now_playing_title  = songs[0]["title"]
                            st.session_state.now_playing_artist = songs[0].get("artist", "")
                            st.session_state.now_playing_thumb  = songs[0].get("thumb", "")
                            st.session_state.queue = songs[1:]
                            st.rerun()

                        for i, s in enumerate(songs):
                            sc1, sc2, sc3, sc4 = st.columns([1, 4, 1, 1])
                            with sc1:
                                if s.get("thumb"):
                                    st.image(s["thumb"], width=50)
                            with sc2:
                                st.markdown(f"<div style='color:white;'>{s['title']}</div>"
                                            f"<div style='color:rgba(255,255,255,0.4); font-size:0.78rem;'>{s.get('artist','')}</div>",
                                            unsafe_allow_html=True)
                            with sc3:
                                if st.button("▶", key=f"pl_play_{i}", use_container_width=True):
                                    st.session_state.now_playing_id     = s["id"]
                                    st.session_state.now_playing_title  = s["title"]
                                    st.session_state.now_playing_artist = s.get("artist", "")
                                    st.session_state.now_playing_thumb  = s.get("thumb", "")
                                    st.session_state.queue = songs[i+1:]
                                    st.rerun()
                            with sc4:
                                if st.button("✕", key=f"pl_rm_{i}", use_container_width=True):
                                    songs.pop(i)
                                    save_playlist(st.session_state.user, active_pl, songs)
                                    st.rerun()
                            st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin:3px 0;'>", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='text-align:center; padding:60px; color:rgba(255,255,255,0.3);'>
                    <div style='font-size:3rem;'>📀</div>
                    <p>Select a playlist on the left to view its tracks</p>
                </div>""", unsafe_allow_html=True)

    # ══ JAM TAB ═══════════════════════════════════════════════════════════════
    with music_tabs[4]:
        st.markdown("<h4 style='color:#ff4444;'>🎵 Music Jam — Listen Together</h4>", unsafe_allow_html=True)
        st.markdown("<p style='color:rgba(255,255,255,0.5);'>Share what you're playing with a friend in real time. They'll get a notification in Messages.</p>", unsafe_allow_html=True)

        if st.session_state.now_playing_id:
            st.markdown(f"""
            <div style='background:rgba(255,68,68,0.1); border:1px solid rgba(255,68,68,0.3);
            border-radius:12px; padding:16px; margin-bottom:16px;'>
                <div style='color:#ff4444; font-weight:700;'>🎵 Now Playing</div>
                <div style='color:white; margin-top:6px;'>{st.session_state.now_playing_title}</div>
                <div style='color:rgba(255,255,255,0.5); font-size:0.8rem;'>{st.session_state.now_playing_artist}</div>
            </div>""", unsafe_allow_html=True)

            my_friends = get_user(st.session_state.user)
            friends_to_jam = my_friends.get("friends", []) if my_friends else []
            if not friends_to_jam:
                st.info("Add friends first to jam with them.")
            else:
                st.markdown("<p style='color:rgba(255,255,255,0.6);'>Share jam with:</p>", unsafe_allow_html=True)
                jam_cols = st.columns(min(len(friends_to_jam), 4))
                for ji, f in enumerate(friends_to_jam):
                    with jam_cols[ji % 4]:
                        if st.button(f"🎵 Jam with {f}", use_container_width=True, key=f"jam_{f}"):
                            send_jam(
                                st.session_state.user, f,
                                st.session_state.now_playing_id,
                                st.session_state.now_playing_title,
                                st.session_state.now_playing_thumb
                            )
                            st.success(f"✅ Jam invite sent to {f}! They will see it in Messages.")
        else:
            st.markdown("""
            <div style='text-align:center; padding:60px; color:rgba(255,255,255,0.3);'>
                <div style='font-size:3rem;'>🎵</div>
                <p>Play a song first, then come here to jam with friends</p>
            </div>""", unsafe_allow_html=True)

        # Incoming jam check
        inc_jam = get_jam(st.session_state.user)
        if inc_jam:
            st.markdown("---")
            st.markdown(f"<h5 style='color:#00ff88;'>📨 {inc_jam['host']} invited you to jam!</h5>", unsafe_allow_html=True)
            if st.button(f"Play: {inc_jam['title']}", use_container_width=True, key="join_jam_music"):
                st.session_state.now_playing_id     = inc_jam["video_id"]
                st.session_state.now_playing_title  = inc_jam["title"]
                st.session_state.now_playing_thumb  = inc_jam["thumbnail"]
                st.session_state.now_playing_artist = inc_jam["host"]
                st.rerun()

    # ══ QUEUE TAB ═════════════════════════════════════════════════════════════
    with music_tabs[5]:
        st.markdown("<h4 style='color:#ffa500;'>📋 Queue</h4>", unsafe_allow_html=True)
        if not st.session_state.queue:
            st.markdown("<p style='color:rgba(255,255,255,0.4);'>Your queue is empty. Hit + Queue on any track.</p>", unsafe_allow_html=True)
        else:
            for qi, track in enumerate(st.session_state.queue):
                qc1, qc2, qc3, qc4 = st.columns([1, 4, 1, 1])
                with qc1:
                    st.markdown(f"<div style='color:rgba(255,255,255,0.3); text-align:center; padding-top:10px;'>{qi+1}</div>", unsafe_allow_html=True)
                    if track.get("thumb"):
                        st.image(track["thumb"], width=50)
                with qc2:
                    st.markdown(f"<div style='color:white;'>{track['title']}</div>"
                                f"<div style='color:rgba(255,255,255,0.4); font-size:0.78rem;'>{track.get('artist','')}</div>",
                                unsafe_allow_html=True)
                with qc3:
                    if st.button("▶ Play Now", key=f"q_play_{qi}", use_container_width=True):
                        st.session_state.now_playing_id     = track["id"]
                        st.session_state.now_playing_title  = track["title"]
                        st.session_state.now_playing_artist = track.get("artist", "")
                        st.session_state.now_playing_thumb  = track.get("thumb", "")
                        st.session_state.queue.pop(qi)
                        st.rerun()
                with qc4:
                    if st.button("✕", key=f"q_rm_{qi}", use_container_width=True):
                        st.session_state.queue.pop(qi)
                        st.rerun()
                st.markdown("<hr style='border-color:rgba(255,255,255,0.06); margin:3px 0;'>", unsafe_allow_html=True)

            if st.button("🗑 Clear Queue", key="clear_queue"):
                st.session_state.queue = []
                st.rerun()

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
