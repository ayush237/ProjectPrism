import os
import asyncio
import logging
from typing import Optional
from apify_client import ApifyClient
from dotenv import load_dotenv

load_dotenv()

class ApifySocialClient:
    """
    Extracts data from locked social networks (Instagram, X/Twitter, LinkedIn) using Apify actors.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("APIFY_API_TOKEN")
        if not self.api_key:
            logging.error("APIFY_API_TOKEN is not set.")
            self.client = None
        else:
            self.client = ApifyClient(self.api_key)
            
    async def extract_instagram(self, url: str) -> Optional[str]:
        if not self.client: return None
        logging.info(f"Extracting Instagram via Apify: {url}")
        
        # Using a popular Instagram scraper actor
        actor_id = "apify/instagram-scraper"
        run_input = {
            "directUrls": [url],
            "resultsType": "details",
            "searchType": "hashtag",
            "searchLimit": 1
        }
        
        return await asyncio.to_thread(self._run_actor_and_format, actor_id, run_input, "Instagram")
        
    async def extract_twitter(self, url: str) -> Optional[str]:
        if not self.client: return None
        logging.info(f"Extracting Twitter/X via Apify: {url}")
        
        # Using a popular Twitter scraper actor
        actor_id = "microworlds/twitter-scraper"
        run_input = {
            "searchTerms": [url],
            "maxItems": 1
        }
        
        return await asyncio.to_thread(self._run_actor_and_format, actor_id, run_input, "Twitter/X")
        
    async def extract_linkedin(self, url: str) -> Optional[str]:
        if not self.client: return None
        logging.info(f"Extracting LinkedIn via Apify: {url}")
        
        # Using a popular LinkedIn scraper actor
        actor_id = "curious_coder/linkedin-post-scraper"
        run_input = {
            "urls": [url]
        }
        
        return await asyncio.to_thread(self._run_actor_and_format, actor_id, run_input, "LinkedIn")
        
    def _run_actor_and_format(self, actor_id: str, run_input: dict, platform: str) -> Optional[str]:
        try:
            # Run the Actor and wait for it to finish
            run = self.client.actor(actor_id).call(run_input=run_input)
            
            # Fetch and format results
            output = f"# {platform} Extraction\n\n"
            has_data = False
            
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                has_data = True
                
                # Dynamic metadata extraction based on whatever the actor returns
                output += "## Metadata\n"
                
                # Common metadata fields across different actors
                metrics = ['likesCount', 'commentsCount', 'viewsCount', 'retweets', 'replies']
                for m in metrics:
                    if m in item and item[m] is not None:
                        output += f"- **{m}:** {item[m]}\n"
                        
                if 'author' in item or 'ownerFullName' in item:
                    author = item.get('author', item.get('ownerFullName', 'Unknown'))
                    output += f"- **Author:** {author}\n"
                
                output += "\n## Content\n"
                
                # Common text fields
                text = item.get('caption', item.get('text', item.get('full_text', 'No text found.')))
                output += f"{text}\n\n"
                
            if not has_data:
                logging.warning(f"Apify {platform} extraction returned no data.")
                return None
                
            return output
            
        except Exception as e:
            logging.error(f"Apify {platform} extraction failed: {e}")
            return None
