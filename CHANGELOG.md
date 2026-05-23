# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.5.0] - 2026-05-23

### Added
- `extra_shapes` keyword argument to `validate_graph()` — callers (e.g. domain adapters via
  `SHACLProvider`) can now inject additional SHACL shapes that are merged with the built-in
  schema shapes before validation.

### Fixed
- `allow_warnings=True` now passed to pyshacl in `validate_graph()` so that `sh:Warning`-severity
  shapes no longer set `conforms=False`; warnings are reported in the validation report text only.
- Conditional SHACL constraint added: `superseded_by` is now required when `claim_status = superseded`.
- Core types (`Claim`, `Evidence`, `Source`, and status enums) are now re-exported from the
  top-level `indicium` package for ergonomic imports.

### Deprecated
- `indicium.adapters.astra.claim_to_insight` — use `astra_bridge` instead.

---

## [1.4.0] - 2026-05-20

### Added
- `IndiciumDocument` container type for grouping claims.
- `superseded_by` field on `Claim`.
- Fixed `ClaimLink` URI generation.

---

## [1.3.0] - 2026-05-15

### Added
- `ClaimLink`, `ClaimStatus` types.
- OA (Web Annotation) selectors for evidence provenance.
- ASTRA bridge adapter.

---

## [1.2.0] - 2026-05-10

### Added
- `Script` and `DataAsset` classes for code/data artefacts as evidence.

---

## [1.1.0] - 2026-05-05

### Added
- `Figure` class and `FigureType` enum for figure-as-evidence support.
