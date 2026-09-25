# N-ONE AI Models and Configuration Guide

This is the primary technical reference for selecting, configuring, evaluating, and operating N-ONE's computer-vision components. It is written for developers, operators, evaluators, and maintainers.

This guide describes the current source configuration and the isolated benchmark evidence. It does not change production settings.

## 1. Important Runtime Status

The current defaults in `app.py` are:

```python
DEEPFACE_MODEL = "Facenet"
DEEPFACE_BACKEND = "opencv"
DEEPFACE_METRIC = "cosine"
COSINE_THRESHOLD = 0.40
```

The benchmark evaluated `Facenet`, `Facenet512`, and `ArcFace` with RetinaFace and cosine distance. That benchmark did **not** change the live application. Therefore, ArcFace is a measured benchmark candidate, not the current production default unless an operator selects it through the runtime settings panel.

The neural models require the supported TensorFlow/DeepFace environment. When that runtime is unavailable, N-ONE uses its OpenCV fallback path. In fallback mode, selecting a neural model name does not activate a neural model.

## 2. N-ONE AI Architecture

N-ONE contains multiple computer-vision tasks. They must not be treated as one single AI model.

```text
N-ONE
|
+-- Victim Face Search
|   +-- Face detection       -> selected detector, RetinaFace for benchmark
|   +-- Face recognition     -> Facenet / Facenet512 / ArcFace
|   +-- Distance             -> cosine distance by default
|   +-- Decision             -> threshold and optional confirmation policy
|   +-- Output               -> selected victim found or face detected/no match
|
+-- Staff Recognition / Attendance
|   +-- Face detection
|   +-- Face recognition     -> configured recognition model
|   +-- Registered profile   -> staff identity and attendance event
|   +-- Unknown handling     -> unknown cache and sighting records
|
+-- Unknown Person Tracking
|   +-- Face representation
|   +-- Comparison with unknown-face cache
|   +-- New unknown storage and sighting history
|
+-- Threat Detection
    +-- Motion/colour/contour analysis and configured threat logic
    +-- Possible weapon/fire regions
    +-- Threat event logging
    +-- No face embedding or identity threshold is used
```

A face-recognition model cannot be used as a threat detector, and a threat detector cannot identify a person. The selected face model is relevant to Victim Search, Staff Recognition, Attendance, and unknown-person comparison only.

## 3. Recognition Pipeline

For a face-recognition mode, the conceptual pipeline is:

1. Capture a frame from a webcam, uploaded video, browser camera, or IP stream.
2. Detect one or more face regions.
3. Align and preprocess each detected face.
4. Generate an embedding vector with the selected recognition model.
5. Compare the vector with enrollment or cached representations.
6. Calculate a distance.
7. Apply the configured threshold.
8. Display and log a result according to the selected N-ONE mode.

In Victim Search, a match must be against the selected victim profile. A detected face that does not pass the identity comparison is reported as a face detected/no match; it must not be presented as the selected victim.

## 4. Face-Recognition Models

### 4.1 FaceNet (`Facenet`)

FaceNet maps a face image into an embedding space. Images of the same identity should have smaller distances than images of different identities.

Use FaceNet when:

- CPU or memory requirements are important.
- A broadly supported baseline is needed.
- A quick comparison with the other models is required.
- Existing operational configuration compatibility matters.

Strengths:

- Established embedding-based approach.
- Useful baseline for controlled comparisons.
- Available through the DeepFace model interface.

Limitations:

- Performance depends on face quality, pose, lighting, and enrollment coverage.
- A threshold calibrated for another model must not be reused without evaluation.
- The current isolated benchmark showed more genuine rejections at threshold `0.40` than the other two tested models.

### 4.2 FaceNet512 (`Facenet512`)

FaceNet512 is a higher-dimensional FaceNet-family embedding configuration. The larger representation can preserve more discriminative information, but it may require more compute and memory.

Use FaceNet512 when:

- More representation capacity is useful.
- The deployment environment can tolerate its inference cost.
- Independent enrollment/test data supports its threshold.
- A balanced alternative between the baseline and ArcFace is needed.

Strengths:

