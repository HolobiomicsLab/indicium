"""Wave 1 slot-audit tests.

One failing test per spec-required slot / class / enum addition (see
docs/superpowers/plans/2026-05-24-indicium-slot-audit-wave1.md). Tests are
added FIRST (red), then the schema is updated (green).
"""
from pathlib import Path

import pytest
from linkml_runtime import SchemaView

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


@pytest.fixture(scope="module")
def sv() -> SchemaView:
    return SchemaView(str(SCHEMA))
