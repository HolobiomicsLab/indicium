"""indicium — shared claim/evidence standard package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("indicium")
except PackageNotFoundError:  # not installed (e.g. running from a raw checkout)
    __version__ = "0.0.0+unknown"

from indicium.validate import validate_graph
from indicium.verify import verify_quote, VerificationResult
from indicium.adapters.astra import claim_to_insight  # deprecated dict-based version; use astra_bridge.claim_to_insight for typed Claim objects
from indicium.adapters.kgmemory import claim_jsonld, MEM_NS
from indicium.adapters.scitask import claim_to_evidence_snippet
from indicium.generated.model import (
    # Core model classes
    Claim, Evidence, Source, CitationLink,
    # Core enums
    ClaimType, EvidenceType, SourceType, SuperPatternQualifier,
    # Figure extension (v1.1)
    Figure, FigureType,
    # Script + DataAsset (v1.2)
    Script, ScriptType, DataAsset, DatasetType,
    # v1.3 additions
    ClaimLink, LinkType, ClaimStatus,
    TextQuoteSelector, FragmentSelector,
    # v1.4 additions
    IndiciumDocument,
)
from indicium.iri_bindings import (
    FIGURE_TYPE_FABIO,
    SCRIPT_TYPE_IRI,
    DATASET_TYPE_IRI,
    KNOWN_REPOSITORIES,
    expand_curie,
    # v1.3 additions
    CLAIM_LINK_TYPE_CITO,
    parse_decision_context,
)

__all__ = [
    "validate_graph",
    "verify_quote",
    "VerificationResult",
    "claim_to_insight",  # deprecated; use from indicium.astra_bridge import claim_to_insight
    "claim_jsonld",
    "MEM_NS",
    "claim_to_evidence_snippet",
    # Core model classes
    "Claim",
    "Evidence",
    "Source",
    "CitationLink",
    # Core enums
    "ClaimType",
    "EvidenceType",
    "SourceType",
    "SuperPatternQualifier",
    # Figure extension (v1.1)
    "Figure",
    "FigureType",
    "FIGURE_TYPE_FABIO",
    # Script + DataAsset extension (v1.2)
    "Script",
    "ScriptType",
    "DataAsset",
    "DatasetType",
    "SCRIPT_TYPE_IRI",
    "DATASET_TYPE_IRI",
    "KNOWN_REPOSITORIES",
    "expand_curie",
    # ClaimLink + ClaimStatus + OA selectors (v1.3)
    "ClaimLink",
    "LinkType",
    "ClaimStatus",
    "TextQuoteSelector",
    "FragmentSelector",
    "CLAIM_LINK_TYPE_CITO",
    "parse_decision_context",
    # IndiciumDocument container (v1.4)
    "IndiciumDocument",
]