- Higher-dimensional embedding representation.
- Useful candidate for difficult appearance changes when measured on representative data.
- Remains available for comparison and deployments where its trade-off is preferable.

Limitations:

- Higher dimensionality does not guarantee better results on every dataset.
- It can be slower or more resource-intensive than a smaller baseline.
- Its distances and threshold behavior are model-specific.

### 4.3 ArcFace

ArcFace learns identity embeddings with an additive angular margin. The angular margin is intended to make identities more separable in the embedding space.

Use ArcFace when:

- The full neural runtime is available.
- Identity separation is the priority.
- The detector and threshold have been measured on the target conditions.
- Victim-safety analysis gives acceptable false-accept and false-reject trade-offs.

Strengths:

- Designed for discriminative identity embeddings.
- Natural fit for cosine/angular comparison.
- In the N-ONE benchmark at threshold `0.40`, it produced the highest measured recall and F1 among the three tested models while recording zero false victim matches in that limited sample.

Limitations:

- It does not guarantee correct identification in production or CCTV conditions.
- It may require more compute and model weights than a lightweight fallback.
- The result is sensitive to detector quality, enrollment quality, threshold choice, and data distribution.

## 5. Which Model Is Used in Each Mode?

| N-ONE mode | AI path | Recognition model relevance |
| --- | --- | --- |
| Victim Face Search | Face detection, embedding, selected-victim comparison, logging | Facenet, FaceNet512, or ArcFace; current source default is Facenet |
| Staff Recognition / Attendance | Face detection, registered-profile comparison, attendance logging | Same configured recognition model |
| Unknown Person Tracking | Face detection, embedding, unknown-cache comparison, storage | Same configured recognition model when neural runtime is active |
| Threat Detection | Contour/colour/motion and threat logic | Face-recognition model is not used for threat decisions |
| Facial analytics/verification tools | Face detection and embedding comparison | Same configured recognition model and metric |

RetinaFace is a detector, not a recognition model. It locates faces before the recognition model generates embeddings.

## 6. Why RetinaFace Is Used for Benchmarking

RetinaFace is used in the isolated benchmark because reliable face localization is important when comparing recognition models. If detection changes between models, a result may measure detector differences instead of recognition differences.

The benchmark therefore used RetinaFace consistently where supported and recorded `detector_backend=retinaface`. The production default in `app.py` remains OpenCV. OpenCV is lighter and easier to run, but it can be more sensitive to pose, scale, lighting, and image quality.

RetinaFace is not automatically a production recommendation. Before changing the live detector, measure:

- Detection success on target camera footage.
- End-to-end latency and FPS.
- CPU/RAM/GPU cost.
- False detections and missed faces.
- Behavior with multiple faces and partial occlusion.

## 7. Cosine Distance and Thresholds

For two embedding vectors `a` and `b`, cosine similarity is:

```text
cosine_similarity(a, b) = (a . b) / (||a|| ||b||)
```

N-ONE uses cosine distance for the benchmark:

```text
cosine_distance(a, b) = 1 - cosine_similarity(a, b)
```

A smaller distance means the vectors are more similar. A trial is a match when:

```text
 distance <= threshold
```

A lower threshold is stricter: it reduces the chance of accepting an impostor, but it can increase false rejects of genuine victims. A higher threshold is more permissive: it can improve genuine recall, but it can increase false victim matches.

A distance is not a percentage match. N-ONE must report the distance, threshold, and decision. It must not display statements such as `95% match` unless a separate, statistically justified calibration method has been implemented and documented.

## 8. Threshold Configuration

The source default is `0.40`. The Streamlit sidebar exposes the selected model, detector backend, distance metric, and similarity threshold for runtime experimentation. The effective values are stored in Streamlit session state and passed into the frame-processing path.

Thresholds are model- and detector-specific. Do not copy a threshold from FaceNet to FaceNet512 or ArcFace without rerunning an evaluation.

For a threshold change:

1. Keep the current production value recorded.
2. Use independent enrollment and test images.
3. Include genuine victim images and non-victim impostors.
4. Sweep a range of thresholds rather than testing one convenient value.
5. Record TP, TN, FP, FN, precision, recall, F1, FAR, and FRR.
6. Inspect false victim matches individually.
7. Test detector and model availability in the actual deployment environment.
8. Review the result before changing the live default.
9. Keep a rollback value and change record.

