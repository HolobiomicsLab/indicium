import importlib.metadata

import indicium

# The distribution is `indicium-standard`; `indicium` is an unrelated PyPI
# package. test_namespace_base pins this name to the one pyproject declares.
DISTRIBUTION = "indicium-standard"


def test_version_matches_installed_metadata():
    assert indicium.__version__ == importlib.metadata.version(DISTRIBUTION)


if __name__ == "__main__":
    print("indicium.__version__ =", indicium.__version__)
