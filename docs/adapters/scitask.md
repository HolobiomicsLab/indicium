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
