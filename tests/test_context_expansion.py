"""Exercise RDF expansion at the package's schema boundary."""

import json
from importlib.resources import files

from linkml_runtime.utils.schemaview import SchemaView
from rdflib import Graph, Literal, Namespace, RDF, URIRef

from indicium import validate_graph

OBO = Namespace("http://purl.obolibrary.org/obo/")
INDICIUM = Namespace("https://w3id.org/indicium/")


def packaged_context():
    return json.loads(files("indicium.schema").joinpath("context.jsonld").read_text())["@context"]


def test_context_terms_expand_to_every_schema_binding():
    view = SchemaView(str(files("indicium.schema").joinpath("indicium.yaml")))
    context = packaged_context()
    for name, slot in view.all_slots().items():
        if name == "id":
            continue
        graph = Graph().parse(data=json.dumps({
            "@context": context, "@id": "urn:test:binding",
            name: {"@id": "urn:test:value"},
        }), format="json-ld")
        expected = URIRef(view.get_uri(slot, expand=True))
        assert (URIRef("urn:test:binding"), expected, URIRef("urn:test:value")) in graph, name


def test_evidence_context_reaches_shacl_and_preserves_distinct_slots():
    payload = {
        "@context": packaged_context(),
        "@graph": [
            {"@id": "urn:test:claim", "@type": "Claim", "context": "in vitro",
             "subject": "A", "qualifier": "inhibits", "relation": "inhibits", "object": "B"},
            {"@id": "urn:test:evidence", "@type": "Evidence", "eco_code": "textual_quotation",
             "quote": "A inhibits B", "quote_exact": "A inhibits B",
             "supports_claim": "urn:test:claim", "for_claim": "urn:test:claim"},
        ],
    }
    graph = Graph().parse(data=json.dumps(payload), format="json-ld")
    evidence = URIRef("urn:test:evidence")
    assert (evidence, RDF.type, OBO.SEPIO_0000002) in graph
    assert (evidence, INDICIUM.eco_code, OBO.ECO_0000033) in graph
    assert (evidence, INDICIUM.quote_exact, Literal("A inhibits B")) in graph
    assert (evidence, INDICIUM.for_claim, URIRef("urn:test:claim")) in graph
    assert (evidence, OBO.SEPIO_0000427, URIRef("urn:test:claim")) in graph
    assert validate_graph(graph)[0] is True
    graph.add((evidence, INDICIUM.eco_code, OBO.ECO_9999999))
    assert validate_graph(graph)[0] is False


def test_asb_validation_annotations_expand_to_real_obo_iris():
    graph = Graph().parse(data=json.dumps({
        "@context": packaged_context(), "@id": "urn:test:assessment",
        "@type": "asbval:ClaimAssessment",
        "sepio:0000183": {"@id": "sepio:0000403"},
        "ro:0002558": {"@id": "eco:0000501"},
    }), format="json-ld")
    subject = URIRef("urn:test:assessment")
    assert (subject, OBO.SEPIO_0000183, OBO.SEPIO_0000403) in graph
    assert (subject, OBO.RO_0002558, OBO.ECO_0000501) in graph
