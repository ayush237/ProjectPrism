import os
import uuid
from mcp.server.fastmcp import FastMCP
from google import genai
from google.genai import types

mcp = FastMCP("Gemini Image MCP")

@mcp.tool()
def generate_vertical_image(prompt: str) -> str:
    """Generates a vertical AI image using Gemini Imagen.
    
    Args:
        prompt: A highly descriptive prompt for the image generation.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY is not set."
        
    client = genai.Client(api_key=api_key)
    
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
        
        if not result.generated_images:
            return "Error: No image generated."
            
        generated_image = result.generated_images[0]
        image_bytes = generated_image.image.image_bytes
        
        # Save to local dir
        save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'mcp_assets'))
        os.makedirs(save_dir, exist_ok=True)
        
        filename = f"imagen_{uuid.uuid4().hex[:8]}.jpg"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
            
        return f"Image generated successfully. Saved to: {filepath}"
    except Exception as e:
        return f"Error generating image: {str(e)}"

if __name__ == "__main__":
    mcp.run()
