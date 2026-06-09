# Architectural Blueprint for Autonomous Asset Generation in AI Media Agencies

## The Paradigm Shift in Autonomous Media Production

The transition from human-driven media production pipelines to fully automated, multi-agent artificial intelligence ecosystems represents a profound reconfiguration of digital content creation. In traditional workflows, human producers act as the connective tissue between disparate software environments, manually searching stock libraries, prompting image generators, and typesetting presentations. In a fully autonomous AI media agency, these responsibilities are delegated to specialized generative agents operating within a complex orchestration graph. 

At the center of this graph is the asset generation agent, a highly specialized entity tasked with translating abstract, finalized scripts into concrete, high-fidelity visual media. For contemporary short-form content ecosystems—such as TikTok, Instagram Reels, YouTube Shorts, and Snapchat Spotlight—the spatial constraints are mathematically rigid. The algorithmic dominance of mobile-first consumption mandates a vertical orientation, universally standardized at a $9:16$ aspect ratio. This typically translates to an optimal resolution of $1080 \times 1920$ pixels.[span_0](start_span)[span_0](end_span) Straying from this exact ratio guarantees algorithmic penalization, as platforms will forcibly crop, stretch, or apply letterboxing to non-conforming media, destroying the visual integrity of the content.[span_1](start_span)[span_1](end_span)

An autonomous agent assigned to this asset generation phase must overcome significant computational and architectural hurdles to provision three distinct types of media: high-quality $9:16$ vertical stock B-roll video, native $9:16$ AI-generated images, and minimalist presentation slides rendered as static images directly from markdown-formatted text. Achieving this mandates the navigation of highly fragmented ecosystems, bridging RESTful JSON APIs, remote generative latent diffusion networks, and programmable typesetting engines. The agent cannot rely on visual intuition; it must operate on deterministic, programmable logic to ensure absolute dimensional accuracy and thematic coherence.

This comprehensive analysis evaluates the available architectural pathways to achieve this tri-fold mandate. By examining the efficacy of direct application programming interface (API) integrations, agentic orchestration frameworks, and the Model Context Protocol (MCP), a robust, maintainable, and highly scalable architecture is established. The primary objective is to decouple the fragile mechanics of tool execution from the cognitive reasoning layer of the language model, ensuring the autonomous agent can continuously search, generate, and compile media assets with enterprise-grade reliability.

## Evaluation of Integration Frameworks and System Architectures

The architectural foundation of an autonomous media agent dictates how the underlying Large Language Model (LLM) interacts with the external world. Historically, establishing these connections required embedding tightly coupled logic within the agent's core execution loop. Today, the landscape has evolved to offer multiple distinct integration paradigms, each possessing unique characteristics regarding maintainability, security, and scalability.

### Direct API Integrations and Hardcoded Scripting

The most primitive approach to equipping an agent with asset generation capabilities involves writing custom Python or Node.js scripts that directly invoke external endpoints using standard HTTP libraries, such as Python's `requests` or JavaScript's `fetch` API. In this paradigm, the agent executes a script that manually formats an HTTP payload, manages authentication headers, dispatches the request, and parses the resulting JSON schema.[span_3](start_span)[span_3](end_span)[span_4](start_span)[span_4](end_span) 

This methodology offers absolute control over the network request. It allows engineers to construct highly customized error-handling routines, implementing exponential backoff algorithms using libraries like `tenacity` to manage rate limits, and writing bespoke file system operations for downloading large media payloads.[span_5](start_span)[span_5](end_span) For example, a hardcoded Python script interacting with the Pexels API can explicitly define the request structures, manage memory buffers for chunked video downloads, and handle specific HTTP 429 "Too Many Requests" errors with customized delays.[span_8](start_span)[span_8](end_span)[span_10](start_span)[span_10](end_span)

However, the strategic implications of deploying direct API scripts within a multi-agent system are overwhelmingly negative as the system scales. The agent's cognitive logic becomes inextricably bound to the volatile schemas of external APIs. If a provider deprecates a parameter, alters a JSON response structure, or updates authentication protocols, the agent's core tool definition must be manually refactored. Furthermore, managing the lifecycle of these requests—such as pagination, asynchronous polling for long-running generative tasks, and state synchronization—requires injecting complex state machine logic directly into the LLM's prompt context.[span_12](start_span)[span_12](end_span)[span_13](start_span)[span_13](end_span) 

