# Architecture Documentation: `slim-process` Branch

## 1. Process Run with the Orchestrator

The `slim-process` branch implements a **simplified optimization loop** without severity tiers. The orchestrator runs steps sequentially, looping back on failure.

### Workflow Overview

```mermaid
flowchart TD
    Start([User: Optimize performance]) --> Orch

    subgraph "Skill: optimization-workflow-orchestrator"
        Orch[Orchestrator] --> Step0{BENCHMARK_BASELINE.md<br>exists?}
        Step0 -->|Yes| Step1[Step 1: Explore<br>Find hypotheses]
        Step1 --> Step2[Step 2: Validate hypothesis]
        Step2 --> Step2_check{Hypothesis<br>confirmed?}
        Step2_check -->|No| Step2_next{More<br>hypotheses?}
        Step2_next -->|Yes| Step2
        Step2_next -->|No| Step1
        Step2_check -->|Yes| Step3[Step 3: Plan<br>Write IMPLEMENTATION_PLAN.md]
        Step3 --> Step4[Step 4: Implement<br>Runs tests & benchmarks]
        Step4 --> Step5{Step 5: Benchmark<br>result?}
        Step5 -->|Faster| Step6[Step 6: Refresh baseline]
        Step6 --> Step7[Step 7: Update lessons learned]
        Step7 --> Step8[Step 8: Clean up]
        Step8 --> Step9[Step 9: Commit]
        Step9 --> Stop([STOP])
        Step5 -->|Slower| Retry{Can improve?}
        Retry -->|Yes| Step4
    end

    subgraph "Agent: baseline-establisher  ·  model: haiku"
        BL_agent[Step 0: Run all benchmarks<br>Write BENCHMARK_BASELINE.md]
    end

    subgraph "Agent: Explore sub-agent"
        EX_agent[Step 1: Explore code<br>Write hypotheses]
    end

    subgraph "Agent: hypothesis-validator  ·  model: sonnet"
        HV_agent[Step 2: Validate hypothesis<br>Reads tool skill files, runs profiling]
    end

    subgraph "Agent: compiler-graph-analyst  ·  model: sonnet"
        CGA_agent[Step 2: Analyze compiler graphs<br>for IR-level validation]
    end

    subgraph "Agent: Plan sub-agent  ·  model: sonnet"
        PL_agent[Step 3: Design implementation<br>Write IMPLEMENTATION_PLAN.md]
    end

    Step0 -->|No| BL_agent
    BL_agent --> Step0
    Step1 --> EX_agent
    EX_agent --> Step2
    Step2 -->|profiling| HV_agent
    Step2 -->|compiler graphs| CGA_agent
    HV_agent --> Step2_check
    CGA_agent --> Step2_check
    Step3 --> PL_agent
    PL_agent --> Step4
    Retry -->|No| Step1
```

### Step Details

| Step | Actor | Input | Output |
|------|-------|-------|--------|
| 0 | `baseline-establisher` subagent (Haiku) | Project code | `BENCHMARK_BASELINE.md` |
| 1 | Explore sub-agent | Language code + baseline + lessons | `HYPOTHESES.md` |
| 2 | `hypothesis-validator` subagent (Sonnet) or `compiler-graph-analyst` subagent | `HYPOTHESES.md` | Updated `HYPOTHESES.md` (confirmed/rejected) |
| 3 | Plan sub-agent (Sonnet) | Confirmed hypothesis + baseline | `IMPLEMENTATION_PLAN.md` |
| 4 | General-purpose sub-agent (Sonnet) | `IMPLEMENTATION_PLAN.md` | Code changes, benchmark results |
| 5-9 | Orchestrator (main agent) | Results | Validate, refresh baseline, lessons, clean up, commit |

---

## 2. How AI Context Is Used

The `slim-process` branch uses a **streamlined context system** with fewer files. Each step of the optimization loop is dispatched by the orchestrator to a purpose-built sub-agent. All sub-agents run in separate agent contexts.

```mermaid
flowchart TD
    subgraph "Plugin Manifest"
        PLUGIN[.claude-plugin/plugin.json<br>- Plugin name & version<br>- Triggers skill discovery]
    end

    subgraph "Skill Context - loaded into main agent"
        ORCH[optimization-workflow-orchestrator/SKILL.md<br>- 10-step linear loop<br>- Dispatches sub-agents per step]
        TOOLS[Tool skills SKILL.md<br>- Fermi verification<br>- Tool options & output format]
        SUPPORT[Supporting .md files<br>- PATTERNS.md, QUERIES.md,<br>  DUMPING.md]
    end

    subgraph "Agent Context - spawned as separate process"
        AGENT1[agents/baseline-establisher.md<br>- model: haiku<br>- Benchmark running procedure]
        AGENT2[agents/compiler-graph-analyst.md<br>- model: sonnet<br>- Compiler graph analysis procedure]
        AGENT3[agents/hypothesis-validator.md<br>- model: sonnet<br>- Reads tool skill files at runtime<br>- Runs profiling commands directly]
    end

    subgraph "Runtime State Files - read/written by agents"
        BL[BENCHMARK_BASELINE.md]
        ANALYSIS[IMPLEMENTATION_PLAN.md<br>- Implementation plan<br>- Verification benchmarks]
        HYPO[HYPOTHESES.md<br>- Ranked hypotheses<br>- Validation results]
        TOOLOUT[tool-outputs/*.txt]
    end

    PLUGIN --> ORCH
    PLUGIN --> TOOLS
    TOOLS --> SUPPORT
    ORCH -->|spawns| AGENT1
    ORCH -->|spawns| AGENT2
    ORCH -->|spawns| AGENT3
    AGENT3 -->|reads at runtime| TOOLS
    ORCH --> BL
    ORCH --> ANALYSIS
    ORCH --> HYPO
    TOOLS --> TOOLOUT
```

