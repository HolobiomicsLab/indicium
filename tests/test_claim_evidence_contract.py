"""The documented evidence contract: evidence is optional, claim slots are not."""
import rdflib

from indicium import ASB_BASE, validate_graph
from indicium.generated.model import Claim, IndiciumDocument

PREFIX = f"@prefix asb: <{ASB_BASE}> .\n"


def _validate(body: str):
    graph = rdflib.Graph().parse(data=PREFIX + body, format="turtle")
    return validate_graph(graph)


def test_claim_without_evidence_conforms():
    conforms, report = _validate(
        '<urn:claim:c1> a asb:Claim ; asb:context "in vitro" ; asb:subject "A" ;'
        ' asb:qualifier "inhibits" ; asb:relation "inhibits growth of" ;'
        ' asb:object "B" .'
    )
    assert conforms, report


def test_claim_without_qualifier_does_not_conform():
    conforms, _ = _validate(
        '<urn:claim:c2> a asb:Claim ; asb:context "in vitro" ; asb:subject "A" ;'
        ' asb:relation "inhibits growth of" ; asb:object "B" .'
    )
    assert not conforms


def test_model_leaves_evidence_collections_optional():
    claim = Claim(
        id="urn:claim:c3",
        context="in vitro",
        subject="A",
        qualifier="inhibits",
        relation="inhibits growth of",
        object="B",
    )
    document = IndiciumDocument(claims={claim.id: claim})
    assert document.evidences is None
    assert document.sources is None
