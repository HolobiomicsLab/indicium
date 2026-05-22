import importlib.metadata

import indicium


def test_version_matches_installed_metadata():
    assert indicium.__version__ == importlib.metadata.version("indicium")
