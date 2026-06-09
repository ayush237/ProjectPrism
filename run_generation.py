import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Setup paths
OUT_DIR = "content/finalScripts/reel1_assets"
os.makedirs(OUT_DIR, exist_ok=True)

# 1. Pexels Fetcher
def fetch_pexels_video(query, filename):
    api_key = os.environ.get("PEXELS_API_KEY")
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&orientation=portrait&per_page=1"
    headers = {"Authorization": api_key}
    print(f"Fetching Pexels: {query}")
    resp = requests.get(url, headers=headers).json()
    if 'videos' in resp and len(resp['videos']) > 0:
        video = resp['videos'][0]
        video_files = video['video_files']
        v_url = video_files[0]['link']
        for vf in video_files:
            if vf['quality'] == 'hd' and vf['height'] and vf['height'] >= 1080:
                v_url = vf['link']
                break
        print(f"Downloading video to {filename}")
        v_data = requests.get(v_url).content
        with open(os.path.join(OUT_DIR, filename), "wb") as f:
            f.write(v_data)
    else:
        print(f"No video found for {query}")

# 2. Gemini Imagen
def generate_imagen(prompt, filename):
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    print(f"Generating image: {prompt}")
    try:
        result = client.models.generate_images(
            model='imagen-3.0-generate-002', # Since imagen-4 might not be accessible depending on the project
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="9:16"
            )
        )
        if result.generated_images:
            image_bytes = result.generated_images[0].image.image_bytes
            with open(os.path.join(OUT_DIR, filename), "wb") as f:
                f.write(image_bytes)
        else:
            print("No image generated")
    except Exception as e:
        print(f"Error generating image: {e}")

# 3. Diagram Kroki
def generate_kroki(markup, filename):
    print(f"Generating diagram to {filename}")
    url = "https://kroki.io/mermaid/png"
    resp = requests.post(url, data=markup.encode('utf-8'), headers={'Content-Type': 'text/plain'})
    if resp.status_code == 200:
        with open(os.path.join(OUT_DIR, filename), "wb") as f:
            f.write(resp.content)
    else:
        print(f"Kroki error: {resp.status_code} - {resp.text}")

# Execution
fetch_pexels_video("retro 90s computers typing", "02_internet_broll.mp4")
fetch_pexels_video("city at night traffic time lapse", "06_city_broll.mp4")
fetch_pexels_video("coffee pouring into mug moody workspace desk", "11_coffee_broll.mp4")

generate_imagen("High contrast cinematic vertical portrait of a glowing futuristic neural network expanding like a deep ocean, dark aesthetic, neon blue.", "01_hook_genai.jpg")
generate_imagen("A sleek futuristic metallic key unlocking a glowing digital vault door, cinematic portrait, dramatic lighting.", "03_vault_genai.jpg")
generate_imagen("A hyper-realistic cyberpunk survival kit floating in the air glowing with neon lights, vertical, highly detailed.", "09_necessity_genai.jpg")

diagram_exposure = '''graph TD
    classDef default fill:#1a1a1a,stroke:#333,stroke-width:2px,color:#fff;
    classDef highlight fill:#0055ff,stroke:#00aaff,stroke-width:4px,color:#fff;
    E[Exposure]:::highlight
    E -->|Growth| O1[Opportunity 1]
    E -->|Scale| O2[Opportunity 2]
    E -->|Impact| O3[Opportunity 3]
'''
generate_kroki(diagram_exposure, "04_exposure_diagram.png")

diagram_velocity = '''xychart-beta
    title "Adoption Velocity"
    x-axis ["1995", "2000", "2010", "2020", "2023", "2026"]
    y-axis "Adoption Rate" 0 --> 100
    line [5, 10, 20, 40, 60, 95]
    bar [5, 10, 20, 40, 60, 95]
'''
generate_kroki(diagram_velocity, "08_velocity_diagram.png")
