import hmac
import os
import shutil
import tempfile
import threading
import time
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit.errors import StreamlitSecretNotFoundError

try:
    import av
    from streamlit_webrtc import VideoProcessorBase, WebRtcMode, webrtc_streamer
except ImportError:  # Keep the dashboard usable until optional WebRTC deps are installed.
    av = None
    VideoProcessorBase = None
    WebRtcMode = None
    webrtc_streamer = None

from deepface_adapter import DEEPFACE_IMPORT_ERROR, DeepFace


APP_ROOT = Path(__file__).resolve().parent
LOGO_PATH = APP_ROOT / "assets" / "n_one_logo.png"


AUTH_SECRET_NAMES = (
    "ADMIN_USERNAME",
    "ADMIN_PASSWORD",
    "OPERATOR_USERNAME",
    "OPERATOR_PASSWORD",
)
MAX_LOGIN_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 60


def _read_secret(name: str) -> str | None:
    """Read a secret from the process environment or Streamlit Secrets."""
    environment_value = os.getenv(name)
    if environment_value is not None:
        return environment_value

    try:
        secret_value = st.secrets.get(name)
    except StreamlitSecretNotFoundError:
        return None

    return None if secret_value is None else str(secret_value)


def load_auth_credentials() -> dict[str, str]:
    """Load Admin and Operator credentials and fail closed when any are missing."""
    credentials = {name: _read_secret(name) for name in AUTH_SECRET_NAMES}
    missing = [name for name, value in credentials.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required authentication secrets: " + ", ".join(missing)
        )
    return {name: value for name, value in credentials.items() if value is not None}

st.set_page_config(
    page_title="N-ONE : NO ONE ESCAPES",
    page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else "🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# `st.set_page_config` must be the first Streamlit command in the script.
# Show the fallback notice only after page configuration so a missing optional
# TensorFlow/DeepFace runtime cannot prevent the dashboard from rendering.
if DEEPFACE_IMPORT_ERROR:
    st.warning(
        "DeepFace runtime is not fully available in this environment. "
        f"The app will continue with a safe fallback. Error: {DEEPFACE_IMPORT_ERROR}"
    )

st.markdown(
    """
    <style>
    .main { background: linear-gradient(135deg, #050816 0%, #111827 100%); color: #f9fafb; }
    .stSidebar { background-color: #0f172a; }
    div.stButton > button:first-child {
        background-color: #22c55e;
        color: white;
        border: none;
        font-weight: 600;
        border-radius: 8px;
        transition: transform 150ms ease, filter 150ms ease, box-shadow 150ms ease;
    }
    div.stButton > button:hover {
        filter: brightness(1.08);
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(34, 197, 94, 0.28);
    }
    div.stButton > button:active {
        transform: translateY(1px) scale(0.98);
        box-shadow: none;
    }
    .surveillance-state {
        display: flex;
        align-items: center;
        gap: 0.55rem;
        width: fit-content;
        margin: 0.6rem 0;
        padding: 0.5rem 0.8rem;
        border-radius: 999px;
        font-weight: 650;
    }
    .surveillance-state.live {
        color: #bbf7d0;
        background: rgba(22, 163, 74, 0.18);
        border: 1px solid rgba(74, 222, 128, 0.55);
    }
    .surveillance-state.offline {
        color: #cbd5e1;
        background: rgba(148, 163, 184, 0.12);
        border: 1px solid rgba(148, 163, 184, 0.35);
    }
    .status-dot {
        width: 0.6rem;
        height: 0.6rem;
        border-radius: 50%;
        background: currentColor;
    }
    .live .status-dot {
        animation: status-pulse 1.15s ease-in-out infinite;
    }
    @keyframes status-pulse {
        0%, 100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.75); }
        50% { transform: scale(1.18); box-shadow: 0 0 0 0.55rem rgba(74, 222, 128, 0); }
    }

    /* ---------- N-ONE UI components ---------- */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    .status-chip.live { background: rgba(34, 197, 94, 0.16); color: #bbf7d0; border-color: rgba(34, 197, 94, 0.45); }
    .status-chip.searching { background: rgba(37, 99, 235, 0.16); color: #bfdbfe; border-color: rgba(37, 99, 235, 0.45); }
    .status-chip.alert { background: rgba(239, 68, 68, 0.16); color: #fecaca; border-color: rgba(239, 68, 68, 0.45); }
    .status-chip.idle { background: rgba(100, 116, 139, 0.14); color: #cbd5e1; border-color: rgba(100, 116, 139, 0.4); }
    .status-chip.threat { background: rgba(234, 88, 12, 0.16); color: #ffedd5; border-color: rgba(234, 88, 12, 0.45); }
    .status-chip .chip-dot {
        width: 8px; height: 8px; border-radius: 50%; background: currentColor;
    }
    .status-chip.live .chip-dot { animation: status-pulse 1.2s ease-in-out infinite; }

    .metric-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px 14px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-card .label {
        font-size: 0.8rem; color: #94a3b8; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 6px;
    }
    .metric-card .value {
        font-size: 1.75rem; font-weight: 700; color: #f8fafc; line-height: 1.1;
    }
    .metric-card .delta {
        font-size: 0.85rem; margin-top: 4px;
    }
    .metric-card .delta.ok { color: #22c55e; }
    .metric-card .delta.warn { color: #f59e0b; }
    .metric-card .delta.bad { color: #ef4444; }

    .camera-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 12px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .camera-card .name { font-weight: 600; color: #f8fafc; }
    .camera-card .health { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
    .camera-card .health.ok { color: #22c55e; }
    .camera-card .health.warn { color: #f59e0b; }
    .camera-card .health.bad { color: #ef4444; }
    .camera-card .meta { font-size: 0.78rem; color: #94a3b8; }

    .panel-card {
        background: #0b0f19;
        border: 1px solid #1f2937;
        border-radius: 10px;
        padding: 14px;
    }

    .video-feed-wrapper {
        border: 1px solid #334155;
        border-radius: 12px;
        overflow: hidden;
        background: #000;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }

    .overlay-badge {
        position: absolute; top: 10px; left: 10px;
        padding: 4px 8px; border-radius: 6px; font-size: 0.8rem;
        font-weight: 600; color: white; background: rgba(0,0,0,0.55);
        backdrop-filter: blur(4px);
    }
    .overlay-badge.live { background: rgba(22, 163, 74, 0.85); }
    .overlay-badge.alert { background: rgba(239, 68, 68, 0.85); }

    @media (prefers-reduced-motion: reduce) {
        div.stButton > button:first-child, .live .status-dot, .status-chip.live .chip-dot { animation: none; transition: none; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Constants and Paths ---
ROOT_DIR = APP_ROOT
REG_DIR = ROOT_DIR / "registered_faces"
LOG_DIR = ROOT_DIR / "detection_logs"
UNKNOWN_DIR = ROOT_DIR / "unknown_faces"
CSV_LOG_PATH = LOG_DIR / "system_audit_logs.csv"
TEMP_VIDEO_PATH = ROOT_DIR / "temp_video_upload.mp4"
UNKNOWN_DB_PATH = ROOT_DIR / "unknown_person_db.csv"
UNKNOWN_SIGHTING_LOG_PATH = ROOT_DIR / "unknown_sighting_log.csv"
VICTIM_SIGHTING_LOG_PATH = LOG_DIR / "victim_sighting_log.csv"
VICTIM_PROFILE_DETAILS_PATH = ROOT_DIR / "victim_profile_details.csv"
CASE_RECORDS_PATH = LOG_DIR / "investigation_cases.csv"
CASE_ACTIVITY_LOG_PATH = LOG_DIR / "case_activity_log.csv"

# DeepFace Model Configuration
DEEPFACE_MODELS = ["VGG-Face", "Facenet", "Facenet512", "OpenFace", "DeepFace", "ArcFace", "SFace"]
DEEPFACE_BACKENDS = ["opencv", "mtcnn", "retinaface", "mediapipe", "dlib", "ssd", "yolov8n", "yunet"]
DEEPFACE_METRICS = ["cosine", "euclidean", "euclidean_l2"]
ATTRIBUTE_TASKS = ["age", "gender", "emotion", "race"]
CASE_STATUS_OPTIONS = ["Open", "Verified Lead", "Resolved", "Closed"]
CASE_PRIORITY_OPTIONS = ["Low", "Medium", "High", "Critical"]
CASE_RECORD_COLUMNS = [
    "case_id",
    "profile_id",
    "subject_name",
    "status",
    "priority",
    "opened_at",
    "last_updated_at",
    "last_seen_location",
    "assigned_to",
    "case_contact",
    "notes",
]
CASE_ACTIVITY_COLUMNS = [
    "activity_id",
    "case_id",
    "timestamp",
    "event_type",
    "location",
    "actor",
    "details",
]

# Default Configuration
DEEPFACE_MODEL = "Facenet512"
# RetinaFace is accurate but expensive on a CPU-only Windows TensorFlow build.
# OpenCV is the responsive default; RetinaFace remains available when needed.
DEEPFACE_BACKEND = "opencv"
DEEPFACE_METRIC = "cosine"
COSINE_THRESHOLD = 0.35
PROFILE_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png"}
ENROLLMENT_ANGLES = ("front", "left", "right", "up", "down")
ENROLLMENT_INSTRUCTIONS = {
    "front": "Look straight at the camera. Keep your face relaxed.",
    "left": "Slowly turn your face to the LEFT and hold still.",
    "right": "Slowly turn your face to the RIGHT and hold still.",
    "up": "Tilt your face slightly UP and hold still.",
    "down": "Tilt your face slightly DOWN and hold still.",
}

# --- In-memory Cache ---
KNOWN_FACE_ENCODINGS = []
KNOWN_FACE_CACHE_SIGNATURE: tuple[object, ...] | None = None
UNKNOWN_FACE_ENCODINGS: list[dict] = []
UNKNOWN_FACE_CACHE_SETTINGS: tuple[str, str] | None = None
UNKNOWN_FACE_CACHE_VERSION = 0
UNKNOWN_FACE_CACHE_BUILT_VERSION = -1
UNKNOWN_SIGHTING_WRITE_INTERVAL_SECONDS = 2.0
UNKNOWN_SIGHTING_LAST_WRITE: dict[tuple[str, str], float] = {}
UNKNOWN_SIGHTING_MEMORY: dict[str, dict[str, str]] = {}
THREAT_LOG_INTERVAL_SECONDS = 2.0
LAST_THREAT_LOG_TIME = 0.0
# Keep more detail for small/distant faces in recorded footage.  The fallback
# detector can now handle profile faces and will retry a small frame at a
# higher scale when necessary.
PROCESSING_MAX_WIDTH = 1280
CPU_SAVER_PROCESSING_MAX_WIDTH = 640
CPU_SAVER_INFERENCE_INTERVAL_SECONDS = 0.40
CPU_SAVER_DISPLAY_INTERVAL_SECONDS = 0.06
LAST_LOCAL_FACE_INFERENCE_TIME = 0.0


def reliable_face_matching_available() -> bool:
    """Return whether the neural recognition runtime is available.

    The OpenCV/HOG fallback is useful for detecting faces, but its handcrafted
    features cannot safely identify a person. Treating its nearest neighbour
    as a known person caused unrelated faces to be labelled as registered
    Staff or the selected Victim.
    """
    return DEEPFACE_IMPORT_ERROR is None


def invalidate_unknown_face_cache() -> None:
    """Mark the in-memory unknown-face index stale after a new registration."""
    global UNKNOWN_FACE_CACHE_VERSION
    UNKNOWN_FACE_CACHE_VERSION += 1


def _represent_saved_unknown(
    image_path: Path,
    model_name: str,
    detector_backend: str,
) -> list[dict]:
    """Represent a saved unknown, including cropped images without context."""
    try:
        representations = DeepFace.represent(
            img_path=str(image_path),
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=False,
            align=True,
        )
        if representations:
            return representations
    except Exception:
        pass

    # Unknown images are face-only crops. The OpenCV fallback supports using
    # the whole crop when its Haar detector cannot find a second face box.
    try:
        representations = DeepFace.represent(
            img_path=str(image_path),
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=False,
            allow_full_image=True,
            align=True,
        )
        return representations if representations else []
    except Exception:
        return []


def ensure_unknown_face_cache(model_name: str, detector_backend: str) -> None:
    """Build the unknown-face index once instead of scanning disk every frame."""
    global UNKNOWN_FACE_CACHE_SETTINGS, UNKNOWN_FACE_CACHE_BUILT_VERSION

    settings = (model_name, detector_backend)
    if (
        UNKNOWN_FACE_CACHE_SETTINGS == settings
        and UNKNOWN_FACE_CACHE_BUILT_VERSION == UNKNOWN_FACE_CACHE_VERSION
    ):
        return

    UNKNOWN_FACE_ENCODINGS.clear()
    converted_unknown_ids: set[str] = set()
    try:
        unknown_rows = pd.read_csv(UNKNOWN_DB_PATH)
        if {"unknown_id", "assigned_name"}.issubset(unknown_rows.columns):
            converted_unknown_ids = set(
                unknown_rows.loc[
                    unknown_rows["assigned_name"].fillna("").astype(str).str.strip() != "",
                    "unknown_id",
                ].astype(str)
            )
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        pass

    if UNKNOWN_DIR.exists():
        for image_path in sorted(UNKNOWN_DIR.iterdir()):
            if not image_path.is_file() or image_path.suffix.lower() not in PROFILE_IMAGE_SUFFIXES:
                continue
            if image_path.stem in converted_unknown_ids:
                continue
            representations = _represent_saved_unknown(
                image_path, model_name, detector_backend
            )
            if representations and representations[0].get("embedding") is not None:
                UNKNOWN_FACE_ENCODINGS.append(
                    {
                        "unknown_id": image_path.stem,
                        "image_path": image_path,
                        "encoding": representations[0]["embedding"],
                    }
                )

    UNKNOWN_FACE_CACHE_SETTINGS = settings
    UNKNOWN_FACE_CACHE_BUILT_VERSION = UNKNOWN_FACE_CACHE_VERSION


def add_unknown_face_to_cache(
    unknown_id: str,
    face_encoding: list,
    image_path: Path,
    model_name: str,
    detector_backend: str,
) -> None:
    """Add the current frame's embedding without rebuilding the whole index."""
    ensure_unknown_face_cache(model_name, detector_backend)
    for entry in UNKNOWN_FACE_ENCODINGS:
        if entry.get("unknown_id") == unknown_id:
            entry["encoding"] = face_encoding
            entry["image_path"] = image_path
            return
    UNKNOWN_FACE_ENCODINGS.append(
        {
            "unknown_id": unknown_id,
            "image_path": image_path,
            "encoding": face_encoding,
        }
    )


def find_face_in_unknown_cache(
    face_encoding: list,
    metric: str,
    model_name: str,
    detector_backend: str,
) -> dict | None:
    """Return the closest cached unknown within the selected metric threshold."""
    ensure_unknown_face_cache(model_name, detector_backend)
    thresholds = {"cosine": 0.4, "euclidean": 0.55, "euclidean_l2": 0.75}
    threshold = thresholds.get(metric, 0.4)
    best_match = None
    best_distance = float("inf")

    for entry in UNKNOWN_FACE_ENCODINGS:
        try:
            probe = np.asarray(face_encoding, dtype=np.float64)
            reference = np.asarray(entry["encoding"], dtype=np.float64)
            if probe.shape != reference.shape:
                continue
            distance = calculate_face_distance(face_encoding, entry["encoding"], metric)
        except (TypeError, ValueError):
            continue

        if np.isfinite(distance) and distance < best_distance:
            best_match = entry
            best_distance = distance

    if best_match is None or best_distance > threshold:
        return None
    return {**best_match, "distance": best_distance}


def initialize_directories() -> None:
    """Create necessary directories if they don't exist."""
    REG_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)
    UNKNOWN_DIR.mkdir(exist_ok=True)


def initialize_log_files() -> None:
    """Create log files with headers if they don't exist."""
    if not CSV_LOG_PATH.exists() or CSV_LOG_PATH.stat().st_size == 0:
        pd.DataFrame(columns=["Timestamp", "Mode", "Subject_ID", "Role", "Event_Type", "Details"]).to_csv(
            CSV_LOG_PATH, index=False
        )
    if not UNKNOWN_DB_PATH.exists() or UNKNOWN_DB_PATH.stat().st_size == 0:
        pd.DataFrame(
            columns=["unknown_id", "image_path", "first_seen_timestamp", "last_seen_timestamp", "last_known_location", "assigned_name"]
        ).to_csv(UNKNOWN_DB_PATH, index=False)
    if not UNKNOWN_SIGHTING_LOG_PATH.exists() or UNKNOWN_SIGHTING_LOG_PATH.stat().st_size == 0:
        pd.DataFrame(columns=["sighting_id", "unknown_id", "timestamp", "location"]).to_csv(
            UNKNOWN_SIGHTING_LOG_PATH, index=False
        )
    if not VICTIM_SIGHTING_LOG_PATH.exists() or VICTIM_SIGHTING_LOG_PATH.stat().st_size == 0:
        pd.DataFrame(columns=["profile_id", "name", "timestamp", "location"]).to_csv(
            VICTIM_SIGHTING_LOG_PATH, index=False
        )
    if not CASE_RECORDS_PATH.exists() or CASE_RECORDS_PATH.stat().st_size == 0:
        pd.DataFrame(columns=CASE_RECORD_COLUMNS).to_csv(CASE_RECORDS_PATH, index=False)
    if not CASE_ACTIVITY_LOG_PATH.exists() or CASE_ACTIVITY_LOG_PATH.stat().st_size == 0:
        pd.DataFrame(columns=CASE_ACTIVITY_COLUMNS).to_csv(
            CASE_ACTIVITY_LOG_PATH, index=False
        )


def log_event(mode: str, subject_id: str, role: str, event_type: str, details: str = "") -> None:
    """Logs a single surveillance event to the main audit CSV."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    new_log_entry = pd.DataFrame(
        [[timestamp, mode, subject_id, role, event_type, details]],
        columns=["Timestamp", "Mode", "Subject_ID", "Role", "Event_Type", "Details"],
    )
    new_log_entry.to_csv(CSV_LOG_PATH, mode="a", header=False, index=False)
    st.session_state.last_logged_event = f"{timestamp} - {event_type}: {subject_id}"


def get_next_unknown_id() -> str:
    """Generates the next sequential ID for a new unknown person."""
    if not UNKNOWN_DB_PATH.exists() or pd.read_csv(UNKNOWN_DB_PATH).empty:
        return "unknown_001"
    db_df = pd.read_csv(UNKNOWN_DB_PATH)
    if db_df.empty:
        return "unknown_001"
    last_id = db_df["unknown_id"].max()
    if not isinstance(last_id, str) or not last_id.startswith("unknown_"):
        return "unknown_001"
    last_num = int(last_id.split("_")[-1])
    return f"unknown_{last_num + 1:03d}"


def get_profile_category(profile_stem: str) -> str:
    """Normalize current and legacy profile prefixes to the dashboard labels."""
    base_stem = profile_stem.split("__", 1)[0]
    prefix = base_stem.split("_", 1)[0].lower()
    return "Victim" if prefix in {"victim", "lost"} else "Staff"


VICTIM_PROFILE_DETAIL_COLUMNS = [
    "profile_id",
    "source_unknown_id",
    "name",
    "approximate_age",
    "description",
    "last_known_area",
    "contact",
    "notes",
    "registered_at",
]


def get_victim_profile_details(profile_id: str | None = None):
    """Load admin-entered case details for converted Victim profiles."""
    try:
        details = pd.read_csv(VICTIM_PROFILE_DETAILS_PATH).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        details = pd.DataFrame(columns=VICTIM_PROFILE_DETAIL_COLUMNS)

    if profile_id is None:
        return details
    if "profile_id" not in details.columns:
        return {}
    matches = details[details["profile_id"].astype(str) == str(profile_id)]
    return matches.iloc[-1].to_dict() if not matches.empty else {}


def get_profile_name(profile_stem: str) -> str:
    """Return a readable profile name from a stored filename."""
    details = get_victim_profile_details(profile_stem)
    if details.get("name"):
        return str(details["name"])
    base_stem = profile_stem.split("__", 1)[0]
    _, separator, name = base_stem.partition("_")
    return (name if separator else base_stem).replace("_", " ")


def get_profile_id(profile_stem: str) -> str:
    """Return the shared ID used by all angle images in one profile."""
    return profile_stem.split("__", 1)[0]


def get_profile_angle(profile_stem: str) -> str:
    """Return an angle suffix, or front for legacy single-photo profiles."""
    return profile_stem.split("__", 1)[1] if "__" in profile_stem else "front"


def get_profile_angle_paths(profile_id: str) -> dict[str, Path]:
    """Return all saved angle images belonging to a profile."""
    angle_paths: dict[str, Path] = {}
    if not REG_DIR.exists():
        return angle_paths
    for image_path in REG_DIR.iterdir():
        if not image_path.is_file() or image_path.suffix.lower() not in PROFILE_IMAGE_SUFFIXES:
            continue
        if get_profile_id(image_path.stem) != profile_id:
            continue
        angle = get_profile_angle(image_path.stem)
        angle_paths.setdefault(angle, image_path)
    return angle_paths


def get_registered_profiles_df() -> pd.DataFrame:
    """Build the registered-face inventory used by both authenticated roles."""
    profiles_by_id: dict[str, dict] = {}
    for image_path in REG_DIR.iterdir() if REG_DIR.exists() else []:
        if not image_path.is_file() or image_path.suffix.lower() not in PROFILE_IMAGE_SUFFIXES:
            continue
        profile_id = get_profile_id(image_path.stem)
        angle = get_profile_angle(image_path.stem)
        current = profiles_by_id.get(profile_id)
        if current is None or (angle == "front" and current["angle"] != "front"):
            profiles_by_id[profile_id] = {
                "profile_id": profile_id,
                "name": get_profile_name(profile_id),
                "category": get_profile_category(profile_id),
                "file_name": image_path.name,
                "image_path": str(image_path),
                "angle": angle,
            }

    profiles = [
        {key: value for key, value in record.items() if key != "angle"}
        for record in profiles_by_id.values()
    ]

    return pd.DataFrame(
        profiles,
        columns=["profile_id", "name", "category", "file_name", "image_path"],
    ).sort_values(["category", "name"], ignore_index=True)


def get_registered_profile_count() -> int:
    """Return the number of saved profiles visible to the dashboard."""
    return len(get_registered_profiles_df())


def get_unknown_face_count() -> int:
    """Return the number of unknown faces that still have a saved photo."""
    return len(get_unknown_profiles_df())


def get_unknown_profiles_df() -> pd.DataFrame:
    """Return unknown profiles whose saved photo is actually available."""
    columns = [
        "unknown_id",
        "image_path",
        "first_seen_timestamp",
        "last_seen_timestamp",
        "last_known_location",
        "assigned_name",
    ]
    records = []
    try:
        unknown_df = pd.read_csv(UNKNOWN_DB_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        unknown_df = pd.DataFrame(columns=columns)

    known_ids: set[str] = set()
    if "unknown_id" in unknown_df.columns:
        for _, row in unknown_df.drop_duplicates("unknown_id").iterrows():
            unknown_id = str(row.get("unknown_id", ""))
            if not unknown_id or unknown_id == "nan":
                continue
            known_ids.add(unknown_id)
            assigned_name = str(row.get("assigned_name", "")).strip()
            if assigned_name and assigned_name.lower() != "nan":
                # Keep the source photo in the audit archive, but show the
                # converted person in the Victim inventory instead.
                continue

            # Prefer the current workspace location. Stored absolute paths can
            # point to an older machine, deployment, or deleted photo.
            image_candidates = [UNKNOWN_DIR / f"{unknown_id}.jpg"]
            stored_path = str(row.get("image_path", ""))
            if stored_path and stored_path != "nan":
                stored_candidate = Path(stored_path)
                image_candidates.append(
                    stored_candidate
                    if stored_candidate.is_absolute()
                    else ROOT_DIR / stored_candidate
                )
            image_path = next(
                (candidate for candidate in image_candidates if candidate.is_file()),
                None,
            )
            if image_path is None:
                # Keep stale database rows out of the photo selector. Their
                # metadata remains in the CSV for audit/history purposes.
                continue

            records.append(
                {
                    "unknown_id": unknown_id,
                    "image_path": str(image_path),
                    "first_seen_timestamp": str(row.get("first_seen_timestamp", "")),
                    "last_seen_timestamp": str(row.get("last_seen_timestamp", "")),
                    "last_known_location": str(row.get("last_known_location", "")),
                    "assigned_name": str(row.get("assigned_name", "")),
                }
            )

    # Also show photos created before their database row was written, or rows
    # from a manually restored unknown_faces directory.
    if UNKNOWN_DIR.exists():
        for image_path in sorted(UNKNOWN_DIR.iterdir()):
            if (
                image_path.is_file()
                and image_path.suffix.lower() in PROFILE_IMAGE_SUFFIXES
                and image_path.stem not in known_ids
            ):
                records.append(
                    {
                        "unknown_id": image_path.stem,
                        "image_path": str(image_path),
                        "first_seen_timestamp": "",
                        "last_seen_timestamp": "",
                        "last_known_location": "",
                        "assigned_name": "",
                    }
                )

    return pd.DataFrame(records, columns=columns).sort_values(
        "unknown_id", ignore_index=True
    )


def is_victim_search_mode(mode: str) -> bool:
    """Return whether the selected mode searches for one victim target only."""
    return mode.startswith("1.")


def is_member_attendance_mode(mode: str) -> bool:
    """Return whether registered profiles should be prioritized for attendance."""
    return mode.startswith("2.")


def record_victim_sighting(profile_id: str, name: str, location: str) -> bool:
    """Persist a victim sighting, throttling duplicate frames at one camera."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        sighting_df = pd.read_csv(VICTIM_SIGHTING_LOG_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        sighting_df = pd.DataFrame(
            columns=["profile_id", "name", "timestamp", "location"]
        )

    matches = sighting_df[sighting_df["profile_id"].astype(str) == str(profile_id)]
    if not matches.empty:
        last = matches.sort_values("timestamp").iloc[-1]
        last_timestamp_value = last.get("timestamp")
        last_timestamp = (
            pd.to_datetime(str(last_timestamp_value), errors="coerce")
            if last_timestamp_value is not None
            else pd.NaT
        )
        current_timestamp = pd.to_datetime(timestamp)
        if (
            str(last.get("location", "")) == location
            and not pd.isna(last_timestamp)
            and (current_timestamp - last_timestamp).total_seconds() < 60
        ):
            return False

    write_header = not VICTIM_SIGHTING_LOG_PATH.exists() or VICTIM_SIGHTING_LOG_PATH.stat().st_size == 0
    pd.DataFrame(
        [[profile_id, name, timestamp, location]],
        columns=["profile_id", "name", "timestamp", "location"],
    ).to_csv(VICTIM_SIGHTING_LOG_PATH, mode="a", header=write_header, index=False)
    return True


