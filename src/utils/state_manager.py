import os
import json
import argparse
import urllib.request
from datetime import datetime, timezone
from utils.logger import get_logger

logger = get_logger(__name__)

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
JSON_FILE = os.path.join(ROOT_DIR, 'pipeline_state.json')

def load_state():
    state = None
    if os.path.exists(JSON_FILE):
        try:
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except json.JSONDecodeError:
            pass
            
    if not state:
        state = {
            "current_status": "Idle",
            "last_execution_time": datetime.now(timezone.utc).isoformat(),
            "active_task": "",
            "errors": [],
            "recent_logs": [],
            "cron_history": {
                "Study Material": [],
                "Series Pipeline": [],
                "Evergreen Hunt": [],
                "Latest Hunt": [],
                "Vector Sync": []
            }
        }
        
    # Ensure all required keys exist if loading an old state schema
    if "cron_history" not in state:
        state["cron_history"] = {
            "Study Material": [],
            "Series Pipeline": [],
            "Evergreen Hunt": [],
            "Latest Hunt": [],
            "Vector Sync": []
        }
    if "recent_logs" not in state:
        state["recent_logs"] = []
        
    return state

def save_state(state):
    state["last_execution_time"] = datetime.now(timezone.utc).isoformat()
    
    # Read the central log file for recent errors
    log_file_path = os.path.join(ROOT_DIR, "logs", "prism_system.log")
    recent_errors = []
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                error_lines = [line.strip() for line in lines if "[ERROR]" in line]
                recent_errors = error_lines[-5:]
        except Exception:
            pass
            
    state["recent_logs"] = recent_errors
    
    state_json_str = json.dumps(state, indent=2)
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        f.write(state_json_str)
        
    _sync_to_gist(state_json_str)

def _sync_to_gist(state_json_str):
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(ROOT_DIR, '.env'))
    except ImportError:
        pass
        
    token = os.getenv("GITHUB_TOKEN")
    gist_id = os.getenv("GIST_ID")
    
    if not token or not gist_id:
        return
        
    url = f"https://api.github.com/gists/{gist_id}"
    payload = {
        "files": {
            "pipeline_state.json": {
                "content": state_json_str
            }
        }
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="PATCH")
    req.add_header("Authorization", f"token {token}")
    req.add_header("Accept", "application/vnd.github.v3+json")
    
    try:
        with urllib.request.urlopen(req) as response:
            pass
    except Exception as e:
        logger.error(f"Failed to sync state to GitHub Gist: {e}", exc_info=True)

def main():
    parser = argparse.ArgumentParser(description="State Machine CLI for Project Prism")
    subparsers = parser.add_subparsers(dest="action", required=True)
    
    subparsers.add_parser("get_status", help="Get current pipeline state")
    
    parser_set_status = subparsers.add_parser("set_status", help="Update current status")
    parser_set_status.add_argument("status", type=str)
    
    parser_set_task = subparsers.add_parser("set_task", help="Update active task")
    parser_set_task.add_argument("task", type=str)
    
    parser_log_error = subparsers.add_parser("log_error", help="Log an error message")
    parser_log_error.add_argument("error_message", type=str)
    
    parser_log_cron = subparsers.add_parser("log_cron", help="Log a cron execution result")
    parser_log_cron.add_argument("job_name", type=str)
    parser_log_cron.add_argument("status", type=str, choices=["SUCCESS", "FAIL"])
    
    subparsers.add_parser("clear_errors", help="Clear all logged errors")
    
    args = parser.parse_args()
    state = load_state()
    
    if args.action == "get_status":
        print(json.dumps(state, indent=2))
        return
        
    if args.action == "set_status":
        state["current_status"] = args.status
    elif args.action == "set_task":
        state["active_task"] = args.task
    elif args.action == "log_error":
        timestamp = datetime.now(timezone.utc).isoformat()
        state["errors"].append(f"[{timestamp}] {args.error_message}")
    elif args.action == "log_cron":
        job = args.job_name
        if job not in state["cron_history"]:
            state["cron_history"][job] = []
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        state["cron_history"][job].append({
            "date": date_str,
            "status": args.status
        })
        # Keep only last 7 executions
        if len(state["cron_history"][job]) > 7:
            state["cron_history"][job] = state["cron_history"][job][-7:]
    elif args.action == "clear_errors":
        state["errors"] = []
        
    save_state(state)
    print(f"Action '{args.action}' executed successfully. JSON updated.")

if __name__ == "__main__":
    main()
