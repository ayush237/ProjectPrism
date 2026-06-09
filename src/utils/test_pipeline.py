import os
import sys
import shutil
import requests

# Add the root directory to path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.gemini_image_mcp import generate_vertical_image
from src.utils.typst_mcp import compile_vertical_slide

def setup_asset_dir():
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'content', 'finalScripts', 'reel1_assets'))
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def get_pexels_video(query, dest_dir):
    print("1. Orchestrating Pexels MCP Server (B-Roll)...")
    api_key = os.environ.get("PEXELS_API_KEY")
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=large&per_page=1"
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data.get("videos"):
            # Get highest quality HD link
            video_files = data["videos"][0]["video_files"]
            hd_files = [v for v in video_files if v["quality"] == "hd"]
            if hd_files:
                video_url = hd_files[0]["link"]
            else:
                video_url = video_files[0]["link"]
                
            video_res = requests.get(video_url)
            filepath = os.path.join(dest_dir, "01_hook_broll.mp4")
            with open(filepath, 'wb') as f:
                f.write(video_res.content)
            print(f"-> B-Roll successfully downloaded to: {filepath}\n")
        else:
            print("-> No video found for query.\n")
    except Exception as e:
        print(f"-> Pexels Error: {e}\n")

def generate_image(dest_dir):
    print("2. Orchestrating Gemini Imagen MCP Server...")
    prompt = "A cinematic, vertical portrait of a futuristic glowing AI brain bridging the gap from 90s retro internet to the futuristic AI era, highly detailed, dramatic lighting, 8k resolution"
    
    res = generate_vertical_image(prompt)
    print(f"-> MCP Output: {res}")
    
    # Extract path from output and move to asset dir
    if "Saved to:" in res:
        src_path = res.split("Saved to: ")[1].strip()
        dest_path = os.path.join(dest_dir, "02_ai_imagery.jpg")
        shutil.copy(src_path, dest_path)
        print(f"-> Copied to final destination: {dest_path}\n")

def compile_slide(dest_dir):
    print("3. Orchestrating Typst MCP Server...")
    markup = '''
#align(center + horizon)[
  #text(weight: "bold", size: 60pt, fill: rgb("2c3e50"))[
    "Exposure is directly proportional to opportunity."
  ]
]
'''
    res = compile_vertical_slide(markup, "03_quote_slide")
    print(f"-> MCP Output: {res}")
    
    # Extract path and move
    if "Saved to:" in res:
        src_path = res.split("Saved to: ")[1].strip()
        dest_path = os.path.join(dest_dir, "03_quote_slide.png")
        shutil.copy(src_path, dest_path)
        print(f"-> Copied to final destination: {dest_path}\n")

if __name__ == "__main__":
    dest_dir = setup_asset_dir()
    
    print(f"Starting Asset Generation Pipeline for: reel1.md")
    print("=" * 50)
    
    get_pexels_video("business future", dest_dir)
    generate_image(dest_dir)
    compile_slide(dest_dir)
    
    print("=" * 50)
    print("Asset generation pipeline complete! Check content/finalScripts/reel1_assets/")
