# User Manual

This plugin gives you three levels of control for optimizing Truffle language performance: use individual tool skills for targeted analysis, invoke sub-agents for structured multi-step tasks, or let the orchestrator run the full optimization loop autonomously.

## Prerequisites

- Claude Code 1.0.33+ with the plugin loaded:
  ```bash
  claude --plugin-dir /path/to/cc-truffle-performance-plugin
  ```
- A built Truffle language with a working launcher binary (e.g., `./sl`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (required for the AWFY benchmark MCP server)

## Quick Start

**Hands-off optimization** -- ask Claude to optimize your language and the orchestrator takes over:

> "Optimize performance of my Truffle language using /optimization-workflow-orchestrator"

**Targeted investigation** -- ask for a specific analysis and Claude picks the right tool skill:

> "Profile CPU usage of my fibonacci benchmark"
>
> "Check if there are deoptimizations when running `./sl benchmarks/fib.sl`"

## Level 1: Tool Skills (Most Control)

Tool skills run individual Truffle/GraalVM profiling tools. Use these when you know exactly what you want to measure. Claude selects the appropriate skill based on your request.

| Skill | What it does | When to use it |
|---|---|---|
| **profiling-with-cpu-sampler** | Time-based sampling showing where execution time is spent, with compilation tier breakdown (T0/T1/T2) | First step to find hot functions |
| **profiling-memory-allocations** | Tracks guest-language memory allocations by site and type | Find allocation-heavy hot loops |
| **tracing-execution-counts** | Counts exact execution frequencies, shows interpreted vs compiled split | Verify functions compile (>95% compiled) |
| **tracing-compilation-events** | Logs every JIT compilation event with timing, tier, and success/failure | Diagnose compilation failures or recompilation cycles |
| **tracing-inlining-decisions** | Shows which calls get inlined and why others don't | Verify critical calls are inlined |
| **detecting-deoptimizations** | Traces fallbacks from compiled code to interpreter | Find compilation instability (goal: zero in steady-state) |
| **detecting-performance-warnings** | Identifies virtual calls, non-constant stores, and other optimization barriers | Eliminate compilation warnings (traditional Truffle DSL only) |
| **fetching-truffle-documentation** | Retrieves official GraalVM/Truffle docs | Look up APIs, compiler flags, or optimization techniques |

You can call a skill directly with `/profiling-with-cpu-sampler` or ask a more general question and Claude will pick the right skill.

### Example prompts

- "Use the CPU sampler to profile `./sl benchmarks/sort.sl`"
- "Trace compilation events for my fibonacci benchmark"
- "Are there any deoptimizations when running `./sl benchmarks/loop.sl`?"
- "Check for performance warnings in my language"
- "How many times does each function execute in my benchmark?"

## Level 2: Sub-Agents (Structured Tasks)

Sub-agents handle multi-step tasks autonomously. They are more capable than individual tool skills but give you control over which phase of the optimization process to run.

| Sub-agent | What it does | Input | Output |
|---|---|---|---|
| **baseline-establisher** | Runs all benchmarks and collects timing data | -- | `BENCHMARK_BASELINE.md` |
| **hypothesis-validator** | Validates a performance hypothesis by selecting and running the right profiling tools | Hypothesis via prompt (inline text or reference to `HYPOTHESES.md`) | Updated `HYPOTHESES.md` with confirmed/rejected status |
| **compiler-graph-analyst** | Dumps and analyzes Graal compiler graphs (BGV) for specific issues | Hypothesis via prompt (inline text or reference to `HYPOTHESES.md`) | Updated `HYPOTHESES.md` with findings |

You can invoke a sub-agent directly with calling `Task(subagent_type="baseline-establisher")` or ask a question that implies a structured investigation and Claude will pick the right sub-agent.

### Example prompts

- "Establish a benchmark baseline for my language"
- "Validate whether megamorphic dispatch is causing slowdowns in the sort benchmark"
- "Analyze compiler graphs to check if escape analysis is failing for my object allocations"

## Level 3: Orchestrator (Fully Autonomous)

The orchestrator runs a complete optimization loop: baseline, explore, hypothesize, validate, plan, implement, benchmark, and commit. Use this when you want Claude to find and fix performance issues end-to-end.

### Example prompts

- "/optimization-workflow-orchestrator"
- "Find and fix performance bottlenecks in my language implementation"

### The optimization loop

```
Step 0: Baseline  (once)
    |
+-- Step 1: Explore (find hypotheses)
|   Step 2: Validate hypothesis
|   Step 3: Plan implementation
|   Step 4: Implement changes
|   Step 5: Validate benchmarks
|   slower? ---> retry or back to Step 1
|   faster? |
|   Step 6: Refresh baseline
|   Step 7: Update lessons learned
|   Step 8: Clean up
|   Step 9: Commit --> STOP
```

### State files

The orchestrator maintains these files across iterations:

| File | Purpose | Persists across iterations? |
|---|---|---|
| `BENCHMARK_BASELINE.md` | Benchmark commands, timing data, performance expectations | Yes (updated on success) |
| `LESSONS_LEARNED.md` | What was tried, what worked, what failed | Yes |
| `HYPOTHESES.md` | Current hypotheses and validation results | No (per iteration) |
| `IMPLEMENTATION_PLAN.md` | Current implementation plan | No (per iteration) |
| `tool-outputs/` | Profiling tool outputs | No (per iteration) |

### Acceptance criteria

A change is accepted as "faster" when:
- The geometric mean speedup across all benchmarks is >3%
- No individual benchmark regresses by more than 5%

### Resuming work

The orchestrator checks for existing `BENCHMARK_BASELINE.md` and `LESSONS_LEARNED.md` on startup, so it can continue from where a previous session left off.