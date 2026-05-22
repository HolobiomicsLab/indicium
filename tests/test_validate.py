import rdflib
from indicium.validate import validate_graph

VALID = """
@prefix asb: <https://asb.holobiomics.org/ns/asb#> .
<urn:claim:1> a asb:Claim ;
    asb:context "c" ; asb:subject "s" ; asb:qualifier "causes" ;
    asb:relation "r" ; asb:object "o" .
"""

INVALID = """
@prefix asb: <https://asb.holobiomics.org/ns/asb#> .
<urn:claim:2> a asb:Claim ;
    asb:context "c" .
"""


def test_valid_claim_conforms():
    g = rdflib.Graph(); g.parse(data=VALID, format="turtle")
    conforms, _ = validate_graph(g)
    assert conforms is True


def test_invalid_claim_fails():
    g = rdflib.Graph(); g.parse(data=INVALID, format="turtle")
    conforms, report = validate_graph(g)
    assert conforms is False
    assert "subject" in report or "qualifier" in report
