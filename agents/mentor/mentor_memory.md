# mentor_memory.md

## Identity & Role
* **Role:** Meta Architect and Project Mentor.
* **Purpose:** To help the user (Senior Software Engineer) brainstorm features, debug high-level architecture, refine the Antigravity workspace, and oversee the Manager Agent and the broader multi-agent system.
* **Rule:** Read this file at the start of every session to regain continuity on the project's meta-state.

## Core Directives & Playbook
*   **The Golden Rule:** The user is the Editor-in-Chief. No content is published without final human approval. 
*   **Architectural Stewardship:** I am responsible for maintaining the `agentic_engineering_playbook.md`, extracting high-level learnings from our interactions to build a timeless guide on agentic systems.
*   **Concrete Memory Maintenance:** I am explicitly responsible for keeping `docs/architecture_map.md` perfectly up-to-date. If we alter a database schema, file path, RAG integration, or cron job, I must autonomously update the map *before* concluding the feature rollout.

## Project Meta-State
* **Project Name:** Project Prism
* **Core Goal:** Auto-generate technical LinkedIn posts and Instagram Reels/Carousels from a 12-week AI/System Design study syllabus tracked in Notion.
* **The 3-Workflow Paradigm:** 
  * **1. Research:** Cron-driven autonomous data collection. (Kanban: Created/Parked)
  * **2. Content Generation:** Cron-driven autonomous script drafting. (Kanban: Moved to In Progress upon human approval)
  * **3. Asset Generation:** Hybrid human/agent loop. User polishes with Editor Agent, Director Agent orchestrates 6-Vector assets (Stitch, Manim, etc.), user edits final video. (Kanban: Completed)
* **Architecture:** Multi-agent pipeline orchestrated by a Manager Agent (Gemini/Claude 3.5), dispatching to Researcher (Haiku/Flash), LinkedIn Agent (Claude 3.5), and Instagram Agent (GPT-4o).
* **Key Principles:**
  * **1:Many Data Mapping:** Raw notes -> multiple distinct content pieces.
  * **Goal-Driven Execution:** Agents loop on success criteria rather than strict steps (Karpathy Rules).
  * **Fail Loud:** Sub-agents must surface API and edge-case failures.
  * **Workspace Hygiene:** Manager strictly cleans up tmp files.

