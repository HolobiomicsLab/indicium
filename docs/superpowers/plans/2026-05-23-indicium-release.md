# Indicium v1.0.0 Release — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the Indicium v1.0.0 release: SciTask adapter, MkDocs spec site deployed to GitHub Pages, GitHub Release tagged v1.0.0, and PyPI-ready packaging.

**Architecture:** Indicium is a pure-Python package at `src/indicium/`. All adapters follow the same dict-in / dict-out pattern as `adapters/astra.py`. The spec site is built with MkDocs Material using the CNRS graphical charter (identical tokens to scitask-spec.org). Two GitHub Actions workflows handle site deployment (on push to `main`) and release (on push of tag `v*`).

**Tech Stack:** Python 3.11+, uv, LinkML (codegen only), MkDocs Material + mkdocstrings[python], pyshacl, rdflib, GitHub Actions, hatchling.

**Reference files:**
- Adapter pattern: `src/indicium/adapters/astra.py`
- Adapter test pattern: `tests/test_astra_adapter.py`
- CSS charter reference: `~/git/AgenticScienceBuilder/site/stylesheets/extra.css`
- SciTask mkdocs.yml: `~/git/AgenticScienceBuilder/mkdocs.yml`
- EvidenceSnippet fields (from ASB): `snippet_id: str`, `source_path: str`, `reason: str`, `text: str`

---

## File map

| Action | Path | Purpose |
|--------|------|---------|
| Create | `src/indicium/adapters/scitask.py` | `claim_to_evidence_snippet()` |
| Modify | `src/indicium/__init__.py` | export `claim_to_evidence_snippet` |
| Create | `tests/test_scitask_adapter.py` | adapter tests |
| Modify | `pyproject.toml` | version 1.0.0 + PyPI metadata + docs extra |
| Create | `mkdocs.yml` | MkDocs Material site config |
| Create | `docs/stylesheets/extra.css` | CNRS charter tokens |
| Create | `docs/index.md` | Home page |
| Create | `docs/quickstart.md` | Install + usage guide |
| Create | `docs/schema/index.md` | Schema overview |
| Create | `docs/schema/claim.md` | Claim class reference |
| Create | `docs/schema/evidence.md` | Evidence + CitationLink reference |
| Create | `docs/schema/source.md` | Source class reference |
| Create | `docs/adapters/astra.md` | ASTRA adapter docs |
| Create | `docs/adapters/scitask.md` | SciTask adapter docs |
| Create | `docs/adapters/kgmemory.md` | KGmemory placeholder |
| Create | `docs/api-reference.md` | Auto-generated API ref |
| Create | `docs/changelog.md` | v1.0.0 changelog |
| Create | `.github/workflows/docs.yml` | Deploy site on push to main |
| Create | `.github/workflows/release.yml` | GitHub Release + assets on tag |
| Modify | `Makefile` | add `schema-assets` copy target |

---

## Task 1: SciTask adapter — failing test

**Files:**
- Create: `tests/test_scitask_adapter.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_scitask_adapter.py
from indicium.adapters.scitask import claim_to_evidence_snippet


def _make_claim(**overrides):
    base = {
        "id": "c001",
        "context": "in vitro",
        "subject": "compound A",
        "qualifier": "inhibits",
        "relation": "inhibits growth of",
        "object": "cell line B",
        "source_excerpt": "Compound A inhibited cell line B by 80%.",
        "evidence": [{"doi": "10.1234/x", "artifact": "results/fig1.png"}],
    }
    base.update(overrides)
    return base


def test_required_fields_present():
    snip = claim_to_evidence_snippet(_make_claim())
    assert snip["snippet_id"] == "c001"
    assert snip["source_path"] == "results/fig1.png"
    assert "compound A" in snip["reason"]
    assert snip["text"] == "Compound A inhibited cell line B by 80%."


def test_source_path_falls_back_to_doi():
    claim = _make_claim(evidence=[{"doi": "10.1234/x"}])
    snip = claim_to_evidence_snippet(claim)
    assert snip["source_path"] == "doi:10.1234/x"


def test_text_falls_back_to_quote():
    claim = _make_claim(source_excerpt="")
    claim["evidence"] = [{"doi": "10.1234/x", "quote": "A inhibited B"}]
    snip = claim_to_evidence_snippet(claim)
    assert snip["text"] == "A inhibited B"


def test_explicit_source_path_overrides():
    snip = claim_to_evidence_snippet(_make_claim(), source_path="custom/path.txt")
    assert snip["source_path"] == "custom/path.txt"


def test_empty_evidence_produces_valid_snippet():
    claim = _make_claim(evidence=[])
    snip = claim_to_evidence_snippet(claim)
    assert snip["snippet_id"] == "c001"
    assert snip["source_path"] == ""
    assert snip["text"] == "Compound A inhibited cell line B by 80%."
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd ~/git/indicium && uv run pytest tests/test_scitask_adapter.py -v
```

