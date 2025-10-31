import streamlit as st
import os, json, time, random, threading
from utils.supabase_client import supabase
from utils.ui_helpers import show_loading_quotes, stop_loading_quotes
from google import generativeai as genai

# --- Configure Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Page title ---
st.title("💬 Career Chatbot Advisor")

# --- Initialize session ---
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "user" not in st.session_state:
    st.session_state["user"] = {"id": None, "email": "anonymous@demo.app"}

resume = st.session_state.get("current_resume", {})

# --- User input ---
user_query = st.chat_input("Ask about careers, roles, or your profile...")

if user_query:
    # --- Show user message ---
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state["chat_history"].append({"role": "user", "text": user_query})

    # --- Show assistant placeholder ---
    with st.chat_message("assistant"):
        msg_placeholder = st.empty()

        # --- Loading spinner + quotes ---
        stop_flag, t, ph, spinner = show_loading_quotes("💭 Thinking deeply about your question...")

        try:
            prompt = f"""
            You are a career assistant. Use the candidate's resume data to answer the user's question helpfully and accurately.

            Resume JSON:
            {json.dumps(resume)}

            User Question:
            {user_query}

            Answer in a friendly, structured conversational tone.
            """
            response = model.generate_content(prompt)
            reply_text = response.text.strip()
        except Exception as e:
            reply_text = f"⚠️ Error: {e}"
        finally:
            stop_loading_quotes(stop_flag, t, ph, spinner)

        # --- Typing animation ---
        final_display = ""
        for ch in reply_text:
            final_display += ch
            msg_placeholder.markdown(final_display)
            time.sleep(0.012)

    # --- Save chat to DB ---
    st.session_state["chat_history"].append({"role": "assistant", "text": reply_text})
    try:
        user_id = st.session_state["user"].get("id")
        supabase.table("chat_history").insert({
            "user_id": user_id,
            "role": "user",
            "message": user_query
        }).execute()
        supabase.table("chat_history").insert({
            "user_id": user_id,
            "role": "assistant",
            "message": reply_text
        }).execute()
    except Exception as e:
        st.warning(f"⚠️ Could not save chat: {e}")

# --- Show previous chat history ---
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])
