import os
import argparse
import asyncio
import aiohttp
import logging
from dotenv import load_dotenv
from google import genai

from utils.notion_client import NotionAPIClient

# Configure logging
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
    parser = argparse.ArgumentParser(description="Tri-Modal Pipeline Trigger")
    parser.add_argument("--mode", type=str, required=True, choices=["study", "series", "virality", "research"])
    args = parser.parse_args()
    
    # Determine Database ID
    db_id = None
    if args.mode == "study":
        db_id = os.environ.get("STUDY_MATERIAL_DB_ID")
    elif args.mode == "series":
        db_id = os.environ.get("NOTION_SERIES_DB_ID")
    elif args.mode == "virality":
        db_id = os.environ.get("SOCIAL_DUMP_DB_ID")
    elif args.mode == "research":
        db_id = os.environ.get("RESEARCH_ARCHIVE_DB_ID")
        
    if not db_id:
        logger.error(f"Missing Database ID for mode: {args.mode}")
        return
        
    # Read Agent Prompts
    insta_prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents", "sub-agents", "instagram_agent.md"))
    linkedin_prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agents", "sub-agents", "linkedin_agent.md"))
    
    with open(insta_prompt_path, 'r', encoding='utf-8') as f:
        insta_sys = f.read()
    with open(linkedin_prompt_path, 'r', encoding='utf-8') as f:
        linkedin_sys = f.read()
        
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "content_outputs", args.mode))
    os.makedirs(out_dir, exist_ok=True)
    
    notion_client = NotionAPIClient()
    from google.genai import types
    retry_config = types.HttpRetryOptions(
        initial_delay=2.0,  # Start with a 2-second delay
        attempts=5          # Retry up to 5 times with exponential backoff
    )
    llm_client = genai.Client(http_options={'retry_options': retry_config})
    
    async with aiohttp.ClientSession() as session:
        logger.info(f"Querying Database {db_id} for mode '{args.mode}'")
        pages = await notion_client.fetch_done_tasks(session, db_id)
        
        if not pages:
            logger.info("No unprocessed 'Done' tasks found.")
            return
            
        logger.info(f"Found {len(pages)} tasks to process.")
        
        content_generated = False
        generated_pages = []
        
        for page in pages:
            page_id = page["id"]
            
            # Extract Title
            props = page.get("properties", {})
            title_prop = props.get("Name", {})
            title = "Untitled"
            if title_prop.get("type") == "title":
                title_parts = title_prop.get("title", [])
                if title_parts:
                    title = "".join([t.get("plain_text", "") for t in title_parts])
            
            # Extract Reel Format
            reel_format = "Spoken"
            for prop_name, prop_data in props.items():
                if prop_name == "Reel Format" and prop_data.get("type") == "select":
                    select_data = prop_data.get("select")
                    if select_data:
                        reel_format = select_data.get("name", "Spoken")
                    break
                    
            # Extract Assigned Series Relation
            assigned_series_prop = props.get("Assigned Series", {})
            series_page_id = None
            if assigned_series_prop.get("type") == "relation":
                relations = assigned_series_prop.get("relation", [])
                if relations:
                    series_page_id = relations[0].get("id")
                    
            series_directive = ""
            current_count = 0
            
            if series_page_id:
                logger.info(f"Relational link found. Fetching Series page: {series_page_id}")
                series_page = await notion_client.get_page(session, series_page_id)
                if series_page:
                    sprops = series_page.get("properties", {})
                    
                    sname_prop = sprops.get("Name", {})
                    series_name = ""
                    if sname_prop.get("type") == "title":
                        series_name = "".join([t.get("plain_text", "") for t in sname_prop.get("title", [])])
                        
                    sdesc_prop = sprops.get("Description", {})
                    sdesc = ""
                    if sdesc_prop.get("type") == "rich_text":
                        sdesc = "".join([t.get("plain_text", "") for t in sdesc_prop.get("rich_text", [])])
                        
                    scount_prop = sprops.get("Current Count", {})
                    if scount_prop.get("type") == "number":
                        current_count = scount_prop.get("number")
                        if current_count is None: current_count = 0
                        
                    if series_name:
                        ep_number = current_count + 1
                        series_directive = f"\n\nCRITICAL SERIES DIRECTIVE: This draft is explicitly Episode {ep_number} of the '{series_name}' series. The specific tone/branding for this series is: {sdesc}. You must format your hook and outro to clearly reflect this episode number and branding."
            
            logger.info(f"Processing page {page_id} with format {reel_format}")
            
            # Extract Brief
            if args.mode == "research":
                local_path = None
                for prop_name, prop_data in props.items():
                    if prop_name == "Local Path" and prop_data.get("type") == "url":
                        local_path = prop_data.get("url")
                        break
                if local_path and os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8") as f:
                        brief = f.read()
                else:
                    logger.warning(f"Local file not found for research mode page {page_id}. Skipping.")
                    continue
            else:
                user_notes, agent_directives = await notion_client.extract_page_content(session, page_id)
                brief = f"User Notes:\n{user_notes}\n\nAgent Directives:\n{agent_directives}"
            
            prompt = f"Content Type / Mode: {args.mode}\nReel Format: {reel_format}\n\nBrief:\n{brief}{series_directive}"
            
            try:
                logger.info("Drafting Instagram Content...")
                insta_content = await draft_content(llm_client, prompt, insta_sys)
                
                logger.info("Drafting LinkedIn Content...")
                linkedin_content = await draft_content(llm_client, prompt, linkedin_sys)
                
                insta_path = os.path.join(out_dir, f"{page_id}_instagram.md")
                linkedin_path = os.path.join(out_dir, f"{page_id}_linkedin.md")
                
                with open(insta_path, 'w', encoding='utf-8') as f:
                    f.write(insta_content)
                with open(linkedin_path, 'w', encoding='utf-8') as f:
                    f.write(linkedin_content)
                    
                logger.info("Outputs saved successfully.")
                
                # Two-Way Sync Handshake
                await notion_client.mark_page_as_processed(session, page_id)
                logger.info(f"Page {page_id} successfully processed and marked in Notion.")
                content_generated = True
                generated_pages.append((page_id, title, reel_format, insta_content, linkedin_content, series_page_id, current_count))
                
            except Exception as e:
                logger.error(f"Failed to process page {page_id}: {e}", exc_info=True)
                
        if content_generated:
            logger.info("Content was generated. Triggering cascading notifications...")
            import subprocess
            import re
            
            pr_url = ""
            try:
                result = subprocess.run(["python3", "src/utils/github_pr_creator.py"], capture_output=True, text=True, check=True)
                logger.info(f"github_pr_creator.py output: {result.stdout}")
                match = re.search(r"PR_URL:\s*(https://[^\s]+)", result.stdout)
                if match:
                    pr_url = match.group(1)
            except Exception as e:
                logger.error(f"Failed to create GitHub PR: {e}", exc_info=True)
                
            kanban_db = os.environ.get("CONTENT_KANBAN_DB_ID")
            
            email_body_html = "<html><body style='font-family: sans-serif;'>"
            
            for page_id, title, reel_format, insta, linkedin, series_id, count in generated_pages:
                notion_deep_link = ""
                if kanban_db:
                    kanban_props = {
                        "Name": {"title": [{"text": {"content": f"[{args.mode.capitalize()}] [{reel_format}] {title}"}}]},
                        "Stage": {"select": {"name": "Parked"}}
                    }
                    if pr_url:
                        kanban_props["Content Drafts"] = {"url": pr_url}
                        
                    try:
                        new_page = await notion_client.create_page(session, kanban_db, kanban_props)
                        if new_page:
                            notion_deep_link = new_page.get("url", "")
                    except Exception as e:
                        logger.error(f"Failed to create Kanban card for {title}: {e}")
                        
                if series_id:
                    logger.info(f"Auto-incrementing episode count for series {series_id}")
                    new_count = count + 1
                    await notion_client.update_page_properties(session, series_id, {
                        "Current Count": {"number": new_count}
                    })
                        
                email_body_html += f"<h2>[{args.mode.capitalize()}] {title}</h2>"
                if notion_deep_link:
                    email_body_html += f'<div style="margin: 20px 0;"><a href="{notion_deep_link}" style="background-color: #2ea44f; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; font-weight: bold; border-radius: 8px;">Manage in Kanban</a></div>'
                if pr_url:
                    email_body_html += f'<p><strong>Pull Request:</strong> <a href="{pr_url}">{pr_url}</a></p>'
                
                email_body_html += f"<h3>Instagram Draft</h3><pre style='background:#f4f4f4;padding:15px;border-radius:8px;white-space:pre-wrap;'>{insta}</pre>"
                email_body_html += f"<h3>LinkedIn Draft</h3><pre style='background:#f4f4f4;padding:15px;border-radius:8px;white-space:pre-wrap;'>{linkedin}</pre>"
                email_body_html += "<hr>"
                
            email_body_html += "</body></html>"
            
            email_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "temp", "email_body.html"))
            os.makedirs(os.path.dirname(email_path), exist_ok=True)
            with open(email_path, "w", encoding="utf-8") as f:
                f.write(email_body_html)
                
            try:
                subprocess.run(["python3", "src/send_email.py", "--subject", f"Project Prism: {len(generated_pages)} New Drafts Ready", "--body-file", email_path], check=True)
            except Exception as e:
                logger.error(f"Failed to send email notification: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
