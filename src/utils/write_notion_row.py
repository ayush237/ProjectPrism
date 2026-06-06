import os
import sys
import argparse
from notion_client import NotionAPIClient

def main():
    parser = argparse.ArgumentParser(description="Push a new row to the Virality Notion Database.")
    parser.add_argument("--title", required=True, help="Title of the idea")
    parser.add_argument("--url", default="", help="Reference URL")
    parser.add_argument("--notes", default="", help="Raw research notes")
    args = parser.parse_args()

    db_id = os.environ.get("NOTION_VIRALITY_DB_ID")
    if not db_id:
        print("Error: NOTION_VIRALITY_DB_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = NotionAPIClient()
    
    properties = {
        "Title": {
            "title": [
                {
                    "text": {
                        "content": args.title
                    }
                }
            ]
        }
    }
    
    if args.url:
        properties["URL"] = {
            "url": args.url
        }
        
    if args.notes:
        properties["Notes"] = {
            "rich_text": [
                {
                    "text": {
                        "content": args.notes[:2000] # Truncate to avoid Notion text limits
                    }
                }
            ]
        }

    print(f"Creating Notion page in {db_id}...")
    res = client.create_page(db_id, properties)
    if res:
        print(f"Success! Page created with ID: {res.get('id')}")
    else:
        print("Failed to create page.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
