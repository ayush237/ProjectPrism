import os
import json
import logging
import asyncio
import hashlib
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from google import genai

load_dotenv()


class NotionAPIClient:
    """
    A unified, Object-Oriented client for interacting with the Notion API.
    Handles querying databases and extracting blocks via aiohttp asynchronously.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
        if not self.api_key:
            raise ValueError("Missing NOTION API key in environment variables.")
            
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }

    async def query_database(self, session, database_id: str, payload: dict = None) -> List[Dict]:
        """
        Queries a Notion database with an optional JSON payload filter asynchronously.
        """
        import uuid
        try:
            formatted_db_id = str(uuid.UUID(database_id))
        except ValueError:
            formatted_db_id = database_id

        url = f"{self.base_url}/databases/{formatted_db_id}/query"
        data = payload or {}
        
        try:
            async with session.post(url, json=data, headers=self.headers) as response:
                if response.status != 200:
                    error_msg = await response.text()
                    logging.error(f"Failed to query Notion Database {formatted_db_id}: HTTP {response.status}: {error_msg}")
                    return []
                response_data = await response.json()
                return response_data.get('results', [])
        except Exception as e:
            logging.error(f"Failed to query Notion Database {formatted_db_id}: {e}")
            return []

    async def fetch_done_tasks(self, session, database_id: str, week_filter: str = "Week 1") -> List[Dict]:
        """
        Domain-specific method for the Study Workstation: Fetches tasks marked 'Done' for a specific week.
        """
        results = await self.query_database(session, database_id)
        filtered_pages = []
        
        for page in results:
            props = page.get("properties", {})
            
            # Extract Status
            status_prop = props.get("Status", {})
            status_val = None
            if status_prop.get("type") == "status":
                status_val = status_prop.get("status", {}).get("name")
            elif status_prop.get("type") == "select":
                select_obj = status_prop.get("select")
                if select_obj:
                    status_val = select_obj.get("name")
                    
            # Extract Week
            week_prop = props.get("Week", {})
            week_val = None
            if week_prop.get("type") == "select":
                select_obj = week_prop.get("select")
                if select_obj:
                    week_val = select_obj.get("name")
            elif week_prop.get("type") == "rich_text":
                rich_text = week_prop.get("rich_text", [])
                if rich_text:
                    week_val = "".join([t.get("plain_text", "") for t in rich_text])
                    
            if status_val == "Done" and week_val == week_filter:
                filtered_pages.append(page)
                
        return filtered_pages

    async def _perform_ocr(self, session, image_url: str, block_id: str) -> str:
        cache_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'temp', 'ocr_cache'))
        os.makedirs(cache_dir, exist_ok=True)
        cache_file = os.path.join(cache_dir, f"{block_id}.txt")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return f.read()
                
        try:
            async with session.get(image_url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                response.raise_for_status()
                image_bytes = await response.read()
                
            client = genai.Client()
            response = await client.aio.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    'Transcribe any text, handwriting, or diagrams from the image.',
                    {'mime_type': 'image/jpeg', 'data': image_bytes}
                ]
            )
            ocr_text = response.text
            with open(cache_file, 'w', encoding='utf-8') as f:
                f.write(ocr_text)
            return ocr_text
        except Exception as e:
            logging.error(f"OCR failed for block {block_id}: {e}")
            return ""

    async def extract_page_content(self, session, page_id: str) -> Tuple[str, str]:
        """
        Extracts content from a Notion page, including Multimodal OCR for images concurrently.
        Returns a tuple: (user_notes, agent_directives)
        """
        url = f"{self.base_url}/blocks/{page_id}/children"
        
        try:
            async with session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                data = await response.json()
                blocks = data.get("results", [])
        except Exception as e:
            logging.error(f"Failed to fetch blocks for page {page_id}: {e}")
            return "", ""
            
        user_notes_lines = []
        agent_directives_lines = []
        
        current_section = None
        
        # We need to collect image blocks to process them concurrently
        image_blocks_info = []

        for block in blocks:
            block_type = block.get("type")
            
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                header_content = block[block_type].get("rich_text", [])
                header_text = "".join([t.get("plain_text", "") for t in header_content]).strip()
                if "@Notes" in header_text:
                    current_section = 'notes'
                    continue
                elif "@Prism" in header_text:
                    current_section = 'prism'
                    continue
                else:
                    current_section = None
                    
            if not current_section:
                continue
                
            if block_type == "image":
                image_obj = block.get("image", {})
                image_url = None
                if image_obj.get("type") == "file":
                    image_url = image_obj.get("file", {}).get("url")
                elif image_obj.get("type") == "external":
                    image_url = image_obj.get("external", {}).get("url")
                    
                if image_url:
                    image_blocks_info.append({
                        "block_id": block.get("id"),
                        "url": image_url,
                        "section": current_section
                    })

        # Process all OCR concurrently
        ocr_tasks = [self._perform_ocr(session, info["url"], info["block_id"]) for info in image_blocks_info]
        ocr_results = await asyncio.gather(*ocr_tasks)
        ocr_map = {info["block_id"]: res for info, res in zip(image_blocks_info, ocr_results)}

        # Second pass to build the final text
        current_section = None
        
        for block in blocks:
            block_type = block.get("type")
            
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                header_content = block[block_type].get("rich_text", [])
                header_text = "".join([t.get("plain_text", "") for t in header_content]).strip()
                if "@Notes" in header_text:
                    current_section = 'notes'
                    continue
                elif "@Prism" in header_text:
                    current_section = 'prism'
                    continue
                else:
                    current_section = None
                    
            if not current_section:
                continue
                
            appended_text = ""
            
            if block_type == "paragraph":
                text_content = block[block_type].get("rich_text", [])
                appended_text = "".join([t.get("plain_text", "") for t in text_content])
            elif block_type in ["bulleted_list_item", "numbered_list_item"]:
                text_content = block[block_type].get("rich_text", [])
                appended_text = "- " + "".join([t.get("plain_text", "") for t in text_content])
            elif block_type == "quote":
                text_content = block[block_type].get("rich_text", [])
                appended_text = "> " + "".join([t.get("plain_text", "") for t in text_content])
            elif block_type == "image":
                block_id = block.get("id")
                ocr_text = ocr_map.get(block_id)
                if ocr_text:
                    appended_text = f"[Extracted from Screenshot]: {ocr_text}"
                        
            if appended_text:
                if current_section == 'notes':
                    user_notes_lines.append(appended_text)
                elif current_section == 'prism':
                    agent_directives_lines.append(appended_text)
                    
        return "\n".join(user_notes_lines), "\n".join(agent_directives_lines)

    async def create_page(self, session, database_id: str, properties: dict) -> Optional[Dict]:
        """
        Creates a new page in a Notion database asynchronously.
        """
        import uuid
        try:
            formatted_db_id = str(uuid.UUID(database_id))
        except ValueError:
            formatted_db_id = database_id

        url = f"{self.base_url}/pages"
        payload = {
            "parent": {"database_id": formatted_db_id},
            "properties": properties
        }
        
        try:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status not in [200, 201]:
                    error_msg = await response.text()
                    logging.error(f"Failed to create Notion Page in DB {formatted_db_id}: HTTP {response.status}: {error_msg}")
                    return None
                return await response.json()
        except Exception as e:
            logging.error(f"Failed to create Notion Page in DB {formatted_db_id}: {e}")
            return None
