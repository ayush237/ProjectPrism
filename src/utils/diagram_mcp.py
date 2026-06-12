from utils.logger import get_logger
logger = get_logger(__name__)

import os
import uuid
import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Diagram MCP")

@mcp.tool()
def generate_diagram(markup: str, output_name: str) -> str:
    """Compiles Mermaid diagram markup into a vertical PNG using the Kroki API.
    
    Args:
        markup: The raw Mermaid diagram markup (do not include the ```mermaid markdown code blocks).
        output_name: A base name for the output file (without extension).
    """
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'mcp_assets'))
    os.makedirs(save_dir, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    png_filename = os.path.join(save_dir, f"{output_name}_{unique_id}.png")
    
    try:
        # Kroki POST endpoint for mermaid to png
        url = "https://kroki.io/mermaid/png"
        response = requests.post(url, data=markup.encode('utf-8'), headers={'Content-Type': 'text/plain'})
        
        if response.status_code == 200:
            with open(png_filename, 'wb') as f:
                f.write(response.content)
            return f"Diagram generated successfully. Saved to: {png_filename}"
        else:
            return f"Error from Kroki API: {response.status_code} - {response.text}"
            
    except Exception as e:
        logger.error(f\"MCP Error: {e}\", exc_info=True)
        return f"Error generating diagram: {str(e)}"

if __name__ == "__main__":
    mcp.run()
