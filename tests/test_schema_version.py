"""The LinkML schema carries the package version and licence into every artefact.

A release bumps ``version`` in ``pyproject.toml`` and in
``src/indicium/schema/indicium.yaml`` together (RELEASING.md); ``make schema-assets``
then writes it into the model, the JSON Schema and the OWL ontology.
"""

import json
import tomllib
from importlib.resources import files
from pathlib import Path

import yaml
from rdflib import Graph, Literal, Namespace, URIRef

from indicium.generated import model

ROOT = Path(__file__).resolve().parents[1]
PAV = Namespace("http://purl.org/pav/")
DCT = Namespace("http://purl.org/dc/terms/")


def package_version():
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def schema_header():
    return yaml.safe_load(files("indicium.schema").joinpath("indicium.yaml").read_text())


def test_schema_version_equals_the_package_version():
    assert str(schema_header().get("version")) == package_version()


def test_schema_declares_the_package_licence():
    assert schema_header().get("license") == "MIT"


def test_generated_model_and_json_schema_carry_the_version():
    assert model.version == package_version()
    schema = json.loads(files("indicium.generated").joinpath("schema.json").read_text())
    assert schema["version"] == package_version()


def test_ontology_document_carries_version_and_licence():
    graph = Graph().parse(files("indicium.generated").joinpath("ontology.ttl"), format="turtle")
    ontology = URIRef("https://w3id.org/indicium")
    assert (ontology, PAV.version, Literal(package_version())) in graph
    assert (ontology, DCT.license, Literal("MIT")) in graph
