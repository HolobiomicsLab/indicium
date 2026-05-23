# Changelog

Schema and package version history for Indicium.

Versions follow [Semantic Versioning](https://semver.org/).

---

## Indicium 1.0.0 — 2026-05-23

First stable public release.

### Added

- **Core schema** (`src/indicium/schema/indicium.yaml`) — Claim (Bucur 5-slot
  SuperPattern), Evidence (ECO-typed), Source (DoCO/FaBiO-typed), CitationLink
  (CiTO-typed), with SEPIO assertion structure and PROV-O provenance.
- **Generated artefacts** — Pydantic v2 model (`model.py`), SHACL shapes
  (`shapes.ttl`), OWL ontology (`ontology.ttl`), JSON Schema (`schema.json`).
- **SHACL validation** — `validate_graph()` via pyshacl over generated +
  supplemental shapes.
- **ASTRA adapter** — `claim_to_insight()` projects a Claim to an ASTRA Insight.
- **SciTask adapter** — `claim_to_evidence_snippet()` projects a Claim to a
  SciTask EvidenceSnippet (new in this release).
- **KGmemory adapter** — `claim_jsonld()` emits a JSON-LD node referencing the
  KGmemory namespace (latent; documentation deferred).
- **IRI bindings** — `iri_bindings.py` with canonical ECO/CiTO/DoCO/IAO IRIs.
- **Public API** — `validate_graph`, `claim_to_insight`, `claim_to_evidence_snippet`,
  `claim_jsonld`, `MEM_NS` exported from `indicium`.
- **Spec site** — MkDocs Material site deployed to GitHub Pages
  (`holobiomicslab.github.io/indicium`).
- **GitHub Actions** — `docs.yml` (site deploy on push to main),
  `release.yml` (GitHub Release + artefact upload on tag).
