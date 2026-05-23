"""Project an indicium Claim onto an ASTRA Insight (lossy — claim becomes a string).

ASTRA Insight = {id, claim (str), evidence: [{doi|artifact, quote:{exact}}]}.
The 5-slot SuperPattern is flattened into the claim string; full typing is
preserved in the RDF/RO-Crate forms, not here.
"""
from __future__ import annotations

import warnings


def _claim_string(c: dict) -> str:
    return f'{c["subject"]} {c["relation"]} {c["object"]} ({c["context"]})'


def claim_to_insight(claim: dict) -> dict:
    """Project an indicium Claim dict onto an ASTRA Insight dict (lossy).

    .. deprecated::
        Use ``indicium.astra_bridge.claim_to_insight(claim: Claim, ...)`` instead.
        This function takes a raw dict and will be removed in a future version.
    """
    warnings.warn(
        "indicium.adapters.astra.claim_to_insight() is deprecated. "
        "Use indicium.astra_bridge.claim_to_insight(claim: Claim, ...) instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    insight: dict = {"id": claim["id"], "claim": _claim_string(claim)}
    ev_out = []
    for ev in claim.get("evidence", []):
        node: dict = {}
        if ev.get("doi"):
            node["doi"] = ev["doi"]
        elif ev.get("artifact"):
            node["artifact"] = ev["artifact"]
        else:
            continue  # ASTRA evidence needs doi or artifact; skip otherwise
        if ev.get("quote"):
            node["quote"] = {"exact": ev["quote"]}
        ev_out.append(node)
    if ev_out:
        insight["evidence"] = ev_out
    return insight