Security vulnerabilities also present a critical failure point in hardcoded integrations. Scripts often run in the identical process memory space as the agent itself. This lack of isolation violates the principle of least privilege. In the event of a prompt injection attack, where malicious input forces the agent to execute arbitrary commands, the shared environment exposes all system environmental variables, including highly sensitive API keys and access tokens, to potential exfiltration.

### Agentic Tooling Frameworks

To mitigate the brittleness of raw scripts, frameworks such as LangChain and CrewAI introduced native abstractions for tool utilization. These frameworks wrap custom functions into standardized interfaces that language models can easily interpret, automatically converting programming language type hints into the JSON schemas required by the LLMs' native function-calling APIs.[span_14](start_span)[span_14](end_span)[span_16](start_span)[span_16](end_span)

LangChain relies on a highly flexible, stateless execution loop. Tools are typically defined using decorators that expose internal logic to the agent, which then autonomously decides when and how to invoke them.[span_18](start_span)[span_18](end_span) CrewAI takes a more structured, declarative approach, utilizing a Domain Specific Language (DSL) to assign agents specific roles, goals, and highly curated lists of tools.[span_23](start_span)[span_23](end_span)[span_25](start_span)[span_25](end_span) This role-based execution model ensures that an agent responsible for fetching B-roll cannot accidentally invoke a tool designed for database management, providing a basic layer of operational security.

While these frameworks significantly streamline the construction of prompts and the parsing of tool outputs, they do not resolve the monolithic scaling problem. Building every integration natively within LangChain or CrewAI requires the central repository to absorb the maintenance burden for every external dependency. As the media agency expands to support dozens of stock libraries, image generators, and audio synthesis APIs, the codebase becomes bloated, and the execution environment becomes dangerously congested with overlapping dependencies.

### The Model Context Protocol (MCP) Architecture

The Model Context Protocol (MCP) introduces a transformative client-server architecture that standardizes the interface between the AI orchestration layer (the client) and external capabilities (the servers). Rather[span_19](start_span)[span_19](end_span) than writing a specific LangChain or CrewAI tool for every service, the orchestration framework connects to independent MCP servers that expose standardized tool sets via a unified, open protocol.

MCP supports multiple transport mechanisms tailored to different execution environments:

| Transport Layer | Communication Mechanism | Ideal Deployment Scenario | Security Profile |
| :--- | :--- | :--- | :--- |
| **Stdio** | Standard Input/Output via local subprocesses [span_27](start_span)[span_27](end_span)[span_28](start_span)[span_28](end_span) | Local file manipulation, compiling binaries, typesetting [span_29](start_span)[span_29](end_span) | Exceptional. Operates in isolated local process; can be bound strictly to internal network constraints.[span_30](start_span)[span_30](end_span) |
| **HTTP / SSE** | Server-Sent Events over standard web protocols [span_38](start_span)[span_38](end_span)[span_39](start_span)[span_39](end_span) | Remote cloud API communication, asynchronous model inference  | High. Enforces HTTPS encry[span_20](start_span)[span_20](end_span)ption; isolates external token management away from the primary agent. |

The [span_31](start_span)[span_31](end_span)architectural superiority of MCP lies in its total decoupling of concerns. The orchestrating agent remains entirely agnostic to the underlying mechanics of the API endpoints, HTTP headers, or authentication tokens. It only interacts with a semantic description of the available tools retrieved during the protocol handshake.[span_40](start_span)[span_40](end_span)[span_41](start_span)[span_41](end_span) 

This separation introduces profound security advantages. MCP servers can be deployed in highly isolated environments, such as locked-down Docker containers or restricted subnets. By binding local development servers strictly to the `127.0.0.1` loopback address, external network access is physically impossible. Furthermore, a[span_32](start_span)[span_32](end_span)ccess tokens and API keys are managed exclusively at the MCP server level. An agent cannot leak a Pexels API key because the agent never possesses it; the key exists only in the environment of the remote MCP server executing the transaction.[span_42](start_span)[span_42](end_span)[span_44](start_span)[span_44](end_span)[span_46](start_span)[span_46](end_span)

