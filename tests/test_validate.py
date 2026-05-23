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


def test_validate_graph_extra_shapes_none_is_backward_compat():
    """validate_graph(data, extra_shapes=None) must behave identically to before."""
    g = rdflib.Graph()
    g.parse(data=VALID, format="turtle")
    conforms, report = validate_graph(g, extra_shapes=None)
    assert conforms is True
    assert isinstance(report, str)


def test_validate_graph_extra_shapes_merged():
    """validate_graph() must merge extra_shapes into the shapes graph before validation."""
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    # A trivial NodeShape with no constraints — must not break conformance
    extra = rdflib.Graph()
    shape_uri = rdflib.URIRef("urn:test:TrivialShape")
    extra.add((shape_uri, rdflib.RDF.type, SH.NodeShape))

    g = rdflib.Graph()
    g.parse(data=VALID, format="turtle")
    conforms, report = validate_graph(g, extra_shapes=extra)
    assert conforms is True


def test_validate_graph_warning_severity_does_not_fail_conformance():
    """sh:Warning violations must not set conforms=False (allow_warnings=True required)."""
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
    ASB = rdflib.Namespace("https://asb.holobiomics.org/ns/asb#")

    # Build a shape with sh:Warning severity targeting a known predicate
    extra = rdflib.Graph()
    shape = rdflib.URIRef("urn:test:WarnShape")
    prop = rdflib.BNode()
    extra.add((shape, rdflib.RDF.type, SH.NodeShape))
    extra.add((shape, SH.targetClass, ASB.Claim))
    extra.add((shape, SH.property, prop))
    extra.add((prop, SH.path, ASB.subject))
    extra.add((prop, SH.minLength, rdflib.Literal(9999)))   # will always fire
    extra.add((prop, SH.severity, SH.Warning))

    g = rdflib.Graph()
    g.parse(data="""
        @prefix asb: <https://asb.holobiomics.org/ns/asb#> .
        <urn:claim:w1> a asb:Claim ;
            asb:context "c" ; asb:subject "s" ; asb:qualifier "causes" ;
            asb:relation "r" ; asb:object "o" .
    """, format="turtle")

    conforms, report = validate_graph(g, extra_shapes=extra)
    assert conforms is True, (
        "sh:Warning violations must not set conforms=False — "
        f"validate_graph() likely missing allow_warnings=True. Report: {report}"
    )