def get_victim_sighting_history(profile_id: str = "") -> pd.DataFrame:
    """Return the latest sighting for each location for a victim profile."""
    columns = ["profile_id", "name", "timestamp", "location"]
    try:
        sighting_df = pd.read_csv(VICTIM_SIGHTING_LOG_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=columns)

    if profile_id:
        sighting_df = sighting_df[
            sighting_df["profile_id"].astype(str) == str(profile_id)
        ]
    if sighting_df.empty:
        return pd.DataFrame(columns=columns)

    return (
        sighting_df.sort_values("timestamp", ascending=False)
        .drop_duplicates("location", keep="first")
        .reset_index(drop=True)
    )


def get_runtime_face_settings() -> tuple[str, str, str]:
    """Return the face settings selected in the sidebar, with safe defaults."""
    return (
        str(st.session_state.get("selected_model", DEEPFACE_MODEL)),
        str(st.session_state.get("selected_backend", DEEPFACE_BACKEND)),
        str(st.session_state.get("selected_metric", DEEPFACE_METRIC)),
    )


def cpu_saver_enabled() -> bool:
    """Return whether live recognition should favor responsiveness over FPS."""
    return bool(st.session_state.get("cpu_saver_mode", True))


def get_processing_max_width() -> int:
    """Use a smaller inference image in the default CPU-saving profile."""
    return (
        CPU_SAVER_PROCESSING_MAX_WIDTH
        if cpu_saver_enabled()
        else PROCESSING_MAX_WIDTH
    )


def should_skip_local_face_inference() -> bool:
    """Throttle only active local camera recognition, never one-off operations."""
    global LAST_LOCAL_FACE_INFERENCE_TIME
    if not (
        cpu_saver_enabled()
        and st.session_state.get("streaming", False)
    ):
        return False
    now = time.monotonic()
    if now - LAST_LOCAL_FACE_INFERENCE_TIME < CPU_SAVER_INFERENCE_INTERVAL_SECONDS:
        return True
    LAST_LOCAL_FACE_INFERENCE_TIME = now
    return False


def represent_registered_face(
    image_path: Path,
    model_name: str,
    detector_backend: str,
) -> list[dict]:
    """Create an embedding for a saved face-only enrollment image.

    Enrollment saves a tight face crop.  Such an image does not always have
    enough context for a detector to find a face again, particularly when the
    OpenCV/HOG fallback is active.  Retry with the whole crop so registered
    Victim profiles never enter the known-face cache with a missing embedding.
    """
    common_args = {
        "img_path": str(image_path),
        "model_name": model_name,
        "detector_backend": detector_backend,
        "enforce_detection": False,
        "align": True,
    }
    representations: list[dict] = []
    try:
        representations = DeepFace.represent(**common_args) or []
    except Exception:
        pass

    # The bundled OpenCV fallback accepts this extra argument and generates an
    # embedding from the whole enrollment crop.  A full DeepFace installation
    # may not support it, in which case its detector-based result above is
    # retained unchanged.
    try:
        crop_representation = DeepFace.represent(
            **common_args, allow_full_image=True, force_full_image=True
        ) or []
        return representations + crop_representation
    except Exception:
        return representations


def get_known_face_cache_signature(
    model_name: str, detector_backend: str
) -> tuple[object, ...]:
    """Return a cheap fingerprint for enrolled images and their display metadata."""
    profile_files = []
    if REG_DIR.exists():
        for image_path in sorted(REG_DIR.glob("*.*")):
            if image_path.suffix.lower() not in PROFILE_IMAGE_SUFFIXES:
                continue
            try:
                stat = image_path.stat()
            except OSError:
                continue
            profile_files.append((image_path.name, stat.st_mtime_ns, stat.st_size))

    victim_details = None
    try:
        stat = VICTIM_PROFILE_DETAILS_PATH.stat()
        victim_details = (stat.st_mtime_ns, stat.st_size)
    except OSError:
        pass
    return (model_name, detector_backend, tuple(profile_files), victim_details)


def invalidate_known_face_cache() -> None:
    """Force the next run to rebuild known embeddings after profile changes."""
    global KNOWN_FACE_CACHE_SIGNATURE
    KNOWN_FACE_ENCODINGS.clear()
    KNOWN_FACE_CACHE_SIGNATURE = None


def load_known_face_encodings(
    model_name: str = DEEPFACE_MODEL,
    detector_backend: str = DEEPFACE_BACKEND,
) -> None:
    """Refresh embeddings only when enrolled profiles or settings change."""
    global KNOWN_FACE_CACHE_SIGNATURE
    if DeepFace is None:
        return

    signature = get_known_face_cache_signature(model_name, detector_backend)
    if signature == KNOWN_FACE_CACHE_SIGNATURE:
        return

    KNOWN_FACE_ENCODINGS.clear()
    for img_path in REG_DIR.glob("*.*"):
        if img_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue

        profile_id = get_profile_id(img_path.stem)
        name = get_profile_name(profile_id)
        role = get_profile_category(profile_id)
        try:
            embedding_obj = represent_registered_face(
                img_path, model_name, detector_backend
            )
        except Exception as e:
            st.warning(f"Could not process {img_path.name}: {e}")
            embedding_obj = []

        # A profile crop can produce more than one valid detector region.
        # Keep every embedding so matching uses the closest angle/crop rather
        # than arbitrarily discarding all but the first representation.
        valid_embeddings = [
            item.get("embedding")
            for item in embedding_obj
            if isinstance(item, dict) and item.get("embedding") is not None
        ]
        for embedding in valid_embeddings or [None]:
            KNOWN_FACE_ENCODINGS.append(
                {
                    "profile_id": profile_id,
                    "name": name,
                    "role": role,
                    "angle": get_profile_angle(img_path.stem),
                    "image_path": str(img_path),
                    "encoding": embedding,
                }
            )
    KNOWN_FACE_CACHE_SIGNATURE = signature


def calculate_face_distance(
    face_encoding: list,
    reference_encoding: list,
    metric: str = DEEPFACE_METRIC,
) -> float:
    """Calculate the selected distance metric with validation."""
    probe = np.asarray(face_encoding, dtype=np.float64)
    reference = np.asarray(reference_encoding, dtype=np.float64)
    if probe.shape != reference.shape:
        raise ValueError("Face embedding dimensions do not match")
    if not np.all(np.isfinite(probe)) or not np.all(np.isfinite(reference)):
        raise ValueError("Face embedding contains non-finite values")
    if metric == "euclidean":
        return float(np.linalg.norm(probe - reference))
    if metric == "euclidean_l2":
        return float(
            np.linalg.norm(probe - reference)
            / max(np.linalg.norm(probe) + np.linalg.norm(reference), 1e-8)
        )
    probe_norm = float(np.linalg.norm(probe))
    reference_norm = float(np.linalg.norm(reference))
    if probe_norm == 0.0 or reference_norm == 0.0:
        # A zero vector is not a valid face embedding. Treat it as a
        # non-match instead of producing NaN or importing SciPy.
        return 1.0
    return float(1.0 - np.dot(probe, reference) / (probe_norm * reference_norm))


def find_face_in_known_cache(
    face_encoding: list,
    threshold: float = COSINE_THRESHOLD,
    profile_id: str | None = None,
    role: str | None = None,
    metric: str = DEEPFACE_METRIC,
) -> dict | None:
    """Return the closest known profile when it is inside the match threshold."""
    best_match = None
    best_distance = float("inf")
    for entry in KNOWN_FACE_ENCODINGS:
        if profile_id and entry.get("profile_id") != profile_id:
            continue
        if role and entry.get("role") != role:
            continue
        if entry.get("encoding") is None:
            continue
        try:
            distance = calculate_face_distance(face_encoding, entry["encoding"], metric)
        except (TypeError, ValueError):
            continue
        if distance < best_distance:
            best_match = entry
            best_distance = distance

    if best_match is None or best_distance > threshold:
        return None

    return {**best_match, "distance": float(best_distance)}


