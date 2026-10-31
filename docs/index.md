<div class="hero" markdown>

![Indicium mark](assets/brand/indicium-mark.svg#only-light){ width="112" }
![Indicium mark](assets/brand/indicium-mark-dark.svg#only-dark){ width="112" }

# Indicium

<p class="tagline">A standard for typed scientific claims bound to their evidence.</p>

[Quickstart](quickstart.md){ .md-button .md-button--primary }
[Schema](schema/index.md){ .md-button }
[URI scheme](uri-scheme.md){ .md-button }

</div>

Indicium standardizes one thing: the **binding** of a scientific claim to typed
evidence and to the source that evidence points to, with provenance. A claim minted
by any tool that imports Indicium has the same structure as one minted by any other,
merges with it, and never travels without its evidence trace.

<div class="feature-grid" markdown>

<div class="feature-card" markdown>
### One source of truth
One LinkML schema generates the pydantic models, JSON Schema, SHACL shapes, the
OWL ontology and the JSON-LD context. The supplemental SHACL shapes (constraints
LinkML cannot express) are kept by hand beside it.
</div>

<div class="feature-card" markdown>
### Reused ontologies
Evidence types come from ECO, citation relations from CiTO, document types from DoCO,
IAO and FaBiO, the assertion structure from SEPIO, provenance from PROV-O.
</div>

<div class="feature-card" markdown>
### SHACL validation
`validate_graph` runs the SHACL shapes over any RDF graph and returns the report.
Domain packages add their own shapes through the same call.
</div>

</div>

## Reuse axes

| Axis | Standard |
|------|----------|
| Evidence type | **ECO** (Evidence & Conclusion Ontology) |
| Claim to citation relation | **CiTO** |
| Source and document type | **DoCO** and **IAO** |
| Article type | **FaBiO** |
| Assertion and evidence structure | **SEPIO** |
| Provenance | **PROV-O** |
| Claim structure | **Bucur et al.** 5-slot SuperPattern (K-CAP 2021) |

## What Indicium defines

| Component | What it is |
|-----------|-----------|
| [`Claim`](schema/claim.md) | The 5-slot Bucur SuperPattern (context, subject, qualifier, relation, object) with ECO-typed evidence |
| [`Evidence`](schema/evidence.md) | A typed evidence record grounding a claim |
| [`Source`](schema/source.md) | A DoCO/FaBiO-typed document or artefact that an evidence record points to |
| [`CitationLink`](schema/evidence.md#citationlink) | A CiTO-typed link from a source to a claim |
| `ClaimLink` | A CiTO-typed relation between two claims (supports, disputes, refines, ...) |
| `IndiciumDocument` | The container that serialises a set of claims, evidence and sources |

## Install

```bash
pip install indicium-standard
```

The 2.0.0 upload to PyPI is pending. Until `pip install indicium-standard` finds it,
install from the repository:

```bash
pip install "git+https://github.com/HolobiomicsLab/indicium"
```

!!! warning "The distribution is `indicium-standard`; the import package is `indicium`"
    The PyPI name `indicium` belongs to an unrelated, abandoned key-value-store package
    that also ships a top-level `indicium` module. Installing both into one environment
    clobbers the import. Always depend on `indicium-standard`.

## Quickstart

```python
import rdflib
from indicium import ASB_BASE, validate_graph

claim = f"""
@prefix asb: <{ASB_BASE}> .
<urn:claim:1> a asb:Claim ;
    asb:context "in vitro" ;
    asb:subject "compound A" ;
    asb:qualifier "inhibits" ;
    asb:relation "inhibits growth of" ;
    asb:object "cell line B" .
"""

conforms, report = validate_graph(rdflib.Graph().parse(data=claim, format="turtle"))
print(conforms)  # True
```

The [Quickstart](quickstart.md) page continues with the typed model and the adapters.

## Schema artefacts

Generated from the LinkML source, `src/indicium/schema/indicium.yaml`:

| Artefact | File |
|----------|------|
| JSON Schema | [`indicium.schema.json`](schema-assets/indicium.schema.json) |
| OWL ontology | [`indicium.owl.ttl`](schema-assets/indicium.owl.ttl) |
| SHACL shapes | [`indicium.shapes.ttl`](schema-assets/indicium.shapes.ttl) |
| JSON-LD context | [`context.jsonld`](context.jsonld) |

## The name

*Indicium* (Latin) is "a sign or mark that points to the truth"; in law, the
evidentiary indication. Every claim carries its **indicia**, the traces that justify
believing it.
