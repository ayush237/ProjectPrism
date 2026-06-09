import os
import sys
import shutil
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.utils.gemini_image_mcp import generate_vertical_image
from src.utils.typst_mcp import compile_vertical_slide

def setup_asset_dir():
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content', 'finalScripts', 'reel1_assets'))
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

def get_pexels_video(query, dest_dir, filename):
    print(f"Pexels: {query}")
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("PEXELS_API_KEY missing")
        return
    headers = {"Authorization": api_key}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&size=large&per_page=1"
    
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        data = res.json()
        if data.get("videos"):
            video_files = data["videos"][0]["video_files"]
            hd_files = [v for v in video_files if v["quality"] == "hd"]
            if hd_files:
                video_url = hd_files[0]["link"]
            else:
                video_url = video_files[0]["link"]
                
            video_res = requests.get(video_url)
            filepath = os.path.join(dest_dir, filename)
            with open(filepath, 'wb') as f:
                f.write(video_res.content)
            print(f"-> Saved: {filepath}\n")
        else:
            print(f"-> No video found for query: {query}\n")
    except Exception as e:
        print(f"-> Pexels Error: {e}\n")

def generate_image(prompt, dest_dir, filename):
    print(f"Gemini: {prompt}")
    res = generate_vertical_image(prompt)
    print(f"-> Output: {res}")
    
    if "Saved to:" in res:
        src_path = res.split("Saved to: ")[1].strip()
        dest_path = os.path.join(dest_dir, filename)
        shutil.copy(src_path, dest_path)
        print(f"-> Saved: {dest_path}\n")

def compile_slide(markup, dest_dir, filename):
    print(f"Typst: {filename}")
    res = compile_vertical_slide(markup, "temp_slide")
    print(f"-> Output: {res}")
    
    if "Saved to:" in res:
        src_path = res.split("Saved to: ")[1].strip()
        dest_path = os.path.join(dest_dir, filename)
        shutil.copy(src_path, dest_path)
        print(f"-> Saved: {dest_path}\n")

if __name__ == "__main__":
    dest_dir = setup_asset_dir()
    
    # Cut 2: Gemini Imagen
    generate_image(
        "Retro 90s computer lab glowing with early internet web pages on CRT monitors, cinematic lighting, vertical 9:16 aspect ratio, high detail", 
        dest_dir, "02_retro_internet.jpg"
    )
    
    # Cut 3: Pexels
    get_pexels_video("fast paced business city walking", dest_dir, "03_city_timelapse.mp4")
    
    # Cut 5: Typst
    compile_slide('''
#align(center + horizon)[
  #text(weight: "bold", size: 60pt, fill: rgb("ffffff"))[
    Exposure = Opportunity
  ]
]
#set page(fill: rgb("111111"))
''', dest_dir, "05_exposure_opportunity.png")
    
    # Cut 6: Pexels
    get_pexels_video("abstract ai glowing network nodes", dest_dir, "06_ai_nodes.mp4")
    
    # Cut 8: Typst
    compile_slide('''
#align(center + horizon)[
  #text(weight: "black", size: 100pt, fill: rgb("ff3333"))[
    THE CATCH.
  ]
]
#set page(fill: rgb("000000"))
''', dest_dir, "08_the_catch.png")
    
    # Cut 10: Gemini Imagen
    generate_image(
        "A futuristic toolbox or glowing high-tech gear laid out on a table, cybernetic, neon accents, 9:16 vertical orientation, masterpiece", 
        dest_dir, "10_futuristic_toolbox.jpg"
    )
    
    # Cut 11: Typst
    compile_slide('''
#align(center + horizon)[
  #rect(fill: rgb("222222"), radius: 20pt, inset: 40pt)[
    #text(weight: "bold", size: 70pt, fill: rgb("4CAF50"))[
      Planned\nAI Approach\n#sym.arrow.t
    ]
  ]
]
#set page(fill: rgb("111111"))
''', dest_dir, "11_planned_approach.png")

    print("DONE")