Expected: `ModuleNotFoundError: No module named 'indicium.adapters.scitask'`

---

## Task 2: SciTask adapter — implementation

**Files:**
- Create: `src/indicium/adapters/scitask.py`

- [ ] **Step 1: Write the implementation**

```python
# src/indicium/adapters/scitask.py
"""Project an indicium Claim onto a SciTask EvidenceSnippet dict.

SciTask EvidenceSnippet fields: snippet_id, source_path, reason, text.
See: scitask-schema/src/scitask_schema/scitask_card.yaml → EvidenceSnippet.
"""
from __future__ import annotations


def claim_to_evidence_snippet(claim: dict, source_path: str = "") -> dict:
    """Map an Indicium Claim dict to a SciTask EvidenceSnippet dict.

    Args:
        claim: An Indicium claim dict with at minimum: id, context, subject,
               qualifier, relation, object. Optional: source_excerpt, evidence.
        source_path: Explicit source path override. When omitted, the first
                     evidence artifact path is used; falls back to doi:<doi>.

    Returns:
        A dict with snippet_id, source_path, reason, text — all required fields
        for a SciTask EvidenceSnippet.
    """
    # Resolve source_path from evidence if not supplied
    if not source_path:
        for ev in claim.get("evidence", []):
            if ev.get("artifact"):
                source_path = ev["artifact"]
                break
            elif ev.get("doi"):
                source_path = f"doi:{ev['doi']}"
                break

    # Resolve text from source_excerpt, then evidence quotes
    text = claim.get("source_excerpt", "")
    if not text:
        for ev in claim.get("evidence", []):
            if ev.get("quote"):
                text = ev["quote"]
                break

    # Build a human-readable reason from the 5-slot SuperPattern
    reason = (
        f"{claim['subject']} {claim['qualifier']} {claim['relation']} "
        f"{claim['object']} (context: {claim['context']})"
    )

    return {
        "snippet_id": claim["id"],
        "source_path": source_path,
        "reason": reason,
        "text": text,
    }
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd ~/git/indicium && uv run pytest tests/test_scitask_adapter.py -v
```

Expected: 5 tests pass.

- [ ] **Step 3: Commit**

```bash
cd ~/git/indicium
git add src/indicium/adapters/scitask.py tests/test_scitask_adapter.py
git commit -m "feat: SciTask adapter — claim_to_evidence_snippet()"
```

---

## Task 3: Export adapter from package `__init__`

**Files:**
- Modify: `src/indicium/__init__.py`

- [ ] **Step 1: Add the import**

Current `__init__.py`:
```python
from indicium.validate import validate_graph
from indicium.adapters.astra import claim_to_insight
from indicium.adapters.kgmemory import claim_jsonld, MEM_NS

__all__ = ["validate_graph", "claim_to_insight", "claim_jsonld", "MEM_NS"]
```

Replace with:
```python
from indicium.validate import validate_graph
from indicium.adapters.astra import claim_to_insight
from indicium.adapters.kgmemory import claim_jsonld, MEM_NS
from indicium.adapters.scitask import claim_to_evidence_snippet

__all__ = [
    "validate_graph",
    "claim_to_insight",
    "claim_jsonld",
    "MEM_NS",
    "claim_to_evidence_snippet",
]
```

- [ ] **Step 2: Verify the full test suite still passes**

```bash
cd ~/git/indicium && uv run pytest -v
```

Expected: all existing tests + 5 new adapter tests pass.

- [ ] **Step 3: Commit**

```bash
cd ~/git/indicium
git add src/indicium/__init__.py
git commit -m "feat: export claim_to_evidence_snippet from package root"
```

---

## Task 4: Bump version and add PyPI metadata

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Replace `pyproject.toml` content**

```toml
[project]
name = "indicium"
version = "1.0.0"
description = "Shared claim/evidence standard (ECO/CiTO/SEPIO/PROV-O + Bucur SuperPattern)"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }
keywords = [
    "linkml", "claims", "evidence", "scientific-standard",
    "agentic-science", "eco", "cito", "sepio", "prov-o",
]
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
]

[project.urls]
Homepage = "https://holobiomicslab.github.io/indicium"
Repository = "https://github.com/HolobiomicsLab/indicium"
Changelog = "https://holobiomicslab.github.io/indicium/changelog/"

# Runtime is intentionally light: validate_graph + the generated pydantic model
# + adapters import only rdflib/pyshacl. `linkml` (the generator) and
# `linkml-runtime` (SchemaView) are needed ONLY for `make gen` and the
# schema-load tests — see the `codegen` extra.
dependencies = [
    "pyshacl>=0.26",
    "rdflib>=7.0",
]

[project.optional-dependencies]
codegen = [
    "linkml>=1.8",
    "linkml-runtime>=1.8",
    "pyyaml>=6.0",
]
docs = [
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/indicium"]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "linkml>=1.8",
    "linkml-runtime>=1.8",
    "pyyaml>=6.0",
    "mkdocs-material>=9.5",
    "mkdocstrings[python]>=0.25",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: Sync and verify tests still pass**

```bash
cd ~/git/indicium && uv sync && uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
cd ~/git/indicium
git add pyproject.toml uv.lock
git commit -m "chore: bump to 1.0.0, add PyPI metadata and docs extra"
```

---

## Task 5: MkDocs config

**Files:**
- Create: `mkdocs.yml`

- [ ] **Step 1: Write `mkdocs.yml`**

```yaml
site_name: Indicium
site_url: https://holobiomicslab.github.io/indicium
site_description: >-
  Indicium — the shared standard for typed scientific claims bound to their
  evidence. ECO / CiTO / SEPIO / PROV-O + Bucur SuperPattern.
