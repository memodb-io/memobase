#!/usr/bin/env python3
"""
P95 Search Time Latency Demo Program

This program simulates search operations and computes the 95th percentile (p95) latency.
It includes timing measurements, data generation, and statistical analysis.
"""

import time
import random
import numpy as np
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json


class LatencyAnalyzer:
    """Analyzes search latencies and computes statistics."""

    def __init__(self, results: list[float]):
        self.results: List[float] = results

    def get_latencies(self) -> List[float]:
        """Extract latency values from all results."""
        return self.results

    def compute_statistics(self) -> Dict[str, float]:
        """Compute comprehensive latency statistics."""
        if not self.results:
            return {}

        latencies = self.get_latencies()

        return {
            "count": len(latencies),
            "min_ms": min(latencies),
            "max_ms": max(latencies),
            "mean_ms": statistics.mean(latencies),
            "median_ms": statistics.median(latencies),
            "p50_ms": np.percentile(latencies, 50),
            "p90_ms": np.percentile(latencies, 90),
            "p95_ms": np.percentile(latencies, 95),  # The main metric
            "p99_ms": np.percentile(latencies, 99),
            "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }

    def print_statistics(self):
        """Print formatted statistics to console."""
        stats = self.compute_statistics()
        if not stats:
            print("No results to analyze.")
            return

        print("\n" + "=" * 50)
        print("SEARCH LATENCY ANALYSIS")
        print("=" * 50)
        print(f"Total searches: {stats['count']}")
        print(f"Min latency: {stats['min_ms']:.2f} ms")
        print(f"Max latency: {stats['max_ms']:.2f} ms")
        print(f"Mean latency: {stats['mean_ms']:.2f} ms")
        print(f"Median latency: {stats['median_ms']:.2f} ms")
        print("-" * 30)
        print("PERCENTILES:")
        print(f"P50 (median): {stats['p50_ms']:.2f} ms")
        print(f"P90: {stats['p90_ms']:.2f} ms")
        print(f"P95: {stats['p95_ms']:.2f} ms ⭐")  # Highlighted
        print(f"P99: {stats['p99_ms']:.2f} ms")
        print("-" * 30)
        print(f"Standard deviation: {stats['std_dev_ms']:.2f} ms")
        print("=" * 50)


with open("./fixture/memobase/results_0710_3000.json", "r") as f:
    data = json.load(f)
latencies = []


for k in data.keys():
    for d in data[k]:
        latencies.append(d["speaker_1_memory_time"] * 1000)
        latencies.append(d["speaker_2_memory_time"] * 1000)


analyzer = LatencyAnalyzer(latencies)
analyzer.print_statistics()
