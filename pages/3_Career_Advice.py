import streamlit as st
import pdfplumber
import google.generativeai as genai
import os
import json

# ---- Setup ----
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No API key found. Please set GEMINI_API_KEY as an environment variable.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("models/gemini-2.5-flash")

# ---- PDF Extractor ----
def extract_text_from_pdf(uploaded_file):
    """Extract text from uploaded PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()

# ---- Streamlit UI ----
st.title("🎯 Career Advisor (Smart Resume Parsing + AI Analysis)")

uploaded_file = st.file_uploader("📂 Upload your resume (PDF)", type=["pdf"])
resume_text = ""

if uploaded_file is not None and api_key:
    # Extract raw text
    resume_text = extract_text_from_pdf(uploaded_file)
    st.subheader("📄 Extracted Resume Text")
    st.text_area("Raw text from your resume:", resume_text, height=200)

    if st.button("🔎 Analyze with Gemini"):
        if resume_text.strip():
            # ---- Step 1: Parse Resume into JSON ----
            with st.spinner("🤖 Parsing resume with Gemini..."):
                parse_prompt = f"""
                You are a JSON generator. Read the following resume text and return a structured JSON summary.

                Resume text:
                {resume_text}

                Return ONLY valid JSON in this exact format:
                {{
                  "Name": "",
                  "Education": "",
                  "Skills": ["", "", ""],
                  "Projects": ["", "", ""],
                  "Experience": ["", "", ""]
                }}
                No explanations or extra text — only valid JSON.
                """

                try:
                    parse_resp = model.generate_content(parse_prompt)
                    parsed_output = parse_resp.text.strip()

                    # Try to locate JSON brackets if extra text appears
                    try:
                        start = parsed_output.index("{")
                        end = parsed_output.rindex("}") + 1
                        parsed_json_str = parsed_output[start:end]
                        parsed_json = json.loads(parsed_json_str)
                        st.subheader("🗂️ Parsed Resume Summary")
                        st.json(parsed_json)
                    except Exception:
                        st.warning("⚠️ Gemini didn’t return pure JSON. Showing raw output:")
                        st.code(parsed_output, language="json")
                        parsed_json = {"RawOutput": parsed_output}

                except Exception as e:
                    st.error(f"Error parsing resume: {e}")
                    parsed_json = {"error": str(e)}

            # ---- Step 2: Analyze for Career Roles ----
            with st.spinner("🚀 Generating career advice..."):
                analysis_prompt = f"""
                You are a career advisor AI. Based on this parsed resume:

                {json.dumps(parsed_json, indent=2)}

                Do the following:
                Do the following:
                1. Suggest **5 suitable career roles** that align with the candidate’s background.
                2. For each role, identify:
                - **Strengths**: Key skills, experiences, or projects that make the candidate a strong fit.
                - **Weaknesses / Skill Gaps**: Areas that need improvement or learning, with difficulty level (Beginner / Intermediate / Advanced).
                3. Recommend **2–3 high-quality online courses or resources** (Coursera, Udemy, or free docs).
                4. Provide a **summary paragraph** at the end with an encouraging and motivational tone.

                Output should be formatted with:
                - Markdown headings for each career role
                - Separate bullet lists for strengths and weaknesses
                - A section titled “🌟 Overall Strengths” summarizing the candidate’s strongest areas across all roles
                """

                try:
                    analysis_resp = model.generate_content(analysis_prompt)
                    advice = analysis_resp.text
                    st.subheader("🚀 Career Suggestions & Skill Gap Analysis")
                    st.markdown(advice)
                except Exception as e:
                    st.error(f"Error analyzing resume: {e}")
