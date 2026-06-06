import os
import json
import logging
import re
from utils.notion_client import NotionAPIClient
from utils.youtube_client import YouTubeClient
from utils.apify_client import ApifySocialClient
from utils.firecrawl_client import FirecrawlAPIClient
from utils.url_classifier import URLClassifier, Platform

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class NotionExtractionTask:
    """
    Orchestrates the extraction of study notes and their attached resources from Notion.
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

    def execute(self):
        try:
            target_db_id = self._parse_database_id()
            client = NotionAPIClient()
            
            logging.info(f"Querying Notion DB: {target_db_id} for 'Done' tasks in 'Week 1'")
            pages = client.fetch_done_tasks(target_db_id, week_filter="Week 1")
            
            if not pages:
                logging.info("No pages found matching the criteria.")
                print(json.dumps({"results": []}))
                return
                
            results = []
            for page in pages:
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
                insights = client.extract_notebooklm_insights(page_id)
                
                # --- LOCAL LAKEHOUSE MIGRATION LOGIC ---
                reference_material = ""
                
                def extract_all_local_files(text):
                    if not text: return []
                    return re.findall(r'file://(/[^\s\n]+)', text)
                    
                local_files = extract_all_local_files(resources_raw) + extract_all_local_files(insights)
                
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
                        extracted = self.youtube_client.extract(url)
                    elif platform == Platform.INSTAGRAM:
                        extracted = self.apify_client.extract_instagram(url)
                    elif platform == Platform.TWITTER:
                        extracted = self.apify_client.extract_twitter(url)
                    elif platform == Platform.LINKEDIN:
                        extracted = self.apify_client.extract_linkedin(url)
                    else:
                        extracted = self.firecrawl_client.scrape_markdown(url)
                        
                    if extracted:
                        reference_material += f"\n\n=== SOURCE: {url} ===\n{extracted}\n"
                
                results.append({
                    "page_id": page_id,
                    "title": title,
                    "notebooklm_insights": insights,
                    "reference_material": reference_material
                })
                
            payload = json.dumps({"results": results}, indent=2)
            print("\n--- JSON OUTPUT FOR RESEARCHER AGENT ---")
            print(payload)
            
        except Exception as e:
            logging.error(f"Failed to execute workflow: {e}")
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    task = NotionExtractionTask()
    task.execute()
