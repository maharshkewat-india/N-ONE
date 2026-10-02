# N-ONE Report Evidence Register

Audit basis: repository state inspected on 2026-09-25. This register records facts used by the report. Where a source is descriptive rather than executable, that distinction is stated.

## Project identity

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Project name is N-ONE / No One Escapes | `README.md`, `SYNOPSIS.md` | Title and synopsis headings | Front matter; Chapters 1, 18 |
| Application is a Streamlit dashboard | `app.py` | `import streamlit as st`; `st.set_page_config`; `main()` | Chapters 6, 7, 9, 12 |
| Three modes exist | `app.py` | `Select Active Surveillance Mode` contains Lost Person Search, Member Attendance Logger, Threat Detection Mode | Chapters 3, 6, 12 |
| Roles are Administrator and Operator | `app.py` | `authenticated_role = "Administrator"` and `authenticated_role = "Operator"` | Chapters 2, 6, 16 |
| Authentication fails closed when required secrets are missing | `app.py` | `load_auth_credentials()` raises `RuntimeError` for missing values | Chapters 6, 16 |
| Credentials are read from environment or Streamlit Secrets | `app.py`, `.env.example` | `_read_secret()` checks `os.getenv()` then `st.secrets` | Chapters 7, 16 |
| Constant-time credential comparison is used | `app.py` | Login uses `hmac.compare_digest` | Chapter 16 |
| Five failed attempts trigger a 60-second session lockout | `app.py` | `MAX_LOGIN_ATTEMPTS = 5`; `LOGIN_LOCKOUT_SECONDS = 60` | Chapter 16 |

## Registration and identity processing

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Registration accepts upload or guided browser camera capture | `app.py` | Sidebar radio values and `st.sidebar.camera_input` | Chapters 6, 12, 13 |
| Guided registration uses five angles | `app.py` | `ENROLLMENT_ANGLES = ("front", "left", "right", "up", "down")` | Chapters 6, 12 |
| Exactly one face is required for registration | `app.py` | `prepare_single_face_crop()` rejects zero or multiple regions | Chapters 4, 6, 12, 15 |
| Minimum detected crop dimensions are 80x80 pixels | `app.py` | `if width < 80 or height < 80` | Chapters 6, 13 |
| Saved registration data is a padded face crop | `app.py` | Padding is 25% of the larger dimension before `cv2.imwrite` | Chapters 6, 12, 13 |
| Current profile prefixes are Staff and Victim | `app.py` | `profile_id = f"{prefix}_{safe_name}"` | Chapters 6, 11 |
| Legacy Member and Lost prefixes are normalized | `app.py`, `tests/test_face_inventory.py` | `get_profile_category()` maps Member to Staff and Lost to Victim | Chapters 6, 15 |
| Multi-angle files share one profile ID | `app.py` | `get_profile_id()` splits on `__`; cache stores angle | Chapters 6, 11 |
| Known embeddings are kept in a process-global cache | `app.py` | `KNOWN_FACE_ENCODINGS`; `load_known_face_encodings()` | Chapters 6, 9, 12 |
| Distance matching supports cosine, Euclidean, and normalized Euclidean | `app.py` | `calculate_face_distance()` branches on metric | Chapters 7, 13, 14 |
| Default source configuration is Facenet, OpenCV, cosine, threshold 0.40 | `app.py`, `AI_MODEL_CONFIGURATION.md` | Constants `DEEPFACE_MODEL`, `DEEPFACE_BACKEND`, `DEEPFACE_METRIC`, `COSINE_THRESHOLD` | Chapters 7, 12, 14 |
| Full DeepFace runtime is conditional | `deepface_adapter.py`, `AI_MODEL_CONFIGURATION.md` | Adapter attempts import and falls back on import failure | Chapters 7, 8, 9, 17 |
| Active fallback uses Haar detection and HOG/CLAHE features | `deepface_adapter.py` | `OpenCVFaceBackend.detect_faces()` and `extract_embedding()` | Chapters 7, 9, 12, 17 |
| Fallback identity matching is disabled for high-impact Victim identification | `app.py` | `reliable_face_matching_available()` and `known_match = None` when fallback active | Chapters 6, 12, 16, 17 |

