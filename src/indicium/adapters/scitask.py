"""Project an indicium Claim onto the EvidenceSnippet dict of an ASB task card.

The target structure is the ``EvidenceSnippet`` class of the ASB task card schema,
``asb_schema/asb_card.yaml`` in the asb-schema package (``asb-schema>=0.4.0``). Its
fields are snippet_id, source_path, reason and text. The module keeps its earlier
name, ``indicium.adapters.scitask``, so that existing imports keep working.
"""
from __future__ import annotations


def claim_to_evidence_snippet(claim: dict, source_path: str = "") -> dict:
    """Map an Indicium Claim dict to an ASB task card EvidenceSnippet dict.

    Args:
        claim: An Indicium claim dict with at minimum: id, context, subject,
               qualifier, relation, object. Optional: source_excerpt, evidence.
        source_path: Explicit source path override. When omitted, the first
                     evidence artifact path is used; falls back to doi:<doi>.

    Returns:
        A dict with snippet_id, source_path, reason and text, the required
        fields of an EvidenceSnippet.
    """
    # Resolve source_path from evidence if not supplied
    if not source_path:
        for ev in claim.get("evidence", []):
            if ev.get("artifact"):
                source_path = ev["artifact"]
                break
            elif ev.get("doi"):
                source_path = f"doi:{ev['doi']}"
                break

    # Resolve text from source_excerpt, then evidence quotes
    text = claim.get("source_excerpt", "")
    if not text:
        for ev in claim.get("evidence", []):
            if ev.get("quote"):
                text = ev["quote"]
                break

    # Build a human-readable reason from the 5-slot SuperPattern.
    # qualifier is the controlled-vocab term (e.g. "inhibits"); relation is the
    # free-text elaboration (e.g. "inhibits growth of").  We bracket the qualifier
    # so they read distinctly rather than "inhibits inhibits growth of".
    reason = (
        f"{claim['subject']} [{claim['qualifier']}] {claim['relation']} "
        f"{claim['object']} (context: {claim['context']})"
    )

    return {
        "snippet_id": claim["id"],
        "source_path": source_path,
        "reason": reason,
        "text": text,
    }
