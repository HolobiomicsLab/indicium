"""Quote verification kernel — match an LLM-extracted quote against source text.

Pure-Python, dependency-light, never raises. Shared across projects that ground
claims / parameters / failure-modes in source passages (Perspicacité, ASB).

Additive to the indicium standard: this module adds a *verifier verb* alongside
the existing data model (Evidence.quote_exact / TextQuoteSelector). It does NOT
touch generated/model.py, the SHACL shapes, or any enum.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Sequence

VERIFIED = "verified"
REPAIRED = "repaired"
UNVERIFIED = "unverified"

_WS_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
    """Collapse all whitespace runs to single spaces and strip ends."""
    return _WS_RE.sub(" ", text).strip()


@dataclass(frozen=True)
class VerificationResult:
    status: str               # "verified" | "repaired" | "unverified"
    matched_index: int | None  # index into candidates, or None
    quote_exact: str | None    # verbatim span recovered from the source candidate
    score: float               # 1.0 exact; lcs_len/len(norm_quote) for repaired; else best ratio


def _verbatim_span(candidate: str, quote: str) -> str | None:
    """Find `quote` inside `candidate` allowing flexible whitespace between
    tokens (a source may wrap a quote across newlines). Returns the span exactly
    as it appears in `candidate` (original casing + whitespace), or None.
    """
    tokens = quote.split()
    if not tokens:
        return None
    pattern = r"\s+".join(re.escape(tok) for tok in tokens)
    m = re.search(pattern, candidate)
    return m.group(0) if m is not None else None


def verify_quote(
    quote: str,
    candidates: Sequence[str],
    *,
    near_threshold: float = 0.9,
) -> VerificationResult:
    """Verify `quote` against `candidates` (source passage texts).

    Outcomes:
      - verified:   `quote` is contained in some candidate (whitespace-flexible,
                    case-sensitive). quote_exact = the candidate's verbatim span;
                    score = 1.0.
      - repaired:   no containment, but the longest common substring vs the best
                    candidate clears `near_threshold` (ratio over len(normalized
                    quote)). quote_exact = that LCS region from the candidate;
                    score = ratio.
      - unverified: nothing clears the threshold (likely paraphrase/hallucination).
                    matched_index = quote_exact = None; score = best below-threshold
                    ratio found (0.0 when quote/candidates are empty or share no run).

    Never raises: empty/whitespace quote or empty candidates -> unverified.
    Ties resolved by highest score, then lowest index.
    """
    norm_quote = _normalize(quote or "")
    if not norm_quote or not candidates:
        return VerificationResult(UNVERIFIED, None, None, 0.0)

    # Pass 1 — exact (whitespace-flexible) containment. Use the normalized quote
    # so both passes operate on the same token form (the helper splits anyway).
    for i, cand in enumerate(candidates):
        span = _verbatim_span(cand, norm_quote)
        if span is not None:
            return VerificationResult(VERIFIED, i, span, 1.0)

    # Pass 2 — longest common substring against each candidate.
    best_idx: int | None = None
    best_ratio = 0.0
    best_span: str | None = None
    for i, cand in enumerate(candidates):
        norm_cand = _normalize(cand)
        if not norm_cand:
            continue
        sm = SequenceMatcher(None, norm_quote, norm_cand, autojunk=False)
        block = sm.find_longest_match(0, len(norm_quote), 0, len(norm_cand))
        if block.size == 0:
            continue
        ratio = block.size / len(norm_quote)
        if ratio > best_ratio:
            best_idx = i
            best_ratio = ratio
            best_span = norm_cand[block.b : block.b + block.size]

    if best_idx is not None and best_ratio >= near_threshold:
        return VerificationResult(REPAIRED, best_idx, best_span, best_ratio)
    return VerificationResult(UNVERIFIED, None, None, best_ratio)
