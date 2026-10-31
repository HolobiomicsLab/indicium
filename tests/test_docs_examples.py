"""The Python examples in the README and the docs must run and print what they say.

Every fenced ``python`` block of a page runs, in page order, in one namespace, so a
later block can use a name an earlier block defined. A line of the form
``print(...)  # expected`` declares the line it prints; the printed lines of the
page must equal those declarations, in order. A page that drifts from the API fails
here instead of misleading a reader.
"""

from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
PAGES = ("README.md", "docs/index.md", "docs/quickstart.md", "docs/uri-scheme.md")
FENCE = re.compile(r"^```python\n(.*?)^```", re.MULTILINE | re.DOTALL)
DECLARED = re.compile(r"^\s*print\(.*\)\s+#\s?(.*)$")


def python_blocks(page: Path) -> list[str]:
    """Return the fenced python blocks of a Markdown page, in order."""
    return FENCE.findall(page.read_text())


def declared_output(blocks: list[str]) -> list[str]:
    """Return the output lines the print comments of the blocks declare."""
    return [
        match.group(1).strip()
        for block in blocks
        for line in block.splitlines()
        if (match := DECLARED.match(line))
    ]


@pytest.mark.parametrize("relative", PAGES)
def test_page_examples_run_and_print_what_they_declare(relative: str) -> None:
    page = REPO_ROOT / relative
    blocks = python_blocks(page)
    assert blocks, f"{relative} has no python example"

    namespace: dict = {"__name__": f"example:{relative}"}
    captured = io.StringIO()
    with contextlib.redirect_stdout(captured):
        for index, block in enumerate(blocks):
            exec(compile(block, f"{relative}[python block {index}]", "exec"), namespace)

    printed = [line.strip() for line in captured.getvalue().splitlines()]
    assert printed == declared_output(blocks)
