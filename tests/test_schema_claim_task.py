"""v1.12.0 — Claim.source_task_kind provenance qualifier.

Canonical replacement for ASB's out-of-schema asbext:source_task_kind field.
Closed SourceTaskKind enum {reproduction, analysis, component_reconstruction,
extension}; claim-level sibling of Evidence.workflow_coupling in the
reproducibility-provenance family (claim↔source-task granularity).
"""
from __future__ import annotations

from pathlib import Path

import rdflib
from linkml_runtime import SchemaView

from indicium.validate import validate_graph

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"
ASB = rdflib.Namespace("https://asb.holobiomics.org/ns/asb#")

EXPECTED_VALUES = {"reproduction", "analysis", "component_reconstruction", "extension"}


# --- schema level (reads indicium.yaml directly) -----------------------------

def test_source_task_kind_schema_slot():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Claim"))
    assert "source_task_kind" in slots
    slot = sv.induced_slot("source_task_kind", "Claim")
    assert slot.range == "SourceTaskKind"
    assert slot.required is False or slot.required is None


def test_source_task_kind_enum_values_in_schema():
    sv = SchemaView(str(SCHEMA))
    enum = sv.get_enum("SourceTaskKind")
    assert enum is not None
    assert set(enum.permissible_values.keys()) == EXPECTED_VALUES


# --- generated-model level (requires `make gen`) -----------------------------

def test_source_task_kind_enum_and_slot_in_model():
    from indicium.generated.model import Claim, SourceTaskKind
    assert {e.value for e in SourceTaskKind} == EXPECTED_VALUES
    c = Claim(
        id="urn:claim:stk",
        context="in vitro",
        subject="RNA-seq study",
        relation="uses",
        object="STAR aligner",
        source_task_kind="reproduction",
    )
    assert (
        str(c.source_task_kind) == "reproduction"
        or c.source_task_kind == SourceTaskKind.reproduction
    )
    c_omitted = Claim(
        id="urn:claim:stk2",
        context="in vitro",
        subject="RNA-seq study",
        relation="uses",
        object="STAR aligner",
    )
    assert c_omitted.source_task_kind is None


# --- SHACL level (requires regenerated src/indicium/generated/shapes.ttl) -----

def _claim(source_task_kind: str | None = None) -> rdflib.Graph:
    """Build a conformant 5-slot Claim, optionally adding source_task_kind."""
    g = rdflib.Graph()
    c = rdflib.URIRef("urn:claim:stk")
    g.add((c, rdflib.RDF.type, ASB.Claim))
    g.add((c, ASB.context, rdflib.Literal("in vitro")))
    g.add((c, ASB.subject, rdflib.Literal("RNA-seq study")))
    g.add((c, ASB.relation, rdflib.Literal("uses")))
    g.add((c, ASB.object, rdflib.Literal("STAR aligner")))
    g.add((c, ASB.qualifier, rdflib.Literal("causes")))  # satisfy QualifierPresenceShape
    if source_task_kind is not None:
        g.add((c, ASB.sourceTaskKind, rdflib.Literal(source_task_kind)))
    return g


def test_claim_with_source_task_kind_conforms():
    g = _claim(source_task_kind="reproduction")
    conforms, report = validate_graph(g)
    assert conforms, f"Valid source_task_kind must conform.\nReport:\n{report}"


def test_off_vocabulary_source_task_kind_rejected():
    g = _claim(source_task_kind="frobnicates")
    conforms, report = validate_graph(g)
    assert not conforms, (
        "Off-vocabulary source_task_kind must be rejected by the closed enum's "
        f"sh:in.\nReport:\n{report}"
    )
