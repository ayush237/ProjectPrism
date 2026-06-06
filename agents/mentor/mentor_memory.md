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

## Current Focus / Open Discussions
* *No open tasks currently. Waiting on user's next architectural challenge.*
