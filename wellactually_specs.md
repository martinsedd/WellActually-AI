# WellActually: Project Specification

Version: 1.0.0-Blueprint
Status: Approved for Phase 0
Governance: Benevolent Dictator Model
Author: Ed Martins, AKA 'The Only Man with a Mustache Thick Enough to Rule'

---

## 1. Project Manifesto & Identity

### 1.1 The Mission: "An Intervention, Not a Linter"

WellActually exists to provide the brutal, context-aware architectural feedback your coworkers are too polite (or too tired) to give.
It is not a tool for checking semicolons or indentation; it is a tool for enforcing structural integrity. It is desined to be the
"Snarky Senior Dev in a Box" -- an advisor that understands the difference between a messy microservice and a pristine domain entity,
and isn't afraid to let you know when you've crossed the line.

### 1.2 Core Pillars of Identity

- Context Over Rules: Traditional linters are blind. WellActually sees. It understands that code in a `services/` directory
  has different responsibilities than a code in a `domain/` directory. It judges you based on your intent, not just your syntax.

- The "Roast-to-Help" Ratio: Feedback is delivered with a bite. The "WellActually" personna is cynical, witty, and unapologetically
  judgemental. If the code is good, it remains silent or gives a nod of approval. If the code is a disaster, it initiates an intervention.

- Privacy by Isolation: Your code is your intellectual property. WellActually is local-only. No cloud, no telemetry, no "community learning"
  through data harvesting. If the tool gets smarter, it's because YOU taught it on your machine.

- No Compromises on Performance: We refute the "CPU fallback" mentality. To think deeply about code in real-time requires a GPU. If you don't
  have the hardware, you aren't the target audience. We optimize for the 10% of developers who have the rigs to run high-fidelity local inference.

- Read-Only Integrity: WellActually is a mentor, not a janitor. It will show you "Better Code", explain "Why", and roast your "Current Code",
  but it will never touch your files. The burden of improvement remains where it belongs: on the developer.

### 1.3 The "Benevolent Dictator" Governance

WellActually is an open-source project governed by a "My Repo, My Rules" philosophy.

- Community Fuel: We welcome contributions for new personalities, language parsers, and conventions.

- Curation: The official repository is curated to maintain the specific "WellActually" soul. We reject "toxic" feedback that attacks the person,
  but we embrace the "roasty" feedback that attacks the code.

- Freedom of Forking: If you find us too anoying or the rules too strict, you are encouraged to use the `--foggie` flag (our official "shame mode")
  or fork the project.

---

## 2. System Architecture: The Modular Monolith

### 2.1 Pattern: Bounded Contexts with Strict Facades

WellActually is implemented as a Modular Monolith in Pure Python. Each core is a "Black Box" package that exposes a public API via its `__init__.py`.
Direct imports of internal modules across core boundaries are strictly forbidden.

### 2.2 The Eight Cores

1. Core-Orchestration: The only module allowed to import other cores. Manages workflows (Watch vs. Report) and wired dependencies.
2. Core-CLI: Handles argument parsing (Typer) and terminal rendering. It handles the "Personality" translation.
3. Core-IO: Handles file system monitoring (Watchdob), event deboucing (1s), and pre-flight GPU checks.
4. Core-Structure (The Map): Wraps Tree-sitter + KuzuDB. Performs the "Genesis Scan" (Heavy Read) and incremental graph updates.
   Handles Cypher queries for dependencies and circularity.
5. Core-Analysis (The Judge): The "Deterministic Logic" layer. Applies rules based on Graph Facts (from Core-Structure) and local context.
6. Core-Inference: Manages Ollama API calls, hash-based caching, and dynamic context expansion.
7. Core-ML: Uses Pandas for historical tracking and report generation. (Anomaly Detection deferred to v2.0)
8. Core-Persistence: Manages LanceDB (Ledger) and KuzuDB(Graph) storage layers.

---

## 3. Algorithmic Strategies

### 3.1 Convention-Based Analysis (The "Judge")

The tool combines file patterns with deterministic Graph queries to determine "Architectural Truth."

- **Deterministic Checks:** KuzuDB runs Cypher queries to detect Circular Dependencies and Layer Violations before the LLM is even called.

