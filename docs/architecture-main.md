# Architecture Documentation: `main` Branch

## 1. Process Run with the Orchestrator

The `main` branch implements a **3-phase optimization loop with severity-tiered iteration**. The orchestrator manages state transitions by checking which files exist on disk.

### Workflow Overview

```mermaid
flowchart TD
    Start([User: Optimize performance]) --> Orch

    subgraph "Skill: optimization-workflow-orchestrator"
        Orch[Orchestrator] --> CheckBL{BENCHMARK_BASELINE.md<br>exists?}
        CheckBL -->|Yes| DetectTier{Detect current<br>severity tier}
        DetectTier --> P2[Invoke PHASE 2 skill<br>for current tier]
        P2 --> P3[Invoke PHASE 3 skill<br>for current tier]
        P3 --> FixResult{Fix<br>succeeded?}
        FixResult -->|Yes| Stop([STOP:<br>Update baseline, commit])
        FixResult -->|No: all failed| NextTier{Next tier<br>available?}
        NextTier -->|Yes| DetectTier
        NextTier -->|No| Done([Done:<br>All tiers exhausted])
    end

    subgraph "Skill: establishing-benchmark-baseline"
        P1[PHASE 1: Create benchmarks<br>Write BENCHMARK_BASELINE.md]
    end

    subgraph "Skill: broad-performance-investigation"
        P2_detail[PHASE 2: Run 4 analysis steps<br>Write PERFORMANCE_THEORIES_TIER.md]
    end

    subgraph "Skill: implementing-performance-fixes"
        P3_detail[PHASE 3: Try fixes one-by-one<br>Update baseline on success]
    end

    subgraph "Skill: deep-performance-investigation"
        Deep[Targeted profiling<br>for uncertain findings]
    end

    CheckBL -->|No| P1
    P1 --> CheckBL
    P2 --> P2_detail
    P2_detail --> P3
    P2_detail -.->|Low confidence| Deep
    Deep -.-> P2_detail
    P3 --> P3_detail
    P3_detail --> FixResult
```

### Severity-Tiered Iteration Detail

```mermaid
flowchart LR
    subgraph CRITICAL
        I1[Investigate] --> F1[Try fixes<br>one-by-one]
    end
    subgraph HIGH
        I2[Investigate] --> F2[Try fixes<br>one-by-one]
    end
    subgraph MEDIUM
        I3[Investigate] --> F3[Try fixes<br>one-by-one]
    end
    subgraph LOW
        I4[Investigate] --> F4[Try fixes<br>one-by-one]
    end

    F1 -->|all failed| I2
    F2 -->|all failed| I3
    F3 -->|all failed| I4

    F1 -->|one succeeds| STOP1([STOP])
    F2 -->|one succeeds| STOP2([STOP])
    F3 -->|one succeeds| STOP3([STOP])
    F4 -->|one succeeds| STOP4([STOP])
    F4 -->|all failed| DONE([All exhausted])
```

### State Detection Logic

The orchestrator determines the current phase by checking files on disk:

1. `BENCHMARK_BASELINE.md` missing -> Phase 1
2. Check `PERFORMANCE_THEORIES_{TIER}.md` files for pending theories -> Phase 3
3. Determine next uninvestigated tier -> Phase 2
4. All tiers complete -> Terminate

### Phase Details

| Phase | Skill | Entry Condition | Output |
|-------|-------|----------------|--------|
| 1 | `establishing-benchmark-baseline` | No `BENCHMARK_BASELINE.md` | `BENCHMARK_BASELINE.md`, benchmark files |
| 2 | `broad-performance-investigation` | Starting new severity tier | `PERFORMANCE_THEORIES_{TIER}.md` |
| 3 | `implementing-performance-fixes` | Theories with `pending` status exist | Updated code, updated baseline |

---

## 2. How AI Context Is Used

The `main` branch uses a **multi-layered context system** where different files provide different scopes of guidance to Claude.

```mermaid
flowchart TD
    subgraph "Plugin Manifest"
        PLUGIN[.claude-plugin/plugin.json<br>- Plugin name & version<br>- Triggers skill discovery]
    end

    subgraph "Skill Context - loaded into agent on invocation"
        SKILL[SKILL.md<br>- Frontmatter: name, description<br>- Quick start steps<br>- Prerequisites<br>- Integration points<br>- Output format]
        WORKFLOW[WORKFLOW.md<br>- Detailed phase-by-phase procedure<br>- In: establishing-benchmark-baseline,<br>  deep-performance-investigation]
        PATTERNS[PATTERNS.md<br>- Problem detection patterns<br>- Fix examples with code<br>- In: cpu-sampler, compiler-graphs]
        EXAMPLE[EXAMPLE.md<br>- Sample output format<br>- In: broad-performance-investigation]
    end

    subgraph "Runtime State Files - read/written during workflow"
        BL[BENCHMARK_BASELINE.md<br>- Benchmark timing data<br>- Language analysis<br>- Execution commands]
        THEORIES[PERFORMANCE_THEORIES_TIER.md<br>- Theories with status/severity<br>- Expected impact estimates<br>- Evidence from tools]
        TOOLOUT[tool-outputs/*.txt<br>- Raw tool output<br>- Profiler results<br>- Compiler graph data]
    end

    PLUGIN --> SKILL
    SKILL --> WORKFLOW
    SKILL --> PATTERNS
    SKILL --> EXAMPLE
    SKILL --> TOOLOUT
    SKILL --> BL
    SKILL --> THEORIES
```

