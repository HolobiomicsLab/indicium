"""Public pages name the ASB task card, not the retired SciTask identity.

The adapter module keeps its name, ``indicium.adapters.scitask``, so that existing
imports keep working. Any other mention of SciTask on a page a reader sees is stale:
ASB calls its cards task cards, and their schema is the public asb-schema package.
"""

import re
from pathlib import Path

import pytest

import indicium.adapters.scitask

ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PAGE = ROOT / "docs" / "adapters" / "scitask.md"
ADAPTER_MODULE = ROOT / "src" / "indicium" / "adapters" / "scitask.py"
# The legacy identifiers that stay: the module path and the page file name.
LEGACY_NAMES = re.compile(r"indicium\.adapters\.scitask|adapters/scitask\.md")


def reader_facing_files():
    yield ROOT / "README.md"
    yield ROOT / "mkdocs.yml"
    yield ADAPTER_MODULE
    docs = ROOT / "docs"
    for path in sorted(docs.rglob("*")):
        if path.is_file() and path.suffix in {".md", ".css"}:
            yield path


def test_scitask_appears_only_as_the_legacy_module_name():
    offenders = [
        f"{path.relative_to(ROOT)}:{number}"
        for path in reader_facing_files()
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if "scitask" in LEGACY_NAMES.sub("", line).lower()
    ]
    assert not offenders, offenders


@pytest.mark.parametrize(
    "text",
    [ADAPTER_PAGE.read_text(), indicium.adapters.scitask.__doc__],
    ids=["adapter page", "module docstring"],
)
def test_adapter_names_its_public_target_structure(text):
    assert "EvidenceSnippet" in text
    assert "asb-schema>=0.4.0" in text
    assert "not public" not in text
