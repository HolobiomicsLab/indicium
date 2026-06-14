"""Domain-qualifier extension (resolves indicium#1, Reading 1).

The core ``asb:qualifier`` slot stays a CLOSED Bucur SuperPattern enum, but is
no longer required on its own. A parallel OPEN slot ``asb:domainQualifier``
(snake_case pattern) carries domain-adapter qualifiers such as
``aligned_with``. A Claim must carry at least one of the two.
"""
from __future__ import annotations

import rdflib
from indicium.validate import validate_graph

ASB = rdflib.Namespace("https://holobiomicslab.eu/ns/asb#")


def _claim(qualifier: str | None = None, domain_qualifier: str | None = None) -> rdflib.Graph:
    """Build a 4-slot claim, optionally adding qualifier and/or domain_qualifier."""
    g = rdflib.Graph()
    c = rdflib.URIRef("urn:claim:dq")
    g.add((c, rdflib.RDF.type, ASB.Claim))
    g.add((c, ASB.context, rdflib.Literal("in vitro")))
    g.add((c, ASB.subject, rdflib.Literal("RNA-seq study")))
    g.add((c, ASB.relation, rdflib.Literal("uses")))
    g.add((c, ASB.object, rdflib.Literal("STAR aligner")))
    if qualifier is not None:
        g.add((c, ASB.qualifier, rdflib.Literal(qualifier)))
    if domain_qualifier is not None:
        g.add((c, ASB.domainQualifier, rdflib.Literal(domain_qualifier)))
    return g


def test_domain_qualifier_only_conforms():
    """A claim carrying only an open domain_qualifier (no core qualifier) is valid."""
    g = _claim(domain_qualifier="aligned_with")
    conforms, report = validate_graph(g)
    assert conforms, (
        "A claim with only asb:domainQualifier should conform once the core "
        f"qualifier is non-required.\nReport:\n{report}"
    )


def test_core_qualifier_only_conforms():
    """Guard: a claim carrying only a core Bucur qualifier is still valid."""
    g = _claim(qualifier="causes")
    conforms, report = validate_graph(g)
    assert conforms, (
        f"A claim with only the core asb:qualifier should still conform.\nReport:\n{report}"
    )


def test_claim_with_neither_qualifier_fails():
    """A claim with neither qualifier nor domain_qualifier violates the at-least-one rule."""
    g = _claim()
    conforms, report = validate_graph(g)
    assert not conforms, (
        "A claim with neither asb:qualifier nor asb:domainQualifier must fail SHACL.\n"
        f"Report:\n{report}"
    )
    assert "domainQualifier" in report or "at least one" in report.lower(), (
        "Violation report should mention the at-least-one-qualifier constraint.\n"
        f"Report:\n{report}"
    )


def test_out_of_enum_core_qualifier_still_rejected():
    """Guard: the core enum stays CLOSED — an off-vocabulary core qualifier is rejected."""
    g = _claim(qualifier="frobnicates")
    conforms, report = validate_graph(g)
    assert not conforms, (
        "An off-vocabulary value on the closed asb:qualifier enum must still be rejected.\n"
        f"Report:\n{report}"
    )


def test_non_snake_case_domain_qualifier_rejected():
    """The open domain_qualifier slot enforces a snake_case pattern."""
    g = _claim(qualifier="causes", domain_qualifier="Not Snake Case")
    conforms, report = validate_graph(g)
    assert not conforms, (
        "asb:domainQualifier must reject non-snake_case values via sh:pattern.\n"
        f"Report:\n{report}"
    )
