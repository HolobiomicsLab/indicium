# Evidence & CitationLink

## Evidence

An `Evidence` record grounds a `Claim` in a typed source.

| Slot | Required | Ontology | Description |
|------|----------|----------|-------------|
| `evidence_type` | no | ECO | Type of evidence (see table below) |
| `source_type` | no | DoCO/IAO | Type of source document or artefact |
| `quote` | no | — | Verbatim passage from the source |
| `confidence` | no | — | Float 0–1 |
| `of_source` | no | — | The `Source` this evidence points to |
| `for_claim` | no | — | The `Claim` this evidence grounds |
| `supports_claim` | no | SEPIO | Semantic alias of `for_claim`; the fields remain distinct |

### EvidenceType (ECO-mapped)

| Value | ECO IRI |
|-------|---------|
| `data` | ECO:0000006 |
| `citation` | ECO:0000033 |
| `knowledge` | ECO:0000302 |
| `inference` | ECO:0000361 |
| `speculation` | ECO:0000034 |

### SourceType (DoCO/IAO-mapped)

| Value | IRI |
|-------|-----|
| `text` | IAO:0000311 |
| `figure` | doco:Figure |
| `table` | doco:Table |
| `image` | IAO:0000536 |
| `code` | fabio:ComputerProgram |
| `data` | dcat:Dataset |

## CitationLink

A CiTO-typed link from a source to a claim.

| Slot | Ontology | Description |
|------|----------|-------------|
| `link_type` | CiTO | Relation type (see table below) |

### LinkType (CiTO-mapped)

| Value | CiTO IRI |
|-------|---------|
| `supports` | cito:supports |
| `disputes` | cito:disputes |
| `qualifies` | cito:qualifies |
| `citesForInformation` | cito:citesForInformation |
| `contradicts` | cito:contradicts |
| `refines` | cito:refines |
| `extends` | cito:extends |
| `agreesWith` | cito:agreesWith |
| `disagreesWith` | cito:disagreesWith |
| `updates` | cito:updates |
| `corrects` | cito:corrects |
| `usesDataFrom` | cito:usesDataFrom |
| `usesMethodIn` | cito:usesMethodIn |
