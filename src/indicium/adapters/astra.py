"""Project an indicium Claim onto an ASTRA Insight (lossy — claim becomes a string).

ASTRA Insight = {id, claim (str), evidence: [{doi|artifact, quote:{exact}}]}.
The 5-slot SuperPattern is flattened into the claim string; full typing is
preserved in the RDF/RO-Crate forms, not here.
"""
from __future__ import annotations


def _claim_string(c: dict) -> str:
    return f'{c["subject"]} {c["relation"]} {c["object"]} ({c["context"]})'


def claim_to_insight(claim: dict) -> dict:
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
