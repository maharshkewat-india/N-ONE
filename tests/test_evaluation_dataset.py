from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = ROOT / "evaluation" / "dataset"
METADATA_PATH = ROOT / "evaluation" / "dataset_metadata.csv"


def test_evaluation_dataset_structure_exists() -> None:
    expected_dirs = [
        DATASET_ROOT / "victims",
        DATASET_ROOT / "staff",
        DATASET_ROOT / "impostors",
        DATASET_ROOT / "unknown",
        DATASET_ROOT / "threats",
    ]
    for directory in expected_dirs:
        assert directory.exists(), f"Missing dataset directory: {directory}"


def test_dataset_metadata_has_required_columns() -> None:
    assert METADATA_PATH.exists(), "Metadata file is missing"
    header = METADATA_PATH.read_text(encoding="utf-8").strip().splitlines()[0]
    expected = "id,file_path,identity,category,split,condition,expected_result"
    assert header == expected, f"Unexpected metadata header: {header!r}"
