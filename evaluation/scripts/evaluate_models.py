#!/usr/bin/env python3
"""Model evaluation entry point for N-ONE.

This script intentionally avoids guessing model quality. It checks the runtime
compatibility and dataset readiness before calculating any metrics.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "evaluation" / "dataset"
METADATA_PATH = ROOT / "evaluation" / "dataset_metadata.csv"
RESULTS_CSV = ROOT / "evaluation" / "results" / "model_results.csv"


def python_version_supported() -> bool:
    return sys.version_info[:2] in {(3, 10), (3, 11), (3, 12), (3, 13)}


def has_real_deepface_runtime() -> bool:
    try:
        import deepface_adapter as adapter
        if adapter.DEEPFACE_IMPORT_ERROR is not None:
            return False
        return hasattr(adapter, "DeepFace") and type(adapter.DeepFace).__name__ != "OpenCVFaceBackend"
    except Exception:
        return False


def dataset_ready() -> bool:
    required = [
        DATASET_DIR / "victims",
        DATASET_DIR / "staff",
        DATASET_DIR / "impostors",
        DATASET_DIR / "unknown",
        DATASET_DIR / "threats",
    ]
    if not METADATA_PATH.exists():
        return False
    return all(path.exists() for path in required)


def write_empty_result() -> None:
    RESULTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with RESULTS_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model", "backend", "metric", "status", "evidence"])
        for model, backend, metric in [
            ("Facenet", "DeepFace", "cosine"),
            ("Facenet512", "DeepFace", "cosine"),
            ("ArcFace", "DeepFace", "cosine"),
            ("OpenCVFaceBackend", "Haar + HOG/CLAHE fallback", "cosine"),
        ]:
            status = "INSUFFICIENT TEST DATA" if model != "OpenCVFaceBackend" else "ACTIVE BASELINE"
            evidence = (
                "No supported TensorFlow/DeepFace runtime or labeled evaluation dataset found."
                if model != "OpenCVFaceBackend"
                else "Current runtime in this workspace; no benchmark data available."
            )
            writer.writerow([model, backend, metric, status, evidence])


def main() -> None:
    if not python_version_supported():
        print("INSUFFICIENT TEST DATA")
        print("Reason: Python is not a supported DeepFace runtime version for TensorFlow-backed models.")
        write_empty_result()
        return

    if not has_real_deepface_runtime() or not dataset_ready():
        print("INSUFFICIENT TEST DATA")
        print("Reason: no supported DeepFace runtime and/or no labeled evaluation dataset found.")
        write_empty_result()
        return

    print("Prepared benchmark environment; dataset and runtime are ready for a real model run.")
    print("Do not declare a winner until measured results are recorded.")


if __name__ == "__main__":
    main()
