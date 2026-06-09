import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

OUT_DIR = "content/finalScripts/reel1_assets"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_imagen(prompt, filename):
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)
    print(f"Generating image: {prompt}")
    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
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
            print(f"Saved {filename}")
        else:
            print("No image generated")
    except Exception as e:
        print(f"Error generating image: {e}")

generate_imagen("High contrast cinematic vertical portrait of a glowing futuristic neural network expanding like a deep ocean, dark aesthetic, neon blue.", "01_hook_genai.jpg")
generate_imagen("A sleek futuristic metallic key unlocking a glowing digital vault door, cinematic portrait, dramatic lighting.", "03_vault_genai.jpg")
generate_imagen("A hyper-realistic cyberpunk survival kit floating in the air glowing with neon lights, vertical, highly detailed.", "09_necessity_genai.jpg")
