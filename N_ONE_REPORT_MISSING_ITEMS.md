# N-ONE Report Missing-Information Checklist

These items are not established by the repository and must be supplied or approved manually before academic submission.

## Academic identity and approvals

- [ ] Student name(s)
- [ ] Student roll number / registration code
- [ ] Degree and department
- [ ] College/university name
- [ ] Academic year
- [ ] Guide/supervisor name and designation
- [ ] Head of department name
- [ ] Certificate wording required by the university
- [ ] Certificate signatures and dates
- [ ] Student declaration wording and signatures
- [ ] Institutional approval or ethics approval, if required for biometric data

## Report presentation

- [ ] Approved cover-page template
- [ ] University formatting rules, margins, fonts, and page-numbering rules
- [ ] Table of contents generated in Microsoft Word after styles are applied
- [ ] List of figures and list of tables generated after final pagination
- [ ] Final approved bibliography style
- [ ] Page count after Word formatting

## Evidence and screenshots

- [ ] Authenticated command-center screenshot
- [ ] Administrator profile-registration screenshot
- [ ] Guided five-angle capture screenshot
- [ ] Face-only crop validation screenshot
- [ ] Victim Search target-selection screenshot
- [ ] Victim Found card screenshot using approved test data
- [ ] Staff recognition/attendance screenshot
- [ ] Unknown re-identification screenshot
- [ ] Threat heuristic screenshot with a `possible` label
- [ ] Log viewer screenshot
- [ ] Inventory/photo viewer screenshot
- [ ] Application startup/runtime screenshot
- [ ] Approved project photographs, if required

## Validation and deliverable status

- [ ] Install `pytest` in the selected project test environment and rerun the full suite
- [ ] Resolve or document the `evaluation/dataset_metadata.csv` header-order mismatch
- [ ] Attach the complete current test output, including any setup/environment errors
- [ ] Reconcile the legacy "no real evaluation data" statements in `evaluation/README.md` and `evaluation/dataset/README.md` with the populated dataset and measured result CSVs
- [ ] Generate and inspect a real paginated DOCX and PDF; current Markdown word count is approximately 7,291 and does not establish a 70–80-page report
- [ ] Verify page count, heading styles, table of contents, figure numbering, table numbering, fonts, margins, and line spacing after Word/PDF generation

## Performance and deployment

- [ ] Application hardware model and RAM used for the final demonstration
- [ ] GPU model and whether it was used
- [ ] Application-level FPS measurement by source and mode
- [ ] Application-level latency measurement
- [ ] Application RAM and CPU measurements
- [ ] Camera resolution and frame-rate details
- [ ] Network topology and IP-camera details, if demonstrated
- [ ] Storage-retention calculation
- [ ] Maximum tested camera count
- [ ] Deployment operating-system/version record

## Mode-specific validation

- [ ] Staff-specific benchmark with independent enrollment and test data
- [ ] Unknown Re-ID benchmark with same-person and different-person trials
- [ ] Threat-detection dataset and ground-truth labels
- [ ] Threat false-positive and false-negative measurements
- [ ] Camera-sequence data for 1-frame, 3-frame, and 5-frame evaluation
- [ ] Threshold calibration on representative operational footage
- [ ] Human-review procedure for Victim or threat alerts

## Security and privacy

- [ ] Approved password policy
- [ ] Decision on password hashing or external identity provider
- [ ] Encryption-at-rest decision for face images and CSVs
- [ ] TLS/reverse-proxy deployment configuration, if network exposed
- [ ] Retention and deletion policy
- [ ] Access-review and login/audit-log policy
- [ ] Consent/legal basis for captured face data
- [ ] Dataset licensing review and attribution approval
- [ ] Incident-response and breach procedure

## Academic appendices

- [ ] Student profile
- [ ] Published paper list, or explicit `Not applicable`
- [ ] Plagiarism report
- [ ] PPT handouts
- [ ] Signed evaluation sheet
- [ ] Final benchmark tables exported to Word/Excel
- [ ] Final test-case evidence and screenshots
- [ ] Final project file-structure snapshot

## Explicit unavailable claims

The report must retain the following wording unless new evidence is added:

- `Staff-specific recognition accuracy: Not measured in the current implementation/evaluation.`
- `Unknown Re-ID accuracy: Not measured in the current implementation/evaluation.`
- `Threat-detection accuracy: Not measured in the current implementation/evaluation.`
- `Multi-frame 1/3/5 confirmation results: Not measured in the current implementation/evaluation.`
- `Application-wide FPS, latency, RAM, and GPU usage: Not measured in the current implementation/evaluation.`
- `Training of a new neural network: Not demonstrated; the application uses pretrained/available model interfaces and enrollment comparison.`

## Fresh audit additions - 2026-10-01

- [ ] Repair the unmatched parenthesis in `evaluation/scripts/evaluate_thresholds.py` and rerun syntax validation.
- [ ] Resolve the Windows cross-drive path assumption exposed by `test_valid_file_saves_and_updates_metadata_atomically`.
- [ ] Reconcile the metadata header-order contract between `tests/test_evaluation_dataset.py`, `evaluation/collector.py`, and `evaluation/dataset_metadata.csv`.
- [ ] Capture sanitized, credential-free screenshots of authenticated Admin and Operator workflows.
- [ ] Demonstrate a usable camera or recorded-video frame under the supported dependency configuration.
- [ ] Demonstrate Staff recognition with a dedicated labeled test set.
- [ ] Demonstrate Unknown Re-ID with a repeat observation and verify sighting IDs.
- [ ] Capture a safe threat-heuristic example and label it as a possible alert, not a confirmed threat.
- [ ] Record exact hardware, RAM, camera resolution, and GPU state for performance reporting.
- [ ] Define biometric retention, deletion, access-review, and encryption requirements.
- [ ] Provide signed institutional front matter and student/guide details.
- [ ] Generate and independently inspect paginated DOCX/PDF files; page count is currently not evidenced.
