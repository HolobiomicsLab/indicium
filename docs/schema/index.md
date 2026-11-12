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

## What validation enforces

`validate_graph` and the SHACL shapes require the claim slots `context`, `subject`,
`relation` and `object`, and at least one of `qualifier` or `domain_qualifier`. They
also apply the required properties of the other classes, for example a
`SoftwareEntity` needs an identifier. Evidence is a separate record that points to
its claim through `supports_claim` or `for_claim`. In the model every document
collection and both of those links are optional, so a claim without evidence is
valid. A producer that promises evidence for every claim has to check it itself.
