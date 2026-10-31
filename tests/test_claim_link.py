"""Tests for Indicium v1.3: ClaimLink, ClaimStatus, OA selectors,
decision_context, asserted_by, astra_insight_ref, and astra_bridge.

Run with: uv run pytest tests/test_claim_link.py -v
"""
from __future__ import annotations

import pytest
from pathlib import Path
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"
FIXTURE_ASTRA = Path(__file__).parent / "fixtures/test_astra.yaml"

# ── Schema-level tests (SchemaView reads YAML directly; no make gen needed) ──

def test_claim_link_class_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("ClaimLink") is not None, "ClaimLink class missing from schema"


def test_claim_link_has_required_slots():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("ClaimLink"))
    assert "from_claim" in slots, "ClaimLink missing from_claim slot"
    assert "to_claim" in slots, "ClaimLink missing to_claim slot"
    assert "link_type" in slots, "ClaimLink missing link_type slot"


def test_link_type_enum_has_13_values():
    sv = SchemaView(str(SCHEMA))
    lt = sv.get_enum("LinkType")
    assert len(lt.permissible_values) == 13, (
        f"Expected 13 LinkType values, got {len(lt.permissible_values)}: "
        f"{list(lt.permissible_values)}"
    )


def test_link_type_new_9_values_present():
    sv = SchemaView(str(SCHEMA))
    lt = sv.get_enum("LinkType")
    for name in ("contradicts", "refines", "extends", "agreesWith",
                 "disagreesWith", "updates", "corrects", "usesDataFrom", "usesMethodIn"):
        assert name in lt.permissible_values, f"LinkType missing new value: {name}"


def test_link_type_original_4_values_preserved():
    sv = SchemaView(str(SCHEMA))
    lt = sv.get_enum("LinkType")
    for name in ("supports", "disputes", "qualifies", "citesForInformation"):
        assert name in lt.permissible_values, f"LinkType lost original value: {name}"


def test_claim_status_enum_exists_with_5_values():
    sv = SchemaView(str(SCHEMA))
    cs = sv.get_enum("ClaimStatus")
    assert cs is not None, "ClaimStatus enum missing"
    assert len(cs.permissible_values) == 5
    for v in ("draft", "verified", "published", "retracted", "superseded"):
        assert v in cs.permissible_values, f"ClaimStatus missing value: {v}"


def test_text_quote_selector_class_exists():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("TextQuoteSelector")
    assert cls is not None
    slots = set(sv.class_slots("TextQuoteSelector"))
    assert "tqs_exact" in slots
    assert "tqs_prefix" in slots
    assert "tqs_suffix" in slots


def test_fragment_selector_class_exists():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("FragmentSelector")
    assert cls is not None
    slots = set(sv.class_slots("FragmentSelector"))
    assert "frag_value" in slots
    assert "frag_page" in slots


def test_evidence_has_new_v1_3_slots():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Evidence"))
    for s in ("text_selector", "fragment_selector", "decision_context", "asserted_by"):
        assert s in slots, f"Evidence missing v1.3 slot: {s}"


def test_figure_has_fragment_selector_slot():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Figure"))
    assert "fragment_selector" in slots, "Figure missing fragment_selector slot"


def test_claim_has_v1_3_slots():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Claim"))
    for s in ("claim_status", "asserted_by", "astra_insight_ref"):
        assert s in slots, f"Claim missing v1.3 slot: {s}"


def test_oa_prefix_declared():
    sv = SchemaView(str(SCHEMA))
    prefixes = sv.schema.prefixes
    assert "oa" in prefixes, "oa: prefix not declared in schema"
    assert str(prefixes["oa"].prefix_reference) == "http://www.w3.org/ns/oa#"


def test_decision_context_is_multivalued():
    sv = SchemaView(str(SCHEMA))
    slot = sv.get_slot("decision_context")
    assert slot is not None
    assert slot.multivalued is True


# ── IRI bindings tests ──

def test_claim_link_type_cito_has_13_entries():
    from indicium.iri_bindings import CLAIM_LINK_TYPE_CITO
    assert len(CLAIM_LINK_TYPE_CITO) == 13, (
        f"Expected 13, got {len(CLAIM_LINK_TYPE_CITO)}: {list(CLAIM_LINK_TYPE_CITO)}"
    )


def test_claim_link_type_cito_all_cito_curies():
    from indicium.iri_bindings import CLAIM_LINK_TYPE_CITO
    for key, val in CLAIM_LINK_TYPE_CITO.items():
        assert val.startswith("cito:"), f"CLAIM_LINK_TYPE_CITO[{key!r}] = {val!r} not a cito: CURIE"


def test_expand_curie_oa_text_quote_selector():
    from indicium.iri_bindings import expand_curie
    result = expand_curie("oa:TextQuoteSelector")
    assert result == "http://www.w3.org/ns/oa#TextQuoteSelector"


def test_expand_curie_oa_fragment_selector():
    from indicium.iri_bindings import expand_curie
    result = expand_curie("oa:FragmentSelector")
    assert result == "http://www.w3.org/ns/oa#FragmentSelector"


def test_parse_decision_context_valid():
    from indicium.iri_bindings import parse_decision_context
    result = parse_decision_context(["fit_method.robust_linear", "outlier_handling.keep_all"])
    assert result == [("fit_method", "robust_linear"), ("outlier_handling", "keep_all")]


def test_parse_decision_context_empty_list():
    from indicium.iri_bindings import parse_decision_context
    assert parse_decision_context([]) == []


def test_parse_decision_context_invalid_raises():
    from indicium.iri_bindings import parse_decision_context
    with pytest.raises(ValueError, match="exactly one"):
        parse_decision_context(["no_dot_here"])


