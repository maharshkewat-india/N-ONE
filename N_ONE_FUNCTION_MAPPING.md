# N-ONE Function Mapping

Audit basis: source inspection completed 2026-10-01. This mapping covers N-ONE-authored project code. The bundled `deepface/` directory is treated as a dependency tree; its internal functions are not represented as N-ONE application functions.

## Application functions (`app.py`)

| Function / class | Lines | Purpose | Inputs | Outputs | Dependencies and callers |
|---|---:|---|---|---|---|
| `_read_secret` | 41 | Read a credential from environment, then Streamlit Secrets | secret name | string or `None` | `os`, `st.secrets`; called by `load_auth_credentials` |
| `load_auth_credentials` | 55 | Load four required Admin/Operator credentials and fail closed if missing | none | credential dictionary | `_read_secret`; sidebar |
| `reliable_face_matching_available` | 193 | Gate identity matching on neural DeepFace import availability | none | bool | `DEEPFACE_IMPORT_ERROR`; frame paths |
| `ensure_unknown_face_cache` | 247 | Build or refresh the in-memory unknown embedding index | model, detector | none | `DeepFace.represent`; unknown matching |
| `find_face_in_unknown_cache` | 302 | Find closest cached unknown under metric-specific threshold | embedding, metric, model, detector | match dictionary or `None` | `calculate_face_distance`; `process_frame` |
| `initialize_directories` | 334 | Create profile, log, and unknown directories | none | none | `main` |
| `initialize_log_files` | 341 | Create CSV files and headers if absent or empty | none | none | `main`, cleanup functions |
| `log_event` | 361 | Append an audit/detection event and update session status | mode, subject, role, event, details | none | Pandas CSV append; recognition and threat paths |
| `get_next_unknown_id` | 372 | Generate the next sequential application unknown ID | none | string such as `unknown_001` | unknown CSV; `register_new_unknown` |
| `get_profile_category` | 386 | Normalize filename prefix to Staff or Victim | profile stem | category string | inventory and cache loading |
| `get_profile_name` | 393 | Convert stored profile stem to display name | profile stem | string | inventory and result panels |
| `get_profile_id` | 400 | Remove angle suffix from a profile stem | profile stem | profile ID | inventory and matching |
| `get_profile_angle` | 405 | Extract angle or default to `front` | profile stem | angle string | inventory and registration |
| `get_profile_angle_paths` | 410 | Find all image files for one profile | profile ID | angle-to-path dictionary | profile gallery and result card |
| `get_registered_profiles_df` | 425 | Build the registered inventory from local image files | none | Pandas DataFrame | inventory, victim selector, cache |
| `get_unknown_profiles_df` | 465 | Reconcile unknown CSV rows with available photos | none | Pandas DataFrame | gallery and count display |
| `is_victim_search_mode` | 545 | Identify target-restricted search mode | mode | bool | frame and UI paths |
| `is_member_attendance_mode` | 550 | Identify attendance mode | mode | bool | frame path |
| `record_victim_sighting` | 555 | Append victim location history with 60-second duplicate suppression | profile ID, name, location | bool written/not written | victim match path |
| `get_victim_sighting_history` | 590 | Read latest sighting per location | optional profile ID | DataFrame | result card and logs |
| `get_runtime_face_settings` | 612 | Read selected model, detector, and metric with defaults | session state | tuple | all matching paths |
| `represent_registered_face` | 621 | Represent saved face crops, including full-image fallback retry | image path, model, detector | representation list | `load_known_face_encodings` |
| `load_known_face_encodings` | 660 | Refresh global known-profile cache from registered images | model, detector | none | authenticated startup and registration |
| `calculate_face_distance` | 711 | Validate vectors and compute cosine, Euclidean, or normalized Euclidean distance | two vectors, metric | float distance | known/unknown matchers |
| `find_face_in_known_cache` | 739 | Select nearest registered embedding after role/profile filtering | embedding, threshold, optional profile/role, metric | match dictionary or `None` | `process_frame`, browser callback |
| `register_new_unknown` | 810 | Save unmatched crop, append unknown database, and log first sighting | crop, location, mode, model, metric | unknown ID | `process_frame` |
| `log_sighting` | 836 | Append one unknown sighting record | unknown ID, timestamp, location | none | registration and update paths |
| `get_last_unknown_sighting` | 849 | Recover prior timestamp and location for an unknown | unknown ID | dictionary | result display |
| `update_unknown_sighting` | 886 | Update last-seen data and throttle repeat writes | unknown ID, location, mode | bool | re-identification path |
| `verify_face_pair` | 947 | Expose one-to-one DeepFace verification | two image paths, model | result dictionary | analytics panel |
| `detect_spoofing` | 962 | Call optional DeepFace anti-spoofing API | frame | result dictionary | available helper; not part of default live pipeline |
| `get_face_embeddings` | 976 | Request DeepFace representations for a frame | frame, model | list | available helper |
| `check_weapon_contours` | 990 | Produce heuristic possible-weapon and possible-fire boxes | BGR frame | bool and labeled boxes | threat-only frame path |
| `process_frame` | 1058 | Main recorded/local/IP frame pipeline | frame, mode, target, location | annotated frame and summary | detection, matching, unknown, logging helpers |
| `annotate_browser_frame` | 1357 | Worker-safe WebRTC annotation path | frame, mode, target, model, detector, metric, threshold, location, sink | annotated frame | browser processor; intentionally avoids state/disk writes |
| `BrowserCameraProcessor` | 1474 | WebRTC worker adapter | stream configuration | video frames and latest victim status | `annotate_browser_frame` |
| `render_browser_camera` | 1513 | Render WebRTC component and status fragment | mode, target, location | UI | WebRTC dependency |
| `render_browser_victim_status` | 1549 | Poll worker result and display a victim card | WebRTC context | UI | Streamlit fragment |
| `render_detection_result` | 1574 | Render latest recognition/unknown/threat state | container | UI | session state |
| `render_victim_found_result` | 1635 | Render selected-victim result and location history | container | UI | session state and CSV history |
| `open_video_source` | 1692 | Probe file or Windows webcam backends for usable frames | video target | capture and status | OpenCV |
| `configure_session_state` | 1743 | Initialize per-session defaults | none | none | `main` |
| `detect_face_regions` | 1777 | Return face boxes from adapter or DeepFace extraction | image | list of regions | registration |
| `prepare_single_face_crop` | 1805 | Decode, detect, enforce one face and crop with 25% padding | uploaded file | crop and message | registration |
| `save_registered_profile_captures` | 1844 | Validate and replace one- or five-angle profile captures | name, role, captures, requirement flag | success and message | registration UI |
| `clear_audit_log` | 1909 | Delete and recreate audit/victim logs | none | none | Admin action |
| `clear_registered_profiles` | 1918 | Delete local registered images and clear cache | none | none | Admin action |
| `clear_unknown_face_data` | 1926 | Delete unknown images and tracking CSVs | none | none | Admin action |
| `clear_all_surveillance_data` | 1948 | Compose all destructive local cleanup operations | none | none | Admin action |
| `render_sidebar` | 1963 | Render authentication, role controls, registration, model controls, cleanup | session state | UI | `main` |
| `render_main_ui` | 2282 | Render mode/source controls, target selection, live feed, inventory | session state | UI | `main` |
| `render_facial_analytics_panel` | 2585 | Render verification, attribute, and tuning utilities | session state | UI | `main` |
| `render_log_viewer` | 2683 | Render audit, unknown, and victim histories | local CSVs | UI | `main` |
| `main` | 2721 | Initialize storage/state, authenticate, and render app | none | UI/application execution | Streamlit entry point |

