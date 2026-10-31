# ASB task card adapter

Projects an Indicium `Claim` dict onto an `EvidenceSnippet` dict, the evidence
structure embedded in the task cards that AgenticScienceBuilder (ASB) produces.
The target structure is the `EvidenceSnippet` class of the ASB task card schema,
`asb_schema/asb_card.yaml` in the [asb-schema](https://pypi.org/project/asb-schema/)
package (`asb-schema>=0.4.0`). The module keeps its earlier name,
`indicium.adapters.scitask`, so that existing imports keep working.

## Function

```python
from indicium.adapters.scitask import claim_to_evidence_snippet

snip = claim_to_evidence_snippet(claim)
# or with an explicit source path:
snip = claim_to_evidence_snippet(claim, source_path="results/fig1.png")
```

## Mapping

| `EvidenceSnippet` field | Indicium source |
|-------------------------|-----------------|
| `snippet_id` | `claim["id"]` |
| `source_path` | First `evidence[].artifact`, then `"doi:<doi>"`, then `""` |
| `reason` | `"{subject} [{qualifier}] {relation} {object} (context: {context})"` |
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
#   "reason": "compound A [inhibits] inhibits growth of cell line B (context: in vitro)",
#   "text": "Compound A inhibited cell line B by 80%."
# }
```
