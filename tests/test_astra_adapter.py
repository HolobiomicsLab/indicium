from indicium.adapters.astra import claim_to_insight


def test_claim_projects_to_astra_insight():
    claim = {
        "id": "c001",
        "context": "in vitro", "subject": "compound A",
        "qualifier": "inhibits", "relation": "inhibits growth of",
        "object": "cell line B",
        "evidence": [{"doi": "10.1234/x", "quote": "A inhibited B"}],
    }
    insight = claim_to_insight(claim)
    assert insight["id"] == "c001"
    assert "compound A" in insight["claim"]
    assert insight["evidence"][0]["doi"] == "10.1234/x"
    assert insight["evidence"][0]["quote"]["exact"] == "A inhibited B"
