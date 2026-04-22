import streamlit as st
from groq import Groq  # <-- New Import
import json
import os
import time
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="ai by sreenand", page_icon="🤖", layout="wide")

st.markdown("<style>.stAppDeployButton { display: none !important; }</style>", unsafe_allow_html=True)

# --- 2. DATABASE HELPERS ---
DB_FILE = "users.json"


def load_users():
    if not os.path.exists(DB_FILE): return {"admin": "admin123"}
    with open(DB_FILE, "r") as f: return json.load(f)


def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(DB_FILE, "w") as f: json.dump(users, f)


# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"New Chat": []}
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "New Chat"
if "request_timestamps" not in st.session_state:
    st.session_state.request_timestamps = []
if "processing" not in st.session_state:
    st.session_state.processing = False


# --- 4. RPM LIMITER (Groq allows 30 RPM for free) ---
def check_rpm_limit(limit=30):
    current_time = time.time()
    st.session_state.request_timestamps = [t for t in st.session_state.request_timestamps if current_time - t < 60]
    return len(st.session_state.request_timestamps) < limit


# --- 5. LOGIN SYSTEM --- (No changes needed)
if not st.session_state.logged_in:
    st.title("🎉Lakshmeeyam ai Login🎈")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Log In"):
            db = load_users()
            if u in db and db[u] == p:
                st.session_state.logged_in, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("Invalid credentials")
    with tab2:
        nu = st.text_input("New Username", key="reg_u")
        np = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Create Account"):
            if nu and np:
                save_user(nu, np)
                st.success("Account created!")
            else:
                st.error("Fill all fields")
    st.stop()

# --- 6. SIDEBAR ---
with st.sidebar:
    st.title("Groq Cloud")
    if st.button("➕ New Chat", use_container_width=True, disabled=st.session_state.processing):
        temp_name = f"New Chat {datetime.now().strftime('%H%M%S')}"
        st.session_state.all_chats[temp_name] = []
        st.session_state.active_chat = temp_name
        st.rerun()

    st.write("---")
    st.subheader("Recent")
    for chat_title in reversed(list(st.session_state.all_chats.keys())):
        if st.button(f"💬 {chat_title}", key=chat_title, use_container_width=True, disabled=st.session_state.processing):
            st.session_state.active_chat = chat_title
            st.rerun()

# --- 7. GROQ CONFIG ---
# Get your key at https://console.groq.com/keys
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Llama 3.1 8B is the best for high daily limits (14,400 RPD)
MODEL_NAME = "llama-3.1-8b-instant"

messages = st.session_state.all_chats[st.session_state.active_chat]
st.header(st.session_state.active_chat)

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 8. CHAT INPUT & LOCKING ---
prompt = st.chat_input(
    "Ask anything..." if not st.session_state.processing else "Groq is processing...",
    disabled=st.session_state.processing
)

if prompt:
    if not check_rpm_limit(30):
        st.error("🚦 Rate Limit Reached! Wait a minute.")
    else:
        st.session_state.processing = True
        messages.append({"role": "user", "content": prompt})
        st.session_state.request_timestamps.append(time.time())
        st.rerun()

if st.session_state.processing and messages and messages[-1]["role"] == "user":
    user_query = messages[-1]["content"]

    # 1. Auto-Naming
    if len(messages) == 1:
        try:
            t_res = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": f"Summarize into 2 words: '{user_query}'"}]
            )
            new_title = t_res.choices[0].message.content.strip().replace('"', '')[:30]
            st.session_state.all_chats[new_title] = st.session_state.all_chats.pop(st.session_state.active_chat)
            st.session_state.active_chat = new_title
        except:
            pass

    # 2. Get AI Response
    with st.chat_message("assistant"):
        with st.spinner("⚡ Lightning fast thinking..."):
            try:
                # Groq uses standard message list format
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                )
                full_text = response.choices[0].message.content
                messages.append({"role": "assistant", "content": full_text})

                st.session_state.processing = False
                st.rerun()
            except Exception as e:
                st.error(f"Groq Error: {e}")
                st.session_state.processing = False