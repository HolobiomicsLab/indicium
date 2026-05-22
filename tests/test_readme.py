from pathlib import Path

README = Path(__file__).parents[1] / "README.md"


def test_readme_records_name_and_role():
    text = README.read_text()
    # The naming rationale must be preserved.
    assert "points to the truth" in text
    assert "indicia" in text
    # The ecosystem positioning must be preserved.
    for sibling in ("ASTRA", "KGmemory", "ECO"):
        assert sibling in text
