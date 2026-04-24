import streamlit as st
from groq import Groq
import json
import secrets
from datetime import datetime
import requests
import hashlib
from supabase import create_client, Client

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

# --- 2. DATABASE HELPERS (SUPABASE) ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def get_user(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    return res.data[0] if res.data else None

def save_user(username, data):
    supabase.table("users").upsert({
        "username": username,
        "password": data["password"],
        "token": data.get("token", ""),
        "friends": data.get("friends", []),
        "requests": data.get("requests", [])
    }).execute()

# --- 3. PERSISTENT LOGIN LOGIC ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    url_token = st.query_params.get("token")
    if url_token:
        res = supabase.table("users").select("*").eq("token", url_token).execute()
        if res.data:
            st.session_state.logged_in = True
            st.session_state.user = res.data[0]["username"]

if "current_page" not in st.session_state: st.session_state.current_page = "home"
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
                <li><b>Custom AI:</b> Powered by Groq Llama 3.1</li>
                <li><b>Cloud Storage:</b> Powered by Supabase DB</li>
                <li><b>Friend System:</b> Messaging in real-time</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='main-box'>", unsafe_allow_html=True)
        st.subheader("🔐 Access")
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            u_in = st.text_input("Username")
            p_in = st.text_input("Password", type="password")
            if st.button("Log In", use_container_width=True):
                user_data = get_user(u_in)
                if user_data:
                    if user_data["password"] == p_in or user_data["password"] == hash_password(p_in):
                        new_token = secrets.token_hex(16)
                        user_data["token"] = new_token
                        save_user(u_in, user_data)
                        st.session_state.logged_in = True
                        st.session_state.user = u_in
                        st.query_params["token"] = new_token
                        st.rerun()
                st.error("❌ Invalid Username or Password")
        with t2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("Create Account", use_container_width=True):
                if nu and np and not get_user(nu):
                    new_user = {"password": hash_password(np), "friends": [], "requests": [], "token": ""}
                    save_user(nu, new_user)
                    st.success("Account Ready! Please Login.")
                else: st.error("User exists or fields empty.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00d4ff;'>Welcome, {st.session_state.user}</h2>", unsafe_allow_html=True)
    if st.button("🏠 home", use_container_width=True): 
        st.session_state.current_page = "home"
        st.rerun()
    if st.button("🤖 AI", use_container_width=True): 
        st.session_state.current_page = "AI Chat"
        st.rerun()
    if st.button("💬 Messaging", use_container_width=True): 
        st.session_state.current_page = "Messages"
        st.rerun()
    if st.button("🌤️ Weather", use_container_width=True): 
        st.session_state.current_page = "Weather"
        st.rerun()
    st.write("---")
    if st.button("🔐 Logout", use_container_width=True):
        user_data = get_user(st.session_state.user)
        if user_data:
            user_data["token"] = ""
            save_user(st.session_state.user, user_data)
        st.session_state.logged_in = False
        st.query_params.clear()
        st.rerun()

# --- 6. PAGES ---

if st.session_state.current_page == "home":
    st.title("🏠 home")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='main-box'><h3>🤖 AI Lab</h3><p>Chat with Llama 3.1</p></div>", unsafe_allow_html=True)
        if st.button("Open AI", use_container_width=True): st.session_state.current_page = "AI Chat"; st.rerun()
    with c2:
        st.markdown("<div class='main-box'><h3>💬 Messaging</h3><p>Inbox & Chat</p></div>", unsafe_allow_html=True)
        if st.button("Open Messages", use_container_width=True): st.session_state.current_page = "Messages"; st.rerun()
    with c3:
        st.markdown("<div class='main-box'><h3>🌤️ SkyView</h3><p>Live Weather</p></div>", unsafe_allow_html=True)
        if st.button("Open Weather", use_container_width=True): st.session_state.current_page = "Weather"; st.rerun()

