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
