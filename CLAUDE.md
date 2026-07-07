# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

This plugin was developed as part of a master's thesis: https://antonykamp.de/masterthesis.pdf

## Overview

This is a Claude Code plugin for analyzing and optimizing GraalVM Truffle language performance. It provides a suite of specialized skills for profiling, tracing, and diagnosing performance issues in Truffle language implementations.

## Plugin Structure

Skills are organized in the `skills/` directory. Each skill is a self-contained directory with:
- `SKILL.md` - Main skill definition with frontmatter metadata (name, description)
- Additional `.md` files - Supporting documentation (WORKFLOW.md, PATTERNS.md, etc.)

Sub-agents are defined in the `agents/` directory as standalone markdown files with YAML frontmatter (name, description, model, optional tools restriction) and a markdown body containing the agent's full instructions. The orchestrator references them by plugin-prefixed name (e.g., `cc-truffle-performance-plugin:performance-explorer`).

The plugin manifest is located at `.claude-plugin/plugin.json`.

## Performance Optimization Workflow

The plugin implements an optimization loop managed by the `optimization-workflow-orchestrator` skill:

```text
Step 0: Baseline  (once)
    ↓
┌─ Step 1: Explore ←───────────────┐
│  Step 2: Validate hypothesis      │
│  Step 3: Plan                     │
│  Step 4: Implement                │
│  Step 5: Validate benchmarks      │
│  slower? ─────────────────────────┘
│  faster? ↓
│  Step 6: Refresh baseline
│  Step 7: Update lessons learned
│  Step 8: Clean up
│  Step 9: Commit → STOP
```

**Step 0 — Baseline**: If `BENCHMARK_BASELINE.md` doesn't exist, run the `baseline-establisher` sub-agent to create benchmarks and collect timing data.

**Step 1 — Explore**: Spawn the `performance-explorer` sub-agent to read the baseline and lessons learned, explore the language implementation, and write 2-3 ranked hypotheses to `HYPOTHESES.md`.

**Step 2 — Validate hypothesis**: Validate the most critical unverified hypothesis. The orchestrator reads `HYPOTHESES.md` to determine the validation approach, then spawns the appropriate sub-agent (`hypothesis-validator` or `compiler-graph-analyst`) which reads `HYPOTHESES.md` itself. Both sub-agents update `HYPOTHESES.md` with results. Only if 100% rejected, try the next hypothesis; if partially confirmed, proceed to planning.

**Step 3 — Plan**: Spawn the `optimization-planner` sub-agent to read the confirmed hypothesis and design an implementation plan. The sub-agent writes the plan to `IMPLEMENTATION_PLAN.md`. The orchestrator reviews the plan and may resume the sub-agent with feedback (max three review rounds).

**Step 4 — Implement**: The `plan-implementer` sub-agent implements the plan from `IMPLEMENTATION_PLAN.md`, builds, runs tests, and runs the verification benchmarks for quick verification.

**Step 5 — Validate benchmarks**: Rerun every language benchmark (one at a time, not in parallel) using the commands and iteration counts from `BENCHMARK_BASELINE.md`. A change is "faster" if the geometric mean of speedup ratios across all benchmarks is >3% and no individual benchmark regresses by more than 5%. Faster → continue to Step 6. Slower → improve the implementation (max three retries) or restart from Step 1.

**Step 6 — Refresh baseline**: Replace the language results table in `BENCHMARK_BASELINE.md` with the new timing data. Keep the reference results (AWFY Python) unchanged.

**Step 7 — Update lessons learned**: Read `HYPOTHESES.md` for hypothesis results. Record what was tried and learned to `LESSONS_LEARNED.md`.

**Step 8 — Clean up**: Remove all intermediate artifacts (`tool-outputs/`, `IMPLEMENTATION_PLAN.md`) so the next iteration starts fresh. `BENCHMARK_BASELINE.md` and `LESSONS_LEARNED.md` carry over.

**Step 9 — Commit**: Commit the changes with a concise message describing what was optimized and the benchmark delta.

## Skills

In skill references, `<launcher>` refers to the target language's launcher binary (e.g., `./sl`, `./my-language`).

**Workflow orchestration**:
- `optimization-workflow-orchestrator` - Orchestrates the optimization loop above

