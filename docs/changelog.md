# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## 2.0.0 — 2026-11-01

First public release. These breaking changes landed *before* any Indicium package
release. Existing downstream records may still embed the earlier context.

### Breaking
- **The `asb:` vocabulary base moved to `https://w3id.org/asb#`.** It had two
  earlier bases. 1.x used `https://asb.holobiomics.org/ns/asb#`, a domain that was
  never registered, so a third party could have taken it and served arbitrary
  definitions for this standard's term IRIs. Indicium PR #4 (2026-06-14) then moved
  it to `https://holobiomicslab.eu/ns/asb#`, and 2.0.0 settles on the permanent
  w3id identifier. Every `asb:` term IRI therefore changes. The 2.0.0 SHACL shapes
  target the w3id IRIs, so they do not recognise a claim typed with either earlier
  base: such a claim goes unchecked instead of failing.
  Released data carries the intermediate base: the 106 `indicium/*.jsonld` files of
  the asb-skill-collections pre-release `metabolomics-v0.1.0` (2026-06-22) bind
  `https://holobiomicslab.eu/ns/asb#` and do not validate against the 2.0.0 shapes.
  To migrate such data, bind the `asb:` prefix of its JSON-LD context (or rewrite
  its IRIs) to `https://w3id.org/asb#`; the local names are unchanged. Then validate
  it with `indicium.validate_graph`. Consumers that bind the `asb:` prefix
  themselves, notably the shape files in `indicium-adapters-metabolomics`, must be
  updated in lockstep.
- **The distribution is renamed `indicium` → `indicium-standard`.** The import
  package is unchanged: `import indicium` still works. The PyPI name `indicium` is
  held by an unrelated, abandoned key-value-store package that also ships a
  top-level `indicium` module; installing both into one environment clobbers the
  import. Depend on `indicium-standard`, never on `indicium`.
- **Two SEPIO bindings are corrected before the namespace deposit.**
  `supports_claim` now expands to `sepio:0000427` (`is_evidence_line_for`),
  an evidence-line-to-claim relation, instead of the oppositely directed
  `sepio:0000007`. Skill reliance `asserts` now expands to `indicium:asserts`,
  declared in the LinkML schema, instead of `sepio:0000130` (`authored_by`).
  JSON keys and the local `for_claim` predicate are unchanged. Refresh embedded
  contexts and regenerate previously expanded RDF. Supporting, disputing or
  inconclusive direction is a separate `sepio:0000183` annotation; the
  historical `supports_claim` key alone does not establish that direction.

### Added
- `LICENSE` (MIT). 1.x declared MIT in `pyproject.toml` but shipped no licence
  text, so a wheel would have distributed MIT-claimed code without the required
  notice.
- **`indicium.ASB_BASE`, `indicium.INDICIUM_BASE`, `indicium.asb_term()`** — the
  vocabulary bases are now part of the public API, read from the generated model's
  prefix map so they cannot drift from the SHACL shapes. Consumers that hardcoded
  the IRI kept validating against a dead namespace after the base moved: the shapes
  matched nothing and every graph reported `conforms=True`. Import these instead.
- `tests/test_namespace_base.py` — guards against reintroducing an unowned
  namespace base, and pins the metadata lookup to the declared distribution name.
- A reproducible JSON-LD context generated from the schema, shipped in the
  package and copied into the documentation site. OBO prefixes expand in JSON-LD
  1.1; property IRIs and enum meanings now agree with the SHACL shapes.
- Local release checks and a Trusted Publishing workflow with matching tag,
  package version and dated changelog checks before publication.

### Fixed
- **`__version__` reported the wrong version.** It queried `importlib.metadata`
  for the distribution `indicium`, which after the rename resolves either to
  nothing (falling back to `0.0.0+unknown`) or to the unrelated squatting PyPI
  package, reporting *its* version as ours. It now queries `indicium-standard`.
  The `wheel-smoke` CI job asserts the installed wheel reports the built version.
- `docs/changelog.md` is now generated from this file (`make docs-changelog`)
  rather than hand-maintained. It had been frozen at 1.0.0 for twelve releases,
  and `release.yml` extracts its release notes from it.
- Installation examples now consistently name `indicium-standard`, including
  its optional extras. Schema generation works on Linux and macOS.
- The generated OWL ontology uses the namespace root `https://w3id.org/indicium` as
  its document IRI and carries the version and the licence (`pav:version`,
  `dct:license`), which the LinkML source now declares; the model and the JSON
  Schema carry the version too. RDF serialization is deterministic for release verification.
- The published SHACL file, `docs/schema-assets/indicium.shapes.ttl` (a release
  asset), now holds the supplemental shapes as well as the generated ones, so a
  SHACL processor run on it agrees with `validate_graph`: before, it accepted a
  claim with neither `qualifier` nor `domain_qualifier`.
- The sdist includes only package source, schema assets and release metadata;
  internal development plans are excluded.
- The package metadata names its author, states the licence as the SPDX
  expression `MIT` with `LICENSE` as its licence file (instead of the full text in
  the License field), and lists Documentation and Issues URLs.
- SEPIO binding regression tests use an attributed excerpt of the ontology's
  inverse, domain and range axioms. The documentation explains the target link,
  separate evidence direction and the local reliance predicate.

### Namespace registration
- Canonical bases remain `https://w3id.org/indicium/` and
  `https://w3id.org/asb#`. The vocabulary deposit and redirects are prepared
  separately; registration does not create a hosted store of claim instances.
- Prepared term redirects send HTML clients to
  `https://holobiomicslab.eu/indicium/reference/<Name>/` and RDF clients to the
  vocabulary representation under `/ns/indicium/`. The reference pages must be
  live before the w3id registration is submitted.
- ASB validation assertions use `SEPIO_0000183` with `SEPIO_0000403`,
  `SEPIO_0000404` or `SEPIO_0000405`, and `RO_0002558` with `ECO_0000501`.
  These are external assertion annotations, not Indicium claim-status values.

---

## 1.12.0 — 2026-06-10
- New `SourceTaskKind` enum {reproduction, analysis, component_reconstruction, extension} + optional `Claim.source_task_kind` slot (`asb:sourceTaskKind`) — a claim-level reproducibility-provenance qualifier, sibling of `Evidence.workflow_coupling` (Suter et al. 2025) at claim↔source-task granularity. Canonical replacement for ASB's out-of-schema `asbext:source_task_kind`. Added to `context.jsonld` for portability. Additive, backward-compatible; SHACL non-closed.

---

## 1.11.0 — 2026-06-03
- New `SSSOMMapping` class (SSSOM term mapping) + `IndiciumDocument.sssom_mappings` collection, with a `derived_from` lineage slot (cthoyt 2026-05-29). Adds sssom/semapv/skos prefixes. Additive, backward-compatible.

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