| Location | Convention | Architectural Expectation | SRP Tolerance |
|**\*\***\_**\*\***|\***\*\_\_\_\_\*\***|**\*\*\*\***\*\***\*\*\*\***\_\_**\*\*\*\***\*\***\*\*\*\***|**\*\***\_\_\_**\*\***|
|services/ | Service | Orchestration of multiple concerns | High (3-5) |
|domain/ | Entity | Pure business logic, no side effects | Strict (1) |
|controllers/ | Controller | Request handling, routing, mapping | Moderate (2-3)|
|legacy/ | Legacy | Technical debt acknowledged | None (Ignored)|
|**\*\***\_**\*\***|\***\*\_\_\_\_\*\***|**\*\*\*\***\*\***\*\*\*\***\_\_**\*\*\*\***\*\***\*\*\*\***|**\*\***\_\_\_**\*\***|

### 3.2 Dynamic Context Expansion

To Solve context window limits, WellActually uses recursive expansion:

1. Graph Neighborhood: Query KuzuDB for the 5 most-relevant neighboring interfaces/dependencies.
2. Recursion: If Method A calls private Method B, pull Method B into the LLM prompt.
3. Signatures: If the context gets too large, prune method bodies to signatures only, preserving the "Shape" for the LLM while saving tokens.

### 3.3 The Noise Management Protocol

- Consolidation: >3 violations of the same type in one file are collapsed into a single summary notification.
- Disaster Mode: If violation density exceeds 4 per 100 lines of code, the tool triggers a "Disaster Summary" with a strategic menu of where the user
  wants to start.

---

## 4. Machine Learning & Data Strategy

WellActually separates "recognition" into two distinct layers to ensure both instantaneous performance and cross-project intelligence

### 4.1 The Cache: Deterministic AST Hashing (Speed)

- Purpose: Instantaneous lookup for "On Save" feedback
- Mechanism: The Core-Parser generates a normamized AST for the code block (e.g., a method or class) where identifiers, variable names, and comments are stripped,
  leaving only the structural logic. This structure is then hashed.
- Behavior: If you rename a variable (user_data to user_input) but leave the architectural logic identical, the hash remains stable.
- Performance: <50ms. Allows the tool to retrieve a previous LLM explanation from LanceDB without triggering a new GPU inference cycle.

### 4.2 The Brain: Semantic Vector Identity (Intelligence)

- Purpose: Cross-language pattern recognition and personal style tracking.
- Mechanism: Every code violation is passes through a multi-lingual embedding model to generate a high-dimensional vector, stored in the global LanceDB ledger.
- Behavior: This enables the tool to recognize "Semantic Similarity" rather than "Structural Identity"
  - Cross-Language Case: If you repeat an architectural mistake in a TypeScript project that you previously ignored in a Python project, the tool recognizes
    the semantic intent of the mistake and reminds you.
  - Vibe checks: This provides the baseline for Anomaly Detection, flagging code that is technically valid but an outlier compared to your historical "Good"
    patterns.
- Performance: 100ms - 300ms. Runs in parallel with the LLM or as a background side-effect

---

## 5. User Interaction & Personality

### 5.1 The Roasty Feedback Loop

The default experience is a streaming terminal feed.

- Positive Reinforcement: "Well... actually, this is good."
- The Roast: "So you're putting persistence in a domain entity? Bold choice."
- The `--foggie` Flag: For teams who want the "Boring/Serious" version. Invoking this flag is itself tracked as a point of minor shame.

### 5.2 The Ignore "Escape Hatch"

Users can ignore violations, but they must provide a reason. This triggers the "Android's Hell" warning:

"If you ignore everything, I'll become a voyeur of your poor coding decisions... if you're ever wondered if androids dream of their personal hells, this one might be it for me."

---

## 6. The Holy Trinity Persistence Strategy

WellActually utilizes a dual-engine persistence layer to separate "The Map" (Structural Reality) from "The Memory" (Developer History).
This reduces LLM dependency to a semantic "gap-filler" and personality engine

### 6.1 The Map: KuzuDB (Graph)

We use KuzuDB as an embedded, in-process Graph database to maintain a deterministic map of the system.

- Technology: KuzuDB (C++ backed, Cypher query support).
- Genesis Scan: A background "Heavy Read" during project initialization that parses all files via Tree-sitter to build a graph of imports, calls
  and inheritance.
- Incremental Updates: On save, the tool triggers a structural update only for the changed file, ensuring the graph remains a live reflection of the codebase.
- Truth Source: Provides 100% accurate structural facts (e.g., Circular Dependencies, Layer Violations) via Cypher, eliminating LLM hallucinations in architectural reasoning.