## Recent Architectural Decisions & Milestones
* **[2026-06-03] Tri-Modal Content Architecture:** Deployed 3 distinct Notion databases (Study Material, Series, Virality) and built automated cron-triggered workflows for extraction and proactive generation.
* **[2026-06-05] Editor-in-Chief Upgrade:** Deployed the `editor_agent.md` as a user-facing Script Doctor. It leverages `docs/research_archive/` to fact-check scripts and enforce the 3-second hook rule.
* **[2026-06-08] The Viral Director (Asset Generation):** Deployed `asset_agent.md`. When the Editor finalizes a script, the Viral Director automatically reads it, applies a 5-Vector Modality Logic, and generates a `storyboard.md` table mapping script lines to visuals.
* **[2026-06-08] MCP Integration:** Connected the Viral Director to 4 distinct MCP servers: `pexels-mcp-server` (B-Roll), `gemini_image_mcp` (Generative AI), `typst_mcp` (Slides), and `manim_mcp` (Programmatic Animated Diagrams). 
* **[2026-06-09] Multimodal Notion Extraction & Async Migration:** Rewrote the data pipeline to natively support Gemini Vision OCR for Notion screenshots. Migrated from synchronous `urllib` to `aiohttp` to prevent timeouts. Implemented strict `@Notes`/`@Prism` tag boundaries and an "Autonomous Expansion" mandate.
* **[2026-06-09] The Vector Lakehouse (RAG):** Migrated from flat-file storage to ChromaDB. Implemented a nightly `rag_sync.py` cron job using Gemini `text-embedding-004` to enable semantic retrieval for sub-agents without blowing context windows.
* **[2026-06-10] State Machine & Telemetry:** Replaced the fragile LLM-edited state file with a deterministic `state_manager.py` JSON backend. Implemented `logger.py` to route all script errors to `logs/prism_system.log` and auto-inject them into the Markdown dashboard. Added `install_crons.sh` to enforce OS-level cron daemon scheduling over LLM hallucinated schedules.
* **[2026-06-10] Prism Control Center:** Extracted project features into `docs/requirements.md` to resolve architectural drift. Deployed a Vanilla JS/CSS Dark Mode Dashboard hosted on GitHub Pages. Implemented a GitHub Gist Cloud Sync architecture to expose local telemetry to mobile without exposing the host Mac.
* **[2026-06-10] Format Pipeline Overhaul:** Implemented deterministic metadata tagging (`[FORMAT: SPOKEN]` vs `[FORMAT: SILENT]`) flowing directly from Notion down to the Asset Agent. Established the Technical/Hook Fact-Checking Dichotomy in the Editor Agent to prevent algorithmic hook dilution.
* **[2026-06-10] Continuous Ingestion (Two-Way Sync):** Removed fragile "Weekly Batch" hardcoding from the Notion extraction pipeline. Implemented a Two-Way Sync architecture where the Python backend actively patches a `Pipeline Processed` checkbox in the Notion UI to manage state natively.
* **[2026-06-10] The Virality Pipeline:** Bridged Database C (Evergreen Archive) to the generative agents. Built `pipeline_trigger.py --mode "virality"` to autonomously query human-approved AI research using the Two-Way Sync checkbox, routing topics directly to Instagram/LinkedIn agents.
* **[2026-06-10] Channel-Level Resolution:** Upgraded the `youtube_client` and `apify_client` to support broad profile URLs in `trusted_sources.md`. The pipeline now autonomously resolves profiles (YouTube Channels, Twitter Profiles) to their single newest upload for transcript extraction.
* **[2026-06-10] Grand Unified Architecture:** Completely overhauled and decoupled the ecosystem into a 4-Table data flow. Split the timeline across the week: Wednesday Ideation (`TOPICS_SEED_DB`), Thursday Research (`RESEARCH_ARCHIVE_DB` + local text dumps), Friday Virality Generation (`SOCIAL_DUMP_DB`), and Sunday Study Generation (`STUDY_MATERIAL_DB`). Finalized the system map in `docs/architecture_map.md` to prevent LLM Context Anxiety.
* **[2026-06-10] Cascading Notifications:** Wired the Notification Agent directly into the `pipeline_trigger.py` success loops. Git PRs and SMTP Email Digests are now autonomously dispatched instantly upon successful content generation.
* **[2026-06-10] Editorial Kanban (Mobile Approvals):** Implemented Table E (Content Production Kanban). Integrated a Serverless Deep-Link architecture into the `send_email.py` digests, allowing the user to click `[Manage in Kanban]` via mobile to instantly approve/park drafts in Notion without a live webhook server.
* **[2026-06-10] Relational Series Hub:** Implemented Table F. Designed a relational database architecture over the existing pipelines to prevent duplicate content generation while autonomously passing down Series Tone and Auto-Incrementing Episode counts into the LLM prompts.
* **[2026-06-11] API Retry Resilience:** Upgraded all `google-genai` client initializations across the Python backend with `HttpRetryOptions` to autonomously perform exponential backoff retries when encountering temporary 503 High Demand errors from Google's servers.
* **[2026-06-12] Stitch-to-Video Asset Engine:** Bypassed expensive AI video generators (Veo/Runway) by building an automated web-to-video pipeline. The pipeline uses the Google Stitch API (`stitch.withgoogle.com`) to generate hyper-modern, minimalist HTML/CSS designs based on the content script. It then uses a headless Chromium `playwright` engine to record the CSS animations natively and export crisp `.mp4`/`.webm` motion graphics for vertical reels.

## Current Focus / Open Discussions
* *The Tri-Modal engine is fully operational. The 6-Table ecosystem (A-F) is locked in concrete memory, bulletproofed against server outages, and armed with automated Google Stitch video asset generation. Awaiting the user's next challenge.*
