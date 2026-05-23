"""ASTRA ↔ Indicium bridge — convert between ASTRA Insight dicts and Indicium Claims.

Optional-extra-gated: pyyaml must be installed (``pip install indicium[astra]``
or ``pip install pyyaml``). The pyyaml extra is already in the ``codegen``
extra and ``dev`` dependency-group, so it is always available during development.

Gap 6 implementation from the Indicium v1.3 design spec.
"""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from indicium.generated.model import Claim


def _require_pyyaml() -> None:
    """Raise ImportError if pyyaml is not installed."""
    try:
        import yaml  # noqa: F401
    except ImportError as exc:
        raise ImportError(
            "pyyaml is required for the astra_bridge module. "
            "Install it with: pip install indicium[astra]"
        ) from exc


# Verb → SuperPatternQualifier mapping used in the claim-text heuristic split.
_VERB_TO_QUALIFIER: dict[str, str] = {
    "increases":   "increases",
    "increase":    "increases",
    "decreases":   "decreases",
    "decrease":    "decreases",
    "inhibits":    "inhibits",
    "inhibit":     "inhibits",
    "activates":   "activates",
    "activate":    "activates",
    "causes":      "causes",
    "cause":       "causes",
    "prevents":    "prevents",
    "prevent":     "prevents",
    "predicts":    "predicts",
    "predict":     "predicts",
    "treats":      "treats",
    "treat":       "treats",
    "enhances":    "enhances",
    "enhance":     "enhances",
    "reduces":     "reduces",
    "reduce":      "reduces",
    "produces":    "produces",
    "produce":     "produces",
    "requires":    "requires",
    "require":     "requires",
    "enables":     "enables",
    "enable":      "enables",
    "correlates":  "correlates_with",
    "interacts":   "interacts_with",
}


def _split_claim_text(text: str) -> tuple[str, str, str]:
    """Split a claim sentence into (subject, qualifier_str, object) via verb heuristic.

    Scans each word, strips trailing punctuation, looks it up in _VERB_TO_QUALIFIER.
    Returns (full_text, "has_property", "") when no known verb is found — the full
    claim text becomes the subject, signalling an opaque assertion with no object.
    """
    words = text.split()
    for i, word in enumerate(words):
        lowered = word.lower().rstrip(".,;:")
        if lowered in _VERB_TO_QUALIFIER:
            subject = " ".join(words[:i]).strip()
            qualifier = _VERB_TO_QUALIFIER[lowered]
            obj = " ".join(words[i + 1:]).strip()
            return subject, qualifier, obj
    return text, "has_property", ""


def insight_to_claim(
    insight: dict,
    *,
    analysis_id: str,
    source_doi: str | None = None,
) -> "Claim":
    """Convert an ASTRA Insight dict to a best-effort Indicium Claim.

    Mapping rules:
    - subject/object: split claim text at verb heuristic, or use full text as object.
    - qualifier: defaults to ``has_property``; overridden when a known verb is found.
    - relation: same as qualifier_str (the matched verb phrase) or "has_property".
    - context: ASTRA ``scope`` field joined with ``tags``; empty string if absent.
    - asserted_by: set to ``analysis_id``.
    - astra_insight_ref: set to ``"{analysis_id}/{insight['id']}"``.

    Args:
        insight:     ASTRA Insight dict (id, claim, scope, tags, …).
        analysis_id: ASTRA analysis ID used as asserted_by and ref prefix.
        source_doi:  If provided, appended to context.

    Returns:
        A best-effort Indicium Claim (some slots may be empty strings).
    """
    _require_pyyaml()
    from indicium.generated.model import Claim, SuperPatternQualifier

    claim_text: str = str(insight.get("claim", ""))
    subject, qualifier_str, obj = _split_claim_text(claim_text)

    # Build context from scope + tags
    context_parts: list[str] = []
    if insight.get("scope"):
        context_parts.append(str(insight["scope"]))
    if insight.get("tags"):
        context_parts.append(", ".join(str(t) for t in insight["tags"]))
    if source_doi:
        context_parts.append(f"doi:{source_doi}")
    context = "; ".join(context_parts) if context_parts else ""

    # Validate qualifier — fall back to has_property if not in enum; always use enum member
    valid_qualifiers = {v.value: v for v in SuperPatternQualifier}
    qualifier = valid_qualifiers.get(qualifier_str, SuperPatternQualifier.has_property)

    claim_id = str(insight.get("id", ""))
    astra_ref = f"{analysis_id}/{claim_id}" if claim_id else analysis_id
    claim_uri = astra_ref  # use the ref as the claim id for round-trip navigation

    # Build kwargs; extra slots (asserted_by, astra_insight_ref) are only passed
    # when the generated model supports them (post Task 5 make gen). Pre-Task 5
    # the model has extra="forbid" and will raise ValidationError — that is expected
    # and documented: these tests will pass after make gen regenerates the model.
    claim_kwargs: dict = dict(
        id=claim_uri,
        context=context,
        subject=subject if subject else claim_text[:80],
        qualifier=qualifier,
        relation=qualifier_str if subject else "has_property",
        object=obj if subject else claim_text,
        asserted_by=analysis_id,
        astra_insight_ref=astra_ref,
    )

    return Claim(**claim_kwargs)