def is_valid_victim_match_candidate(frame: np.ndarray, facial_area: dict) -> bool:
    """Apply stricter fallback validation before declaring a victim match."""
    validator = getattr(DeepFace, "is_valid_face_region", None)
    if callable(validator):
        return bool(validator(frame, facial_area))
    return True


def record_detection_result(
    result_type: str,
    subject: str = "",
    distance: float | None = None,
    details: str = "",
    image_name: str = "",
    location: str = "",
    previous_timestamp: str = "",
    previous_location: str = "",
    profile_id: str = "",
    model_name: str = "",
    detector_backend: str = "",
    metric: str = "",
) -> None:
    """Store the latest recognition event for the live status panel."""
    st.session_state.last_detection = {
        "type": result_type,
        "subject": subject,
        "distance": distance,
        "details": details,
        "image_name": image_name,
        "location": location,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "previous_timestamp": previous_timestamp,
        "previous_location": previous_location,
        "profile_id": profile_id,
        "model_name": model_name,
        "detector_backend": detector_backend,
        "metric": metric,
    }


def register_new_unknown(
    face_roi: np.ndarray,
    location: str,
    mode: str,
    model_name: str = DEEPFACE_MODEL,
    metric: str = DEEPFACE_METRIC,
) -> str:
    """Registers a new unknown person, saves their image, logs the event, and updates the DB."""
    unknown_id = get_next_unknown_id()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    image_path = UNKNOWN_DIR / f"{unknown_id}.jpg"
    
    cv2.imwrite(str(image_path), face_roi)

    new_person_df = pd.DataFrame(
        [[unknown_id, str(image_path), timestamp, timestamp, location, ""]],
        columns=["unknown_id", "image_path", "first_seen_timestamp", "last_seen_timestamp", "last_known_location", "assigned_name"],
    )
    new_person_df.to_csv(UNKNOWN_DB_PATH, mode="a", header=False, index=False)

    log_sighting(unknown_id, timestamp, location)
    log_event(mode=mode, subject_id=unknown_id, role="Unknown", event_type="New Unknown Detected")
    
    return unknown_id


