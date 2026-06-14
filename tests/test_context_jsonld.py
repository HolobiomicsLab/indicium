"""Validate the published JSON-LD @context."""
import json
from pathlib import Path

CONTEXT = Path(__file__).parents[1] / "docs/context.jsonld"


def test_context_file_exists():
    assert CONTEXT.exists(), "docs/context.jsonld missing"


def test_context_is_valid_json():
    json.loads(CONTEXT.read_text())


def test_context_declares_required_prefixes():
    ctx = json.loads(CONTEXT.read_text())["@context"]
    for prefix in ("indicium", "asb", "sepio", "eco", "cito", "doco", "fabio",
                   "dct", "prov", "edam"):
        assert prefix in ctx, f"missing prefix: {prefix}"


def test_context_maps_wave1_slots_by_name():
    ctx = json.loads(CONTEXT.read_text())["@context"]
    # Each spec-required slot name MUST appear as a top-level @context key
    # so JSON-LD consumers can use the short name directly.
    for slot in (
        "predicate", "super_pattern",
        "eco_code", "quote_exact", "quote_location", "supports_claim",
        "doi", "paragraph_id", "xpath_pointer",
        "canonical_url", "version", "edam_operation", "edam_topics", "bio_tools_id",
    ):
        assert slot in ctx, f"@context missing slot mapping: {slot}"


def test_context_maps_asserts_to_sepio_predicate():
    """The SEPIO `is asserted by` predicate (sepio:0000130) must be reachable
    via the short term `asserts`."""
    ctx = json.loads(CONTEXT.read_text())["@context"]
    assert "asserts" in ctx
    entry = ctx["asserts"]
    target = entry["@id"] if isinstance(entry, dict) else entry
    assert target == "sepio:0000130", f"asserts must map to sepio:0000130 (got {target})"


def test_context_is_loadable_via_importlib_resources():
    """The context.jsonld must ship inside the installable package so that
    downstream consumers (Scriptorium, etc.) can find it via
    `importlib.resources.files('indicium.schema') / 'context.jsonld'`."""
    from importlib import resources
    ref = resources.files("indicium.schema") / "context.jsonld"
    assert ref.is_file(), (
        "indicium.schema/context.jsonld is not packaged. "
        "It must live under src/indicium/schema/ so wheels include it."
    )
    import json
    payload = json.loads(ref.read_text())
    assert "@context" in payload
    assert payload["@context"]["asb"].startswith("https://holobiomicslab.eu")
