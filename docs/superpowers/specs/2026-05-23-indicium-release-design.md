# Indicium v1.0.0 Release Design

**Date:** 2026-05-23  
**Status:** Approved  
**Scope:** Spec site (GitHub Pages) + GitHub Release v1.0.0 + PyPI-ready packaging + SciTask adapter implementation

---

## 1. Overview

Indicium is a standalone Python package and vocabulary standard for typed scientific claims bound to the evidence that grounds them. This release delivers:

- A public spec site at `HolobiomicsLab.github.io/indicium` (graphical style identical to SciTask)
- A GitHub Release tagged `v1.0.0` with changelog and schema artefacts attached
- A new `adapters/scitask.py` (`claim_to_evidence_snippet()`)
- PyPI packaging metadata prepared; publish step is manual / deferred
- Future domains (`indicium-spec.org`, `w3id.org/indicium`) are not in scope for this release

---

## 2. Site structure

MkDocs Material with the CNRS graphical charter (IBM Plex fonts, navy `#00284b` + yellow `#ffeb6e`, warm paper `#fbf7ef`) — token names changed from `--scitask-*` to `--indicium-*` but hex values identical.

```
Home                  index.md
Quickstart            quickstart.md
Schema
  Overview            schema/index.md
  Claim               schema/claim.md
  Evidence            schema/evidence.md
  Source              schema/source.md
Adapters
  ASTRA               adapters/astra.md
  SciTask             adapters/scitask.md
  KGmemory            adapters/kgmemory.md   ← "In preparation" placeholder
API Reference         api-reference.md        ← mkdocstrings auto-generated
Changelog             changelog.md
```

Static schema artefacts served at predictable URLs (Option C):
```
/schema-assets/indicium.schema.json
/schema-assets/indicium.owl.ttl
/schema-assets/indicium.shapes.ttl
```

---

## 3. Repository layout

```
indicium/
├── docs/
│   ├── index.md
│   ├── quickstart.md
│   ├── schema/
│   │   ├── index.md
│   │   ├── claim.md
│   │   ├── evidence.md
│   │   └── source.md
│   ├── adapters/
│   │   ├── astra.md
│   │   ├── scitask.md
│   │   └── kgmemory.md
│   ├── api-reference.md
│   ├── changelog.md
│   ├── stylesheets/
│   │   └── extra.css
│   └── schema-assets/        ← copied from generated/ at build time
│       ├── indicium.schema.json
│       ├── indicium.owl.ttl
│       └── indicium.shapes.ttl
├── mkdocs.yml
├── .github/
│   └── workflows/
│       ├── docs.yml          ← build + deploy on push to main
│       └── release.yml       ← tag v* → GitHub Release + attach artefacts
├── src/indicium/
│   └── adapters/
│       ├── astra.py          ← existing
│       ├── kgmemory.py       ← existing
│       └── scitask.py        ← new: claim_to_evidence_snippet()
└── pyproject.toml            ← bumped to 1.0.0, PyPI metadata added
```

---

## 4. Home page content

**Hero tagline:**
> **Indicium** — *The shared standard for typed scientific claims bound to their evidence.*

**Standard definition paragraph:**
> Every claim minted by any tool in the agentic science ecosystem carries its **indicia**: the typed, provenance-stamped evidence that justifies believing it. Indicium defines the binding — claim → evidence → source — so claims produced by **ASTRA**, **AgenticScienceBuilder (ASB)**, and **Perspicacité** are structurally identical and mergeable.

*(Link URLs for ASTRA, ASB, and Perspicacité to be confirmed at implementation time.)*

**Reuse axes table:**

| Axis | Standard |
|------|----------|
| Evidence type | ECO (Evidence & Conclusion Ontology) |
| Claim ↔ citation relation | CiTO |
| Source / document type | DoCO + IAO |
| Article type | FaBiO |
| Assertion + evidence structure | SEPIO |
| Provenance | PROV-O |
| Claim structure | Bucur et al. 5-slot SuperPattern (K-CAP 2021) |

**What Indicium defines table:**

