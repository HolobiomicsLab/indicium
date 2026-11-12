"""KGmemory-ready projection (latent). Points outward at mem:SemanticMemory.

We do NOT import, vendor, or modify KGmemory's vocabulary — we only reference
its canonical IRI so an emitted ASB Claim is ingestible if/when KGmemory adopts
it. The ECO->validationState crosswalk is intentionally NOT here (it is
KGmemory's seam to author).
"""
from __future__ import annotations

from indicium.iri_bindings import ASB_BASE

MEM_NS = "http://kgmemory.org/ns#"
# Kept as an adapter-local compatibility alias for callers that imported it
# directly before the projection was corrected to the canonical ASB vocabulary.
CLAIM_NS = ASB_BASE


def claim_jsonld(claim: dict) -> dict:
    return {
        "@id": f"urn:indicium:claim:{claim['id']}",
        "@type": [f"{CLAIM_NS}Claim", f"{MEM_NS}SemanticMemory"],
        f"{CLAIM_NS}context": claim["context"],
        f"{CLAIM_NS}subject": claim["subject"],
        f"{CLAIM_NS}qualifier": claim["qualifier"],
        f"{CLAIM_NS}relation": claim["relation"],
        f"{CLAIM_NS}object": claim["object"],
    }
