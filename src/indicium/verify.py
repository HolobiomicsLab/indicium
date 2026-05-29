"""Quote verification kernel — match an LLM-extracted quote against source text.

Pure-Python, dependency-light, never raises. Shared across projects that ground
claims / parameters / failure-modes in source passages (Perspicacité, ASB).

Additive to the indicium standard: this module adds a *verifier verb* alongside
the existing data model (Evidence.quote_exact / TextQuoteSelector). It does NOT
touch generated/model.py, the SHACL shapes, or any enum.

VerificationResult also carries a `char_span` — (start, end) offsets into the
matched candidate's *original* (un-normalized) text — so callers can highlight or
re-slice the exact source region instead of re-searching for it.

`verify_quote(..., punctuation_flexible=True)` adds an opt-in pass that matches a
quote's alphanumeric tokens in order across arbitrary punctuation/whitespace
(e.g. "P=0.001" ~ "P = 0.001,"), so a verbatim-modulo-punctuation quote verifies
instead of degrading to a sub-threshold LCS. This mirrors ASB claim_ledger's
token-sequence matcher, letting both projects share one kernel.
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
_TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:\.[A-Za-z0-9]+)*")


def _normalize(text: str) -> str:
    """Collapse all whitespace runs to single spaces and strip ends."""
    return _WS_RE.sub(" ", text).strip()


@dataclass(frozen=True)
class VerificationResult:
    status: str               # "verified" | "repaired" | "unverified"
    matched_index: int | None  # index into candidates, or None
    quote_exact: str | None    # verbatim span recovered from the source candidate
    score: float               # 1.0 exact; lcs_len/len(norm_quote) for repaired; else best ratio
    char_span: tuple[int, int] | None = None  # (start, end) into candidates[matched_index], original offsets


def _verbatim_match(candidate: str, quote: str) -> "re.Match[str] | None":
    """Locate `quote` in `candidate` with flexible inter-token whitespace.

    A source may wrap a quote across newlines + indentation. Returns the regex
    match (caller reads `.group(0)` for the candidate's verbatim span — original
    casing + whitespace — and `.span()` for the original char offsets), or None.
    """
    tokens = quote.split()
    if not tokens:
        return None
    pattern = r"\s+".join(re.escape(tok) for tok in tokens)
    return re.search(pattern, candidate)


def _punct_flexible_span(candidate: str, quote: str) -> "tuple[int, int] | None":
    """Match the quote's alphanumeric tokens in order, separated by arbitrary
    non-alphanumeric padding, with per-token boundary guards so a token never
    latches onto a longer word. Returns (start, end) over the original
    candidate, or None. Mirrors ASB claim_ledger's token-sequence pass.
    """
    tokens = _TOKEN_RE.findall(quote)
    if not tokens:
        return None
    body = r"[^A-Za-z0-9]*".join(re.escape(t) + r"(?![A-Za-z0-9])" for t in tokens)
    m = re.search(r"(?<![A-Za-z0-9])" + body, candidate)
    return m.span() if m is not None else None


def _relocate(candidate: str, span_text: str) -> "tuple[int, int] | None":
    """Best-effort: re-find a (normalized) span back in the original candidate."""
    m = _verbatim_match(candidate, span_text)
    return m.span() if m is not None else None


def verify_quote(
    quote: str,
    candidates: Sequence[str],
    *,
    near_threshold: float = 0.9,
    punctuation_flexible: bool = False,
) -> VerificationResult:
    """Verify `quote` against `candidates` (source passage texts).

    Outcomes:
      - verified:   `quote` is contained in some candidate (whitespace-flexible,
                    case-sensitive). quote_exact = the candidate's verbatim span;
                    score = 1.0; char_span = (start, end) offsets into that
                    candidate's original text.
      - repaired:   no containment, but the longest common substring vs the best
                    candidate clears `near_threshold` (ratio over len(normalized
                    quote)). quote_exact = that LCS region from the candidate;
                    score = ratio; char_span best-effort (the normalized span is
                    re-located in the original candidate; may be None).
      - unverified: nothing clears the threshold (likely paraphrase/hallucination).
                    matched_index = quote_exact = char_span = None; score = best
                    below-threshold ratio (0.0 when quote/candidates are empty or
                    share no run).

    With `punctuation_flexible=True`, an opt-in pass between containment and LCS
    matches the quote's alphanumeric tokens in order across arbitrary punctuation
    (e.g. "P=0.001" ~ "P = 0.001,"); a hit is verified, score 1.0. Off by default
    so existing thresholds are unchanged.

    Never raises: empty/whitespace quote or empty candidates -> unverified.
    Ties resolved by highest score, then lowest index.
    """
    norm_quote = _normalize(quote or "")
    if not norm_quote or not candidates:
        return VerificationResult(UNVERIFIED, None, None, 0.0)

    # Coerce candidates defensively: a None/non-str can slip in when the kernel is
    # called directly by other projects. Map None -> "" so a degenerate entry
    # simply never matches, honoring the never-raises contract while keeping the
    # index alignment that matched_index depends on.
    cands = ["" if c is None else str(c) for c in candidates]

    # Pass 1 — exact (whitespace-flexible) containment. Use the normalized quote
    # so both passes operate on the same token form (the helper splits anyway).
    for i, cand in enumerate(cands):
        m = _verbatim_match(cand, norm_quote)
        if m is not None:
            return VerificationResult(VERIFIED, i, m.group(0), 1.0, m.span())

    # Pass 1.5 — punctuation-flexible token sequence (opt-in). A real verbatim
    # match modulo punctuation: "P=0.001" matches "P = 0.001,".
    if punctuation_flexible:
        for i, cand in enumerate(cands):
            span = _punct_flexible_span(cand, quote)
            if span is not None:
                s, e = span
                return VerificationResult(VERIFIED, i, cand[s:e], 1.0, span)

    # Pass 2 — longest common substring against each candidate.
    best_idx: int | None = None
    best_ratio = 0.0
    best_span: str | None = None
    for i, cand in enumerate(cands):
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
        char_span = _relocate(cands[best_idx], best_span) if best_span else None
        return VerificationResult(REPAIRED, best_idx, best_span, best_ratio, char_span)
    return VerificationResult(UNVERIFIED, None, None, best_ratio)
