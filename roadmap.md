# WellActually v1.0 Execution Roadmap

## Phase 0: The Skeleton

Goal: Establish the Modular Monolith and the core execution loop.

- [ ] Project Setup: Initialize Python repo with the `cores/` package structure and strict
  `__init__.py` facades.
- [ ] Core-IO(The Trigger): Implement the watchdog event loop with the 1s debouce and temporary file filtering.
- [ ] Core-CLI(The Interface): Build the base Typer app with `watch`, `init` and `doctor` commands.
- [ ] Ollama Wiring: Establish a robust async connection to the Ollama local API and implement the "VRAM Warm-up" ping.
- [ ] Pre-flight Doctor: Implement checks for NVIDIA/Apple/AMD GPU availability and C-compiler presense

## Phase 1: The Map (KuzuDB Strategy)

Goal: Implement deterministic structural awareness

- [ ] Tree-sitter Integration: Setup Tier-1 parsers (TypeScript/Python) and bundle pre-compiled binaries.
- [ ] The Genesis Scan: Implement the `multiprocessing` worker pool to parse an entire project and batch-insert
  results into KuzuDB
- [ ] Structural Schema: Define Graph nodes (File, Class, Interface) and edges (Depends_On, Implements, Calls).
- [ ] Delta Updates: Implement the "On-Save" logic: delete old file node/edges and recreate them in the graph.
- [ ] Fact Queries: Write the initial Cypher queries to detect Circular Dependencies and Layer Violations
  (e.g., Domain -> Infra).

## Phase 2: The Memory (LanceDB Strategy)

Goal: Implement the history ledger and high-speed cache.

- [ ] LanceDB Setup: Initialize the global ledger in `~/.config/wellactually/`.
- [ ] The Deterministic Cache: Implement the AST Normalization logic (strip identifiers) to create stable hashes
  for method-level caching.
- [ ] The Violation Ledger: Create the schema for storing previous roasts, severity levels, and vector embeddings of the code.
- [ ] Vector Pipeline: Integrate a lightweight CPU-based embedding model (e.g., `all-MiniLM-L6-v2`) to vectorize violations
  for future similarity checks.

## Phase 3: The Judge & The Voice (LLM Integration)

Goal: Synthesize facts and personality into the "Trinity" prompt.

- [ ] Prompt Engineering: Build the system prompt that injects:
  - HARD FACTS from KuzuDB.
  - HISTORICAL CONTEXT from LanceDB.
  - SEMANTIC CONTEXT from the parser (method helpers).
- [ ] The Analysis Engine: Implement the "Big 5" rules (SRP, DRY, Naming, Complexity, God-Class) using the Trinity context.
- [ ] Streaming Feedback: Implement the CLI streamer so tokens appear on screen as they generate (<500ms TTFT).
- [ ] Pre-emptive Roasting: Create "Static Roasts" for Graph-detected errors to show before LLM inference starts.

## Phase 4: Personality & Plugin API

Goal: Open the tool to customization and personal control.

- [ ] YAML Plugin Engine: Build the loader for `personalities/` and `conventions/`.
- [ ] Personality Packs: Finalize the "Roasty" (default), "Pirate", "Zen", and "--foggie"(shame) variants.
- [ ] The Ignore Hatch: Implement the `wellactually ignore` command with the "Android's Hell" warning and the
  `finetune.jsonl` export side-effect.
- [ ] Convention Detection: Finalize the logic that applies different SRP/Complexity thresholds based on directory location.

## Phase 5: The Audit & CI/CD

Goal: Enable system-wide reporting and pipeline integration

- [ ] Codebase Mode: Implement `wellactually codebase .` that runs global Cypher queries and violation counts.
- [ ] The Pandas Core: Implement statistical aggregation and "Blast Radius" calculations based on Graph centrality.
- [ ] Export Engine: Generate Mardown `CODE_REVIEW.md` and the standard JSON schema for CI/CD usage.
- [ ] Build Guard: Add a command line flag to exit with status code 1 on critical architectural failures

## Phase 6: Hardening & Public Launch

Goal: Polish for the open-sourcing community.

- [ ] Snapshot testing: Implement tests to ensure personalities don't break during engine updates.
- [ ] Migration Logic: Ensure LanceDB/KuzuDB can handle schema updates without losing user data.
- [ ] Documentation: Finalize `README.md`, `CONTRIBUTING.md` (detailing the Benevolent Dictator model),
  and installation guides.
- [ ] v1.0 Release: Push to GitHub and PyPI.

---

# Critical Path Checklist

- [ ] Rule #1: GPU is present? (Stop if false)
- [ ] Rule #2: Feedback <5s? (Optimize if false)
- [ ] Rule #3? Tool is snarky? (Adjust prompt if false)