def write_csv_atomically(frame: pd.DataFrame, path: Path) -> None:
    """Replace one app CSV without leaving a partially-written file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            suffix=".tmp",
            dir=path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            frame.to_csv(temporary_file, index=False)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_investigation_cases() -> pd.DataFrame:
    """Load the case register, returning a stable shape for an empty or old file."""
    try:
        cases = pd.read_csv(CASE_RECORDS_PATH).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=CASE_RECORD_COLUMNS)

    for column in CASE_RECORD_COLUMNS:
        if column not in cases.columns:
            cases[column] = ""
    cases = cases[CASE_RECORD_COLUMNS]
    return cases[
        cases["case_id"].astype(str).str.strip() != ""
    ].sort_values("opened_at", ascending=False, ignore_index=True)


def load_case_activity() -> pd.DataFrame:
    """Load human-entered case actions without exposing malformed rows to the UI."""
    try:
        activity = pd.read_csv(CASE_ACTIVITY_LOG_PATH).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return pd.DataFrame(columns=CASE_ACTIVITY_COLUMNS)

    for column in CASE_ACTIVITY_COLUMNS:
        if column not in activity.columns:
            activity[column] = ""
    return activity[CASE_ACTIVITY_COLUMNS]


def get_investigation_case(case_id: str) -> dict[str, str]:
    """Return one case record, or an empty mapping when it no longer exists."""
    cases = load_investigation_cases()
    matches = cases[cases["case_id"].astype(str) == str(case_id)]
    return matches.iloc[0].to_dict() if not matches.empty else {}


def _next_case_id(cases: pd.DataFrame) -> str:
    """Create a readable, daily sequence without placing personal data in the ID."""
    date_prefix = time.strftime("CASE-%Y%m%d-")
    existing_ids = set(cases.get("case_id", pd.Series(dtype=str)).astype(str))
    sequence = 1
    while f"{date_prefix}{sequence:03d}" in existing_ids:
        sequence += 1
    return f"{date_prefix}{sequence:03d}"


def _append_case_activity(
    case_id: str,
    event_type: str,
    location: str,
    actor: str,
    details: str,
) -> None:
    """Persist one human case action as an immutable timeline event."""
    activity = load_case_activity()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    event = pd.DataFrame(
        [[
            f"{case_id}-ACT-{time.time_ns()}",
            case_id,
            timestamp,
            str(event_type).strip(),
            str(location).strip(),
            str(actor).strip(),
            str(details).strip(),
        ]],
        columns=CASE_ACTIVITY_COLUMNS,
    )
    write_csv_atomically(
        pd.concat([activity, event], ignore_index=True), CASE_ACTIVITY_LOG_PATH
    )


def create_investigation_case(
    profile_id: str,
    priority: str = "Medium",
    last_seen_location: str = "",
    assigned_to: str = "",
    case_contact: str = "",
    notes: str = "",
) -> tuple[bool, str, str]:
    """Open one administrator-approved investigation for a registered Victim."""
    if st.session_state.get("role") != "Administrator":
        return False, "Only an Administrator can open an investigation case.", ""
    if priority not in CASE_PRIORITY_OPTIONS:
        return False, "Choose a valid case priority.", ""

    profiles = get_registered_profiles_df()
    victim = profiles[
        (profiles["profile_id"].astype(str) == str(profile_id))
        & (profiles["category"].astype(str) == "Victim")
    ]
    if victim.empty:
        return False, "Choose a registered Victim profile for this case.", ""

    cases = load_investigation_cases()
    active_duplicate = cases[
        (cases["profile_id"].astype(str) == str(profile_id))
        & (~cases["status"].astype(str).isin(["Resolved", "Closed"]))
    ]
    if not active_duplicate.empty:
        return (
            False,
            f"{victim.iloc[0]['name']} already has active case "
            f"{active_duplicate.iloc[0]['case_id']}.",
            "",
        )

    case_id = _next_case_id(cases)
    subject_name = str(victim.iloc[0]["name"]).strip()
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    record = pd.DataFrame(
        [[
            case_id,
            str(profile_id),
            subject_name,
            "Open",
            priority,
            timestamp,
            timestamp,
            str(last_seen_location).strip(),
            str(assigned_to).strip(),
            str(case_contact).strip(),
            str(notes).strip(),
        ]],
        columns=CASE_RECORD_COLUMNS,
    )
    write_csv_atomically(pd.concat([cases, record], ignore_index=True), CASE_RECORDS_PATH)
    _append_case_activity(
        case_id,
        "Case opened",
        last_seen_location,
        "Administrator",
        "Investigation opened from the registered Victim profile.",
    )
    log_event(
        mode="Case Command Center",
        subject_id=case_id,
        role="Victim Case",
        event_type="Case Opened",
        details=f"Victim profile: {profile_id}; priority: {priority}.",
    )
    return True, f"Case {case_id} opened for {subject_name}.", case_id


def update_investigation_case(
    case_id: str,
    status: str,
    priority: str,
    last_seen_location: str,
    assigned_to: str,
    case_contact: str,
    notes: str,
    activity_type: str,
    activity_location: str,
    activity_note: str,
) -> tuple[bool, str]:
    """Update case metadata and append a reviewable human investigation action."""
    if st.session_state.get("role") != "Administrator":
        return False, "Only an Administrator can update an investigation case."
    if status not in CASE_STATUS_OPTIONS or priority not in CASE_PRIORITY_OPTIONS:
        return False, "Choose a valid case status and priority."

    cases = load_investigation_cases()
    matches = cases["case_id"].astype(str) == str(case_id)
    if not matches.any():
        return False, "The selected case is no longer available."

    current = cases.loc[matches].iloc[0]
    updated_values = {
        "status": str(status).strip(),
        "priority": str(priority).strip(),
        "last_seen_location": str(last_seen_location).strip(),
        "assigned_to": str(assigned_to).strip(),
        "case_contact": str(case_contact).strip(),
        "notes": str(notes).strip(),
    }
    changed_fields = [
        label
        for label, value in updated_values.items()
        if str(current.get(label, "")).strip() != value
    ]
    clean_activity_note = str(activity_note).strip()
    if not changed_fields and not clean_activity_note:
        return False, "Change a case field or add an investigation update before saving."

    for field, value in updated_values.items():
        cases.loc[matches, field] = value
    cases.loc[matches, "last_updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    write_csv_atomically(cases[CASE_RECORD_COLUMNS], CASE_RECORDS_PATH)

    change_summary = ", ".join(field.replace("_", " ") for field in changed_fields)
    timeline_details = clean_activity_note or f"Updated: {change_summary}."
    _append_case_activity(
        str(case_id),
        str(activity_type).strip() or "Case update",
        str(activity_location).strip() or updated_values["last_seen_location"],
        "Administrator",
        timeline_details,
    )
    log_event(
        mode="Case Command Center",
        subject_id=str(case_id),
        role="Victim Case",
        event_type="Case Updated",
        details=(
            f"Status: {updated_values['status']}; changed: "
            f"{change_summary or 'timeline note'}"
        ),
    )
    return True, f"Case {case_id} updated."


def get_investigation_timeline(case_id: str) -> pd.DataFrame:
    """Merge immutable human updates with raw victim-sighting records for one case."""
    case = get_investigation_case(case_id)
    timeline_columns = ["timestamp", "event_type", "location", "source", "actor", "details"]
    if not case:
        return pd.DataFrame(columns=timeline_columns)

    human_activity = load_case_activity()
    human_activity = human_activity[
        human_activity["case_id"].astype(str) == str(case_id)
    ]
    manual_events = pd.DataFrame(
        {
            "timestamp": human_activity.get("timestamp", pd.Series(dtype=str)),
            "event_type": human_activity.get("event_type", pd.Series(dtype=str)),
            "location": human_activity.get("location", pd.Series(dtype=str)),
            "source": "Investigation team",
            "actor": human_activity.get("actor", pd.Series(dtype=str)),
            "details": human_activity.get("details", pd.Series(dtype=str)),
        }
    )

    try:
        sightings = pd.read_csv(VICTIM_SIGHTING_LOG_PATH).fillna("")
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
        sightings = pd.DataFrame(columns=["profile_id", "name", "timestamp", "location"])
    sightings = sightings[
        sightings.get("profile_id", pd.Series(dtype=str)).astype(str)
        == str(case["profile_id"])
    ]
    sighting_events = pd.DataFrame(
        {
            "timestamp": sightings.get("timestamp", pd.Series(dtype=str)),
            "event_type": "Camera sighting recorded",
            "location": sightings.get("location", pd.Series(dtype=str)),
            "source": "Surveillance log",
            "actor": "System",
            "details": "Recorded by the active Lost Person Search workflow.",
        }
    )

    timeline = pd.concat([manual_events, sighting_events], ignore_index=True)
    if timeline.empty:
        return pd.DataFrame(columns=timeline_columns)
    timeline["_sort_timestamp"] = pd.to_datetime(timeline["timestamp"], errors="coerce")
    return timeline.sort_values(
        ["_sort_timestamp", "timestamp"], ascending=False, na_position="last"
    ).drop(columns="_sort_timestamp").reset_index(drop=True)


def convert_unknown_to_victim(
    unknown_id: str,
    name: str,
    approximate_age: str = "",
    description: str = "",
    last_known_area: str = "",
    contact: str = "",
    notes: str = "",
    confirmed: bool = False,
    profile_category: str = "Victim",
) -> tuple[bool, str]:
    """Promote an admin-confirmed unknown photo to a searchable known profile."""
    global UNKNOWN_FACE_CACHE_SETTINGS, UNKNOWN_FACE_CACHE_BUILT_VERSION

    if st.session_state.get("role") != "Administrator":
        return False, "Only an Administrator can register an Unknown profile."
    if profile_category not in {"Staff", "Victim"}:
        return False, "Choose Staff or Victim as the known profile category."
    if not confirmed:
        return False, "Confirm that the photo and person details have been checked."

    clean_name = str(name).strip()
    if not clean_name:
        return False, "Enter the person's name or confirmed identifier."
    safe_name = "".join(ch if ch.isalnum() else "_" for ch in clean_name).strip("_")
    safe_unknown_id = "".join(
        ch if ch.isalnum() else "_" for ch in str(unknown_id)
    ).strip("_")
    if not safe_name or not safe_unknown_id:
        return False, "The name or Unknown ID is not valid."

    unknown_profiles = get_unknown_profiles_df()
    matches = unknown_profiles[unknown_profiles["unknown_id"].astype(str) == str(unknown_id)]
    if matches.empty:
        return False, "That Unknown profile is unavailable or was already converted."
    source_path = Path(str(matches.iloc[0]["image_path"]))
    if not source_path.is_file():
        return False, "The saved Unknown photo could not be found."

    base_profile_id = f"{profile_category}_{safe_name}_{safe_unknown_id}"
    profile_id = base_profile_id
    suffix = 2
    while get_profile_angle_paths(profile_id) or any(
        REG_DIR.glob(f"{profile_id}__*.*")
    ):
        profile_id = f"{base_profile_id}_{suffix}"
        suffix += 1
    destination = REG_DIR / f"{profile_id}__front{source_path.suffix.lower()}"
    save_victim_details = profile_category == "Victim"
    details_path_existed = VICTIM_PROFILE_DETAILS_PATH.exists()
    unknown_path_existed = UNKNOWN_DB_PATH.exists()
    original_details_df = get_victim_profile_details()
    details_written = False
    unknown_written = False

    try:
        if save_victim_details:
            details_df = original_details_df.copy()
            details_df = details_df.reindex(columns=VICTIM_PROFILE_DETAIL_COLUMNS)
            details_df = details_df[details_df["profile_id"].astype(str) != profile_id]
            details_df = pd.concat(
                [
                    details_df,
                    pd.DataFrame(
                        [[
                            profile_id,
                            str(unknown_id),
                            clean_name,
                            str(approximate_age).strip(),
                            str(description).strip(),
                            str(last_known_area).strip(),
                            str(contact).strip(),
                            str(notes).strip(),
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                        ]],
                        columns=VICTIM_PROFILE_DETAIL_COLUMNS,
                    ),
                ],
                ignore_index=True,
            )

        try:
            unknown_df = pd.read_csv(UNKNOWN_DB_PATH).fillna("")
        except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError):
            unknown_df = pd.DataFrame()
        original_unknown_df = unknown_df.copy()
        required_columns = [
            "unknown_id",
            "image_path",
            "first_seen_timestamp",
            "last_seen_timestamp",
            "last_known_location",
            "assigned_name",
        ]
        for column in required_columns:
            if column not in unknown_df.columns:
                unknown_df[column] = ""
        db_rows = unknown_df[unknown_df["unknown_id"].astype(str) == str(unknown_id)]
        if db_rows.empty:
            unknown_df = pd.concat(
                [
                    unknown_df,
                    pd.DataFrame(
                        [[
                            str(unknown_id),
                            str(source_path),
                            "",
                            "",
                            "",
                            clean_name,
                        ]],
                        columns=required_columns,
                    ),
                ],
                ignore_index=True,
            )
        else:
            unknown_df.loc[
                unknown_df["unknown_id"].astype(str) == str(unknown_id),
                "assigned_name",
            ] = clean_name

        REG_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        if save_victim_details:
            write_csv_atomically(details_df, VICTIM_PROFILE_DETAILS_PATH)
            details_written = True
        write_csv_atomically(unknown_df, UNKNOWN_DB_PATH)
        unknown_written = True
    except Exception as exc:
        if destination.exists():
            destination.unlink()
        if details_written:
            if details_path_existed:
                write_csv_atomically(original_details_df, VICTIM_PROFILE_DETAILS_PATH)
            elif VICTIM_PROFILE_DETAILS_PATH.exists():
                VICTIM_PROFILE_DETAILS_PATH.unlink()
        if unknown_written:
            if unknown_path_existed:
                write_csv_atomically(original_unknown_df, UNKNOWN_DB_PATH)
            elif UNKNOWN_DB_PATH.exists():
                UNKNOWN_DB_PATH.unlink()
        return False, f"Could not save the {profile_category} profile: {exc}"

    UNKNOWN_FACE_ENCODINGS[:] = [
        entry for entry in UNKNOWN_FACE_ENCODINGS
        if str(entry.get("unknown_id")) != str(unknown_id)
    ]
    UNKNOWN_FACE_CACHE_SETTINGS = None
    UNKNOWN_FACE_CACHE_BUILT_VERSION = -1
    invalidate_known_face_cache()
    log_event(
        mode="Victim Profile Administration",
        subject_id=profile_id,
        role=profile_category,
        event_type=f"Unknown Converted to {profile_category}",
        details=f"Source Unknown ID: {unknown_id}; admin-confirmed enrollment.",
    )
    return True, f"{clean_name} is now registered as {profile_category}."


def log_sighting(unknown_id: str, timestamp: str, location: str) -> None:
    """Adds a record to the sighting log for an unknown person."""
    try:
        sighting_id = (pd.read_csv(UNKNOWN_SIGHTING_LOG_PATH)["sighting_id"].max() + 1)
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError):
        sighting_id = 1

    new_sighting_df = pd.DataFrame(
        [[sighting_id, unknown_id, timestamp, location]], columns=["sighting_id", "unknown_id", "timestamp", "location"]
    )
    new_sighting_df.to_csv(UNKNOWN_SIGHTING_LOG_PATH, mode="a", header=False, index=False)


def get_last_unknown_sighting(unknown_id: str) -> dict[str, str]:
    """Read the last saved date/time and location before a new re-identification."""
    cached_sighting = UNKNOWN_SIGHTING_MEMORY.get(str(unknown_id))
    if cached_sighting:
        return cached_sighting.copy()

    try:
        sighting_df = pd.read_csv(UNKNOWN_SIGHTING_LOG_PATH)
        matches = sighting_df[sighting_df["unknown_id"].astype(str) == unknown_id]
        if not matches.empty:
            last = matches.sort_values("timestamp").iloc[-1]
            result = {
                "timestamp": str(last.get("timestamp", "")),
                "location": str(last.get("location", "")),
            }
            UNKNOWN_SIGHTING_MEMORY[str(unknown_id)] = result
            return result.copy()
    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError, IndexError):
        pass

    try:
        unknown_df = pd.read_csv(UNKNOWN_DB_PATH)
        matches = unknown_df[unknown_df["unknown_id"].astype(str) == unknown_id]
        if not matches.empty:
            last = matches.iloc[-1]
            result = {
                "timestamp": str(last.get("last_seen_timestamp", "")),
                "location": str(last.get("last_known_location", "")),
            }
            UNKNOWN_SIGHTING_MEMORY[str(unknown_id)] = result
            return result.copy()
    except (FileNotFoundError, pd.errors.EmptyDataError, KeyError, IndexError):
        pass

    return {"timestamp": "", "location": ""}


def update_unknown_sighting(unknown_id: str, location: str, mode: str) -> bool:
    """Persist an unknown sighting at most once every few seconds."""
    sighting_key = (str(unknown_id), location)
    now = time.monotonic()
    if now - UNKNOWN_SIGHTING_LAST_WRITE.get(sighting_key, 0.0) < UNKNOWN_SIGHTING_WRITE_INTERVAL_SECONDS:
        return False

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        db_df = pd.read_csv(UNKNOWN_DB_PATH)
        db_df.loc[db_df["unknown_id"] == unknown_id, "last_seen_timestamp"] = timestamp
        db_df.loc[db_df["unknown_id"] == unknown_id, "last_known_location"] = location
        db_df.to_csv(UNKNOWN_DB_PATH, index=False)
        log_sighting(unknown_id, timestamp, location)
        log_event(mode=mode, subject_id=unknown_id, role="Unknown", event_type="Re-identified")
        UNKNOWN_SIGHTING_LAST_WRITE[sighting_key] = now
        UNKNOWN_SIGHTING_MEMORY[str(unknown_id)] = {
            "timestamp": timestamp,
            "location": location,
        }
        return True
    except (FileNotFoundError, pd.errors.EmptyDataError, IndexError):
        return False


def analyze_facial_attributes(frame: np.ndarray, face_objs: list) -> list[dict]:
    """Analyze facial attributes (age, gender, emotion, race) for detected faces."""
    attributes_list = []
    if DeepFace is None:
        return attributes_list
    
    try:
        analysis = DeepFace.analyze(
            img_path=frame, enforce_detection=False, silent=True
        )
        if isinstance(analysis, list):
            attributes_list = analysis
    except Exception as e:
        pass
    
    return attributes_list


def extract_and_align_faces(frame: np.ndarray) -> list[np.ndarray]:
    """Extract and align faces from the frame."""
    aligned_faces = []
    if DeepFace is None:
        return aligned_faces
    
    try:
        extracted = DeepFace.extract_faces(
            img_path=frame, enforce_detection=False, silent=True
        )
        if isinstance(extracted, list):
            aligned_faces = [face.get("face") for face in extracted if "face" in face]
    except Exception as e:
        pass
    
    return aligned_faces


def verify_face_pair(img1_path: str, img2_path: str, model: str = DEEPFACE_MODEL) -> dict:
    """Verify if two face images belong to the same person (1-to-1 matching)."""
    if DeepFace is None:
        return {"verified": False, "distance": 1.0, "threshold": 0.4}
    
    try:
        result = DeepFace.verify(
            img1_path=img1_path, img2_path=img2_path,
            model_name=model, enforce_detection=False, silent=True
        )
        return result
    except Exception as e:
        return {"verified": False, "distance": 1.0, "threshold": 0.4, "error": str(e)}


def detect_spoofing(frame: np.ndarray) -> dict:
    """Detect face spoofing/liveness attacks using anti-spoofing model."""
    if DeepFace is None:
        return {"is_real": True, "confidence": 0.0}
    
    try:
        result = DeepFace.detect_spoofing(
            img_path=frame, detector_backend="opencv", silent=True
        )
        return result
    except Exception as e:
        return {"is_real": True, "confidence": 0.0, "error": str(e)}


def get_face_embeddings(frame: np.ndarray, model: str = DEEPFACE_MODEL) -> list:
    """Get facial embeddings for faces in the frame."""
    if DeepFace is None:
        return []
    
    try:
        embeddings = DeepFace.represent(
            img_path=frame, model_name=model, enforce_detection=False
        )
        return embeddings if isinstance(embeddings, list) else []
    except Exception as e:
        return []


def check_weapon_contours(
    frame: np.ndarray,
) -> tuple[bool, list[tuple[int, int, int, int, str]]]:
    """Detect possible elongated weapons and warm fire-like regions.

    This is deliberately labelled heuristic: contours cannot prove that an
    object is a gun or knife. A trained threat detector is required for that.
    """
    frame_height, frame_width = frame.shape[:2]
    frame_area = max(frame_height * frame_width, 1)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 60, 180)
    edges = cv2.morphologyEx(
        edges,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
    )
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes: list[tuple[int, int, int, int, str]] = []
    min_contour_area = max(250.0, frame_area * 0.001)
    max_contour_area = frame_area * 0.20
    for contour in contours:
        area = cv2.contourArea(contour)
        if not min_contour_area <= area <= max_contour_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = max(w, h) / max(min(w, h), 1)
        contour_box_area = max(w * h, 1)
        fill_ratio = area / contour_box_area
        hull_area = max(cv2.contourArea(cv2.convexHull(contour)), 1.0)
        solidity = area / hull_area
        if aspect_ratio >= 2.5 and fill_ratio >= 0.08 and solidity >= 0.15:
            boxes.append((x, y, w, h, "Possible weapon"))

    # Fire often has no useful edge contour, so separately inspect saturated
    # red/orange/yellow regions in HSV space.
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    warm_mask = cv2.inRange(
        hsv,
        np.array([0, 100, 100], dtype=np.uint8),
        np.array([35, 255, 255], dtype=np.uint8),
    )
    warm_mask = cv2.morphologyEx(
        warm_mask,
        cv2.MORPH_OPEN,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
    )
    warm_mask = cv2.morphologyEx(
        warm_mask,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)),
    )
    fire_contours, _ = cv2.findContours(
        warm_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    for contour in fire_contours:
        area = cv2.contourArea(contour)
        if area < max(400.0, frame_area * 0.002) or area > frame_area * 0.35:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        if area / max(w * h, 1) >= 0.12:
            boxes.append((x, y, w, h, "Possible fire"))

    return bool(boxes), boxes


def process_frame(
    frame: np.ndarray,
    mode: str,
    target_profile_id: str | None = None,
    location: str = "Main Feed",
) -> tuple[np.ndarray, str]:
    """The core processing pipeline for each video frame."""
    processing_frame = frame
    processing_max_width = get_processing_max_width()
    if frame.shape[1] > processing_max_width:
        resize_ratio = processing_max_width / frame.shape[1]
        processing_frame = cv2.resize(
            frame,
            (processing_max_width, max(1, int(frame.shape[0] * resize_ratio))),
            interpolation=cv2.INTER_AREA,
        )
    annotated_frame = processing_frame.copy()
    detection_summary = "Status: Idle"
    victim_search = is_victim_search_mode(mode)
    attendance_mode = is_member_attendance_mode(mode)
    victim_found = None
    model_name, detector_backend, metric = get_runtime_face_settings()
    can_match_identities = reliable_face_matching_available()

    is_face_rec_mode = "Threat" not in mode
    
    # --- 1. Threat Detection (Exclusive Mode) ---
    if not is_face_rec_mode:
        threat_detected, boxes = check_weapon_contours(annotated_frame)
        if threat_detected:
            threat_labels = []
            for x, y, w, h, threat_label in boxes:
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                cv2.putText(annotated_frame, threat_label, (x, max(0, y - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                threat_labels.append(threat_label)
            detection_summary = "Possible threat: " + ", ".join(sorted(set(threat_labels)))
            global LAST_THREAT_LOG_TIME
            if time.monotonic() - LAST_THREAT_LOG_TIME >= THREAT_LOG_INTERVAL_SECONDS:
                log_event(
                    mode=mode,
                    subject_id="System",
                    role="N/A",
                    event_type="Threat Detected",
                    details="Heuristic alert: " + ", ".join(sorted(set(threat_labels))),
                )
                LAST_THREAT_LOG_TIME = time.monotonic()
        else:
            detection_summary = "No threats detected."
        record_detection_result(
            "threat" if threat_detected else "no_threat",
            details=detection_summary,
        )
        st.session_state.last_status = detection_summary
        return annotated_frame, detection_summary

    if should_skip_local_face_inference():
        detection_summary = "CPU saver: waiting for next face scan."
        st.session_state.last_status = detection_summary
        return annotated_frame, detection_summary

    # --- 2. Face Detection & Recognition (For all other modes) ---
    try:
        face_objs = DeepFace.represent(
            img_path=processing_frame,
            model_name=model_name,
            enforce_detection=False,
            detector_backend=detector_backend,
            align=True,
        )
    except Exception as e:
        st.session_state.last_status = f"DeepFace Error: {e}"
        record_detection_result("error", details=f"Face analysis error: {e}")
        return annotated_frame, f"Error during face representation: {e}"

    if not face_objs:
        st.session_state.last_status = "No faces detected in frame."
        record_detection_result("no_face", details="No face detected in the current frame.")
        return annotated_frame, "No faces detected in frame."

    detection_summary = f"Found {len(face_objs)} face(s), analyzing..."
    
    for face_obj in face_objs:
        facial_area = face_obj["facial_area"]
        x = int(facial_area["x"])
        y = int(facial_area["y"])
        w = int(facial_area["w"])
        h = int(facial_area["h"])
        face_roi = processing_frame[y : y + h, x : x + w]
        if face_roi.size == 0:
            continue
            
        face_encoding = face_obj["embedding"]

        if victim_search and not is_valid_victim_match_candidate(
            processing_frame, facial_area
        ):
            # Never turn a low-quality Haar false detection (for example,
            # clothing texture) into a victim alert.
            continue

        # Step A: Check against the KNOWN faces in-memory cache
        match_threshold = float(
            st.session_state.get("similarity_threshold", COSINE_THRESHOLD)
        )
        if victim_search and can_match_identities:
            known_match = (
                find_face_in_known_cache(
                    face_encoding,
                    match_threshold,
                    profile_id=target_profile_id,
                    role="Victim",
                    metric=metric,
                )
                if target_profile_id
                else None
            )
        elif can_match_identities:
            known_match = find_face_in_known_cache(
                face_encoding,
                match_threshold,
                metric=metric,
            )
        else:
            known_match = None
        if known_match:
            name, role = known_match["name"], known_match["role"]
            distance = known_match["distance"]
            if victim_search:
                victim_found = known_match
                # Red means the selected victim was positively found.
                color = (0, 0, 255)
                label = "VICTIM FOUND"
                if record_victim_sighting(
                    known_match["profile_id"], name, location
                ):
                    log_event(
                        mode=mode,
                        subject_id=known_match["profile_id"],
                        role="Victim",
                        event_type="Victim Found",
                        details=f"Camera location: {location}",
                    )
            elif attendance_mode:
                # Registered/manual profiles always win before unknown search.
                color = (0, 255, 0)
                label = f"Known: {name}"
            else:
                color = (0, 255, 0) if role == "Staff" else (255, 0, 0)
                label = f"{role}: {name}"
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(annotated_frame, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            detection_summary = f"Matched: {label} (distance {distance:.3f})"
            if victim_search:
                record_detection_result(
                    "victim_found",
                    subject=name,
                    distance=distance,
                    details="Selected victim matched against the camera feed.",
                    image_name=Path(known_match.get("image_path", "")).name,
                    location=location,
                    profile_id=known_match["profile_id"],
                    model_name=model_name,
                    detector_backend=detector_backend,
                    metric=metric,
                )
            else:
                record_detection_result(
                    "known_match",
                    subject=label,
                    distance=distance,
                    details="Matched against a registered profile.",
                    location=location,
                )
                log_event(mode=mode, subject_id=name, role=role, event_type="Known Face Match")
            continue

        # Step B: Check the in-memory unknown index. Disk/database I/O is
        # intentionally not part of the per-frame recognition path.
        unknown_match = find_face_in_unknown_cache(
            face_encoding,
            metric=metric,
            model_name=model_name,
            detector_backend=detector_backend,
        )
        if unknown_match:
            unknown_id = str(unknown_match["unknown_id"])
            match_path = Path(unknown_match["image_path"])
            distance = float(unknown_match["distance"])
            previous_sighting = (
                get_last_unknown_sighting(unknown_id) if not victim_search else {}
            )
            update_unknown_sighting(unknown_id, location, mode)
            detection_summary = f"Re-identified previous unknown: {unknown_id} (distance {distance:.3f})"
            if not victim_search:
                record_detection_result(
                    "unknown_match",
                    subject=unknown_id,
                    distance=distance,
                    details="Matched against a previously saved unknown face.",
                    image_name=match_path.name,
                    location=location,
                    previous_timestamp=previous_sighting.get("timestamp", ""),
                    previous_location=previous_sighting.get("location", ""),
                )
            if victim_search:
                # Keep the selected victim's identity private until verified,
                # while still confirming that camera face detection is working.
                color = (0, 255, 0)
                label = "FACE DETECTED - NO MATCH"
                cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(annotated_frame, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
                continue
            elif attendance_mode:
                color = (0, 0, 255)
                label = f"Unknown: {unknown_id}"
            else:
                color = (255, 165, 0) # Orange
                label = f"ID: {unknown_id}"
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            if label:
                cv2.putText(annotated_frame, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            continue
        
        # Step C: If not known and not previously unknown, register as a NEW UNKNOWN
        unknown_id = register_new_unknown(
            face_roi,
            location,
            mode,
            model_name=model_name,
            metric=metric,
        )
        add_unknown_face_to_cache(
            unknown_id,
            face_encoding,
            UNKNOWN_DIR / f"{unknown_id}.jpg",
            model_name,
            detector_backend,
        )
        detection_summary = f"No registered match - saved as new unknown: {unknown_id}"
        if not victim_search:
            record_detection_result(
                "new_unknown",
                subject=unknown_id,
                details="No known or previous-unknown match; face image was saved.",
                image_name=f"{unknown_id}.jpg",
                location=location,
            )
        if victim_search:
            # A green box confirms detection without incorrectly identifying
            # the person as the selected victim.
            color = (0, 255, 0)
            label = "FACE DETECTED - NO MATCH"
            cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(annotated_frame, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2)
            continue
        elif attendance_mode:
            color = (0, 0, 255)
            label = f"Unknown: {unknown_id}"
        else:
            color = (255, 255, 0) # Cyan
            label = f"New ID: {unknown_id}"
        cv2.rectangle(annotated_frame, (x, y), (x + w, y + h), color, 2)
        if label:
            cv2.putText(annotated_frame, label, (x, max(0, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    if victim_search:
        if victim_found:
            detection_summary = (
                f"Victim found: {victim_found['name']} at {location}"
            )
        elif not can_match_identities:
            detection_summary = (
                "Face detected. Victim identification requires the neural "
                "DeepFace runtime; fallback mode will not label a victim."
            )
            record_detection_result(
                "victim_search",
                details="Victim identification is disabled in OpenCV fallback mode.",
                location=location,
                profile_id=target_profile_id or "",
            )
        else:
            target_name = next(
                (
                    entry["name"]
                    for entry in KNOWN_FACE_ENCODINGS
                    if entry.get("profile_id") == target_profile_id
                ),
                target_profile_id or "selected victim",
            )
            detection_summary = (
                f"Searching for {target_name}. Selected victim not found in this frame."
            )
            record_detection_result(
                "victim_search",
                details="No selected victim match in the current camera frame.",
                location=location,
                profile_id=target_profile_id or "",
            )

    st.session_state.last_status = detection_summary
    return annotated_frame, detection_summary


def annotate_browser_frame(
    frame: np.ndarray,
    mode: str,
    target_profile_id: str | None,
    model_name: str,
    detector_backend: str,
    metric: str,
    threshold: float,
    location: str = "Main Feed",
    status_sink: dict | None = None,
    processing_max_width: int = PROCESSING_MAX_WIDTH,
) -> np.ndarray:
    """Annotate a browser-camera frame without touching Streamlit state.

    WebRTC invokes this function on a worker thread, so it deliberately keeps
    the callback free of widgets, session-state writes, CSV logging, and disk
    writes. Recognition still uses the same registered-face cache and matcher
    as the recorded-video path.
    """
    processing_frame = frame
    if frame.shape[1] > processing_max_width:
        ratio = processing_max_width / frame.shape[1]
        processing_frame = cv2.resize(
            frame,
            (processing_max_width, max(1, int(frame.shape[0] * ratio))),
            interpolation=cv2.INTER_AREA,
        )
    annotated = processing_frame.copy()
    if status_sink is not None and is_victim_search_mode(mode):
        status_sink["victim"] = None

    if "Threat" in mode:
        detected, boxes = check_weapon_contours(annotated)
        for x, y, w, h, label in boxes:
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.putText(annotated, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        if not detected:
            cv2.putText(annotated, "No threat detected", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 0), 2)
        return annotated

    try:
        face_objects = DeepFace.represent(
            img_path=processing_frame,
            model_name=model_name,
            detector_backend=detector_backend,
            enforce_detection=False,
            align=True,
        )
    except Exception as exc:
        cv2.putText(annotated, f"Recognition error: {str(exc)[:70]}", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        return annotated

    for face_object in face_objects or []:
        area = face_object.get("facial_area", {})
        x, y = int(area.get("x", 0)), int(area.get("y", 0))
        w, h = int(area.get("w", 0)), int(area.get("h", 0))
        if w <= 0 or h <= 0:
            continue
        if is_victim_search_mode(mode) and not is_valid_victim_match_candidate(
            processing_frame, area
        ):
            continue
        if is_victim_search_mode(mode) and reliable_face_matching_available():
            match = (
                find_face_in_known_cache(
                    face_object.get("embedding", []),
                    threshold,
                    profile_id=target_profile_id,
                    role="Victim",
                    metric=metric,
                )
                if target_profile_id
                else None
            )
        elif reliable_face_matching_available():
            match = find_face_in_known_cache(
                face_object.get("embedding", []), threshold, metric=metric
            )
        else:
            match = None

        if match:
            if is_victim_search_mode(mode):
                label = f"VICTIM FOUND: {match['name']} ({match['distance']:.2f})"
                color = (0, 0, 255)
                if status_sink is not None:
                    status_sink["victim"] = {
                        "subject": match["name"],
                        "profile_id": match.get("profile_id", target_profile_id or ""),
                        "image_name": Path(match.get("image_path", "")).name,
                        "distance": float(match["distance"]),
                        "location": location,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "model_name": model_name,
                        "detector_backend": detector_backend,
                        "metric": metric,
                    }
            else:
                label = f"MATCH: {match['name']} ({match['distance']:.2f})"
                color = (0, 200, 0)
        elif is_victim_search_mode(mode):
            # Detection is visible, but an unmatched person is never labelled
            # as the selected victim or given an identity.
            label = "FACE DETECTED - NO MATCH"
            color = (0, 255, 0)
        else:
            label = "Unknown"
            color = (0, 165, 255)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
        cv2.putText(annotated, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.62, color, 2)

    if not face_objects:
        cv2.putText(annotated, "No face detected", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    return annotated


if VideoProcessorBase is not None:
    class BrowserCameraProcessor(VideoProcessorBase):
        """WebRTC worker that performs live browser-camera face matching."""

        def __init__(self, mode: str, target_profile_id: str | None, model_name: str, detector_backend: str, metric: str, threshold: float, location: str, processing_max_width: int = PROCESSING_MAX_WIDTH, inference_interval_seconds: float = 0.0):
            self.mode = mode
            self.target_profile_id = target_profile_id
            self.model_name = model_name
            self.detector_backend = detector_backend
            self.metric = metric
            self.threshold = threshold
            self.location = location
            self.processing_max_width = processing_max_width
            self.inference_interval_seconds = inference_interval_seconds
            self._last_inference_time = 0.0
            self._status_lock = threading.Lock()
            self._latest_victim = None

        def get_latest_victim(self):
            with self._status_lock:
                return dict(self._latest_victim) if self._latest_victim else None

        def recv(self, frame):
            image = frame.to_ndarray(format="bgr24")
            now = time.monotonic()
            if (
                self.inference_interval_seconds > 0
                and now - self._last_inference_time < self.inference_interval_seconds
            ):
                preview = image
                if preview.shape[1] > self.processing_max_width:
                    ratio = self.processing_max_width / preview.shape[1]
                    preview = cv2.resize(
                        preview,
                        (self.processing_max_width, max(1, int(preview.shape[0] * ratio))),
                        interpolation=cv2.INTER_AREA,
                    )
                cv2.putText(preview, "CPU saver: live preview", (12, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 220, 255), 2)
                return av.VideoFrame.from_ndarray(preview, format="bgr24")
            self._last_inference_time = now
            status_sink = {}
            annotated = annotate_browser_frame(
                image,
                self.mode,
                self.target_profile_id,
                self.model_name,
                self.detector_backend,
                self.metric,
                self.threshold,
                self.location,
                status_sink,
                self.processing_max_width,
            )
            with self._status_lock:
                self._latest_victim = status_sink.get("victim")
            return av.VideoFrame.from_ndarray(annotated, format="bgr24")
else:
    BrowserCameraProcessor = None


def render_browser_camera(
    mode: str,
    target_profile_id: str | None,
    location: str,
) -> None:
    """Render the browser webcam and its live face-match overlay."""
    if webrtc_streamer is None or BrowserCameraProcessor is None:
        st.error("WebRTC is not installed. Run: python -m pip install -r requirements.txt")
        return

    model_name, detector_backend, metric = get_runtime_face_settings()
    threshold = float(st.session_state.get("similarity_threshold", COSINE_THRESHOLD))
    cpu_saver = cpu_saver_enabled()
    processing_max_width = get_processing_max_width()
    st.info("Allow camera permission, then press START inside the browser camera panel.")
    try:
        context = webrtc_streamer(
            key="n_one_browser_camera",
            mode=WebRtcMode.SENDRECV,
            media_stream_constraints={"video": True, "audio": False},
            video_processor_factory=lambda: BrowserCameraProcessor(
                mode,
                target_profile_id,
                model_name,
                detector_backend,
                metric,
                threshold,
                location,
                processing_max_width,
                CPU_SAVER_INFERENCE_INTERVAL_SECONDS if cpu_saver else 0.0,
            ),
            async_processing=True,
        )
        if is_victim_search_mode(mode):
            render_browser_victim_status(context)
    except Exception as exc:
        st.error(f"Browser camera panel could not load: {exc}")


@st.fragment(run_every="1s")
def render_browser_victim_status(context) -> None:
    """Poll the WebRTC worker and show the latest victim match separately."""
    processor = context.video_processor if context is not None else None
    result = processor.get_latest_victim() if processor is not None else None
    if not result:
        return

    image_path = REG_DIR / str(result.get("image_name", ""))
    with st.container(border=True):
        st.success(f"VICTIM FOUND: {result.get('subject', 'Selected victim')}")
        image_column, details_column = st.columns([1, 2])
        with image_column:
            if image_path.is_file():
                st.image(str(image_path), caption="Matched victim profile", width="content")
        with details_column:
            st.write(f"**Profile ID:** `{result.get('profile_id') or 'Unavailable'}`")
            st.write(f"**Camera location:** {result.get('location') or 'Unavailable'}")
            st.write(f"**Match distance:** {float(result.get('distance', 0)):.3f}")
            st.write(f"**Detected at:** {result.get('timestamp') or 'Unavailable'}")
            st.caption(
                f"Model: {result.get('model_name')} | Backend: "
                f"{result.get('detector_backend')} | Metric: {result.get('metric')}"
            )


def render_detection_result(container) -> None:
    """Render a clear, human-readable result for the most recent face event."""
    panel = container.container()
    result = st.session_state.get("last_detection", {})
    if not isinstance(result, dict):
        panel.info(str(result))
        return

    result_type = result.get("type", "idle")
    subject = result.get("subject", "")
    distance = result.get("distance")
    distance_text = f" | distance: {distance:.3f}" if distance is not None else ""
    timestamp = result.get("timestamp", "")
    details = result.get("details", "")
    previous_timestamp = result.get("previous_timestamp", "")
    previous_location = result.get("previous_location", "")
    current_location = result.get("location", "")
    profile_id = result.get("profile_id", "")

    if result_type == "victim_found":
        # Victim matches are rendered in their own dedicated alert card below.
        panel.empty()
        return
    elif result_type == "victim_search":
        panel.info("SEARCHING: Selected victim was not found in the current frame.")
    elif result_type == "known_match":
        panel.success(f"MATCH FOUND: {subject}{distance_text}")
    elif result_type == "unknown_match":
        panel.warning(f"PREVIOUS UNKNOWN MATCH: {subject}{distance_text}")
        if previous_timestamp or previous_location:
            panel.markdown(
                "**Previous sighting:** "
                f"{previous_timestamp or 'date/time unavailable'} at "
                f"{previous_location or 'location unavailable'}"
            )
    elif result_type == "new_unknown":
        panel.warning(f"NO MATCH - SAVED AS NEW UNKNOWN: {subject}")
    elif result_type == "no_face":
        panel.info("NO FACE DETECTED")
    elif result_type == "threat":
        panel.error(details or "Possible threat detected by heuristic analysis.")
    elif result_type == "error":
        panel.error(details or "Face analysis failed.")
    elif result_type == "no_threat":
        panel.info(details or "No threat detected.")
    else:
        panel.info(details or "Waiting for a detection result.")

    if details and result_type not in {"error", "no_threat", "threat"}:
        panel.caption(details)
    if result.get("image_name"):
        image_path = UNKNOWN_DIR / result["image_name"]
        panel.caption(f"Saved/matched image: {result['image_name']}")
        if image_path.exists():
            panel.image(str(image_path), caption="Previous/saved unknown face", width="content")
    if timestamp:
        event_label = "Current match" if result_type == "unknown_match" else "Last event"
        current_context = f" at {current_location}" if current_location else ""
        panel.caption(f"{event_label}: {timestamp}{current_context}")


def render_victim_found_result(container) -> None:
    """Render the selected victim in a dedicated, high-visibility result card."""
    result = st.session_state.get("last_detection", {})
    if not isinstance(result, dict) or result.get("type") != "victim_found":
        container.empty()
        return

    subject = result.get("subject", "Selected victim")
    distance = result.get("distance")
    distance_text = f"{float(distance):.3f}" if distance is not None else "Unavailable"
    profile_id = result.get("profile_id", "")
    image_name = str(result.get("image_name", "")).strip()
    image_path = REG_DIR / image_name if image_name else Path()
    if not image_path.is_file() and profile_id:
        angle_paths = get_profile_angle_paths(profile_id)
        image_path = angle_paths.get("front") or next(iter(angle_paths.values()), Path())

    with container.container(border=True):
        st.markdown("### VICTIM FOUND")
        image_column, details_column = st.columns([1, 2])
        with image_column:
            if image_path.is_file():
                st.image(str(image_path), caption="Matched victim profile", width="content")
            else:
                st.warning("Matched victim image is unavailable.")
        with details_column:
            st.success(f"{subject} matched successfully")
            st.write(f"**Profile ID:** `{profile_id or 'Unavailable'}`")
            st.write(f"**Camera location:** {result.get('location') or 'Unavailable'}")
            st.write(f"**Match distance:** {distance_text}")
            st.write(f"**Detected at:** {result.get('timestamp') or 'Unavailable'}")
            st.caption(
                "Model: "
                f"{result.get('model_name') or 'fallback'} | Backend: "
                f"{result.get('detector_backend') or 'opencv'} | Metric: "
                f"{result.get('metric') or 'cosine'}"
            )

        history = get_victim_sighting_history(profile_id)
        if not history.empty:
            st.write("**Victim sighting history by location**")
            st.dataframe(
                history[["timestamp", "location"]].rename(
                    columns={"timestamp": "Last seen", "location": "Camera location"}
                ),
                hide_index=True,
                width="stretch",
            )


def _frame_has_content(frame: np.ndarray | None) -> bool:
    """Reject empty/black camera frames before sending them to recognition."""
    if frame is None or frame.size == 0:
        return False
    return float(frame.std()) > 2.0 or float(frame.mean()) > 5.0


def open_video_source(video_target) -> tuple[cv2.VideoCapture | None, str]:
    """Open a video source and validate that it returns usable frames.

    Windows exposes cameras through different OpenCV backends and device
    indices. Probe the common combinations for a local webcam instead of
    assuming device 0. This does not access a browser camera; remote apps
    still need a WebRTC/browser component.
    """
    if not isinstance(video_target, int):
        capture = cv2.VideoCapture(video_target)
        if not capture.isOpened():
            capture.release()
            return None, "Could not open the selected video source."
        return capture, ""

    attempts = []
    backends = [
        ("DirectShow", cv2.CAP_DSHOW),
        ("Media Foundation", cv2.CAP_MSMF),
        ("Default", cv2.CAP_ANY),
    ]
    for camera_index in range(3):
        for backend_name, backend in backends:
            capture = cv2.VideoCapture(camera_index, backend)
            if not capture.isOpened():
                capture.release()
                attempts.append(f"camera {camera_index}/{backend_name}: unavailable")
                continue

            capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            usable = False
            for _ in range(3):
                ret, frame = capture.read()
                usable = ret and _frame_has_content(frame)
                if usable:
                    break
            if usable:
                return capture, f"camera {camera_index} via {backend_name}"

            capture.release()
            attempts.append(f"camera {camera_index}/{backend_name}: black/no frame")

    return None, (
        "No usable local webcam frame was found. "
        "If this app is running remotely, Laptop Webcam requires WebRTC/browser capture. "
        + " Attempts: "
        + "; ".join(attempts)
    )


def configure_session_state() -> None:
    defaults = {
        "authenticated": False, "role": "Guest", "streaming": False,
        "last_frame": None, "last_status": "Idle",
        "last_detection": {
            "type": "idle",
            "subject": "",
            "distance": None,
            "details": "No detections yet.",
            "image_name": "",
            "timestamp": "",
            "location": "",
            "previous_timestamp": "",
            "previous_location": "",
            "profile_id": "",
        },
        "camera_location": "Main Feed",
        "victim_search_target": None,
        "last_logged_event": "",
        "active_alerts": [],
        "login_attempts": 0, "login_locked_until": 0.0,
        "selected_model": DEEPFACE_MODEL,
        "selected_backend": DEEPFACE_BACKEND,
        "selected_metric": DEEPFACE_METRIC,
        "enable_attributes": True,
        "enable_spoofing_detection": False,
        "similarity_threshold": COSINE_THRESHOLD,
        "registration_capture_started": False,
        "registration_capture_source": None,
        "show_log_viewer": False,
        "cpu_saver_mode": True,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def detect_face_regions(image: np.ndarray) -> list[dict]:
    """Return face bounding boxes from either the real or fallback backend."""
    if hasattr(DeepFace, "detect_faces"):
        try:
            return [
                item["facial_area"]
                for item in DeepFace.detect_faces(image)
                if item.get("facial_area")
            ]
        except Exception:
            pass

    try:
        extracted = DeepFace.extract_faces(
            img_path=image,
            detector_backend="opencv",
            enforce_detection=True,
            align=True,
        )
        return [
            item["facial_area"]
            for item in extracted
            if item.get("facial_area")
        ]
    except Exception:
        return []


def prepare_single_face_crop(uploaded_file) -> tuple[np.ndarray | None, str]:
    """Validate a registration photo and return a face-only BGR crop."""
    if uploaded_file is None:
        return None, "Choose an image or capture a photo first."

    try:
        image = Image.open(BytesIO(uploaded_file.getvalue())).convert("RGB")
        frame = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    except Exception as exc:
        return None, f"Could not read the image: {exc}"

    regions = detect_face_regions(frame)
    if len(regions) == 0:
        return None, "No face detected. Face the camera directly with good lighting."
    if len(regions) > 1:
        return None, "Multiple faces detected. Keep only one person in the frame."

    region = regions[0]
    x, y, width, height = (
        int(region["x"]),
        int(region["y"]),
        int(region["w"]),
        int(region["h"]),
    )
    if width < 80 or height < 80:
        return None, "Face is too small. Move closer to the camera."

    padding = int(max(width, height) * 0.25)
    left = max(0, x - padding)
    top = max(0, y - padding)
    right = min(frame.shape[1], x + width + padding)
    bottom = min(frame.shape[0], y + height + padding)
    crop = frame[top:bottom, left:right]
    if crop.size == 0:
        return None, "Face crop was empty. Please capture the image again."

    return crop, "One face detected. Only the face crop will be saved."


def save_registered_profile_captures(
    name: str,
    role_label: str,
    captures: dict[str, object],
    require_all_angles: bool = True,
) -> tuple[bool, str]:
    """Validate and save one or more face captures under one profile ID."""
    if not name:
        return False, "Provide a name or identifier."

    prefix = "Victim" if "Victim" in role_label or "Lost" in role_label else "Staff"
    safe_name = "".join(
        character if character.isalnum() else "_" for character in name
    ).strip("_")
    if not safe_name:
        return False, "Provide a valid name or identifier."

    required_angles = ENROLLMENT_ANGLES if require_all_angles else ("front",)
    missing_angles = [angle for angle in required_angles if angle not in captures]
    if missing_angles:
        return False, "Capture all required angles: " + ", ".join(missing_angles)

    profile_id = f"{prefix}_{safe_name}"
    crops: dict[str, np.ndarray] = {}
    for angle in required_angles:
        capture = captures.get(angle)
        if isinstance(capture, (bytes, bytearray)):
            capture = BytesIO(capture)
        crop, message = prepare_single_face_crop(capture)
        if crop is None:
            return False, f"{angle.title()} capture invalid: {message}"
        crops[angle] = crop

    # Replace only this profile's old angle files, if the administrator is
    # updating an existing profile.
    for old_path in REG_DIR.glob(f"{profile_id}__*.*"):
        if old_path.is_file():
            old_path.unlink()
    legacy_path = REG_DIR / f"{profile_id}.jpg"
    if legacy_path.exists():
        legacy_path.unlink()

    for angle, crop in crops.items():
        destination = REG_DIR / f"{profile_id}__{angle}.jpg"
        cv2.imwrite(str(destination), crop)

    model_name, detector_backend, _ = get_runtime_face_settings()
    load_known_face_encodings(model_name, detector_backend)
    return True, f"Saved {len(crops)} angle captures for {name}."


def save_registered_profile(
    name: str, role_label: str, uploaded_file
) -> tuple[bool, str]:
    """Backward-compatible single-photo profile save."""
    if uploaded_file is None:
        return False, "Choose an image or capture a photo first."
    return save_registered_profile_captures(
        name,
        role_label,
        {"front": uploaded_file},
        require_all_angles=False,
    )


def clear_audit_log() -> None:
    """Clear audit records. This operation is available to Administrators only."""
    if CSV_LOG_PATH.exists():
        CSV_LOG_PATH.unlink()
    if VICTIM_SIGHTING_LOG_PATH.exists():
        VICTIM_SIGHTING_LOG_PATH.unlink()
    initialize_log_files()


def clear_case_command_data() -> None:
    """Remove case metadata and manual updates during a full local-data reset."""
    for data_path in (CASE_RECORDS_PATH, CASE_ACTIVITY_LOG_PATH):
        if data_path.exists():
            data_path.unlink()
    initialize_log_files()


def clear_registered_profiles() -> None:
    """Clear registered face profiles. This operation is available to Administrators only."""
    profile_paths = [profile_path for profile_path in REG_DIR.glob("*") if profile_path.is_file()]
    removed_profile_ids = {
        get_profile_id(profile_path.stem)
        for profile_path in profile_paths
        if profile_path.suffix.lower() in PROFILE_IMAGE_SUFFIXES
    }
    for profile_path in profile_paths:
        if profile_path.is_file():
            profile_path.unlink()
    if removed_profile_ids and VICTIM_PROFILE_DETAILS_PATH.exists():
        details = get_victim_profile_details()
        if "profile_id" in details.columns:
            details = details[
                ~details["profile_id"].astype(str).isin(removed_profile_ids)
            ]
            if details.empty:
                VICTIM_PROFILE_DETAILS_PATH.unlink()
            else:
                write_csv_atomically(details, VICTIM_PROFILE_DETAILS_PATH)
    invalidate_known_face_cache()


def clear_unknown_face_data() -> None:
    """Remove unknown-face photos and tracking records, then recreate empty logs."""
    global UNKNOWN_FACE_CACHE_SETTINGS, UNKNOWN_FACE_CACHE_BUILT_VERSION

    for face_path in UNKNOWN_DIR.glob("*"):
        if face_path.is_file():
            face_path.unlink()

    for data_path in (UNKNOWN_DB_PATH, UNKNOWN_SIGHTING_LOG_PATH):
        if data_path.exists():
            data_path.unlink()

    UNKNOWN_FACE_ENCODINGS.clear()
    UNKNOWN_SIGHTING_LAST_WRITE.clear()
    UNKNOWN_SIGHTING_MEMORY.clear()
    invalidate_unknown_face_cache()
    UNKNOWN_FACE_CACHE_SETTINGS = None
    UNKNOWN_FACE_CACHE_BUILT_VERSION = -1
    initialize_directories()
    initialize_log_files()


def clear_all_surveillance_data() -> None:
    """Remove registered faces, unknown faces, cases, logs, and the temporary upload."""
    clear_registered_profiles()
    clear_unknown_face_data()
    clear_audit_log()
    clear_case_command_data()
    if TEMP_VIDEO_PATH.exists():
        TEMP_VIDEO_PATH.unlink()


def render_status_chip(label: str, state: str, icon: str = "") -> None:
    """Render a modern status chip: live/searching/alert/idle/threat"""
    colors = {
        "live": ("rgba(34, 197, 94, 0.16)", "#bbf7d0", "rgba(34, 197, 94, 0.45)", "🟢"),
        "searching": ("rgba(37, 99, 235, 0.16)", "#bfdbfe", "rgba(37, 99, 235, 0.45)", "🔵"),
        "alert": ("rgba(239, 68, 68, 0.16)", "#fecaca", "rgba(239, 68, 68, 0.45)", "🔴"),
        "idle": ("rgba(100, 116, 139, 0.14)", "#cbd5e1", "rgba(100, 116, 139, 0.40)", "⚪"),
        "threat": ("rgba(234, 88, 12, 0.16)", "#ffedd5", "rgba(234, 88, 12, 0.45)", "🟠"),
    }
    bg, color, border, default_icon = colors.get(state, colors["idle"])
    icon = icon or default_icon
    st.markdown(f"""
        <span style="display:inline-flex; align-items:center; gap:4px; padding:4px 10px; border-radius:999px; font-weight:600; font-size:0.8rem; background:{bg}; color:{color}; border:1px solid {border};">
            <span class="chip-dot"></span> {icon} {label}
        </span>
    """, unsafe_allow_html=True)
def render_metric_card(title: str, value: str | int, delta: str | None = None,
                       delta_color: str = "normal", icon: str = "") -> None:
    """Render a metric card with consistent styling"""
    delta_style = ""
    if delta:
        if delta_color == "normal":
            delta_style = f'<div class="delta ok">{delta}</div>'
        elif delta_color == "negative":
            delta_style = f'<div class="delta bad">{delta}</div>'
        else:
            delta_style = f'<div class="delta warn">{delta}</div>'

    st.markdown(f"""
        <div class="metric-card">
            <div class="label">{icon} {title}</div>
            <div class="value">{value}</div>
            {delta_style}
        </div>
    """, unsafe_allow_html=True)
def render_camera_health_card(source_name: str, status: str, latency_ms: int | None = None,
                             fps: float | None = None, last_frame_ts: str | None = None) -> None:
    """Render a compact camera health/status card"""
    status_map = {
        "healthy": ("ok", "✅"),
        "degraded": ("warn", "🟡"),
        "offline": ("bad", "❌"),
        "connecting": ("warn", "🔵"),
    }
    status_class, status_icon = status_map.get(status, status_map["bad"])
    with st.container(border=True):
        cols = st.columns([3, 1, 1, 1])
        with cols[0]:
            st.markdown(f"**{status_icon} {source_name}**")
        with cols[1]:
            st.markdown(f"**{status.upper()}**")
        with cols[2]:
            if latency_ms:
                st.caption(f"{latency_ms}ms")
        with cols[3]:
            if fps:
                st.caption(f"{fps:.1f} FPS")
        if last_frame_ts:
            st.caption(f"Last: {last_frame_ts}")
def render_brand_logo() -> None:
    """Show the N-ONE brand mark on the current page when the asset exists."""
    if LOGO_PATH.is_file():
        st.image(str(LOGO_PATH), width=240)


def render_case_command_center(
    registered_df: pd.DataFrame | None = None,
) -> None:
    """Render the persistent, human-reviewed investigation workspace."""
    profiles = registered_df if registered_df is not None else get_registered_profiles_df()
    cases = load_investigation_cases()
    active_cases = cases[~cases["status"].astype(str).isin(["Resolved", "Closed"])]

    st.markdown("---")
    st.subheader(":material/folder_shared: Case command center")
    st.caption(
        "Open a victim investigation, keep human case notes, and review camera "
        "sightings in one chronological timeline. Camera records are evidence "
        "leads and still require operator verification."
    )

    with st.container(horizontal=True):
        st.metric("Active cases", len(active_cases), border=True)
        st.metric("All cases", len(cases), border=True)
        st.metric("Recorded updates", len(load_case_activity()), border=True)

    victim_profiles = profiles[profiles["category"] == "Victim"]
    with st.expander(":material/add_circle: Open a new victim investigation"):
        if st.session_state.get("role") != "Administrator":
            st.info("Only an Administrator can open or edit cases. Operators have read-only access.")
        elif victim_profiles.empty:
            st.info("Register a Victim profile before opening an investigation case.")
        else:
            victim_labels = {
                row["profile_id"]: row["name"]
                for _, row in victim_profiles.iterrows()
            }
            with st.form("open_investigation_case", clear_on_submit=True):
                profile_id = st.selectbox(
                    "Victim profile",
                    options=list(victim_labels),
                    format_func=lambda value: victim_labels[value],
                )
                create_col1, create_col2 = st.columns(2)
                with create_col1:
                    priority = st.selectbox("Priority", CASE_PRIORITY_OPTIONS, index=1)
                    assigned_to = st.text_input("Assigned investigator (optional)")
                    case_contact = st.text_input("Case contact (optional)")
                with create_col2:
                    last_seen_location = st.text_input("Last known location (optional)")
                    notes = st.text_area("Opening notes (optional)", height=100)
                create_submitted = st.form_submit_button(
                    "Open investigation case", type="primary", width="stretch"
                )
            if create_submitted:
                created, message, new_case_id = create_investigation_case(
                    profile_id=profile_id,
                    priority=priority,
                    last_seen_location=last_seen_location,
                    assigned_to=assigned_to,
                    case_contact=case_contact,
                    notes=notes,
                )
                if created:
                    st.session_state["selected_investigation_case"] = new_case_id
                    st.toast(message)
                    st.rerun()
                else:
                    st.error(message)

    if cases.empty:
        st.info("No investigation case has been opened yet.")
        return

    case_overview = cases[
        [
            "case_id",
            "subject_name",
            "status",
            "priority",
            "last_seen_location",
            "assigned_to",
            "last_updated_at",
        ]
    ].rename(
        columns={
            "case_id": "Case ID",
            "subject_name": "Victim",
            "status": "Status",
            "priority": "Priority",
            "last_seen_location": "Last known location",
            "assigned_to": "Assigned investigator",
            "last_updated_at": "Last updated",
        }
    )
    with st.container(border=True):
        st.markdown("**Case register**")
        st.dataframe(case_overview, hide_index=True, height=240, width="stretch")

    case_ids = cases["case_id"].tolist()
    selected_case_key = "selected_investigation_case"
    if (
        selected_case_key in st.session_state
        and st.session_state[selected_case_key] not in case_ids
    ):
        del st.session_state[selected_case_key]
    selected_case_id = st.selectbox(
        "Open case workspace",
        options=case_ids,
        format_func=lambda value: (
            f"{value} — "
            f"{cases.loc[cases['case_id'] == value, 'subject_name'].iloc[0]}"
        ),
        key=selected_case_key,
    )
    case = get_investigation_case(selected_case_id)
    if not case:
        st.warning("The selected case could not be loaded.")
        return

    with st.container(border=True):
        st.markdown(f"**{case['subject_name']} · {case['case_id']}**")
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        summary_col1.metric("Status", case["status"] or "Open")
        summary_col2.metric("Priority", case["priority"] or "Medium")
        summary_col3.metric("Opened", case["opened_at"] or "Unavailable")
        summary_col4.metric("Last updated", case["last_updated_at"] or "Unavailable")
        if case.get("assigned_to"):
            st.write(f"**Assigned investigator:** {case['assigned_to']}")
        if case.get("last_seen_location"):
            st.write(f"**Last known location:** {case['last_seen_location']}")
        if case.get("case_contact"):
            st.write(f"**Case contact:** {case['case_contact']}")
        if case.get("notes"):
            st.write(f"**Case notes:** {case['notes']}")

    timeline = get_investigation_timeline(selected_case_id)
    with st.container(border=True):
        st.markdown("**Investigation timeline**")
        if timeline.empty:
            st.info("No manual updates or camera sightings have been recorded for this case.")
        else:
            st.dataframe(
                timeline.rename(
                    columns={
                        "timestamp": "Time",
                        "event_type": "Event",
                        "location": "Location",
                        "source": "Source",
                        "actor": "Recorded by",
                        "details": "Details",
                    }
                ),
                hide_index=True,
                height=320,
                width="stretch",
            )

    if st.session_state.get("role") != "Administrator":
        st.caption("Operator access is read-only. Ask an Administrator to update case status or notes.")
        return

    with st.expander(":material/edit_note: Add investigation update"):
        current_status = case.get("status", "Open")
        current_priority = case.get("priority", "Medium")
        status_index = (
            CASE_STATUS_OPTIONS.index(current_status)
            if current_status in CASE_STATUS_OPTIONS
            else 0
        )
        priority_index = (
            CASE_PRIORITY_OPTIONS.index(current_priority)
            if current_priority in CASE_PRIORITY_OPTIONS
            else 1
        )
        with st.form(f"update_investigation_case_{selected_case_id}"):
            update_col1, update_col2 = st.columns(2)
            with update_col1:
                status = st.selectbox("Case status", CASE_STATUS_OPTIONS, index=status_index)
                priority = st.selectbox("Priority", CASE_PRIORITY_OPTIONS, index=priority_index)
                assigned_to = st.text_input(
                    "Assigned investigator (optional)", value=case.get("assigned_to", "")
                )
                case_contact = st.text_input(
                    "Case contact (optional)", value=case.get("case_contact", "")
                )
            with update_col2:
                last_seen_location = st.text_input(
                    "Last known location (optional)", value=case.get("last_seen_location", "")
                )
                activity_type = st.selectbox(
                    "Update type",
                    [
                        "Case update",
                        "Lead reported",
                        "Lead verified",
                        "False lead",
                        "Status review",
                    ],
                )
                activity_location = st.text_input("Update location (optional)")
                activity_note = st.text_area("Investigation update", height=100)
            notes = st.text_area("Case notes", value=case.get("notes", ""), height=100)
            update_submitted = st.form_submit_button(
                "Save investigation update", type="primary", width="stretch"
            )
        if update_submitted:
            updated, message = update_investigation_case(
                case_id=selected_case_id,
                status=status,
                priority=priority,
                last_seen_location=last_seen_location,
                assigned_to=assigned_to,
                case_contact=case_contact,
                notes=notes,
                activity_type=activity_type,
                activity_location=activity_location,
                activity_note=activity_note,
            )
            if updated:
                st.toast(message)
                st.rerun()
            else:
                st.error(message)


def render_operator_sidebar() -> None:
    """Render a minimal sidebar for Operator role: auth + CPU saver + active case."""
    st.sidebar.title("🔐 N-ONE Security Gate")
    if LOGO_PATH.is_file():
        st.sidebar.image(str(LOGO_PATH), width=180)
    st.sidebar.caption("RBAC access control for surveillance ops")

    try:
        credentials = load_auth_credentials()
    except RuntimeError:
        st.sidebar.error("Authentication is unavailable: required secrets are not configured.")
        st.sidebar.caption(
            "Configure ADMIN_USERNAME, ADMIN_PASSWORD, OPERATOR_USERNAME, and "
            "OPERATOR_PASSWORD in Streamlit Secrets "
            "or the process environment."
        )
        return

    if st.session_state.authenticated:
        if st.sidebar.button("🔒 Logout System", width='stretch'):
            st.session_state.streaming = False
            st.session_state.authenticated = False
            st.session_state.role = "Guest"
            st.rerun()
        st.sidebar.markdown(f"**Current Role:** {st.session_state.role}")
    else:
        st.sidebar.info("Login to access the command center.")
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login", width='stretch'):
            now = time.monotonic()
            locked_until = st.session_state.get("login_locked_until", 0.0)
            if now < locked_until:
                remaining = max(1, int(locked_until - now) + 1)
                st.sidebar.error(f"Too many failed attempts. Try again in {remaining} seconds.")
                return

            authenticated_role = None
            if (
                hmac.compare_digest(username, credentials["ADMIN_USERNAME"])
                and hmac.compare_digest(password, credentials["ADMIN_PASSWORD"])
            ):
                authenticated_role = "Administrator"
            elif (
                hmac.compare_digest(username, credentials["OPERATOR_USERNAME"])
                and hmac.compare_digest(password, credentials["OPERATOR_PASSWORD"])
            ):
                authenticated_role = "Operator"

            if authenticated_role is not None:
                st.session_state.login_attempts = 0
                st.session_state.login_locked_until = 0.0
                st.session_state.authenticated = True
                st.session_state.role = authenticated_role
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
                    st.session_state.login_locked_until = now + LOGIN_LOCKOUT_SECONDS
                    st.session_state.login_attempts = 0
                    st.sidebar.error("Too many failed attempts. Login is locked for 60 seconds.")
                else:
                    st.sidebar.error("Invalid credentials.")

    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        st.sidebar.toggle(
            "CPU saver (recommended)",
            key="cpu_saver_mode",
            help="Uses the faster OpenCV detector, a smaller scan image, and a 2.5 FPS face-scan limit. Turn it off only when maximum detection frequency is required.",
        )

    # Operator-only: show active case read-only
    if st.session_state.role == "Operator":
        st.sidebar.markdown("---")
        st.sidebar.caption("Active Case")
        cases = load_investigation_cases()
        active_cases = cases[~cases["status"].astype(str).isin(["Resolved", "Closed"])]
        if not active_cases.empty:
            latest = active_cases.iloc[-1]
            st.sidebar.info(f"Case: {latest.get('subject_name', '—')} ({latest.get('case_id', '—')})")
            st.sidebar.caption(f"Status: {latest.get('status', 'Open')}")
        else:
            st.sidebar.info("No active cases.")
        st.sidebar.caption("Operator access is read-only. Ask an Administrator to open or update cases.")


def render_administrator_sidebar() -> None:
    """Render the full sidebar for Administrator role: profile registration, AI config, admin actions."""
    st.sidebar.title("🔐 N-ONE Security Gate")
    if LOGO_PATH.is_file():
        st.sidebar.image(str(LOGO_PATH), width=180)
    st.sidebar.caption("RBAC access control for surveillance ops")

    try:
        credentials = load_auth_credentials()
    except RuntimeError:
        st.sidebar.error("Authentication is unavailable: required secrets are not configured.")
        st.sidebar.caption(
            "Configure ADMIN_USERNAME, ADMIN_PASSWORD, OPERATOR_USERNAME, and "
            "OPERATOR_PASSWORD in Streamlit Secrets "
            "or the process environment."
        )
        return

    if st.session_state.authenticated:
        if st.sidebar.button("🔒 Logout System", width='stretch'):
            st.session_state.streaming = False
            st.session_state.authenticated = False
            st.session_state.role = "Guest"
            st.rerun()
        st.sidebar.markdown(f"**Current Role:** {st.session_state.role}")
    else:
        st.sidebar.info("Login to access the command center.")
        username = st.sidebar.text_input("Username", key="login_username")
        password = st.sidebar.text_input("Password", type="password", key="login_password")
        if st.sidebar.button("Login", width='stretch'):
            now = time.monotonic()
            locked_until = st.session_state.get("login_locked_until", 0.0)
            if now < locked_until:
                remaining = max(1, int(locked_until - now) + 1)
                st.sidebar.error(f"Too many failed attempts. Try again in {remaining} seconds.")
                return

            authenticated_role = None
            if (
                hmac.compare_digest(username, credentials["ADMIN_USERNAME"])
                and hmac.compare_digest(password, credentials["ADMIN_PASSWORD"])
            ):
                authenticated_role = "Administrator"
            elif (
                hmac.compare_digest(username, credentials["OPERATOR_USERNAME"])
                and hmac.compare_digest(password, credentials["OPERATOR_PASSWORD"])
            ):
                authenticated_role = "Operator"

            if authenticated_role is not None:
                st.session_state.login_attempts = 0
                st.session_state.login_locked_until = 0.0
                st.session_state.authenticated = True
                st.session_state.role = authenticated_role
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                if st.session_state.login_attempts >= MAX_LOGIN_ATTEMPTS:
                    st.session_state.login_locked_until = now + LOGIN_LOCKOUT_SECONDS
                    st.session_state.login_attempts = 0
                    st.sidebar.error("Too many failed attempts. Login is locked for 60 seconds.")
                else:
                    st.sidebar.error("Invalid credentials.")

    if st.session_state.authenticated:
        st.sidebar.markdown("---")
        cpu_saver = st.sidebar.toggle(
            "CPU saver (recommended)",
            key="cpu_saver_mode",
            help="Uses the faster OpenCV detector, a smaller scan image, and a 2.5 FPS face-scan limit. Turn it off only when maximum detection frequency is required.",
        )
        if cpu_saver:
            current_backend = st.session_state.get("selected_backend", DEEPFACE_BACKEND)
            if current_backend != "opencv":
                st.session_state["cpu_saver_previous_backend"] = current_backend
                st.session_state["selected_backend"] = "opencv"
            st.sidebar.caption("Fast CPU profile: OpenCV detector, 640px scans, up to 2.5 face scans/sec.")
        elif st.session_state.get("cpu_saver_previous_backend"):
            st.session_state["selected_backend"] = st.session_state.pop(
                "cpu_saver_previous_backend"
            )

    if st.session_state.role == "Administrator":
        st.sidebar.markdown("---")
        st.sidebar.header("Administrator controls")
        photo_source = st.sidebar.radio(
            "Profile photo source",
            ["Guided multi-angle camera", "Upload single image"],
            horizontal=True,
            key="registration_photo_source",
        )
        if st.session_state.registration_capture_source != photo_source:
            st.session_state.registration_capture_source = photo_source
            st.session_state.registration_capture_started = False

        uploaded_photo = None
        enrollment_captures = st.session_state.setdefault(
            "enrollment_captures", {}
        )

        if photo_source == "Guided multi-angle camera":
            current_angle = next(
                (
                    angle
                    for angle in ENROLLMENT_ANGLES
                    if angle not in enrollment_captures
                ),
                None,
            )
            completed_count = len(enrollment_captures)
            st.sidebar.progress(
                completed_count / len(ENROLLMENT_ANGLES),
                text=f"Angle captures: {completed_count}/{len(ENROLLMENT_ANGLES)}",
            )
            if current_angle:
                st.sidebar.info(
                    f"Step {completed_count + 1}/{len(ENROLLMENT_ANGLES)} — "
                    f"{ENROLLMENT_INSTRUCTIONS[current_angle]}"
                )
                if not st.session_state.registration_capture_started:
                    st.sidebar.caption(
                        "Camera access stays off until you start this capture."
                    )
                    if st.sidebar.button(
                        f"Start {current_angle.title()} capture",
                        key=f"start_registration_capture_{current_angle}",
                        type="primary",
                        width="stretch",
                    ):
                        st.session_state.registration_capture_started = True
                        st.rerun()
                else:
                    angle_capture = st.sidebar.camera_input(
                        f"Capture {current_angle.title()} angle",
                        key=f"registration_camera_{current_angle}",
                        help="Keep one person centered and ensure the face is clearly visible.",
                        resolution="720p",
                    )
                    if angle_capture is not None and current_angle not in enrollment_captures:
                        prepared_crop, crop_message = prepare_single_face_crop(angle_capture)
                        if prepared_crop is None:
                            st.sidebar.warning(crop_message)
                        else:
                            enrollment_captures[current_angle] = angle_capture.getvalue()
                            st.session_state.registration_capture_started = False
                            st.sidebar.success(
                                f"{current_angle.title()} angle accepted. Next angle is ready."
                            )
                            st.rerun()

            if enrollment_captures:
                st.sidebar.caption("Captured angles")
                preview_columns = st.sidebar.columns(len(enrollment_captures))
                for preview_column, angle in zip(
                    preview_columns, ENROLLMENT_ANGLES
                ):
                    if angle in enrollment_captures:
                        crop, _ = prepare_single_face_crop(
                            BytesIO(enrollment_captures[angle])
                        )
                        if crop is not None:
                            preview_column.image(
                                cv2.cvtColor(crop, cv2.COLOR_BGR2RGB),
                                caption=angle.title(),
                                width="content",
                            )

                if st.sidebar.button("Clear angle captures", key="clear_enrollment_captures"):
                    enrollment_captures.clear()
                    st.session_state.registration_capture_started = False
                    st.rerun()
        else:
            uploaded_photo = st.sidebar.file_uploader(
                "Upload face image", type=["jpg", "jpeg", "png"], key="registration_upload"
            )

        prepared_crop = None
        if uploaded_photo is not None:
            prepared_crop, crop_message = prepare_single_face_crop(uploaded_photo)
            if prepared_crop is not None:
                st.sidebar.success(crop_message)
                st.sidebar.image(
                    cv2.cvtColor(prepared_crop, cv2.COLOR_BGR2RGB),
                    caption="Face-only profile preview",
                    width="content",
                )
            else:
                st.sidebar.warning(crop_message)

        with st.sidebar.form("registration_form"):
            reg_name = st.text_input("Full Name / Identifier")
            reg_role = st.selectbox(
                "Classification Role",
                ["Staff", "Victim"],
            )
            can_save = (
                photo_source == "Upload single image"
                or all(angle in enrollment_captures for angle in ENROLLMENT_ANGLES)
            )
            submitted = st.form_submit_button(
                "Save multi-angle profile"
                if photo_source == "Guided multi-angle camera"
                else "Save Profile",
                disabled=not can_save,
            )
            if submitted:
                if photo_source == "Guided multi-angle camera":
                    saved, save_message = save_registered_profile_captures(
                        reg_name,
                        reg_role,
                        enrollment_captures,
                        require_all_angles=True,
                    )
                else:
                    saved, save_message = save_registered_profile(
                        reg_name, reg_role, uploaded_photo
                    )
                if saved:
                    st.sidebar.success(f"Registered profile for {reg_name}")
                    st.session_state.last_status = "Profile saved"
                    enrollment_captures.clear()
                else:
                    st.sidebar.error(save_message)

        st.sidebar.markdown("---")
        st.sidebar.header("AI Model Configuration")
        with st.sidebar.expander("DeepFace Settings", expanded=False):
            st.session_state.selected_model = st.selectbox(
                "Facial Recognition Model",
                DEEPFACE_MODELS,
                index=(
                    DEEPFACE_MODELS.index(st.session_state.selected_model)
                    if st.session_state.selected_model in DEEPFACE_MODELS
                    else 0
                ),
                help="Choose the facial recognition model",
            )
            st.session_state.selected_backend = st.selectbox(
                "Face Detection Backend",
                DEEPFACE_BACKENDS,
                index=(
                    DEEPFACE_BACKENDS.index(st.session_state.selected_backend)
                    if st.session_state.selected_backend in DEEPFACE_BACKENDS
                    else 0
                ),
                help="Choose the face detection method",
            )
            st.session_state.selected_metric = st.selectbox(
                "Similarity Metric",
                DEEPFACE_METRICS,
                index=(
                    DEEPFACE_METRICS.index(st.session_state.selected_metric)
                    if st.session_state.selected_metric in DEEPFACE_METRICS
                    else 0
                ),
                help="Choose distance metric for comparison",
            )
            st.session_state.similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.similarity_threshold,
                step=0.05,
                help="Lower = more strict matching",
            )
            st.info(
                "Victim-search recommendation with the full DeepFace runtime: "
                "Facenet512 + retinaface + cosine. Start around 0.30–0.40 and "
                "calibrate using one genuine and one different-person test."
            )
            if DEEPFACE_IMPORT_ERROR:
                st.warning(
                    "Full DeepFace is unavailable here, so the app is using the "
                    "OpenCV/HOG fallback. It can detect faces, but registered and "
                    "Victim identity matches are disabled to prevent false positives. "
                    "Install TensorFlow/DeepFace to enable identity matching."
                )

        with st.sidebar.expander("Analysis Features", expanded=False):
            st.session_state.enable_attributes = st.checkbox(
                "Enable Facial Attributes (Age/Gender/Emotion/Race)",
                value=st.session_state.enable_attributes,
                help="Analyze demographic attributes",
            )
            st.session_state.enable_spoofing_detection = st.checkbox(
                "Enable Anti-Spoofing Detection",
                value=st.session_state.enable_spoofing_detection,
                help="Detect face spoofing/liveness attacks",
            )

        st.sidebar.markdown("---")
        st.sidebar.header("Admin Actions")
        st.sidebar.warning("These actions permanently delete local surveillance data.")
        deletion_confirmed = st.sidebar.checkbox(
            "I understand this cannot be undone",
            key="admin_deletion_confirmed",
        )
        if st.sidebar.button(
            "Clear registered profiles",
            width="stretch",
            type="primary",
            disabled=not deletion_confirmed,
        ):
            clear_registered_profiles()
            st.sidebar.success("All registered profiles deleted.")
            st.rerun()
        if st.sidebar.button(
            "Clear unknown face data",
            width="stretch",
            type="primary",
            disabled=not deletion_confirmed,
        ):
            clear_unknown_face_data()
            st.sidebar.success("Unknown-face photos and tracking records deleted.")
            st.rerun()
        if st.sidebar.button(
            "Reset audit logs",
            width="stretch",
            type="primary",
            disabled=not deletion_confirmed,
        ):
            clear_audit_log()
            st.sidebar.success("Audit logs reset.")
            st.rerun()
        if st.sidebar.button(
            "Clear all surveillance data",
            width="stretch",
            type="primary",
            disabled=not deletion_confirmed,
        ):
            clear_all_surveillance_data()
            st.sidebar.success("All registered, unknown, case, log, and temporary-upload data deleted.")
            st.rerun()

    return



def render_main_ui() -> None:
    """Main UI with 2-column layout: controls left, video feed right during live mode."""
    render_brand_logo()
    st.title("🎯 N-ONE COMMAND CENTER")

    # Load data
    log_df = pd.read_csv(CSV_LOG_PATH) if CSV_LOG_PATH.exists() and CSV_LOG_PATH.stat().st_size > 0 else pd.DataFrame()
    registered_df = get_registered_profiles_df()
    unknown_count = get_unknown_face_count()

    # ---------- CONTROL PANEL ----------
    with st.container(border=True):
        st.subheader("⚙️ Operational Console")

        # Row 1: Mode + Source
        col_mode, col_source = st.columns([1, 2])
        with col_mode:
            mode = st.selectbox(
                "Mode",
                ["1. Lost Person Search", "2. Member Attendance Logger", "3. Threat Detection Mode"],
                key="selected_mode", help="Select the primary mission for the AI."
            )
        with col_source:
            switch_to_browser = st.session_state.pop("switch_to_browser_camera", False)
            if switch_to_browser:
                st.session_state["input_source"] = "Browser Webcam (WebRTC)"
            camera_fallback_message = st.session_state.pop("camera_fallback_message", "")
            camera_fallback_details = st.session_state.pop("camera_fallback_details", "")
            source_type = st.radio(
                "Video Source",
                ["Browser Webcam (WebRTC)", "Laptop Webcam", "Recorded Video File", "IP Camera Stream"],
                horizontal=True,
                key="input_source",
                help="Laptop Webcam accesses server-attached cameras. If unavailable, browser WebRTC is offered.",
            )
            if camera_fallback_message:
                st.info(camera_fallback_message)
                if camera_fallback_details:
                    with st.expander("Local webcam attempt details"):
                        st.caption(camera_fallback_details)

        # Row 2: Source-specific config
        video_target = None
        browser_camera = source_type == "Browser Webcam (WebRTC)"
        with st.container():
            if source_type == "Laptop Webcam":
                video_target = 0
                st.caption("💻 Using server-attached webcam (device 0)")
            elif source_type == "Recorded Video File":
                uploaded_video = st.file_uploader("Upload Video File", type=["mp4", "avi", "mov"])
                if uploaded_video:
                    TEMP_VIDEO_PATH.write_bytes(uploaded_video.getbuffer())
                    video_target = str(TEMP_VIDEO_PATH)
            elif source_type == "IP Camera Stream":
                video_target = st.text_input("RTSP / HTTP Stream URL", placeholder="rtsp://user:pass@ip:554/stream", key="rtsp_url")

        # Row 3: Camera location + Victim selector (if in victim search)
        col_loc, col_victim = st.columns([1, 1])
        with col_loc:
            camera_location = st.text_input(
                "Camera location",
                key="camera_location",
                help="Saved with unknown tracking and victim sightings.",
            ).strip() or "Main Feed"

        victim_search_target = None
        with col_victim:
            if is_victim_search_mode(mode):
                victim_profiles = registered_df[registered_df["category"] == "Victim"]
                if victim_profiles.empty:
                    st.warning("No Victim profile registered. Admin must register a Victim first.")
                else:
                    victim_labels = {row["profile_id"]: row["name"] for _, row in victim_profiles.iterrows()}
                    victim_search_target = st.selectbox(
                        "Victim to search",
                        options=list(victim_labels),
                        format_func=lambda pid: victim_labels[pid],
                        key="victim_search_target",
                        help="Only this Victim is matched. Other faces tracked silently as unknown.",
                    )
                    st.caption("Victim search matches only selected target. Others → unknown DB.")

        # Row 4: Metrics (using custom metric cards)
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            render_metric_card("Role", st.session_state.role, icon="👤")
        with m2:
            render_metric_card("Registered", len(registered_df), icon="👥")
        with m3:
            render_metric_card("Unknown", unknown_count, icon="❓")
        with m4:
            render_metric_card("Log Events", len(log_df), icon="📋")

        # Row 5: Start/Stop button + Live status
        col_btn, col_status = st.columns([1, 3])
        with col_btn:
            button_label = "Stop Surveillance" if st.session_state.streaming else "Start Surveillance"
            if st.button(button_label, width='stretch', type="primary" if not st.session_state.streaming else "secondary"):
                if not st.session_state.streaming and video_target is None and not browser_camera:
                    st.error("Cannot start stream: no valid video source selected.")
                elif not st.session_state.streaming and is_victim_search_mode(mode) and not victim_search_target:
                    st.error("Select a Victim profile before starting Lost Person Search.")
                else:
                    st.session_state.streaming = not st.session_state.streaming
                    st.rerun()
        with col_status:
            if st.session_state.streaming:
                render_status_chip("LIVE", "live", "🔴")
            else:
                render_status_chip("IDLE", "idle", "⚪")

    # ---------- LIVE MODE: 2-column layout ----------
    if st.session_state.streaming:
        # LEFT COLUMN: Controls + Detection Results
        # RIGHT COLUMN: Video Feed
        left_col, right_col = st.columns([1, 2], gap="large")

        with left_col:
            with st.container(border=True):
                st.markdown("### 🎮 Live Controls")

                # Quick threshold slider (only for face modes)
                if is_victim_search_mode(mode) or is_member_attendance_mode(mode):
                    threshold = st.slider(
                        "Similarity Threshold",
                        0.0, 1.0,
                        st.session_state.get("similarity_threshold", COSINE_THRESHOLD),
                        0.01,
                        key="live_threshold",
                        help="Lower = stricter match"
                    )
                    st.session_state.similarity_threshold = threshold

                # Quick actions
                a1, a2 = st.columns(2)
                with a1:
                    if st.button("📸 Snapshot", width="stretch", disabled=not st.session_state.streaming):
                        st.session_state["request_snapshot"] = True
                with a2:
                    if st.button("⏹️ Stop", width="stretch", type="secondary"):
                        st.session_state.streaming = False
                        st.rerun()

            # Detection Results Panel
            with st.container(border=True):
                st.markdown("### 📡 Detection Results")
                status_area = st.empty()
                match_area = st.empty()
                victim_match_area = st.empty()
                render_detection_result(match_area)
                render_victim_found_result(victim_match_area)

                # Live status text
                status_text = st.session_state.get('last_status', "Idle")
                status_area.info(f"Status: {status_text}")

        with right_col:
            # Video Feed with wrapper
            with st.container(border=True):
                st.markdown("### 📹 Live Feed")
                frame_placeholder = st.empty()

        # Render the video stream (WebRTC or OpenCV)
        if browser_camera:
            frame_placeholder.empty()
            render_browser_camera(mode, victim_search_target, camera_location)
        elif video_target is not None:
            cap, source_status = open_video_source(video_target)
            if cap is None:
                if source_type == "Laptop Webcam":
                    st.session_state["switch_to_browser_camera"] = True
                    st.session_state["camera_fallback_message"] = (
                        "OpenCV could not access the server webcam. N-ONE switched to the browser camera; "
                        "allow camera access and press START in its panel."
                    )
                    st.session_state["camera_fallback_details"] = source_status
                    st.rerun()
                else:
                    st.session_state.streaming = False
                    st.error(source_status)
                    frame_placeholder.error(
                        "Feed unavailable. Select Recorded Video File, or allow webcam access "
                        "and use WebRTC when the app is running remotely."
                    )
            else:
                if source_status:
                    # We can't easily update left_col status_area from here without rerun
                    pass
                while st.session_state.streaming:
                    ret, frame = cap.read()
                    if not ret:
                        st.session_state.streaming = False
                        st.warning("Video stream ended or file finished.")
                        cap.release()
                        st.rerun()
                        break

                    if not _frame_has_content(frame):
                        st.session_state.streaming = False
                        message = (
                            "Camera returned a black/empty frame. Check camera permission, "
                            "another app using the camera, or use WebRTC for a remote app."
                        )
                        frame_placeholder.error(message)
                        cap.release()
                        break

                    annotated_frame, detection_summary = process_frame(
                        frame,
                        mode,
                        target_profile_id=victim_search_target,
                        location=camera_location,
                    )

                    # Update detection result panels in left column via session state
                    # The panels read from st.session_state.get("last_detection")
                    final_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                    frame_placeholder.image(final_frame, width='stretch')

                    time.sleep(
                        CPU_SAVER_DISPLAY_INTERVAL_SECONDS
                        if cpu_saver_enabled()
                        else 0.01
                    )

            if cap is not None and cap.isOpened():
                cap.release()
        else:
            frame_placeholder.info("Surveillance feed is offline. Select a source and start the stream.")

    else:
        # ---------- IDLE MODE: Show video placeholder + analysis panels ----------
        with st.container(border=True):
            st.markdown("### 📹 Video Feed")
            st.info("Surveillance feed is offline. Select a source and press Start Surveillance to begin.")
            # Show a placeholder image or just text
            st.image(str(LOGO_PATH) if LOGO_PATH.is_file() else None, caption="N-ONE Ready")

    # ---------- ANALYSIS PANELS (Tabs at bottom) ----------
    render_analysis_tabs(registered_df)
def render_face_inventory_panel(registered_df: pd.DataFrame | None = None) -> None:
    """Show registered-face categories and counts to Administrators and Operators."""
    profiles = registered_df if registered_df is not None else get_registered_profiles_df()
    staff_count = int((profiles["category"] == "Staff").sum()) if not profiles.empty else 0
    victim_count = int((profiles["category"] == "Victim").sum()) if not profiles.empty else 0

    st.markdown("---")
    st.subheader("Registered face inventory")
    count_col1, count_col2, count_col3 = st.columns(3)
    count_col1.metric("All registered faces", len(profiles))
    count_col2.metric("Staff", staff_count)
    count_col3.metric("Victim", victim_count)

    with st.container(border=True):
        selected_category = st.segmented_control(
            "Show registered faces",
            ["All", "Staff", "Victim"],
            default="All",
            key="registered_face_category",
            width="stretch",
        ) or "All"
        visible_profiles = profiles
        if selected_category != "All":
            visible_profiles = profiles[profiles["category"] == selected_category]

        if visible_profiles.empty:
            st.info(f"No {selected_category.lower()} profiles registered yet.")
        else:
            st.dataframe(
                visible_profiles[["name", "category", "file_name"]].rename(
                    columns={
                        "name": "Name",
                        "category": "Category",
                        "file_name": "Profile file",
                    }
                ),
                hide_index=True,
                width="stretch",
            )


def render_face_photo_gallery(registered_df: pd.DataFrame | None = None) -> None:
    """Let authenticated users view a selected registered, Victim, or unknown photo."""
    profiles = registered_df if registered_df is not None else get_registered_profiles_df()
    st.markdown("---")
    st.subheader("Face photo viewer")

    gallery_category = st.segmented_control(
        "Photo category",
        ["Registered", "Victim", "Unknown"],
        default="Registered",
        key="photo_view_category",
        width="stretch",
    ) or "Registered"

    selected_record = None
    if gallery_category in {"Registered", "Victim"}:
        candidates = profiles
        if gallery_category == "Victim":
            candidates = candidates[candidates["category"] == "Victim"]

        if candidates.empty:
            st.info(f"No {gallery_category.lower()} photos available.")
            return

        labels = {
            row["profile_id"]: f"{row['name']} ({row['category']})"
            for _, row in candidates.iterrows()
        }
        selected_id = st.selectbox(
            f"Select {gallery_category.lower()} profile",
            options=list(labels),
            format_func=lambda profile_id: labels[profile_id],
            key="selected_photo_profile",
        )
        selected_record = candidates[candidates["profile_id"] == selected_id].iloc[0]
    else:
        unknown_profiles = get_unknown_profiles_df()
        if unknown_profiles.empty:
            st.info("No unknown photos available.")
            return

        selected_id = st.selectbox(
            "Select unknown profile",
            options=unknown_profiles["unknown_id"].tolist(),
            key="selected_unknown_photo",
        )
        selected_record = unknown_profiles[
            unknown_profiles["unknown_id"] == selected_id
        ].iloc[0]

    image_path = Path(str(selected_record["image_path"]))
    with st.container(border=True):
        photo_col, details_col = st.columns([1, 2])
        with photo_col:
            if image_path.exists():
                st.image(
                    str(image_path),
                    caption=image_path.name,
                    width="content",
                )
            else:
                st.warning("Photo file is not available at the stored path.")

            if gallery_category in {"Registered", "Victim"}:
                angle_paths = get_profile_angle_paths(
                    str(selected_record["profile_id"])
                )
                if len(angle_paths) > 1:
                    st.caption("Saved profile angles")
                    angle_columns = st.columns(len(angle_paths))
                    for angle_column, (angle, angle_path) in zip(
                        angle_columns, sorted(angle_paths.items())
                    ):
                        angle_column.image(
                            str(angle_path),
                            caption=angle.title(),
                            width="content",
                        )

        with details_col:
            if gallery_category in {"Registered", "Victim"}:
                st.write(f"**Name:** {selected_record['name']}")
                st.write(f"**Category:** {selected_record['category']}")
                st.write(f"**Profile ID:** `{selected_record['profile_id']}`")
                if gallery_category == "Victim":
                    victim_details = get_victim_profile_details(
                        str(selected_record["profile_id"])
                    )
                    detail_labels = {
                        "approximate_age": "Approximate age",
                        "description": "Identifying details",
                        "last_known_area": "Last known area",
                        "contact": "Family / case contact",
                        "notes": "Case notes",
                    }
                    for field, label in detail_labels.items():
                        value = str(victim_details.get(field, "")).strip()
                        if value and value.lower() != "nan":
                            st.write(f"**{label}:** {value}")
            else:
                st.write(f"**Unknown ID:** `{selected_record['unknown_id']}`")
                assigned_name = selected_record.get("assigned_name", "")
                if assigned_name and assigned_name != "nan":
                    st.write(f"**Assigned name:** {assigned_name}")
                st.write(
                    f"**First seen:** {selected_record.get('first_seen_timestamp', '') or 'Unavailable'}"
                )
                st.write(
                    f"**Last seen:** {selected_record.get('last_seen_timestamp', '') or 'Unavailable'}"
                )
                st.write(
                    f"**Last location:** {selected_record.get('last_known_location', '') or 'Unavailable'}"
                )
                if st.session_state.get("role") == "Administrator":
                    st.markdown("#### Register this Unknown as a known person")
                    st.caption(
                        "Confirm the person's identity before enrollment. Their original Unknown photo and sightings stay in the audit archive."
                    )
                    profile_category = st.selectbox(
                        "Register as",
                        options=["Staff", "Victim"],
                        key=f"convert_category_{selected_record['unknown_id']}",
                        help="Staff profiles are available for known-person matching; Victim profiles are available in Victim Search.",
                    )
                    with st.form(f"convert_unknown_{selected_record['unknown_id']}"):
                        victim_name = st.text_input(
                            "Confirmed name or identifier",
                            key=f"convert_name_{selected_record['unknown_id']}",
                        )
                        if profile_category == "Victim":
                            victim_age = st.text_input(
                                "Approximate age (optional)",
                                key=f"convert_age_{selected_record['unknown_id']}",
                            )
                            victim_description = st.text_area(
                                "Identifying details (optional)",
                                key=f"convert_description_{selected_record['unknown_id']}",
                            )
                            victim_area = st.text_input(
                                "Last known area (optional)",
                                key=f"convert_area_{selected_record['unknown_id']}",
                            )
                            victim_contact = st.text_input(
                                "Family / case contact (optional)",
                                key=f"convert_contact_{selected_record['unknown_id']}",
                            )
                            victim_notes = st.text_area(
                                "Case notes (optional)",
                                key=f"convert_notes_{selected_record['unknown_id']}",
                            )
                        identity_confirmed = st.checkbox(
                            "I verified that this photo and the entered details belong to this person.",
                            key=f"convert_confirm_{selected_record['unknown_id']}",
                        )
                        submitted = st.form_submit_button(
                            "Add to known profiles", type="primary", width="stretch"
                        )
                    if submitted:
                        converted, message = convert_unknown_to_victim(
                            unknown_id=str(selected_record["unknown_id"]),
                            name=victim_name,
                            profile_category=profile_category,
                            approximate_age=(
                                victim_age if profile_category == "Victim" else ""
                            ),
                            description=(
                                victim_description if profile_category == "Victim" else ""
                            ),
                            last_known_area=(
                                victim_area if profile_category == "Victim" else ""
                            ),
                            contact=(
                                victim_contact if profile_category == "Victim" else ""
                            ),
                            notes=(
                                victim_notes if profile_category == "Victim" else ""
                            ),
                            confirmed=identity_confirmed,
                        )
                        if converted:
                            st.toast(message)
                            st.rerun()
                        else:
                            st.error(message)


def render_analysis_tabs(registered_df: pd.DataFrame) -> None:
    """Group secondary panels into tabs: Inventory, Gallery, Cases, Analytics, Logs."""
    tab_inventory, tab_gallery, tab_cases, tab_analytics, tab_logs = st.tabs([
        "📋 Inventory", "🖼️ Gallery", "📁 Cases", "🔬 Analytics", "📊 Logs"
    ])

    with tab_inventory:
        render_face_inventory_panel(registered_df)

    with tab_gallery:
        render_face_photo_gallery(registered_df)

    with tab_cases:
        render_case_command_center(registered_df)

    with tab_analytics:
        render_facial_analytics_panel()

    with tab_logs:
        render_log_viewer()


def render_facial_analytics_panel() -> None:
    """Render facial analytics and verification tools."""
    st.markdown("---")
    st.subheader("🔬 Facial Analytics & Verification Tools")

    analytics_tab1, analytics_tab2, analytics_tab3 = st.tabs(
        ["Face Comparison", "Batch Analysis", "Detection Tuning"]
    )
    
    with analytics_tab1:
        st.write("**1-to-1 Face Verification**")
        col1, col2 = st.columns(2)
        
        with col1:
            uploaded_img1 = st.file_uploader("Upload First Face Image", type=["jpg", "jpeg", "png"], key="verify_img1")
        with col2:
            uploaded_img2 = st.file_uploader("Upload Second Face Image", type=["jpg", "jpeg", "png"], key="verify_img2")
        
        if uploaded_img1 and uploaded_img2 and st.button("Verify Match"):
            temp_path1 = ROOT_DIR / "temp_verify_1.jpg"
            temp_path2 = ROOT_DIR / "temp_verify_2.jpg"
            
            with Image.open(uploaded_img1) as img:
                img.convert("RGB").save(temp_path1)
            with Image.open(uploaded_img2) as img:
                img.convert("RGB").save(temp_path2)
            
            result = verify_face_pair(str(temp_path1), str(temp_path2), st.session_state.selected_model)
            
            col_result1, col_result2, col_result3 = st.columns(3)
            col_result1.metric("Match Status", "✅ MATCH" if result.get("verified") else "❌ NO MATCH")
            col_result2.metric("Distance", f"{result.get('distance', 0):.4f}")
            col_result3.metric("Threshold", f"{result.get('threshold', 0):.4f}")
            
            if not result.get("verified"):
                st.warning("Faces do not match with current threshold settings.")
            else:
                st.success("Faces successfully verified as the same person!")
            
            temp_path1.unlink(missing_ok=True)
            temp_path2.unlink(missing_ok=True)
    
    with analytics_tab2:
        st.write("**Batch Facial Attribute Analysis**")
        uploaded_batch = st.file_uploader("Upload Image for Analysis", type=["jpg", "jpeg", "png"], key="batch_analysis")
        
        if uploaded_batch and st.button("Analyze Attributes"):
            temp_image = ROOT_DIR / "temp_analysis.jpg"
            with Image.open(uploaded_batch) as img:
                img.convert("RGB").save(temp_image)
            
            analysis_frame = cv2.imread(str(temp_image))
            if analysis_frame is None:
                analysis_results = []
                st.error("The uploaded image could not be read for analysis.")
            else:
                analysis_results = analyze_facial_attributes(analysis_frame, [])
            
            if analysis_results:
                for idx, result in enumerate(analysis_results):
                    st.write(f"**Face #{idx + 1}**")
                    col_a1, col_a2, col_a3, col_a4 = st.columns(4)
                    col_a1.metric("Age", f"{result.get('age', 'N/A')} yrs")
                    col_a2.metric("Gender", result.get('dominant_gender', 'N/A'))
                    col_a3.metric("Emotion", result.get('dominant_emotion', 'N/A'))
                    col_a4.metric("Race", result.get('dominant_race', 'N/A'))
            else:
                st.info("No faces detected or attribute analysis unavailable.")
            
            temp_image.unlink(missing_ok=True)
    
    with analytics_tab3:
        st.write("**Detection Model Tuning**")
        st.info("Model settings are managed by the platform owner and are read-only for User accounts.")
        
        col_tune1, col_tune2 = st.columns(2)
        with col_tune1:
            st.write("**Current Model Settings:**")
            st.code(f"""
