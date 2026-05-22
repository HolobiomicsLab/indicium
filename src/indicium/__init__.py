"""indicium — shared claim/evidence standard package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("indicium")
except PackageNotFoundError:  # not installed (e.g. running from a raw checkout)
    __version__ = "0.0.0+unknown"

from indicium.validate import validate_graph
from indicium.adapters.astra import claim_to_insight
from indicium.adapters.kgmemory import claim_jsonld, MEM_NS

__all__ = ["validate_graph", "claim_to_insight", "claim_jsonld", "MEM_NS"]
