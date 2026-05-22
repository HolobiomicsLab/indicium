from indicium.iri_bindings import EVIDENCE_TYPE_ECO, LINK_TYPE_CITO, SOURCE_TYPE_IRI


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
