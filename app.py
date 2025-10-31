import streamlit as st
from dotenv import load_dotenv
load_dotenv()
import time, threading, random
from utils.supabase_client import supabase


# --- Initialize user session ---
if "user" not in st.session_state:
    st.session_state["user"] = {
        "id": "00000000-0000-0000-0000-000000000001",
        "email": "testuser@example.com"
    }

user_id = st.session_state["user"].get("id")

# --- Fetch latest resume safely ---
try:
    query = supabase.table('resumes').select('*')
    if user_id and user_id != "None":
        query = query.eq('user_id', user_id)
    resp = query.order('created_at', desc=True).limit(1).execute()
    if resp.data:
        st.session_state['current_resume'] = resp.data[0]['parsed_json']
        st.session_state['current_resume_id'] = resp.data[0]['id']
except Exception as e:
    st.warning(f"⚠️ Could not fetch resume: {e}")

# --- Page UI ---
st.title("🏠 Welcome to the Career Coach App!")
st.subheader("🚀 Your Personal AI Career Companion")

st.markdown("""
This platform helps you **analyze your resume**, practice **mock interviews**, 
and chat with your **AI mentor** — all in one place! 💬💼  

But before you dive in — let’s have some fun! 🎮
""")

# --- Rotating motivational quotes ---
QUOTES = [
    "🌱 Every expert was once a beginner.",
    "🎯 Patience is power — magic happens while you wait.",
    "💡 Great things take time, stay curious!",
    "🔥 Your career story is being written — one skill at a time.",
    "🌎 AI is learning from you, too 😉",
    "🚀 Keep experimenting. Every click teaches the app something new!"
]
placeholder = st.empty()
stop_flag = {"value": False}

def rotate_quotes():
    i = 0
    while not stop_flag["value"]:
        quote = QUOTES[i % len(QUOTES)]
        placeholder.markdown(
            f"<div style='text-align:center;font-style:italic;color:#888;'>{quote}</div>",
            unsafe_allow_html=True
        )
        time.sleep(5)
        i += 1

t = threading.Thread(target=rotate_quotes)
t.start()

st.markdown("---")

# --- Game Selector ---
game_choice = st.selectbox(
    "🎮 Choose a Fun Mini-Game to Play:",
    ["💭 Spin the Wheel", "🎲 Rock, Paper, Scissors"]
)

st.markdown("---")

# --- Game 1: Spin the Wheel ---
if game_choice == "💭 Spin the Wheel":
    st.subheader("💫 Spin the Career Fortune Wheel!")
    fortunes = [
        "🎯 Focus on building one new skill this week!",
        "🚀 Apply to at least one internship today — progress > perfection!",
        "💡 Revisit an old project — you’ll see how far you’ve grown.",
        "🔥 Teach someone a skill you learned — it cements your knowledge.",
        "🌟 Network with 1 new professional on LinkedIn today!",
        "📚 Spend 30 mins learning something completely new — curiosity fuels creativity."
    ]
    if st.button("🎡 Spin the Wheel"):
        with st.spinner("Spinning the wheel... 🎠"):
            time.sleep(2)
        st.success(random.choice(fortunes))

# --- Game 2: Rock Paper Scissors ---
elif game_choice == "🎲 Rock, Paper, Scissors":
    st.subheader("🎯 Play Rock, Paper, Scissors — AI Edition")
    choices = ["🪨 Rock", "📄 Paper", "✂️ Scissors"]
    user_choice = st.radio("Pick your move:", choices, horizontal=True)
    ai_choice = random.choice(choices)

    if st.button("Play with AI 🤖"):
        st.write("🤖 Thinking...")
        time.sleep(1)
        st.success(f"AI chose: **{ai_choice}**")

        # Determine outcome
        if user_choice == ai_choice:
            result = "🤝 It's a tie!"
        elif (
            (user_choice == "🪨 Rock" and ai_choice == "✂️ Scissors") or
            (user_choice == "📄 Paper" and ai_choice == "🪨 Rock") or
            (user_choice == "✂️ Scissors" and ai_choice == "📄 Paper")
        ):
            result = "🎉 You win!"
        else:
            result = "💀 AI wins this time!"
        st.subheader(result)

        # Fun message
        if "win" in result:
            st.info(random.choice([
                "💡 A winner’s mindset will take you far — apply this in your interviews!",
                "🚀 You’re on fire! Keep that confidence for your next challenge.",
                "🎯 Great reflexes — just what a future innovator needs!"
            ]))
        elif "tie" in result:
            st.info(random.choice([
                "😄 Great minds think alike! Maybe you and AI could co-found a startup someday?",
                "🧠 A draw? That’s balance — the perfect skill for project management."
            ]))
        else:
            st.info(random.choice([
                "😅 AI wins today, but you’ll beat it in your next interview!",
                "📚 Every loss is a lesson — just like debugging code."
            ]))

st.markdown("---")

# --- Friendly info box (your original one) ---
st.info("""
💡 **Heads up, Explorer!**
- This is a **new experimental version** 🧪 — so things might take a few extra seconds to load ⏳  
- You might see some “thinking” or “...” screens — don’t worry, that’s just the AI brewing up magic ✨  
- Feel free to explore:
  - 🎯 **Career Advisor** → Upload resume & get career insights  
  - 🧠 **Mock Interview** → Practice questions tailored to you  
  - 💬 **Chatbot** → Ask career-related doubts freely
""")

st.markdown("---")
st.caption("Built with ❤️ using Streamlit, Gemini AI, and Supabase ⚡")

# --- Stop quotes rotation ---
stop_flag["value"] = True
t.join()
