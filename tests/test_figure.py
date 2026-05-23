"""Tests for the Figure class, FigureType enum, and Evidence.of_figure slot."""
from pathlib import Path

import pytest
from linkml_runtime import SchemaView

from indicium.generated.model import (
    Claim,
    Evidence,
    EvidenceType,
    Figure,
    FigureType,
    Source,
    SourceType,
    SuperPatternQualifier,
)
from indicium.iri_bindings import FIGURE_TYPE_FABIO, expand_curie

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


# ---------------------------------------------------------------------------
# Schema-level checks (via SchemaView)
# ---------------------------------------------------------------------------


def test_figure_class_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("Figure") is not None


def test_figure_class_uri_is_doco():
    sv = SchemaView(str(SCHEMA))
    fig = sv.get_class("Figure")
    assert str(fig.class_uri) == "doco:Figure"


def test_figure_type_enum_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_enum("FigureType") is not None


def test_figure_type_has_eight_values():
    sv = SchemaView(str(SCHEMA))
    pv = sv.get_enum("FigureType").permissible_values
    assert set(pv.keys()) == {
        "data_plot", "graph", "photograph", "plate",
        "diagram", "flowchart", "table", "generic",
    }


def test_figure_type_meanings_are_fabio():
    sv = SchemaView(str(SCHEMA))
    pv = sv.get_enum("FigureType").permissible_values
    for name, val in pv.items():
        assert str(val.meaning).startswith("fabio:"), (
            f"FigureType.{name} meaning should start with 'fabio:'; got {val.meaning!r}"
        )


def test_figure_identifier_is_optional():
    sv = SchemaView(str(SCHEMA))
    induced = sv.induced_slot("identifier", "Figure")
    # slot_usage overrides required to false for Figure
    assert induced.required is not True


def test_evidence_has_of_figure_slot():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Evidence"))
    assert "of_figure" in slots


def test_of_figure_range_is_figure():
    sv = SchemaView(str(SCHEMA))
    slot = sv.induced_slot("of_figure", "Evidence")
    assert slot.range == "Figure"


# ---------------------------------------------------------------------------
# Pydantic model round-trip
# ---------------------------------------------------------------------------


def test_figure_model_minimal():
    fig = Figure(figure_id="fig3a", caption="Dose-response curve.")
    assert fig.figure_id == "fig3a"
    assert fig.figure_type is None
    assert fig.identifier is None


def test_figure_model_full():
    fig = Figure(
        identifier="doi:10.1/p1#fig3a",
        figure_id="Fig 3A",
        caption="Confocal images of compound X treatment.",
        figure_type=FigureType.plate,
        panel_label="A",
        page=4,
        media_type="image/png",
        content_url="https://example.org/figures/fig3a.png",
        source_doi="10.1/p1",
        is_supplementary=False,
    )
    assert fig.figure_type == FigureType.plate
    assert fig.panel_label == "A"
    assert fig.content_url == "https://example.org/figures/fig3a.png"


def test_figure_type_values():
    for ft in FigureType:
        # Each enum value should round-trip through string comparison
        fig = Figure(figure_id="x", figure_type=ft)
        assert fig.figure_type == ft


def test_evidence_with_figure():
    src = Source(identifier="doi:10.1/p1")
    fig = Figure(
        identifier="doi:10.1/p1#fig2",
        figure_id="Fig 2",
        caption="Bar chart of efficacy.",
        figure_type=FigureType.data_plot,
        source_doi="10.1/p1",
    )
    claim_id = "claim-001"
    ev = Evidence(
        evidence_type=EvidenceType.data,
        source_type=SourceType.figure,
        quote="Fig 2 shows a statistically significant increase.",
        of_source=src,
        for_claim=claim_id,
        of_figure=fig,
    )
    assert ev.of_figure is not None
    assert ev.of_figure.figure_type == FigureType.data_plot
    assert ev.source_type == SourceType.figure


def test_evidence_without_figure_is_valid():
    """Backward compat: of_figure is optional; existing Evidence records still valid."""
    ev = Evidence(
        evidence_type=EvidenceType.citation,
        source_type=SourceType.text,
        quote="As reported by Smith et al.",
        of_source=Source(identifier="doi:10.2/p2"),
        for_claim="claim-002",
    )
    assert ev.of_figure is None


# ---------------------------------------------------------------------------
# IRI bindings
# ---------------------------------------------------------------------------


def test_figure_type_fabio_dict_complete():
    """FIGURE_TYPE_FABIO covers all FigureType enum values."""
    for ft in FigureType:
        assert ft.value in FIGURE_TYPE_FABIO, (
            f"FigureType.{ft.value} missing from FIGURE_TYPE_FABIO"
        )


def test_expand_curie_fabio():
    assert expand_curie("fabio:DataPlot") == "http://purl.org/spar/fabio/DataPlot"
    assert expand_curie("fabio:Plate") == "http://purl.org/spar/fabio/Plate"
    assert expand_curie("fabio:Figure") == "http://purl.org/spar/fabio/Figure"


def test_expand_curie_fabio_all_figure_types():
    for name, curie in FIGURE_TYPE_FABIO.items():
        iri = expand_curie(curie)
        assert iri.startswith("http://purl.org/spar/fabio/"), (
            f"FigureType.{name} → {curie} → {iri} does not expand to fabio base"
        )
