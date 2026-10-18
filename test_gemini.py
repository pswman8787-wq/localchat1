# test_gemini.py
import os

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("Set the GEMINI_API_KEY environment variable before running this test.")

client = genai.Client(api_key=api_key, http_options={"api_version": "v1"})
try:
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents="Halo, apakah kamu aktif?",
    )
    print("Respon AI:", response.text)
except Exception as e:
    print("Error Terjadi:", e)
    