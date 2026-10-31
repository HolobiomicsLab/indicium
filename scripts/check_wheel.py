"""Smoke-test the installed wheel, including a rejected RDF negative control."""

import json
import tomllib
from importlib.resources import files
from pathlib import Path

import indicium
from rdflib import Graph, Literal, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]


def check_evidence_bindings(context, graph):
    """Verify the installed context keeps evidence targets and reliance distinct."""
    payload = {**context, "@graph": [
        {"@id": "urn:smoke:evidence", "@type": "Evidence",
         "supports_claim": "urn:smoke:claim", "for_claim": "urn:smoke:claim",
         "sepio:0000183": {"@id": "sepio:0000404"}},
        {"@id": "urn:smoke:skill", "asserts": "urn:smoke:claim"},
    ]}
    graph.parse(data=json.dumps(payload), format="json-ld")
    obo = Namespace("http://purl.obolibrary.org/obo/")
    local = Namespace(indicium.INDICIUM_BASE)
    evidence, claim = URIRef("urn:smoke:evidence"), URIRef("urn:smoke:claim")
    assert (evidence, obo.SEPIO_0000427, claim) in graph
    assert (evidence, local.for_claim, claim) in graph
    assert (evidence, obo.SEPIO_0000183, obo.SEPIO_0000404) in graph
    assert (URIRef("urn:smoke:skill"), local.asserts, claim) in graph
    assert not list(graph.triples((None, obo.SEPIO_0000007, None)))
    assert not list(graph.triples((None, obo.SEPIO_0000130, None)))


def check_installed_wheel():
    """Verify version, model round-trip, packaged context and active SHACL shapes."""
    expected = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert indicium.__version__ == expected
    assert ROOT / "src" not in Path(indicium.__file__).parents, indicium.__file__
    claim = indicium.Claim(id="urn:smoke:claim", context="in vitro", subject="A",
                           qualifier="inhibits", relation="inhibits", object="B")
    assert indicium.Claim.model_validate_json(claim.model_dump_json()) == claim
    context = json.loads(files("indicium.schema").joinpath("context.jsonld").read_text())
    graph = Graph().parse(data=json.dumps({**context, "@type": "Claim", **claim.model_dump(mode="json", exclude_none=True)}), format="json-ld")
    asb = Namespace(indicium.ASB_BASE)
    assert (URIRef(claim.id), RDF.type, asb.Claim) in graph
    check_evidence_bindings(context, graph)
    assert indicium.validate_graph(graph)[0] is True
    graph.remove((URIRef(claim.id), asb.subject, Literal("A")))
    assert indicium.validate_graph(graph)[0] is False
    print(f"Wheel {expected}: model/context/SEPIO/reliance/SHACL passed; negative control rejected")
    print(f"Imported from {indicium.__file__}")


if __name__ == "__main__":
    check_installed_wheel()
