import os
import json
import logging
from utils.notion_client import NotionAPIClient
from utils.firecrawl_client import FirecrawlAPIClient
from utils.youtube_client import YouTubeClient
from utils.apify_client import ApifySocialClient
from utils.url_classifier import URLClassifier, Platform

from utils.logger import get_logger
logger = get_logger(__name__)s: %(message)s')

class SocialDumpTask:
    """
    Orchestrates the fetching and intelligent scraping of saved social media URLs from Notion.
    """
    def __init__(self):
        self.database_id = os.environ.get("SOCIAL_DUMP_DB_ID")
        if not self.database_id:
            logger.error("SOCIAL_DUMP_DB_ID environment variable is not set.", exc_info=True)
            
        try:
            self.notion_client = NotionAPIClient()
            self.firecrawl_client = FirecrawlAPIClient()
            self.youtube_client = YouTubeClient()
            self.apify_client = ApifySocialClient()
        except ValueError as e:
            logger.error(f"Client initialization failed: {e}", exc_info=True)
            self.notion_client = None
            
    def execute(self):
        if not self.database_id or not self.notion_client:
            return

        logger.info("Initiating Intelligent Social Dump pipeline...")
        records = self.notion_client.query_database(self.database_id)
        
        if not records:
            logger.info("No records found in the Social Dump database.")
            return

        for record in records:
            props = record.get('properties', {})
            title = None
            url = None
            notes = None
            
            for prop_name, prop_data in props.items():
                if prop_data.get('type') == 'title':
                    title_arr = prop_data.get('title', [])
                    if title_arr:
                        title = "".join([t.get('plain_text', '') for t in title_arr])
                elif prop_data.get('type') == 'url':
                    url = prop_data.get('url')
                elif prop_data.get('type') == 'rich_text' and prop_name.lower() == 'url':
                    url_arr = prop_data.get('rich_text', [])
                    if url_arr:
                        url = "".join([t.get('plain_text', '') for t in url_arr])
                elif prop_data.get('type') == 'rich_text' and prop_name.lower() == 'notes':
                    notes_arr = prop_data.get('rich_text', [])
                    if notes_arr:
                        notes = "".join([t.get('plain_text', '') for t in notes_arr])

            # If URL property was empty but they pasted a URL into the Title column
            if not url and title and title.startswith('http'):
                url = title
                title = None
                
            # --- LOCAL LAKEHOUSE MIGRATION LOGIC ---
            local_archive_content = None
            import re
            def extract_local_file(text):
                if not text: return None
                match = re.search(r'file://(/[^\s\n]+)', text)
                if match:
                    filepath = match.group(1)
                    if os.path.exists(filepath):
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                return f.read()
                        except Exception as e:
                            logger.error(f"Failed to read local archive {filepath}: {e}", exc_info=True)
                return None

            local_archive_content = extract_local_file(notes) or extract_local_file(url)
            
            if not url and not local_archive_content:
                continue
                
            extracted_content = None
            platform_value = "LOCAL_ARCHIVE"
            
            if local_archive_content:
                logger.info(f"Detected Local Lakehouse Archive in record: {title or 'Untitled'}")
                extracted_content = local_archive_content
                if not url:
                    url = "Local File"
            else:
                platform = URLClassifier.classify(url)
                platform_value = platform.value
                logger.info(f"Scraping URL: {url} (Identified as {platform_value})")
                
                if platform == Platform.YOUTUBE:
                    extracted_content = self.youtube_client.extract(url)
                elif platform == Platform.INSTAGRAM:
                    extracted_content = self.apify_client.extract_instagram(url)
                elif platform == Platform.TWITTER:
                    extracted_content = self.apify_client.extract_twitter(url)
                elif platform == Platform.LINKEDIN:
                    extracted_content = self.apify_client.extract_linkedin(url)
                else:
                    # Fallback to Firecrawl for Blogs and GitHub
                    extracted_content = self.firecrawl_client.scrape_markdown(url)
            
            if not extracted_content:
                logger.warning(f"Failed to extract content from {url}")
                continue
                
            # Cleanly tag the output so the Manager Agent knows how to route it
            dump_type = "VIRALITY IDEA" if title or notes else "RAW SOCIAL DUMP"
            print(f"=== BEGIN {dump_type} ===")
            if title:
                print(f"Title: {title}")
            print(f"URL: {url}")
            print(f"Platform: {platform.value}")
            if notes:
                print(f"User Notes:\n{notes}\n")
            print("Extracted Content:")
            print(extracted_content)
            print(f"=== END {dump_type} ===\n")

if __name__ == "__main__":
    task = SocialDumpTask()
    task.execute()
