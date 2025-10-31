import json
import streamlit as st
import google.generativeai as genai



# ---- Setup ----
genai.configure(api_key="AIzaSyB_NDGAwjqsq5TcEznWv7Jip0N-ML3rXnQ") 
model = genai.GenerativeModel("models/gemini-2.5-flash")


st.title("🧪 Mock Interview (v1 — typed answers)")

# ---- Question bank (starter) ----
QUESTION_BANK = {
    "Software Engineer": [
        "Explain the difference between a process and a thread.",
        "What is a race condition? How do you prevent it?",
        "How does a hash map work under the hood?",
        "Describe SOLID principles briefly.",
        "What happens when you type a URL in the browser and hit Enter?"
    ],
    "Data Analyst": [
        "How would you handle missing data?",
        "Explain the difference between inner and left joins.",
        "When would you use a median instead of a mean?",
        "What is a p-value in hypothesis testing?",
        "How do you detect outliers?"
    ],
    "ML Engineer": [
        "Bias vs variance — explain with examples.",
        "What is regularization and why is it useful?",
        "How do you evaluate an imbalanced classifier?",
        "Explain gradient descent and learning rate.",
        "What is overfitting? How do you prevent it?"
    ],
    "DevOps Engineer": [
        "Blue/green vs rolling deployments — differences?",
        "What is IaC and why use it?",
        "Explain CI vs CD with examples.",
        "How do you design observability for a microservice?",
        "What is a container vs a VM?"
    ]
}

# ---- UI ----
role = st.selectbox("Choose your role", list(QUESTION_BANK.keys()))
question = st.selectbox("Pick a question", QUESTION_BANK[role])
answer = st.text_area("Your answer (2–6 sentences recommended):")

if st.button("Evaluate"):
    if not answer.strip():
        st.warning("Write an answer first 🙂")
        st.stop()

    with st.spinner("Scoring your answer..."):
        prompt = f"""
You are an interview evaluator. Score the candidate's answer based on these rubrics:

- Technical (0–10): Accuracy, correctness, and relevance of the content.
- English (0–10): Grammar, fluency, clarity of expression.
- Confidence (0–10): Structured answer, direct tone, minimal hesitation words.

Return STRICT JSON only with this schema:
{{
  "technical": int,
  "english": int,
  "confidence": int,
  "feedback": string,
  "improvement_plan": string
}}

Question: {question}
Answer: {answer}
"""

        resp = model.generate_content(prompt)
        raw = resp.text

    # Try to parse JSON robustly
    try:
        result = json.loads(raw)
    except Exception:
        try:
            start = raw.index("{")
            end = raw.rindex("}") + 1
            result = json.loads(raw[start:end])
        except Exception:
            st.error("I couldn't parse the scoring JSON. Here's the raw response:")
            st.code(raw)
            st.stop()

    # Clamp scores
    def clamp(x): 
        try: 
            return max(0, min(10, int(x))) 
        except: 
            return 0
    technical = clamp(result.get("technical", 0))
    english = clamp(result.get("english", 0))
    confidence = clamp(result.get("confidence", 0))
    avg_score = round((technical + english + confidence) / 3, 1)

    # ---- Results UI ----
    st.subheader("Scores")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Technical", technical)
    c2.metric("English", english)
    c3.metric("Confidence", confidence)
    c4.metric("Average", avg_score)

    st.subheader("Feedback")
    st.write(result.get("feedback", "—"))

    st.subheader("Improvement Plan")
    st.write(result.get("improvement_plan", "—"))

    # ---- Perfect Answer ----
    with st.spinner("Generating a model answer..."):
        pa_prompt = f"Give the perfect interview answer for this question:\n\n{question}\n\nKeep it concise (4–6 sentences)."
        pa_resp = model.generate_content(pa_prompt)
        perfect_answer = pa_resp.text

    st.subheader("📌 Perfect Answer")
    st.write(perfect_answer)