## Adapter functions (`deepface_adapter.py`)

| Function / class | Lines | Purpose | Inputs | Outputs | Dependencies |
|---|---:|---|---|---|---|
| `cosine_distance` | 17 | Safe cosine distance without SciPy | two arrays | float | NumPy |
| `OpenCVFaceBackend._init_opencv` | 39 | Load frontal/profile/eye Haar cascades and optional LBPH object | none | none | OpenCV |
| `OpenCVFaceBackend.detect_faces` | 79 | Detect frontal and mirrored profiles with equalization and optional upscaling | BGR/gray array | face dictionaries | OpenCV |
| `OpenCVFaceBackend.is_valid_face_region` | 155 | Reject small, implausible, or eye-free fallback regions | image, region | bool | OpenCV |
| `OpenCVFaceBackend.extract_embedding` | 211 | Generate CLAHE-normalized HOG vector | face ROI | NumPy vector or `None` | OpenCV |
| `OpenCVFaceBackend.represent` | 268 | DeepFace-compatible fallback representation API | image, model, detection flags | representation list | detector and HOG |
| `OpenCVFaceBackend.find` | 340 | DeepFace-compatible local database search API | image, database, model, metric | DataFrame list | fallback representations |
| `OpenCVFaceBackend.verify` | 431 | DeepFace-compatible pair comparison API | two images, model, metric | result dictionary | fallback representations |
| `load_deepface_backend` | 488 | Import bundled DeepFace or instantiate fallback | none | backend object and import error | TensorFlow/DeepFace/OpenCV |

## Evaluation functions

| Function | Source | Purpose | Inputs | Outputs |
|---|---|---|---|---|
| `clean_path_segment` | `evaluation/collector.py:42` | Sanitize one dataset path segment | text, label | safe segment or error |
| `build_dataset_path` | `evaluation/collector.py:51` | Keep enrollment/test paths disjoint | category, identity, split, condition, suffix, ID | path |
| `read_metadata_rows` | `evaluation/collector.py:91` | Read and normalize metadata rows | none | row dictionaries |
| `write_metadata_rows` | `evaluation/collector.py:112` | Atomically rewrite metadata CSV | rows | none |
| `validate_faces` | `evaluation/collector.py:148` | Require detectable face and exactly one for enrollment | image, enrollment flag | face count or error |
| `save_sample` | `evaluation/collector.py:168` | Validate, save image, append metadata | bytes, name, identity, labels | path and count |
| `read_records` | `evaluation/scripts/run_benchmark.py:69` | Split metadata into enrollment, genuine, impostor records | none | three record lists |
| `minimum_distance` | `evaluation/scripts/run_benchmark.py:108` | Compare all enrollment/test embedding pairs | embedding tuples | minimum cosine distance |
| `summarize_metrics` | `evaluation/scripts/run_benchmark.py:144` | Compute confusion and classification metrics at a threshold | trials, threshold | metric dictionary |
| `run_model` | `evaluation/scripts/run_benchmark.py:211` | Represent all records, run trials, emit thresholds/performance | DeepFace, model, record groups | trials, threshold rows, performance |
| `write_report` | `evaluation/scripts/run_benchmark.py:285` | Write the benchmark narrative report | environment and results | Markdown file |
| `main` | `evaluation/scripts/run_benchmark.py:370` | Run isolated model benchmark and write CSV artifacts | none | result files and stdout |

## Verified implementation boundary

`app.py` is the presentation, session, orchestration, storage, recognition, unknown tracking, and threat-heuristic layer in one module. `deepface_adapter.py` is the runtime boundary. `evaluation/collector.py` and `evaluation/scripts/run_benchmark.py` are separate evaluation utilities. No SQL repository, external identity provider, microservice, or persistent RBAC database was found in the N-ONE-authored code.
