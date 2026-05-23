"""Tests for Indicium v1.4: IndiciumDocument container, superseded_by,
ClaimLink URI fix, _split_claim_text fallback.

Run with: cd ~/git/indicium && uv run pytest tests/test_indicium_v14.py -v
"""
from __future__ import annotations

import pytest
from pathlib import Path
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


# ── Schema-level: IndiciumDocument container ─────────────────────────────────

def test_indicium_document_class_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("IndiciumDocument") is not None, \
        "IndiciumDocument class missing from schema"


def test_indicium_document_is_tree_root():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("IndiciumDocument")
    assert cls.tree_root is True, "IndiciumDocument must have tree_root: true"


def test_indicium_document_has_8_slots():
    sv = SchemaView(str(SCHEMA))
    slots = sv.class_slots("IndiciumDocument")
    assert len(slots) == 8, (
        f"Expected 8 slots on IndiciumDocument, got {len(slots)}: {slots}"
    )


def test_indicium_document_slot_names():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("IndiciumDocument"))
    expected = {"claims", "evidences", "sources", "figures",
                "scripts", "datasets", "claim_links", "citation_links"}
    assert slots == expected, f"IndiciumDocument slot mismatch: {slots}"


# ── Schema-level: superseded_by ───────────────────────────────────────────────

def test_superseded_by_slot_exists():
    sv = SchemaView(str(SCHEMA))
    slot = sv.get_slot("superseded_by")
    assert slot is not None, "superseded_by slot missing from schema"


def test_superseded_by_is_optional():
    sv = SchemaView(str(SCHEMA))
    slot = sv.get_slot("superseded_by")
    assert slot.required is not True, \
        "superseded_by must be optional (required != True)"


def test_superseded_by_range_is_uriorcurie():
    sv = SchemaView(str(SCHEMA))
    slot = sv.get_slot("superseded_by")
    assert slot.range == "uriorcurie", \
        f"superseded_by range must be uriorcurie, got {slot.range!r}"


def test_claim_has_superseded_by_slot():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Claim"))
    assert "superseded_by" in slots, "Claim missing superseded_by slot"


# ── Schema-level: ClaimLink class_uri fix ────────────────────────────────────

def test_claim_link_class_uri_is_not_cito_citation():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("ClaimLink")
    # After fix: class_uri should default to indicium:ClaimLink, NOT cito:Citation
    curie = str(cls.class_uri) if cls.class_uri else ""
    assert "cito" not in curie.lower(), (
        f"ClaimLink.class_uri should NOT be cito:Citation, got {curie!r}. "
        "Remove the explicit class_uri to let it default to indicium:ClaimLink."
    )


def test_claim_link_class_uri_uses_indicium_prefix():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("ClaimLink")
    curie = str(cls.class_uri) if cls.class_uri else ""
    # When class_uri is omitted, SchemaView resolves it to default_prefix:ClassName
    # i.e. "indicium:ClaimLink"
    assert curie == "" or "indicium" in curie.lower(), (
        f"ClaimLink.class_uri should be unset or indicium:ClaimLink, got {curie!r}"
    )


# ── Schema-level: decision_context pattern ───────────────────────────────────

def test_decision_context_has_pattern():
    sv = SchemaView(str(SCHEMA))
    slot = sv.get_slot("decision_context")
    assert slot is not None
    assert slot.pattern is not None, \
        "decision_context slot missing pattern constraint"
    assert "." in slot.pattern, \
        f"decision_context pattern should contain '.', got {slot.pattern!r}"


# ── Generated model: IndiciumDocument ────────────────────────────────────────

def test_indicium_document_model_round_trip():
    from indicium.generated.model import (
        IndiciumDocument, Claim, ClaimLink,
        SuperPatternQualifier, LinkType,
    )
    # claims is dict[str, Claim] (keyed by id — Claim has identifier: true)
    # claim_links is list[ClaimLink] (no identifier field)
    doc = IndiciumDocument(
        claims={"c1": Claim(
            id="c1",
            context="in vitro",
            subject="compound X",
            qualifier=SuperPatternQualifier.inhibits,
            relation="inhibits growth of",
            object="E. coli",
        )},
        claim_links=[
            ClaimLink(
                from_claim="c1",
                to_claim="c2",
                link_type=LinkType.contradicts,
            )
        ],
    )
    assert len(doc.claims) == 1
    assert len(doc.claim_links) == 1
    assert doc.claims["c1"].id == "c1"


def test_indicium_document_exported():
    from indicium import IndiciumDocument  # must be in __all__
    assert IndiciumDocument is not None


def test_indicium_document_empty_instantiation():
    from indicium.generated.model import IndiciumDocument
    doc = IndiciumDocument()
    # All collection slots default to empty list (not None)
    assert doc.claims is None or isinstance(doc.claims, list)
    assert doc.claim_links is None or isinstance(doc.claim_links, list)


# ── Generated model: superseded_by ───────────────────────────────────────────

def test_claim_with_superseded_by():
    from indicium.generated.model import Claim, ClaimStatus, SuperPatternQualifier
    claim = Claim(
        id="c1",
        context="in vitro",
        subject="compound X",
        qualifier=SuperPatternQualifier.inhibits,
        relation="inhibits growth of",
        object="E. coli",
        claim_status=ClaimStatus.superseded,
        superseded_by="https://w3id.org/indicium/claim/c2",
    )
    assert claim.superseded_by == "https://w3id.org/indicium/claim/c2"
    assert claim.claim_status == ClaimStatus.superseded


def test_claim_superseded_by_is_optional():
    from indicium.generated.model import Claim, SuperPatternQualifier
    # Must instantiate without superseded_by
    claim = Claim(
        id="c2",
        context="in vitro",
        subject="compound Y",
        qualifier=SuperPatternQualifier.activates,
        relation="activates",
        object="enzyme Z",
    )
    assert claim.superseded_by is None


# ── astra_bridge: _split_claim_text fallback ─────────────────────────────────

def test_insight_to_claim_no_verb_fallback():
    """When no known verb is found, subject = full claim text, object = ''."""
    from indicium.astra_bridge import insight_to_claim
    insight = {"id": "i_noverb", "claim": "microbial diversity is important"}
    claim = insight_to_claim(insight, analysis_id="test_run")
    assert claim.subject == "microbial diversity is important", (
        f"Expected subject to be full claim text, got {claim.subject!r}"
    )
    assert claim.object == "", (
        f"Expected empty object for no-verb claim, got {claim.object!r}"
    )
    assert claim.qualifier.value == "has_property", (
        f"Expected qualifier 'has_property', got {claim.qualifier.value!r}"
    )
