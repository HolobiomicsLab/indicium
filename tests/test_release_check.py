"""Release metadata must stop mismatched or undated publication."""

import runpy
from pathlib import Path

import pytest

CHECK = runpy.run_path(str(Path(__file__).parents[1] / "scripts/check_release.py"))["release_notes"]


@pytest.fixture
def release_root(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "indicium-standard"\nversion = "2.0.0"\n')
    notes = "# Changelog\n\n## 2.0.0 — 2026-09-14\n\nFirst public release.\n"
    (tmp_path / "CHANGELOG.md").write_text(notes)
    (tmp_path / "docs/changelog.md").write_text(notes)
    return tmp_path


def test_dated_matching_release_passes(release_root):
    assert CHECK(release_root, "v2.0.0") == "First public release."


def test_mismatched_tag_is_rejected(release_root):
    with pytest.raises(ValueError, match="Expected indicium-standard tag v2.0.0"):
        CHECK(release_root, "v2.1.0")


def test_placeholder_requires_explicit_preparation_mode(release_root):
    for path in [release_root / "CHANGELOG.md", release_root / "docs/changelog.md"]:
        path.write_text(path.read_text().replace("2026-09-14", "YYYY-MM-DD"))
    with pytest.raises(ValueError):
        CHECK(release_root, "v2.0.0")
    assert CHECK(release_root, "v2.0.0", allow_unreleased=True)


def test_stale_documentation_changelog_is_rejected(release_root):
    (release_root / "docs/changelog.md").write_text("stale")
    with pytest.raises(ValueError, match="differs"):
        CHECK(release_root, "v2.0.0")
