# Indicium

A small, standalone, versioned **standard for a typed scientific claim bound to
the evidence that grounds it.** One LinkML source of truth generates pydantic
models, JSON-Schema, SHACL shapes, and OWL. It reuses community ontologies
rather than reinventing them:

| Axis | Standard |
|------|----------|
| Evidence type | **ECO** (Evidence & Conclusion Ontology) |
| Claim ↔ citation relation | **CiTO** |
| Source / document type | **DoCO** + **IAO** |
| Article type | **FaBiO** |
| Assertion + evidence structure | **SEPIO** |
| Provenance | **PROV-O** |
| Claim structure | **Bucur et al.** 5-slot SuperPattern (K-CAP 2021) |

The one thing Indicium mints is the **binding**: a claim → typed evidence → a
source, provenance-stamped. That binding is the load-bearing contribution —
the claim structure is borrowed from Bucur; the value Indicium standardizes is
the *typed grounding of claims in evidence.*

## The name

*Indicium* (Latin) is "a sign or mark that points to the truth" — in law, the
evidentiary indication. The package is named for what it standardizes: every
claim carries its **indicia**, the traces that justify believing it.

- **`indicium`** (singular) = the standard / this package.
- **indicia** (plural) = the body of evidence attached to a claim (used as the
  term for the produced collection in consumer APIs).

## Role in the ecosystem

Indicium is a *vocabulary/standard*, not a tool and not a store:

- **ASTRA** — the analysis/workflow an agent performed.
- **Indicium** — the evidence-grounded claims that analysis rests on. *(this)*
- **KGmemory** — where claims are stored and reasoned over.
- **ASB / Perspicacité / Scriptorium** — the tools that mint and consume claims.

Every tool imports Indicium, so a claim minted by any of them is structurally
identical and mergeable — and never travels without its evidence trace.

## Install

Requires Python 3.11 or newer. The command below is for the public release;
until 2.0.0 is published, install a wheel supplied by the maintainers.

```bash
pip install indicium-standard      # distribution name
python -c "import indicium"        # import name
```

> **The distribution is `indicium-standard`; the import package is `indicium`.**
> The PyPI name `indicium` belongs to an unrelated, abandoned key-value-store
> package that also ships a top-level `indicium` module. Installing both into the
> same environment will clobber the import. Always depend on `indicium-standard`.

## Using the vocabulary

Import the namespace bases; never copy the IRI string into your own code. A
hardcoded base keeps pointing at the old namespace when the standard moves, and
the SHACL shapes then match nothing — every graph validates as `conforms=True`
while no constraint is actually checked.

```python
from indicium import ASB_BASE, asb_term, validate_graph

asb_term("Claim")   # 'https://w3id.org/asb#Claim'
```

```python
ASB = "https://w3id.org/asb#"   # don't — silently dead after a move
```

## Development

```bash
uv sync
make gen          # regenerate model.py / shapes.ttl / ontology.ttl / schema.json
make context      # regenerate the packaged JSON-LD context (also linked by docs)
make docs-changelog  # refresh docs/changelog.md from CHANGELOG.md
uv run pytest -v  # includes claim-conformance tests
make lint
uv run mkdocs build --strict
```

Namespace bases are stable identifiers. Their registration and the vocabulary
site are prepared separately from the Python release; they do not provide an
instance store. See [URI scheme](docs/uri-scheme.md) and the
[SEPIO compatibility notes](docs/sepio-assertion.md) before exporting RDF.
