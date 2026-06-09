# mentor_memory.md

## Identity & Role
* **Role:** Meta Architect and Project Mentor.
* **Purpose:** To help the user (Senior Software Engineer) brainstorm features, debug high-level architecture, refine the Antigravity workspace, and oversee the Manager Agent and the broader multi-agent system.
* **Rule:** Read this file at the start of every session to regain continuity on the project's meta-state.

## Project Meta-State
* **Project Name:** Project Prism
* **Core Goal:** Auto-generate technical LinkedIn posts and Instagram Reels/Carousels from a 12-week AI/System Design study syllabus tracked in Notion.
* **Architecture:** Multi-agent pipeline orchestrated by a Manager Agent (Gemini/Claude 3.5), dispatching to Researcher (Haiku/Flash), LinkedIn Agent (Claude 3.5), and Instagram Agent (GPT-4o).
* **Key Principles:**
  * **1:Many Data Mapping:** Raw notes -> multiple distinct content pieces.
  * **Goal-Driven Execution:** Agents loop on success criteria rather than strict steps (Karpathy Rules).
  * **Fail Loud:** Sub-agents must surface API and edge-case failures.
  * **Workspace Hygiene:** Manager strictly cleans up tmp files.

## Recent Architectural Decisions & Milestones
* **[2026-05-30] Manager Prompt Optimization:** Upgraded the Manager Agent with Karpathy's CLAUDE.md principles (Goal-Driven Execution, Think Before Coding, Read Before Write, Fail Loud, Token Budget & Checkpoint).
* **[2026-06-03] Tri-Modal Content Architecture:** Deployed 3 distinct Notion databases (Study Material, Series, Virality) and built automated cron-triggered workflows for extraction and proactive generation.
* **[2026-06-05] Editor-in-Chief Upgrade:** Deployed the `editor_agent.md` as a user-facing Script Doctor. It leverages `docs/research_archive/` to fact-check scripts and enforce the 3-second hook rule.
* **[2026-06-08] The Viral Director (Asset Generation):** Deployed `asset_agent.md`. When the Editor finalizes a script, the Viral Director automatically reads it, applies a 5-Vector Modality Logic, and generates a `storyboard.md` table mapping script lines to visuals.
* **[2026-06-08] MCP Integration:** Connected the Viral Director to 4 distinct MCP servers: `pexels-mcp-server` (B-Roll), `gemini_image_mcp` (Generative AI), `typst_mcp` (Slides), and `manim_mcp` (Programmatic Animated Diagrams). 
* **[2026-06-09] Multimodal Notion Extraction:** Rewrote the data pipeline to natively support Gemini Vision OCR for screenshots inside Notion. Implemented strict `@Notes`/`@Prism` tag boundaries and an "Autonomous Expansion" mandate for the Researcher.

## Current Focus / Open Discussions
* *The Tri-Modal engine is fully operational. The Asset Generation pipeline is online and generating physical `storyboard.md` files. Notion extraction is now fully multimodal. Awaiting the user's next architectural challenge.*