site_author: HolobiomicsLab

repo_name: HolobiomicsLab/indicium
repo_url: https://github.com/HolobiomicsLab/indicium

docs_dir: docs
site_dir: site

theme:
  name: material
  palette:
    - scheme: default
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - scheme: slate
      primary: custom
      accent: custom
      toggle:
        icon: material/brightness-4
        name: Switch to light mode
  font:
    text: IBM Plex Sans
    code: IBM Plex Mono
  features:
    - navigation.tabs
    - navigation.sections
    - toc.integrate
    - content.code.copy

extra_css:
  - stylesheets/extra.css

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [src]
          options:
            show_source: false
            show_root_heading: true
            show_category_heading: true
            docstring_style: google
            show_signature_annotations: true

nav:
  - Home: index.md
  - Quickstart: quickstart.md
  - Schema:
    - Overview: schema/index.md
    - Claim: schema/claim.md
    - Evidence: schema/evidence.md
    - Source: schema/source.md
  - Adapters:
    - ASTRA: adapters/astra.md
    - SciTask: adapters/scitask.md
    - KGmemory: adapters/kgmemory.md
  - API Reference: api-reference.md
  - Changelog: changelog.md

markdown_extensions:
  - admonition
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.superfences
  - tables
  - toc:
      permalink: true
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add mkdocs.yml
git commit -m "docs: add mkdocs.yml (Material theme, CNRS charter)"
```

---

## Task 6: CNRS CSS charter

**Files:**
- Create: `docs/stylesheets/extra.css`

- [ ] **Step 1: Create the directory and write the file**

```bash
mkdir -p ~/git/indicium/docs/stylesheets
```

```css
/* Indicium spec site — CNRS graphical charter
   Token palette mirrors SciTask (scitask-spec.org) exactly.
   Source of truth: styles/tokens.css in holobiomicslab_website.
   ---------------------------------------------------------------- */

@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&family=IBM+Plex+Serif:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

/* ── Light mode tokens ── */
:root {
  --indicium-blue:        #00284b;
  --indicium-blue-ink:   #001833;
  --indicium-blue-soft:  #0d3a66;
  --indicium-yellow:     #ffeb6e;
  --indicium-yellow-soft:#fff5a6;
  --indicium-paper:      #fbf7ef;
  --indicium-paper-2:    #f3ecdc;
  --indicium-ink:        #16242f;
  --indicium-mute:       #5d6a78;
  --indicium-teal:       #04919a;

  --md-primary-fg-color:          var(--indicium-blue);
  --md-primary-fg-color--light:   var(--indicium-blue-soft);
  --md-primary-fg-color--dark:    var(--indicium-blue-ink);
  --md-primary-bg-color:          var(--indicium-paper);
  --md-accent-fg-color:           var(--indicium-teal);
  --md-accent-fg-color--transparent: rgba(4, 145, 154, 0.1);

  --md-default-bg-color:          var(--indicium-paper);
  --md-default-fg-color:          var(--indicium-ink);
  --md-default-fg-color--light:   var(--indicium-mute);
  --md-default-fg-color--lighter: #8b95a1;

  --md-code-bg-color:             var(--indicium-paper-2);
  --md-code-fg-color:             var(--indicium-blue);

  --md-typeset-a-color:           var(--indicium-teal);

  --indicium-table-head-bg:       var(--indicium-blue);
  --indicium-table-stripe:        var(--indicium-paper-2);
}

/* ── Dark (slate) mode ── */
[data-md-color-scheme="slate"] {
  --md-default-bg-color:          var(--indicium-blue-ink);
  --md-default-fg-color:          var(--indicium-paper);
  --md-default-fg-color--light:   #aebccb;
  --md-code-bg-color:             #00203c;
  --md-code-fg-color:             var(--indicium-paper);
  --md-primary-fg-color:          var(--indicium-yellow);
  --md-accent-fg-color:           #2dd4bf;
  --indicium-table-head-bg:       #062a4d;
  --indicium-table-stripe:        #00203c;
}

