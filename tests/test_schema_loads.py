from pathlib import Path
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


def test_claim_class_has_five_slot_pattern():
    sv = SchemaView(str(SCHEMA))
    claim = sv.get_class("Claim")
    assert claim is not None
    slots = set(sv.class_slots("Claim"))
    for s in ("context", "subject", "qualifier", "relation", "object"):
        assert s in slots, f"Claim missing SuperPattern slot {s}"


def test_qualifier_enum_has_20_bucur_terms():
    sv = SchemaView(str(SCHEMA))
    e = sv.get_enum("SuperPatternQualifier")
    assert len(e.permissible_values) == 20


def test_evidence_type_enum_bound_to_eco():
    sv = SchemaView(str(SCHEMA))
    e = sv.get_enum("EvidenceType")
    data = e.permissible_values["data"]
    assert data.meaning == "ECO:0000006"
