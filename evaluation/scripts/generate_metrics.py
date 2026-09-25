#!/usr/bin/env python3
"""Metric-generation stub for N-ONE evaluation.

This script intentionally avoids inventing metrics. It writes a placeholder
result file whenever the required dataset is not available.
"""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS_DIR = ROOT / "evaluation" / "results"


def write_placeholder(filename: str, rows: list[list[str]]) -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    path = RESULTS_DIR / filename
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value", "status", "notes"])
        for row in rows:
            writer.writerow(row)


def main() -> None:
    write_placeholder(
        "victim_results.csv",
        [["tp", "0", "INSUFFICIENT TEST DATA", "No labeled victim evaluation set found."]],
    )
    write_placeholder(
        "staff_results.csv",
        [["tp", "0", "INSUFFICIENT TEST DATA", "No labeled staff evaluation set found."]],
    )
    write_placeholder(
        "threat_results.csv",
        [["precision", "0", "INSUFFICIENT TEST DATA", "Threat detection is heuristic and dataset is absent."]],
    )
    print("INSUFFICIENT TEST DATA")


if __name__ == "__main__":
    main()
