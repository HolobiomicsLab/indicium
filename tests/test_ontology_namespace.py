"""The generated ontology document must stay inside the registered namespace."""

from importlib.resources import files

from rdflib import Graph, OWL, RDF, URIRef

from indicium import INDICIUM_BASE


def test_ontology_document_uses_the_registered_namespace_root():
    graph = Graph().parse(files("indicium.generated").joinpath("ontology.ttl"), format="turtle")
    assert set(graph.subjects(RDF.type, OWL.Ontology)) == {URIRef(INDICIUM_BASE.rstrip("/"))}
