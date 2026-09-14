"""Smoke-test the installed wheel, including a rejected RDF negative control."""

import json
import tomllib
from importlib.resources import files
from pathlib import Path

import indicium
from rdflib import Graph, Literal, Namespace, RDF, URIRef

ROOT = Path(__file__).resolve().parents[1]


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
    assert indicium.validate_graph(graph)[0] is True
    graph.remove((URIRef(claim.id), asb.subject, Literal("A")))
    assert indicium.validate_graph(graph)[0] is False
    print(f"Wheel {expected}: model/context/SHACL passed; negative control rejected")
    print(f"Imported from {indicium.__file__}")


if __name__ == "__main__":
    check_installed_wheel()
