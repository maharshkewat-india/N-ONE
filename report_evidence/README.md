# N-ONE Report Evidence Package

This directory contains screenshots and execution records captured from the existing N-ONE Streamlit application on 2026-09-25.

## Capture method

- Application: existing `app.py`
- Local URL: `http://localhost:8501`
- Browser automation: VS Code integrated browser with Playwright-backed controls
- Screenshot format: PNG
- Credentials: used only in the live session; no credentials are recorded here
- Existing project data was not deleted or modified
- No source code or production configuration was changed for screenshots

## Evidence status

- `Captured`: an actual screenshot file exists and was observed in the live application.
- `Blocked`: the state could not be demonstrated because of a runtime, access, or environment limitation.
- `Not Captured`: the feature may be implemented, but no screenshot was taken in this run.
- `Not Applicable`: the item is not a UI state or is outside the current implementation.

## Organization

Screenshots are grouped under `screenshots/` using the requested report categories. The complete mapping is in `report_screenshot_mapping.md`; the machine-readable record is `screenshot_manifest.csv`; limitations are in `missing_screenshots.md`.

## Important interpretation

The screenshots demonstrate UI and workflow states only. They do not prove recognition accuracy, threat-detection accuracy, security compliance, or production readiness. The benchmark CSVs and `N_ONE_REPORT_EVIDENCE.md` remain the quantitative evidence sources.

## Word report use

Insert captured images in the report sections listed in the mapping file. Preserve the captions and evidence status. Do not insert blocked items as if they were screenshots. Appendix F should include the captured images plus a short note listing blocked states.
