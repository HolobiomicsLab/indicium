from pathlib import Path
import rdflib
from indicium.validate import validate_graph

FIX = Path(__file__).parent / "fixtures"


def _verdict(fixture: str) -> bool:
    g = rdflib.Graph(); g.parse(FIX / fixture, format="turtle")
    conforms, _ = validate_graph(g)
    return conforms


def test_valid_claim_conforms():
    # Encodes the core requirement Scriptorium's mb-shapes ClaimShape also
    # enforces: a fully-populated 5-slot SuperPattern claim is accepted.
    # (Not a mechanical cross-validation — Scriptorium's shape additionally
    # requires dct:description and mb:claimType, which indicium does not.)
    assert _verdict("valid_claim.ttl") is True


def test_claim_missing_five_slots_is_rejected():
    # Core SuperPattern requirement, same as Scriptorium's ClaimShape:
    # a claim missing all five required slots is rejected.
    assert _verdict("invalid_claim_missing_slots.ttl") is False


def test_enriched_claim_with_external_properties_conforms():
    # Open shapes: a claim carrying KGmemory/PROV-O/DC properties beyond
    # indicium's own slots must still conform (cross-tool mergeability).
    assert _verdict("valid_claim.ttl") is True
