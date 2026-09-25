#!/usr/bin/env python3
"""Placeholder benchmark script for future real-model evaluation.

This script remains intentionally non-destructive and does not claim any model
winner. It validates the dataset layout and documents the runtime status.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "evaluation" / "dataset"
RESULTS_PATH = ROOT / "evaluation" / "results" / "benchmark_plan.csv"


def main() -> None:
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ["backend", "metric", "status", "notes"],
        ["OpenCVFaceBackend", "cosine", "ACTIVE BASELINE", "Current runtime in this workspace; baseline only."],
        ["Facenet", "cosine", "PLANNED", "Requires supported Python 3.10-3.13 DeepFace runtime and labeled dataset."],
        ["Facenet512", "cosine", "PLANNED", "Requires supported Python 3.10-3.13 DeepFace runtime and labeled dataset."],
        ["ArcFace", "cosine", "PLANNED", "Requires supported Python 3.10-3.13 DeepFace runtime and labeled dataset."],
    ]
    with RESULTS_PATH.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    print("Benchmark plan prepared. No model winner declared.")


if __name__ == "__main__":
    main()