Language interoperability is another major advantage. An MCP server written in TypeScript to leverage Node.js ecosystems can be seamlessly consumed by a Python-based CrewAI agent without requiring complex Foreign Function Interfaces (FFI) or brittle bridging libraries.[span_48](start_span)[span_48](end_span)[span_49](start_span)[span_49](end_span) This allows engineering teams to deploy tools in the language best suited for the specific task while maintaining a unified, Python-centric multi-agent orchestration layer.

## Sourcing High-Fidelity 9:16 Vertical Stock B-Roll

The continuous provision of dynamic, visually engaging B-roll is a non-negotiable requirement for short-form media. Audience retention on vertical platforms is heavily correlated with the frequency of visual pattern interrupts. However, the requirement for native $9:16$ vertical orientation introduces a severe constraint. Traditional stock media libraries have spent decades accumulating $16:9$ landscape footage for television and desktop consumption. Cropping a $16:9$ video to fit a $9:16$ frame discards $68.4\%$ of the original image, routinely cropping out subjects and destroying the cinematographer's intended framing. Therefore, the agent must programmatically source natively shot or pre-cropped vertical assets.

### Comparative Analysis of Stock Media APIs

The dominant programmatic providers of royalty-free stock footage are Pixabay and Pexels. Both platforms offer API access, but their architectural suitability for an autonomous, high-volume agency differs substantially.

Pixabay provides a comprehensive RESTful API supporting both image and video queries. Its architecture utilizes a standard endpoint where developers can pass query parameters such as `video_type` (which filters by film or animation) and `orientation` (which accepts horizontal, vertical, or all). While Pixabay's implementation of a fluent interface and method chaining makes it attract[span_6](start_span)[span_6](end_span)ive for traditional software development , its rate-limiting structures and the highly variable quality of its user-uploaded conten[span_7](start_span)[span_7](end_span)t pose challenges for an AI agent operating without a human quality-assurance filter.[span_50](start_span)[span_50](end_span)

Pexels is widely recognized as the premier source for modern, cinematic stock footage, possessing a vast catalog specifically optimized for mobile-first, vertical consumption.[span_51](start_span)[span_51](end_span)[span_52](start_span)[span_52](end_span) The Pexels v1 API provides a dedicated `/v1/videos/search` endpoint that is exceptionally well-suited for autonomous querying. 

The Pexels API accepts highly granular parameters that align perfectly with the requirements of an AI media pipeline:
*   `query`: The semantic search term (e.g., "ocean waves", "city timelapse").[span_53](start_span)[span_53](end_span)
*   `orientation`: Explicitly accepts the `portrait` string, commanding the database to return only assets matching the vertical ratio.[span_54](start_span)[span_54](end_span)
*   `size`: Accepts `small` (HD), `medium` (Full HD), and `large` (4K) strings, allowing the agent to establish a minimum quality threshold.[span_55](start_span)[span_55](end_span)
*   `page` and `per_page`: Facilitate deep pagination. The API permits up to 80 results per query, providing the agent with a large array of options for secondary filtering.[span_58](start_span)[span_58](end_span)

A critical architectural distinction is the metadata structure returned by the Pexels API. A successful response includes an array of `video_files` nested within each video object. Th[span_56](start_span)[span_56](end_span)is array details multiple available download URLs alongside their exact width, height, and duration. For an autonomous agent, this data is invaluable. The agentic tool can be programmed to iterate through this array and select the specific file where width is exactly 1080 and height is exactly 1920, ensuring flawless integration into the final rendering timeline without computationally expensive scaling operations.

### Designing the B-Roll Provisioning Architecture

Deploying a hardcoded Python integration for Pexels is suboptimal due to the complexity of managing search states and rate limits. Pexels restricts free-tier usage to 200 requests per hour and 20,000 requests per month. An automated agency could exhaust this limit in minutes if an agent enters a hallucination loop. 

The optim[span_9](start_span)[span_9](end_span)[span_11](start_span)[span_11](end_span)al architecture delegates this responsibility to a dedicated MCP Server operating over HTTP transport.[span_61](start_span)[span_61](end_span) This server exposes a highly constrained tool to the agent, for example, `search_and_retrieve_vertical_video`.