def test_parse_decision_context_too_many_dots_raises():
    from indicium.iri_bindings import parse_decision_context
    with pytest.raises(ValueError, match="exactly one"):
        parse_decision_context(["a.b.c"])


# ── Generated model tests (require `make gen` to have been run) ──

def test_claim_link_model_round_trip():
    from indicium.generated.model import ClaimLink, LinkType
    link = ClaimLink(
        from_claim="claim:001",
        to_claim="claim:002",
        link_type=LinkType.contradicts,
    )
    assert link.link_type == LinkType.contradicts


def test_claim_status_model():
    from indicium.generated.model import Claim, ClaimStatus, SuperPatternQualifier
    claim = Claim(
        id="c1",
        context="in vitro",
        subject="compound X",
        qualifier=SuperPatternQualifier.inhibits,
        relation="inhibits growth of",
        object="E. coli",
        claim_status=ClaimStatus.verified,
    )
    assert claim.claim_status == ClaimStatus.verified


def test_text_quote_selector_model():
    from indicium.generated.model import TextQuoteSelector
    tqs = TextQuoteSelector(
        tqs_exact="gut microbiome diversity decreases",
        tqs_prefix="We observed that",
        tqs_suffix="with antibiotic treatment.",
    )
    assert tqs.tqs_exact == "gut microbiome diversity decreases"


def test_fragment_selector_model():
    from indicium.generated.model import FragmentSelector
    fs = FragmentSelector(frag_value="page=3", frag_page=3)
    assert fs.frag_page == 3


def test_evidence_with_decision_context():
    from indicium.generated.model import Evidence
    ev = Evidence(decision_context=["fit_method.robust_linear", "outlier_handling.keep_all"])
    assert ev.decision_context == ["fit_method.robust_linear", "outlier_handling.keep_all"]


def test_claim_with_asserted_by():
    from indicium.generated.model import Claim, SuperPatternQualifier
    claim = Claim(
        id="c2",
        context="RCT study",
        subject="probiotic X",
        qualifier=SuperPatternQualifier.increases,
        relation="increases abundance of",
        object="Lactobacillus",
        asserted_by="https://orcid.org/0000-0001-2345-6789",
    )
    assert claim.asserted_by == "https://orcid.org/0000-0001-2345-6789"


def test_claim_with_astra_insight_ref():
    from indicium.generated.model import Claim, SuperPatternQualifier
    claim = Claim(
        id="c3",
        context="metabolomics study",
        subject="SCFA",
        qualifier=SuperPatternQualifier.correlates_with,
        relation="correlates with",
        object="gut inflammation",
        astra_insight_ref="iris_pipeline/insight_diversity_r2",
    )
    assert claim.astra_insight_ref == "iris_pipeline/insight_diversity_r2"


# ── astra_bridge tests ──

def test_insight_to_claim_basic():
    from indicium.astra_bridge import insight_to_claim
    insight = {
        "id": "i1",
        "claim": "Bacteroidetes increases with dietary fiber",
        "created_at": "2026-01-01T00:00:00Z",
        "evidence": [{"id": "e1", "doi": "10.1000/xyz"}],
    }
    claim = insight_to_claim(insight, analysis_id="test_run")
    assert claim.astra_insight_ref == "test_run/i1"
    assert claim.asserted_by == "test_run"
    # text was parsed — subject or object should contain part of the claim
    assert "Bacteroidetes" in claim.subject or "Bacteroidetes" in claim.object
    assert claim.object != ""


def test_insight_to_claim_verb_heuristic():
    from indicium.astra_bridge import insight_to_claim
    insight = {
        "id": "i2",
        "claim": "gut microbiome diversity decreases with antibiotic treatment",
    }
    claim = insight_to_claim(insight, analysis_id="test_run")
    assert claim.qualifier.value == "decreases"
    assert "gut microbiome diversity" in claim.subject


def test_claim_to_insight_basic():
    from indicium.astra_bridge import claim_to_insight
    from indicium.generated.model import Claim, SuperPatternQualifier
    claim = Claim(
        id="c1",
        context="in vitro",
        subject="compound X",
        qualifier=SuperPatternQualifier.inhibits,
        relation="inhibits growth of",
        object="E. coli",
    )
    insight = claim_to_insight(claim, evidence_doi="10.1000/xyz")
    assert "compound X" in insight["claim"]
    assert insight["indicium_claim_ref"] == "c1"
    assert insight["evidence"][0]["doi"] == "10.1000/xyz"


def test_load_astra_findings():
    from indicium.astra_bridge import load_astra_findings
    claims = load_astra_findings(FIXTURE_ASTRA)
    assert len(claims) == 2
    assert all(c.asserted_by == "test_analysis" for c in claims)
    assert any("decreases" in c.qualifier.value for c in claims)


def test_load_astra_prior_insights():
    from indicium.astra_bridge import load_astra_prior_insights
    claims = load_astra_prior_insights(FIXTURE_ASTRA)
    assert len(claims) == 1
    assert claims[0].asserted_by == "test_analysis"


def test_astra_bridge_missing_pyyaml(monkeypatch):
    import sys
    # Set sys.modules["yaml"] = None to simulate pyyaml not being installed.
    # Python raises ImportError for any "import yaml" when the entry is None.
    # monkeypatch restores the original value after the test automatically.
    monkeypatch.setitem(sys.modules, "yaml", None)
    from indicium.astra_bridge import _require_pyyaml
    with pytest.raises(ImportError, match="pyyaml"):
        _require_pyyaml()