Never select a threshold only because it maximizes F1, recall, or precision. Victim Search gives special weight to false victim identification.

## 9. Why ArcFace Is Available and Why It Is Not Automatically the Default

ArcFace, FaceNet512, and FaceNet remain available so N-ONE can be evaluated against different embedding behaviors and deployment constraints. Keeping alternatives available supports:

- Reproducible benchmark comparisons.
- Hardware-specific deployments.
- Threshold calibration per model.
- Regression testing after dependency or camera changes.
- A fallback plan when a model is unavailable or too slow.

The current code does not set ArcFace as the production default. The isolated benchmark provides evidence for considering ArcFace, but it is limited to 5 victim identities, 32 genuine test images, and 10 impostor identities represented by 12 images. That evidence is not proof of production accuracy, universal accuracy, or guaranteed victim identification.

At the benchmark's configured threshold of `0.40`, ArcFace had the strongest measured recall/F1 of the three models and zero false victim matches in the sample. That supports further ArcFace testing, not an automatic production switch.

## 10. Threat Detection Is Different

Threat Detection is an object/scene analysis path. It looks for possible threat regions using the threat-processing logic and records threat or no-threat results. It does not:

- Generate a face identity embedding for the threat decision.
- Compare a face against a victim or staff profile.
- Use the face-recognition cosine threshold to decide whether an object is a weapon.
- Prove that a detected region is a weapon without suitable validation data.

Threat alerts are possible detections that require appropriate human review and threat-specific evaluation. Face-recognition benchmark metrics must not be reused as threat-detection metrics.

## 11. Multi-Frame Confirmation

A single image decision and a multi-frame decision are different measurements. A future confirmation policy could require the same identity decision in 3 or 5 consecutive frames. It should measure:

- False victim matches per sequence.
- False rejects per sequence.
- Confirmation latency.
- Behavior when faces enter or leave the frame.
- Duplicate-frame correlation.

The current benchmark had still images and no labeled video/frame sequences. Its 1-, 3-, and 5-frame results are therefore unavailable, not zero and not estimated.

## 12. How to Use Future Benchmark Results

Future benchmark reports should be compared using the same protocol:

- Same enrollment/test separation.
- Same identities and conditions where possible.
- Same detector configuration.
- Same distance metric.
- Documented threshold sweep.
- Per-image distances and decisions.
- Hardware and software records.

For Victim Search, review in this order:

1. False Victim Matches and FAR.
2. The actual false-positive images and distances.
3. FRR and genuine victim failures.
4. Recall, precision, and F1.
5. Latency and resource cost.
6. Robustness across lighting, pose, blur, distance, occlusion, and multiple faces.

A configuration should be considered for production only when its safety trade-off is acceptable on a larger, representative dataset and the result is reproducible. No benchmark on the current limited sample should be described as universal accuracy.

## 13. Safe Change Checklist

Before changing a production model, detector, metric, or threshold:

- Confirm the full neural runtime is installed and actually active.
- Confirm the selected model and detector are recorded in logs/results.
- Do not mix enrollment images with test images.
- Do not use the same image for enrollment and testing.
- Add independent impostor identities.
- Run a threshold sweep.
- Review false victim matches before recall improvements.
- Record latency and resource usage.
- Test fallback behavior if a dependency is unavailable.
- Obtain the required operational approval.
- Change one configuration dimension at a time where practical.
- Preserve the previous configuration for rollback.
- Do not commit credentials, face images, or runtime logs.

## 14. References Within This Repository

- Production configuration and frame pipeline: `app.py`
- Adapter and OpenCV fallback: `deepface_adapter.py`
- Existing configuration notes: `AI_MODEL_CONFIGURATION.md`
- DeepFace feature notes: `DEEPFACE_FEATURES.md`
- Benchmark report: `docs/AI_MODEL_EVALUATION_REPORT.md`
- Benchmark scripts: `evaluation/scripts/`
- Aggregate benchmark results: `evaluation/results/`

The benchmark report is the source of measured N-ONE results. Published model descriptions explain model design, but they are not substitutes for N-ONE measurements.