## Operational modes

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Victim Search requires one selected Victim | `app.py` | Victim selector and start validation | Chapters 6, 12 |
| Victim Search filters known matching by target profile and Victim role | `app.py` | `find_face_in_known_cache(... profile_id=target_profile_id, role="Victim")` | Chapters 6, 12, 13 |
| Non-target faces are displayed as face detected/no match in Victim Search | `app.py` | Victim branch labels unmatched faces without identity | Chapters 6, 12 |
| Victim sightings are written with location and duplicate suppression | `app.py` | `record_victim_sighting()` writes `victim_sighting_log.csv` and suppresses same location under 60 seconds | Chapters 6, 10, 12 |
| Staff/attendance mode compares against registered profiles | `app.py` | Attendance branch uses unrestricted known cache | Chapters 6, 12 |
| Unknown faces receive sequential IDs | `app.py` | `get_next_unknown_id()` returns `unknown_001`, etc. | Chapters 6, 11, 12 |
| Unknown photos and metadata are persisted | `app.py` | `register_new_unknown()`, `log_sighting()`, `update_unknown_sighting()` | Chapters 6, 10, 11, 12 |
| Unknown sighting writes are throttled per ID/location pair | `app.py` | `UNKNOWN_SIGHTING_WRITE_INTERVAL_SECONDS = 2.0` | Chapters 6, 12 |
| Threat mode is exclusive of face recognition | `app.py` | `if "Threat" not in mode`; threat branch returns before face pipeline | Chapters 6, 9, 12 |
| Threat detection is heuristic contour and warm-colour analysis | `app.py` | `check_weapon_contours()` uses Canny, morphology, contour shape, HSV mask | Chapters 6, 12, 13, 16 |
| Threat labels are explicitly possible alerts | `app.py` | Labels `Possible weapon`, `Possible fire`; docstring says contours cannot prove a weapon | Chapters 4, 6, 16, 17 |

## Sources and storage

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Registered images are stored under `registered_faces/` | `app.py` | `REG_DIR = ROOT_DIR / "registered_faces"` | Chapters 6, 9, 11 |
| Unknown images are stored under `unknown_faces/` | `app.py` | `UNKNOWN_DIR = ROOT_DIR / "unknown_faces"` | Chapters 6, 9, 11 |
| Main audit CSV fields are Timestamp, Mode, Subject_ID, Role, Event_Type, Details | `app.py` | `initialize_log_files()` | Chapters 6, 10, 11 |
| Unknown database fields are known | `app.py` | `initialize_log_files()` creates six-column CSV | Chapters 10, 11 |
| Unknown sighting fields are sighting_id, unknown_id, timestamp, location | `app.py` | `initialize_log_files()` | Chapters 10, 11 |
| Victim sighting fields are profile_id, name, timestamp, location | `app.py` | `initialize_log_files()` | Chapters 10, 11 |
| Browser camera uses optional WebRTC/PyAV dependencies | `app.py`, `requirements.txt` | Optional import and conditional dependency | Chapters 7, 8, 9, 12 |
| OpenCV handles local webcam, files, and IP streams | `app.py` | `open_video_source()` and source selector | Chapters 6, 7, 12 |

## Evaluation evidence

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Benchmark measured Facenet, Facenet512, ArcFace | `evaluation/results/model_comparison.csv` | Three measured rows | Chapter 14 |
| Detector/backend in benchmark was RetinaFace | `docs/AI_MODEL_EVALUATION_REPORT.md`, `performance_results.csv` | Protocol and result column | Chapters 7, 14 |
| Metric was cosine | `docs/AI_MODEL_EVALUATION_REPORT.md`, CSVs | Protocol and `distance_metric=cosine` | Chapters 7, 14 |
| Threshold-0.40 trials were 32 genuine and 60 impostor | `model_comparison.csv` | `genuine_trials=32`, `impostor_trials=60` | Chapter 14 |
| Facenet at 0.40: TP 21, TN 60, FP 0, FN 11, recall 0.65625, F1 0.7924528301886793 | `model_comparison.csv` | Exact measured row | Chapter 14 |
| Facenet512 at 0.40: TP 22, TN 60, FP 0, FN 10, recall 0.6875, F1 0.8148148148148148 | `model_comparison.csv` | Exact measured row | Chapter 14 |
| ArcFace at 0.40: TP 23, TN 60, FP 0, FN 9, recall 0.71875, F1 0.8363636363636363 | `model_comparison.csv` | Exact measured row | Chapter 14 |
| All three had zero false victim matches in this sample at 0.40 | `model_comparison.csv` | `false_victim_matches=0` for each | Chapter 14 |
| Threshold sweep includes 0.20 through 0.60 | `threshold_comparison.csv` | Exact threshold rows | Chapter 14 |
| At higher thresholds false accepts appeared in the sweep | `threshold_comparison.csv` | Facenet FP 1 at 0.50/0.55 and FP 2 at 0.60 | Chapter 14 |
| Performance rows measured CPU inference latency and derived FPS | `performance_results.csv` | 55 images per model; latency and FPS columns | Chapter 14 |
| Performance figures are benchmark-run measurements, not application-wide guarantees | `docs/AI_MODEL_EVALUATION_REPORT.md` | Protocol and limitations | Chapters 8, 14, 17 |
| Multi-frame metrics are unavailable | `multi_frame_results.csv` | All models and 1/3/5 rows are `not_available` | Chapters 14, 17 |
| LFW was used for impostor sources | `evaluation/impostor_sources.csv` | Source dataset and source reference | Chapter 14 |
| Dataset validation tests exist | `tests/test_evaluation_dataset.py`, `tests/test_evaluation_collector.py` | Structure, metadata, path containment, face-count tests | Chapter 15 |

## Test evidence