Model: {st.session_state.selected_model}
Backend: {st.session_state.selected_backend}
Metric: {st.session_state.selected_metric}
Threshold: {st.session_state.similarity_threshold:.2f}
            """)
        
        with col_tune2:
            st.write("**Features Enabled:**")
            features = []
            if st.session_state.enable_attributes:
                features.append("✓ Facial Attributes")
            if st.session_state.enable_spoofing_detection:
                features.append("✓ Anti-Spoofing")
            if features:
                st.write("\n".join(features))
            else:
                st.write("No additional features enabled")


def render_log_viewer() -> None:
    st.markdown("---")
    st.subheader("📊 Structured Audit & Detection Logs")
    if CSV_LOG_PATH.exists() and CSV_LOG_PATH.stat().st_size > 0:
        log_df = pd.read_csv(CSV_LOG_PATH).sort_values(by="Timestamp", ascending=False)
        st.dataframe(log_df, width='stretch', height=300)
    else:
        st.info("No audit logs recorded yet.")

    st.subheader("🕵️ Unknown Persons Database")
    if UNKNOWN_DB_PATH.exists() and UNKNOWN_DB_PATH.stat().st_size > 0:
        try:
            unknown_df = pd.read_csv(UNKNOWN_DB_PATH).sort_values(by="last_seen_timestamp", ascending=False)
            st.dataframe(unknown_df, width='stretch', height=300)
        except pd.errors.EmptyDataError:
            st.info("Unknown person database is empty.")
    else:
        st.info("No unknown persons recorded yet.")

    st.subheader("Victim sighting history")
    victim_history = get_victim_sighting_history()
    if victim_history.empty:
        st.info("No Victim sightings recorded yet.")
    else:
        st.dataframe(
            victim_history[["name", "timestamp", "location"]].rename(
                columns={
                    "name": "Victim",
                    "timestamp": "Last seen",
                    "location": "Camera location",
                }
            ),
            hide_index=True,
            width="stretch",
            height=300,
        )


def main() -> None:
    """Main function to run the Streamlit application."""
    initialize_directories()
    initialize_log_files()
    configure_session_state()

    if st.session_state.get("role") == "Administrator":
        render_administrator_sidebar()
    else:
        render_operator_sidebar()
    if not st.session_state.authenticated:
        render_brand_logo()

    if st.session_state.authenticated:
        model_name, detector_backend, _ = get_runtime_face_settings()
        load_known_face_encodings(model_name, detector_backend)
        render_main_ui()
    else:
        st.warning("🔒 System locked. Please authenticate via the sidebar.")


if __name__ == "__main__":
    main()
