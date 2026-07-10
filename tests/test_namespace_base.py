"""Guard: the ``asb:`` vocabulary base must stay on the w3id.org permanent identifier.

Indicium moved the base onto ``https://w3id.org/asb#`` — an institution-independent
permanent-identifier redirect that no single lab has to own or keep renewing, so the
term IRIs survive any change of hosting or organisation. The previous base lived on
``asb.holobiomics.org``, which was never registered; a third party could have taken it
and served arbitrary definitions for this standard's term IRIs. A stale reference to
that unowned host in any shipped artefact would mint IRIs under it again, so both
facts — the expected base and the absence of the unowned host — are asserted here.

The same release renamed the distribution to ``indicium-standard``, so the
metadata lookup that populates ``__version__`` is pinned to that name too.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import indicium

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "src" / "indicium" / "schema" / "indicium.yaml"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
INIT_PATH = REPO_ROOT / "src" / "indicium" / "__init__.py"
EXPECTED_BASE = "https://w3id.org/asb#"
UNOWNED_HOST = "asb.holobiomics.org"
SCANNED_DIRS = ("src/indicium", "docs/schema-assets", "tests/fixtures")
TEXT_SUFFIXES = {".yaml", ".yml", ".json", ".jsonld", ".ttl", ".py", ".md"}


def read_asb_prefix() -> str:
    """Return the ``asb:`` prefix base declared in the LinkML schema."""
    match = re.search(r"^\s*asb:\s*(\S+)", SCHEMA_PATH.read_text(), re.MULTILINE)
    assert match, f"no asb: prefix declared in {SCHEMA_PATH}"
    return match.group(1)


def find_files_referencing(host: str) -> list[str]:
    """Return shipped files that still mention the given host."""
    hits = []
    for scanned in SCANNED_DIRS:
        for path in (REPO_ROOT / scanned).rglob("*"):
            if path.suffix not in TEXT_SUFFIXES:
                continue
            if host in path.read_text(errors="ignore"):
                hits.append(str(path.relative_to(REPO_ROOT)))
    return sorted(hits)


def read_distribution_name() -> str:
    """Return the distribution name declared in pyproject."""
    return tomllib.loads(PYPROJECT_PATH.read_text())["project"]["name"]


def test_asb_prefix_uses_an_owned_domain() -> None:
    assert read_asb_prefix() == EXPECTED_BASE


def test_no_shipped_artefact_references_the_unowned_domain() -> None:
    assert find_files_referencing(UNOWNED_HOST) == []


def test_exported_base_matches_the_schema() -> None:
    """Consumers import ASB_BASE; it must equal what the SHACL shapes target."""
    assert indicium.ASB_BASE == read_asb_prefix()


def test_asb_term_expands_against_the_exported_base() -> None:
    assert indicium.asb_term("Claim") == f"{EXPECTED_BASE}Claim"


def test_version_lookup_uses_the_declared_distribution_name() -> None:
    """A dist rename must update the metadata lookup, else __version__ reports
    the squatting `indicium` package's version instead of ours."""
    assert f'version("{read_distribution_name()}")' in INIT_PATH.read_text()


if __name__ == "__main__":
    print("asb: prefix base =", read_asb_prefix())
    print("exported ASB_BASE =", indicium.ASB_BASE)
    print("distribution      =", read_distribution_name())
    print("stale references  =", find_files_referencing(UNOWNED_HOST) or "none")
