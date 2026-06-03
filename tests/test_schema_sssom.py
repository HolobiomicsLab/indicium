"""Tests for SSSOMMapping class and IndiciumDocument.sssom_mappings slot (v1.11.0)."""
import rdflib
import indicium
from indicium.generated.model import SSSOMMapping, IndiciumDocument


def test_sssom_mapping_constructs():
    m = SSSOMMapping(
        id="asb.skill:peak-detection--EDAM:operation_3215",
        subject_id="asb.skill:peak-detection",
        predicate_id="skos:closeMatch",
        object_id="EDAM:operation_3215",
        mapping_justification="semapv:LexicalMatching",
        confidence=0.83,
        derived_from=["someprior:mapping"],
    )
    assert m.subject_id == "asb.skill:peak-detection"
    assert m.confidence == 0.83
    assert list(m.derived_from) == ["someprior:mapping"]


def test_indicium_document_carries_sssom_mappings():
    # The generated model keys inlined identifier-bearing classes by id (dict[str, T])
    doc = IndiciumDocument(
        sssom_mappings={
            "m1": SSSOMMapping(
                id="m1",
                subject_id="asb.skill:x",
                predicate_id="skos:closeMatch",
                object_id="EDAM:operation_3215",
            )
        }
    )
    assert len(doc.sssom_mappings) == 1


def test_sssom_mapping_shacl_valid(tmp_path):
    m = SSSOMMapping(
        id="m1",
        subject_id="asb.skill:x",
        predicate_id="skos:closeMatch",
        object_id="EDAM:operation_3215",
        mapping_justification="semapv:LexicalMatching",
    )
    # The SHACL shapes use indicium: namespace for all generated slots.
    # sssom:Mapping is the rdf:type; slots are indicium:subject_id etc.
    sssom_ns = rdflib.Namespace("https://w3id.org/sssom/")
    indicium_ns = rdflib.Namespace("https://w3id.org/indicium/")
    g = rdflib.Graph()
    g.bind("sssom", sssom_ns)
    g.bind("indicium", indicium_ns)
    node = rdflib.URIRef("https://w3id.org/indicium/m1")
    g.add((node, rdflib.RDF.type, sssom_ns.Mapping))
    g.add((node, indicium_ns.subject_id, rdflib.Literal(m.subject_id)))
    g.add((node, indicium_ns.predicate_id, rdflib.Literal(m.predicate_id)))
    g.add((node, indicium_ns.object_id, rdflib.Literal(m.object_id)))
    g.add((node, indicium_ns.mapping_justification, rdflib.Literal(m.mapping_justification)))

    ok, report = indicium.validate_graph(g)
    assert ok, report
