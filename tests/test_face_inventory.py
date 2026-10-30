import shutil
import time
from pathlib import Path
from uuid import uuid4

import numpy as np
import pandas as pd

import app


def test_profile_labels_support_new_and_legacy_prefixes() -> None:
    assert app.get_profile_category("Staff_Maharsh_kewat") == "Staff"
    assert app.get_profile_category("Victim_vivek_patel") == "Victim"
    assert app.get_profile_category("Member_ravendra") == "Staff"
    assert app.get_profile_category("Lost_vivek_patel") == "Victim"
    assert app.get_profile_name("Staff_Maharsh_kewat") == "Maharsh kewat"


def test_registered_inventory_counts_and_categories(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_face_inventory_{uuid4().hex}"
    registered_dir = test_dir / "registered_faces"
    registered_dir.mkdir(parents=True)
    try:
        for filename in ["Staff_alpha.jpg", "Victim_beta.png", "Member_legacy.jpeg", "notes.txt"]:
            (registered_dir / filename).touch()

        monkeypatch.setattr(app, "REG_DIR", registered_dir)
        inventory = app.get_registered_profiles_df()

        assert len(inventory) == 3
        assert inventory["category"].value_counts().to_dict() == {"Staff": 2, "Victim": 1}
        assert app.get_registered_profile_count() == 3
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_unknown_count_uses_unique_database_ids(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_face_inventory_{uuid4().hex}"
    unknown_dir = test_dir / "unknown_faces"
    unknown_dir.mkdir(parents=True)
    unknown_db = test_dir / "unknown_person_db.csv"
    try:
        (unknown_dir / "unknown_001.jpg").touch()
        (unknown_dir / "unknown_002.jpg").touch()
        pd.DataFrame({"unknown_id": ["unknown_001", "unknown_001", "unknown_002"]}).to_csv(
            unknown_db, index=False
        )

        monkeypatch.setattr(app, "UNKNOWN_DIR", unknown_dir)
        monkeypatch.setattr(app, "UNKNOWN_DB_PATH", unknown_db)

        assert app.get_unknown_face_count() == 2
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_clear_unknown_face_data_removes_photos_and_resets_tracking(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_clear_unknown_{uuid4().hex}"
    unknown_dir = test_dir / "unknown_faces"
    logs_dir = test_dir / "logs"
    unknown_dir.mkdir(parents=True)
    logs_dir.mkdir()
    unknown_db = test_dir / "unknown_person_db.csv"
    sighting_log = test_dir / "unknown_sighting_log.csv"
    audit_log = logs_dir / "system_audit_logs.csv"
    victim_log = logs_dir / "victim_sighting_log.csv"
    (unknown_dir / "unknown_001.jpg").touch()
    unknown_db.write_text("unknown_id\nunknown_001\n", encoding="utf-8")
    sighting_log.write_text("sighting_id\n1\n", encoding="utf-8")
    try:
        monkeypatch.setattr(app, "UNKNOWN_DIR", unknown_dir)
        monkeypatch.setattr(app, "UNKNOWN_DB_PATH", unknown_db)
        monkeypatch.setattr(app, "UNKNOWN_SIGHTING_LOG_PATH", sighting_log)
        monkeypatch.setattr(app, "CSV_LOG_PATH", audit_log)
        monkeypatch.setattr(app, "VICTIM_SIGHTING_LOG_PATH", victim_log)
        app.UNKNOWN_FACE_ENCODINGS[:] = [{"unknown_id": "unknown_001"}]

        app.clear_unknown_face_data()

        assert list(unknown_dir.iterdir()) == []
        assert app.UNKNOWN_FACE_ENCODINGS == []
        assert pd.read_csv(unknown_db).empty
        assert pd.read_csv(sighting_log).empty
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_known_face_cache_can_be_limited_to_one_victim(monkeypatch) -> None:
    monkeypatch.setattr(
        app,
        "KNOWN_FACE_ENCODINGS",
        [
            {"profile_id": "Staff_a", "name": "a", "role": "Staff", "encoding": [1.0, 0.0]},
            {"profile_id": "Victim_b", "name": "b", "role": "Victim", "encoding": [1.0, 0.0]},
        ],
    )

    match = app.find_face_in_known_cache(
        [1.0, 0.0], profile_id="Victim_b", role="Victim"
    )

    assert match is not None
    assert match["profile_id"] == "Victim_b"


def test_known_face_database_refresh_includes_all_saved_angles(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_known_refresh_{uuid4().hex}"
    registered_dir = test_dir / "registered_faces"
    registered_dir.mkdir(parents=True)

    class EmbeddingBackend:
        @staticmethod
        def represent(**kwargs):
            return [{"embedding": [1.0, 0.0]}]

    try:
        for angle in ("front", "left", "right", "up", "down"):
            (registered_dir / f"Victim_alpha__{angle}.jpg").touch()
        monkeypatch.setattr(app, "REG_DIR", registered_dir)
        monkeypatch.setattr(app, "DeepFace", EmbeddingBackend)

        app.load_known_face_encodings("Facenet", "opencv")

        assert {entry["angle"] for entry in app.KNOWN_FACE_ENCODINGS} == {
            "front", "left", "right", "up", "down"
        }
        assert all(entry["profile_id"] == "Victim_alpha" for entry in app.KNOWN_FACE_ENCODINGS)
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_known_face_cache_skips_unchanged_enrollment_images(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_known_cache_{uuid4().hex}"
    registered_dir = test_dir / "registered_faces"
    registered_dir.mkdir(parents=True)
    profile_image = registered_dir / "Staff_alpha__front.jpg"
    profile_image.touch()
    calls = []

    class EmbeddingBackend:
        @staticmethod
        def represent(**kwargs):
            calls.append(kwargs)
            return [{"embedding": [1.0, 0.0]}]

    try:
        monkeypatch.setattr(app, "REG_DIR", registered_dir)
        monkeypatch.setattr(app, "DeepFace", EmbeddingBackend)
        monkeypatch.setattr(app, "KNOWN_FACE_CACHE_SIGNATURE", None)
        app.KNOWN_FACE_ENCODINGS.clear()

        app.load_known_face_encodings("Facenet", "opencv")
        initial_call_count = len(calls)
        app.load_known_face_encodings("Facenet", "opencv")

        assert initial_call_count > 0
        assert len(calls) == initial_call_count
        assert len(app.KNOWN_FACE_ENCODINGS) == initial_call_count

        profile_image.write_bytes(b"updated enrollment")
        app.load_known_face_encodings("Facenet", "opencv")
        assert len(calls) == initial_call_count * 2
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_registered_face_crop_retries_with_full_image(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_registered_crop_{uuid4().hex}"
    test_dir.mkdir()
    profile_image = test_dir / "Victim_test__front.jpg"
    profile_image.touch()
    calls: list[dict] = []

    class CropAwareBackend:
        @staticmethod
        def represent(**kwargs):
            calls.append(kwargs)
            if kwargs.get("force_full_image"):
                return [{"embedding": [1.0, 0.0]}]
            return []

    monkeypatch.setattr(app, "DeepFace", CropAwareBackend)

    try:
        representations = app.represent_registered_face(
            profile_image, "Facenet", "opencv"
        )

        assert representations == [{"embedding": [1.0, 0.0]}]
        assert len(calls) == 2
        assert calls[1]["force_full_image"] is True
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_browser_camera_marks_unmatched_victim_face_with_green_box(monkeypatch) -> None:
    class LiveFaceBackend:
        @staticmethod
        def represent(**kwargs):
            return [
                {
                    "embedding": [0.0, 1.0],
                    "facial_area": {"x": 10, "y": 10, "w": 30, "h": 30},
                }
            ]

    monkeypatch.setattr(app, "DeepFace", LiveFaceBackend)
    monkeypatch.setattr(app, "KNOWN_FACE_ENCODINGS", [])
    frame = np.zeros((60, 60, 3), dtype=np.uint8)

    annotated = app.annotate_browser_frame(
        frame, "1. Lost Person Search", "Victim_test", "Facenet", "opencv", "cosine", 0.4
    )

    assert annotated[10, 10].tolist() == [0, 255, 0]


def test_browser_camera_rejects_invalid_fallback_victim_candidate(monkeypatch) -> None:
    class FalseDetectionBackend:
        @staticmethod
        def represent(**kwargs):
            return [
                {
                    "embedding": [1.0, 0.0],
                    "facial_area": {"x": 10, "y": 10, "w": 30, "h": 30},
                }
            ]

        @staticmethod
        def is_valid_face_region(*args):
            return False

    monkeypatch.setattr(app, "DeepFace", FalseDetectionBackend)
    monkeypatch.setattr(
        app,
        "KNOWN_FACE_ENCODINGS",
        [{"profile_id": "Victim_test", "role": "Victim", "encoding": [1.0, 0.0]}],
    )
    frame = np.zeros((60, 60, 3), dtype=np.uint8)

    annotated = app.annotate_browser_frame(
        frame, "1. Lost Person Search", "Victim_test", "Facenet", "opencv", "cosine", 0.4
    )

    assert annotated[10, 10].tolist() == [0, 0, 0]


def test_browser_camera_does_not_identify_victim_with_opencv_fallback(monkeypatch) -> None:
    class FallbackBackend:
        @staticmethod
        def represent(**kwargs):
            return [
                {
                    "embedding": [1.0, 0.0],
                    "facial_area": {"x": 10, "y": 10, "w": 30, "h": 30},
                }
            ]

        @staticmethod
        def is_valid_face_region(*args):
            return True

    monkeypatch.setattr(app, "DeepFace", FallbackBackend)
    monkeypatch.setattr(app, "DEEPFACE_IMPORT_ERROR", "TensorFlow is unavailable")
    monkeypatch.setattr(
        app,
        "KNOWN_FACE_ENCODINGS",
        [{"profile_id": "Victim_test", "role": "Victim", "name": "test", "encoding": [1.0, 0.0]}],
    )
    frame = np.zeros((60, 60, 3), dtype=np.uint8)

    annotated = app.annotate_browser_frame(
        frame, "1. Lost Person Search", "Victim_test", "Facenet", "opencv", "cosine", 0.4
    )

    # Green means detected but not identified; a false victim alert is red.
    assert annotated[10, 10].tolist() == [0, 255, 0]


def test_browser_camera_identifies_selected_victim_with_neural_runtime(monkeypatch) -> None:
    class NeuralBackend:
        @staticmethod
        def represent(**kwargs):
            return [
                {
                    "embedding": [1.0, 0.0],
                    "facial_area": {"x": 10, "y": 10, "w": 30, "h": 30},
                }
            ]

    monkeypatch.setattr(app, "DeepFace", NeuralBackend)
    monkeypatch.setattr(app, "DEEPFACE_IMPORT_ERROR", None)
    monkeypatch.setattr(
        app,
        "KNOWN_FACE_ENCODINGS",
        [{"profile_id": "Victim_test", "role": "Victim", "name": "test", "encoding": [1.0, 0.0]}],
    )
    frame = np.zeros((60, 60, 3), dtype=np.uint8)

    annotated = app.annotate_browser_frame(
        frame, "1. Lost Person Search", "Victim_test", "Facenet", "opencv", "cosine", 0.4
    )

    # Red is reserved for a verified selected-victim match.
    assert annotated[10, 10].tolist() == [0, 0, 255]


def test_process_frame_calls_represent_without_legacy_silent_argument(monkeypatch) -> None:
    class CurrentDeepFaceBackend:
        @staticmethod
        def represent(
            *,
            img_path,
            model_name,
            enforce_detection,
            detector_backend,
            align,
        ):
            return []

    monkeypatch.setattr(app, "DeepFace", CurrentDeepFaceBackend)
    monkeypatch.setattr(
        app, "get_runtime_face_settings", lambda: ("Facenet512", "retinaface", "cosine")
    )
    monkeypatch.setattr(app, "record_detection_result", lambda *args, **kwargs: None)

    _, summary = app.process_frame(
        np.zeros((60, 60, 3), dtype=np.uint8), "1. Lost Person Search"
    )

    assert summary == "No faces detected in frame."


def test_cpu_saver_uses_smaller_frames_and_throttles_live_inference(monkeypatch) -> None:
    monkeypatch.setattr(
        app,
        "LAST_LOCAL_FACE_INFERENCE_TIME",
        time.monotonic(),
    )
    monkeypatch.setattr(
        app.st,
        "session_state",
        {
            "cpu_saver_mode": True,
            "streaming": True,
            "selected_model": "Facenet512",
            "selected_backend": "opencv",
            "selected_metric": "cosine",
        },
    )

    assert app.get_processing_max_width() == app.CPU_SAVER_PROCESSING_MAX_WIDTH
    assert app.get_runtime_face_settings()[1] == "opencv"
    assert app.should_skip_local_face_inference() is True


def test_unknown_gallery_resolves_current_image_path(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_face_inventory_{uuid4().hex}"
    unknown_dir = test_dir / "unknown_faces"
    unknown_dir.mkdir(parents=True)
    image_path = unknown_dir / "unknown_001.jpg"
    image_path.touch()
    unknown_db = test_dir / "unknown_person_db.csv"
    try:
        pd.DataFrame(
            {
                "unknown_id": ["unknown_001"],
                "image_path": ["old/path/unknown_001.jpg"],
                "first_seen_timestamp": ["2026-08-09 10:00:00"],
                "last_seen_timestamp": ["2026-08-09 11:00:00"],
                "last_known_location": ["Gate 1"],
                "assigned_name": [""],
            }
        ).to_csv(unknown_db, index=False)

        monkeypatch.setattr(app, "UNKNOWN_DIR", unknown_dir)
        monkeypatch.setattr(app, "UNKNOWN_DB_PATH", unknown_db)
        gallery = app.get_unknown_profiles_df()

        assert len(gallery) == 1
        assert Path(gallery.iloc[0]["image_path"]) == image_path
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_unknown_can_be_registered_as_staff(monkeypatch) -> None:
    test_dir = Path(__file__).parent / f"_unknown_to_staff_{uuid4().hex}"
    registered_dir = test_dir / "registered_faces"
    unknown_dir = test_dir / "unknown_faces"
    registered_dir.mkdir(parents=True)
    unknown_dir.mkdir()
    source_path = unknown_dir / "unknown_001.jpg"
    source_path.write_bytes(b"face image")
    unknown_db = test_dir / "unknown_person_db.csv"
    details_path = test_dir / "victim_profile_details.csv"
    pd.DataFrame(
        {
            "unknown_id": ["unknown_001"],
            "image_path": [str(source_path)],
            "assigned_name": [""],
        }
    ).to_csv(unknown_db, index=False)
    events = []
    try:
        monkeypatch.setattr(app, "REG_DIR", registered_dir)
        monkeypatch.setattr(app, "UNKNOWN_DB_PATH", unknown_db)
        monkeypatch.setattr(app, "VICTIM_PROFILE_DETAILS_PATH", details_path)
        monkeypatch.setattr(app, "UNKNOWN_DIR", unknown_dir)
        monkeypatch.setattr(
            app,
            "get_unknown_profiles_df",
            lambda: pd.DataFrame(
                [{"unknown_id": "unknown_001", "image_path": str(source_path)}]
            ),
        )
        monkeypatch.setattr(app.st, "session_state", {"role": "Administrator"})
        monkeypatch.setattr(app, "log_event", lambda **event: events.append(event))
        monkeypatch.setattr(app, "UNKNOWN_FACE_ENCODINGS", [])

        registered, message = app.convert_unknown_to_victim(
            unknown_id="unknown_001",
            name="Ravendra Rao",
            confirmed=True,
            profile_category="Staff",
        )

        profile_path = registered_dir / "Staff_Ravendra_Rao_unknown_001__front.jpg"
        assert registered
        assert "Staff" in message
        assert profile_path.read_bytes() == b"face image"
        assert pd.read_csv(unknown_db).iloc[0]["assigned_name"] == "Ravendra Rao"
        assert not details_path.exists()
        assert events[0]["role"] == "Staff"
        assert events[0]["event_type"] == "Unknown Converted to Staff"
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
