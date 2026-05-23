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
