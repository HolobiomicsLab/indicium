"""The published SHACL file applies the same constraints as ``validate_graph``.

``docs/schema-assets/indicium.shapes.ttl`` is the GitHub release asset and the file
the ``/indicium`` identifier would serve. ``validate_graph`` checks the generated
shapes plus the supplemental shapes LinkML cannot express, so the published file must
hold both: a reader who runs pyshacl on it must get the verdict the package gives.
"""

from importlib.resources import files
from pathlib import Path

import pytest
import rdflib
from pyshacl import validate as shacl_validate
from rdflib.compare import isomorphic

from indicium import ASB_BASE, INDICIUM_BASE, validate_graph

ROOT = Path(__file__).resolve().parents[1]
ARTEFACT = ROOT / "docs" / "schema-assets" / "indicium.shapes.ttl"
FIXTURES = sorted((ROOT / "tests" / "fixtures").glob("*.ttl"))

FULL_CLAIM = f"""
@prefix asb: <{ASB_BASE}> .
@prefix indicium: <{INDICIUM_BASE}> .
<urn:claim:1> a asb:Claim ;
    asb:context "in vitro" ; asb:subject "A" ; asb:relation "inhibits" ; asb:object "B"
"""

CASES = {
    "with_qualifier": FULL_CLAIM + ' ; asb:qualifier "inhibits" .',
    "with_domain_qualifier": FULL_CLAIM + ' ; asb:domainQualifier "upregulates" .',
    "no_qualifier": FULL_CLAIM + " .",
    "superseded_without_replacement": FULL_CLAIM
    + ' ; asb:qualifier "inhibits" ; indicium:claim_status "superseded" .',
}


def package_shapes():
    graph = rdflib.Graph()
    graph.parse(files("indicium.generated").joinpath("shapes.ttl"), format="turtle")
    graph.parse(files("indicium.augmentation").joinpath("supplemental-shapes.ttl"), format="turtle")
    return graph


def artefact_verdict(data):
    shapes = rdflib.Graph().parse(ARTEFACT, format="turtle")
    conforms, _, _ = shacl_validate(
        data_graph=data, shacl_graph=shapes, inference="none",
        abort_on_first=False, meta_shacl=False, allow_warnings=True,
    )
    return conforms


def test_artefact_holds_the_generated_and_supplemental_shapes():
    assert isomorphic(rdflib.Graph().parse(ARTEFACT, format="turtle"), package_shapes())


@pytest.mark.parametrize("fixture", FIXTURES, ids=[path.name for path in FIXTURES])
def test_artefact_and_validate_graph_agree_on_fixtures(fixture):
    data = rdflib.Graph().parse(fixture, format="turtle")
    assert artefact_verdict(data) == validate_graph(data)[0]


@pytest.mark.parametrize("name", sorted(CASES))
def test_artefact_and_validate_graph_agree_on_qualifier_cases(name):
    data = rdflib.Graph().parse(data=CASES[name], format="turtle")
    assert artefact_verdict(data) == validate_graph(data)[0]


def test_no_qualifier_claim_is_rejected_by_the_artefact():
    data = rdflib.Graph().parse(data=CASES["no_qualifier"], format="turtle")
    assert artefact_verdict(data) is False
