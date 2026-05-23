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

## The claim dict format

Indicium adapters consume a **claim dict** — a plain Python dictionary with the following keys:

| Key | Required | Type | Notes |
|-----|----------|------|-------|
| `id` | yes | `str` | Stable identifier (e.g. `"c001"`, a UUID, or a URN) |
| `context` | yes | `str` | Experimental or conceptual setting |
| `subject` | yes | `str` | Entity the claim is about |
| `qualifier` | yes | `str` | One of the 20 Bucur SuperPattern terms |
| `relation` | yes | `str` | Free-text elaboration of the relation |
| `object` | yes | `str` | Target entity |
| `claim_type` | no | `str` | `"explicit"` or `"implicit"` |
| `source_excerpt` | no | `str` | Verbatim text from the source |
| `evidence` | no | `list[dict]` | Each item may carry `doi`, `artifact`, `quote`, `evidence_type` |

The formal `Claim` Pydantic model (`indicium.generated.model.Claim`) validates the same required slots and the `qualifier` enum, and produces a compatible dict via `.model_dump()`. The `evidence` list is an adapter-layer convenience; in the RDF/SHACL model, evidence is a separate `Evidence` class linked to a claim via `for_claim`.

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
#  'reason': 'compound A [inhibits] inhibits growth of cell line B (context: in vitro)',
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
