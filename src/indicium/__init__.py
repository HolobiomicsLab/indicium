"""indicium — shared claim/evidence standard package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("indicium")
except PackageNotFoundError:  # not installed (e.g. running from a raw checkout)
    __version__ = "0.0.0+unknown"
