# Claim

A scientific claim expressed using the
[Bucur et al. (K-CAP 2021)](https://dl.acm.org/doi/10.1145/3460210.3493561)
5-slot SuperPattern.

## Slots

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `id` | yes | `dct:identifier` | Stable claim identifier (string, UUID, or URN). Note: LinkML's `identifier: true` generates `sh:maxCount 1` in SHACL but not `sh:minCount 1`; `id` is enforced as required by the Pydantic model and JSON Schema instead. |
| `context` | yes | `asb:context` | The experimental or conceptual setting |
| `subject` | yes | `asb:subject` | What the claim is about |
| `qualifier` | yes | `asb:qualifier` | Directional relation from the 20-term vocabulary |
| `relation` | yes | `asb:relation` | Free-text relation elaboration |
| `object` | yes | `asb:object` | The target entity |
| `claim_type` | no | — | `explicit` or `implicit` |
| `source_excerpt` | no | — | Verbatim text from the source |

## SuperPatternQualifier vocabulary

20 terms from Bucur et al.: `causes`, `prevents`, `inhibits`, `activates`,
`increases`, `decreases`, `correlates_with`, `is_associated_with`, `predicts`,
`interacts_with`, `produces`, `requires`, `enables`, `treats`, `enhances`,
`reduces`, `has_property`, `is_part_of`, `is_a`, `consistent_with`.

## Example

```python
claim = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "claim_type": "explicit",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
}
```
