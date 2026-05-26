# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.6.1] - 2026-05-26

### Fixed

- **Package `context.jsonld` for downstream consumers.** Move
  `docs/context.jsonld` into `src/indicium/schema/context.jsonld` (canonical
  location) and symlink it back to `docs/` so mkdocs continues to publish it.
  Wheels now ship the file, so consumers can load it via
  `importlib.resources.files("indicium.schema") / "context.jsonld"`.

---

## [1.6.0] - 2026-05-24

### Added

- **Claim aliases:** `predicate` (alias for `relation`) and `super_pattern`
  (alias for `qualifier`) — explicit names matching the ASB spec.
- **Evidence aliases + new slots:** `quote_exact` (alias for `quote`),
  `supports_claim` (alias for `for_claim`, mapped to `sepio:0000007`),
  `quote_location` (string locator), `eco_code` (range:
  `EcoCodeAsbSubset`).
- **`EcoCodeAsbSubset` enum** — 8 ECO codes ASB emits (textual_quotation,
  computational_evidence, expert_curation, inference_from_background_knowledge,
  author_statement, experimental_evidence, combinatorial_evidence,
  traceable_author_statement).
- **Source slots:** `doi`, `paragraph_id`, `xpath_pointer` — explicit
  forms of the InformationSource locators ASB targets.
- **`SoftwareEntity` class** — new class for globally-identified tools
  (`canonical_url`, `version`, `edam_operation`, `edam_topics`,
  `bio_tools_id`). Added to `IndiciumDocument.software_entities`.
- **JSON-LD `@context`** at `docs/context.jsonld` — stable mapping for
  downstream consumers. To be served at `w3id.org/indicium/context.jsonld`
  pending the w3id PR; currently published at
  `holobiomicslab.github.io/indicium/context.jsonld`.
- **`docs/sepio-assertion.md`** — reference for the SEPIO assertion
  pattern (skill → claim).
- **`docs/uri-scheme.md`** — reference for `indicium:claim/<uuid>` +
  content-hash citation variant.
- **`tests/fixtures/asb_skill_roundtrip/`** — canonical fixture consumed
  by Plan 1c's round-trip CI test in indicium-adapters.

### Compatibility

All Wave 1 changes are **additive**: every new slot is non-required and
shares its `slot_uri` with an existing slot (where one exists). v1.5
serialisations remain valid; v1.6 consumers gain the spec-required
names.

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
