# N-ONE Report Figure Plan

All figures must be generated from the current implementation or replaced with approved repository screenshots. Mermaid diagrams are included in the report as editable source. No fake screenshots should be added.

| Figure | Title | Source / screenshot required | Chapter | Explanation requirement |
|---|---|---|---|---|
| Figure 1 | Overall System Architecture | `app.py`, `deepface_adapter.py`, `ARCHITECTURE.md`; Mermaid in report | 9 | Explain Streamlit, authentication, source selection, processing, storage, and review paths. |
| Figure 2 | N-ONE Module Architecture | `app.py` function groups and storage paths | 6 | Explain authentication, registration, ingestion, matching, unknown tracking, threats, logging, and UI. |
| Figure 3 | Victim Search Workflow | `process_frame()`, `find_face_in_known_cache()`, `record_victim_sighting()` | 12 | Show selected Victim restriction, match decision, no-match handling, logging, and visible result. |
| Figure 4 | Staff Recognition Workflow | `process_frame()` attendance branch | 12 | Show unrestricted registered-profile comparison and unknown fallback. |
| Figure 5 | Unknown Re-ID Workflow | `find_face_in_unknown_cache()`, `register_new_unknown()`, `update_unknown_sighting()` | 12 | Distinguish known identity verification from same-unknown matching. |
| Figure 6 | Threat Detection Workflow | `check_weapon_contours()` and threat branch in `process_frame()` | 12 | Show contour/HSV heuristic path and possible-alert limitation. |
| Figure 7 | Authentication and RBAC Workflow | `load_auth_credentials()`, `render_sidebar()` | 6 or 16 | Show secret loading, constant-time comparison, role assignment, lockout, and UI restrictions. |
| Figure 8 | Victim Registration Workflow | `prepare_single_face_crop()`, `save_registered_profile_captures()` | 12 | Show capture, exact-one-face validation, crop/padding, filename, cache refresh. |
| Figure 9 | Data Storage Architecture | `initialize_log_files()`, path constants in `app.py` | 11 | Show registered images, unknown images, four CSV stores, and read/write relationships. |
| Figure 10 | AI Recognition Pipeline | `deepface_adapter.py`, `process_frame()` | 7 | Show detection, representation, distance, threshold, target filtering, and outcome. |
| Figure 11 | Level-0 DFD | Application inputs and outputs in `app.py` | 10 | Treat N-ONE as one process and show external actors/stores. |
| Figure 12 | Level-1 DFD | `render_main_ui()`, `process_frame()`, persistence helpers | 10 | Decompose authentication, capture, recognition, threat logic, and logging. |
| Figure 13 | Victim Search DFD | Victim-specific branch in `process_frame()` | 10 | Show target selection and target-only visible result. |
| Figure 14 | Logical ER/Data Model | Actual CSV columns and filename-derived profile entities | 11 | Label as logical data model, not a relational schema implemented by SQL. |
| Figure 15 | AI Model Evaluation Pipeline | `evaluation/scripts/`, `evaluation/results/` | 14 | Show separate enrollment/test data, embedding, distance, threshold sweep, metrics. |
| Figure 16 | Safe Model Change Workflow | `AI_MODEL_CONFIGURATION.md`, `docs/AI_MODELS_AND_CONFIGURATION_GUIDE.md` | 17 | Show isolated config, independent data, benchmark, environmental tests, review, pilot, decision. |

## Screenshots

| Screenshot item | Status | Required action |
|---|---|---|
| Authenticated command center | Not present in repository | Capture from a configured local run after supplying non-production test secrets. |
| Administrator registration panel | Not present in repository | Capture upload and guided multi-angle states. |
| Victim Found card | Not present in repository | Capture only with synthetic/test data or approved faces. |
| Staff/unknown attendance result | Not present in repository | Capture from a controlled test session. |
| Threat heuristic result | Not present in repository | Capture a clearly labeled heuristic demonstration; do not caption as verified weapon detection. |
| Log viewer and inventory | Not present in repository | Capture dashboard tables with approved redacted data. |
| Evaluation charts | No generated chart image present | Generate from CSVs in a reproducible script or use Markdown tables only. |
| Logo | Present | `assets/n_one_logo.png` may be used as an application asset, not as an operational screenshot. |

## Diagram conventions

- Use solid arrows for implemented data flow.
- Use dashed arrows for optional full DeepFace/TensorFlow capabilities.
- Use `possible` or `heuristic` in threat labels.
- Mark WebRTC worker annotation as a separate path because it intentionally avoids disk/session writes.
- Do not depict a SQL database, blockchain, IPFS, encryption layer, or trained threat model because the repository does not implement them.

## Fresh audit figure status - 2026-10-01

| Figure | Title | Source | Status |
|---|---|---|---|
| Figure 17 | Verified monolithic architecture | Forensic audit supplement, Mermaid | Ready |
| Figure 18 | Authentication and lockout flow | Forensic audit supplement, Mermaid | Ready |
| Figure 19 | Target-restricted Victim Search pipeline | Forensic audit supplement, Mermaid | Ready |
| Figure 20 | Fresh Streamlit login/fallback state | Live port 8503 | Not retained; browser state contained credential input |

No screenshot file is currently present under `report_evidence/screenshots/`. Screenshot figures must not be marked captured until sanitized image files are supplied.
