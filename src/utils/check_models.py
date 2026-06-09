import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

print("Listing available imagen models...")
for model in client.models.list():
    if 'imagen' in model.name.lower():
        print(f"Found model: {model.name}")
