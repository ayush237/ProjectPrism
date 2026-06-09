import os
import sys
import shutil
import requests
import uuid
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.utils.gemini_image_mcp import generate_vertical_image
from src.utils.manim_mcp import compile_manim_scene

OUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'content', 'finalScripts', 'reel1_assets'))
os.makedirs(OUT_DIR, exist_ok=True)

def fetch_pexels_video(query, filename):
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("PEXELS_API_KEY missing")
        return
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(query)}&orientation=portrait&per_page=1"
    headers = {"Authorization": api_key}
    print(f"Fetching Pexels: {query}")
    try:
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
            filepath = os.path.join(OUT_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(v_data)
            print(f"-> Saved: {filepath}")
        else:
            print(f"No video found for {query}")
    except Exception as e:
        print(f"Pexels Error: {e}")

def run_gemini(prompt, filename):
    print(f"Gemini: {prompt}")
    try:
        res = generate_vertical_image(prompt)
        print(f"-> Output: {res}")
        if "Saved to:" in res:
            src_path = res.split("Saved to: ")[1].strip()
            dest_path = os.path.join(OUT_DIR, filename)
            shutil.copy(src_path, dest_path)
            print(f"-> Saved: {dest_path}")
    except Exception as e:
        print(f"Gemini Error: {e}")

def run_manim(code, class_name, filename):
    print(f"Manim: {class_name}")
    try:
        res = compile_manim_scene(code, class_name, filename.replace(".mp4", ""))
        print(f"-> Output: {res}")
        if "Saved to:" in res:
            src_path = res.split("Saved to: ")[1].strip()
            dest_path = os.path.join(OUT_DIR, filename)
            shutil.copy(src_path, dest_path)
            print(f"-> Saved: {dest_path}")
    except Exception as e:
        print(f"Manim Error: {e}")

# Row 1: Gemini
run_gemini("High contrast cinematic vertical portrait of a glowing futuristic neural network expanding like a deep ocean, dark aesthetic, neon blue.", "01_hook_genai.jpg")

# Row 2: Pexels
fetch_pexels_video("retro 90s computers", "02_internet_broll.mp4")

# Row 3: Pexels
fetch_pexels_video("city at night traffic time lapse", "03_city_broll.mp4")

# Row 5: Manim
run_manim("""
from manim import *
class ExposureOpportunity(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 10], y_range=[0, 10], axis_config={"color": BLUE})
        labels = axes.get_axis_labels(x_label="Exposure", y_label="Opportunity")
        curve = axes.plot(lambda x: 0.1 * x**2, color=YELLOW)
        self.play(Create(axes), Write(labels))
        self.play(Create(curve), run_time=2)
""", "ExposureOpportunity", "05_exposure_opportunity.mp4")

# Row 6: Pexels
fetch_pexels_video("abstract ai glowing network nodes", "06_ai_nodes.mp4")

# Row 8: Manim
run_manim("""
from manim import *
class TheCatch(Scene):
    def construct(self):
        text = Text("THE CATCH", font_size=96, color=RED, weight=BOLD)
        self.play(Write(text))
        self.play(Indicate(text, color=YELLOW))
""", "TheCatch", "08_the_catch.mp4")

# Row 9: Manim
run_manim("""
from manim import *
class SpeedComparison(Scene):
    def construct(self):
        internet_text = Text("Internet", font_size=36).shift(UP*1 + LEFT*4)
        ai_text = Text("AI", font_size=36).shift(DOWN*1 + LEFT*4)
        internet_bar = Rectangle(height=0.5, width=2, color=BLUE).next_to(internet_text, RIGHT)
        ai_bar = Rectangle(height=0.5, width=8, color=GREEN).next_to(ai_text, RIGHT)
        self.add(internet_text, ai_text)
        self.play(Create(internet_bar, run_time=2), Create(ai_bar, run_time=0.5))
""", "SpeedComparison", "09_ai_speed.mp4")

# Row 10: Gemini
run_gemini("A hyper-realistic cyberpunk survival kit floating in the air glowing with neon lights, vertical, highly detailed.", "10_necessity_genai.jpg")

# Row 11: Manim
run_manim("""
from manim import *
class PlannedApproach(Scene):
    def construct(self):
        title = Text("Planned AI Approach", font_size=48, color=YELLOW).to_edge(UP)
        step1 = Text("1. Basics", font_size=36).shift(UP*0.5)
        step2 = Text("2. Tools", font_size=36).next_to(step1, DOWN)
        step3 = Text("3. Mastery", font_size=36).next_to(step2, DOWN)
        self.play(Write(title))
        self.play(FadeIn(step1, shift=DOWN))
        self.play(FadeIn(step2, shift=DOWN))
        self.play(FadeIn(step3, shift=DOWN))
""", "PlannedApproach", "11_roadmap.mp4")

print("All automated tools executed successfully.")
