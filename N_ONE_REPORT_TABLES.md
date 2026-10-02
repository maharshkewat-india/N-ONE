# N-ONE Report Table Plan

| Table | Title | Data source | Chapter |
|---|---|---|---|
| Table 1 | Technology Stack | `requirements.txt`, `requirements-deepface.txt`, imports in `app.py` and `deepface_adapter.py` | 7 |
| Table 2 | Hardware Configuration and Measurement Status | `docs/AI_MODEL_EVALUATION_REPORT.md`, repository environment notes | 8 |
| Table 3 | Software Configuration | `requirements.txt`, `requirements-deepface.txt`, `.env.example` | 8 |
| Table 4 | Project Modules | `app.py`, `deepface_adapter.py`, storage directories | 6 |
| Table 5 | User Roles and Permissions | `render_sidebar()` in `app.py` | 6 and 16 |
| Table 6 | Model Comparison at Threshold 0.40 | `evaluation/results/model_comparison.csv` | 14 |
| Table 7 | Threshold Sweep Summary | `evaluation/results/threshold_comparison.csv` | 14 |
| Table 8 | Dataset Summary | `evaluation/dataset_metadata.csv`, `docs/AI_MODEL_EVALUATION_REPORT.md` | 14 |
| Table 9 | Confusion-Matrix Counts | `model_comparison.csv` | 14 |
| Table 10 | Functional Test Cases | `tests/test_face_inventory.py`, application behavior | 15 |
| Table 11 | AI and Dataset Test Cases | `tests/test_evaluation_dataset.py`, `tests/test_evaluation_collector.py` | 15 |
| Table 12 | Limitations | Source-backed gaps from code, docs, and CSVs | 17 |
| Table 13 | Future Scope | Evidence gaps and safe-change guide | 17 |
| Table 14 | Storage Fields | `initialize_log_files()` in `app.py` | 10 and 11 |
| Table 15 | Operational Mode Configuration | `app.py`, `AI_MODEL_CONFIGURATION.md`, model guide | 7 and 12 |
| Table 16 | Performance Benchmark | `evaluation/results/performance_results.csv` | 14 |
| Table 17 | Multi-Frame Status | `evaluation/results/multi_frame_results.csv` | 14 and 17 |
| Table 18 | Security Control Matrix | `app.py`, `.env.example`, absence of encryption/hash implementation | 16 |
| Table 19 | Missing Academic Inputs | `N_ONE_REPORT_MISSING_ITEMS.md` | Appendices |

## Reproducibility rules

- Copy measured values directly from CSVs.
- Preserve decimal values where they matter; explain rounded display values.
- Separate benchmark configuration from production defaults.
- Never use Victim benchmark values as Staff, Unknown Re-ID, or Threat metrics.
- Mark unavailable fields as `Not measured in the current implementation/evaluation.`

## Fresh audit tables - 2026-10-01

| Table | Title | Data source | Status |
|---|---|---|---|
| Table 20 | Verified project fact sheet | Forensic audit supplement | Verified |
| Table 21 | Fresh dataset partition counts | `evaluation/dataset_metadata.csv` | Verified |
| Table 22 | Fresh pytest failures | Current `pytest` output | Verified |
| Table 23 | Threat model | Forensic audit supplement | Source-grounded analysis |
| Table 24 | Function-to-module mapping | `N_ONE_FUNCTION_MAPPING.md` | Verified source inventory |
