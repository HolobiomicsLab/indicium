"""Verified ontology IRIs for the indicium vocabularies.

Provenance: seeded from ASB semantic.py, then verified against EBI OLS4 / CiTO
(plan Task 2). Update here AND in the LinkML schema `meaning:` together.

Verification method
-------------------
ECO labels were fetched from:
  https://www.ebi.ac.uk/ols4/api/ontologies/eco/terms?iri=http://purl.obolibrary.org/obo/ECO_<id>
CiTO predicates were confirmed to resolve (HTTP 302 → 200) at:
  http://purl.org/spar/cito/<predicate>

Changes vs. ASB semantic.py
---------------------------
* citation:    ECO:0000305 → ECO:0000033
    Old label: "curator inference used in manual assertion" (wrong branch — this
    is under inferential/curator-inference, not literature citation).
    New label:  "author statement supported by traceable reference" — an author
    assertion whose support can be traced to a cited reference; this is the
    standard GO/ECO code for evidence derived from a published source.

* inference:   ECO:0000001 → ECO:0000361
    Old label: "inference from background scientific knowledge" — a leaf under
    ECO:0000205 (curator inference) → ECO:0000361.  It is too specific (curator
    only) and was incorrectly described in the task spec as the root.
    New label:  "inferential evidence" — the direct child of ECO:0000000 (root
    "evidence") that heads the entire inference/reasoning branch.  Using the
    upper-level branch term is correct for a vocabulary binding that must
    subsume all forms of computational, logical, and manual inference.

* speculation: ECO:0007672 → ECO:0000034
    Old label: "computational evidence" — entirely wrong; this is about
    computer-generated data, not hypothetical assertions.
    New label:  "author statement without traceable support" — an assertion not
    associated with results presented or a cited reference.  This is the
    closest available ECO upper-level term for a speculative/hypothetical claim.
    ECO does not have a dedicated "speculation" class; this is the best match.

All other terms (data, knowledge) are retained with confirmed labels.
"""
from __future__ import annotations

# ECO — evidence types.  Verified labels recorded inline.
# Root of the ECO hierarchy: ECO:0000000 "evidence" (is_root=True).
EVIDENCE_TYPE_ECO: dict[str, str] = {
    "data":        "ECO:0000006",   # experimental evidence
    "citation":    "ECO:0000033",   # author statement supported by traceable reference
    "knowledge":   "ECO:0000302",   # author statement used in manual assertion
    "inference":   "ECO:0000361",   # inferential evidence  (direct child of root; NOT ECO:0000001)
    "speculation": "ECO:0000034",   # author statement without traceable support
}

# CiTO — claim/citation relations.
# All four predicates confirmed: HTTP 302 → 200 at http://purl.org/spar/cito/<predicate>
LINK_TYPE_CITO: dict[str, str] = {
    "supports":            "cito:supports",
    "disputes":            "cito:disputes",
    "qualifies":           "cito:qualifies",
    "citesForInformation": "cito:citesForInformation",
}

# DoCO + IAO — source/document component types.
SOURCE_TYPE_IRI: dict[str, str] = {
    "text":   "IAO:0000311",   # publication
    "figure": "doco:Figure",
    "table":  "doco:Table",
    "image":  "IAO:0000536",   # image
}
