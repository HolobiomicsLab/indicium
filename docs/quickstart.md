# Quickstart

Every Python block on this page runs, in order, in the test suite
(`tests/test_docs_examples.py`).

## Install

```bash
pip install indicium-standard
# or, in a uv project:
uv add indicium-standard
```

Optional extras:

```bash
pip install "indicium-standard[astra]"     # ASTRA bridge (PyYAML)
pip install "indicium-standard[codegen]"   # regenerate the artefacts from the LinkML source
```

The import package is `indicium`. Never install the unrelated PyPI package named
`indicium` next to it: both ship a top-level `indicium` module.

## Validate a claim

A claim is an RDF node of type `asb:Claim` with the five SuperPattern slots. Build
the prefix from `ASB_BASE` rather than typing the IRI:

```python
import rdflib
from indicium import ASB_BASE, validate_graph

claim_ttl = f"""
@prefix asb: <{ASB_BASE}> .
<urn:claim:c001> a asb:Claim ;
    asb:context "in vitro" ;
    asb:subject "compound A" ;
    asb:qualifier "inhibits" ;
    asb:relation "inhibits growth of" ;
    asb:object "cell line B" .
"""

conforms, report = validate_graph(rdflib.Graph().parse(data=claim_ttl, format="turtle"))
print(conforms)  # True
```

A claim without its subject, relation and object does not conform, and the report
names each missing slot:

```python
incomplete_ttl = f"""
@prefix asb: <{ASB_BASE}> .
<urn:claim:c002> a asb:Claim ; asb:context "in vitro" ; asb:qualifier "inhibits" .
"""

conforms, report = validate_graph(rdflib.Graph().parse(data=incomplete_ttl, format="turtle"))
print(conforms)  # False
print("asb:subject" in report, "asb:relation" in report, "asb:object" in report)  # True True True
```

`validate_graph(data, extra_shapes=...)` merges additional SHACL shapes, for example
those of a domain adapter, into the base shapes before validating.

## The typed model

The pydantic classes are generated from the same LinkML source and re-exported from
`indicium`:

```python
from indicium import Claim, SuperPatternQualifier

claim = Claim(
    id="c001",
    context="in vitro",
    subject="compound A",
    qualifier="inhibits",
    relation="inhibits growth of",
    object="cell line B",
)
print(claim.qualifier is SuperPatternQualifier.inhibits)  # True
```

`qualifier` takes one of the 20 Bucur SuperPattern terms. A domain package may use
`domain_qualifier` instead; the SHACL shapes require at least one of the two.

## The claim dict

The adapters take a plain dictionary:

| Key | Required | Type | Notes |
|-----|----------|------|-------|
| `id` | yes | `str` | Stable identifier (e.g. `"c001"`, a UUID, or a URN) |
| `context` | yes | `str` | Experimental or conceptual setting |
| `subject` | yes | `str` | Entity the claim is about |
| `qualifier` | yes, for the adapters below | `str` | One of the 20 Bucur SuperPattern terms |
| `relation` | yes | `str` | Free-text elaboration of the relation |
| `object` | yes | `str` | Target entity |
| `claim_type` | no | `str` | `"explicit"` or `"implicit"` |
| `source_excerpt` | no | `str` | Verbatim text from the source |
| `evidence` | no | `list[dict]` | Each item may carry `doi`, `artifact`, `quote`, `evidence_type` |

`Claim(**{k: v for k, v in claim_dict.items() if k != "evidence"})` validates the same
slots and the qualifier enum (the model rejects the `evidence` key, which belongs to the
adapter layer), and `claim.model_dump(mode="json", exclude_none=True)` returns a dict
the adapters accept. In the RDF model, evidence is a separate `Evidence` node linked
to its claim.

## Project a claim onto other formats

```python
from indicium import claim_to_evidence_snippet, claim_jsonld

claim_dict = {
    "id": "c001",
    "context": "in vitro",
    "subject": "compound A",
    "qualifier": "inhibits",
    "relation": "inhibits growth of",
    "object": "cell line B",
    "source_excerpt": "Compound A inhibited cell line B by 80%.",
    "evidence": [{"doi": "10.1234/test", "quote": "Compound A inhibited cell line B by 80%."}],
}

# EvidenceSnippet, as embedded in ASB task cards
snippet = claim_to_evidence_snippet(claim_dict)
print(snippet["source_path"])  # doi:10.1234/test
print(snippet["reason"])       # compound A [inhibits] inhibits growth of cell line B (context: in vitro)

# JSON-LD node for KGmemory
node = claim_jsonld(claim_dict)
print(node["@id"])  # urn:indicium:claim:c001
print(node["@type"])  # ['https://w3id.org/asb#Claim', 'http://kgmemory.org/ns#SemanticMemory']
```

The ASTRA bridge works on the typed model and needs the `astra` extra:

```python
from indicium.astra_bridge import claim_to_insight

insight = claim_to_insight(claim, evidence_doi="10.1234/test")
print(insight["claim"])     # compound A inhibits inhibits growth of cell line B
print(insight["evidence"])  # [{'id': 'e1', 'doi': '10.1234/test'}]
```

`indicium.claim_to_insight`, the dict-based version, is deprecated and emits a
`DeprecationWarning`.

## Validate a file

```python
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "my_claims.ttl"
    path.write_text(claim_ttl)

    g = rdflib.Graph()
    g.parse(path, format="turtle")
    conforms, report = validate_graph(g)
    if not conforms:
        print(report)
```

## Regenerate the schema artefacts

From a checkout of the repository:

```bash
uv sync --frozen --extra codegen
make gen             # src/indicium/generated/: model.py, shapes.ttl, ontology.ttl, schema.json
make context         # src/indicium/schema/context.jsonld, from the LinkML URI bindings
make schema-assets   # make gen and make context, then copy the artefacts and the changelog into docs/
```

The Turtle output is canonicalised, so a second run is byte-identical to the first.
