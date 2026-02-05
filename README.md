# WellActually

**"An Intervention, Not a Linter."**
WellActually is a modular monolith designed to provide brutal, context-aware architectural feedback. It uses a combination of
deterministic graph queries and local LLM inference to enforce structural integrity.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![KuzuDB](https://img.shields.io/badge/KuzuDB-Graph-purple?style=for-the-badge)
![LanceDB](https://img.shields.io/badge/LanceDB-Vector-blue?style=for-the-badge)

---

## Engineering Highlights

- **The Holy Trinity Persistence Layer:**
  - **KuzuDB (The Map):** Handles deterministic structural trugh (Circular dependencies, Layer violations) via Cypher.
  - **LanceDB (The Memory):** A global vector ledger that tracks architectural regressions and "ignore" history across projects.
  - **Ollama (The Voice):** Local-only GPU inference for snarky, high-fidelity code reviews.
- **Context-Aware Empathy System:** Features a dynamic "humor throttle" that monitors session-based violation density and time-on-task
  to tone down the snark if the developer is having a particularly difficult day.
- **AST-Normalized Hashing:** Sub-50ms cache lookups that recognizes logical structural identity even when variable names or comments change.
- **Read-Only Integrity:** WellActually acts as a mentor, never a janitor. It identifies the "Why" and "How", but the burden of improvement remaisn
  on the developer

## What does an "Intervention" look like?

WellActually isn't a linter; it's a conversation. Here is how the tool reacts to common architectural "crimes":

### Scenario 1: The "Swiss Army Knife" (SRP Violation)

**The Crime:** You add a `send_marketing_email()` method to a `UserDomain` entity that already handles password hashing and database mapping.

**The Intervention:**

```text
$ "Well, actually, your `UserDomain` class is currently having an identity crisis. My analysis shows **3 distinct semantic clusters** (Persistence, Auth, and Communication)
and a **Naming Entropy score of 0.82**. You've effectively built a Swiss Army Knive out of duct tape. Move the email logic to a Service before I lose respect for your git history."
```

### Scenario 2: The "Circular Spaguetti" (Graph Violation)

**The Crime:** `OrdersService` imports `PaymentService`, but `PaymentService` needs to check `OrdersService` to verify a total. You save the file

**The Intervention:**

```text
$ "Stop right there. KuzuDB just flagged a **Circular Dependency** loop: `Orders` -> `Payments` -> `Orders`. You're creating a digital Ouroboros.
This isn't 'decoupling', it's a suicide pact for your test suite. Refactor the shared logic into a `PricingEngine` or I'm telling the CTO."
```

### Scenario 3: The "Layer Leaker" (Guardrail Violation)

**The crime:** You're in a `Controller` and decide it's easiner to just call `db.execute("SELECT...")` instead of using a Repository.

**The Intervention:**

```text
$ "Bold choice. You've just triggered a **Layer Violation Boost**. Controllers shouldn't know the Database exists, yet here you are, importing `sqlalchemy` in
the presentation layer. I've logged this in your **LanceDB Ledger** as a 'Tactical Regret'. Try using the Repository I know you already wrote."
```

### Scenario 4: The "Hard Day" (Empathy Mode)

**The Context:** It's 8:00PM on a Friday. You've triggered 12 violations in the last hour.

**The Intervention:**

```text
$ "I see you're still at it. Look, that last method is technically a 'God Object' (Complexity score: 0.91/1.0), but we've both had a long day.
Just add a `# TODO` and go get a beer. We'll fix your architectural sins on Monday."
```

## Architecture: Modular Monolith

WellActually is architected as a **Modular Monolith** emploting a strict \*_Facade Design Pattern_. Each core (e.g., `Core-Inference`, `Core-Structure`)
encapsulates its inner complexities behind a singular, public-facing Facade (e.g., `InferenceFacade`).

This ensures (hopefully):

- **Strict Encapsulation:** Internal logic, third-party libraries specifics, and helper functions are hidden; external consumers have
  "no business knowing" the underlying complexity.
- **Stable Public API:** Orchestration only intereacts with Facades, allowing developers to refactor the internal guts of a core without breaking
  the entire system.
- **Contributor-Friendly Isolation:** Community members can build new features inside a core with total confidence that they won't leak side effects
  into the rest of the monolith

```text
[ Core-Orchestration ]
        |
        v
    +---+-----------------------+---------------------------+
    | [ StructureFacade ]       |   [ AnalysisFacade ]      |
    | - Tree-sitter             |   - SRP Heuristics        |
    | - KuzuDB / Cypher         |   - Pattern Matching      |
    +---+-----------------------+---------------------------+
    | [ InferenceFacade ]       |   [ PersistenceFacade ]   |
    | - Ollama / GPU            |   - Cache                 |
    | - Semantic Hashing        |   - LanceDB               |
    +---+-----------------------+---------------------------+

```

## Designed for Open Source

The Facade architecture serves as a "Contributor Guardrail." By exposing only what is necessary,
the project provides a clean entry point for:

- **Logic Contributors:** Improve internal heuristics within `Core-Analysis` without needing to
  understand VRAM management in `Core-Inference`.
- **Language Specialists:** Extend the `StructureFacade` to support new grammars while relying on the
  existing Graph logic.
- **Personality Designers:** Hot-swap `PersonalityFacade` implementations to shift the tool's soul from
  "Cynical Architect" to "Core Buddy."

### The "Benevolent Dictator" Governance

While we embrace the "My Repo, My Rules" philosophy to maintain the tool's cynical soul,
the code base is strictly curated to ensure high-signal contributions and architectural purity.

## Project Status: Phase 3 (The Judge)

We are currently deep in the **Analysis** phase, focusing on deterministic architectural heuristics.

| Module               | Status      | Technical Notes                                                                                         |
| :------------------- | :---------- | :------------------------------------------------------------------------------------------------------ |
| **Graph Parser**     | Complete    | Tree-sitter to KuzuDB mapping for Python                                                                |
| **Inference Core**   | Complete    | Semantic caching and dynamic context expansion                                                          |
| **Core-Analysis**    | In Progress | **Current Focus:** Multi-signal SRP scoring system combining semantic, dependency, and naming diversity |
| **Memory Ledger**    | In Progress | Vectorized regression tracking in LanceDB                                                               |
| **Language Support** | Partial     | Python (Tier-1) operational; TypeScript (Tier-1) skeleton initialized                                   |

### Current Challenge: Algorithmic SRP Detection

We have moved beyond simple line-count metrics to a **Multi-Signal SRP Scoring Engine**. Single Responsibility Principle violations are now
detected via four primary vectors:

1. **Semantic Clustering (ML-Driven):** Utilizing **DBSCAN clustering** on method signature embeddings to identify unrelated semantic clusters within
   a single class.
2. **Dependency Domain Mapping:** Categorizing imports into concert domains (e.g., Persistence, Communication, Security) to detect "Concert Drift".
3. **Naming Entropy:** Applying **Shannon Entropy** to method verb categories to calculate the statistical diversity of class responsibilities.
4. **Layer Guardrails:** Deterministic Cypher queries in KuzuDB that trigger "Layer Violation Boots" when, for example, a Domain entity imports
   Infrastructure-layer repositories

#### The scoring Formula

```python
total_score = (
    0.4 * semantic_diversity +
    0.3 * dependency_diversity +
    0.2 * naming_diversity +
    0.1 * method_count_diversity +
    layer_violation_bost
)
```

_A score of >= 0.7 triggers a "High Severity" intervention._

---

## Performance Requirement

**GPU-Bound Inference:** WellActually explicitly refutes "CPU fallback" for its LLM. To ensure high-fidelity architectural reasoning in near real-time,
a dedicated GPU (CUDA/ROCm/Apply Silicon) is required.

---

**Author:** Eduardo Martins - Feb 2026
