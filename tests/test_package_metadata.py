"""The PyPI metadata of indicium-standard is complete; PyPI freezes it per version."""

import re
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = tomllib.loads((ROOT / "pyproject.toml").read_text())
PROJECT = PYPROJECT["project"]


def test_licence_is_an_spdx_expression_with_its_file():
    assert PROJECT["license"] == "MIT"
    assert PROJECT["license-files"] == ["LICENSE"]
    assert not [c for c in PROJECT["classifiers"] if c.startswith("License ::")]


def test_build_backend_supports_license_expressions():
    assert "hatchling>=1.27" in PYPROJECT["build-system"]["requires"]


def test_an_author_with_an_email_is_declared():
    assert PROJECT["authors"]
    assert all(author.get("name") and author.get("email") for author in PROJECT["authors"])


def test_project_urls_include_documentation_and_issues():
    urls = PROJECT["urls"]
    for key in ("Homepage", "Documentation", "Repository", "Issues", "Changelog"):
        assert urls.get(key, "").startswith("https://"), key


def test_classifiers_claim_exactly_the_python_versions_ci_tests():
    ci = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yml").read_text())
    tested = ci["jobs"]["test"]["strategy"]["matrix"]["python-version"]
    claimed = [
        classifier.rsplit(" :: ", 1)[1]
        for classifier in PROJECT["classifiers"]
        if re.fullmatch(r"Programming Language :: Python :: 3\.\d+", classifier)
    ]
    assert sorted(claimed) == sorted(tested)
    oldest = min(tested, key=lambda version: tuple(map(int, version.split("."))))
    assert PROJECT["requires-python"] == f">={oldest}"
