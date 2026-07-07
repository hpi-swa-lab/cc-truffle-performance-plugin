# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mcp-awfy is an MCP (Model Context Protocol) server that exposes the [Are-We-Fast-Yet](https://github.com/smarr/are-we-fast-yet) benchmark suite as tools. It allows MCP-compatible clients (like Claude) to run 14 classic performance benchmarks and get timing statistics.

## Build & Run

This project uses **uv** as its package manager and build system. Python 3.12+ required.

```bash
uv sync              # Install dependencies
uv build             # Build the package
mcp-awfy             # Run the MCP server (entry point defined in pyproject.toml)
```

There are no tests or linting configured.

## Architecture

The server exposes a single MCP tool `run_python_benchmark` via FastMCP:

```
__init__.py (entry point: main())
  → server.py (FastMCP "awfy" instance, defines run_python_benchmark tool)
    → runner.py (execute_benchmark: timing loop using perf_counter_ns)
      → awfy/ (benchmark implementations)
```

**Key flow**: `run_python_benchmark(name, inner_iterations, outer_iterations)` → instantiates benchmark class from `BENCHMARKS` registry → runs outer loop (timed) × inner loop (with verification) → returns `BenchmarkResult` with min/max/sum/avg runtime in microseconds.

### Core modules

- `models.py` — `BenchmarkName` (Literal of 14 names) and `BenchmarkResult` (Pydantic model with timing stats)
- `runner.py` — Orchestrates benchmark execution, measures time in nanoseconds, converts to microseconds, verifies correctness
- `awfy/__init__.py` — `BENCHMARKS` dict mapping name strings to benchmark classes
- `awfy/benchmark.py` — Abstract `Benchmark` base class with `benchmark()`, `verify_result()`, and `inner_benchmark_loop()` methods

### Benchmarks

All 14 benchmarks (Bounce, CD, DeltaBlue, Havlak, Json, List, Mandelbrot, NBody, Permute, Queens, Richards, Sieve, Storage, Towers) inherit from `Benchmark` and implement `benchmark()` + `verify_result()` with hardcoded expected results. Benchmarks use custom data structures from `awfy/som/` (Vector, Set, Dictionary, Random) rather than Python stdlib equivalents.

### Adding a new benchmark

1. Create `src/mcp_awfy/awfy/<name>.py` implementing `Benchmark` with `benchmark()` and `verify_result()`
2. Register it in `awfy/__init__.py` in the `BENCHMARKS` dict
3. Add the name to the `BenchmarkName` Literal in `models.py`