| Fact | Source | Evidence | Used in |
|---|---|---|---|
| Adapter exposes represent and find | `tests/test_deepface_adapter.py` | Assertions on backend interface | Chapter 15 |
| Inventory tests cover prefixes and unique unknown counts | `tests/test_face_inventory.py` | Assertions for Staff/Victim/Member/Lost and duplicate IDs | Chapter 15 |
| Tests cover Victim-only cache filtering | `tests/test_face_inventory.py` | `test_known_face_cache_can_be_limited_to_one_victim` | Chapter 15 |
| Tests cover all saved angles | `tests/test_face_inventory.py` | `test_known_face_database_refresh_includes_all_saved_angles` | Chapter 15 |
| Browser tests distinguish unmatched, invalid fallback, fallback, and neural selected-Victim cases | `tests/test_face_inventory.py` | Four browser annotation tests | Chapter 15 |
| Collector prevents dataset path escape and validates face counts | `tests/test_evaluation_collector.py` | Path and validation tests | Chapters 15, 16 |
| A prior project audit recorded six passing tests | `project_report.md` | Historical audit statement; not a current rerun | Chapter 15 |
| Current workspace test rerun was unavailable | `new_venv`, system Python | `pytest` is not installed in either attempted environment | Chapter 15 |
| A prior broader test run recorded 24 passed, 1 failed, and 1 error | prior audit output referenced during 2026-09-25 audit | Historical result; failure was metadata-header mismatch and error was temporary-directory setup | Chapter 15 |
| Dataset metadata test expects a different header order from checked-in CSV/collector schema | `tests/test_evaluation_dataset.py`, `evaluation/collector.py`, `evaluation/dataset_metadata.csv` | Test expects `file_path` first while checked-in schema begins with `id` | Chapter 15 |

## Evidence limitations

- The repository contains only one application module plus the adapter; the vendored `deepface/` tree is treated as a dependency, not as N-ONE-authored application logic.
- Staff recognition, unknown re-identification, and threat detection do not have their own measured accuracy tables in the repository.
- Browser WebRTC annotations deliberately avoid CSV and session-state writes from the worker thread, so browser and OpenCV paths are not behaviorally identical.
- The repository does not provide measured retention, scalability, maximum camera count, RAM consumption for the application, or a production deployment security assessment.
- Academic identity details, certificate signatures, plagiarism results, publications, and approved screenshots are absent.
- `evaluation/README.md` and `evaluation/dataset/README.md` contain legacy text saying that no real evaluation data is present, which conflicts with the populated dataset and measured result CSVs. The measured CSVs are treated as the stronger direct evidence; the contradiction remains recorded for cleanup.
- The requested DOCX/PDF page count cannot be verified from the Markdown source alone. No generated paginated Word/PDF artifact was present in the audited repository.

## Fresh audit additions - 2026-10-01

| Claim | Evidence file | Function/section | Evidence type | Verified status |
|---|---|---|---|---|
| The app starts without source modification | `app.py`, live run on port 8503 | `main()` | Runtime observation; HTTP 200; page title `N-ONE : NO ONE ESCAPES` | Verified |
| The current environment lacks the neural runtime | `app.py`, `deepface_adapter.py` | import boundary and fallback warning | Runtime warning: `No module named 'tensorflow'` | Verified |
| Victim Search restricts visible identity matching to the selected Victim | `app.py` | `process_frame()` and `annotate_browser_frame()` | `profile_id` and `role="Victim"` filters | Verified |
| Fallback mode does not label registered identities | `app.py` | `reliable_face_matching_available()` | Explicit source gate and status text | Verified |
| Threat mode is heuristic and separate from face recognition | `app.py` | `check_weapon_contours()`, `process_frame()` | Canny/contour/HSV code path | Verified |
| Dataset contains 11 enrollment, 32 genuine, and 12 impostor images | `evaluation/dataset_metadata.csv` | metadata partitions | CSV count and path existence audit | Verified |
| ArcFace is strongest within the measured protocol at threshold 0.40 | `evaluation/results/model_comparison.csv` | model comparison | TP/TN/FP/FN and derived metrics | Verified within dataset/protocol only |
| Threshold sweep includes measured rows | `evaluation/results/threshold_comparison.csv` | threshold comparison | CSV rows from 0.20 through 0.60 | Verified |
| Performance was measured on CPU only | `evaluation/results/performance_results.csv` | performance table | latency and derived FPS fields | Verified; GPU unavailable |
| Multi-frame evaluation is unavailable | `evaluation/results/multi_frame_results.csv` | 1/3/5 frame rows | Explicit `not_available` status | Verified |
| Fresh project tests are not fully passing | pytest output from 2026-10-01 | root `tests/` | 24 passed, 2 failed | Verified |
| Threshold script has a syntax error | `evaluation/scripts/evaluate_thresholds.py` | `dataset_ready()` | `py_compile` output: unmatched `)` | Verified |
| Screenshot files are not currently present | `report_evidence/screenshots/` | screenshot inventory | Fresh directory inventory returned zero files | Verified |
| Staff, Unknown Re-ID, and Threat accuracy are unavailable | `N_ONE_REPORT_TESTING.md` and evaluation results | coverage register | No dedicated benchmarks | Verified |

The fresh runtime audit intentionally did not retain a screenshot containing credentials. The browser login page and fallback warning were inspected live, but no credential-bearing image is treated as report evidence.
