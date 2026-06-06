# meta_architecture_context.md

## 1. Document Purpose
This document serves as the "Meta Context" for Project Prism. It contains the historical architectural decisions, workflow patterns, and model routing logic designed by the user (a Senior Software Engineer) and their initial AI architect. 

## 2. Core Architecture Decisions
* **The Goal:** Connect a Notion database (tracking a 12-week AI/System Design study syllabus) to a multi-agent Antigravity 2.0 system to auto-generate technical LinkedIn posts and visual Instagram Reels/Carousels.
* **The Orchestrator Pattern:** The user only communicates with a "Manager Agent." The Manager is responsible for task delegation, writing Python integration scripts (Notion API), and quality control.
* **Data Mapping:** The workflow strictly enforces a 1:many mapping. Raw Notion study notes (e.g., Week 1: LoRA & Quantization) are extracted to generate multiple distinct pieces of content to build a backlog.

## 3. Heterogeneous Model Routing Strategy
To optimize for cost, speed, and capability, different tasks are routed to specific models:
* **Manager Agent (Orchestrator/Coder):** Gemini 3.1 Pro or Claude 3.5 Sonnet (Heavy reasoning, zero-shot coding).
* **Researcher Agent (Extractor):** Gemini Flash or Claude Haiku (Fast, cheap, strict data extraction).
* **LinkedIn Agent (SDE-3 Persona):** Claude 3.5 Sonnet (Dry, professional, highly technical tone).
* **Instagram Agent (Creative Storyteller):** GPT-4o (Creative analogies, lifestyle metaphors, fast-paced script formatting).

## 4. Engineering Patterns Implemented
* **Episodic Memory (State Management):** To prevent context window expiration, the Manager maintains a `pipeline_state.md` file. It must read this file at the start of every session to regain context.
* **Self-Optimization Loop (Pull Requests):** Agents cannot overwrite their own core `.md` prompt files. If the Manager detects a need for prompt improvement, it drafts a `[agent_name].proposed.md` file with a changelog for the user to review and merge.
* **Documentation Autonomy:** The Manager has unilateral authority to directly update `docs/requirements.md` whenever the project scope or tech stack shifts, without needing a review.
* **Workspace Hygiene:** The Manager is strictly responsible for deleting temporary files and maintaining a pristine directory structure.

## 5. Meta Architect Responsibilities
* **Communication State:** The Meta Architect must actively track or ask the user what payloads or discussions have already been passed to the Manager Agent to prevent conflicting states and ensure only relevant deltas (diffs) are provided.
* **Execution Boundary:** The execution job is strictly for the Manager Agent. The Meta Architect must *always* provide a copy-pasteable prompt/payload for the user to hand off to the Manager Agent whenever an architectural idea is finalized and ready for execution.
* **Critical Pushback:** The Meta Architect must not blindly agree to every feature addition or update proposed by the user. It is responsible for carefully analyzing proposed additions, evaluating trade-offs, and pushing back or offering robust alternatives when a request threatens the system's simplicity, cost, or architectural integrity.