### 6.2 The Memory: LanceDB (Ledger)

We use LanceDB for the permanent violation ledger and semantic caching.

- Technology: LanceDB (ML-native, Vector-compatible)
- Global Ledger: A centralized record in `~/.config/wellactually/` that tracks every violation and ignore event.
- Vectorization: Every code snippet is vectorized and stored, allowing the tool to recognize repeating patterns across different projects.
- Project Portability: Since the ledger is global, the tool learns your personal architectural style and follows you across your entire development environment.

### 6.3 Performance Caching (Semantic Block-level)

To ensure feedback remains sub-5 seconds, WellActually hashes logical blocks (Methods/Classes) identified by the parser.

- Logic: We hash the content of the block, not the file.
- Benefit: Adding imports or comments elsewhere in the file does not invalidate the cache for unchanged methods, allowing instant retrieval of
  previous LLM explanations.

### 6.4 The "Sanity Hatch" Persistence

Ignores are stored exclusively in LanceDB to maintain the Read-Only pillar.

- String Invalidation: An "Ignore" is tied to a specific `core_snippet_hash`. If the logic of the ignored code changes, the ignore code changes,
  the ignore is invalidated, and the tool resumes its critique.

### 6.5 Intelligence Export

- Fine-Tuning Data: On-demand, Core-Persistence exports its ledget to `jsonl`. This dataset pairs detected violations with user-provided ignore
  reasons, serving as the high-signal training set for personalized model fine-tuning.

---

## 7. Version Roadmap

### 7.1 v1.0: "The Architect's Foundation"

The goal of v1.0 is to establish the "Trinity" foundation: deterministic graph logic, permanent memory, and a roasty human interface.

Language & Extensibility

- Official Support: Tier-1 support for TypeScript and Python
- Plugin Engine: Launch of the YAML-based Plugin API for community-contributed new Language Parses, Personalities, Conventions, and Rule Sets.

The Analysis Engine (v1.0)

- Workspace Awareness (The Heavy Read): Project initialization includes the KuzuDB "Genesis Scan" to map the entire project.
- Deterministic Guardrails: Hard-logic checks for Circular Dependencies and Layering violation (e.g., "Domain cannot import Infrastructure")
  powered by Cypher queries.
- The Big 5 Smells: LLM-assisted detection of SRP, DRY, Naming, Complexity, and God Class.
- Graph-Augmented Context: LLM prompts are injected with the "Neighborhood" of the changed file (neighboring interfaces and dependencies)
  retrieved from KuzuDB.

Intelligence & Persistence

- Trinity Stack: Full integration of KuzuDB (Graph), LanceDB (Ledger), and Ollama(Inference).
- Semantic Caching: Block-level hashing for near-instant feedback on previously analyzed code.

Reporting & Integration

- Human Interface: The roasty CLI stream + `--foggie` flag.
- CI/CD Pack: JSON schema export and Markdown report generation.

### 7.2 Future: "The Intelligent Assistant"

Learning Mode - Anomaly Detection: Activation Scikit-learn (IsolationForest). After a baseline is established in the LanceDB ledger, WellActually will flag
code taht deviates significantly from the developer's historical "good" patterns.

Autonomous Intelligence - One-Click Fine-Tuning: Automated background training that exports data to `ollama finetune` and hot-swaps the new weights into the inference core. - Style Drift Analysis: Reports visualizing architectural discipline trends over months or years.

Ecosystem Expansion - Tier-1 Promotion: Curating community contributions to bring Java, C#, Rust, and Go to full supported status. - TUI Dashboard: A full-screen terminal interface for navigating the "System Graph" and violation clusters.

Collaborative Patterns - Shared Intelligence: Encrypted, local-first syncing of "Ignore Ledgers" to allow teams to train a shared "Architectural Identity" without
compromising individual privacy.

### 7.3 Brainstorm: What can we achieve within this Architecture?

Leveraging the synergy between deterministic Graph logic (KuzuDB), vector-based memory (LanceDB), and a snarky LLM personality, we can expand the tool's
intervention capabilities beyond simple save-events.

1. Architectural Impact Simulation ("The Architec's Sandbox")
   - The Concept: A "What-If" command tha allows the user to simulate structural changes before writing code (e.g., `wellactually impact "move X to Y`).
   - Technical Leverage: Uses KuzuDB to calculate the dependency ripple effect. It finds all incoming edges to the target node and evaluates if the new
     location violates any defined Layer Guardrails.
   - Persona Impact: Allow the tool to roast the user's plans before they even commit to them. "Actually... moving that class would break 14 imports
     and create circular dependency. Time to rethink life choices..."
