# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 1.10.0 — 2026-06-03
- Evidence gains optional `workflow_coupling` (`WorkflowCoupling` enum: tight/loose/ad_hoc/unknown) — a reproducibility qualifier per Suter et al. 2025 (DOI 10.1016/j.future.2025.107974). Additive, backward-compatible; SHACL non-closed.

---

## [1.9.0] - 2026-05-29

### Added

- **`VerificationResult.char_span`** — a 5th, defaulted field
  (`tuple[int, int] | None = None`) giving `(start, end)` offsets into the
  matched candidate's *original* (un-normalized) text. Populated for verified
  matches from the regex span; best-effort for repaired matches (the recovered
  span is re-located in the original candidate, and may remain `None`). Lets
  callers highlight or re-slice the exact source region without re-searching.
- **`verify_quote(..., punctuation_flexible=True)`** — an opt-in pass between
  exact containment and LCS that matches the quote's alphanumeric tokens
  (`[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*`) in order across arbitrary non-alphanumeric
  padding, with per-token boundary guards. A hit is `verified` with `score = 1.0`
  and a `char_span` spanning first-token-start → last-token-end. This recognises
  a verbatim-modulo-punctuation quote (e.g. `P=0.001` ~ `P = 0.001,`) instead of
  degrading it to a sub-threshold LCS, mirroring ASB `claim_ledger`'s
  token-sequence matcher.

### Why

Lets ASB `claim_ledger` and Perspicacité consume one shared verification kernel:
`char_span` carries the exact source offsets downstream, and the opt-in
punctuation-flexible pass matches numeric/statistical quotes whose punctuation
shifts between extraction and source. **Backward-compatible and additive only**:
both changes are defaulted off / defaulted `None`, existing thresholds and the 11
prior kernel tests are unchanged, and there are no changes to `generated/model.py`,
the SHACL shapes, or any enum.

---

## [1.8.0] - 2026-05-29

### Added

- **`verify_quote` kernel** (`indicium.verify`, exported from the package root)
  — a pure-Python, dependency-light, never-raises verifier that matches an
  LLM-extracted quote against source passage texts. Returns
  `VerificationResult(status, matched_index, quote_exact, score)` where status
  is `verified` (whitespace-flexible, case-sensitive containment; recovers the
  source's verbatim span, `score = 1.0`), `repaired` (no containment, but the
  longest common substring vs the best candidate clears `near_threshold`,
  default 0.9), or `unverified`. Structurally guarantees
  `unverified ⇒ matched_index is None`; degenerate input (empty/whitespace
  quote, empty candidates, or `None`/non-str entries) degrades safely instead
  of raising.
- Exported `verify_quote` and `VerificationResult` from the package root.

### Why

Lets downstream projects (Perspicacité R3, ASB) ground claim / parameter /
failure-mode quotes against original source text — verifying provenance and
catching paraphrase or hallucination — without depending on rdflib or the
generated model. **Additive only**: no changes to `generated/model.py`, the
SHACL shapes, or any enum.

---

## [1.7.0] - 2026-05-29

### Added

- **`domain_qualifier` slot** (`slot_uri: asb:domainQualifier`) — an OPEN,
  snake_case-patterned (`^[a-z][a-z0-9_]*$`) qualifier slot for domain-adapter
  vocabularies (e.g. transcriptomics `aligned_with`,
  `differentially_expressed_in`). This is the standard's side-channel for
  domain extensions, mirroring how enrichment terms ride on
  `asb:*_ontology_term`. The closed Bucur `SuperPatternQualifier` enum on
  `asb:qualifier` is **unchanged** — domain terms never pollute it.
- **`QualifierPresenceShape`** (supplemental SHACL, `sh:or`) — a Claim must
  carry at least one of `asb:qualifier` (closed Bucur SuperPattern) or
  `asb:domainQualifier` (open domain extension).

### Changed

- **`qualifier` slot is no longer `required` on its own.** A Claim previously
  had to carry a core Bucur qualifier; it may now satisfy the "at least one
  qualifier" rule via `domain_qualifier` instead. The closed enum and its
  `maxCount 1` are retained; only the slot-level `minCount 1` moved to the
  either-or `QualifierPresenceShape`.

### Why

Resolves **indicium#1** (reported by Dina, 2026-05-29). Domain-adapter
qualifiers extended `asb:qualifier` directly, but that slot is a CLOSED 20-term
LinkML enum (Bucur K-CAP 2021), so the generated `sh:in` shapes rejected every
extended qualifier — blocking all domain adapters (metabolomics, metabokg, emi,
transcriptomics) and the ASB benchmark. SHACL merges additively
(`validate_graph` graph-union), so an adapter-side shape could never relax the
existing `sh:in`; the fix had to live in the core standard. We chose to keep
`asb:qualifier` pristine and route domain qualifiers to a new open slot
(Reading 1) rather than dilute the published closed vocabulary.

### Compatibility

Additive. v1.6 serialisations always carry a core `asb:qualifier`, so they
still satisfy `QualifierPresenceShape` and remain valid. Consumers gain the
`domain_qualifier` slot; no existing slot changed its `slot_uri` or range.

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
