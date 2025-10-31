import streamlit as st
import google.generativeai as genai

# ---- Setup ----
genai.configure(api_key="AIzaSyB_NDGAwjqsq5TcEznWv7Jip0N-ML3rXnQ")
model = genai.GenerativeModel("models/gemini-2.5-flash")


st.title("🤖 Career Buddy Chatbot")

# Keep chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
user_input = st.chat_input("Ask me anything about careers, jobs, or learning or anything...")

if user_input:
    # Append user message
    st.session_state.chat_history.append(("🧑 You", user_input))

    with st.spinner("Thinking..."):
        # Use chat mode instead of single-shot
        response = model.generate_content(
            user_input,
            generation_config={"temperature": 0.8}  # make it more fun/creative
        )
        bot_reply = response.text

    # Append bot reply
    st.session_state.chat_history.append(("🤖 CareerBot", bot_reply))

# Show conversation
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
