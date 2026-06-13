import urllib.request
import xml.etree.ElementTree as ET
import ssl
import logging
from utils.logger import get_logger
logger = get_logger(__name__)
from typing import List, Dict

class RSSFeedClient:
    """
    A unified, Object-Oriented client for fetching and parsing RSS feeds.
    Handles unverified SSL contexts for reliable local execution.
    """
    def __init__(self, user_agent: str = 'Mozilla/5.0 (AI Content Engine)'):
        self.user_agent = user_agent
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE

    def fetch_items(self, url: str, limit: int = 15) -> List[Dict[str, str]]:
        """
        Fetches the RSS feed and extracts the top N items with title and link.
        """
        req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
        
        try:
            with urllib.request.urlopen(req, context=self.ctx) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            items = []
            
            for item in root.findall('.//item')[:limit]:
                title_elem = item.find('title')
                link_elem = item.find('link')
                
                title = title_elem.text if title_elem is not None else "Untitled"
                link = link_elem.text if link_elem is not None else ""
                
                items.append({
                    "title": title,
                    "link": link
                })
                
            return items
        except Exception as e:
            logger.error(f"Failed to fetch or parse RSS feed at {url}: {e}", exc_info=True)
            return []