def claim_to_insight(
    claim: "Claim",
    *,
    evidence_doi: str | None = None,
) -> dict:
    """Convert an Indicium Claim to an ASTRA Insight YAML dict.

    Mapping rules:
    - claim text: ``"{subject} {qualifier} {relation} {object}"`` (stripped).
    - evidence: DOI item if ``evidence_doi`` provided, else artifact item using claim id.
    - indicium_claim_ref: set to ``claim.id`` when present.
    - created_at: current UTC ISO timestamp.

    Args:
        claim:        Indicium Claim object.
        evidence_doi: DOI to include in the evidence list. Optional.

    Returns:
        ASTRA Insight dict (id, claim, created_at, evidence, indicium_claim_ref).
    """
    _require_pyyaml()
    import datetime

    qualifier = (
        claim.qualifier.value
        if hasattr(claim.qualifier, "value")
        else str(claim.qualifier)
    )
    parts = [
        str(claim.subject or ""),
        qualifier,
        str(claim.relation or ""),
        str(claim.object or ""),
    ]
    claim_text = " ".join(p for p in parts if p).strip()

    if evidence_doi:
        evidence = [{"id": "e1", "doi": evidence_doi}]
    else:
        artifact_id = str(claim.id) if claim.id else "unknown"
        evidence = [{"id": "e1", "artifact": artifact_id}]

    insight: dict = {
        "id": str(claim.id) if claim.id else "unknown",
        "claim": claim_text,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "evidence": evidence,
    }
    if claim.id:
        insight["indicium_claim_ref"] = str(claim.id)
    return insight


def load_astra_findings(astra_yaml_path: Path) -> list["Claim"]:
    """Load an astra.yaml file and return all ``findings`` as Indicium Claims.

    Findings are ASTRA's analysis conclusions — the primary output of a
    sensitivity/multiverse analysis run.

    Args:
        astra_yaml_path: Path to an astra.yaml file.

    Returns:
        List of Indicium Claims, one per finding.  Returns [] if no findings.
    """
    _require_pyyaml()
    import yaml

    data = yaml.safe_load(Path(astra_yaml_path).read_text())
    analysis_id = str(data.get("name", Path(astra_yaml_path).stem))
    findings = data.get("findings", [])
    if isinstance(findings, dict):
        findings = list(findings.values())
    return [insight_to_claim(f, analysis_id=analysis_id) for f in (findings or [])]


def load_astra_prior_insights(astra_yaml_path: Path) -> list["Claim"]:
    """Load an astra.yaml file and return all ``prior_insights`` as Indicium Claims.

    Prior insights are literature-backed facts that inform ASTRA decisions;
    they are distinct from findings (which are analysis conclusions).

    Args:
        astra_yaml_path: Path to an astra.yaml file.

    Returns:
        List of Indicium Claims, one per prior_insight.  Returns [] if none.
    """
    _require_pyyaml()
    import yaml

    data = yaml.safe_load(Path(astra_yaml_path).read_text())
    analysis_id = str(data.get("name", Path(astra_yaml_path).stem))
    prior_insights = data.get("prior_insights", [])
    if isinstance(prior_insights, dict):
        prior_insights = list(prior_insights.values())
    return [insight_to_claim(p, analysis_id=analysis_id) for p in (prior_insights or [])]