**Sub-agents** (spawned as separate agent processes, defined in `agents/`):
- `baseline-establisher` - Runs all benchmarks and creates `BENCHMARK_BASELINE.md`
- `compiler-graph-analyst` - Analyzes compiler graphs for specific issues across benchmarks; receives hypothesis via prompt and updates `HYPOTHESES.md` with findings
- `hypothesis-validator` - Validates a performance hypothesis by running profiling tools; receives hypothesis via prompt and updates `HYPOTHESES.md` with confirmed/rejected status
- `performance-explorer` - Explores the language implementation for performance issues and writes ranked hypotheses to `HYPOTHESES.md`
- `optimization-planner` - Designs an implementation plan for a confirmed performance hypothesis and writes it to `IMPLEMENTATION_PLAN.md`
- `plan-implementer` - Implements an optimization plan, builds the project, runs tests, and reports results

**Tool skills** (invoke Truffle/Graal profiling tools):

- `profiling-with-cpu-sampler` - Time-based profiling, tier breakdown (T0/T1/T2)
- `profiling-memory-allocations` - Allocation tracking
- `tracing-execution-counts` - Execution frequency measurement
- `tracing-compilation-events` - JIT compilation monitoring
- `tracing-inlining-decisions` - Inlining behavior analysis
- `detecting-deoptimizations` - Deoptimization tracking (goal: zero in steady-state)
- `detecting-performance-warnings` - Finds optimization barriers (virtual calls, type checks)

**Utility**:
- `fetching-truffle-documentation` - Access Truffle API docs

## Key Concepts

### Fermi Verification
Every tool skill requires "Fermi verification" - pre-calculate expected results before running tools, then validate actual results are within expectations. This prevents silent tool failures and garbage data.

### Tool Output Storage
Tools save outputs to `tool-outputs/` directory with naming pattern: `tool-outputs/{tool-name}-{benchmark}.txt`

### State Files

Each state file is owned by the sub-agent(s) that write it. The orchestrator only writes `LESSONS_LEARNED.md` (cross-iteration state).

- `BENCHMARK_BASELINE.md` - Benchmark descriptions, timing data, performance expectations. Written by `baseline-establisher`, refreshed by orchestrator (Step 6).
- `HYPOTHESES.md` - Performance hypotheses and validation results. Written by `performance-explorer`, updated by `hypothesis-validator` and `compiler-graph-analyst`.
- `IMPLEMENTATION_PLAN.md` - Optimization plan for the current iteration. Written by `optimization-planner`.
- `LESSONS_LEARNED.md` - Accumulated findings from past iterations: what was tried, what failed, and what approaches are ruled out. Written by the orchestrator.

## Common Patterns

### Truffle Performance Issues
The skills are designed to detect and fix common Truffle performance anti-patterns (see PATTERNS.md in individual tool skill directories):

**Control Flow Patterns:**
- Megamorphic dispatch (>3 receiver types)
- Polymorphic cache instability
- Implementation-induced branches
- Guard proliferation

**Truffle DSL Patterns:**
- Missing primitive specializations (boxing overhead)
- Uncached library usage
- Hot path boundary calls
- Frame slot type instability
- Missing @Cached for lookups

### Compilation Tiers
- T0 (Interpreter) - Should be <10% for hot functions
- T1 (First-tier compiled) - Transitional
- T2 (Fully optimized) - Should be >80% for hot functions

## Testing Plugin Changes

To test changes to skills:
1. Edit skill definitions in `skills/` directory
2. Update `.claude-plugin/plugin.json` if needed
3. Restart Claude Code: `claude --plugin-dir /path/to/cc-truffle-performance-plugin`
4. Verify with `/help` command

## Skill Invocation

Skills are model-invoked (Claude selects based on context). Sub-agents (`baseline-establisher`, `compiler-graph-analyst`, `hypothesis-validator`, `performance-explorer`, `optimization-planner`, `plan-implementer`) are spawned as separate agent processes with their own context. Sub-agents communicate results via files. The `hypothesis-validator` agent reads tool skill SKILL.md files at runtime to understand how to run profiling commands. Tool skills run in the main conversation and provide Truffle/Graal profiling domain knowledge.
