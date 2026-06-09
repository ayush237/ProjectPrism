import os
import json
import logging
import re
import asyncio
import aiohttp
from utils.notion_client import NotionAPIClient
from utils.youtube_client import YouTubeClient
from utils.apify_client import ApifySocialClient
from utils.firecrawl_client import FirecrawlAPIClient
from utils.url_classifier import URLClassifier, Platform

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class NotionExtractionTask:
    """
    Orchestrates the extraction of study notes and their attached resources from Notion asynchronously.
    """
    def __init__(self):
        self.database_id = os.environ.get("NOTION_DATABASE_ID")
        self.youtube_client = YouTubeClient()
        self.apify_client = ApifySocialClient()
        self.firecrawl_client = FirecrawlAPIClient()
        
    def _parse_database_id(self) -> str:
        if not self.database_id:
            raise ValueError("NOTION_DATABASE_ID environment variable is not set.")
            
        db_id = self.database_id
        if "notion.so" in db_id:
            match = re.search(r'([a-f0-9]{32})', db_id.replace('-', ''))
            if match:
                db_id = match.group(1)
            else:
                raise ValueError("Could not extract a valid 32-character Database ID from the provided URL.")
                
        import uuid
        try:
            return str(uuid.UUID(db_id))
        except Exception:
            raise ValueError("Invalid NOTION_DATABASE_ID format.")

    async def process_page(self, session, client, page):
        try:
            page_id = page["id"]
            title = "Untitled"
            properties = page.get("properties", {})
            
            # Extract Title
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title":
                    title_parts = prop_data.get("title", [])
                    if title_parts:
                        title = "".join([t.get("plain_text", "") for t in title_parts])
                    break
                    
            # Extract Resources
            resources_raw = ""
            for prop_name, prop_data in properties.items():
                if prop_name.lower() == "resources":
                    if prop_data.get("type") == "rich_text":
                        rich_texts = prop_data.get("rich_text", [])
                        resources_raw = "".join([t.get("plain_text", "") for t in rich_texts])
                    elif prop_data.get("type") == "url":
                        resources_raw = prop_data.get("url", "")
                    break
                    
            logging.info(f"Processing page: '{title}' ({page_id})")
            user_notes, agent_directives = await client.extract_page_content(session, page_id)
            
            # --- LOCAL LAKEHOUSE MIGRATION LOGIC ---
            reference_material = ""
            
            def extract_all_local_files(text):
                if not text: return []
                return re.findall(r'file://(/[^\s\n]+)', text)
                
            local_files = extract_all_local_files(resources_raw) + extract_all_local_files(user_notes) + extract_all_local_files(agent_directives)
            
            for filepath in set(local_files):
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            reference_material += f"\n\n=== LOCAL ARCHIVE: {filepath} ===\n{content}\n"
                            logging.info(f"Appended Local Lakehouse Archive: {filepath}")
                    except Exception as e:
                        logging.error(f"Failed to read local archive {filepath}: {e}")

            # Scrape External Links
            urls = [u.strip() for u in re.split(r'[,\n\s]+', resources_raw) if u.strip().startswith('http')]
            
            for url in urls:
                platform = URLClassifier.classify(url)
                logging.info(f"Extracting resource [{platform.value}]: {url}")
                extracted = None
                if platform == Platform.YOUTUBE:
                    extracted = await self.youtube_client.extract(url)
                elif platform == Platform.INSTAGRAM:
                    extracted = await self.apify_client.extract_instagram(url)
                elif platform == Platform.TWITTER:
                    extracted = await self.apify_client.extract_twitter(url)
                elif platform == Platform.LINKEDIN:
                    extracted = await self.apify_client.extract_linkedin(url)
                else:
                    extracted = await self.firecrawl_client.scrape_markdown(url, session)
                    
                if extracted:
                    reference_material += f"\n\n=== SOURCE: {url} ===\n{extracted}\n"
            
            return {
                "page_id": page_id,
                "title": title,
                "user_notes": user_notes,
                "agent_directives": agent_directives,
                "reference_material": reference_material
            }
        except Exception as e:
            logging.error(f"Failed to process page {page.get('id', 'Unknown')}: {e}")
            return None

    async def run_pipeline(self):
        try:
            target_db_id = self._parse_database_id()
            client = NotionAPIClient()
            
            async with aiohttp.ClientSession() as session:
                logging.info(f"Querying Notion DB: {target_db_id} for 'Done' tasks in 'Week 1'")
                pages = await client.fetch_done_tasks(session, target_db_id, week_filter="Week 1")
                
                if not pages:
                    logging.info("No pages found matching the criteria.")
                    print(json.dumps({"results": []}))
                    return
                    
                # Execute all pages concurrently
                tasks = [self.process_page(session, client, page) for page in pages]
                results_raw = await asyncio.gather(*tasks)
                
                # Filter out failures
                results = [r for r in results_raw if r is not None]
                
                payload = json.dumps({"results": results}, indent=2)
                print("\n--- JSON OUTPUT FOR RESEARCHER AGENT ---")
                print(payload)
            
        except Exception as e:
            logging.error(f"Failed to execute workflow: {e}")
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    task = NotionExtractionTask()
    asyncio.run(task.run_pipeline())
