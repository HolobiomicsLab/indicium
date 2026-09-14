"""Check Evidence and reliance bindings against pinned SEPIO OWL axioms."""

import json
from pathlib import Path

import pytest
from linkml_runtime.utils.schemaview import SchemaView
from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.namespace import OWL

ROOT = Path(__file__).parents[1]
OBO = Namespace("http://purl.obolibrary.org/obo/")
INDICIUM = Namespace("https://w3id.org/indicium/")
SCHEMA = ROOT / "src/indicium/schema/indicium.yaml"
CONTEXT = SCHEMA.with_name("context.jsonld")
AXIOMS = Path(__file__).parent / "fixtures/sepio/binding-axioms.ttl"


@pytest.fixture(scope="module")
def ontology():
    return Graph().parse(AXIOMS, format="turtle")


def test_supports_claim_uses_an_inverse_with_evidence_line_domain(ontology):
    view = SchemaView(str(SCHEMA))
    slot = view.induced_slot("supports_claim", "Evidence")
    predicate = URIRef(view.get_uri(slot, expand=True))
    forward = ontology.value(predicate, OWL.inverseOf)
    forward = forward or ontology.value(predicate=OWL.inverseOf, object=predicate)
    assert forward is not None, "Evidence -> Claim must invert has_evidence_line"
    assert ontology.value(predicate, RDFS.label) == ontology.value(OBO.SEPIO_0000427, RDFS.label)
    assert ontology.value(forward, RDFS.range) == URIRef(view.get_uri(view.get_class("Evidence"), expand=True))
    domain = ontology.value(forward, RDFS.domain)
    alternatives = Collection(ontology, ontology.value(domain, OWL.unionOf))
    assert set(alternatives) == {OBO.SEPIO_0000000, OBO.SEPIO_0000001}
    assert slot.range == "Claim"
    assert slot.aliases == ["for_claim"]
    assert view.get_uri(view.get_slot("for_claim"), expand=True) == str(INDICIUM.for_claim)


def test_asserts_is_schema_owned_local_reliance_without_external_mapping(ontology):
    view = SchemaView(str(SCHEMA))
    slot = view.get_slot("asserts")
    assert slot is not None, "Reliance must have a schema-owned local predicate"
    assert view.get_uri(slot, expand=True) == str(INDICIUM.asserts)
    assert slot.range == "Claim"
    assert not slot.exact_mappings
    assert not slot.close_mappings
    assert str(ontology.value(OBO.SEPIO_0000130, RDFS.label)) == "authored_by"
    contributor = ontology.value(OBO.SEPIO_0000130, RDFS.subPropertyOf)
    assert ontology.value(contributor, RDFS.range) == URIRef("http://www.w3.org/ns/prov#Agent")


def test_asserts_expands_to_reliance_instead_of_authorship():
    payload = json.loads(CONTEXT.read_text()) | {
        "@id": "urn:test:skill", "asserts": "urn:test:claim",
    }
    graph = Graph().parse(data=json.dumps(payload), format="json-ld")
    assert (URIRef("urn:test:skill"), INDICIUM.asserts, URIRef("urn:test:claim")) in graph
    assert not list(graph.triples((None, OBO.SEPIO_0000130, None)))


@pytest.mark.parametrize("direction", ["0000403", "0000404", "0000405"])
def test_evidence_target_and_direction_are_independent(ontology, direction):
    target = OBO["SEPIO_" + direction]
    direction_class = ontology.value(OBO.SEPIO_0000183, RDFS.range)
    assert (target, RDF.type, direction_class) in ontology
    assert ontology.value(OBO.SEPIO_0000183, RDFS.domain) == OBO.SEPIO_0000002
    payload = json.loads(CONTEXT.read_text()) | {
        "@id": "urn:test:evidence", "@type": "Evidence",
        "supports_claim": "urn:test:claim", "for_claim": "urn:test:claim",
        "sepio:0000183": {"@id": "sepio:" + direction},
    }
    graph = Graph().parse(data=json.dumps(payload), format="json-ld")
    evidence = URIRef("urn:test:evidence")
    assert (evidence, OBO.SEPIO_0000427, URIRef("urn:test:claim")) in graph
    assert (evidence, INDICIUM.for_claim, URIRef("urn:test:claim")) in graph
    assert (evidence, OBO.SEPIO_0000183, target) in graph
    assert not list(graph.triples((None, OBO.SEPIO_0000007, None)))


def test_shacl_uses_evidence_line_to_claim_direction():
    graph = Graph().parse(ROOT / "src/indicium/generated/shapes.ttl", format="turtle")
    sh = Namespace("http://www.w3.org/ns/shacl#")
    assert list(graph.triples((None, sh.path, OBO.SEPIO_0000427)))
    assert not list(graph.triples((None, sh.path, OBO.SEPIO_0000007)))
