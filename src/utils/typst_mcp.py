from utils.logger import get_logger
logger = get_logger(__name__)

import os
import uuid
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Typst MCP")

@mcp.tool()
def compile_vertical_slide(markup: str, output_name: str) -> str:
    """Compiles raw text/markup into a vertical 1080x1920 PNG slide using Typst.
    
    Args:
        markup: The Typst/Markdown formatted text content for the slide.
        output_name: A base name for the output file (without extension).
    """
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'mcp_assets'))
    os.makedirs(save_dir, exist_ok=True)
    
    typ_content = f"""#set page(width: 1080pt, height: 1920pt, margin: 80pt)
#set text(size: 40pt, font: "Arial")

{markup}
"""
    
    unique_id = uuid.uuid4().hex[:8]
    typ_filename = os.path.join(save_dir, f"{output_name}_{unique_id}.typ")
    png_filename = os.path.join(save_dir, f"{output_name}_{unique_id}.png")
    
    with open(typ_filename, "w", encoding="utf-8") as f:
        f.write(typ_content)
        
    try:
        result = subprocess.run(["typst", "compile", typ_filename, png_filename], capture_output=True, text=True)
        if result.returncode != 0:
            return f"Typst compilation failed: {result.stderr}"
            
        return f"Slide compiled successfully. Saved to: {png_filename}"
    except Exception as e:
        logger.error(f\"MCP Error: {e}\", exc_info=True)
        return f"Error compiling slide: {str(e)}"

if __name__ == "__main__":
    mcp.run()
