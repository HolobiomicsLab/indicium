from pathlib import Path
import rdflib
from indicium.validate import validate_graph

FIX = Path(__file__).parent / "fixtures"


def _verdict(fixture: str) -> bool:
    g = rdflib.Graph(); g.parse(FIX / fixture, format="turtle")
    conforms, _ = validate_graph(g)
    return conforms


def test_scriptorium_valid_claim_still_conforms():
    # Same accept verdict as Scriptorium's mb-shapes ClaimShape.
    assert _verdict("valid_claim.ttl") is True


def test_scriptorium_invalid_claim_still_rejected():
    # Same reject verdict — missing all five required SuperPattern slots.
    assert _verdict("invalid_claim_missing_slots.ttl") is False
