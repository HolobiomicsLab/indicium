# ASTRA Adapter

Projects an Indicium claim onto an [ASTRA](https://astra-spec.org) `Insight` dict.

!!! note "Use the typed bridge"
    `indicium.astra_bridge.claim_to_insight(claim, evidence_doi=...)` takes a typed
    `Claim` and needs the `astra` extra (`pip install "indicium-standard[astra]"`).
    The dict-based `indicium.adapters.astra.claim_to_insight` described below is
    deprecated and emits a `DeprecationWarning`. The bridge also reads ASTRA files
    back into claims: `insight_to_claim`, `load_astra_findings`,
    `load_astra_prior_insights`.

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
