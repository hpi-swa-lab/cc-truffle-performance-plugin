# Truffle Performance Plugin

A Claude Code plugin for analyzing and optimizing GraalVM Truffle performance. This plugin provides specialized skills for profiling, tracing, and diagnosing performance issues in Truffle language implementations.

Thesis: [Enhancing AI Coding Agents for TruffleDSL
Performance Optimization](https://antonykamp.de/masters-thesis.pdf)

## Features

This plugin includes expert-level skills for:

- **Analyzing Compiler Graphs** - Understanding IGV dumps and compilation patterns
- **Detecting Deoptimizations** - Identifying and fixing runtime deoptimizations
- **Detecting Performance Warnings** - Spotting compiler and runtime warnings
- **Establishing Benchmark Baselines** - Creating reliable performance benchmarks
- **Fetching Truffle Documentation** - Accessing up-to-date Truffle API docs
- **Optimization Workflow Orchestrator** - Optimization loop: baseline, analyze & plan, implement & validate, refresh baseline, update lessons learned, clean up, commit
- **Profiling Memory Allocations** - Tracking allocation patterns and memory usage
- **Profiling with CPU Sampler** - Collecting and analyzing CPU profiles
- **Tracing Compilation Events** - Monitoring JIT compilation activity
- **Tracing Execution Counts** - Measuring node execution frequencies
- **Tracing Inlining Decisions** - Understanding inlining behavior

## Installation

### Prerequisites

- Claude Code installed and authenticated ([installation guide](https://code.claude.com/docs/en/quickstart#step-1-install-claude-code))
- Claude Code version 1.0.33 or later (run `claude --version` to check)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) installed (required for the MCP AWFY benchmark server)

### Install the Plugin

1. **Clone or download this repository** to your local machine

2. **Load the plugin** when starting Claude Code:
   ```bash
   claude --plugin-dir /path/to/cc-truffle-performance-plugin
   ```

3. **Verify installation** by running `/help` in Claude Code - you should see the plugin's commands listed

## Usage

Once installed, Claude will automatically use the appropriate skills based on your Truffle performance analysis needs. The skills are model-invoked, meaning Claude selects and applies them contextually when analyzing your code.

### Example Scenarios

- Ask Claude to analyze compiler graphs from IGV dumps
- Request help debugging deoptimizations in your Truffle language
- Get assistance profiling memory allocations
- Have Claude generate performance reports for your benchmarks

## Plugin Structure

```
cc-truffle-performance-plugin/
├── .claude-plugin/
│   └── plugin.json         # Plugin manifest
├── agents/                 # Sub-agent definitions
│   ├── baseline-establisher.md
│   ├── compiler-graph-analyst.md
│   └── hypothesis-validator.md
└── skills/                 # Skill definitions
    ├── detecting-deoptimizations/
    ├── detecting-performance-warnings/
    ├── fetching-truffle-documentation/
    ├── optimization-workflow-orchestrator/
    ├── profiling-memory-allocations/
    ├── profiling-with-cpu-sampler/
    ├── tracing-compilation-events/
    ├── tracing-execution-counts/
    └── tracing-inlining-decisions/
```

## Development

To modify or extend this plugin:

1. Edit the skill definitions in the `skills/` directory
2. Update the plugin manifest in `.claude-plugin/plugin.json` if needed
3. Restart Claude Code to pick up changes