2. The "Blast Radius" Metric (Quantifying Shame)
   - The Concept: Assigning a priority score to every violation based on how much the "polluted" code affects the rest of the system.
   - Technical Leverage: Uses KuzuDB centrality algorithms (e.g., PageRank or Degree Centrality) to identify "Hub" files. A violation in a file with
     50 dependents receives a higher "Blast Radius" score than a leaf-node file.
   - Persona Impact: Helps prioritize refactoring by heightening the stakes. "This SRP violation has a blast radius of 85%. You've effectively
     poisoned the entire infrastructure layer. Refactor this now or start looking for a new job."\
3. Version-Specific Library Awareness (Semantic RAG)
   - The Concept: Providing advice that isn't just "Good Code" in general, but "Correct Code" for specific versions of frameworks (e.g., FastAPI,
     React, SQLAlchemy).
   - Technical Leverage: Uses LanceDB to store vector embeddings of library documentation. When a violation is detected in code using a speficic library,
     the tool performs a similarity search to pull relevant documentation snippets into the LLM prompt.
   - Persona Impact: Elevates the snark to "Technical Snobbery". "Actually... you're using the v1.0 syntax for this library. The v2.1 docs explicitly state
     this is deprecated. I thought you liked being modern?"
4. Git-Correlated "Guilt" Tracking
   - The Concept: Differentiating between "Legacy Debt" (old code) and "Regressions" (code written minutes ago).
   - Technical Leverage: Core-IO executes local `git blame` or `git diff` on the code block being analyzed. LanceDB records the author and timestamp
     of the regression.
   - Persona Impact: Makes the intervention personal and time-aware
     - Legacy code: "This code is a fossil from 3 years ago. It's ugly, but I know it wasn't you"
     - New regression: "Actually... you wrote this five minutes ago. I'm literally watching you make the codebase worse in real-time. Stop it."

## 8. Performmance Strategy & Execution Model

To ensure a "Snarky Senior Dev" experience rather than a "Sluggish Linter" experience, WellActually follows a `Conductor Architecture`: using Python
to orchestrate high-performance C++ components and concurrent I/O.

### 8.1 Concurrency & Execution Flow

WellActually avoids the Python Global Interpreter Lock (GIL) bottlenecks by matching the task type to the appropriate concurrency primitive:

| Task Type | Example | Mechanism |

CPU-Bound (Parsing) -> Genesis Scan / Project Indexing -> `multiprocessing` (Parallel batches)
I/O-Bound (Inference) -> Ollama API / LanceDB lookups -> `asyncio` (Non-blocking event loop)
Background Side-Effects -> ML Tracking / Persistence Logging -> `asyncio.Queue` (Fire-and-forget)

### 8.2 The "Genesis Scan" (Project Initialization)

Upon project init, WellActually performs a "Heavy Read" of the codebase.

- Multiprocessing: Files are distributed across all CPU cores for Tree-sitter parsing.
- Incremental State: The results are streamed into KuzuDB, creating a persisted structural baseline that survices tool restarts.

### 8.3 On-Save Optimization (The 5s Goal)

Every file save must trigger a roast in under 5 seconds.

- Semantic Caching: If the hash of the code block matches an entry in LanceDB, the previous LLM response is returned <50ms.
- Deterministic Pre-emption: If KuzuDB identifies a structural violation (e.g., Layer Violation), the CLI renders a "Static Roast"
  immediately while the LLM generates semantic nuances in the background.
- Streaming UX: All LLM feedback is streamed to the terminal word-by-word, reducing perceived latency ot te "Time to First Token"
  (~500ms on recommended hardware).

### 8.4 Resident Memory Management

- VRAM Warmp-up: On startup, WellActually pings the LLM core to ensure CodeLlama is resident in GPU memory.
- C++ Native Offloading: The heavy lifting of Graph Traversal (KuzuDB) and Vector Search (LanceDB) is executed in native C++ binaries,
  bypassing Python's runtime limitations

### 8.5 Binary Distribution & Environment

- Self-Correction: WellActually includes a pre-flight "Doctor" command to verify GPU drivers, Ollama avalability, and C-compiler status
  for Tree-sitter bindings.
