"""Wave 1 slot-audit tests.

One failing test per spec-required slot / class / enum addition. Tests are
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


def test_eco_code_asb_subset_enum_exists(sv):
    enum = sv.get_enum("EcoCodeAsbSubset")
    assert enum is not None, "EcoCodeAsbSubset enum missing"
    pv = enum.permissible_values
    expected = {
        "textual_quotation",
        "computational_evidence",
        "expert_curation",
        "inference_from_background_knowledge",
        "author_statement",
        "experimental_evidence",
        "combinatorial_evidence",
        "traceable_author_statement",
    }
    assert expected <= set(pv.keys()), (
        f"missing values: {expected - set(pv.keys())}"
    )


def test_eco_code_asb_subset_values_have_eco_meanings(sv):
    enum = sv.get_enum("EcoCodeAsbSubset")
    for name, pv in enum.permissible_values.items():
        assert pv.meaning is not None and pv.meaning.startswith("ECO:"), (
            f"EcoCodeAsbSubset.{name} must carry an ECO: meaning"
        )


def test_evidence_has_eco_code_slot(sv):
    slots = set(sv.class_slots("Evidence"))
    assert "eco_code" in slots, "Evidence.eco_code missing"
    induced = sv.induced_slot("eco_code", "Evidence")
    assert induced.range == "EcoCodeAsbSubset", (
        f"eco_code range must be EcoCodeAsbSubset (got {induced.range})"
    )


def test_source_has_doi_slot(sv):
    slots = set(sv.class_slots("Source"))
    assert "doi" in slots
    induced = sv.induced_slot("doi", "Source")
    assert induced.slot_uri == "dct:identifier" or "doi" in (induced.slot_uri or ""), (
        f"doi slot should expose a dct:identifier-compatible IRI (got {induced.slot_uri})"
    )


def test_source_has_paragraph_id_slot(sv):
    slots = set(sv.class_slots("Source"))
    assert "paragraph_id" in slots


def test_source_has_xpath_pointer_slot(sv):
    slots = set(sv.class_slots("Source"))
    assert "xpath_pointer" in slots


def test_software_entity_class_exists(sv):
    assert sv.get_class("SoftwareEntity") is not None, "SoftwareEntity class missing"


def test_software_entity_has_required_slots(sv):
    slots = set(sv.class_slots("SoftwareEntity"))
    expected = {
        "identifier", "canonical_url", "version",
        "edam_operation", "edam_topics", "bio_tools_id",
    }
    missing = expected - slots
    assert not missing, f"SoftwareEntity missing slots: {missing}"


def test_software_entity_edam_topics_multivalued(sv):
    induced = sv.induced_slot("edam_topics", "SoftwareEntity")
    assert induced.multivalued is True, "edam_topics must be multivalued"


def test_indicium_document_holds_software_entities(sv):
    slots = set(sv.class_slots("IndiciumDocument"))
    assert "software_entities" in slots
    induced = sv.induced_slot("software_entities", "IndiciumDocument")
    assert induced.range == "SoftwareEntity"
    assert induced.multivalued is True
    assert induced.inlined is True


def test_fixture_loads_against_schema():
    """Canonical round-trip fixture parses with the generated Pydantic models.

    Plan 1c (indicium-adapters) consumes this same fixture to verify its
    ASB → indicium adapter round-trips without loss.
    """
    import json
    from indicium.generated import model

    fixture = (
        Path(__file__).parent
        / "fixtures/asb_skill_roundtrip/skill_to_claim.json"
    )
    data = json.loads(fixture.read_text())

    # --- Minimal JSON-LD → Pydantic bridge (smoke-test only) ---
    # The generated Pydantic model uses:
    #   claims: dict[str, Claim]  (keyed by id, because Claim has `id` identifier)
    #   evidences/sources/software_entities: list[Entity]
    # We normalise the JSON-LD arrays into the shapes the model expects.

    # Classes with an `id` identifier slot (maps @id → id)
    ID_CLASSES = {"Claim"}
    # Classes with an `identifier` slot (maps @id → identifier)
    IDENTIFIER_CLASSES = {"Source", "SoftwareEntity"}
    # Classes with no primary key (drop @id)
    NO_KEY_CLASSES = {"Evidence"}

    def _strip_entity(obj, class_hint=None):
        """Remove @type, map @id to the right field, drop IRI-valued relation slots."""
        if not isinstance(obj, dict):
            return obj
        class_name = obj.pop("@type", class_hint)
        at_id = obj.pop("@id", None)
        if at_id is not None:
            if class_name in ID_CLASSES:
                obj["id"] = at_id
            elif class_name in IDENTIFIER_CLASSES:
                obj.setdefault("identifier", at_id)
            # else: drop @id (no primary key slot, e.g. Evidence)
        # Drop slots that carry IRI strings for related objects (not nested dicts);
        # they would fail Pydantic's model-type validation in this simple bridge.
        for key in ("of_source", "for_claim", "supports_claim"):
            if key in obj and isinstance(obj[key], str):
                obj.pop(key)
        return obj

    data.pop("@context", None)
    data.pop("@type", None)

    # claims → dict[str, Claim] (Claim has `id` identifier slot)
    claims_list = data.pop("claims", [])
    data["claims"] = {
        c["@id"]: _strip_entity(c, "Claim")
        for c in claims_list
    }

    # evidences / sources / software_entities → list (strip in place)
    for key, hint in (("evidences", "Evidence"), ("sources", "Source"),
                      ("software_entities", "SoftwareEntity")):
        data[key] = [_strip_entity(e, hint) for e in data.get(key, [])]

    doc = model.IndiciumDocument(**data)
    assert len(doc.claims) == 1
    assert len(doc.evidences) == 1
    assert len(doc.sources) == 1
    assert len(doc.software_entities) == 1
