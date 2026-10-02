# N-ONE Report Testing Register

Audit date: 25 September 2026

## Evidence status

The repository contains tests for the DeepFace-compatible adapter, profile categorization, unknown storage/counting, Victim target filtering, browser annotation behavior, dataset metadata, path containment, and face-count validation. A fresh suite run could not be reproduced in the audited environments because `pytest` is not installed in `new_venv` or the system Python 3.14 environment.

A prior audit recorded 24 passed, 1 failed, and 1 error. That is historical evidence only. The reported assertion failure was a dataset metadata header-order mismatch: the test expected `file_path` first while the checked-in collector schema and CSV begin with `id`. The reported error was temporary-directory setup related. This status must not be summarized as a fully passing suite.

## Test coverage register

| ID | Area | Repository evidence | Status |
|---|---|---|---|
| T01 | Adapter interface | `tests/test_deepface_adapter.py` checks `represent`, `find`, and `verify` | Historical test coverage; current rerun unavailable |
| T02 | Staff/Victim and legacy profile labels | `tests/test_face_inventory.py` | Historical test coverage; current rerun unavailable |
| T03 | Unique unknown count | `tests/test_face_inventory.py` | Historical test coverage; current rerun unavailable |
| T04 | Unknown data clearing | `tests/test_face_inventory.py` | Historical test coverage; current rerun unavailable |
| T05 | Victim-only known cache | `tests/test_face_inventory.py` | Historical test coverage; current rerun unavailable |
| T06 | Browser annotation safety | `tests/test_face_inventory.py` | Historical test coverage; current rerun unavailable |
| T07 | Dataset path containment | `tests/test_evaluation_collector.py` | Historical test coverage; current rerun unavailable |
| T08 | Enrollment/test face-count validation | `tests/test_evaluation_dataset.py` and collector tests | Historical test coverage; current rerun unavailable |
| T09 | Authentication and RBAC | Source inspection in `app.py`; no complete browser E2E suite | Implemented source path; E2E result unavailable |
| T10 | Staff recognition accuracy | No dedicated benchmark CSV | Not measured in current implementation/evaluation. |
| T11 | Unknown Re-ID accuracy | No dedicated benchmark CSV | Not measured in current implementation/evaluation. |
| T12 | Threat detection accuracy | No labeled threat dataset or confusion matrix | Not measured in current implementation/evaluation. |
| T13 | Multi-frame confirmation | `evaluation/results/multi_frame_results.csv` marks all rows unavailable | Not available |

## Required next validation

Install `pytest` in the selected supported environment, resolve or explicitly document the metadata-header mismatch, run the full suite, and attach the unedited output. Do not convert source-level test coverage into a passing result without that run.

## Fresh executable validation - 2026-10-01

Command: `d:\n-0ne\.venv\Scripts\python.exe -m pytest tests -q`

Result: 24 passed, 2 failed.

| Test | Actual result | Finding |
|---|---|---|
| `test_valid_file_saves_and_updates_metadata_atomically` | Failed | Cross-drive `Path.relative_to(ROOT)` error when the test redirects the dataset root to a Windows temporary directory |
| `test_dataset_metadata_has_required_columns` | Failed | Test expects `file_path` first; collector and checked-in CSV begin with `id,file_path` |

Syntax command: `python -m py_compile app.py deepface_adapter.py evaluation/collector.py evaluation/scripts/run_benchmark.py evaluation/scripts/evaluate_models.py evaluation/scripts/evaluate_thresholds.py evaluation/scripts/generate_metrics.py`.

Result: the command reached `evaluate_thresholds.py` and reported `SyntaxError: unmatched )` at line 27. This is a current executable defect.

Runtime command: `python -m streamlit run app.py --server.headless true --server.port 8503`.

Result: Streamlit started, HTTP 200 was returned, the page title loaded, and the actual TensorFlow-missing fallback warning was visible. A successful Operator session, live camera, Victim Found event, Staff result, Unknown Re-ID event, or threat alert was not demonstrated.
