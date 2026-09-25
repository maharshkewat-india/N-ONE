# Evaluation Workspace

This folder is intentionally reserved for evidence-driven benchmarking without altering the current working application.

## Structure

- dataset/ — evaluation assets and paired enrollment/test data
- dataset_metadata.csv — dataset inventory template
- scripts/ — benchmark and validation scripts
- results/ — generated CSVs from benchmark runs
- screenshots/ — place for labeled visual evidence if available

## Important rules

- Do not use enrollment images as test images.
- Do not invent metrics or accuracy.
- Keep the OpenCV fallback active.
- Only benchmark the real DeepFace runtime in a supported Python 3.10-3.13 environment.
- Use scientific labels: victim, staff, impostor, unknown, threat.

## Current status

The workspace currently contains only the fallback baseline and no real evaluation dataset. The result is therefore:

INSUFFICIENT TEST DATA

## Collecting real evaluation data

Use the standalone collector to add real images without changing the live N-ONE application:

```powershell
.\.venv-deepface\Scripts\python.exe -m streamlit run evaluation\collector.py
```

The collector supports upload and browser-camera capture. For each sample, choose an identity, category, split, and (for test images) condition. It uses RetinaFace to reject unreadable images and requires exactly one detected face for enrollment; test images require at least one face and may contain multiple faces.

Images are saved under `evaluation/dataset/<category>/enrollment/<identity>/` or `evaluation/dataset/<category>/test/<condition>/<identity>/`. Each successful save rewrites `evaluation/dataset_metadata.csv` atomically with these columns:

```text
id,file_path,identity,category,split,condition,expected_result
```

Do not upload files copied from `registered_faces/`, and keep enrollment and test images independently collected.
