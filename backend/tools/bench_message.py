#!/usr/bin/env python3
"""
Benchmark script for measuring end-to-end latency of the Munimji chatbot graph.

Usage:
    python tools/bench_message.py [--iterations N] [--output FILE]
    
This script measures:
- Total wall-clock time per request
- Per-node timing (if timing decorators are enabled)
- Median, 95th percentile, and average latencies
"""
import os
import sys
import time
import json
import statistics
import argparse
from datetime import datetime
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from langchain_core.messages import HumanMessage
from backend.agents.state import AgentState

# Test messages covering various intents
TEST_MESSAGES = [
    # Expense intents (should hit rule-based fast path)
    "Fuel 200",
    "Petrol bharwaya 500",
    "Rent paid 5000",
    "Electricity bill 1200",
    
    # Sale intents
    "Sold 10 packets chips to Ramesh for 200",
    "Becha 5 kg rice 300 rupees",
    "Invoice to Mohan 1500",
    
    # Purchase intents
    "Bought stock 2000 from wholesale",
    "Kharida 50 packets biscuit 500",
    "Purchase 10 kg dal 800",
    
    # Udhaar intents
    "Aman ko udhaar 500 diya",
    "Ramesh se udhaar liya 1000",
    "Customer Suresh udhar 300",
    
    # Payment intents
    "Received 500 from Ramesh",
    "Paid back 200 to supplier",
    "Payment received from Mohan 1000",
    
    # Query intents
    "Show today's summary",
    "Show ledger",
    "Who owes me?",
    
    # Greeting
    "Hi",
    "Namaste",
]


def run_single_benchmark(message: str, user_id: int = 1) -> Dict[str, Any]:
    """Run a single benchmark iteration."""
    from backend.agents.graph import compiled_graph
    from backend.decorators.timeit import get_timings, clear_timings
    
    clear_timings()
    
    initial_state: AgentState = {
        "messages": [HumanMessage(content=message)],
        "intent": "",
        "intent_confidence": 0.0,
        "intent_reason": "",
        "entities": {},
        "context": {},
        "response": "",
        "user_id": user_id,
        "missing_slots": [],
        "needs_followup": False,
        "route": ""
    }
    
    start_time = time.perf_counter()
    result = compiled_graph.invoke(initial_state)
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    node_timings = get_timings()
    
    return {
        "message": message,
        "total_time_ms": total_time * 1000,
        "intent": result.get("intent", ""),
        "intent_reason": result.get("intent_reason", ""),
        "response": result.get("response", "")[:100],  # Truncate for readability
        "node_timings_ms": {k: v * 1000 for k, v in node_timings.items()} if node_timings else {},
    }


def run_benchmark(iterations: int = 3, messages: List[str] = None) -> Dict[str, Any]:
    """Run full benchmark suite."""
    if messages is None:
        messages = TEST_MESSAGES
    
    results = []
    all_times = []
    
    print(f"Running benchmark with {iterations} iterations per message...")
    print(f"Total messages: {len(messages)}")
    print("-" * 60)
    
    for i, msg in enumerate(messages):
        msg_times = []
        for iteration in range(iterations):
            try:
                result = run_single_benchmark(msg)
                msg_times.append(result["total_time_ms"])
                all_times.append(result["total_time_ms"])
                
                if iteration == 0:  # Only store first iteration details
                    results.append(result)
                    
            except Exception as e:
                print(f"Error processing '{msg}': {e}")
                continue
        
        if msg_times:
            avg_time = statistics.mean(msg_times)
            print(f"[{i+1}/{len(messages)}] '{msg[:40]}...' - Avg: {avg_time:.1f}ms")
    
    # Calculate statistics
    if all_times:
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_messages": len(messages),
            "iterations_per_message": iterations,
            "total_runs": len(all_times),
            "statistics": {
                "median_ms": statistics.median(all_times),
                "mean_ms": statistics.mean(all_times),
                "p95_ms": statistics.quantiles(all_times, n=20)[-1] if len(all_times) >= 20 else max(all_times),
                "min_ms": min(all_times),
                "max_ms": max(all_times),
                "stdev_ms": statistics.stdev(all_times) if len(all_times) > 1 else 0,
            },
            "results": results,
        }
    else:
        stats = {"error": "No successful runs", "timestamp": datetime.now().isoformat()}
    
    return stats


def print_summary(stats: Dict[str, Any]):
    """Print a summary of benchmark results."""
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    if "error" in stats:
        print(f"Error: {stats['error']}")
        return
    
    s = stats["statistics"]
    print(f"Total runs: {stats['total_runs']}")
    print(f"Median latency: {s['median_ms']:.1f}ms")
    print(f"Mean latency: {s['mean_ms']:.1f}ms")
    print(f"95th percentile: {s['p95_ms']:.1f}ms")
    print(f"Min: {s['min_ms']:.1f}ms, Max: {s['max_ms']:.1f}ms")
    print(f"Std Dev: {s['stdev_ms']:.1f}ms")
    
    # Check against target
    target_ms = 3000
    if s['median_ms'] <= target_ms:
        print(f"\n✅ PASS: Median latency ({s['median_ms']:.1f}ms) is under target ({target_ms}ms)")
    else:
        print(f"\n❌ FAIL: Median latency ({s['median_ms']:.1f}ms) exceeds target ({target_ms}ms)")
    
    # Per-intent breakdown
    print("\n" + "-" * 40)
    print("PER-INTENT BREAKDOWN:")
    intent_times = {}
    for r in stats.get("results", []):
        intent = r.get("intent", "unknown")
        if intent not in intent_times:
            intent_times[intent] = []
        intent_times[intent].append(r["total_time_ms"])
    
    for intent, times in sorted(intent_times.items()):
        avg = statistics.mean(times)
        reason = "rule-based" if any(r.get("intent_reason") == "rule-based" for r in stats["results"] if r.get("intent") == intent) else "llm"
        print(f"  {intent}: {avg:.1f}ms avg ({len(times)} samples) [{reason}]")
    
    # Node timing breakdown if available
    node_times = {}
    for r in stats.get("results", []):
        for node, time_ms in r.get("node_timings_ms", {}).items():
            if node not in node_times:
                node_times[node] = []
            node_times[node].append(time_ms)
    
    if node_times:
        print("\n" + "-" * 40)
        print("PER-NODE TIMING:")
        for node, times in sorted(node_times.items(), key=lambda x: -statistics.mean(x[1])):
            avg = statistics.mean(times)
            print(f"  {node}: {avg:.1f}ms avg")


def main():
    parser = argparse.ArgumentParser(description="Benchmark Munimji chatbot latency")
    parser.add_argument("--iterations", "-n", type=int, default=3, help="Iterations per message")
    parser.add_argument("--output", "-o", type=str, help="Output file for JSON results")
    parser.add_argument("--quick", "-q", action="store_true", help="Quick mode: fewer messages")
    args = parser.parse_args()
    
    messages = TEST_MESSAGES[:5] if args.quick else TEST_MESSAGES
    
    stats = run_benchmark(iterations=args.iterations, messages=messages)
    print_summary(stats)
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(stats, f, indent=2)
        print(f"\nResults saved to {args.output}")
    
    # Return exit code based on target
    if "statistics" in stats:
        target_ms = 5000  # CI threshold
        if stats["statistics"]["median_ms"] > target_ms:
            sys.exit(1)
    
    return 0


if __name__ == "__main__":
    main()
