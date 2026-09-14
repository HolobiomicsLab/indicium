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
pip install indicium-standard
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
