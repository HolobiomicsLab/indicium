# Source

A `Source` is a DoCO/FaBiO-typed document or artefact that an `Evidence` record
points to.

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `identifier` | yes | `dct:identifier` | DOI, URL, or local path |
| `title` | no | `dct:title` | Human-readable title |
| `authors` | no | — | List of author names |
| `license_id` | no | — | SPDX license identifier |

## Example

```python
source = {
    "identifier": "10.1234/test",
    "title": "Inhibition study of compound A",
    "authors": ["Smith J", "Doe A"],
}
```
