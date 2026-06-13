import os
import argparse
import asyncio
import aiohttp
import json
import logging
import uuid
from dotenv import load_dotenv
from google import genai
from utils.notion_client import NotionAPIClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

async def draft_content(client, prompt: str, system_instruction: str) -> str:
    response = await client.aio.models.generate_content(
        model='gemini-3.1-pro-preview',
        contents=prompt,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7
        )
    )
    return response.text

async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, required=True, choices=["ideation", "deep_dive"])
    args = parser.parse_args()
    
    seed_db = os.environ.get("TOPICS_SEED_DB_ID")
    archive_db = os.environ.get("RESEARCH_ARCHIVE_DB_ID")
    
    if not seed_db or not archive_db:
        logger.error("Missing TOPICS_SEED_DB_ID or RESEARCH_ARCHIVE_DB_ID in .env")
        return
        
    notion_client = NotionAPIClient()
    from google.genai import types
    retry_config = types.HttpRetryOptions(
        initial_delay=2.0,  # Start with a 2-second delay
        attempts=5          # Retry up to 5 times with exponential backoff
    )
    llm_client = genai.Client(http_options={'retry_options': retry_config})
    
    async with aiohttp.ClientSession() as session:
        if args.mode == "ideation":
            logger.info("Starting Ideation phase...")
            trusted_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "trusted_sources.md"))
            try:
                with open(trusted_path, "r", encoding="utf-8") as f:
                    trusted_content = f.read()
            except FileNotFoundError:
                logger.error("trusted_sources.md not found.")
                return
                
            prompt = f"Analyze these trusted sources:\n{trusted_content}\n\nExtract and propose exactly 7 distinct technical topics (e.g. 'RAG Implementations', 'Agentic Workflows'). Output ONLY a JSON array of strings, e.g. [\"Topic 1\", \"Topic 2\"]."
            
            topics_json = await draft_content(llm_client, prompt, "You are a senior technical content ideator. Output only JSON.")
            try:
                clean_json = topics_json.replace("```json", "").replace("```", "").strip()
                topics = json.loads(clean_json)
                logger.info(f"Generated {len(topics)} topics.")
                
                # Write to Table D
                for topic in topics:
                    properties = {
                        "Topic Name": {"title": [{"text": {"content": topic}}]}
                    }
                    await notion_client.create_page(session, seed_db, properties)
                    logger.info(f"Pushed '{topic}' to Table D.")
            except Exception as e:
                logger.error(f"Failed to parse or upload topics: {e}\nRaw output: {topics_json}")

        elif args.mode == "deep_dive":
            logger.info("Starting Deep Dive phase...")
            pages = await notion_client.fetch_done_tasks(session, seed_db)
            if not pages:
                logger.info("No unprocessed topics found in Table D.")
                return
                
            for page in pages:
                page_id = page["id"]
                props = page.get("properties", {})
                title_prop = props.get("Name", {})
                title = "Untitled"
                if title_prop.get("type") == "title":
                    title_parts = title_prop.get("title", [])
                    if title_parts:
                        title = "".join([t.get("plain_text", "") for t in title_parts])
                
                logger.info(f"Executing Deep Dive for topic: {title}")
                
                prompt = f"Execute a comprehensive technical deep dive on the following topic: {title}. Explain the core concepts, modern architectures, best practices, and code structure if applicable. Provide a massive text response."
                deep_dive_text = await draft_content(llm_client, prompt, "You are a distinguished Principal Engineer performing deep research.")
                
                cat_prompt = f"Given this deep dive, classify it into a single category word (e.g. 'Evergreen', 'Latest', 'Architecture', 'AI'). Output ONLY the word.\n\n{deep_dive_text[:1000]}"
                category = (await draft_content(llm_client, cat_prompt, "You are a taxonomy expert. Output a single word.")).strip()
                
                safe_title = "".join([c if c.isalnum() else "_" for c in title])
                filename = f"{safe_title}_{uuid.uuid4().hex[:6]}.txt"
                
                sub_dir = "latest" if "latest" in category.lower() else "evergreen"
                save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "research", "schedules", sub_dir))
                os.makedirs(save_dir, exist_ok=True)
                
                save_path = os.path.join(save_dir, filename)
                
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(deep_dive_text)
                    
                logger.info(f"Saved deep dive to {save_path}")
                
                # Push metadata to Table C
                properties = {
                    "Name": {"title": [{"text": {"content": title}}]},
                    "Category": {"select": {"name": category}},
                    "Reel Format": {"select": {"name": "Spoken"}}, 
                    "Local Path": {"url": save_path},
                    "Status": {"status": {"name": "Done"}},
                    "Pipeline Processed": {"checkbox": False}
                }
                await notion_client.create_page(session, archive_db, properties)
                
                # Mark Table D row as processed
                await notion_client.mark_page_as_processed(session, page_id)
                logger.info(f"Marked topic '{title}' as processed in Table D.")

if __name__ == "__main__":
    asyncio.run(main())