The operational sequence follows a strict trajectory:
1.  **Semantic Translation:** The language model analyzes the finalized script to deduce specific visual requirements. A script detailing corporate cybersecurity is translated by the LLM from abstract concepts into concrete, filmable search parameters, such as "server room flashing lights" or "person typing in dark".[span_62](start_span)[span_62](end_span)
2.  **Tool Invocation:** The agent invokes the MCP tool, passing the semantic strings. 
3.  **MCP Server Execution:** The MCP server constructs the HTTP GET request to `https://api.pexels.com/v1/videos/search`, automatically injecting the `orientation=portrait` and `size=large` parameters, and appending the securely stored API key to the `Authorization` header.
4.  **[span_59](start_span)[span_59](end_span)Data Processing and Fallback Logic:** The server parses the response. If the API returns a 429 Too Many Requests error, the MCP server automatically handles the exponential backoff, shielding the agent from the interruption. If the[span_60](start_span)[span_60](end_span) API returns an empty array indicating no results, the MCP server intercepts this failure and returns a structured `ToolMessage` to the agent.[span_64](start_span)[span_64](end_span)[span_65](start_span)[span_65](end_span) This message instructs the LLM to dynamically alter its strategy, suggesting it retry the search with broader, less specific terminology.
5.  **Asset Acquisition:** Upon identifying a suitable candidate, the MCP server executes the physical download of the `.mp4` file, saving it to a designated local or cloud storage volume, and returns the absolute path to the agent for downstream processing.

This[span_63](start_span)[span_63](end_span) architecture ensures the language model focuses entirely on semantic reasoning, while the MCP server absorbs all the friction of network latency, rate limiting, and binary file manipulation.

## Provisioning Native 9:16 AI-Generated Images

While stock video provides grounding and realism, AI-generated images are strictly necessary to visualize hyper-specific, fantastical, or highly branded concepts that do not exist in stock databases. The requirement for a native $9:16$ aspect ratio presents a unique challenge in the realm of latent diffusion models. Historically, image generation pipelines would produce a $1024 \times 1024$ square image, which would then be cropped. This approach destroys the composition, frequently truncating subjects' heads or cropping out critical elements, while simultaneously degrading the final resolution below the $1080 \times 1920$ benchmark.

### Foundation Model Selection

The generation of images must be integrated seamlessly. Traditional models from providers like OpenAI (DALL-E 3) or Midjourn[span_2](start_span)[span_2](end_span)ey offer exceptional quality but frequently suffer from rigid API constraints, extremely high latency, or a complete lack of programmatic access. 

The current apex of rapid, high-fidelity text-to-image generation suited for automated pipelines is the FLUX family of models, specifically the FLUX.1 [schnell] variant.[span_66](start_span)[span_66](end_span)[span_68](start_span)[span_68](end_span) FLUX.1 [schnell] is a 12-billion parameter flow transformer optimized for unprecedented speed. Utilizing advanced flow-based distillation techniques, it produces commercial-grade imagery in a remarkable 1 to 4 inference steps.[span_67](start_span)[span_67](end_span)[span_69](start_span)[span_69](end_span) For a multi-agent system generating dozens of images per minute, this sub-second response time is the difference between a functional pipeline and massive systemic bottlenecks.

Crucially, FLUX natively supports parameterized aspect ratios directly in the latent initialization phase. The API accepts an `image_size` parameter, which can be defined using strict custom dimensions or via predefined enumerations such as `portrait_16_9` (which maps to a resolution of $576 \times 1024$).[span_70](start_span)[span_70](end_span)[span_73](start_span)[span_73](end_span) 

A strict mathematical constraint governs these dimensions: both the height and width values must be multiples of 32.[span_76](start_span)[span_76](end_span) The target width of 1080 pixels is not a multiple of 32 (yielding a fractional result of 33.75). Therefore, the autonomous system cannot simply request $1080 \times 1920$. To maintain the exact $9:16$ ratio without violating the API's constraints, the architecture must calculate compliant dimensions. The system must be programmed to request dimensions such as $1024 \times 1824$ or $1088 \times 1920$, which satisfy the modulo 32 requirement and can subsequently be subjected to minor, lossless scaling operations during the final video rendering phase.[span_77](start_span)[span_77](end_span)

### Infrastructure Providers: Fal.ai versus Replicate

Accessing the FLUX models requires a robust serverless GPU infrastructure. The market is currently dominated by two primary providers: Replicate and Fal.ai.

