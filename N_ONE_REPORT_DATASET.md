# N-ONE Report Dataset Register

Audit date: 25 September 2026

## Direct metadata summary

The checked-in `evaluation/dataset_metadata.csv` contains 11 Victim enrollment images and 32 Victim test images. The test set includes 12 impostor images. The Victim tests are distributed across normal, angle, lighting, distance, blur, and multiple_faces conditions. `evaluation/impostor_sources.csv` records ten impostor identities and identifies LFW source metadata.

| Category | Split | Count | Evidence |
|---|---|---:|---|
| victims | enrollment | 11 | `evaluation/dataset_metadata.csv` |
| victims | test | 32 | `evaluation/dataset_metadata.csv` |
| impostor | test | 12 | `evaluation/dataset_metadata.csv` |
| staff | any | 0 | No checked-in metadata rows |
| unknown | any | 0 | No checked-in metadata rows |
| threats | any | 0 | No checked-in metadata rows |

## Evaluation protocol represented by results

The measured model and threshold CSVs use 32 genuine Victim trials and 60 impostor trials. The 60 negative trials result from comparing the available impostor images against Victim identities in the benchmark protocol. Enrollment and test paths are separate in the metadata. The benchmark is a still-image evaluation; `evaluation/results/multi_frame_results.csv` marks 1-, 3-, and 5-frame confirmation as `not_available` because no labeled sequences are present.

## Measured result files

- `evaluation/results/model_comparison.csv`: FaceNet, FaceNet512, and ArcFace at threshold 0.40.
- `evaluation/results/threshold_comparison.csv`: thresholds 0.20 through 0.60 for the three models.
- `evaluation/results/performance_results.csv`: 55-image benchmark performance rows.
- `evaluation/results/multi_frame_results.csv`: explicit unavailable status for sequence evaluation.

## Evidence limits

The dataset is small relative to a deployment claim and does not support staff accuracy, unknown re-identification accuracy, threat-detection accuracy, or universal face-recognition accuracy. Older text in `evaluation/README.md` and `evaluation/dataset/README.md` says that no real evaluation data is present; that text conflicts with the populated metadata and measured result files and should be reconciled before submission. The measured CSVs are treated as direct evidence, while the older statements remain a documented inconsistency.

## Fresh dataset integrity audit - 2026-10-01

`evaluation/dataset_metadata.csv` contains 50 rows and all referenced files exist. The verified partition is:

| Category | Split/condition | Count |
|---|---|---:|
| Victims | Enrollment | 11 |
| Victims | Test normal | 5 |
| Victims | Test angle | 5 |
| Victims | Test lighting | 6 |
| Victims | Test distance | 9 |
| Victims | Test blur | 3 |
| Victims | Test multiple_faces | 4 |
| Impostor | Test normal | 12 |

The genuine set contains five victim identities and 32 images. The impostor set contains 12 images representing ten labeled impostor IDs, with repeated identities for two records. No Staff, Unknown, or Threat rows were present in the validated metadata. Hash-overlap analysis, demographic representativeness, and production-camera equivalence are not available in the current evidence.
