#!/usr/bin/env python3
"""Jev vs Claude benchmark runner."""

import argparse
import json
import statistics
import sys
import os

from dotenv import load_dotenv
load_dotenv()

from tasks import TASKS
from scoring import score_case, compute_ece, compute_calibration_curve

COST_TABLE = {
    "jev":          {"input": 0.042 / 1_000_000, "output": 0.0},
    "opus":         {"input": 5.0   / 1_000_000, "output": 25.0 / 1_000_000},
    "sonnet":       {"input": 3.0   / 1_000_000, "output": 15.0 / 1_000_000},
    "opus-think":   {"input": 5.0   / 1_000_000, "output": 25.0 / 1_000_000},
    "sonnet-think": {"input": 3.0   / 1_000_000, "output": 15.0 / 1_000_000},
}


def make_runner(model_key: str):
    if model_key == "jev":
        from runners.jev_runner import JevRunner
        return JevRunner()
    elif model_key == "opus":
        from runners.claude_runner import ClaudeRunner
        return ClaudeRunner("claude-opus-4-6")
    elif model_key == "sonnet":
        from runners.claude_runner import ClaudeRunner
        return ClaudeRunner("claude-sonnet-4-6")
    elif model_key == "opus-think":
        from runners.claude_runner import ClaudeRunner
        return ClaudeRunner("claude-opus-4-6", label="opus-think", thinking=True)
    elif model_key == "sonnet-think":
        from runners.claude_runner import ClaudeRunner
        return ClaudeRunner("claude-sonnet-4-6", label="sonnet-think", thinking=True)
    else:
        raise ValueError(f"Unknown model: {model_key}")


def run_task(runner, task_slug: str, task: dict) -> dict:
    print(f"\n{'='*60}")
    print(f"  {task['emoji']} {task['name']} — {task['tagline']}")
    print(f"  Model: {runner.name()} ({runner.model_string()})")
    print(f"{'='*60}")

    cases_results = []

    for case in task["cases"]:
        print(f"  Case {case['id']:2d}... ", end="", flush=True)
        result = runner.run_case(task, case)

        if result is None:
            print("FAILED")
            cases_results.append({
                "id": case["id"],
                "input": case["text"],
                "expected": case["ground_truth"],
                "predicted": None,
                "confidence": None,
                "score": 0.0,
                "latency_ms": None,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": 0.0,
            })
            continue

        scored = score_case(task, result, case)

        predicted_values = {
            qname: ans["value"]
            for qname, ans in result["answers"].items()
        }

        cost_rates = COST_TABLE[runner.name()]
        cost = (
            result["input_tokens"] * cost_rates["input"]
            + result["output_tokens"] * cost_rates["output"]
        )

        cases_results.append({
            "id": case["id"],
            "input": case["text"],
            "expected": case["ground_truth"],
            "predicted": predicted_values,
            "confidence": scored["confidence"],
            "score": scored["score"],
            "latency_ms": result["latency_ms"],
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "cost_usd": cost,
        })

        status = "OK" if scored["score"] >= 1.0 else f"{scored['score']:.2f}"
        print(f"{status}  (conf={scored['confidence']:.2f}, {result['latency_ms']:.0f}ms)")

    completed = [c for c in cases_results if c["predicted"] is not None]
    latencies = [c["latency_ms"] for c in completed if c["latency_ms"] is not None]
    scores = [c["score"] for c in cases_results]
    total_cost = sum(c["cost_usd"] for c in cases_results)
    num_correct = sum(1 for s in scores if s >= 1.0)

    calibration_data = [
        {"confidence": c["confidence"], "score": c["score"]}
        for c in completed
    ]

    summary = {
        "accuracy": statistics.mean(scores) if scores else 0.0,
        "mean_confidence": statistics.mean(c["confidence"] for c in completed) if completed else 0.0,
        "calibration_error": compute_ece(calibration_data),
        "calibration_curve": compute_calibration_curve(calibration_data),
        "median_latency_ms": statistics.median(latencies) if latencies else 0.0,
        "p95_latency_ms": sorted(latencies)[min(int(len(latencies) * 0.95) - 1, len(latencies) - 1)] if latencies else 0.0,
        "total_cost_usd": total_cost,
        "cost_per_correct_usd": total_cost / num_correct if num_correct > 0 else None,
        "completed": len(completed),
        "total": len(cases_results),
    }

    print(f"\n  Accuracy: {summary['accuracy']*100:.1f}%  |  "
          f"ECE: {summary['calibration_error']:.3f}  |  "
          f"Median: {summary['median_latency_ms']:.0f}ms  |  "
          f"Cost: ${summary['total_cost_usd']:.6f}")

    return {
        "model": runner.name(),
        "model_string": runner.model_string(),
        "task": task_slug,
        "cases": cases_results,
        "summary": summary,
    }


def main():
    parser = argparse.ArgumentParser(description="Jev vs Claude Benchmark")
    parser.add_argument("--model", choices=["jev", "opus", "sonnet", "opus-think", "sonnet-think"], help="Run a single model")
    parser.add_argument("--task", choices=list(TASKS.keys()), help="Run a single task")
    parser.add_argument("--output", default="results.json", help="Output file (default: results.json)")
    args = parser.parse_args()

    models = [args.model] if args.model else ["jev", "opus", "sonnet", "opus-think", "sonnet-think"]
    task_slugs = [args.task] if args.task else list(TASKS.keys())

    existing = []
    if os.path.exists(args.output):
        with open(args.output) as f:
            existing = json.load(f)

    results = [
        r for r in existing
        if not (r["model"] in models and r["task"] in task_slugs)
    ]

    for model_key in models:
        try:
            runner = make_runner(model_key)
        except (ImportError, Exception) as e:
            print(f"\nSkipping {model_key}: {e}")
            continue

        try:
            for slug in task_slugs:
                result = run_task(runner, slug, TASKS[slug])
                results.append(result)
        finally:
            if hasattr(runner, "close"):
                runner.close()

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to {args.output}")
    print(f"Run `python report.py` to generate the HTML report.")


if __name__ == "__main__":
    main()
