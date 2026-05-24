"""Wave 1 slot-audit tests.

One failing test per spec-required slot / class / enum addition (see
docs/superpowers/plans/2026-05-24-indicium-slot-audit-wave1.md). Tests are
added FIRST (red), then the schema is updated (green).
"""
from pathlib import Path

import pytest
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


@pytest.fixture(scope="module")
def sv() -> SchemaView:
    return SchemaView(str(SCHEMA))


def test_claim_has_predicate_slot(sv):
    """Claim.predicate is the spec-required name for the CiTO/SEPIO predicate.

    It aliases relation (same slot_uri asb:relation) so existing serialisations
    keep working while the new name is available to the ASB adapter.
    """
    slots = set(sv.class_slots("Claim"))
    assert "predicate" in slots, "Claim.predicate missing — add as alias for relation"
    induced = sv.induced_slot("predicate", "Claim")
    assert induced.slot_uri == "asb:relation", (
        f"predicate must share slot_uri asb:relation (got {induced.slot_uri})"
    )


def test_claim_has_super_pattern_slot(sv):
    """Claim.super_pattern is the spec-required name for the Bucur qualifier.

    Aliases `qualifier` (same slot_uri, same range SuperPatternQualifier).
    """
    slots = set(sv.class_slots("Claim"))
    assert "super_pattern" in slots, "Claim.super_pattern missing — add as alias for qualifier"
    induced = sv.induced_slot("super_pattern", "Claim")
    assert induced.range == "SuperPatternQualifier", (
        f"super_pattern range must be SuperPatternQualifier (got {induced.range})"
    )
    assert induced.slot_uri == "asb:qualifier"


def test_evidence_has_quote_exact_slot(sv):
    slots = set(sv.class_slots("Evidence"))
    assert "quote_exact" in slots, "Evidence.quote_exact missing — alias for quote"


def test_evidence_has_supports_claim_slot(sv):
    slots = set(sv.class_slots("Evidence"))
    assert "supports_claim" in slots, "Evidence.supports_claim missing — alias for for_claim"
    induced = sv.induced_slot("supports_claim", "Evidence")
    assert induced.range == "Claim", (
        f"supports_claim range must be Claim (got {induced.range})"
    )


def test_evidence_has_quote_location_slot(sv):
    """quote_location is a free-form locator (paragraph id, xpath, page-offset,
    OA-fragment IRI). Selector classes remain for structured locators."""
    slots = set(sv.class_slots("Evidence"))
    assert "quote_location" in slots, "Evidence.quote_location missing"
    induced = sv.induced_slot("quote_location", "Evidence")
    assert induced.range == "string"
