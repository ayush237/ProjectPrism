import os
import json
import logging
import urllib.request
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class FirecrawlAPIClient:
    """
    A unified, Object-Oriented client for interacting with the Firecrawl API.
    Handles web scraping and bypassing anti-bot measures.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("FIRECRAWL_API_KEY")
        if not self.api_key:
            logging.warning("FIRECRAWL_API_KEY is missing. Scraping capabilities may be limited.")
            
        self.base_url = "https://api.firecrawl.dev/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def scrape_markdown(self, url: str, session) -> Optional[str]:
        """
        Scrapes the given URL and returns the content in markdown format asynchronously.
        """
        if not self.api_key:
            logging.error("Cannot scrape: FIRECRAWL_API_KEY is not set.")
            return None

        api_url = f"{self.base_url}/scrape"
        payload = {"url": url, "formats": ["markdown"]}
        
        try:
            async with session.post(api_url, json=payload, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get('data', {}).get('markdown', '')
        except Exception as e:
            logging.error(f"Firecrawl scraping failed for {url}: {e}")
            return None
