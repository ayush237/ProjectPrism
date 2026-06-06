import os
import sys
import argparse
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def write_archive(filename, content):
    """
    Saves exhaustive research to the Local Lakehouse archive and returns the absolute URI.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    archive_dir = os.path.join(base_dir, 'docs', 'research_archive')
    
    os.makedirs(archive_dir, exist_ok=True)
    
    if not filename.endswith('.md'):
        filename += '.md'
        
    file_path = os.path.join(archive_dir, filename)
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Output the absolute file URI so the Researcher knows exactly what to pass to Notion
        print("=== SUCCESS: ARCHIVE SAVED ===")
        print(f"ABSOLUTE PATH: file://{file_path}")
        print("You must append this path to the Virality Database row using write_notion_row.py")
    except Exception as e:
        logging.error(f"Failed to write archive: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Save exhaustive research to the Local Lakehouse archive.")
    parser.add_argument("--filename", type=str, required=True, help="The date-prefixed filename (e.g. 2026-06-11_topic.md)")
    
    args, unknown = parser.parse_known_args()
    
    # Read from stdin
    content = sys.stdin.read()
        
    if not content.strip():
        logging.error("No content provided via stdin.")
        sys.exit(1)
        
    write_archive(args.filename, content)
