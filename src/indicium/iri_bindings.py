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

# FaBiO — figure sub-type classification (FigureType enum meanings).
# All terms verified to exist in FaBiO 2.1 (http://purl.org/spar/fabio/).
FIGURE_TYPE_FABIO: dict[str, str] = {
    "data_plot":  "fabio:DataPlot",
    "graph":      "fabio:Graph",
    "photograph": "fabio:Photograph",
    "plate":      "fabio:Plate",
    "diagram":    "fabio:Diagram",
    "flowchart":  "fabio:Flowchart",
    "table":      "fabio:Table",
    "generic":    "fabio:Figure",
}

# FaBiO — script role classification (ScriptType enum meanings).
# All values map to fabio:ComputerProgram; the enum value carries the role.
SCRIPT_TYPE_IRI: dict[str, str] = {
    "analysis":      "fabio:ComputerProgram",
    "visualization": "fabio:ComputerProgram",
    "workflow":      "fabio:ComputerProgram",
    "notebook":      "fabio:ComputerProgram",
    "utility":       "fabio:ComputerProgram",
    "generic":       "fabio:ComputerProgram",
}

# DCAT — dataset content-type classification (DatasetType enum meanings).
# All values map to dcat:Dataset; the enum value carries the domain category.
DATASET_TYPE_IRI: dict[str, str] = {
    "tabular":     "dcat:Dataset",
    "sequence":    "dcat:Dataset",
    "spectral":    "dcat:Dataset",
    "image_stack": "dcat:Dataset",
    "network":     "dcat:Dataset",
    "model":       "dcat:Dataset",
    "generic":     "dcat:Dataset",
}

# Well-known data repository identifiers (for DataAsset.repository).
KNOWN_REPOSITORIES: dict[str, str] = {
    "geo":          "https://www.ncbi.nlm.nih.gov/geo/",
    "pride":        "https://www.ebi.ac.uk/pride/",
    "arrayexpress": "https://www.ebi.ac.uk/arrayexpress/",
    "zenodo":       "https://zenodo.org/",
    "figshare":     "https://figshare.com/",
    "dryad":        "https://datadryad.org/",
    "osf":          "https://osf.io/",
    "github":       "https://github.com/",
    "gitlab":       "https://gitlab.com/",
}

# ---------------------------------------------------------------------------
# CURIE expansion — used by Scriptorium and other consumers to build URIRefs
# ---------------------------------------------------------------------------

_ECO_BASE   = "http://purl.obolibrary.org/obo/ECO_"
_IAO_BASE   = "http://purl.obolibrary.org/obo/IAO_"
_DOCO_BASE  = "http://purl.org/spar/doco/"
_CITO_BASE  = "http://purl.org/spar/cito/"
_FABIO_BASE = "http://purl.org/spar/fabio/"
_DCAT_BASE  = "http://www.w3.org/ns/dcat#"

def expand_curie(curie: str) -> str:
    """Expand a short CURIE to a full IRI string.

    Supported prefixes: ECO, IAO, doco, cito, fabio, dcat.

    Examples::

        expand_curie("ECO:0000006")      # → "http://purl.obolibrary.org/obo/ECO_0000006"
        expand_curie("doco:Figure")      # → "http://purl.org/spar/doco/Figure"
        expand_curie("IAO:0000536")      # → "http://purl.obolibrary.org/obo/IAO_0000536"
        expand_curie("fabio:DataPlot")   # → "http://purl.org/spar/fabio/DataPlot"
        expand_curie("dcat:Dataset")     # → "http://www.w3.org/ns/dcat#Dataset"
    """
    if ":" not in curie:
        raise ValueError(f"Not a valid CURIE (missing ':'): {curie!r}")
    prefix, local = curie.split(":", 1)
    bases = {
        "ECO":   _ECO_BASE,
        "IAO":   _IAO_BASE,
        "doco":  _DOCO_BASE,
        "cito":  _CITO_BASE,
        "fabio": _FABIO_BASE,
        "dcat":  _DCAT_BASE,
    }
    if prefix not in bases:
        raise ValueError(
            f"Unknown CURIE prefix: {prefix!r}. Supported: {list(bases)}"
        )
    return bases[prefix] + local
