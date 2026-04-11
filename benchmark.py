#!/usr/bin/env python3
"""
Performance Benchmarking Suite
==============================

Measures and validates performance claims:
- Observation masking compression ratios
- Context window savings
- Persistence latency
- Memory overhead

Usage:
    python benchmark.py --all
    python benchmark.py --compression
    python benchmark.py --latency
"""

import time
import tempfile
import shutil
import statistics
from pathlib import Path
import argparse
import json

from recursive_agent import RecursiveAgent, ObservationMask, MemGPTLite
from advanced_features import AdvancedRecursiveAgent


class Benchmark:
    """Performance benchmarking suite"""

    def __init__(self):
        self.results = {}

    def benchmark_observation_masking(self, iterations=100):
        """Benchmark observation masking compression"""
        print("\n🎭 Benchmarking Observation Masking...")
        print("-" * 60)

        test_sizes = [100, 500, 1000, 5000, 10000, 50000]
        results = {}

        for size in test_sizes:
            ratios = []
            times = []

            for _ in range(iterations):
                content = "A" * size

                start = time.perf_counter()
                mask = ObservationMask.from_raw(content, "test")
                elapsed = time.perf_counter() - start

                placeholder = mask.to_placeholder()
                ratio = size / len(placeholder)

                ratios.append(ratio)
                times.append(elapsed)

            results[size] = {
                'avg_compression': statistics.mean(ratios),
                'max_compression': max(ratios),
                'avg_time_ms': statistics.mean(times) * 1000,
                'placeholder_size': len(placeholder)
            }

            print(f"  Size {size:>6}: {results[size]['avg_compression']:>6.1f}x "
                  f"compression in {results[size]['avg_time_ms']:.3f}ms")

        self.results['observation_masking'] = results
        return results

    def benchmark_context_savings(self):
        """Calculate context window savings"""
        print("\n📊 Calculating Context Window Savings...")
        print("-" * 60)

        # Simulate realistic conversation with large observations
        memory = MemGPTLite(tempfile.mkdtemp())

        # Add mix of short and long messages
        messages = [
            "Short message",  # 15 chars
            "A" * 5000,       # Large observation
            "Another short",  # 13 chars
            "B" * 3000,       # Another large
            "Final message",  # 13 chars
        ]

        raw_size = sum(len(m) for m in messages)

        for msg in messages:
            memory.write_to_ram(msg, "observation")

        masked_size = sum(len(e['content']) for e in memory.ram['conversation_buffer'])

        savings = raw_size - masked_size
        savings_pct = (savings / raw_size) * 100

        print(f"  Raw content size: {raw_size:,} chars")
        print(f"  Masked size: {masked_size:,} chars")
        print(f"  Savings: {savings:,} chars ({savings_pct:.1f}%)")

        shutil.rmtree(memory.storage_dir, ignore_errors=True)

        self.results['context_savings'] = {
            'raw_size': raw_size,
            'masked_size': masked_size,
            'savings': savings,
            'savings_pct': savings_pct
        }

        return savings_pct

    def benchmark_persistence_latency(self, iterations=10):
        """Measure session persistence latency"""
        print("\n💾 Benchmarking Persistence Latency...")
        print("-" * 60)

        temp_dir = tempfile.mkdtemp()
        latencies = []

        for i in range(iterations):
            agent = RecursiveAgent(f"BenchAgent{i}", temp_dir)

            # Add some data
            for j in range(5):
                agent.memory.write_to_ram(f"Message {j}", "user_input")

            start = time.perf_counter()
            agent.end_session()
            elapsed = time.perf_counter() - start

            latencies.append(elapsed * 1000)  # Convert to ms

        shutil.rmtree(temp_dir, ignore_errors=True)

        results = {
            'avg_ms': statistics.mean(latencies),
            'min_ms': min(latencies),
            'max_ms': max(latencies),
            'median_ms': statistics.median(latencies)
        }

        print(f"  Average: {results['avg_ms']:.2f}ms")
        print(f"  Min: {results['min_ms']:.2f}ms")
        print(f"  Max: {results['max_ms']:.2f}ms")
        print(f"  Median: {results['median_ms']:.2f}ms")

        self.results['persistence_latency'] = results
        return results

    def benchmark_memory_overhead(self):
        """Measure memory overhead per agent"""
        print("\n🧠 Measuring Memory Overhead...")
        print("-" * 60)

        import psutil
        import os

        process = psutil.Process(os.getpid())

        # Baseline
        baseline_mem = process.memory_info().rss / 1024 / 1024  # MB

        # Create multiple agents
        agents = []
        temp_dirs = []
        mem_usage = []

        for i in range(5):
            temp_dir = tempfile.mkdtemp()
            temp_dirs.append(temp_dir)
            agent = RecursiveAgent(f"Agent{i}", temp_dir)
            agents.append(agent)

            current_mem = process.memory_info().rss / 1024 / 1024
            overhead = current_mem - baseline_mem
            mem_usage.append(overhead)

            print(f"  Agent {i+1}: {overhead:.2f} MB overhead")

        # Cleanup
        for temp_dir in temp_dirs:
            shutil.rmtree(temp_dir, ignore_errors=True)

        avg_overhead = statistics.mean(mem_usage)
        print(f"\n  Average per agent: {avg_overhead:.2f} MB")

        self.results['memory_overhead'] = {
            'avg_mb': avg_overhead,
            'per_agent': mem_usage
        }

        return avg_overhead

    def benchmark_skill_loading(self):
        """Benchmark L1/L2/L3 skill loading"""
        print("\n🛠️  Benchmarking Skill Loading...")
        print("-" * 60)

        temp_dir = tempfile.mkdtemp()
        agent = RecursiveAgent("SkillBench", temp_dir)

        # Create skills
        for i in range(10):
            agent.skill_factory.create_skill(
                f"skill-{i}",
                f"Test skill {i}",
                f"# Skill {i}\nInstructions here\n" * 50
            )

        # Benchmark L1 (metadata)
        start = time.perf_counter()
        skills = agent.skill_factory.list_skills()
        l1_time = (time.perf_counter() - start) * 1000

        # Benchmark L2 (instructions)
        start = time.perf_counter()
        for skill in skills[:5]:
            agent.skill_factory.load_skill(skill['name'])
        l2_time = (time.perf_counter() - start) * 1000

        shutil.rmtree(temp_dir, ignore_errors=True)

        print(f"  L1 (metadata): {l1_time:.2f}ms for {len(skills)} skills")
        print(f"  L2 (instructions): {l2_time:.2f}ms for 5 skills")

        self.results['skill_loading'] = {
            'l1_ms': l1_time,
            'l2_ms': l2_time
        }

        return l1_time, l2_time

    def run_all(self):
        """Run all benchmarks"""
        print("="*60)
        print("RECURSIVE SELF-EVOLUTION - PERFORMANCE BENCHMARKS")
        print("="*60)

        self.benchmark_observation_masking()
        self.benchmark_context_savings()
        self.benchmark_persistence_latency()

        try:
            self.benchmark_memory_overhead()
        except ImportError:
            print("\n⚠️  psutil not installed, skipping memory benchmark")

        self.benchmark_skill_loading()

        # Summary
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)

        if 'observation_masking' in self.results:
            comp = self.results['observation_masking'][10000]['avg_compression']
            print(f"✅ Observation Masking: {comp:.1f}x compression")

        if 'context_savings' in self.results:
            savings = self.results['context_savings']['savings_pct']
            print(f"✅ Context Window Savings: {savings:.1f}%")

        if 'persistence_latency' in self.results:
            latency = self.results['persistence_latency']['avg_ms']
            print(f"✅ Persistence Latency: {latency:.2f}ms")

        # Save results
        with open('benchmark_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print("\n📄 Results saved to: benchmark_results.json")

        return self.results


def main():
    parser = argparse.ArgumentParser(description="Performance Benchmarks")
    parser.add_argument('--all', action='store_true', help='Run all benchmarks')
    parser.add_argument('--compression', action='store_true', help='Test observation masking')
    parser.add_argument('--context', action='store_true', help='Test context savings')
    parser.add_argument('--latency', action='store_true', help='Test persistence latency')
    parser.add_argument('--memory', action='store_true', help='Test memory overhead')

    args = parser.parse_args()

    benchmark = Benchmark()

    if args.all or not any([args.compression, args.context, args.latency, args.memory]):
        benchmark.run_all()
    else:
        if args.compression:
            benchmark.benchmark_observation_masking()
        if args.context:
            benchmark.benchmark_context_savings()
        if args.latency:
            benchmark.benchmark_persistence_latency()
        if args.memory:
            benchmark.benchmark_memory_overhead()


if __name__ == '__main__':
    main()