Replicate provides a massive repository of open-source models and maintains a highly polished developer ecosystem.[span_78](start_span)[span_78](end_span) A significant architectural advantage is the existence of an official Replicate MCP server within the `mcpservers.org` registry.[span_80](start_span)[span_80](end_span)[span_81](start_span)[span_81](end_span) This server provides sophisticated controls over generation, including quality presets, precise dimensional control, and asynchronous progress tracking.[span_82](start_span)[span_82](end_span) 

However, when evaluating unit economics and latency for a high-volume agency, Fal.ai presents a compellingly superior profile. Comparative pricing metrics consistently demonstrate that Fal.ai operates at a 30% to 50% cost reduction compared to Replicate for identical open-source models, and frequently up to 80% cheaper for heavy video generation tasks (such as Wan 2.1) should the agency expand its capabilities. Fal.ai util[span_79](start_span)[span_79](end_span)izes a proprietary inference engine that yields significantly faster execution times, which is critical when chaining multiple generative requests.[span_83](start_span)[span_83](end_span)

The Fal.ai JSON payload schema is highly streamlined. A standard POST request accepts the `prompt`, the `num_inference_steps` (defaulting to 4 for Schnell), the `image_size`, and features advanced options such as `enable_prompt_expansion`. Prompt expansion is a particula[span_71](start_span)[span_71](end_span)[span_74](start_span)[span_74](end_span)rly valuable feature; it intercepts the agent's short, descriptive prompt and processes it through a secondary LLM to expand the text into a rich, highly detailed composition, dramatically improving the aesthetic quality of the output.[span_85](start_span)[span_85](end_span)

### Integrating Fal.ai via MCP

To implement this functionality, a custom HTTP MCP Server interfacing with the Fal.ai API should be deployed, exposing a `generate_vertical_image` tool. 

A critical architectural consideration during this integration is the management of content moderation and safety filters. Unlike stock video libraries, generative models can hallucinate inappropriate or off-brand content. Fal.ai implements a mandatory safety checker (`enable_safety_checker=true`) that evaluates the output of the diffusion process. If [span_84](start_span)[span_84](end_span)an image is flagged as Not Safe For Work (NSFW), the API replaces the image with a solid black frame of the same dimensions and appends a `has_nsfw_concepts` boolean array to the response payload. 

The MCP server must be programmed to [span_72](start_span)[span_72](end_span)[span_75](start_span)[span_75](end_span)intercept this payload, parse the boolean array, and validate the image. If the image is flagged, the MCP server must halt the process and return an error payload to the agent. Attempting to program an LLM to "look" for a black square is an impossibility; the validation logic must exist within the deterministic code of the MCP server. By returning a structured error indicating a safety violation, the agent can autonomously rewrite its prompt, utilizing less ambiguous language to circumvent the false positive and retry the generation sequence.[span_86](start_span)[span_86](end_span)

## Generating Minimalist Presentation Slides (9:16) from Markdown

The final component of the asset generation pipeline—converting markdown text into pixel-perfect, minimalist presentation slides formatted precisely to a vertical $9:16$ ratio—presents the steepest technical challenge. Large Language Models excel at generating structured text (Markdown), but they possess zero spatial reasoning capabilities. They cannot calculate font metrics, predict text overflow, or align elements on a canvas. Therefore, the system requires a programmatic rendering engine that bridges the gap between text generation and visual layout.

### Ecosystem Evaluation: Slidev, Marp, and Typst

Three dominant text-to-presentation ecosystems exist. Each relies on fundamentally different rendering technologies, and their suitability for an autonomous agent varies significantly.

**1. Slidev (The Web Ecosystem)**
Slidev is an exceptionally flexible presentation framework built on modern web technologies. It utilizes Vue.js components, Vite for bundling, and UnoCSS for utility-based styling.[span_87](start_span)[span_87](end_span)[span_89](start_span)[span_89](end_span) Slidev natively supports custom aspect ratios. By modifying the YAML headmatter of the markdown document to include `aspectRatio: 9/16` and setting the `canvasWidth` explicitly (e.g., to 1080 pixels), the framework instantly configures a vertical canvas.[span_88](start_span)[span_88](end_span)[span_90](start_span)[span_90](end_span) 

