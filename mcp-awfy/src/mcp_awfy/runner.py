from time import perf_counter_ns

from .awfy import BENCHMARKS
from .models import BenchmarkName, BenchmarkResult


def execute_benchmark(
    name: BenchmarkName,
    inner_iterations: int = 1,
    outer_iterations: int = 1,
) -> BenchmarkResult:
    if name not in BENCHMARKS:
        raise ValueError(f"Unknown benchmark: {name}")
    bench = BENCHMARKS[name]()
    runtimes: list[int] = []

    for _ in range(outer_iterations):
        start = perf_counter_ns()
        success = bench.inner_benchmark_loop(inner_iterations)
        end = perf_counter_ns()
        if not success:
            raise RuntimeError(f"Benchmark {name} failed verification")
        runtimes.append((end - start) // 1000)

    return BenchmarkResult(
        benchmark_name=name,
        inner_iterations=inner_iterations,
        outer_iterations=outer_iterations,
        min_runtime_us=min(runtimes),
        max_runtime_us=max(runtimes),
        sum_runtime_us=sum(runtimes),
        avg_runtime_us=sum(runtimes) / len(runtimes),
    )
