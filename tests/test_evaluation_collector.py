from __future__ import annotations

import csv
import inspect
from pathlib import Path

import cv2
import numpy as np
import pytest

from evaluation import collector


def test_enrollment_and_test_paths_are_separate() -> None:
    enrollment = collector.build_dataset_path(
        "victims", "victim 01", "enrollment", "normal", ".jpg", "enroll-id"
    )
    test = collector.build_dataset_path(
        "victims", "victim 01", "test", "angle", ".jpg", "test-id"
    )

    assert enrollment.relative_to(collector.DATASET_ROOT).as_posix() == (
        "victims/enrollment/victim_01/enroll-id.jpg"
    )
    assert test.relative_to(collector.DATASET_ROOT).as_posix() == (
        "victims/test/angle/victim_01/test-id.jpg"
    )
    assert enrollment != test


def test_path_segments_cannot_escape_dataset() -> None:
    path = collector.build_dataset_path(
        "victims", "../../registered_faces", "test", "normal", ".png", "sample"
    )

    assert path.is_relative_to(collector.DATASET_ROOT)
    assert path.parent == collector.DATASET_ROOT / "victims" / "test" / "normal" / "registered_faces"


def test_invalid_category_and_condition_are_rejected() -> None:
    with pytest.raises(ValueError):
        collector.build_dataset_path(
            "registered_faces", "person", "test", "normal", ".jpg", "id"
        )
    with pytest.raises(ValueError):
        collector.build_dataset_path(
            "victims", "person", "test", "weather", ".jpg", "id"
        )


def test_legacy_metadata_rows_gain_ids(monkeypatch: pytest.MonkeyPatch) -> None:
    metadata_path = Path.cwd() / "tests" / ".collector_metadata_test.csv"
    try:
        metadata_path.write_text(
            "file_path,identity,category,split,condition,expected_result\n"
            "evaluation/dataset/victims/enrollment/a.jpg,a,victims,enrollment,normal,enrollment\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(collector, "METADATA_PATH", metadata_path)

        rows = collector.read_metadata_rows()

        assert len(rows) == 1
        assert rows[0]["id"]
        assert set(rows[0]) == set(collector.METADATA_FIELDS)
    finally:
        metadata_path.unlink(missing_ok=True)


class FakeFaceDetector:
    def __init__(self, face_count: int) -> None:
        self.face_count = face_count

    def detectMultiScale(self, image: np.ndarray, **kwargs: object) -> list[tuple[int, int, int, int]]:
        del image, kwargs
        return [(index, 0, 10, 10) for index in range(self.face_count)]


@pytest.mark.parametrize("face_count", [0, 2])
def test_enrollment_requires_exactly_one_face(
    monkeypatch: pytest.MonkeyPatch, face_count: int
) -> None:
    monkeypatch.setattr(collector, "load_face_detector", lambda: FakeFaceDetector(face_count))

    with pytest.raises(ValueError):
        collector.validate_faces(np.zeros((40, 40, 3), dtype=np.uint8), enrollment=True)


def test_enrollment_accepts_exactly_one_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(collector, "load_face_detector", lambda: FakeFaceDetector(1))

    assert collector.validate_faces(
        np.zeros((40, 40, 3), dtype=np.uint8), enrollment=True
    ) == 1


def test_test_images_require_at_least_one_face(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(collector, "load_face_detector", lambda: FakeFaceDetector(0))

    with pytest.raises(ValueError, match="at least one"):
        collector.validate_faces(np.zeros((40, 40, 3), dtype=np.uint8), enrollment=False)


def test_multiple_faces_are_allowed_for_test(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(collector, "load_face_detector", lambda: FakeFaceDetector(3))

    assert collector.validate_faces(
        np.zeros((40, 40, 3), dtype=np.uint8), enrollment=False
    ) == 3


def test_valid_file_saves_and_updates_metadata_atomically(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    class FixedUuid:
        hex = "sample-id"

    dataset_root = tmp_path / "dataset"
    metadata_path = tmp_path / "dataset_metadata.csv"
    image_bytes = b"valid image bytes"
    monkeypatch.setattr(collector, "DATASET_ROOT", dataset_root)
    monkeypatch.setattr(collector, "METADATA_PATH", metadata_path)
    monkeypatch.setattr(collector, "decode_image", lambda _: np.zeros((2, 2, 3), dtype=np.uint8))
    monkeypatch.setattr(collector, "validate_faces", lambda image, enrollment: 1)
    monkeypatch.setattr(collector.uuid, "uuid4", lambda: FixedUuid())

    target, face_count = collector.save_sample(
        image_bytes, "capture.png", "victim 01", "victims", "test", "angle"
    )

    assert target == dataset_root / "victims/test/angle/victim_01/sample-id.png"
    assert target.read_bytes() == image_bytes
    assert face_count == 1
    with metadata_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows == [
        {
            "id": "sample-id",
            "file_path": target.relative_to(collector.ROOT).as_posix(),
            "identity": "victim_01",
            "category": "victims",
            "split": "test",
            "condition": "angle",
            "expected_result": "genuine_victim",
        }
    ]
    assert not list(tmp_path.glob("*.tmp"))


def test_collector_does_not_require_deepface() -> None:
    source = inspect.getsource(collector).lower()

    assert "deepface" not in source