However, the underlying technology stack makes Slidev highly unsuitable for an autonomous agent. Because it is a web framework, exporting the slides to static images requires spinning up a Node.js web server and launching a headless Chromium browser instance (typically orchestrated via Playwright or Puppeteer) to screenshot the Document Object Model (DOM) elements.[span_91](start_span)[span_91](end_span)[span_92](start_span)[span_92](end_span) This introduces massive operational overhead. Furthermore, HTML/CSS layouts are inherently fluid. If the LLM generates slightly too much text, the CSS will frequently overflow the canvas. While utilities exist to scale text (`zoom`), they are difficult to orchestrate blindly.[span_93](start_span)[span_93](end_span)[span_94](start_span)[span_94](end_span) The process is highly susceptible to asynchronous rendering race conditions, resulting in blank or partially rendered screenshots.

**2. Marp (The CSS/Markdown Ecosystem)**
Marp is a simpler framework that strictly adheres to standard Markdown format and utilizes custom CSS themes to format slides.[span_95](start_span)[span_95](end_span)[span_97](start_span)[span_97](end_span) While Marp natively supports standard $16:9$ and $4:3$ horizontal layouts, forcing a $9:16$ aspect ratio requires injecting custom metadata into a standalone CSS theme file.[span_99](start_span)[span_99](end_span) For example, the developer must create a CSS file declaring `@size 9:16 1080px 1920px`. Thi[span_96](start_span)[span_96](end_span)[span_98](start_span)[span_98](end_span)s theme must then be referenced in the Markdown frontmatter, taking care to strip away any default size directives that might conflict.[span_100](start_span)[span_100](end_span)

Like Slidev, the Marp CLI relies on a headless browser to render and export the final PDFs or images. The reliance on external CSS files makes the compilation pipeline fragile for an autonomous agent, which must accurately stage both the Markdown file and the adjacent CSS file in the correct directory structure before invoking the command-line interface.[span_101](start_span)[span_101](end_span)[span_102](start_span)[span_102](end_span)

**3. Typst (The Compiled Typesetting Ecosystem)**
Typst represents a massive leap forward for programmable document generation. Written in Rust, Typst is a modern typesetting engine designed as a streamlined, highly performant alternative to LaTeX.[span_103](start_span)[span_103](end_span)[span_104](start_span)[span_104](end_span) It compiles documents in milliseconds using a single, dependency-free binary executable. 

Typst provides absolute, granular control over page dimensions. Utilizing the built-in `#set page()` function, dimensions can be strictly enforced. While it provides presets for standard presentations [span_105](start_span)[span_105](end_span), configuring a custom vertical layout requires only a single line of code:
```typst
#set page(width: 1080pt, height: 1920pt, margin: 80pt)
```
The Typst universe features sophisticated slide frameworks, such as `typslides`, `parcio-slides`, and `touying`.[span_106](start_span)[span_106](end_span)[span_107](start_span)[span_107](end_span)[span_108](start_span)[span_108](end_span) The `typslides` package, for instance, allows for the rapid application of minimalist themes via a simple `#show` rule initialization, providing elegant, out-of-the-box aesthetics that align with modern corporate branding.[span_109](start_span)[span_109](end_span)

| Feature | Slidev | Marp | Typst |
| :--- | :--- | :--- | :--- |
| **Rendering Engine** | HTML/CSS via Headless Chromium | HTML/CSS via Headless Chromium | Native Rust Typesetting Engine |
| **Compilation Speed** | Slow (Requires Browser Launch) | Moderate | Ultra-Fast (Millisecond execution) |
| **Dependency Tree** | Massive (Node Modules, Vite, Vue) | Moderate (Marp CLI binary) | Minimal (Single static binary) |
| **Agent Suitability** | Poor (Prone to DOM overflow) | Good | Excellent (Deterministic output) |

### Implementing the Typst Compilation Pipeline

For a fully automated agency, Typst is the undisputed superior choice due to its lack of web dependencies, ultra-fast execution, and deterministic layout algorithms.[span_110](start_span)[span_110](end_span)[span_111](start_span)[span_111](end_span) If an LLM generates text that exceeds the bounds of a Typst slide, the engine deterministically pushes the overflow to a new slide rather than clipping it invisibly out of the DOM.

The implementation strategy requires strict coordination between the agent's prompts and the execution environment. 