/* ── Typography ── */
body, .md-content, .md-typeset {
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.md-typeset h1, .md-typeset h2, .md-typeset h3,
.md-typeset h4, .md-typeset h5 {
  font-family: 'IBM Plex Serif', Georgia, serif;
  font-weight: 500;
  letter-spacing: -0.01em;
  color: var(--indicium-blue);
}

[data-md-color-scheme="slate"] .md-typeset h1,
[data-md-color-scheme="slate"] .md-typeset h2,
[data-md-color-scheme="slate"] .md-typeset h3 {
  color: var(--indicium-paper);
}

code, pre, .md-typeset code, .md-typeset pre {
  font-family: 'IBM Plex Mono', ui-monospace, monospace;
}

/* ── Header & tabs ── */
.md-header {
  background: var(--indicium-blue);
  box-shadow: 0 1px 0 rgba(255, 235, 110, 0.3);
}

.md-tabs {
  background: var(--indicium-blue-soft);
}

/* ── Nav active link ── */
.md-nav__link--active,
.md-nav__link:is(:focus, :hover) {
  color: var(--indicium-teal) !important;
}

.md-tabs__link--active,
.md-tabs__link:hover {
  color: var(--indicium-yellow) !important;
}

/* ── Sidebar ── */
.md-sidebar { background: var(--indicium-paper); }
[data-md-color-scheme="slate"] .md-sidebar { background: #00203c; }

/* ── Admonitions — yellow left-rule ── */
.md-typeset .admonition, .md-typeset details {
  border-left: 4px solid var(--indicium-yellow) !important;
  background: var(--indicium-yellow-soft) !important;
  border-radius: 4px;
}

.md-typeset .admonition-title, .md-typeset summary {
  background: rgba(255, 235, 110, 0.35) !important;
  color: var(--indicium-blue) !important;
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-weight: 600;
}

[data-md-color-scheme="slate"] .md-typeset .admonition,
[data-md-color-scheme="slate"] .md-typeset details {
  background: #1a2d3f !important;
  border-left-color: var(--indicium-yellow) !important;
}

[data-md-color-scheme="slate"] .md-typeset .admonition-title {
  background: rgba(255, 235, 110, 0.12) !important;
  color: var(--indicium-yellow) !important;
}

/* ── Tables ── */
.md-typeset table:not([class]) th {
  background: var(--indicium-table-head-bg);
  color: var(--indicium-paper);
  font-family: 'IBM Plex Sans', system-ui, sans-serif;
  font-weight: 600;
}

.md-typeset table:not([class]) tr:nth-child(even) {
  background: var(--indicium-table-stripe);
}

/* ── Clipboard ── */
.md-clipboard { color: var(--indicium-teal); }
.md-clipboard:hover { color: var(--indicium-blue); }

/* ── Footer ── */
.md-footer { background: var(--indicium-blue-ink); color: var(--indicium-paper); }
.md-footer a { color: var(--indicium-yellow); }

/* ── Selection ── */
::selection { background: var(--indicium-yellow); color: var(--indicium-blue); }

/* ── Scrollbar (WebKit) ── */
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb {
  background: rgba(0, 40, 75, 0.2);
  border-radius: 999px;
}
[data-md-color-scheme="slate"] *::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.15);
}

