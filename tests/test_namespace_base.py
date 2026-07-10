"""Guard: the ``asb:`` vocabulary base must stay on a domain the lab owns.

Indicium 2.0.0 moved the base off ``asb.holobiomics.org``, which was never
registered — a third party could have taken it and served arbitrary definitions
for this standard's term IRIs. A stale reference in any shipped artefact would
mint IRIs under that unowned domain again, so both facts are asserted here.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "src" / "indicium" / "schema" / "indicium.yaml"
EXPECTED_BASE = "https://holobiomicslab.eu/ns/asb#"
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


def test_asb_prefix_uses_an_owned_domain() -> None:
    assert read_asb_prefix() == EXPECTED_BASE


def test_no_shipped_artefact_references_the_unowned_domain() -> None:
    assert find_files_referencing(UNOWNED_HOST) == []


if __name__ == "__main__":
    print("asb: prefix base =", read_asb_prefix())
    print("stale references =", find_files_referencing(UNOWNED_HOST) or "none")
