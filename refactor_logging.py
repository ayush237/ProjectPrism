import os
import re

SRC_DIR = "/Users/ayush/Documents/StudyAndContentWorkstation/src"

def refactor_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original = content
    
    # Replace basicConfig
    content = re.sub(
        r"logging\.basicConfig\(.*?\)", 
        "from utils.logger import get_logger\nlogger = get_logger(__name__)", 
        content
    )
    
    # If the file didn't have basicConfig but uses logging, add the logger
    if "from utils.logger import get_logger" not in content and "logging." in content:
        content = re.sub(
            r"(import logging\n)", 
            r"\1from utils.logger import get_logger\nlogger = get_logger(__name__)\n", 
            content
        )
        
    # Replace logging.xxx with logger.xxx
    content = content.replace("logging.info(", "logger.info(")
    content = content.replace("logging.warning(", "logger.warning(")
    content = content.replace("logging.debug(", "logger.debug(")
    
    # For error, add exc_info=True
    content = re.sub(r"logging\.error\((.*?)\)", r"logger.error(\1, exc_info=True)", content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Refactored {filepath}")

for root, _, files in os.walk(SRC_DIR):
    for f in files:
        if f.endswith('.py') and f != 'logger.py':
            refactor_file(os.path.join(root, f))