1.  **Strict Prompt Engineering:** The LLM must be constrained by rigid formatting rules to prevent typesetting overflow. The prompt must enforce a "Per-Slide Budget" (e.g., maximum 6 bullet points, maximum 50 body words per slide, maximum 1 idea per slide).[span_112](start_span)[span_112](end_span) The LLM is instructed to output its content using Typst markup syntax rather than standard Markdown.
2.  **The Stdio MCP Server:** Generating physical files requires local machine access. A custom MCP server is constructed utilizing the `fastmcp` or `@modelcontextprotocol/sdk` library. Crucially, this server operates over the `stdio` transport layer. This means it runs as a secure local background process, communicating with the agent via standard input and output streams.[span_113](start_span)[span_113](end_span)[span_114](start_span)[span_114](end_span)
3.  **Execution and Compilation:** The server exposes a tool named `compile_minimalist_vertical_slides`. The agent [span_15](start_span)[span_15](end_span)[span_17](start_span)[span_17](end_span)passes the generated Typst markup to this tool as a raw string. The MCP server writes this string to a temporary `presentation.typ` file. It then programmatically prepends a global preamble to the file, injecting the `#set page()` directives that enforce the $9:16$ styling and corporate typography settings.[span_115](start_span)[span_115](end_span)[span_116](start_span)[span_116](end_span) Finally, the server executes the subprocess command `typst compile presentation.typ --format png output_{n}.png`. The server validates the successful creation of the PNG assets and returns their absolute file paths to the agent.

This architecture entirely abstracts the complexity of visual layout away from the language model. The LLM acts purely as a copywriter, while the `stdio` MCP server functions as the deterministic art director, ensuring the output perfectly matches the agency's minimalist brand identity and spatial requirements.

## Orchestration Frameworks and Lifecycle Management

With the individual tooling pathways established—Pexels via an HTTP MCP server, Fal.ai via an HTTP MCP server, and Typst via a local `stdio` MCP server—the final architectural requirement is assembling the orchestrator that manages the multi-agent graph.

Both LangChain and CrewAI provide robust, enterprise-grade adapters for multi-server MCP integrations.[span_117](start_span)[span_117](end_span)[span_118](start_span)[span_118](end_span)

### The LangChain Integration Pattern

LangChain utilizes the `langchain-mcp-adapters` library to instantiate a `MultiServerMCPClient`.[span_119](start_span)[span_119](end_span)[span_120](start_span)[span_120](end_span) This client configuration maps out the diverse transport layers required for the architecture:

```python
client = MultiServerMCPClient({
    "pexels_server": {"transport": "http", "url": "https://internal-media-api/mcp"},
    "fal_server": {"transport": "http", "url": "https://internal-fal-api/mcp"},
    "typst_server": {"transport": "stdio", "command": "python", "args": ["/mcp/typst_server.py"]}
})
```

The application fetches the tools asynchronously via the `client.get_tools()` method and injects them directly into the agent's execution loop. A critical architectural feature of LangChain's MCP implementation is that the client is stateless by default. Each time the agent invokes a tool, LangChain creates a fresh, ephemeral execution context. It executes the tool, retrieves the output, and immediately cleans up the session. This statelessness guarantees memory sa[span_21](start_span)[span_21](end_span)fety, preventing variable bleed between discrete generation tasks.

### The CrewAI Integration Pattern

CrewAI approaches MCP integration through an elegantly declarative Domain Specific Language (DSL) that aligns perfectly with its role-based multi-agent philosophy.[span_121](start_span)[span_121](end_span) Within the agent d[span_22](start_span)[span_22](end_span)efinition, the `mcps` array natively accepts both URLs (for establishing HTTP/SSE transport connections) and structured dictionaries for local `stdio` servers.

For complex, dynamic routing scenarios, CrewAI’s `MCPServerAdapter` can connect to multiple servers concurrently.[span_122](start_span)[span_122](end_span) The adapter handles the lifecycle of the connections, automatically starting and stopping the transports when the context is exited.[span_123](start_span)[span_123](end_span) CrewAI also introduces advanced access control via static tool filtering. [span_24](start_span)[span_24](end_span)[span_26](start_span)[span_26](end_span)Using the `create_static_tool_filter` function, the orchestration layer can explicitly whitelist specific tools (e.g., allowing only `generate_vertical_image` from the Fal server).[span_124](start_span)[span_124](end_span) This drastically limits the LLM's action space, preventing the agent from hallucinating calls to unrelated tools on a shared server, thereby improving execution speed and reducing error rates.

