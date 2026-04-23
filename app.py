import streamlit as st
from groq import Groq
import json
import os
import time
from datetime import datetime
import requests

# --- 1. PAGE CONFIG & FUTURISTIC STYLING ---
st.set_page_config(page_title="Lakshmeeyam AI", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&q=80&w=2072");
        background-size: cover;
    }
    .main-box {
        background-color: rgba(0, 0, 0, 0.85);
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        color: white;
        margin-bottom: 20px;
        box-shadow: 0px 0px 15px rgba(0, 212, 255, 0.3);
    }
    .stAppDeployButton { display: none !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 5px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE HELPERS ---
USERS_FILE = "users.json"
CHATS_FILE = "ai_chats.json"
MESSAGES_FILE = "user_messages.json"

def load_data(file, default):
    if not os.path.exists(file):
        with open(file, "w") as f: json.dump(default, f)
        return default
    with open(file, "r") as f:
        try: return json.load(f)
        except: return default

def save_data(file, data):
    with open(file, "w") as f: json.dump(data, f)

db_users = load_data(USERS_FILE, {})
db_chats = load_data(CHATS_FILE, {})
db_messages = load_data(MESSAGES_FILE, {})

# --- 3. PERSISTENT LOGIN LOGIC ---
# This checks the URL for a 'user' parameter to keep you logged in on refresh
if "logged_in" not in st.session_state:
    if "user" in st.query_params:
        st.session_state.logged_in = True
        st.session_state.user = st.query_params["user"]
    else:
        st.session_state.logged_in = False

if "user" not in st.session_state: st.session_state.user = None
if "current_page" not in st.session_state: st.session_state.current_page = "Dashboard"
if "active_chat" not in st.session_state: st.session_state.active_chat = "New Chat"
if "processing" not in st.session_state: st.session_state.processing = False

# --- 4. LOGIN SYSTEM ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #00d4ff;'>🚀 LAKSHMEEYAM AI</h1>", unsafe_allow_html=True)
    col_l, _, col_r = st.columns([1.5, 0.1, 1])
    with col_l:
        st.markdown("""
        <div class='main-box'>
            <h2 style='color: #00d4ff;'>👨‍💻 About the Creator</h2>
            <p><b>Lakshmeeyam AI</b> is a digital ecosystem built by <b>Sreenand-P</b>.</p>
            <p>At 14 years old, Sreenand created this platform as a hobby to integrate AI tools with a social network.</p>
            <hr style='border-color: #333;'>
            <ul>
                <li><b>Custom AI:</b> Powered by Grok Llama 3.1</li>
                <li><b>Auto-Save:</b> Stays logged in via URL parameters</li>
                <li><b>Friend System:</b> Messaging in real-time</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        st.subheader("🔐 Access Portal")
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            u_in = st.text_input("Username")
            p_in = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                if u_in in db_users and db_users[u_in]["password"] == p_in:
                    st.session_state.logged_in = True
                    st.session_state.user = u_in
                    st.query_params["user"] = u_in # Save to URL
                    if u_in not in db_chats: db_chats[u_in] = {"New Chat": []}
                    save_data(CHATS_FILE, db_chats)
                    st.rerun()
                else: st.error("❌ Invalid Username or Password")
        with t2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                if nu and np and nu not in db_users:
                    db_users[nu] = {"password": np, "friends": [], "requests": []}
                    save_data(USERS_FILE, db_users)
                    st.success("Account Ready!")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00d4ff;'>Welcome, {st.session_state.user}</h2>", unsafe_allow_html=True)
    if st.button("🏠 Dashboard", use_container_width=True): st.session_state.current_page = "Dashboard"
    if st.button("🤖 AI Lab", use_container_width=True): st.session_state.current_page = "AI Chat"
    if st.button("💬 Messaging", use_container_width=True): st.session_state.current_page = "Messages"
    if st.button("🌤️ Weather", use_container_width=True): st.session_state.current_page = "Weather"
    st.write("---")
    
    if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
        st.session_state.logged_in = False
        st.query_params.clear() # Clear URL parameter
        st.rerun()

# --- 6. PAGES ---

# DASHBOARD
if st.session_state.current_page == "Dashboard":
    st.title("📱 Tech Dashboard")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='main-box'><h3>🤖 AI Lab</h3><p>Chat with Groq Llama</p></div>", unsafe_allow_html=True)
        if st.button("Open AI", use_container_width=True, key="dash_ai"): 
            st.session_state.current_page = "AI Chat"; st.rerun()
    with c2:
        st.markdown("<div class='main-box'><h3>💬 Messaging</h3><p>Inbox & Chat</p></div>", unsafe_allow_html=True)
        if st.button("Open Messages", use_container_width=True, key="dash_msg"): 
            st.session_state.current_page = "Messages"; st.rerun()
    with c3:
        st.markdown("<div class='main-box'><h3>🌤️ SkyView</h3><p>Live Weather</p></div>", unsafe_allow_html=True)
        if st.button("Open Weather", use_container_width=True, key="dash_weather"): 
            st.session_state.current_page = "Weather"; st.rerun()

# AI CHAT
elif st.session_state.current_page == "AI Chat":
    st.title("🤖 AI Lab")
    client = Groq(api_key="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")
    
    if st.session_state.user not in db_chats:
        db_chats[st.session_state.user] = {"New Chat": []}
    
    my_h = db_chats[st.session_state.user]
    
    with st.sidebar:
        st.write("---")
        if st.button("➕ New Session", use_container_width=True, key="chat_new_session"):
            st.session_state.active_chat = "New Chat"
            my_h["New Chat"] = []
            save_data(CHATS_FILE, db_chats)
            st.rerun()
            
        st.write("#### History")
        for t in reversed(list(my_h.keys())):
            if st.button(f"💬 {t}", use_container_width=True, key=f"hist_{t}"):
                st.session_state.active_chat = t
                st.rerun()

    msgs = my_h.get(st.session_state.active_chat, [])
    for m in msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    p = st.chat_input("Ask Lakshmeeyam AI anything...")
    if p:
        st.session_state.processing = True
        msgs.append({"role": "user", "content": p})
        my_h[st.session_state.active_chat] = msgs
        save_data(CHATS_FILE, db_chats)
        st.rerun()

    if st.session_state.processing:
        with st.chat_message("assistant"):
            sys = {"role": "system", "content": "You are Lakshmeeyam AI, created by Sreenand. Be helpful and smart."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[sys] + msgs)
            ans = res.choices[0].message.content
            msgs.append({"role": "assistant", "content": ans})
            
            # RENAME LOGIC
            if st.session_state.active_chat == "New Chat" and len(msgs) >= 2:
                rename_req = [{"role": "system", "content": "Title this topic in 2 words. No dots."}, {"role": "user", "content": msgs[0]['content']}]
                try:
                    rn_res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=rename_req)
                    new_title = rn_res.choices[0].message.content.strip()
                    if new_title in my_h: new_title += f" ({datetime.now().strftime('%H:%M')})"
                    my_h[new_title] = my_h.pop("New Chat")
                    st.session_state.active_chat = new_title
                except: pass
            
            save_data(CHATS_FILE, db_chats)
            st.session_state.processing = False
            st.rerun()

# MESSAGING
elif st.session_state.current_page == "Messages":
    st.title("📫 Communication Center")
    t_chat, t_inbox = st.tabs(["💬 DM", "📥 Inbox & Requests"])
    u_data = db_users.get(st.session_state.user, {})

    with t_inbox:
        st.subheader("Add Friend")
        target = st.text_input("Enter Username")
        if st.button("Send Friend Request"):
            if target in db_users and target != st.session_state.user:
                if st.session_state.user not in db_users[target].get("requests", []):
                    db_users[target].setdefault("requests", []).append(st.session_state.user)
                    save_data(USERS_FILE, db_users)
                    st.success(f"Request sent to {target}!")
            else: st.error("User not found.")
        
        st.write("---")
        for r in u_data.get("requests", []):
            cl, ca, cd = st.columns([2, 1, 1])
            cl.write(f"**{r}** wants to be friends.")
            if ca.button("Accept", key=f"acc_{r}"):
                u_data.setdefault("friends", []).append(r)
                db_users[r].setdefault("friends", []).append(st.session_state.user)
                u_data["requests"].remove(r)
                save_data(USERS_FILE, db_users); st.rerun()
            if cd.button("Decline", key=f"dec_{r}"):
                u_data["requests"].remove(r); save_data(USERS_FILE, db_users); st.rerun()

    with t_chat:
        friends = u_data.get("friends", [])
        if not friends: st.info("No friends yet.")
        else:
            fl, cl = st.columns([1, 2])
            with fl:
                for f in friends:
                    if st.button(f"👤 {f}", use_container_width=True, key=f"friend_btn_{f}"): 
                        st.session_state.msg_target = f
            with cl:
                dest = st.session_state.get("msg_target")
                if dest:
                    cid = "_".join(sorted([st.session_state.user, dest]))
                    if cid not in db_messages: db_messages[cid] = []
                    for m in db_messages[cid]:
                        role = "user" if m["sender"] == st.session_state.user else "assistant"
                        with st.chat_message(role): st.write(f"**{m['sender']}**: {m['text']}")
                    txt = st.chat_input(f"Send to {dest}...")
                    if txt:
                        db_messages[cid].append({"sender": st.session_state.user, "text": txt})
                        save_data(MESSAGES_FILE, db_messages); st.rerun()

# WEATHER
elif st.session_state.current_page == "Weather":
    st.title("🌤️ SkyView Weather not ready")
    loc = st.text_input("Enter City:", "")
    if st.button("Get Weather", key="btn_get_weather"):
        try:
            g = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={loc}&count=1").json()
            if "results" in g:
                r = g["results"][0]
                w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={r['latitude']}&longitude={r['longitude']}&current_weather=true").json()
                curr = w["current_weather"]
                st.success(f"Weather for {loc.title()}")
                w1, w2 = st.columns(2)
                w1.metric("Temperature", f"{curr['temperature']}°C")
                w2.metric("Wind Speed", f"{curr['windspeed']} km/h")
        except: st.error("Error connecting to weather service.")
