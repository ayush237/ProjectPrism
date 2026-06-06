import os
import re
import logging
from utils.rss_client import RSSFeedClient
from utils.firecrawl_client import FirecrawlAPIClient
from utils.youtube_client import YouTubeClient
from utils.apify_client import ApifySocialClient
from utils.url_classifier import URLClassifier, Platform

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class TrustedSourcesTask:
    """
    Orchestrates fetching data from curated trusted sources and writing to raw txt format.
    """
    def __init__(self):
        self.rss_client = RSSFeedClient()
        self.firecrawl_client = FirecrawlAPIClient()
        self.youtube_client = YouTubeClient()
        self.apify_client = ApifySocialClient()
        
    def extract_urls_from_markdown(self, filepath: str) -> list[str]:
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            return []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Match markdown links: [text](url)
        urls = re.findall(r'\[.*?\]\((https?://.*?)\)', content)
        return urls

    def execute(self):
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'docs'))
        sources_file = os.path.join(docs_dir, 'trusted_sources.md')
        
        urls = self.extract_urls_from_markdown(sources_file)
        if not urls:
            logging.warning("No URLs found in trusted_sources.md")
            return
            
        output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'content_outputs'))
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, 'latest_trends_raw.txt')
        
        logging.info(f"Processing {len(urls)} trusted sources...")
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("=== TRUSTED SOURCES DATA ===\n\n")
                
                for url in urls:
                    # Skip placeholder examples
                    if "placeholder" in url.lower():
                        continue
                        
                    platform = URLClassifier.classify(url)
                    logging.info(f"Scraping {url} (Identified as {platform.value})")
                    
                    extracted_content = None
                    
                    # Heuristic for RSS
                    if "rss" in url.lower() or url.endswith(".xml"):
                        items = self.rss_client.fetch_items(url, limit=10)
                        if items:
                            extracted_content = "RSS ITEMS:\n" + "\n".join([f"- {i['title']}: {i['link']}" for i in items])
                    elif platform == Platform.YOUTUBE:
                        extracted_content = self.youtube_client.extract(url)
                    elif platform == Platform.INSTAGRAM:
                        extracted_content = self.apify_client.extract_instagram(url)
                    elif platform == Platform.TWITTER:
                        extracted_content = self.apify_client.extract_twitter(url)
                    elif platform == Platform.LINKEDIN:
                        extracted_content = self.apify_client.extract_linkedin(url)
                    else:
                        extracted_content = self.firecrawl_client.scrape_markdown(url)
                        
                    if extracted_content:
                        f.write(f"--- SOURCE: {url} ---\n")
                        f.write(f"{extracted_content}\n\n")
                    else:
                        logging.warning(f"Failed to extract content from {url}")
                        
            logging.info(f"Successfully processed trusted sources into {output_path}")
            
        except Exception as e:
            logging.error(f"Failed to write trusted sources data: {e}")

if __name__ == "__main__":
    task = TrustedSourcesTask()
    task.execute()
