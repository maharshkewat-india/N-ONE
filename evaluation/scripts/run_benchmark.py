#!/usr/bin/env python3
"""Run the isolated N-ONE victim recognition benchmark."""

from __future__ import annotations

import csv
import hashlib
import os
import platform
import sys
import tempfile
import types
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = ROOT / "evaluation" / "dataset_metadata.csv"
RESULTS_DIR = ROOT / "evaluation" / "results"
REPORT_PATH = ROOT / "docs" / "AI_MODEL_EVALUATION_REPORT.md"
MODELS = ("Facenet", "Facenet512", "ArcFace")
DETECTOR = "retinaface"
DISTANCE_METRIC = "cosine"
THRESHOLDS = (0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
DEFAULT_THRESHOLD = 0.40


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    identity: str
    category: str
    split: str
    condition: str
    expected_result: str


@dataclass(frozen=True)
class Representation:
    embeddings: tuple[np.ndarray, ...]
    latency_seconds: float
    status: str
    error: str = ""


@dataclass(frozen=True)
class Trial:
    model: str
    trial_type: str
    image_path: str
    image_identity: str
    target_identity: str
    distance: float
    status: str


def configure_isolated_cache() -> Path:
    cache = Path(tempfile.gettempdir()) / "n_one_deepface_benchmark_cache"
    cache.mkdir(parents=True, exist_ok=True)
    os.environ["HOME"] = str(cache)
    os.environ["USERPROFILE"] = str(cache)
    return cache


def read_records() -> tuple[list[ImageRecord], list[ImageRecord], list[ImageRecord]]:
    with METADATA_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    enrollment: list[ImageRecord] = []
    genuine: list[ImageRecord] = []
    impostors: list[ImageRecord] = []
    for row in rows:
        path = ROOT / row["file_path"]
        if not path.exists():
            raise FileNotFoundError(f"Metadata path does not exist: {path}")
        record = ImageRecord(
            path=path,
            identity=row["identity"],
            category=row["category"],
            split=row["split"],
            condition=row["condition"],
            expected_result=row["expected_result"],
        )
        if record.category == "victims" and record.split == "enrollment":
            enrollment.append(record)
        elif record.category == "victims" and record.split == "test":
            genuine.append(record)
        elif record.category == "impostor" and record.split == "test":
            impostors.append(record)

    if not enrollment or not genuine or not impostors:
        raise ValueError("The validated victim and impostor dataset is incomplete.")
    return enrollment, genuine, impostors


def cosine_distance(left: np.ndarray, right: np.ndarray) -> float:
    left_norm = np.linalg.norm(left)
    right_norm = np.linalg.norm(right)
    if left_norm == 0 or right_norm == 0:
        return 1.0
    return float(1.0 - np.dot(left, right) / (left_norm * right_norm))


def minimum_distance(
    left_embeddings: tuple[np.ndarray, ...],
    right_embeddings: tuple[np.ndarray, ...],
) -> float:
    if not left_embeddings or not right_embeddings:
        return float("inf")
    return min(cosine_distance(left, right) for left in left_embeddings for right in right_embeddings)


def represent_image(deepface: Any, model: str, record: ImageRecord) -> Representation:
    started = time.perf_counter()
    try:
        values = deepface.represent(
            img_path=str(record.path),
            model_name=model,
            detector_backend=DETECTOR,
            enforce_detection=False,
            align=True,
        )
        embeddings = tuple(
            np.asarray(value["embedding"], dtype=np.float64) for value in values
        )
        return Representation(
            embeddings=embeddings,
            latency_seconds=time.perf_counter() - started,
            status="ok" if embeddings else "no_face",
        )
    except Exception as exc:  # model/detector errors are recorded per model
        return Representation(
            embeddings=(),
            latency_seconds=time.perf_counter() - started,
            status="error",
            error=f"{type(exc).__name__}: {exc}",
        )


def summarize_metrics(trials: list[Trial], threshold: float) -> dict[str, Any]:
    genuine = [trial for trial in trials if trial.trial_type == "genuine"]
    impostor = [trial for trial in trials if trial.trial_type == "impostor"]
    tp = sum(trial.distance <= threshold for trial in genuine)
    fn = len(genuine) - tp
    fp = sum(trial.distance <= threshold for trial in impostor)
    tn = len(impostor) - fp
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    far = fp / (fp + tn) if fp + tn else 0.0
    frr = fn / (fn + tp) if fn + tp else 0.0
    return {
        "threshold": threshold,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "far": far,
        "frr": frr,
        "false_victim_matches": fp,
        "genuine_trials": len(genuine),
        "impostor_trials": len(impostor),
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def environment_info(cache: Path) -> dict[str, str]:
    try:
        import psutil

        memory = f"{psutil.virtual_memory().total / (1024 ** 3):.2f} GiB"
    except Exception:
        memory = "unavailable"
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "processor": platform.processor() or "unavailable",
        "ram": memory,
        "gpu": "not measured; CPU execution requested",
        "cache": str(cache),
    }


def import_deepface() -> Any:
    try:
        import pandas  # noqa: F401
    except ImportError:
        pandas_stub = types.ModuleType("pandas")
        pandas_stub.DataFrame = type("DataFrame", (), {})
        pandas_stub.Series = type("Series", (), {})
        sys.modules["pandas"] = pandas_stub

    from deepface import DeepFace

    return DeepFace


def run_model(
    deepface: Any,
    model: str,
    enrollment: list[ImageRecord],
    genuine: list[ImageRecord],
    impostors: list[ImageRecord],
) -> tuple[list[Trial], list[dict[str, Any]], dict[str, Any]]:
    by_identity: dict[str, list[ImageRecord]] = {}
    for record in enrollment:
        by_identity.setdefault(record.identity, []).append(record)

    all_records = enrollment + genuine + impostors
    representations: dict[Path, Representation] = {}
    for record in all_records:
        representations[record.path] = represent_image(deepface, model, record)

    errors = [
        representation.error
        for representation in representations.values()
        if representation.status == "error"
    ]
    if errors:
        raise RuntimeError("; ".join(sorted(set(errors))))

    enrollment_embeddings = {
        identity: tuple(
            embedding
            for record in records
            for embedding in representations[record.path].embeddings
        )
        for identity, records in by_identity.items()
    }
    trials: list[Trial] = []
    comparison_latencies: list[float] = []
    for record in genuine:
        started = time.perf_counter()
        distance = minimum_distance(
            representations[record.path].embeddings,
            enrollment_embeddings[record.identity],
        )
        comparison_latencies.append(time.perf_counter() - started)
        trials.append(
            Trial(model, "genuine", str(record.path.relative_to(ROOT)), record.identity, record.identity, distance, representations[record.path].status)
        )
    for record in impostors:
        for identity, embeddings in enrollment_embeddings.items():
            started = time.perf_counter()
            distance = minimum_distance(representations[record.path].embeddings, embeddings)
            comparison_latencies.append(time.perf_counter() - started)
            trials.append(
                Trial(model, "impostor", str(record.path.relative_to(ROOT)), record.identity, identity, distance, representations[record.path].status)
            )

    embedding_latencies = [representation.latency_seconds for representation in representations.values()]
    performance = {
        "model": model,
        "detector_backend": DETECTOR,
        "distance_metric": DISTANCE_METRIC,
        "image_count": len(all_records),
        "no_face_images": sum(rep.status == "no_face" for rep in representations.values()),
        "error_images": sum(rep.status == "error" for rep in representations.values()),
        "average_inference_latency_seconds": sum(embedding_latencies) / len(embedding_latencies),
        "median_inference_latency_seconds": median(embedding_latencies),
        "fps_from_average_inference": 1 / (sum(embedding_latencies) / len(embedding_latencies)),
        "average_embedding_generation_seconds": sum(embedding_latencies) / len(embedding_latencies),
        "average_comparison_seconds": sum(comparison_latencies) / len(comparison_latencies),
        "preprocessing_seconds": "included in inference latency; not separately exposed by DeepFace",
        "cpu_ram_gpu": "CPU/RAM/GPU details in report; GPU not used",
        "status": "measured",
    }
    threshold_rows = [dict(model=model, **summarize_metrics(trials, threshold)) for threshold in THRESHOLDS]
    return trials, threshold_rows, performance


def write_report(
    env: dict[str, str],
    enrollment: list[ImageRecord],
    genuine: list[ImageRecord],
    impostors: list[ImageRecord],
    model_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    performance_rows: list[dict[str, Any]],
    failures: list[dict[str, str]],
) -> None:
    lines = [
        "# N-ONE AI Model Evaluation Report",
        "",
        "## 1. Executive Summary",
        "",
        "This report contains measured results from the isolated N-ONE victim face-recognition benchmark. It does not modify the live application or production thresholds. The impostor sample is limited to 10 LFW identities and 12 images, so results are evidence for this dataset only and are not production or universal accuracy claims.",
        "",
        "## 2. Objective and Protocol",
        "",
        f"Each of {len(genuine)} independent genuine victim test images was compared with enrollment representations for its labeled victim. Each of {len(impostors)} impostor images was compared against each of {len({record.identity for record in enrollment})} victim identities, producing {len(impostors) * len({record.identity for record in enrollment})} negative trials. Enrollment and test paths were separate.",
        "",
        f"Distance metric: `{DISTANCE_METRIC}`. Thresholds tested: {', '.join(f'{value:.2f}' for value in THRESHOLDS)}. Detector/backend: `{DETECTOR}` where supported. A test decision is a match when the minimum distance to that victim's enrollment embeddings is less than or equal to the tested threshold.",
        "",
        "## 3. Environment",
        "",
        *[f"- {key}: {value}" for key, value in env.items()],
        "",
        "## 4. Dataset",
        "",
        f"- Victim identities: {len({record.identity for record in enrollment})}",
        f"- Victim enrollment images: {len(enrollment)}",
        f"- Genuine victim test images: {len(genuine)}",
        f"- Impostor identities: {len({record.identity for record in impostors})}",
        f"- Impostor images: {len(impostors)}",
        "- Source: Labeled Faces in the Wild (LFW), with source labels recorded in `evaluation/impostor_sources.csv`.",
        "- Dataset limitation: 10 identities and 12 impostor images are a limited evaluation sample.",
        "",
        "## 5. Measured Model Results",
        "",
        "The model comparison below uses the configured threshold of 0.40. Values are measured, not estimated.",
        "",
        "| Model | Status | TP | TN | FP | FN | Precision | Recall | F1 | FAR | FRR | False victim matches |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in model_rows:
        lines.append(
            f"| {row['model']} | {row['status']} | {row.get('tp', '')} | {row.get('tn', '')} | {row.get('fp', '')} | {row.get('fn', '')} | {row.get('precision', '')} | {row.get('recall', '')} | {row.get('f1', '')} | {row.get('far', '')} | {row.get('frr', '')} | {row.get('false_victim_matches', '')} |"
        )
    if failures:
        lines.extend(["", "Model failures:"])
        lines.extend(f"- {row['model']}: {row['error']}" for row in failures)
    lines.extend(
        [
            "",
            "## 6. Threshold Results",
            "",
            "Complete threshold metrics are in `evaluation/results/threshold_comparison.csv`. No threshold was selected solely because it maximized one metric.",
            "",
            "## 7. Performance",
            "",
            "Measured performance is in `evaluation/results/performance_results.csv`. Inference latency includes detector, alignment/preprocessing, and embedding generation because DeepFace does not expose those stages separately through this API. Comparison latency is measured separately. GPU usage was not used.",
            "",
            "## 8. Multi-frame Results",
            "",
            "No video or frame-sequence assets were present in the validated evaluation dataset. One-frame, three-frame, and five-frame confirmation metrics were therefore not measured and are recorded as unavailable rather than inferred.",
            "",
            "## 9. Failure Cases and Limitations",
            "",
            "- Face detection failures are represented as no-match decisions when DeepFace returns no embeddings.",
            "- The impostor sample is limited and contains still images rather than operational CCTV sequences.",
            "- Results do not establish production accuracy, universal accuracy, real-world CCTV accuracy, guaranteed victim identification, or 100% recognition.",
            "- Published/model documentation describes the models and detector; all tables in this report are N-ONE measurements from this run.",
            "",
            "## 10. Evidence-Based Analysis",
            "",
            "False victim matches, FAR, precision, recall, and FRR should be considered together. A lower FAR is especially important for Victim Search, but a configuration that rejects too many genuine victim images also has operational cost. The complete measured CSVs should be reviewed before changing any production threshold or model.",
            "",
            "## 11. Recommended Next Experiment",
            "",
            "Collect additional independently labeled impostor identities and real frame sequences across lighting, distance, angle, blur, occlusion, and multiple-face conditions. Then repeat this isolated protocol and evaluate three- and five-frame confirmation before considering any production change.",
        ]
    )
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    cache = configure_isolated_cache()
    enrollment, genuine, impostors = read_records()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    env = environment_info(cache)

    DeepFace = import_deepface()

    model_rows: list[dict[str, Any]] = []
    threshold_rows: list[dict[str, Any]] = []
    performance_rows: list[dict[str, Any]] = []
    trial_rows: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for model in MODELS:
        try:
            trials, model_thresholds, performance = run_model(
                DeepFace, model, enrollment, genuine, impostors
            )
            threshold_rows.extend(model_thresholds)
            performance_rows.append(performance)
            trial_rows.extend(
                {
                    "model": trial.model,
                    "trial_type": trial.trial_type,
                    "image_path": trial.image_path,
                    "image_identity": trial.image_identity,
                    "target_identity": trial.target_identity,
                    "distance": trial.distance,
                    "status": trial.status,
                    "default_threshold": DEFAULT_THRESHOLD,
                    "decision_at_default": trial.distance <= DEFAULT_THRESHOLD,
                }
                for trial in trials
            )
            model_rows.append(dict(model=model, status="measured", **summarize_metrics(trials, DEFAULT_THRESHOLD)))
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
            failures.append({"model": model, "error": error})
            model_rows.append({"model": model, "status": "unavailable", "error": error})
            performance_rows.append(
                {
                    "model": model,
                    "detector_backend": DETECTOR,
                    "distance_metric": DISTANCE_METRIC,
                    "status": "unavailable",
                    "error": error,
                }
            )

    write_csv(
        RESULTS_DIR / "model_comparison.csv",
        ["model", "status", "threshold", "tp", "tn", "fp", "fn", "precision", "recall", "f1", "far", "frr", "false_victim_matches", "genuine_trials", "impostor_trials", "error"],
        model_rows,
    )
    write_csv(
        RESULTS_DIR / "threshold_comparison.csv",
        ["model", "threshold", "tp", "tn", "fp", "fn", "precision", "recall", "f1", "far", "frr", "false_victim_matches", "genuine_trials", "impostor_trials"],
        threshold_rows,
    )
    write_csv(
        RESULTS_DIR / "performance_results.csv",
        sorted({key for row in performance_rows for key in row}),
        performance_rows,
    )
    write_csv(
        RESULTS_DIR / "victim_results.csv",
        ["model", "trial_type", "image_path", "image_identity", "target_identity", "distance", "status", "default_threshold", "decision_at_default"],
        [row for row in trial_rows if row["trial_type"] == "genuine"],
    )
    write_csv(
        RESULTS_DIR / "impostor_results.csv",
        ["model", "trial_type", "image_path", "image_identity", "target_identity", "distance", "status", "default_threshold", "decision_at_default"],
        [row for row in trial_rows if row["trial_type"] == "impostor"],
    )
    write_csv(
        RESULTS_DIR / "multi_frame_results.csv",
        ["model", "confirmation_frames", "status", "reason"],
        [
            {"model": model, "confirmation_frames": frames, "status": "not_available", "reason": "No labeled video/frame sequences in evaluation dataset."}
            for model in MODELS
            for frames in (1, 3, 5)
        ],
    )
    write_report(env, enrollment, genuine, impostors, model_rows, threshold_rows, performance_rows, failures)

    print(f"Wrote benchmark results to {RESULTS_DIR}")
    print(f"Wrote report to {REPORT_PATH}")
    for row in model_rows:
        print(row)


if __name__ == "__main__":
    main()
