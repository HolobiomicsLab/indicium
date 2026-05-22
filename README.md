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

## Quickstart

```bash
uv sync
make gen          # regenerate model.py / shapes.ttl / ontology.ttl / schema.json
uv run pytest -v  # includes the conformance suite (parity vs Scriptorium SHACL)
```
