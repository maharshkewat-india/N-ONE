# Evaluation Dataset

The benchmark dataset must be collected separately from the application's working profile storage. The project should not reuse registration images for test evaluation.

## Required categories

- victims
- staff
- impostors
- unknown
- threats

## Required splits

- enrollment
- test

The enrollment set and test set must be disjoint.

## Recommended minimum volumes

### Victims
- 5-10 identities
- 5 enrollment images per identity
- 20+ independent test images per identity
- optional video samples

### Impostors
- 15-30 non-target identities

### Staff
- 5 identities with separate enroll/test sets

### Unknown
- 5-10 identities with multiple appearances

### Threats
- positive cases
- negative cases
- difficult cases

## Status

No real evaluation data is currently present in this workspace. The dataset folders are scaffolded only to enforce the required structure.
