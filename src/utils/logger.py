import os
import logging
from logging.handlers import RotatingFileHandler

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOGS_DIR = os.path.join(ROOT_DIR, 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, 'prism_system.log')

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] - %(message)s')
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        # Prevent propagation to the root logger to avoid duplicate prints if root is configured
        logger.propagate = False
        
    return logger
