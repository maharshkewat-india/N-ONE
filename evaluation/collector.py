"""Standalone Streamlit utility for collecting labeled evaluation images."""

from __future__ import annotations

import csv
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATASET_ROOT = ROOT / "evaluation" / "dataset"
METADATA_PATH = ROOT / "evaluation" / "dataset_metadata.csv"
METADATA_FIELDS = (
    "id",
    "file_path",
    "identity",
    "category",
    "split",
    "condition",
    "expected_result",
)
CATEGORIES = ("victims", "staff", "impostors", "unknown", "threats")
TEST_CONDITIONS = (
    "normal",
    "angle",
    "lighting",
    "distance",
    "blur",
    "occlusion",
    "multiple_faces",
)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def clean_path_segment(value: str, label: str) -> str:
    """Return a safe, non-empty single path segment."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = cleaned.strip("._-")
    if not cleaned:
        raise ValueError(f"{label} must contain letters or numbers.")
    return cleaned


def build_dataset_path(
    category: str,
    identity: str,
    split: str,
    condition: str,
    suffix: str,
    image_id: str,
) -> Path:
    """Build a path that keeps enrollment and test data disjoint."""
    if category not in CATEGORIES:
        raise ValueError("Unsupported category.")
    if split not in {"enrollment", "test"}:
        raise ValueError("Split must be enrollment or test.")
    if split == "test" and condition not in TEST_CONDITIONS:
        raise ValueError("Unsupported test condition.")

    safe_identity = clean_path_segment(identity, "Identity")
    safe_suffix = suffix.lower() if suffix.lower() in IMAGE_SUFFIXES else ".jpg"
    if split == "enrollment":
        relative = Path(category) / split / safe_identity / f"{image_id}{safe_suffix}"
    else:
        relative = (
            Path(category)
            / split
            / condition
            / safe_identity
            / f"{image_id}{safe_suffix}"
        )
    return DATASET_ROOT / relative


def expected_result_for(category: str, split: str) -> str:
    """Return the label used by benchmark consumers for a saved sample."""
    if category == "victims" and split == "test":
        return "genuine_victim"
    if category == "victims":
        return "enrollment"
    return "non_victim"


def read_metadata_rows() -> list[dict[str, str]]:
    """Read existing rows and upgrade the previous header format in memory."""
    if not METADATA_PATH.exists() or METADATA_PATH.stat().st_size == 0:
        return []

    with METADATA_PATH.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        required_without_id = set(METADATA_FIELDS) - {"id"}
        if not required_without_id.issubset(fieldnames):
            raise ValueError("Metadata CSV is missing required columns.")

        rows: list[dict[str, str]] = []
        for row in reader:
            normalized = {field: str(row.get(field, "") or "") for field in METADATA_FIELDS}
            if not normalized["id"]:
                normalized["id"] = uuid.uuid4().hex
            rows.append(normalized)
        return rows


def write_metadata_rows(rows: list[dict[str, str]]) -> None:
    """Write metadata atomically so a rerun cannot leave a partial CSV."""
    METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", newline="", encoding="utf-8", dir=METADATA_PATH.parent, delete=False
    ) as temporary:
        temporary_path = Path(temporary.name)
        writer = csv.DictWriter(temporary, fieldnames=METADATA_FIELDS)
        writer.writeheader()
        rows_for_csv: Any = rows
        writer.writerows(rows_for_csv)
    temporary_path.replace(METADATA_PATH)


def decode_image(image_bytes: bytes) -> np.ndarray:
    """Decode uploaded bytes and reject unreadable or empty images."""
    image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None or image.size == 0:
        raise ValueError("The uploaded file is not a readable image.")
    return image


@st.cache_resource(show_spinner=False)
def load_face_detector() -> cv2.CascadeClassifier:
    """Load OpenCV's bundled frontal-face detector once per collector session."""
    cascade_path = (
        Path(cv2.__file__).resolve().parent
        / "data"
        / "haarcascade_frontalface_default.xml"
    )
    detector = cv2.CascadeClassifier(str(cascade_path))
    if detector.empty():
        raise RuntimeError(f"Could not load OpenCV face detector: {cascade_path}")
    return detector


