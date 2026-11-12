"""Keep hand-written schema documentation aligned with generated artefacts."""

from __future__ import annotations

import inspect
import re
from collections import Counter
from collections.abc import Iterable
from enum import Enum
from pathlib import Path

import rdflib

import indicium

ROOT = Path(__file__).resolve().parents[1]
API_REFERENCE = ROOT / "docs/api-reference.md"
EVIDENCE_DOC = ROOT / "docs/schema/evidence.md"
URI_SCHEME = ROOT / "docs/uri-scheme.md"
SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")
INDICIUM_BASE = "https://w3id.org/indicium/"
ASB_BASE = "https://w3id.org/asb#"
SHAPE_ROW = re.compile(
    r"^\| `(?P<path>[^`]+\.ttl)` \| (?P<statements>\d+) \| "
    r"(?P<indicium>\d+) \| (?P<asb>\d+) \| (?P<other>\d+) \| "
    r"(?P<distinct>\d+) \| (?P<distinct_indicium>\d+) \| "
    r"(?P<distinct_asb>\d+) \| (?P<distinct_other>\d+) \|$",
    re.MULTILINE,
)


def _public_types() -> dict[str, type]:
    return {
        name: value
        for name in indicium.__all__
        if inspect.isclass(value := getattr(indicium, name))
    }


def _documented_enum_values(enum_name: str) -> set[str]:
    text = EVIDENCE_DOC.read_text()
    section = text.split(f"### {enum_name}", 1)[1].split("\n##", 1)[0]
    return set(re.findall(r"^\| `([^`]+)` \|", section, re.MULTILINE))


def _shape_path_counts(path: Path) -> tuple[int, ...]:
    graph = rdflib.Graph().parse(path, format="turtle")
    paths = list(graph.objects(None, SH.path))
    occurrences = _namespace_counts(paths)
    distinct = _namespace_counts(set(paths))
    return occurrences + distinct


def _namespace_counts(paths: Iterable[object]) -> tuple[int, int, int, int]:
    prefixes = Counter(_path_namespace(str(value)) for value in paths)
    return (
        sum(prefixes.values()),
        prefixes["indicium"],
        prefixes["asb"],
        prefixes["other"],
    )


def _path_namespace(value: str) -> str:
    if value.startswith(INDICIUM_BASE):
        return "indicium"
    if value.startswith(ASB_BASE):
        return "asb"
    return "other"


def test_api_reference_lists_every_public_class_and_enum() -> None:
    """Every class exported from the package root is in the API member list."""
    api_reference = API_REFERENCE.read_text()
    missing = [
        name
        for name in _public_types()
        if f"        - {name}\n" not in api_reference
    ]
    assert not missing, f"Public types missing from API reference: {missing}"


def test_evidence_page_lists_current_source_and_link_types() -> None:
    """The two hand-written enum tables exactly match their runtime enums."""
    for enum_type in (indicium.SourceType, indicium.LinkType):
        assert issubclass(enum_type, Enum)
        expected = {member.value for member in enum_type}
        assert _documented_enum_values(enum_type.__name__) == expected


def test_uri_scheme_counts_match_both_shapes_graphs() -> None:
    """Documented path counts come from the generated and published graphs."""
    count_fields = (
        "statements", "indicium", "asb", "other", "distinct",
        "distinct_indicium", "distinct_asb", "distinct_other",
    )
    documented = {
        match["path"]: tuple(int(match[name]) for name in count_fields)
        for match in SHAPE_ROW.finditer(URI_SCHEME.read_text())
    }
    expected = {
        relative: _shape_path_counts(ROOT / relative)
        for relative in (
            "src/indicium/generated/shapes.ttl",
            "docs/schema-assets/indicium.shapes.ttl",
        )
    }
    assert documented == expected
