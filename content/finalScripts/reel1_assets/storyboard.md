# Director's Cut: Reel 1 Storyboard

> [!TIP]
> This storyboard is mapped using the **5-Vector Modality Logic**. It ensures rapid visual pattern interrupts and high-quality pacing. Pacing is calculated at roughly 3-4 seconds per spoken line.

---

### Cut 1: "Here is exactly why you need to explore AI much deeper than you think." (~3s)
- **Modality:** Generative AI
- **Visual Instructions:** A highly detailed, glowing futuristic neon neural network expanding like a deep ocean, vertical aspect ratio.
- **Prompt:** High contrast cinematic vertical portrait of a glowing futuristic neural network expanding like a deep ocean, dark aesthetic, neon blue.
- **Filename:** `01_hook_genai.jpg`
- **Sound Design:** Deep cinematic bass boom.

---

### Cut 2: "Look back to the time when the internet boom happened." (~2s)
- **Modality:** Stock B-Roll
- **Visual Instructions:** Retro 90s computers, old CRT monitors.
- **Prompt:** retro 90s computers
- **Filename:** `02_internet_broll.mp4`
- **Sound Design:** Dial-up modem glitch sound.

---

### Cut 3: "It caused a massive shift in how people and businesses operate." (~3s)
- **Modality:** Stock B-Roll
- **Visual Instructions:** Fast-paced business city timelapse.
- **Prompt:** city at night traffic time lapse
- **Filename:** `03_city_broll.mp4`
- **Sound Design:** City traffic whoosh.

---

### Cut 4: "The folks who understood it early gained a massive advantage in multiple aspects." (~3s)
- **Modality:** 🎥 Faceless POV (MANUAL)
- **Visual Instructions:** Top-down desk view of hands quickly typing on a glowing mechanical keyboard.
- **Prompt:** MANUAL
- **Filename:** `04_typing_manual.mp4`
- **Sound Design:** Mechanical keyboard clacks.

---

### Cut 5: "Because exposure is directly proportional to opportunity." (~3s)
- **Modality:** Animated Diagram (Manim)
- **Visual Instructions:** A sleek animated graph showing an upward curve from Exposure to Opportunity.
- **Prompt:**
```python
from manim import *
class ExposureOpportunity(Scene):
    def construct(self):
        axes = Axes(x_range=[0, 10], y_range=[0, 10], axis_config={"color": BLUE})
        labels = axes.get_axis_labels(x_label="Exposure", y_label="Opportunity")
        curve = axes.plot(lambda x: 0.1 * x**2, color=YELLOW)
        self.play(Create(axes), Write(labels))
        self.play(Create(curve), run_time=2)
```
- **Filename:** `05_exposure_opportunity.mp4`
- **Sound Design:** Digital rising synth.

---

### Cut 6: "And pretty evidently , the next major shift is the adaption of AI in a lot of domains." (~4s)
- **Modality:** Stock B-Roll
- **Visual Instructions:** Abstract glowing network nodes representing AI.
- **Prompt:** abstract ai glowing network nodes
- **Filename:** `06_ai_nodes.mp4`
- **Sound Design:** Data processing flutter.

---

### Cut 7: "The entire way we work is fundamentally changing. We have to adapt to this change" (~5s)
- **Modality:** 💻 Screen Recording (MANUAL)
- **Visual Instructions:** Record VS Code terminal running an AI script, apply a cinematic smooth zoom.
- **Prompt:** MANUAL
- **Filename:** `07_vscode_manual.mp4`
- **Sound Design:** Digital terminal blips.

---

### Cut 8: "But here is the catch." (~1.5s)
- **Modality:** Animated Diagram (Manim)
- **Visual Instructions:** Bold text "THE CATCH" appearing with a glitch effect.
- **Prompt:**
```python
from manim import *
class TheCatch(Scene):
    def construct(self):
        text = Text("THE CATCH", font_size=96, color=RED, weight=BOLD)
        self.play(Write(text))
        self.play(Indicate(text, color=YELLOW))
```
- **Filename:** `08_the_catch.mp4`
- **Sound Design:** Sudden record scratch.

---

### Cut 9: "The AI space is updating ten times faster than the internet ever did." (~3s)
- **Modality:** Animated Diagram (Manim)
- **Visual Instructions:** Two progress bars, one labeled "Internet" moving slow, one labeled "AI" moving 10x faster.
- **Prompt:**
```python
from manim import *
class SpeedComparison(Scene):
    def construct(self):
        internet_text = Text("Internet", font_size=36).shift(UP*1 + LEFT*4)
        ai_text = Text("AI", font_size=36).shift(DOWN*1 + LEFT*4)
        internet_bar = Rectangle(height=0.5, width=2, color=BLUE).next_to(internet_text, RIGHT)
        ai_bar = Rectangle(height=0.5, width=8, color=GREEN).next_to(ai_text, RIGHT)
        self.add(internet_text, ai_text)
        self.play(Create(internet_bar, run_time=2), Create(ai_bar, run_time=0.5))
```
- **Filename:** `09_ai_speed.mp4`
- **Sound Design:** Fast swoosh panning left to right.

---

### Cut 10: "Hence getting yourself well equipped isn't just an opportunity —it’s a baseline necessity." (~3.5s)
- **Modality:** Generative AI
- **Visual Instructions:** A hyper-realistic cyberpunk survival kit floating in the air, neon lights.
- **Prompt:** A hyper-realistic cyberpunk survival kit floating in the air glowing with neon lights, vertical, highly detailed.
- **Filename:** `10_necessity_genai.jpg`
- **Sound Design:** Sci-fi scanner hum.

---

### Cut 11: "That's why having a planned approach towards learning AI is the best bet." (~3s)
- **Modality:** Animated Diagram (Manim)
- **Visual Instructions:** A roadmap diagram unfolding step by step.
- **Prompt:**
```python
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
```
- **Filename:** `11_roadmap.mp4`
- **Sound Design:** Clean checkmark dings.

---

### Cut 12: "So That's my perspective, maybe not very fresh but I would love to hear yours. Let's discuss in the comments, and you can follow this page for more insights and breakdowns in this space, thanks!" (~6s)
- **Modality:** 🎥 Faceless POV (MANUAL)
- **Visual Instructions:** A top-down view of a coffee mug being placed on a desk, panning over to an open notebook.
- **Prompt:** MANUAL
- **Filename:** `12_outro_manual.mp4`
- **Sound Design:** Ceramic mug clink, ambient coffee shop hum.
