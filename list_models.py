import os
from dotenv import load_dotenv
from google import genai
load_dotenv()
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
for m in client.models.list():
    if "imagen" in m.name:
        print(m.name)
