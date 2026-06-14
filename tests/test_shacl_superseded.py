"""SHACL constraint: superseded_by must be set when claim_status=superseded."""
from __future__ import annotations

import rdflib
import pytest
from indicium.validate import validate_graph

# Use the same namespace/class as the generated shapes
ASB = rdflib.Namespace("https://holobiomicslab.eu/ns/asb#")
INDICIUM = rdflib.Namespace("https://w3id.org/indicium/")
DCT = rdflib.Namespace("http://purl.org/dc/terms/")

def _make_full_claim(claim_iri: str, status: str, superseded_by: str | None = None) -> rdflib.Graph:
    """Make a fully-valid claim triple set, optionally with superseded_by.

    The five Bucur SuperPattern slots (context, subject, qualifier, relation, object)
    are in the asb: namespace — matching the sh:path values in generated shapes.ttl.
    claim_status and superseded_by are in the indicium: namespace.
    """
    g = rdflib.Graph()
    c = rdflib.URIRef(claim_iri)
    g.add((c, rdflib.RDF.type, ASB.Claim))
    # asb: namespace for the five SuperPattern slots (matches sh:path in shapes.ttl)
    g.add((c, ASB.context, rdflib.Literal("in vitro")))
    g.add((c, ASB.subject, rdflib.Literal("compound X")))
    g.add((c, ASB.qualifier, rdflib.Literal("inhibits")))
    g.add((c, ASB.relation, rdflib.Literal("inhibits growth of")))
    g.add((c, ASB.object, rdflib.Literal("E. coli")))
    # indicium: namespace for status fields
    g.add((c, INDICIUM.claim_status, rdflib.Literal(status)))
    if superseded_by:
        g.add((c, INDICIUM.superseded_by, rdflib.URIRef(superseded_by)))
    return g


def test_superseded_without_pointer_fails_shacl():
    """claim_status=superseded but no superseded_by → SHACL violation."""
    g = _make_full_claim(
        "https://w3id.org/indicium/claim/c1",
        status="superseded",
        superseded_by=None,
    )
    conforms, report = validate_graph(g)
    assert not conforms, (
        "Expected SHACL violation for superseded claim without superseded_by pointer, "
        f"but validate_graph returned conforms=True.\nReport:\n{report}"
    )


def test_superseded_with_pointer_passes_shacl():
    """claim_status=superseded with superseded_by set → valid."""
    g = _make_full_claim(
        "https://w3id.org/indicium/claim/c1",
        status="superseded",
        superseded_by="https://w3id.org/indicium/claim/c2",
    )
    conforms, report = validate_graph(g)
    assert conforms, (
        f"Superseded claim with superseded_by should pass SHACL.\nReport:\n{report}"
    )


def test_non_superseded_without_pointer_passes_shacl():
    """claim_status=verified with no superseded_by → valid (rule only applies to 'superseded')."""
    g = _make_full_claim(
        "https://w3id.org/indicium/claim/c2",
        status="verified",
        superseded_by=None,
    )
    conforms, report = validate_graph(g)
    assert conforms, (
        f"Non-superseded claim without superseded_by must pass SHACL.\nReport:\n{report}"
    )
