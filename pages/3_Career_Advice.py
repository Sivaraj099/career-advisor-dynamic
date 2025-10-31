import streamlit as st
import json, uuid, io, os
import pdfplumber
from utils.supabase_client import supabase
from utils.ui_helpers import show_loading_quotes, stop_loading_quotes
from google import generativeai as genai

# --- Configure Gemini ---
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash")

# --- Helper: Extract text from PDF ---
def extract_text_from_pdf_bytes(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()

# --- Streamlit UI ---
st.title("🎯 Career Advisor")
uploaded = st.file_uploader("📂 Upload resume (PDF)", type=["pdf"])

parsed_json = None  # global

if uploaded:
    if st.button("Upload & Parse"):
        file_bytes = uploaded.read()
        file_key = f"{st.session_state.get('user', {}).get('id', 'anon')}_{uuid.uuid4().hex}.pdf"

        # --- 1️⃣ Upload file to Supabase ---
        res = supabase.storage.from_('resumes').upload(file_key, file_bytes)
        if hasattr(res, "error") and res.error:
            st.error("❌ Upload failed: " + str(res.error))
            st.stop()
        else:
            st.success(f"✅ File uploaded to Supabase as {file_key}")

        # --- 2️⃣ Extract resume text ---
        raw_text = extract_text_from_pdf_bytes(file_bytes)

        # --- 3️⃣ Parse Resume using Gemini ---
        parse_prompt = f"""
        Extract this resume into JSON with keys:
        {{
          "Skills": "...",
          "Education": "...",
          "Projects": "...",
          "Experience": "..."
        }}
        Resume:
        {raw_text}
        Return strict JSON only.
        """

        stop_flag, t, ph, spinner = show_loading_quotes("🤖 Analyzing resume with Gemini...")
        try:
            resp = model.generate_content(parse_prompt)
            parsed_text = resp.text.strip()
            try:
                parsed_json = json.loads(parsed_text)
            except Exception:
                st.warning("⚠️ Could not parse clean JSON. Showing raw output:")
                st.code(parsed_text)
                parsed_json = {"raw_text": raw_text}
        except Exception as e:
            st.error("Gemini error: " + str(e))
            parsed_json = {"raw_text": raw_text}
        finally:
            stop_loading_quotes(stop_flag, t, ph, spinner)

        # --- 4️⃣ Insert parsed data into Supabase ---
        user_id = st.session_state.get("user", {}).get("id")
        row = {"storage_path": file_key, "parsed_json": parsed_json}
        if user_id:
            row["user_id"] = user_id

        try:
            insert = supabase.table("resumes").insert(row).execute()
            if hasattr(insert, "error") and insert.error:
                st.error("❌ Database insert failed: " + str(insert.error))
            else:
                resume_row = insert.data[0]
                st.success("✅ Resume saved successfully!")
                st.session_state["current_resume"] = parsed_json
                st.session_state["current_resume_id"] = resume_row["id"]
                st.json(parsed_json)

                # --- 5️⃣ Generate Career Advice ---
                if parsed_json:
                    st.markdown("---")
                    st.subheader("🚀 Career Recommendations & Skill Insights")

                    analysis_prompt = f"""
                    You are an AI career coach. Based on this candidate's resume:

                    {json.dumps(parsed_json, indent=2)}

                    Respond in Markdown format with:
                    1️⃣ Strengths
                    2️⃣ Recommended Career Roles (with reasons)
                    3️⃣ Skill Gaps & Improvement Areas
                    4️⃣ Learning Suggestions (Coursera/Udemy/free docs)
                    """

                    stop_flag, t, ph, spinner = show_loading_quotes("💡 Generating personalized career recommendations...")
                    try:
                        resp = model.generate_content(analysis_prompt)
                        advice = resp.text.strip()
                        st.markdown(advice)

                        # --- Save advice to DB (if column exists)
                        try:
                            supabase.table("resumes").update({
                                "career_advice": advice
                            }).eq("id", resume_row["id"]).execute()
                        except Exception:
                            pass
                    except Exception as e:
                        st.error(f"Error while generating career path: {e}")
                    finally:
                        stop_loading_quotes(stop_flag, t, ph, spinner)

        except Exception as e:
            st.error("DB error: " + str(e))