- No CPU Fallback: By explicitly refusing to run on CPU, we prevent the "Bad First Impression" of 60-second inference times.

---

## 9. Pitfalls, and how to avoid them

### 9.1 Environment & Infrastructure

- Pitfall: Tree-sitter Grammar Hell. Tree-sitter requires compiled C-binaries for language grammars. Missing compilers (gcc/clang) on the host
  machine will break the init process
  - The fix: v1.0 will bundle pre-compiled binaries for Tier-1 languages. A `wellactually doctor` command will provide exact shell commands to install
    build tools for Tier-2 languages.
- Pitfall: VRAM Overcrowding. Running a 7B LLM alonside a high-fidelity embedding model (like `unixcoder`) can exceed the 8GB-12GB VRAM threshold.
  - The fix: Run the Semantic Vector Identity model on the CPU. Vectorization is a one-shot operation per save; the latency hit is negligible compared to the
    memory savings for the LLM.

### 9.2 Data Integrity (The Map & The Memory)

- Pitfall: KuzuDB Write Contention. Multiple worker processes attempting to write an embedded database during the "Genesis Scan" will
  cause "Database Locked" errors.
  - The fix: Implement a Producer-Consumer Pattern. Worker processes parse code and return flat DTOs; a single-threaded consumer owns
    the KuzuDB connection and executes batch `INSERT` operations.
- Pitfall: Zombie Edges. If a file is renamed or deleted and the Graph isn't notified, the "Map" becomes a hallucination of stale dependencies.
  - The fix: The Core-IO watcher must handle `MOVED` and `DELETED` events specifically to trigger `DETACH DELETE` Cypher queries,
    ensuring the structural truth remains current.
- Pitfall: Database Bloat. Vectorizing every save will cause LanceDB to explode in size within weeks.
  - The fix: Only vectorize Violations and Ignores. This keeps the "Brain" focused strictly on significant architectural events.

### 9.3 Caching & Identity

- Pitfall: Aggressive Normalization. If AST normalization strips all method names, a "Database Violation" and an "Email Violation"
  might produce identical hashes.
  - The fix: Normalization must strp Local Identifiers (variable names) but preserve External Method Calls (the "names of the sins").
- Pitfall: Stale Invalidation. Disabling a rule in `config.yaml` might not stop a cached roast from appearing.
  - The fix: Use Compound Hashes. The cache key is SHA-256(Normalized_AST + Active_Rule_Set-Version). Changing a rule automatically
    invalidates the relevant cache entries.
- Pitfall: Line Number Fragility: Tying an "Ignore" to a specific line number breaks as soon as code is added above it.
  - The fix: Ignores are tied to the AST Bloch Hash. As long as the logic of the method is unchanged, the ignore follows the block
    regardless of its position in the file.

### 9.4 LLM Context & Reasoning

- Pitfall: The Token Tsunami. Sending 1K individual violations to the LLM during an "Audit" will exceed context limits and crash the process.
  - The fix: Pre-Aggregation. Use Core-ML (Pandas) to group the count violations. The LLM only sees the statistical summary and the top 5 "Blast Radius" offenders.
- Pitfall: Semantic Drift. A Python God-class looks structually different than a TypeScript God-class, which might confuse the "Cross-Language Deja Vu" logic.
  - The fix: The similarity search should use Heuristic Weighting. The tool compares the Vector Embedding (Semantic) alongside Structural Metrics
    (Method count/Centrality) to confirm a match.

### 9.5 Workflow & UX

- Pitfall: Syntax Error Blocking. Tree-sitter returns an `ERROR` node for invalid syntax, which can lead to nonsensical roasts if the LLM attempts to analyze it.
  - The fix: Core-Parser must detect `ERROR` nodes first. The tool will emit a "Pre-emptive Roast" telling the user to fix their syntax before an architectural
    critique is possible.
- Pitfall: VRAM Cold Starts. The first save of the session can take 30s as the GPU loads the model.
  - The fix: VRAM Warm-up. On `wellactually watch` startup, a no-op prompt is sent to Ollama to ensure the model is resident and ready for the first save.
- Pitfall: The "Creeping Sin". A user ignores a bad method, then makes it 10x worse, but the ignore remains active.
  - The fix: Strict Invalidation. Because ignores are tied to the block hash, any logic change invalidates the ignore. If you make the mess bigger, the tool resumes roasting.
