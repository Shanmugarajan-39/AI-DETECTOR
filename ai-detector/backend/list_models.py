import google.generativeai as genai
import os

GEMINI_API_KEY = "AIzaSyBuFuqf6Kw1RFX4vgvJVtzyADjQEije9MQ"
genai.configure(api_key=GEMINI_API_KEY)

print("Listing available models from Gemini API...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name} (Supports generateContent)")
except Exception as e:
    print(f"Error listing models: {e}")
