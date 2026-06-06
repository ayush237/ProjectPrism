import os
import json
import logging
import urllib.request
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class NotionAPIClient:
    """
    A unified, Object-Oriented client for interacting with the Notion API.
    Handles querying databases and extracting blocks.
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

    def query_database(self, database_id: str, payload: dict = None) -> List[Dict]:
        """
        Queries a Notion database with an optional JSON payload filter.
        """
        import uuid
        try:
            formatted_db_id = str(uuid.UUID(database_id))
        except ValueError:
            formatted_db_id = database_id

        url = f"{self.base_url}/databases/{formatted_db_id}/query"
        data = json.dumps(payload or {}).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data.get('results', [])
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            logging.error(f"Failed to query Notion Database {formatted_db_id}: HTTP {e.code}: {error_msg}")
            return []
        except Exception as e:
            logging.error(f"Failed to query Notion Database {formatted_db_id}: {e}")
            return []

    def fetch_done_tasks(self, database_id: str, week_filter: str = "Week 1") -> List[Dict]:
        """
        Domain-specific method for the Study Workstation: Fetches tasks marked 'Done' for a specific week.
        """
        # Using a raw query, since Notion API filters can be verbose and property names vary.
        # For maximum reliability (as seen in earlier scripts), we pull everything and filter in memory.
        results = self.query_database(database_id)
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

    def extract_notebooklm_insights(self, page_id: str) -> Optional[str]:
        """
        Domain-specific method: Fetches blocks from a page and extracts text under 'NotebookLM Insights'.
        """
        url = f"{self.base_url}/blocks/{page_id}/children"
        req = urllib.request.Request(url, headers=self.headers, method="GET")
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                blocks = data.get("results", [])
        except Exception as e:
            logging.error(f"Failed to fetch blocks for page {page_id}: {e}")
            return None
            
        insights_text = []
        capture = False
        
        for block in blocks:
            block_type = block.get("type")
            if block_type in ["heading_1", "heading_2", "heading_3"]:
                header_content = block[block_type].get("rich_text", [])
                header_text = "".join([t.get("plain_text", "") for t in header_content]).strip()
                
                if "NotebookLM Insights" in header_text:
                    capture = True
                    continue
                elif capture:
                    capture = False # Stop capturing on next header
            
            if capture:
                if block_type == "paragraph":
                    text_content = block[block_type].get("rich_text", [])
                    text = "".join([t.get("plain_text", "") for t in text_content])
                    if text:
                        insights_text.append(text)
                elif block_type in ["bulleted_list_item", "numbered_list_item"]:
                    text_content = block[block_type].get("rich_text", [])
                    text = "".join([t.get("plain_text", "") for t in text_content])
                    if text:
                        insights_text.append(f"- {text}")
                elif block_type == "quote":
                    text_content = block[block_type].get("rich_text", [])
                    text = "".join([t.get("plain_text", "") for t in text_content])
                    if text:
                        insights_text.append(f"> {text}")
        
        return "\n".join(insights_text) if insights_text else None

    def create_page(self, database_id: str, properties: dict) -> Optional[Dict]:
        """
        Creates a new page in a Notion database.
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
        data = json.dumps(payload).encode('utf-8')
        
        req = urllib.request.Request(url, data=data, headers=self.headers, method="POST")
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode('utf-8')
            logging.error(f"Failed to create Notion Page in DB {formatted_db_id}: HTTP {e.code}: {error_msg}")
            return None
        except Exception as e:
            logging.error(f"Failed to create Notion Page in DB {formatted_db_id}: {e}")
            return None
