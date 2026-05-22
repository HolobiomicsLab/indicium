from indicium.adapters.kgmemory import MEM_NS, claim_jsonld


def test_canonical_mem_namespace():
    assert MEM_NS == "http://kgmemory.org/ns#"


def test_claim_aligns_to_semantic_memory_only():
    doc = claim_jsonld({"id": "c001", "context": "x", "subject": "s",
                        "qualifier": "causes", "relation": "r", "object": "o"})
    types = doc["@type"]
    assert "http://kgmemory.org/ns#SemanticMemory" in types
    # disjointness-safe: never also Episodic/Procedural
    assert not any(t.endswith(("EpisodicMemory", "ProceduralMemory")) for t in types)


def test_no_kgmemory_ontology_is_shipped():
    # We only reference the IRI; we must not vendor mem.ttl.
    import indicium, pathlib
    root = pathlib.Path(indicium.__file__).parent
    assert not list(root.rglob("mem.ttl"))
