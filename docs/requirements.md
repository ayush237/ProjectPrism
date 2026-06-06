# requirements.md: Project Study-Sync & Content Engine

## 1. Project Overview
This project is an automated AI content agency managed via Google Antigravity. The goal is to synthesize the user's weekly AI and System Design study notes (stored in Notion) and automatically generate high-quality, technically accurate content for LinkedIn and Instagram. 

## 2. The Tech Stack
* **Knowledge Base:** Notion API (Master Syllabus & Notes) using dynamic Search API to automatically resolve database IDs.
* **Processing Engine:** NotebookLM (For deep-dive summaries, manually fed to Notion, now treated as an optional field).
* **Agentic Orchestration:** Google Antigravity 2.0 (running in a multi-agent sub-process architecture).
* **Integration Scripting:** Python (running inside `/src`).
* **Output Format:** Clean, beautifully styled HTML pages natively editable in the browser via `contenteditable="true"`, stored securely in `/content_outputs` with a centralized global stylesheet.

## 3. Agent Team Hierarchy (Dual-Endpoint System)
* **Engineering Manager (The Orchestrator):** Handles all architecture, Python integration code, API connections, and pipeline routing. Responsible for tracking project state and ensuring strict OOP engineering standards.
* **Editor-in-Chief (The Refiner):** A user-facing agent dedicated strictly to interacting with the user to edit, rewrite, and finalize the generated `.html` and `.md` content drafts before publication.
* **Researcher Agent (The Brain):** Synthesizes Notion raw data and web content into structured technical briefs. Extracts algorithmic insights from social metadata.
* **LinkedIn Agent (The Technical Writer):** Drafts authoritative, text-heavy posts based on the provided briefs, enforcing strict algorithmic constraints.
* **Instagram Agent (The Creative):** Drafts visual, analogy-driven Reel scripts (with hashtags), generating a unique script for *each* brief provided.
* **Notification Agent (The Alert System):** Formats successful deliverables into clean HTML/Markdown email digests, and intelligently translates failure tracebacks into actionable alerts before dispatch.

## 4. Automation Triggers
The Tri-Modal Content Architecture separates data ingestion and content execution across three distinct streams:
*   **Database A (Study Material):** Extracted on Tuesdays at 9:00 PM (`0 21 * * 2`). Data is passed down the agent chain for multi-content generation.
*   **Database B (Series):** Extracted on Fridays at 9:00 PM (`0 21 * * 5`).
*   **Database C (Virality & Social Dump):** Extracted on Fridays at 9:00 PM (`0 21 * * 5`). The Researcher autonomously pushes raw trend ideas directly into this database via two distinct Deep Hunt schedules:
    *   **Latest Developments Hunt:** Runs every 10 days (1st, 11th, and 21st of the month at 9:00 PM: `0 21 1,11,21 * *`) to scrape the latest AI advancements.
    *   **Evergreen Foundations Hunt:** Runs every Thursday at 9:00 PM (`0 21 * * 4`) to research timeless, highly technical AI system design concepts.

## 5. Third-Party Integrations
* **Notion API:** Primary data ingestion source for both study notes and saved social URLs.
* **Firecrawl API:** Integrated via `fetch_social_dump.py` to bypass anti-bot protections and cleanly scrape raw markdown from saved social media URLs.
* **SMTP (send_email.py):** Integrated for DevOps alerts and digests via the Notification Agent.
