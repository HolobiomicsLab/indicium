from pathlib import Path
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


def test_evidence_links_claim_to_source():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("Evidence") is not None
    slots = set(sv.class_slots("Evidence"))
    assert {"evidence_type", "source_type", "quote", "of_source"} <= slots


def test_source_requires_identifier():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("Source") is not None
    ident = sv.induced_slot("identifier", "Source")
    assert ident.required is True


def test_citation_link_has_link_type_enum():
    sv = SchemaView(str(SCHEMA))
    link = sv.induced_slot("link_type", "CitationLink")
    assert link.range == "LinkType"
