#!/usr/bin/env python3
"""Threshold calibration script for N-ONE.

This script does not fabricate numbers. It records the planned threshold sweep
for future real evaluation runs while the current workspace remains data-limited.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "evaluation" / "dataset"
RESULTS_CSV = ROOT / "evaluation" / "results" / "threshold_results.csv"


def dataset_ready() -> bool:
    return all(
        (
            DATASET_PATH / "victims").exists(),
            (DATASET_PATH / "staff").exists(),
            (DATASET_PATH / "impostors").exists(),
            (DATASET_PATH / "unknown").exists(),
            (DATASET_PATH / "threats").exists(),
        )
    )


def main() -> None:
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["threshold", "metric", "model", "status", "notes"])
        for threshold in [0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]:
            status = "PLANNED" if dataset_ready() else "INSUFFICIENT TEST DATA"
            notes = (
                "Threshold sweep is ready once dataset and runtime exist."
                if dataset_ready()
                else "Threshold values cannot be calibrated without labeled victim and impostor data."
            )
            writer.writerow([
                threshold,
                "cosine",
                "OpenCVFaceBackend",
                status,
                notes,
            ])

    if dataset_ready():
        print("Threshold sweep prepared. Real model results still need to be collected.")
    else:
        print("INSUFFICIENT TEST DATA")
        print("Threshold calibration requires a labeled dataset and a real DeepFace runtime.")


if __name__ == "__main__":
    main()