### Systemic Security and Token Management

Autonomous systems executing external commands face severe security implications, particularly concerning credential leakage, unauthorized data access, and prompt injection vulnerabilities. The MCP architecture natively mitigates these risks, provided specific network topologies are strictly enforced.

The foundational principle of MCP security is identity separation. The agentic orchestrator must possess absolute zero knowledge of the underlying API keys. By utilizing MCP servers, the Pexels and[span_33](start_span)[span_33](end_span) Fal.ai authentication tokens are stored exclusively as environment variables on the remote servers executing the logic. If the LLM is compromised by a malicious script input designed to exfiltrate data, the system remains secure because the agent literally cannot access the keys.

Furthermore, CrewAI security documentation strictly warns against the architectural anti-pattern of "token passthrough," wh[span_43](start_span)[span_43](end_span)[span_45](start_span)[span_45](end_span)[span_47](start_span)[span_47](end_span)ere an MCP server blindly forwards an access token provided by the agent. The architecture must ensure that the MCP server intrinsically handles its own authentication to third-party endpoints, validating the token's audience claim independently.

Network binding provides the final layer of defense. The Typst `stdio` MCP server, which compiles binaries and reads the local file system, must be [span_34](start_span)[span_34](end_span)restricted strictly to local processes. Binding the server to the `127.0.0.1` loopback address eliminates any possibility of remote execution vectors. Remote HTTP MCP server[span_35](start_span)[span_35](end_span)s must universally enforce HTTPS to encrypt data in transit, protecting against eavesdropping and man-in-the-middle attacks as the agent transmits potentially sensitive script data across the internet.

## Conclusion

The construction of a fully automated, multi-agent AI media agency necessitates a [span_36](start_span)[span_36](end_span)complete departure from monolithic, hardcoded scripting in favor of highly decoupled, protocol-driven microservices. The Asset Generation phase represents the most technically demanding component of this pipeline due to its [span_37](start_span)[span_37](end_span)strict mathematical adherence to the $9:16$ vertical aspect ratio, demanding high-fidelity visual composition devoid of human intervention.

Based on an exhaustive analysis of available foundational models, application programming interfaces, and agentic frameworks, the recommended architecture for the autonomous agent relies entirely on the deployment of independent **Model Context Protocol (MCP)** servers, orchestrated by a high-level framework such as **CrewAI** or **LangChain**.

The final architectural blueprint is delineated as follows:

1.  **B-Roll Video Provisioning:** The architecture must utilize the **Pexels API** encapsulated within a custom HTTP MCP server. Pexels natively supports the critical `orientation=portrait` parameter, and its deep metadata structure allows the MCP server to programmatically filter the `video_files` array to extract `.mp4` URLs that perfectly match the required $1080 \times 1920$ resolution requirements, guaranteeing zero pixel distortion.
2.  **Native AI Image Generation:** The system must deploy the **FLUX.1 [schnell]** model via **Fal.ai**, integrated through an HTTP MCP server.[span_125](start_span)[span_125](end_span)[span_126](start_span)[span_126](end_span) Fal.ai provides superior inference speed and cost-efficiency. The MCP server manages the modulo 32 dimensional[span_57](start_span)[span_57](end_span) requirements (e.g., requesting $1024 \times 1824$) and strictly handles the platform's safety checker flags to prevent hallucination loops.[span_127](start_span)[span_127](end_span)[span_128](start_span)[span_128](end_span)[span_129](start_span)[span_129](end_span)
3.  **Presentation Slide Generation:** The architecture must discard web-based rendering frameworks like Slidev and Marp. Instead, it employs **Typst**.[span_130](start_span)[span_130](end_span)[span_131](start_span)[span_131](end_span)[span_132](start_span)[span_132](end_span) A local `stdio` MCP server receives generated markup from the agent, applies deterministic `#set page()` formatting directives, and compiles the document into static PNG assets using the standalone Rust binary. This ensures unbreakable formatting and millisecond execution times completely isolated from DOM rendering race conditions.

By embracing this decentralized, MCP-driven methodology, the AI media agency guarantees a system that is fundamentally secure, highly resilient against API schema drift, and infinitely scalable as foundation models and stock library ecosystems inevitably evolve.