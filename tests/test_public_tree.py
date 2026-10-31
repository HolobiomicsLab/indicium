"""Files that ship or are published carry no local machine path.

The sdist holds ``src/``; the documentation site is built from ``docs/``; the tests,
the scripts and the top-level Markdown files are read by every contributor. None of
them should point at one maintainer's home directory.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LOCAL_PATHS = ("/" + "Users/", "~" + "/git/")
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".ttl", ".json", ".jsonld", ".cff", ".txt"}


def public_text_files():
    for top in ("src", "tests", "docs", "scripts"):
        for path in sorted((ROOT / top).rglob("*")):
            if path.is_file() and path.suffix in TEXT_SUFFIXES:
                yield path
    yield from sorted(ROOT.glob("*.md"))


@pytest.mark.parametrize("marker", LOCAL_PATHS)
def test_no_local_paths_in_public_files(marker):
    offenders = [
        str(path.relative_to(ROOT))
        for path in public_text_files()
        if marker in path.read_text(errors="replace")
    ]
    assert not offenders, offenders


def test_internal_plans_are_not_in_the_public_tree():
    assert not (ROOT / "docs" / "superpowers").exists()