elif st.session_state.current_page == "AI Chat":
    st.title("🤖 Lakshmeeyam AI")
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    
    # Load history from Supabase
    chat_res = supabase.table("ai_chats").select("*").eq("username", st.session_state.user).execute()
    user_history = {row['chat_title']: row['messages'] for row in chat_res.data} if chat_res.data else {"New Chat": []}

    with st.sidebar:
        st.write("---")
        if st.button("➕ New Session", use_container_width=True):
            st.session_state.active_chat = "New Chat"
            st.rerun()
        st.write("#### History")
        for title in reversed(list(user_history.keys())):
            if st.button(f"💬 {title}", use_container_width=True):
                st.session_state.active_chat = title
                st.rerun()

    current_msgs = user_history.get(st.session_state.active_chat, [])
    for m in current_msgs:
        with st.chat_message(m["role"]): st.write(m["content"])

    p = st.chat_input("Ask AI...")
    if p:
        current_msgs.append({"role": "user", "content": p})
        st.session_state.processing = True
        # Save immediately
        supabase.table("ai_chats").upsert({"username": st.session_state.user, "chat_title": st.session_state.active_chat, "messages": current_msgs}, on_conflict="username,chat_title").execute()
        st.rerun()

    if st.session_state.processing:
        with st.chat_message("assistant"):
            sys = {"role": "system", "content": "You are Lakshmeeyam AI, created by Sreenand. Be helpful."}
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[sys] + current_msgs)
            ans = res.choices[0].message.content
            current_msgs.append({"role": "assistant", "content": ans})
            
            # Title handling
            active_title = st.session_state.active_chat
            if active_title == "New Chat" and len(current_msgs) >= 2:
                rn_res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": "Title this in 2 words."}, {"role": "user", "content": current_msgs[0]['content']}])
                active_title = rn_res.choices[0].message.content.strip()
                # Delete old "New Chat" entry and save new one
                supabase.table("ai_chats").delete().eq("username", st.session_state.user).eq("chat_title", "New Chat").execute()
                st.session_state.active_chat = active_title

            supabase.table("ai_chats").upsert({"username": st.session_state.user, "chat_title": active_title, "messages": current_msgs}, on_conflict="username,chat_title").execute()
            st.session_state.processing = False
            st.rerun()

elif st.session_state.current_page == "Messages":
    st.title("📫 Communication")
    t_chat, t_inbox = st.tabs(["💬 DM", "📥 Inbox & Requests"])
    u_data = get_user(st.session_state.user)

    with t_inbox:
        st.subheader("Add Friend")
        target = st.text_input("Enter Username")
        if st.button("Send Request"):
            target_data = get_user(target)
            if target_data and target != st.session_state.user:
                reqs = target_data.get("requests", [])
                if st.session_state.user not in reqs:
                    reqs.append(st.session_state.user)
                    target_data["requests"] = reqs
                    save_user(target, target_data)
                    st.success("Sent!")
            else: st.error("User not found.")
        
        st.write("---")
        for r in u_data.get("requests", []):
            cl, ca, cd = st.columns([2, 1, 1])
            cl.write(f"**{r}** wants to be friends.")
            if ca.button("Accept", key=f"acc_{r}"):
                u_data["friends"].append(r)
                u_data["requests"].remove(r)
                save_user(st.session_state.user, u_data)
                r_data = get_user(r)
                r_data["friends"].append(st.session_state.user)
                save_user(r, r_data)
                st.rerun()
            if cd.button("Decline", key=f"dec_{r}"):
                u_data["requests"].remove(r)
                save_user(st.session_state.user, u_data)
                st.rerun()

    with t_chat:
        friends = u_data.get("friends", [])
        if not friends: st.info("No friends yet.")
        else:
            fl, cl = st.columns([1, 2])
            with fl:
                for f in friends:
                    if st.button(f"👤 {f}", use_container_width=True): st.session_state.msg_target = f
            with cl:
                dest = st.session_state.get("msg_target")
                if dest:
                    cid = "_".join(sorted([st.session_state.user, dest]))
                    res = supabase.table("user_messages").select("*").eq("chat_id", cid).order("created_at").execute()
                    for m in res.data:
                        role = "user" if m["sender"] == st.session_state.user else "assistant"
                        with st.chat_message(role): st.write(f"**{m['sender']}**: {m['text']}")
                    
                    txt = st.chat_input(f"Message {dest}...")
                    if txt:
                        supabase.table("user_messages").insert({"chat_id": cid, "sender": st.session_state.user, "text": txt}).execute()
                        st.rerun()

elif st.session_state.current_page == "Weather":
    st.title("🌤️ SkyView Weather")
    loc = st.text_input("Enter City:")
    if st.button("Get Weather"):
        try:
            g = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={loc}&count=1").json()
            if "results" in g:
                r = g["results"][0]
                w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={r['latitude']}&longitude={r['longitude']}&current_weather=true").json()
                curr = w["current_weather"]
                w1, w2 = st.columns(2)
                w1.metric("Temperature", f"{curr['temperature']}°C")
                w2.metric("Wind Speed", f"{curr['windspeed']} km/h")
        except: st.error("Connection error.")
