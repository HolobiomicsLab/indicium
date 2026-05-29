"""Tests that all public types are importable directly from `indicium`."""
from __future__ import annotations


def test_core_model_classes_importable():
    from indicium import (
        Claim, Evidence, Source, CitationLink,
    )
    assert Claim is not None
    assert Evidence is not None
    assert Source is not None
    assert CitationLink is not None


def test_core_enums_importable():
    from indicium import (
        ClaimType, EvidenceType, SourceType, SuperPatternQualifier,
    )
    assert ClaimType is not None
    assert EvidenceType is not None
    assert SourceType is not None
    assert SuperPatternQualifier is not None


def test_instantiate_claim_from_top_level_import():
    from indicium import Claim, SuperPatternQualifier
    c = Claim(
        id="c1",
        context="in vitro",
        subject="X",
        qualifier=SuperPatternQualifier.inhibits,
        relation="inhibits",
        object="Y",
    )
    assert c.id == "c1"
    assert c.qualifier == SuperPatternQualifier.inhibits


def test_instantiate_evidence_from_top_level_import():
    from indicium import Evidence, EvidenceType
    ev = Evidence(evidence_type=EvidenceType.data)
    assert ev.evidence_type == EvidenceType.data


def test_verify_quote_importable_from_top_level():
    from indicium import VerificationResult, verify_quote

    res = verify_quote("aerobic glycolysis", ["cells show aerobic glycolysis here"])
    assert isinstance(res, VerificationResult)
    assert res.status == "verified"
    assert res.matched_index == 0
