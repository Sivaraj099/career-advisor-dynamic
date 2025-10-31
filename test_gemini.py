import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# use one that actually appears in your list
model = genai.GenerativeModel("models/gemini-2.5-flash")

resp = model.generate_content("Say hello Gemini 2.5!")
print(resp.text)
