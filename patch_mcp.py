import os
import re

FILES = [
    "src/utils/diagram_mcp.py",
    "src/utils/gemini_image_mcp.py",
    "src/utils/manim_mcp.py",
    "src/utils/typst_mcp.py"
]

for file in FILES:
    filepath = f"/Users/ayush/Documents/StudyAndContentWorkstation/{file}"
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r') as f:
        content = f.read()
    
    if "from utils.logger import get_logger" not in content:
        content = "from utils.logger import get_logger\nlogger = get_logger(__name__)\n\n" + content
        
    content = re.sub(
        r"(except Exception as e:\n)",
        r"\1        logger.error(f\"MCP Error: {e}\", exc_info=True)\n",
        content
    )
    
    with open(filepath, 'w') as f:
        f.write(content)
    print(f"Patched {filepath}")
