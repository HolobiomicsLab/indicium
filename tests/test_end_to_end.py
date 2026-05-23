import rdflib
import indicium
from indicium import claim_to_evidence_snippet


def test_public_api_round_trip():
    claim = {"id": "c1", "context": "in vitro", "subject": "A",
             "qualifier": "inhibits", "relation": "inhibits", "object": "B",
             "evidence": [{"doi": "10.1/x", "quote": "A inhibits B"}]}

    # ASTRA projection
    insight = indicium.claim_to_insight(claim)
    assert insight["evidence"][0]["doi"] == "10.1/x"

    # KGmemory-ready JSON-LD
    doc = indicium.claim_jsonld(claim)
    assert indicium.MEM_NS + "SemanticMemory" in doc["@type"]

    # SHACL validation of the RDF form
    g = rdflib.Graph()
    g.parse(data="""
@prefix asb: <https://asb.holobiomics.org/ns/asb#> .
<urn:c1> a asb:Claim ; asb:context "in vitro" ; asb:subject "A" ;
    asb:qualifier "inhibits" ; asb:relation "inhibits" ; asb:object "B" .
""", format="turtle")
    conforms, _ = indicium.validate_graph(g)
    assert conforms is True

    # SciTask adapter
    snip = claim_to_evidence_snippet(claim)
    assert snip["snippet_id"] == claim["id"]
    assert isinstance(snip["text"], str)
