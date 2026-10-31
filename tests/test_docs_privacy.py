"""The documentation site fetches no font from a third-party host.

mkdocs-material loads Google Fonts on every page unless ``theme.font`` is false,
and an ``@import`` of a font stylesheet does the same; either one sends each
visitor's IP address to Google. The site uses the fonts installed on the visitor's
system instead.
"""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REMOTE_FONT_HOSTS = re.compile(r"fonts\.googleapis\.com|fonts\.gstatic\.com")
REMOTE_IMPORT = re.compile(r"@import\s+(url\()?\s*['\"]?(https?:)?//", re.IGNORECASE)


def test_theme_does_not_load_google_fonts():
    config = yaml.safe_load((ROOT / "mkdocs.yml").read_text())
    assert config["theme"].get("font") is False


def test_site_stylesheets_import_nothing_remote():
    offenders = [
        str(path.relative_to(ROOT))
        for path in sorted((ROOT / "docs").rglob("*.css"))
        if REMOTE_FONT_HOSTS.search(text := path.read_text()) or REMOTE_IMPORT.search(text)
    ]
    assert not offenders, offenders
