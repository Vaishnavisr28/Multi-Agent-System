# utils/llm_utils.py
import os
import google.generativeai as genai
from utils.logger import append_log

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not set in environment")

genai.configure(api_key=GEMINI_API_KEY)

# Use the correct Gemini model
MODEL_NAME = "gemini-1.5-flash"

def generate_summary(prompt: str) -> str:
    """
    Generate a concise summary using Gemini API.
    """
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        text = response.text if hasattr(response, "text") else str(response)
        append_log(f"✅ Gemini summary generated ({len(text)} chars)")
        return text.strip()
    except Exception as e:
        append_log(f"⚠️ Gemini error: {e}")
        return f"⚠️ Gemini error: {e}"
