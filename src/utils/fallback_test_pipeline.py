import os
import json
import urllib.request
import urllib.error
import subprocess
import shutil

def setup_asset_dir():
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'content', 'finalScripts', 'reel1_assets'))
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def get_pexels_video(query, dest_dir):
    print("1. Orchestrating Pexels (B-Roll)...")
    api_key = os.environ.get("PEXELS_API_KEY")
    url = f"https://api.pexels.com/videos/search?query={query.replace(' ', '%20')}&orientation=portrait&size=large&per_page=1"
    
    req = urllib.request.Request(url, headers={"Authorization": api_key})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if data.get("videos"):
                video_files = data["videos"][0]["video_files"]
                hd_files = [v for v in video_files if v["quality"] == "hd"]
                video_url = hd_files[0]["link"] if hd_files else video_files[0]["link"]
                
                filepath = os.path.join(dest_dir, "01_hook_broll.mp4")
                urllib.request.urlretrieve(video_url, filepath)
                print(f"-> B-Roll successfully downloaded to: {filepath}\n")
            else:
                print("-> No video found for query.\n")
    except Exception as e:
        print(f"-> Pexels Error: {e}\n")

def generate_image(dest_dir):
    print("2. Orchestrating Gemini Imagen...")
    api_key = os.environ.get("GEMINI_API_KEY")
    prompt = "A cinematic, vertical portrait of a futuristic glowing AI brain bridging the gap from 90s retro internet to the futuristic AI era, highly detailed, dramatic lighting, 8k resolution"
    
    # We use the REST endpoint to bypass the broken pip environment
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict?key={api_key}"
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "outputOptions": {"mimeType": "image/jpeg"},
            "aspectRatio": "9:16"
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            if 'predictions' in data and len(data['predictions']) > 0:
                b64_image = data['predictions'][0]['bytesBase64Encoded']
                import base64
                image_bytes = base64.b64decode(b64_image)
                filepath = os.path.join(dest_dir, "02_ai_imagery.jpg")
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                print(f"-> Image generated successfully to: {filepath}\n")
            else:
                print("-> No image returned in predictions.\n")
    except Exception as e:
        print(f"-> Gemini Error: {e}\n")

def compile_slide(dest_dir):
    print("3. Orchestrating Typst Compile...")
    markup = '''
#set page(width: 1080pt, height: 1920pt, margin: 80pt)
#set text(size: 40pt, font: "Arial")

#align(center + horizon)[
  #text(weight: "bold", size: 60pt, fill: rgb("2c3e50"))[
    "Exposure is directly proportional to opportunity."
  ]
]
'''
    typ_filename = os.path.join(dest_dir, "temp_slide.typ")
    png_filename = os.path.join(dest_dir, "03_quote_slide.png")
    
    with open(typ_filename, "w", encoding="utf-8") as f:
        f.write(markup)
        
    try:
        result = subprocess.run(["typst", "compile", typ_filename, png_filename], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"-> Typst compilation failed: {result.stderr}\n")
        else:
            print(f"-> Slide compiled successfully to: {png_filename}\n")
    except Exception as e:
        print(f"-> Typst Error: {e}\n")
    finally:
        if os.path.exists(typ_filename):
            os.remove(typ_filename)

if __name__ == "__main__":
    dest_dir = setup_asset_dir()
    
    print(f"Starting Fallback Asset Generation Pipeline for: reel1.md")
    print("=" * 50)
    
    get_pexels_video("business future", dest_dir)
    generate_image(dest_dir)
    compile_slide(dest_dir)
    
    print("=" * 50)
    print("Asset generation pipeline complete! Check content/finalScripts/reel1_assets/")
