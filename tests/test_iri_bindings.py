import pytest
from indicium.iri_bindings import EVIDENCE_TYPE_ECO, LINK_TYPE_CITO, SOURCE_TYPE_IRI
from indicium.iri_bindings import expand_curie


def test_no_placeholder_iris_remain():
    assert "ECO:<verified>" not in EVIDENCE_TYPE_ECO.values()
    assert EVIDENCE_TYPE_ECO["inference"] != "ECO:0000001", \
        "inference must not bind to the ECO root 'evidence' class"


def test_all_five_evidence_types_present():
    assert set(EVIDENCE_TYPE_ECO) == {
        "data", "citation", "knowledge", "inference", "speculation"
    }


def test_cito_and_source_maps_nonempty():
    assert len(LINK_TYPE_CITO) == 4
    assert set(SOURCE_TYPE_IRI) == {"text", "figure", "table", "image"}


@pytest.mark.parametrize("curie,expected", [
    ("ECO:0000006", "http://purl.obolibrary.org/obo/ECO_0000006"),
    ("IAO:0000311", "http://purl.obolibrary.org/obo/IAO_0000311"),
    ("IAO:0000536", "http://purl.obolibrary.org/obo/IAO_0000536"),
    ("doco:Figure", "http://purl.org/spar/doco/Figure"),
    ("cito:supports", "http://purl.org/spar/cito/supports"),
])
def test_expand_curie(curie, expected):
    assert expand_curie(curie) == expected


def test_expand_curie_unknown_prefix_raises():
    with pytest.raises(ValueError, match="Unknown CURIE prefix"):
        expand_curie("owl:Class")
