from typing import Literal

from pydantic import BaseModel

BenchmarkName = Literal[
    "bounce",
    "cd",
    "deltablue",
    "havlak",
    "json",
    "list",
    "mandelbrot",
    "nbody",
    "permute",
    "queens",
    "richards",
    "sieve",
    "storage",
    "towers",
]


class BenchmarkResult(BaseModel):
    benchmark_name: str
    inner_iterations: int
    outer_iterations: int
    min_runtime_us: int
    max_runtime_us: int
    sum_runtime_us: int
    avg_runtime_us: float


class BenchmarkComparison(BaseModel):
    benchmark_name: str
    baseline_time_us: float
    new_time_us: float
    speedup_ratio: float


class GeomeanSpeedupResult(BaseModel):
    comparisons: list[BenchmarkComparison]
    geomean_speedup: float
    is_faster: bool
