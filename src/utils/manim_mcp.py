import os
import sys
import uuid
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Manim MCP")

@mcp.tool()
def compile_manim_scene(python_code: str, scene_class_name: str, output_name: str) -> str:
    """Compiles raw Python code containing a Manim Scene class into an MP4 video.
    
    Args:
        python_code: The raw Python code containing the Manim imports and Scene class definition.
        scene_class_name: The exact name of the Scene class to render (e.g., "AnimatedDiagram").
        output_name: A base name for the output MP4 file (without extension).
    """
    save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'mcp_assets'))
    os.makedirs(save_dir, exist_ok=True)
    
    unique_id = uuid.uuid4().hex[:8]
    temp_py_file = os.path.join(save_dir, f"{output_name}_{unique_id}.py")
    
    # Write the dynamic python code
    with open(temp_py_file, 'w', encoding='utf-8') as f:
        f.write(python_code)
        
    try:
        # Execute manim temp.py scene_name -qm (medium quality) --format=mp4 -o out_name
        # --media_dir sets where manim drops its output
        media_dir = os.path.join(save_dir, f"media_{unique_id}")
        
        cmd = [
            sys.executable,
            "-m", "manim",
            temp_py_file,
            scene_class_name,
            "-qm",
            "--media_dir", media_dir,
            "-o", f"{output_name}_{unique_id}.mp4"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return f"Manim compilation failed: {result.stderr}\n\nStdout: {result.stdout}"
            
        # Manim creates deep directory structures: media/videos/temp_py_file/720p30/out_name.mp4
        # We need to locate the actual MP4 file generated
        compiled_mp4_path = None
        for root, dirs, files in os.walk(media_dir):
            for file in files:
                if file.endswith(f"{output_name}_{unique_id}.mp4"):
                    compiled_mp4_path = os.path.join(root, file)
                    break
        
        if compiled_mp4_path:
            return f"Scene compiled successfully. Saved to: {compiled_mp4_path}"
        else:
            return f"Compilation succeeded, but output file could not be located in {media_dir}. Stdout: {result.stdout}"
            
    except Exception as e:
        return f"Error running Manim: {str(e)}"

if __name__ == "__main__":
    mcp.run()
