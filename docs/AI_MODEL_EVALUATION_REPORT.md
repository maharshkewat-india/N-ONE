# N-ONE AI Model Evaluation Report

## 1. Executive Summary

This report contains measured results from the isolated N-ONE victim face-recognition benchmark. It does not modify the live application or production thresholds. The impostor sample is limited to 10 LFW identities and 12 images, so results are evidence for this dataset only and are not production or universal accuracy claims.

## 2. Objective and Protocol

Each of 32 independent genuine victim test images was compared with enrollment representations for its labeled victim. Each of 12 impostor images was compared against each of 5 victim identities, producing 60 negative trials. Enrollment and test paths were separate.

Distance metric: `cosine`. Thresholds tested: 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60. Detector/backend: `retinaface` where supported. A test decision is a match when the minimum distance to that victim's enrollment embeddings is less than or equal to the tested threshold.

## 3. Environment

- python: 3.12.10
- platform: Windows-11-10.0.26200-SP0
- processor: Intel64 Family 6 Model 183 Stepping 1, GenuineIntel
- ram: unavailable
- gpu: not measured; CPU execution requested
- cache: C:\Users\MAHARSH\AppData\Local\Temp\n_one_deepface_benchmark_cache

## 4. Dataset

- Victim identities: 5
- Victim enrollment images: 11
- Genuine victim test images: 32
- Impostor identities: 10
- Impostor images: 12
- Source: Labeled Faces in the Wild (LFW), with source labels recorded in `evaluation/impostor_sources.csv`.
- Dataset limitation: 10 identities and 12 impostor images are a limited evaluation sample.

## 5. Measured Model Results

The model comparison below uses the configured threshold of 0.40. Values are measured, not estimated.

| Model | Status | TP | TN | FP | FN | Precision | Recall | F1 | FAR | FRR | False victim matches |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Facenet | measured | 21 | 60 | 0 | 11 | 1.0 | 0.65625 | 0.7924528301886793 | 0.0 | 0.34375 | 0 |
| Facenet512 | measured | 22 | 60 | 0 | 10 | 1.0 | 0.6875 | 0.8148148148148148 | 0.0 | 0.3125 | 0 |
| ArcFace | measured | 23 | 60 | 0 | 9 | 1.0 | 0.71875 | 0.8363636363636363 | 0.0 | 0.28125 | 0 |

## 6. Threshold Results

Complete threshold metrics are in `evaluation/results/threshold_comparison.csv`. No threshold was selected solely because it maximized one metric.

## 7. Performance

Measured performance is in `evaluation/results/performance_results.csv`. Inference latency includes detector, alignment/preprocessing, and embedding generation because DeepFace does not expose those stages separately through this API. Comparison latency is measured separately. GPU usage was not used.

## 8. Multi-frame Results

No video or frame-sequence assets were present in the validated evaluation dataset. One-frame, three-frame, and five-frame confirmation metrics were therefore not measured and are recorded as unavailable rather than inferred.

## 9. Failure Cases and Limitations

- Face detection failures are represented as no-match decisions when DeepFace returns no embeddings.
- The impostor sample is limited and contains still images rather than operational CCTV sequences.
- Results do not establish production accuracy, universal accuracy, real-world CCTV accuracy, guaranteed victim identification, or 100% recognition.
- Published/model documentation describes the models and detector; all tables in this report are N-ONE measurements from this run.

## 10. Evidence-Based Analysis

False victim matches, FAR, precision, recall, and FRR should be considered together. A lower FAR is especially important for Victim Search, but a configuration that rejects too many genuine victim images also has operational cost. The complete measured CSVs should be reviewed before changing any production threshold or model.

## 11. Recommended Next Experiment

Collect additional independently labeled impostor identities and real frame sequences across lighting, distance, angle, blur, occlusion, and multiple-face conditions. Then repeat this isolated protocol and evaluate three- and five-frame confirmation before considering any production change.