def validate_faces(image: np.ndarray, enrollment: bool) -> int:
    """Require a face and exactly one face for enrollment images."""
    detector = load_face_detector()
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = detector.detectMultiScale(
        grayscale,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
    )
    face_count = len(faces)
    if face_count < 1:
        raise ValueError("The image must contain at least one detectable face.")
    if enrollment and face_count != 1:
        raise ValueError(
            f"Enrollment images must contain exactly one face; detected {face_count}."
        )
    return face_count


def save_sample(
    image_bytes: bytes,
    original_name: str,
    identity: str,
    category: str,
    split: str,
    condition: str,
) -> tuple[Path, int]:
    """Validate and save one image, then append its metadata."""
    image = decode_image(image_bytes)
    face_count = validate_faces(image, enrollment=split == "enrollment")
    image_id = uuid.uuid4().hex
    suffix = Path(original_name).suffix.lower()
    target = build_dataset_path(category, identity, split, condition, suffix, image_id)
    relative_path = target.relative_to(ROOT).as_posix()

    rows = read_metadata_rows()
    if any(row["file_path"] == relative_path for row in rows):
        raise ValueError("The generated file path already exists in metadata.")
    if target.exists():
        raise ValueError("The generated file path already exists on disk.")

    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        target.write_bytes(image_bytes)
        rows.append(
            {
                "id": image_id,
                "file_path": relative_path,
                "identity": clean_path_segment(identity, "Identity"),
                "category": category,
                "split": split,
                "condition": condition if split == "test" else "normal",
                "expected_result": expected_result_for(category, split),
            }
        )
        write_metadata_rows(rows)
    except Exception:
        target.unlink(missing_ok=True)
        raise
    return target, face_count


def render_collector() -> None:
    """Render the standalone collection workflow."""
    st.set_page_config(
        page_title="N-ONE evaluation dataset collector",
        page_icon=":material/collections_bookmark:",
    )
    st.title("N-ONE evaluation dataset collector")
    st.caption("Collect real, labeled evaluation data without touching the live application.")

    with st.container(border=True):
        st.subheader("Sample details")
        identity = st.text_input("Identity", placeholder="For example: victim_01")
        category = st.selectbox("Category", CATEGORIES)
        split = st.segmented_control(
            "Dataset split", ("enrollment", "test"), default="test"
        )
        if split is None:
            split = "test"
        condition = "normal"
        if split == "test":
            condition = st.selectbox("Test condition", TEST_CONDITIONS)
        source = st.segmented_control(
            "Image source", ("Upload", "Camera"), default="Upload"
        )

        uploaded = None
        original_name = "camera_capture.jpg"
        if source == "Camera":
            uploaded = st.camera_input("Capture image")
        else:
            uploaded = st.file_uploader(
                "Upload image",
                type=sorted(suffix.removeprefix(".") for suffix in IMAGE_SUFFIXES),
            )
            if uploaded is not None:
                original_name = uploaded.name

        submitted = st.button(
            "Validate and save", type="primary", icon=":material/save:"
        )

    if submitted:
        if not identity.strip():
            st.error("Enter an identity before saving.")
            return
        if uploaded is None:
            st.error("Choose an image or capture one before saving.")
            return
        try:
            target, face_count = save_sample(
                uploaded.getvalue(), original_name, identity, category, split, condition
            )
        except Exception as error:
            st.error(f"Sample was not saved: {type(error).__name__}: {error}")
            return
        st.success(f"Saved {target.relative_to(ROOT).as_posix()} with {face_count} face(s).")
        st.info("Enrollment and test paths are separate; no registered-face files are copied.")

    rows = read_metadata_rows()
    st.caption(f"Recorded samples: {len(rows)}")
    if rows:
        st.dataframe(rows, width="stretch", hide_index=True)


if __name__ == "__main__":
    render_collector()