| Component | What it is |
|-----------|-----------|
| `Claim` | 5-slot Bucur SuperPattern (context / subject / qualifier / relation / object) with ECO-typed evidence |
| `Evidence` | A typed, CiTO-linked evidence record grounding a claim |
| `Source` | A DoCO/FaBiO-typed document or artefact that an evidence record points to |
| `CitationLink` | A CiTO-typed directed relation between two claims or between a claim and a source |

**Minimal quickstart snippet:**
```python
from indicium import validate_graph, claim_to_insight
from indicium.adapters.scitask import claim_to_evidence_snippet
```

---

## 5. SciTask adapter

New file: `src/indicium/adapters/scitask.py`

**Function:** `claim_to_evidence_snippet(claim: Claim) -> dict`

Maps an Indicium `Claim` to a SciTask `EvidenceSnippet` dict (the structure ASB embeds in SciTask Cards). Fields below are approximate — verify against `scitask-schema/src/scitask_schema/scitask_card.yaml` at implementation time:

| SciTask field | Source |
|---------------|--------|
| `text` | `claim.source_excerpt` |
| `source` | `claim.evidence.of_source.title` or identifier |
| `evidence_type` | mapped from `claim.evidence.evidence_type` (ECO → ASB label) |
| `claim_subject` | `claim.subject` |
| `claim_relation` | `claim.qualifier` + `claim.relation` |
| `claim_object` | `claim.object` |

---

## 6. GitHub Actions workflows

### `docs.yml` — triggered on push to `main`
1. `uv sync --extra codegen`
2. `make gen` (regenerates model.py / shapes.ttl / ontology.ttl / schema.json)
3. Copy `src/indicium/generated/*.{json,ttl}` → `docs/schema-assets/`
4. `mkdocs gh-deploy --force`

### `release.yml` — triggered on push of tag `v*`
1. Same gen + copy as docs.yml
2. `uv build` (wheel + sdist → `dist/`)
3. Extract v1.0.0 section from `docs/changelog.md` as release body
4. `gh release create $TAG --notes "$BODY"` with `dist/*` and `docs/schema-assets/*` attached
5. PyPI upload step is present but commented out — uncomment when token is ready:
   ```yaml
   # - run: uv publish
   #   env:
   #     UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
   ```

---

## 7. `pyproject.toml` additions

```toml
[project]
version = "1.0.0"
readme = "README.md"
license = { text = "MIT" }
keywords = ["linkml", "claims", "evidence", "scientific-standard", "agentic-science"]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

[project.urls]
Homepage = "https://holobiomicslab.github.io/indicium"
Repository = "https://github.com/HolobiomicsLab/indicium"
Changelog = "https://holobiomicslab.github.io/indicium/changelog/"
```

---

## 8. KGmemory adapter page

Single placeholder page in the deployed site:

> **KGmemory adapter** — *In preparation.*
>
> A `claim_jsonld()` adapter for KGmemory is implemented in `src/indicium/adapters/kgmemory.py` and will be documented here when the KGmemory standard is publicly released.

The code is not hidden — it ships in the package — but the public documentation is deferred.

---

## 9. Visual design

CSS token file (`docs/stylesheets/extra.css`) is a direct copy of the SciTask charter with names changed from `--scitask-*` to `--indicium-*`. All hex values are identical:

| Token | Value |
|-------|-------|
| `--indicium-blue` | `#00284b` |
| `--indicium-blue-ink` | `#001833` |
| `--indicium-yellow` | `#ffeb6e` |
| `--indicium-paper` | `#fbf7ef` |
| `--indicium-teal` | `#04919a` |
| `--indicium-ink` | `#16242f` |

Logo: a minimal SVG "I" signet mark in the header (same slot as SciTask's book icon), navy background, yellow accent.

---

## 10. Out of scope for this release

- `indicium-spec.org` domain registration and DNS
- `w3id.org/indicium` namespace registration
- Scriptorium adapter (separate release, later)
- KGmemory adapter documentation
- PyPI publish (packaging prepared; token + publish step manual)
- Making the GitHub repo public
