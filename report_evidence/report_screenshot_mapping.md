# N-ONE Screenshot-to-Report Mapping

| Screenshot ID | Filename | Report chapter | Report section | Caption | Purpose | Evidence status |
|---|---|---|---|---|---|---|
| SS-01 | `screenshots/01_authentication/SS-01_authentication_fallback.png` | Chapter 6 | Authentication and RBAC | N-ONE authentication gate with fallback notice | Shows the login gate and actual TensorFlow-unavailable runtime notice | Captured |
| SS-02 | `screenshots/01_authentication/SS-02_invalid_login.png` | Chapter 15 | Authentication testing | Invalid credentials response | Shows the real invalid-login validation state without exposing a password | Captured |
| SS-03 | `screenshots/02_admin_dashboard/SS-03_admin_dashboard.png` | Chapter 6 | Administrator module | Administrator command center | Shows Administrator controls, operational console, counts, and fallback status | Captured |
| SS-04 | `screenshots/10_model_configuration/SS-04_model_configuration_fallback.png` | Chapter 7 | Model configuration | Current source settings and fallback status | Shows Facenet, OpenCV, cosine, threshold 0.40, and the actual fallback warning | Captured |
| SS-05 | `screenshots/06_victim_search/SS-05_victim_search_selection.png` | Chapter 12 | Victim Search | Victim Search target-selection interface | Shows target selection, camera location context, and the target-only search UI | Captured |
| SS-06 | `screenshots/15_error_validation/SS-06_browser_camera_unavailable.png` | Chapter 15 | Error and validation testing | Browser camera unavailable state | Shows the real WebRTC dependency/source failure state | Captured |
| SS-07 | `screenshots/11_logs_and_audit/SS-08_logs_and_history.png` | Chapter 6 | Dashboard inventory | Registered and unknown inventory | Shows actual registered count, unknown count, filters, and photo viewer | Captured |
| SS-08 | `screenshots/11_logs_and_audit/SS-08_logs_and_history.png` | Chapter 12 | Logs and dashboard review | Audit, unknown database, and Victim history views | Shows actual log/history areas and repository-backed counts | Captured |
| SS-09 | Not present | Chapter 6 | Operator RBAC | Operator dashboard | Intended to show restricted Operator controls | Blocked: supplied operator credential was rejected by the running app during this session |
| SS-10 | `screenshots/05_staff/SS-10_staff_attendance_interface.png` | Chapter 12 | Staff Recognition / Attendance | Staff Attendance mode interface | Shows the actual mode selector and attendance workflow UI | Captured |
| SS-11 | `screenshots/08_threat_detection/SS-11_threat_detection_interface.png` | Chapter 12 | Threat Detection | Threat Detection mode interface | Shows the actual separate threat mode UI; it is not a verified weapon result | Captured |
| SS-12 | Not present | Chapter 6 | Profile Registration | Valid Staff registration | Intended to show a successful new profile registration | Not Captured: existing data was preserved and no new profile was created |
| SS-13 | Not present | Chapter 6 | Profile Registration | Valid Victim registration | Intended to show a successful new Victim registration | Not Captured: existing data was preserved and no new profile was created |
| SS-14 | Not present | Chapter 15 | Registration validation | No-face or multiple-face error | Intended to show actual validation feedback | Not Captured: no safe upload interaction was performed |
| SS-15 | Not present | Chapter 12 | Victim Found | Victim Found result card | Intended to show name, profile ID, distance, timestamp, location, and history | Blocked: active runtime reports TensorFlow unavailable and disables identity matching in fallback mode |
| SS-16 | Not present | Chapter 12 | Victim Search no-match | Selected Victim not found | Intended to show a genuine no-match processing result | Blocked: no usable camera/video frame was available in the live UI |
| SS-17 | Not present | Chapter 12 | Unknown Re-ID | New unknown and repeat unknown | Intended to show creation and reuse of an unknown ID | Not Captured: no new/repeat frame was intentionally generated |
| SS-18 | Not present | Chapter 12 | Threat Detection result | Possible threat/fire heuristic alert | Intended to show an actual heuristic alert | Not Captured: no safe test image/video was staged and no alert was observed |
| SS-19 | Not present | Chapter 14 | Evaluation | Benchmark result tables/charts | Intended to show actual evaluation evidence | Not Captured: quantitative evidence remains in repository CSV/Markdown files rather than the running UI |
| SS-20 | Not present | Appendix F | Camera sources | Source selector and working feed | Intended to document each available source | Partially covered by SS-06; working webcam/file/IP feeds were not demonstrated |

## Insertion rule

Use SS-01 through SS-11 in the corresponding chapters and Appendix F. Keep blocked and not-captured rows in the evidence appendix as limitations; do not replace them with fabricated images.
