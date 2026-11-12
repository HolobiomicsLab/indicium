import json

import rdflib

from indicium.adapters.kgmemory import MEM_NS, claim_jsonld
from indicium.iri_bindings import ASB_BASE
from indicium.validate import validate_graph


def test_canonical_mem_namespace():
    assert MEM_NS == "http://kgmemory.org/ns#"


def test_claim_aligns_to_semantic_memory_only():
    doc = claim_jsonld({"id": "c001", "context": "x", "subject": "s",
                        "qualifier": "causes", "relation": "r", "object": "o"})
    types = doc["@type"]
    assert "http://kgmemory.org/ns#SemanticMemory" in types
    # disjointness-safe: never also Episodic/Procedural
    assert not any(t.endswith(("EpisodicMemory", "ProceduralMemory")) for t in types)


def test_claim_projection_is_checked_by_claim_shape():
    doc = claim_jsonld({"id": "c001", "context": "x", "subject": "s",
                        "qualifier": "causes", "relation": "r", "object": "o"})

    graph = rdflib.Graph().parse(data=json.dumps(doc), format="json-ld")
    claim = rdflib.URIRef("urn:indicium:claim:c001")
    assert (claim, rdflib.RDF.type, rdflib.URIRef(f"{ASB_BASE}Claim")) in graph
    assert (claim, rdflib.RDF.type,
            rdflib.URIRef(f"{MEM_NS}SemanticMemory")) in graph
    conforms, report = validate_graph(graph)
    assert conforms is True, report

    graph.remove((claim, rdflib.URIRef(f"{ASB_BASE}object"), None))
    conforms, report = validate_graph(graph)
    assert conforms is False
    assert "asb:object" in report


def test_no_kgmemory_ontology_is_shipped():
    # We only reference the IRI; we must not vendor mem.ttl.
    import indicium, pathlib
    root = pathlib.Path(indicium.__file__).parent
    assert not list(root.rglob("mem.ttl"))