### Context Layers

| Layer | File(s) | Loaded When | Purpose |
|-------|---------|------------|---------|
| Plugin | `plugin.json` | Plugin load via `--plugin-dir` | Skill and agent discovery |
| Skill | `skills/*/SKILL.md` + support files | When skill is model-invoked | Procedures, tool options, output format |
| Agent | `agents/*.md` | When subagent is spawned | Self-contained procedure for the subagent |
| Runtime | `BENCHMARK_BASELINE.md`, `IMPLEMENTATION_PLAN.md`, `HYPOTHESES.md` | During workflow execution | State tracking, data exchange between steps |

### Context Size Comparison

| Component | `main` | `slim-process` | Change |
|-----------|--------|----------------|--------|
| Orchestrator SKILL.md | 204 lines | ~100 lines | -51% |
| Phase/workflow skills | 3 skills (698 lines total) | Removed | -100% |
| Subagent definitions | None | 3 agents (baseline + compiler-graph + hypothesis-validator) | New |
| Tool skills | 8 skills (unchanged) | 8 skills (minor edits) | ~same |
| `deep-performance-investigation` | 1 skill (116 + 141 lines) | Removed | -100% |
| **Total plugin context** | **~2400 lines** | **~1100 lines** | **~-54%** |

---

## 3. Agent/Skill Call Hierarchy

```mermaid
flowchart TD
    User([User]) -->|Optimize performance| Orch

    subgraph "Orchestrator (Main Agent Context)"
        Orch[optimization-workflow-orchestrator<br>- 10-step linear loop<br>- Dispatches sub-agents per step]
    end

    subgraph "Subagents (Separate Agent Context)"
        SA1[baseline-establisher<br>SUBAGENT<br>model: haiku]
        SA_EX[Explore sub-agent<br>Task subagent_type: Explore]
        SA_HV[hypothesis-validator<br>SUBAGENT<br>model: sonnet]
        SA_CGA[compiler-graph-analyst<br>SUBAGENT<br>model: sonnet]
        SA_PL[Plan sub-agent<br>Task subagent_type: Plan<br>model: sonnet]
        SA_IMPL[General-purpose sub-agent<br>Task subagent_type: general-purpose<br>model: sonnet]
    end

    subgraph "Tool Skills (Read by hypothesis-validator at runtime)"
        CPU[profiling-with-cpu-sampler]
        MEM[profiling-memory-allocations]
        EXEC[tracing-execution-counts]
        WARN[detecting-performance-warnings]
        COMP[tracing-compilation-events]
        INL[tracing-inlining-decisions]
        DEOPT[detecting-deoptimizations]
        DOCS[fetching-truffle-documentation]
    end

    Orch -->|"Step 0<br>(spawns subagent)"| SA1
    Orch -->|"Step 1<br>(spawns Explore)"| SA_EX
    Orch -->|"Step 2<br>(spawns subagent)"| SA_HV
    Orch -->|"Step 2<br>(spawns subagent, if needed)"| SA_CGA
    Orch -->|"Step 3<br>(spawns Plan)"| SA_PL
    Orch -->|"Step 4<br>(spawns subagent)"| SA_IMPL

    SA_HV -->|"reads SKILL.md, runs"| CPU
    SA_HV -->|"reads SKILL.md, runs"| MEM
    SA_HV -.->|"if needed"| EXEC
    SA_HV -.->|"if needed"| WARN
    SA_HV -.->|"if needed"| COMP
    SA_HV -.->|"if needed"| INL
    SA_HV -.->|"if needed"| DEOPT

    Orch -.->|"Step 4:<br>uses directly"| DOCS
```

### Call Hierarchy Table

| Caller | Calls | Mechanism | When |
|--------|-------|-----------|------|
| `optimization-workflow-orchestrator` | `baseline-establisher` | **Subagent spawn** (Haiku) | Step 0: no baseline exists |
| `optimization-workflow-orchestrator` | Explore sub-agent | **Task** (subagent_type: Explore) | Step 1: explore for hypotheses |
| `optimization-workflow-orchestrator` | `hypothesis-validator` | **Subagent spawn** (Sonnet) | Step 2: validate with profiling tools |
| `optimization-workflow-orchestrator` | `compiler-graph-analyst` | **Subagent spawn** (Sonnet) | Step 2: validate with compiler graphs (conditional) |
| `optimization-workflow-orchestrator` | Plan sub-agent | **Task** (subagent_type: Plan, Sonnet) | Step 3: design implementation plan |
| `optimization-workflow-orchestrator` | General-purpose sub-agent | **Task** (subagent_type: general-purpose, Sonnet) | Step 4: implement the plan |
| `optimization-workflow-orchestrator` | (self) | Direct execution | Steps 5-9: validate, refresh, lessons, clean up, commit |
| `hypothesis-validator` subagent | Tool skill SKILL.md files | **File read** (reads at runtime) | Understands tool options and runs commands |

### Key Architectural Properties

- **All sub-agents run in separate contexts**: no agent invokes skills or spawns other agents
- **3 agent definitions** in `agents/` directory (baseline-establisher, compiler-graph-analyst, hypothesis-validator)
- **hypothesis-validator reads tool skill files at runtime**: it reads SKILL.md to learn command format, then runs profiling commands directly
- **State managed via files**: `BENCHMARK_BASELINE.md`, `IMPLEMENTATION_PLAN.md`, `HYPOTHESES.md`
- **No severity tiers** — single iteration loop
- **10-step linear workflow**: each step dispatches one sub-agent or runs directly
