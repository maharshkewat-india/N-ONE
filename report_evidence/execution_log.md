# N-ONE Execution Log

## Run metadata

- Date: 2026-09-25
- Operating system: Windows
- Workspace: `D:\n-0ne`
- Python command used: `python -m streamlit run app.py --server.headless true --server.port 8501`
- Local URL: `http://localhost:8501`
- Application source changed: No
- Production configuration changed: No
- Existing project data deleted: No
- Screenshot directory: `report_evidence/screenshots/`

## Runtime

The application started successfully. Streamlit reported a local server on port 8501 and the page title loaded as `N-ONE : NO ONE ESCAPES`.

The UI displayed the actual warning:

> DeepFace runtime is not fully available in this environment. The app will continue with a safe fallback. Error: No module named 'tensorflow'

The live application therefore exposed the OpenCV/HOG fallback boundary. No neural-model or successful neural identity result was claimed.

## Tests performed

| Test | Result | Evidence |
|---|---|---|
| Authentication page loads | Passed | SS-01 |
| Invalid login response | Passed | SS-02 |
| Administrator login | Passed | SS-03 |
| Administrator controls | Passed | SS-03 |
| Model configuration panel | Passed | SS-04 |
| Victim Search target selector | Passed | SS-05 |
| Browser camera unavailable state | Passed | SS-06 |
| Inventory and counts | Passed | SS-07 |
| Audit/history sections | Passed | SS-08 |
| Staff Attendance interface | Passed | SS-10 |
| Threat Detection interface | Passed | SS-11 |
| Operator login/dashboard | Blocked | Supplied operator credential was rejected by the running app during this session; no secret was recorded or guessed |
| Victim Found identity result | Blocked | Runtime reported TensorFlow unavailable and the source disables fallback identity matching for Victim alerts |
| Genuine Victim frame | Blocked | No usable live camera/video frame was available |
| Staff recognition result | Not demonstrated | No usable live frame was available; no Victim benchmark was reused |
| Unknown Re-ID result | Not demonstrated | No new/repeat observation was generated for evidence |
| Threat alert result | Not demonstrated | No safe test image/video produced an observed alert |
| Working camera feed | Blocked | WebRTC dependency unavailable; no local camera feed was demonstrated |
| Evaluation dashboard screenshot | Not captured | Quantitative evidence is stored in repository CSV/Markdown files, not rendered in this UI run |

## Data observed

The authenticated Administrator dashboard showed the repository-backed counts visible in the UI: two registered profiles, 23 unknown faces, and 2,799 total log events at the time of capture. Existing profile names and event data were not copied into this log beyond what is visible in screenshots; review for privacy before academic distribution.

## Safety and integrity

- No passwords, tokens, API keys, or camera credentials were written to this file.
- No profile, unknown, or audit data was deleted.
- No fake result was staged.
- No source code or production default was modified.
- Screenshot files were saved with absolute workspace paths after confirming the browser sandbox initially used an isolated path.
