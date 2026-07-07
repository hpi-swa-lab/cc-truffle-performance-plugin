# mcp-awfy

An MCP server that exposes the [Are-We-Fast-Yet](https://github.com/smarr/are-we-fast-yet) benchmark suite as a tool. It allows MCP-compatible clients to run performance benchmarks and get timing statistics.

## Installation

Requires Python 3.12+.

```bash
uv sync
```

## Usage

Run the MCP server:

```bash
mcp-awfy
```

### Tool: `run_python_benchmark`

Runs a benchmark and returns timing statistics (min, max, sum, avg runtime in microseconds).

**Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `name` | `BenchmarkName` | — | Benchmark to run |
| `inner_iterations` | `int` | 100 | Executions within each timed run |
| `outer_iterations` | `int` | 20 | Number of independently timed runs |

**Available benchmarks:** Bounce, CD, DeltaBlue, Havlak, Json, List, Mandelbrot, NBody, Permute, Queens, Richards, Sieve, Storage, Towers

## Client Configuration

### Claude Code

```bash
claude mcp add awfy -- uv run --directory /path/to/mcp-awfy mcp-awfy
```

### OpenCode

Add to `opencode.json`:

```json
{
  "mcp": {
    "awfy": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-awfy", "mcp-awfy"]
    }
  }
}
```

### GitHub Copilot (VS Code)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "awfy": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-awfy", "mcp-awfy"]
    }
  }
}
```

### OpenAI Codex

```bash
codex --mcp-config codex-mcp.json
```

With `codex-mcp.json`:

```json
{
  "mcpServers": {
    "awfy": {
      "command": "uv",
      "args": ["run", "--directory", "/path/to/mcp-awfy", "mcp-awfy"]
    }
  }
}
```

## License

Benchmark implementations are based on the [SOM class library](https://github.com/smarr/are-we-fast-yet) — see source files for license details.