/* ── Reduced motion ── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    transition-duration: 0.001ms !important;
  }
}
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add docs/stylesheets/extra.css
git commit -m "docs: CNRS charter CSS (indicium tokens)"
```

---

## Task 7: Home page

**Files:**
- Create: `docs/index.md`

- [ ] **Step 1: Write `docs/index.md`**

```markdown
# Indicium

**The shared standard for typed scientific claims bound to their evidence.**

Every claim minted by any tool in the agentic science ecosystem carries its
**indicia**: the typed, provenance-stamped evidence that justifies believing it.
Indicium defines the binding — claim → evidence → source — so claims produced
by [ASTRA](https://astra-spec.org), [AgenticScienceBuilder (ASB)](https://github.com/HolobiomicsLab/AgenticScienceBuilder),
and [Perspicacité](https://holobiomicslab.github.io/Perspicacite-AI) are
structurally identical and mergeable.

---

## Reuse axes

| Axis | Standard |
|------|----------|
| Evidence type | **ECO** (Evidence & Conclusion Ontology) |
| Claim ↔ citation relation | **CiTO** |
| Source / document type | **DoCO** + **IAO** |
| Article type | **FaBiO** |
| Assertion + evidence structure | **SEPIO** |
| Provenance | **PROV-O** |
| Claim structure | **Bucur et al.** 5-slot SuperPattern (K-CAP 2021) |

## What Indicium defines

| Component | What it is |
|-----------|-----------|
| [`Claim`](schema/claim.md) | 5-slot Bucur SuperPattern (context / subject / qualifier / relation / object) with ECO-typed evidence |
| [`Evidence`](schema/evidence.md) | A typed, CiTO-linked evidence record grounding a claim |
| [`Source`](schema/source.md) | A DoCO/FaBiO-typed document or artefact that an evidence record points to |
| [`CitationLink`](schema/evidence.md#citationlink) | A CiTO-typed directed relation between two claims or between a claim and a source |

## Install

```bash
pip install indicium
```

## Quickstart

```python
from indicium import validate_graph, claim_to_insight
from indicium.adapters.scitask import claim_to_evidence_snippet

claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
    "evidence": [{"doi": "10.1234/test"}],
}

# Project to SciTask EvidenceSnippet
snip = claim_to_evidence_snippet(claim)

# Project to ASTRA Insight
insight = claim_to_insight(claim)
```

## Schema artefacts

Machine-readable artefacts generated from the [LinkML source](https://github.com/HolobiomicsLab/indicium/blob/main/src/indicium/schema/indicium.yaml):

| Artefact | Link |
|----------|------|
| JSON Schema | [`indicium.schema.json`](schema-assets/indicium.schema.json) |
| OWL Ontology | [`indicium.owl.ttl`](schema-assets/indicium.owl.ttl) |
| SHACL Shapes | [`indicium.shapes.ttl`](schema-assets/indicium.shapes.ttl) |

## The name

*Indicium* (Latin) is "a sign or mark that points to the truth" — in law, the
evidentiary indication. Every claim carries its **indicia**, the traces that
justify believing it.
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add docs/index.md
git commit -m "docs: home page (indicium v1.0.0)"
```

---

## Task 8: Quickstart page

**Files:**
- Create: `docs/quickstart.md`

- [ ] **Step 1: Write `docs/quickstart.md`**

```markdown
# Quickstart

## Install

```bash
pip install indicium
# or with uv:
uv add indicium
```

For codegen (regenerating pydantic model / SHACL / OWL from the LinkML source):

```bash
pip install indicium[codegen]
```

## Round-trip example

```python
from indicium import validate_graph, claim_to_insight, claim_to_evidence_snippet

claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
    "evidence": [
        {
            "doi": "10.1234/test",
            "quote": "Compound A inhibited cell line B by 80%.",
            "evidence_type": "data",
        }
    ],
}

# Project to ASTRA Insight (for astra validate)
insight = claim_to_insight(claim)
print(insight)
# {'id': 'c001', 'claim': 'compound A inhibits growth of cell line B (in vitro)',
#  'evidence': [{'doi': '10.1234/test', 'quote': {'exact': 'Compound A ...'}}]}

# Project to SciTask EvidenceSnippet (for ASB SciTask Cards)
snip = claim_to_evidence_snippet(claim)
print(snip)
# {'snippet_id': 'c001', 'source_path': 'doi:10.1234/test',
#  'reason': 'compound A inhibits inhibits growth of cell line B (context: in vitro)',
#  'text': 'Compound A inhibited cell line B by 80%.'}
```

## SHACL validation

```python
import rdflib
from indicium import validate_graph

g = rdflib.Graph()
g.parse("my_claims.ttl", format="turtle")

conforms, report = validate_graph(g)
if not conforms:
    print(report)
```

## Regenerate schema artefacts

```bash
cd path/to/indicium
uv sync --extra codegen
make gen
```

This regenerates `src/indicium/generated/model.py`, `shapes.ttl`, `ontology.ttl`, `schema.json` from the LinkML source at `src/indicium/schema/indicium.yaml`.
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add docs/quickstart.md
git commit -m "docs: quickstart page"
```

---

## Task 9: Schema pages

**Files:**
- Create: `docs/schema/index.md`
- Create: `docs/schema/claim.md`
- Create: `docs/schema/evidence.md`
- Create: `docs/schema/source.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p ~/git/indicium/docs/schema
```

- [ ] **Step 2: Write `docs/schema/index.md`**

```markdown
# Schema Overview

The Indicium schema has one LinkML source of truth:
[`src/indicium/schema/indicium.yaml`](https://github.com/HolobiomicsLab/indicium/blob/main/src/indicium/schema/indicium.yaml)

From it, four artefacts are generated:

| Artefact | Purpose |
|----------|---------|
| `generated/model.py` | Pydantic v2 models for Python consumers |
| `generated/schema.json` | JSON Schema for any language |
| `generated/shapes.ttl` | SHACL shapes for RDF validation |
| `generated/ontology.ttl` | OWL ontology for semantic alignment |

## Core classes

```
Claim
 └── evidence: list[Evidence]
      └── of_source: Source

CitationLink   (connects two Claims or a Claim to a Source)
```

## The binding

The one thing Indicium mints is the **binding**: a claim → typed evidence → a
source, provenance-stamped. The claim structure is borrowed from Bucur et al.;
the value Indicium standardizes is the *typed grounding of claims in evidence.*
```

- [ ] **Step 3: Write `docs/schema/claim.md`**

```markdown
# Claim

A scientific claim expressed using the
[Bucur et al. (K-CAP 2021)](https://dl.acm.org/doi/10.1145/3460210.3493560)
5-slot SuperPattern.

## Slots

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `context` | yes | `asb:context` | The experimental or conceptual setting |
| `subject` | yes | `asb:subject` | What the claim is about |
| `qualifier` | yes | `asb:qualifier` | Directional relation from the 20-term vocabulary |
| `relation` | yes | `asb:relation` | Free-text relation elaboration |
| `object` | yes | `asb:object` | The target entity |
| `claim_type` | no | — | `explicit` or `implicit` |
| `source_excerpt` | no | — | Verbatim text from the source |

## SuperPatternQualifier vocabulary

20 terms from Bucur et al.: `causes`, `prevents`, `inhibits`, `activates`,
`increases`, `decreases`, `correlates_with`, `is_associated_with`, `predicts`,
`interacts_with`, `produces`, `requires`, `enables`, `treats`, `enhances`,
`reduces`, `has_property`, `is_part_of`, `is_a`, `consistent_with`.

## Example

```python
claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "claim_type": "explicit",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
}
```
```

- [ ] **Step 4: Write `docs/schema/evidence.md`**

```markdown
# Evidence & CitationLink

## Evidence

An `Evidence` record grounds a `Claim` in a typed source.

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `evidence_type` | no | ECO | Type of evidence (see table below) |
| `source_type` | no | DoCO/IAO | Type of source document or artefact |
| `quote` | no | — | Verbatim passage from the source |
| `confidence` | no | — | Float 0–1 |
| `of_source` | no | — | The `Source` this evidence points to |
| `for_claim` | no | — | The `Claim` this evidence grounds |

### EvidenceType (ECO-mapped)

| Value | ECO IRI |
|-------|---------|
| `data` | ECO:0000006 |
| `citation` | ECO:0000033 |
| `knowledge` | ECO:0000302 |
| `inference` | ECO:0000361 |
| `speculation` | ECO:0000034 |

### SourceType (DoCO/IAO-mapped)

| Value | IRI |
|-------|-----|
| `text` | IAO:0000311 |
| `figure` | doco:Figure |
| `table` | doco:Table |
| `image` | IAO:0000536 |

## CitationLink

A CiTO-typed directed relation between a claim and another claim or source.

| Slot | Ontology | Description |
|------|----------|-------------|
| `link_type` | CiTO | Relation type (see table below) |

### LinkType (CiTO-mapped)

| Value | CiTO IRI |
|-------|---------|
| `supports` | cito:supports |
| `disputes` | cito:disputes |
| `qualifies` | cito:qualifies |
| `citesForInformation` | cito:citesForInformation |
```

- [ ] **Step 5: Write `docs/schema/source.md`**

```markdown
# Source

A `Source` is a DoCO/FaBiO-typed document or artefact that an `Evidence` record
points to.

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `identifier` | yes | `dct:identifier` | DOI, URL, or local path |
| `title` | no | `dct:title` | Human-readable title |
| `authors` | no | — | List of author names |
| `license_id` | no | — | SPDX license identifier |

## Example

```python
source = {
    "identifier": "10.1234/test",
    "title": "Inhibition study of compound A",
    "authors": ["Smith J", "Doe A"],
}
```
```

- [ ] **Step 6: Commit**

```bash
cd ~/git/indicium
git add docs/schema/
git commit -m "docs: schema reference pages (Claim, Evidence, Source)"
```

---

## Task 10: Adapter pages

**Files:**
- Create: `docs/adapters/astra.md`
- Create: `docs/adapters/scitask.md`
- Create: `docs/adapters/kgmemory.md`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p ~/git/indicium/docs/adapters
```

- [ ] **Step 2: Write `docs/adapters/astra.md`**

```markdown
# ASTRA Adapter

Projects an Indicium `Claim` dict onto an
[ASTRA](https://astra-spec.org) `Insight` dict.

## Function

```python
from indicium.adapters.astra import claim_to_insight

insight = claim_to_insight(claim)
```

The 5-slot SuperPattern is flattened into a single `claim` string.
Evidence records map to ASTRA `evidence` entries (doi or artifact + optional quote).
This is a lossy projection — full typing is preserved in the RDF/RO-Crate forms.

## Mapping

| ASTRA field | Indicium source |
|-------------|----------------|
| `id` | `claim["id"]` |
| `claim` | `"{subject} {relation} {object} ({context})"` |
| `evidence[].doi` | `evidence[].doi` |
| `evidence[].artifact` | `evidence[].artifact` |
| `evidence[].quote.exact` | `evidence[].quote` |

## Example

```python
from indicium.adapters.astra import claim_to_insight

claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "evidence": [{"doi": "10.1234/x", "quote": "A inhibited B by 80%."}],
}

insight = claim_to_insight(claim)
# {
#   "id": "c001",
#   "claim": "compound A inhibits growth of cell line B (in vitro)",
#   "evidence": [{"doi": "10.1234/x", "quote": {"exact": "A inhibited B by 80%."}}]
# }
```
```

- [ ] **Step 3: Write `docs/adapters/scitask.md`**

```markdown
# SciTask Adapter

Projects an Indicium `Claim` dict onto a
[SciTask Standard](https://holobiomicslab.github.io/AgenticScienceBuilder)
`EvidenceSnippet` dict — the structure embedded in SciTask Cards by
[AgenticScienceBuilder (ASB)](https://github.com/HolobiomicsLab/AgenticScienceBuilder).

## Function

```python
from indicium.adapters.scitask import claim_to_evidence_snippet

snip = claim_to_evidence_snippet(claim)
# or with an explicit source path:
snip = claim_to_evidence_snippet(claim, source_path="results/fig1.png")
```

## Mapping

| SciTask field | Indicium source |
|---------------|----------------|
| `snippet_id` | `claim["id"]` |
| `source_path` | First `evidence[].artifact`, then `"doi:<doi>"`, then `""` |
| `reason` | `"{subject} {qualifier} {relation} {object} (context: {context})"` |
| `text` | `claim["source_excerpt"]`, then first `evidence[].quote`, then `""` |

## Example

```python
from indicium.adapters.scitask import claim_to_evidence_snippet

claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
    "evidence": [{"doi": "10.1234/x", "artifact": "results/fig1.png"}],
}

snip = claim_to_evidence_snippet(claim)
# {
#   "snippet_id": "c001",
#   "source_path": "results/fig1.png",
#   "reason": "compound A inhibits inhibits growth of cell line B (context: in vitro)",
#   "text": "Compound A inhibited cell line B by 80%."
# }
```
```

- [ ] **Step 4: Write `docs/adapters/kgmemory.md`**

```markdown
# KGmemory Adapter

!!! note "In preparation"
    The KGmemory adapter documentation will be published here when the
    KGmemory standard is publicly released.

A `claim_jsonld()` adapter for KGmemory is implemented in
`src/indicium/adapters/kgmemory.py` and ships with this package.
It emits a JSON-LD node referencing the KGmemory namespace
(`http://kgmemory.org/ns#SemanticMemory`) so an Indicium claim is
ingestible when KGmemory adopts the vocabulary.
```

- [ ] **Step 5: Commit**

```bash
cd ~/git/indicium
git add docs/adapters/
git commit -m "docs: adapter pages (ASTRA, SciTask, KGmemory placeholder)"
```

---

## Task 11: API reference + Changelog pages

**Files:**
- Create: `docs/api-reference.md`
- Create: `docs/changelog.md`

- [ ] **Step 1: Write `docs/api-reference.md`**

```markdown
# API Reference

## Package root (`indicium`)

::: indicium
    options:
      members:
        - validate_graph
        - claim_to_insight
        - claim_to_evidence_snippet
        - claim_jsonld
        - MEM_NS

## Adapters

### ASTRA (`indicium.adapters.astra`)

::: indicium.adapters.astra
    options:
      members:
        - claim_to_insight

### SciTask (`indicium.adapters.scitask`)

::: indicium.adapters.scitask
    options:
      members:
        - claim_to_evidence_snippet

### KGmemory (`indicium.adapters.kgmemory`)

::: indicium.adapters.kgmemory
    options:
      members:
        - claim_jsonld
        - MEM_NS

## Validation (`indicium.validate`)

::: indicium.validate
    options:
      members:
        - validate_graph
```

- [ ] **Step 2: Write `docs/changelog.md`**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
cd ~/git/indicium
git add docs/api-reference.md docs/changelog.md
git commit -m "docs: API reference and changelog pages"
```

---

## Task 12: Makefile — schema-assets target

**Files:**
- Modify: `Makefile`

- [ ] **Step 1: Update the Makefile**

Current content:
```makefile
SCHEMA=src/indicium/schema/indicium.yaml
GEN=src/indicium/generated

.PHONY: gen
gen:
	mkdir -p $(GEN)
	uv run gen-pydantic $(SCHEMA) > $(GEN)/model.py
	uv run gen-shacl --non-closed $(SCHEMA) > $(GEN)/shapes.ttl
	uv run gen-owl $(SCHEMA) > $(GEN)/ontology.ttl
	uv run gen-json-schema $(SCHEMA) > $(GEN)/schema.json
```

Replace with:
```makefile
SCHEMA=src/indicium/schema/indicium.yaml
GEN=src/indicium/generated
ASSETS=docs/schema-assets

.PHONY: gen schema-assets

gen:
	mkdir -p $(GEN)
	uv run gen-pydantic $(SCHEMA) > $(GEN)/model.py
	uv run gen-shacl --non-closed $(SCHEMA) > $(GEN)/shapes.ttl
	uv run gen-owl $(SCHEMA) > $(GEN)/ontology.ttl
	uv run gen-json-schema $(SCHEMA) > $(GEN)/schema.json

schema-assets: gen
	mkdir -p $(ASSETS)
	cp $(GEN)/schema.json $(ASSETS)/indicium.schema.json
	cp $(GEN)/ontology.ttl $(ASSETS)/indicium.owl.ttl
	cp $(GEN)/shapes.ttl $(ASSETS)/indicium.shapes.ttl
```

- [ ] **Step 2: Run schema-assets and verify**

```bash
cd ~/git/indicium && uv sync --extra codegen && make schema-assets
ls docs/schema-assets/
```

Expected: `indicium.owl.ttl  indicium.schema.json  indicium.shapes.ttl`

- [ ] **Step 3: Commit**

```bash
cd ~/git/indicium
git add Makefile docs/schema-assets/
git commit -m "build: schema-assets Makefile target + generated artefacts"
```

---

## Task 13: GitHub Actions — docs workflow

**Files:**
- Create: `.github/workflows/docs.yml`

- [ ] **Step 1: Create directory and write workflow**

```bash
mkdir -p ~/git/indicium/.github/workflows
```

```yaml
# .github/workflows/docs.yml
name: Deploy docs

on:
  push:
    branches: [main]

permissions:
  contents: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Install dependencies
        run: uv sync --extra codegen --extra docs

      - name: Regenerate schema artefacts
        run: uv run make gen

      - name: Copy schema artefacts to docs
        run: make schema-assets

      - name: Deploy site
        run: uv run mkdocs gh-deploy --force
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add .github/workflows/docs.yml
git commit -m "ci: deploy docs to GitHub Pages on push to main"
```

---

## Task 14: GitHub Actions — release workflow

**Files:**
- Create: `.github/workflows/release.yml`

- [ ] **Step 1: Write the release workflow**

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - "v*"

permissions:
  contents: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: astral-sh/setup-uv@v3
        with:
          version: "latest"

      - name: Install dependencies
        run: uv sync --extra codegen --extra docs

      - name: Regenerate schema artefacts
        run: uv run make gen

      - name: Copy schema artefacts
        run: make schema-assets

      - name: Build wheel and sdist
        run: uv build

      - name: Extract changelog for this release
        id: changelog
        run: |
          # Extract the section for this tag from docs/changelog.md
          TAG="${GITHUB_REF_NAME#v}"
          BODY=$(awk "/^## Indicium ${TAG}/{found=1; next} found && /^## /{exit} found{print}" docs/changelog.md)
          echo "body<<EOF" >> $GITHUB_OUTPUT
          echo "$BODY" >> $GITHUB_OUTPUT
          echo "EOF" >> $GITHUB_OUTPUT

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.changelog.outputs.body }}
          files: |
            dist/*
            docs/schema-assets/indicium.schema.json
            docs/schema-assets/indicium.owl.ttl
            docs/schema-assets/indicium.shapes.ttl

      # PyPI publish — uncomment when PYPI_TOKEN secret is configured:
      # - name: Publish to PyPI
      #   run: uv publish
      #   env:
      #     UV_PUBLISH_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

- [ ] **Step 2: Commit**

```bash
cd ~/git/indicium
git add .github/workflows/release.yml
git commit -m "ci: release workflow — GitHub Release + artefacts on tag push"
```

---

## Task 15: Local build verification

- [ ] **Step 1: Build and serve the site locally**

```bash
cd ~/git/indicium
uv sync --extra codegen --extra docs
make schema-assets
uv run mkdocs build --strict
uv run mkdocs serve
```

Expected: `mkdocs build --strict` exits 0. `mkdocs serve` starts at `http://127.0.0.1:8000`.

Open the local site and verify:
- Home page renders with the CNRS navy header and yellow accents
- All nav links resolve (no 404s)
- Schema artefact links in the home page point to existing files
- API reference renders docstrings for all adapters

- [ ] **Step 2: Fix any warnings from `--strict` mode before continuing**

`mkdocs build --strict` treats warnings as errors. Common issues:
- Missing pages referenced in `nav:` → create the file
- Broken `:::` mkdocstrings directives → check module paths in `src/`

---

## Task 16: Tag v1.0.0 and push

- [ ] **Step 1: Confirm all tests pass**

```bash
cd ~/git/indicium && uv run pytest -v
```

Expected: all tests pass.

- [ ] **Step 2: Create and push the tag**

```bash
cd ~/git/indicium
git tag v1.0.0
git push origin main
git push origin v1.0.0
```

The `docs.yml` workflow will deploy the site to GitHub Pages.
The `release.yml` workflow will create the GitHub Release and attach artefacts.

- [ ] **Step 3: Verify GitHub Actions**

Go to `https://github.com/HolobiomicsLab/indicium/actions` and confirm both workflows succeed.

- [ ] **Step 4: Verify the deployed site**

Open `https://holobiomicslab.github.io/indicium` and confirm the site is live.

---

## Out of scope (deferred)

- `indicium-spec.org` DNS / domain registration
- `w3id.org/indicium` namespace registration
- KGmemory adapter documentation
- PyPI publish (`uv publish` — token setup required; step is commented out in `release.yml`)
- Making the GitHub repo public
- Scriptorium adapter
