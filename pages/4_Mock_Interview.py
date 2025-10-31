import streamlit as st
import json, os
from utils.supabase_client import supabase
from utils.ui_helpers import show_loading_quotes, stop_loading_quotes
from google import generativeai as genai

# --- Configure Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Session setup ---
if "user" not in st.session_state:
    st.session_state["user"] = {"id": None, "email": "anonymous@demo.app"}

st.title("🧠 AI Mock Interview Assistant")

resume = st.session_state.get("current_resume")
if not resume:
    st.info("⚠️ Please upload your resume first on Career Advisor page.")
    st.stop()

# --- Generate Questions ---
if st.button("🎯 Generate Interview Questions"):
    stop_flag, t, ph, spinner = show_loading_quotes("🤖 Generating custom interview questions...")
    try:
        prompt = f"""
        Based on this resume:
        {json.dumps(resume, indent=2)}

        Create 8 interview questions:
        - 4 Behavioral (communication, teamwork, problem-solving)
        - 4 Technical (related to Python, Power BI, Excel, SQL, Pandas, DAX, Azure)
        Return strict JSON array:
        [
          "Behavioral: ...",
          "Technical: ..."
        ]
        """
        resp = model.generate_content(prompt)
        raw = resp.text.strip()

        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            questions = json.loads(raw)
        except:
            questions = [q.strip("-• ") for q in raw.splitlines() if q.strip()]

        questions = [q for q in questions if len(q) > 5]

        if not questions:
            st.error("❌ No valid questions generated.")
            st.stop()

        sess_row = {
            "user_id": st.session_state["user"].get("id"),
            "resume_id": st.session_state.get("current_resume_id"),
            "questions": questions
        }
        try:
            supabase.table("mock_sessions").insert(sess_row).execute()
        except:
            pass

        st.session_state["current_questions"] = questions
        st.success("✅ Questions generated successfully!")
    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        stop_loading_quotes(stop_flag, t, ph, spinner)

# --- Answer & Feedback ---
if st.session_state.get("current_questions"):
    st.markdown("---")
    st.subheader("🗣️ Answer the following questions:")

    questions = st.session_state["current_questions"]
    for idx, q in enumerate(questions):
        st.write(f"**Q{idx+1}:** {q}")
        st.text_area(f"Your Answer for Q{idx+1}", key=f"ans_{idx}")

    if st.button("📤 Submit & Get Feedback"):
        answers = [st.session_state.get(f"ans_{i}", "") for i in range(len(questions))]
        if not any(answers):
            st.warning("⚠️ Please answer at least one question before submitting.")
            st.stop()

        feedback_all = []
        st.subheader("🧾 Feedback Summary")
        progress = st.progress(0)

        for i, (q, a) in enumerate(zip(questions, answers)):
            progress.progress((i + 1) / len(questions))
            is_behavioral = q.lower().startswith("behavioral")

            if is_behavioral:
                score_prompt = f"""
                Evaluate this behavioral answer:
                Q: {q}
                A: {a}
                Return JSON:
                {{
                    "communication": int,
                    "emotional_intelligence": int,
                    "confidence": int,
                    "feedback": "..."
                }}
                """
            else:
                score_prompt = f"""
                Evaluate this technical answer:
                Q: {q}
                A: {a}
                Return JSON:
                {{
                    "technical": int,
                    "clarity": int,
                    "confidence": int,
                    "feedback": "..."
                }}
                """

            stop_flag, t, ph, spinner = show_loading_quotes(f"🧩 Evaluating Q{i+1}...")
            try:
                sresp = model.generate_content(score_prompt)
                raw_fb = sresp.text.strip()
                if raw_fb.startswith("```"):
                    raw_fb = raw_fb.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(raw_fb)
            except:
                parsed = {"feedback": "Could not parse feedback."}
            finally:
                stop_loading_quotes(stop_flag, t, ph, spinner)

            feedback_all.append(parsed)

        st.success("✅ Feedback generated successfully!")
        for i, fb in enumerate(feedback_all):
            st.markdown(f"### 💬 Q{i+1} Feedback")
            for k, v in fb.items():
                if k != "feedback":
                    st.write(f"**{k.capitalize()}:** {v}/10")
            st.write(f"**Feedback:** {fb.get('feedback', '')}")
