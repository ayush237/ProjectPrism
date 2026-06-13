# The Prism Architecture Map

**CRITICAL AGENT INSTRUCTION:** You MUST read this entire document before writing any Python integration code or modifying any database schemas. This file is the absolute, concrete source of truth for the Tri-Modal Engine.

---

## 0. The 3-Workflow Paradigm
The entire ecosystem operates on three distinct, Kanban-linked workflows:

### Workflow 1: Research (Data Collection)
* **Action:** Agents run via cron jobs to execute automated content research on latest news, specific study topics, and evergreen seeds, updating our storage databases.
* **Kanban State:** A new Kanban card is **Created** and placed in the *Parked* stage.

### Workflow 2: Content Generation (Drafting)
* **Action:** Agents automatically pull the researched topics/references and refine them into final drafts for Instagram and LinkedIn scripts. This runs autonomously via cron across all pipelines.
* **Kanban State:** The user receives the notification and manually approves the draft, moving the Kanban card to **In Progress**.

### Workflow 3: Asset Generation (Hybrid Polish & Production)
* **Action:** A human-in-the-loop workflow. The user picks the generated scripts, engages the **Editor Agent** to polish them, and moves the final draft to `content/finalScripts/`. The user then engages the **Director Agent (Asset Agent)** to run the 6-Vector asset generation pipeline (Manim diagrams, Google Stitch motion graphics, Nano Banana images, B-roll). 
* **Kanban State:** The user edits the final video and moves the Kanban card to **Completed**.

---

## 1. Notion Database Schemas
All Notion API integration scripts must use these exact, case-sensitive columns.

### Table A: Study Material Workstation
*   **Name:** (Type: `Title`)
*   **Domain:** (Type: `Select` or `Text`)
*   **Status:** (Type: `Status` or `Select`) -> *Must have a "Done" option.*
*   **Reel Format:** (Type: `Select`) -> *Options: "Spoken", "Silent"*
*   **Resources:** (Type: `URL`)
*   **NotebookLM Insights:** (Type: `Text` or `URL`)
*   **Assigned Series:** (Type: `Relation` pointing to Table F)
*   **Pipeline Processed:** (Type: `Checkbox`)

### Table B: Social & Virality Dump
*   **URL:** (Type: `Title`) -> *The Title column was renamed to URL for faster pasting.*
*   **Status:** (Type: `Status` or `Select`) -> *Must have a "Done" option.*
*   **Notes:** (Type: `Text`)
*   **Reel Format:** (Type: `Select`) -> *Options: "Spoken", "Silent"*
*   **Assigned Series:** (Type: `Relation` pointing to Table F)
*   **Pipeline Processed:** (Type: `Checkbox`)

### Table C: Research Archive
*   **Topic Name:** (Type: `Title`)
*   **Category:** (Type: `Select`) -> *Options: "Evergreen", "Latest"*
*   **Brief:** (Type: `Text`)
*   **Local File Path:** (Type: `Text`) -> *Points to `research/schedules/...`*
*   **Status:** (Type: `Status` or `Select`) -> *Must have a "Done" option.*
*   **Reel Format:** (Type: `Select`) -> *Options: "Spoken", "Silent"*
*   **Assigned Series:** (Type: `Relation` pointing to Table F)
*   **Pipeline Processed:** (Type: `Checkbox`)

### Table D: Topics Seed Bank
*   **Topic Name:** (Type: `Title`)
*   **Source:** (Type: `Select`) -> *Options: "Human", "AI"*
*   **Notes:** (Type: `Text`)
*   **Pipeline Processed:** (Type: `Checkbox`)

### Table E: Content Production Kanban
*   **Name:** (Type: `Title`) -> *Format: "[Pipeline Source] [Format] Topic Name" (e.g., "[Research-Latest] [Spoken] What is LoRA?")*
*   **Stage:** (Type: `Status` or `Select`) -> *Options: Parked, Picked, In-Progress, Done*
*   **Pipeline Source:** (Type: `Select`) -> *Options: Study, Virality, Research-Latest, Research-Evergreen*
*   **Content Drafts:** (Type: `URL`) -> *Link to the GitHub PR containing the generated drafts.*

### Table F: The Series Hub
*   **Name:** (Type: `Title`) -> *e.g., "100 Days of AI", "System Design 101"*
*   **Description/Tone:** (Type: `Text`) -> *The specific personality or vibe this series should have.*
*   **Current Count:** (Type: `Number`) -> *Tracking which episode we are on.*

---

## 2. Cron Trigger Matrix
These schedules dictate the autonomous data flows. (`cron_config.txt`)

1.  **Sunday 9:00 PM (`0 21 * * 0`):** `pipeline_trigger.py --mode "study"`
    *   *Reads Table A. Generates content. Triggers Email Digest and Git PR.*
2.  **Tuesday 9:00 PM (`0 21 * * 2`):** `pipeline_trigger.py --mode "research"`
    *   *Reads Table C. Generates content. Triggers Email Digest and Git PR.*
3.  **Wednesday 9:00 PM (`0 21 * * 3`):** `research_trigger.py --mode "ideation"`
    *   *Reads `trusted_sources.md`. Writes topics to Table D.*
4.  **Thursday 9:00 PM (`0 21 * * 4`):** `research_trigger.py --mode "deep_dive"`
    *   *Reads Table D. Writes to `research/schedules/` and Table C.*
5.  **Friday 9:00 PM (`0 21 * * 5`):** `pipeline_trigger.py --mode "virality"`
    *   *Reads Table B. Generates content. Triggers Email Digest and Git PR.*

---

## 3. Local File Topology
*   `docs/trusted_sources.md`: Dynamic configuration of URLs used by the Wednesday Ideation Hunt.
*   `research/schedules/latest/`: Output directory where Thursday Deep Dives store massive text files for "Latest" topics.
*   `research/schedules/evergreen/`: Output directory where Thursday Deep Dives store massive text files for "Evergreen" topics.

---

## 4. The Vector Lakehouse (RAG) Usage
*   **Write/Sync Phase:** A nightly cron job runs `rag_sync.py` to crawl markdown documents and embed them into ChromaDB using Gemini.
*   **Read/Query Phase:** Agents authorized for Deep Archive fact-checking use `rag_query.py` to retrieve dense semantic context, bypassing LLM token limits and preventing hallucinations.
