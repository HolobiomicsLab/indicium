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


# ---------------------------------------------------------------------------
# v1.10.0 — Evidence.workflow_coupling (Suter et al. 2025)
# ---------------------------------------------------------------------------

def test_evidence_workflow_coupling_enum_and_slot():
    from indicium.generated.model import Evidence, WorkflowCoupling
    assert {e.value for e in WorkflowCoupling} == {"tight", "loose", "ad_hoc", "unknown"}
    ev = Evidence(workflow_coupling="tight")
    assert str(ev.workflow_coupling) == "tight" or ev.workflow_coupling == WorkflowCoupling.tight
    assert Evidence().workflow_coupling is None


def test_evidence_workflow_coupling_shacl_conforms():
    """An Evidence with workflow_coupling='loose' must pass SHACL validation."""
    import rdflib
    import indicium
    from indicium.generated.model import Evidence

    ev = Evidence(workflow_coupling="loose")
    # Build the minimal valid RDF graph directly (Evidence alone is not a Claim,
    # so we validate just the Evidence node with open SHACL shapes)
    asb = rdflib.Namespace("https://asb.holobiomics.org/ns/asb#")
    indicium_ns = rdflib.Namespace("https://w3id.org/indicium/")
    g = rdflib.Graph()
    g.bind("asb", asb)
    g.bind("indicium", indicium_ns)

    ev_node = rdflib.URIRef("urn:evidence:e1")
    g.add((ev_node, rdflib.RDF.type, rdflib.URIRef("http://purl.obolibrary.org/obo/SEPIO_0000002")))
    g.add((ev_node, asb.workflowCoupling, rdflib.Literal(ev.workflow_coupling.value)))

    conforms, _ = indicium.validate_graph(g)
    assert conforms is True


def test_evidence_workflow_coupling_schema_slot():
    """Schema-level check: workflow_coupling is a slot of Evidence with range WorkflowCoupling."""
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Evidence"))
    assert "workflow_coupling" in slots
    wc_slot = sv.induced_slot("workflow_coupling", "Evidence")
    assert wc_slot.range == "WorkflowCoupling"
    assert wc_slot.required is False or wc_slot.required is None
