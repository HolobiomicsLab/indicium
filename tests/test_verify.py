"""Unit tests for the quote-verification kernel (pure, no rdflib)."""
from __future__ import annotations

from indicium.verify import (
    REPAIRED,
    UNVERIFIED,
    VERIFIED,
    VerificationResult,
    verify_quote,
)


def test_exact_containment_verified():
    src = "Cells exhibit aerobic glycolysis under hypoxia."
    res = verify_quote("aerobic glycolysis", [src])
    assert isinstance(res, VerificationResult)
    assert res.status == VERIFIED
    assert res.matched_index == 0
    assert res.quote_exact == "aerobic glycolysis"
    assert res.score == 1.0


def test_whitespace_flexible_match_across_newline():
    # Source wraps the quote across a newline + indentation; still verified,
    # and quote_exact is recovered with the source's ACTUAL whitespace.
    src = "the quick brown\n    fox jumps over"
    res = verify_quote("quick brown fox", [src])
    assert res.status == VERIFIED
    assert res.matched_index == 0
    assert res.quote_exact == "quick brown\n    fox"
    assert res.score == 1.0


def test_original_casing_preserved_in_quote_exact():
    src = "We observed that ATP Synthase activity increased."
    res = verify_quote("ATP Synthase activity", [src])
    assert res.status == VERIFIED
    assert res.quote_exact == "ATP Synthase activity"


def test_repaired_when_lcs_clears_threshold():
    quote = "the quick brown fox jumped"  # 26 normalized chars
    candidate = "the quick brown fox jumps over the lazy dog"
    # Longest common substring "the quick brown fox jump" = 24 chars -> 24/26 ~= 0.923 >= 0.9
    res = verify_quote(quote, [candidate])
    assert res.status == REPAIRED
    assert res.matched_index == 0
    assert res.quote_exact == "the quick brown fox jump"
    assert 0.9 <= res.score < 1.0


def test_just_below_threshold_is_unverified():
    quote = "alpha beta gamma delta"  # 22 chars
    candidate = "alpha beta and many other unrelated words entirely"
    # LCS "alpha beta " = 11 chars -> 11/22 = 0.5 < 0.9
    res = verify_quote(quote, [candidate])
    assert res.status == UNVERIFIED
    assert res.matched_index is None
    assert 0.0 < res.score < 0.9


def test_unverified_when_no_overlap():
    res = verify_quote(
        "mitochondria regulate calcium homeostasis",
        ["the weather today is sunny with a light breeze"],
    )
    assert res.status == UNVERIFIED
    assert res.matched_index is None
    assert res.quote_exact is None


def test_empty_quote_is_unverified_no_raise():
    res = verify_quote("", ["some source text"])
    assert res.status == UNVERIFIED
    assert res.matched_index is None
    assert res.score == 0.0


def test_empty_candidates_is_unverified():
    res = verify_quote("anything", [])
    assert res.status == UNVERIFIED


def test_exact_match_in_second_candidate_returns_index_1():
    res = verify_quote(
        "calcium signaling",
        ["unrelated text here", "calcium signaling cascade"],
    )
    assert res.status == VERIFIED
    assert res.matched_index == 1
    assert res.quote_exact == "calcium signaling"
