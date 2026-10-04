# N-ONE Report Testing Register

Latest audit: 4 October 2026

## Evidence status

The 4 October audit ran the full test suite with the project `.venv` and recorded **26 passed**. The metadata test now expects the checked-in seven-column schema. The atomic collector test uses a workspace-local scratch directory because pytest's system temporary directory is inaccessible in this managed Windows environment. The listed project Python files compile successfully.

The neural benchmark remains unavailable in this environment: Windows Application Control blocks TensorFlow's native `ml_dtypes` extension. The checked-in metric CSV arithmetic was independently checked, but no fresh neural inference results were produced. A Streamlit server smoke check returned HTTP 200; authentication and protected workflows were not exercised.

## Test coverage register

| ID | Area | Repository evidence | Status |
|---|---|---|---|
| T01 | Adapter interface | `tests/test_deepface_adapter.py` checks `represent`, `find`, and `verify` | Passed in the 4 October suite; adapter behavior tested without a live neural model |
| T02 | Staff/Victim and legacy profile labels | `tests/test_face_inventory.py` | Passed in the 4 October suite |
| T03 | Unique unknown count | `tests/test_face_inventory.py` | Passed in the 4 October suite |
| T04 | Unknown data clearing | `tests/test_face_inventory.py` | Passed in the 4 October suite |
| T05 | Victim-only known cache | `tests/test_face_inventory.py` | Passed in the 4 October suite |
| T06 | Browser annotation safety | `tests/test_face_inventory.py` | Passed in the 4 October suite; annotation behavior only, not browser E2E |
| T07 | Dataset path containment | `tests/test_evaluation_collector.py` | Passed in the 4 October suite |
| T08 | Enrollment/test face-count validation | `tests/test_evaluation_dataset.py` and collector tests | Passed in the 4 October suite |
| T09 | Authentication and RBAC | Source inspection in `app.py`; no complete browser E2E suite | Implemented source path; E2E result unavailable |
| T10 | Staff recognition accuracy | No dedicated benchmark CSV | Not measured in current implementation/evaluation. |
| T11 | Unknown Re-ID accuracy | No dedicated benchmark CSV | Not measured in current implementation/evaluation. |
| T12 | Threat detection accuracy | No labeled threat dataset or confusion matrix | Not measured in current implementation/evaluation. |
| T13 | Multi-frame confirmation | `evaluation/results/multi_frame_results.csv` marks all rows unavailable | Not available |

## Required next validation

Run the neural benchmark in an environment where TensorFlow's native extension is permitted, add full browser E2E and labeled video tests, and create independent Staff, Unknown Re-ID, and Threat Detection benchmarks. Do not treat unit-test success as evidence of recognition accuracy.

## Fresh executable validation - 2026-10-01

This run is retained as historical evidence and is superseded by the 4 October validation below.

Command: `d:\n-0ne\.venv\Scripts\python.exe -m pytest tests -q`

Result: 24 passed, 2 failed.

| Test | Actual result | Finding |
|---|---|---|
| `test_valid_file_saves_and_updates_metadata_atomically` | Failed | Cross-drive `Path.relative_to(ROOT)` error when the test redirects the dataset root to a Windows temporary directory |
| `test_dataset_metadata_has_required_columns` | Failed | Test expects `file_path` first; collector and checked-in CSV begin with `id,file_path` |

Syntax command: `python -m py_compile app.py deepface_adapter.py evaluation/collector.py evaluation/scripts/run_benchmark.py evaluation/scripts/evaluate_models.py evaluation/scripts/evaluate_thresholds.py evaluation/scripts/generate_metrics.py`.

Result: the command reached `evaluate_thresholds.py` and reported `SyntaxError: unmatched )` at line 27. The defect was fixed and recompiled on 4 October.

Runtime command: `python -m streamlit run app.py --server.headless true --server.port 8503`.

Result: Streamlit started, HTTP 200 was returned, the page title loaded, and the actual TensorFlow-missing fallback warning was visible. A successful Operator session, live camera, Victim Found event, Staff result, Unknown Re-ID event, or threat alert was not demonstrated.

## Fresh executable validation - 2026-10-04

Command: `.venv\Scripts\python.exe -m pytest tests -q`

Result: **26 passed in 3.27s**.

Syntax command: `.venv\Scripts\python.exe -m py_compile app.py deepface_adapter.py evaluation/collector.py evaluation/scripts/run_benchmark.py evaluation/scripts/evaluate_models.py evaluation/scripts/evaluate_thresholds.py evaluation/scripts/generate_metrics.py`

Result: passed. The extra closing parenthesis in `evaluate_thresholds.py` was removed.

Dataset audit: 55 metadata rows, zero missing image files, and all 12 source-manifest SHA-256 values matched their local LFW images. The partitions were 11 Victim enrollment, 32 Victim test, and 12 impostor test images.

Model preflight: `RUNTIME UNAVAILABLE`; labeled data is present, but DeepFace/TensorFlow could not be imported. A direct benchmark run was blocked when Windows Application Control denied loading `ml_dtypes._ml_dtypes_ext`. No fresh neural model results were written.

Threshold script: ran successfully and wrote seven `PLANNED` rows from 0.20 through 0.50. It records readiness only and does not generate recognition metrics.

Application smoke check: Streamlit started on port 8513 and `http://127.0.0.1:8513` returned HTTP 200. Login, protected workflows, live camera, and recognition results were not exercised in this check.
