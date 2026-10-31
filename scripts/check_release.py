"""Check a release tag, version and changelog before building or publishing."""

import argparse
import datetime
import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def release_notes(root, tag, allow_unreleased=False):
    """Return matching notes; reject a mismatched tag or undated public release."""
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    version = project["version"]
    if project["name"] != "indicium-standard" or tag != f"v{version}":
        raise ValueError(f"Expected indicium-standard tag v{version}; got {tag}")
    changelog = (root / "CHANGELOG.md").read_text()
    if changelog != (root / "docs/changelog.md").read_text():
        raise ValueError("docs/changelog.md differs; run make docs-changelog")
    heading = re.search(rf"^## {re.escape(version)} — (\S+)\s*$", changelog, re.MULTILINE)
    if heading is None:
        raise ValueError(f"No changelog section for {version}")
    date = heading.group(1)
    if date != "YYYY-MM-DD" or not allow_unreleased:
        datetime.date.fromisoformat(date)
    notes = changelog[heading.end():].split("\n## ", 1)[0].strip().rstrip("-\n").strip()
    if not notes:
        raise ValueError("Release notes are empty")
    return notes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--allow-unreleased", action="store_true", help="Preparation only: allow the date placeholder")
    parser.add_argument("--notes-output", type=Path)
    args = parser.parse_args()
    try:
        notes = release_notes(ROOT, args.tag, args.allow_unreleased)
    except ValueError as error:
        parser.exit(1, f"Release check failed: {error}\n")
    if args.notes_output:
        args.notes_output.write_text(notes + "\n")
    print(f"Release metadata verified for {args.tag}")