### Context Layers

| Layer | File(s) | Loaded When | Purpose |
|-------|---------|------------|---------|
| Plugin | `plugin.json` | Plugin load via `--plugin-dir` | Skill discovery and registration |
| Skill | `skills/*/SKILL.md` | When skill is model-invoked | Specific procedures, tool options, output format |
| Skill Support | `WORKFLOW.md`, `PATTERNS.md`, `EXAMPLE.md` | Referenced from SKILL.md | Detailed procedures, pattern catalogs, sample outputs |
| Runtime | `BENCHMARK_BASELINE.md`, `PERFORMANCE_THEORIES_*.md` | During workflow execution | State tracking, data exchange between phases |
| Tool Output | `tool-outputs/*.txt` | After tool execution | Raw profiling data for analysis |

### Context Size (main branch)

The `main` branch has **substantial context** per skill:

| Skill | Files | Approx. Context |
|-------|-------|-----------------|
| `optimization-workflow-orchestrator` | SKILL.md (204 lines) | Large: full state machine, tier logic, mermaid diagrams |
| `establishing-benchmark-baseline` | SKILL.md + WORKFLOW.md + EXAMPLES.md | Very large: 5-phase procedure with detailed instructions |
| `broad-performance-investigation` | SKILL.md + EXAMPLE.md (232 lines) | Large: 4-step analysis, theory structure, severity tiers |
| `implementing-performance-fixes` | SKILL.md (162 lines) | Large: fix workflow, status tracking, tier transitions |
| `deep-performance-investigation` | SKILL.md + WORKFLOW.md (257 lines) | Large: targeted profiling, impact estimation |
| Tool skills (7 skills) | SKILL.md + optional PATTERNS.md/QUERIES.md/DUMPING.md | Medium: tool options, output interpretation |

---

## 3. Agent/Skill Call Hierarchy

```mermaid
flowchart TD
    User([User]) -->|Optimize performance| Orch

    subgraph "Orchestrator Layer"
        Orch[optimization-workflow-orchestrator<br>- State detection<br>- Phase routing<br>- Tier management]
    end

    subgraph "Phase Skills"
        P1[establishing-benchmark-baseline<br>PHASE 1]
        P2[broad-performance-investigation<br>PHASE 2]
        P3[implementing-performance-fixes<br>PHASE 3]
        Deep[deep-performance-investigation<br>UTILITY]
    end

    subgraph "Tool Skills"
        CPU[profiling-with-cpu-sampler]
        MEM[profiling-memory-allocations]
        IGV[compiler-graph-analyst]
        EXEC[tracing-execution-counts]
        WARN[detecting-performance-warnings]
        COMP[tracing-compilation-events]
        INL[tracing-inlining-decisions]
        DEOPT[detecting-deoptimizations]
        DOCS[fetching-truffle-documentation]
    end

    Orch -->|"No baseline"| P1
    Orch -->|"New tier"| P2
    Orch -->|"Pending theories"| P3

    P2 -->|"Step B"| CPU
    P2 -->|"Step C"| MEM
    P2 -->|"Step D"| IGV
    P2 -->|"Low confidence<br>findings"| Deep

    P3 -->|"All failed<br>at tier"| P2

    Deep --> CPU
    Deep --> MEM
    Deep --> IGV
    Deep --> EXEC
    Deep --> WARN
    Deep --> COMP
    Deep --> INL
    Deep --> DEOPT

    P1 -.->|"uses"| DOCS
```

### Call Hierarchy Table

| Caller | Calls | Mechanism | When |
|--------|-------|-----------|------|
| `optimization-workflow-orchestrator` | `establishing-benchmark-baseline` | Direct invocation (skill) | No baseline exists |
| `optimization-workflow-orchestrator` | `broad-performance-investigation` | Direct invocation (skill) | Starting new severity tier |
| `optimization-workflow-orchestrator` | `implementing-performance-fixes` | Direct invocation (skill) | Pending theories exist |
| `broad-performance-investigation` | `profiling-with-cpu-sampler` | Tool skill invocation | Step B (mandatory) |
| `broad-performance-investigation` | `profiling-memory-allocations` | Tool skill invocation | Step C (mandatory) |
| `broad-performance-investigation` | `compiler-graph-analyst` | Subagent spawn | Step D (mandatory) |
| `broad-performance-investigation` | `deep-performance-investigation` | Skill invocation | Low-confidence findings |
| `deep-performance-investigation` | All 8 tool skills | Tool skill invocation | Targeted profiling |
| `implementing-performance-fixes` | `broad-performance-investigation` | Triggers next phase | All theories at tier failed |

### Key Architectural Properties

- **14 skills total**: 1 orchestrator + 3 phase skills + 1 utility skill + 8 tool skills + 1 docs skill
- **All skills are model-invoked** (Claude selects based on context, not user commands)
- **State managed via files**: `BENCHMARK_BASELINE.md`, `PERFORMANCE_THEORIES_{TIER}.md`
- **4 theory files** (one per severity tier, never deleted)
- **File-based state machine**: Orchestrator checks file existence and content to determine next action
