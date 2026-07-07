import math
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

from .models import (
    BenchmarkComparison,
    BenchmarkName,
    BenchmarkResult,
    GeomeanSpeedupResult,
)
from .runner import execute_benchmark

mcp = FastMCP(
    "awfy",
    instructions="This server runs Are-We-Fast-Yet benchmarks to get a reasonable execution time for a benchmark on the current machine.",
)


@mcp.tool
def run_python_benchmark(
    name: Annotated[
        BenchmarkName,
        Field(description="Name of the Are-We-Fast-Yet benchmark to run."),
    ],
    inner_iterations: Annotated[
        int,
        Field(
            default=100,
            ge=1,
            description="Number of times the benchmark is executed and verified within each outer iteration.",
        ),
    ] = 100,
    outer_iterations: Annotated[
        int,
        Field(
            default=20,
            ge=1,
            description="Number of independently timed runs. Each outer iteration produces one timing sample.",
        ),
    ] = 20,
) -> BenchmarkResult:
    """Run an Are-We-Fast-Yet benchmark to get a reasonable execution time on the current machine.

    Executes the specified benchmark with configurable iteration counts.
    Inner iterations repeat the benchmark within a single timed run,
    while outer iterations produce independent timing samples used to
    compute min, max, sum, and average runtime in microseconds.
    """
    return execute_benchmark(name, inner_iterations, outer_iterations)


@mcp.tool
def compute_geomean_speedup(
    baseline_times_us: Annotated[
        list[float],
        Field(
            description="Average runtimes in microseconds from the baseline run, one per benchmark.",
        ),
    ],
    new_times_us: Annotated[
        list[float],
        Field(
            description="Average runtimes in microseconds from the new run, one per benchmark. Must be in the same order as baseline_times_us.",
        ),
    ],
    benchmark_names: Annotated[
        list[str],
        Field(
            description="Names of the benchmarks corresponding to each timing pair.",
        ),
    ],
    speedup_threshold: Annotated[
        float,
        Field(
            default=1.03,
            gt=0,
            description="Minimum geometric mean of speedup ratios to consider the change 'faster'. Default is 1.03 (3% improvement).",
        ),
    ] = 1.03
) -> GeomeanSpeedupResult:
    """Compute the geometric mean of speedup ratios across multiple benchmarks.

    For each benchmark, the speedup ratio is baseline_time / new_time.
    A ratio > 1 means the new version is faster.
    The geometric mean summarizes the overall speedup across all benchmarks.

    The change is considered "faster" if the geometric mean exceeds the
    speedup_threshold.
    """
    if not (len(baseline_times_us) == len(new_times_us) == len(benchmark_names)):
        raise ValueError(
            "baseline_times_us, new_times_us, and benchmark_names must have the same length"
        )
    if len(baseline_times_us) == 0:
        raise ValueError("At least one benchmark comparison is required")

    comparisons: list[BenchmarkComparison] = []
    for name, baseline, new in zip(benchmark_names, baseline_times_us, new_times_us):
        if baseline <= 0 or new <= 0:
            raise ValueError(f"Times must be positive, got baseline={baseline}, new={new} for {name}")
        ratio = baseline / new
        comparisons.append(
            BenchmarkComparison(
                benchmark_name=name,
                baseline_time_us=baseline,
                new_time_us=new,
                speedup_ratio=ratio,
            )
        )

    log_sum = sum(math.log(c.speedup_ratio) for c in comparisons)
    geomean = math.exp(log_sum / len(comparisons))

    return GeomeanSpeedupResult(
        comparisons=comparisons,
        geomean_speedup=geomean,
        is_faster=geomean > speedup_threshold
    )
