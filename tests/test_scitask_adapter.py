from indicium.adapters.scitask import claim_to_evidence_snippet


def _make_claim(**overrides):
    base = {
        "id": "c001",
        "context": "in vitro",
        "subject": "compound A",
        "qualifier": "inhibits",
        "relation": "inhibits growth of",
        "object": "cell line B",
        "source_excerpt": "Compound A inhibited cell line B by 80%.",
        "evidence": [{"doi": "10.1234/x", "artifact": "results/fig1.png"}],
    }
    base.update(overrides)
    return base


def test_required_fields_present():
    snip = claim_to_evidence_snippet(_make_claim())
    assert snip["snippet_id"] == "c001"
    assert snip["source_path"] == "results/fig1.png"
    assert "compound A" in snip["reason"]
    assert snip["text"] == "Compound A inhibited cell line B by 80%."


def test_source_path_falls_back_to_doi():
    claim = _make_claim(evidence=[{"doi": "10.1234/x"}])
    snip = claim_to_evidence_snippet(claim)
    assert snip["source_path"] == "doi:10.1234/x"


def test_text_falls_back_to_quote():
    claim = _make_claim(source_excerpt="")
    claim["evidence"] = [{"doi": "10.1234/x", "quote": "A inhibited B"}]
    snip = claim_to_evidence_snippet(claim)
    assert snip["text"] == "A inhibited B"


def test_explicit_source_path_overrides():
    snip = claim_to_evidence_snippet(_make_claim(), source_path="custom/path.txt")
    assert snip["source_path"] == "custom/path.txt"


def test_empty_evidence_produces_valid_snippet():
    claim = _make_claim(evidence=[])
    snip = claim_to_evidence_snippet(claim)
    assert snip["snippet_id"] == "c001"
    assert snip["source_path"] == ""
    assert snip["text"] == "Compound A inhibited cell line B by 80%."
