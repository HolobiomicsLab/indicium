"""Tests for Script, ScriptType, DataAsset, DatasetType, and extended Evidence."""
from pathlib import Path

import pytest
from linkml_runtime import SchemaView

from indicium.generated.model import (
    DataAsset,
    DatasetType,
    Evidence,
    EvidenceType,
    Script,
    ScriptType,
    Source,
    SourceType,
)
from indicium.iri_bindings import (
    DATASET_TYPE_IRI,
    KNOWN_REPOSITORIES,
    SCRIPT_TYPE_IRI,
    expand_curie,
)

SCHEMA = Path(__file__).parents[1] / "src/indicium/schema/indicium.yaml"


# ---------------------------------------------------------------------------
# Schema-level checks
# ---------------------------------------------------------------------------


def test_script_class_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("Script") is not None


def test_script_class_uri_is_fabio_computer_program():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("Script")
    assert str(cls.class_uri) == "fabio:ComputerProgram"


def test_script_type_enum_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_enum("ScriptType") is not None


def test_script_type_has_six_values():
    sv = SchemaView(str(SCHEMA))
    pv = sv.get_enum("ScriptType").permissible_values
    assert set(pv.keys()) == {
        "analysis", "visualization", "workflow", "notebook", "utility", "generic"
    }


def test_dataset_class_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_class("DataAsset") is not None


def test_dataset_class_uri_is_dcat():
    sv = SchemaView(str(SCHEMA))
    cls = sv.get_class("DataAsset")
    assert str(cls.class_uri) == "dcat:Dataset"


def test_dataset_type_enum_exists():
    sv = SchemaView(str(SCHEMA))
    assert sv.get_enum("DatasetType") is not None


def test_dataset_type_has_seven_values():
    sv = SchemaView(str(SCHEMA))
    pv = sv.get_enum("DatasetType").permissible_values
    assert set(pv.keys()) == {
        "tabular", "sequence", "spectral", "image_stack", "network", "model", "generic"
    }


def test_source_type_has_code_and_data():
    sv = SchemaView(str(SCHEMA))
    pv = sv.get_enum("SourceType").permissible_values
    assert "code" in pv
    assert "data" in pv


def test_evidence_has_of_script_and_of_dataset():
    sv = SchemaView(str(SCHEMA))
    slots = set(sv.class_slots("Evidence"))
    assert "of_script" in slots
    assert "of_dataset" in slots


def test_of_script_range_is_script():
    sv = SchemaView(str(SCHEMA))
    assert sv.induced_slot("of_script", "Evidence").range == "Script"


def test_of_dataset_range_is_dataset():
    sv = SchemaView(str(SCHEMA))
    assert sv.induced_slot("of_dataset", "Evidence").range == "DataAsset"


def test_script_identifier_is_optional():
    sv = SchemaView(str(SCHEMA))
    assert sv.induced_slot("identifier", "Script").required is not True


def test_dataset_identifier_is_optional():
    sv = SchemaView(str(SCHEMA))
    assert sv.induced_slot("identifier", "DataAsset").required is not True


# ---------------------------------------------------------------------------
# Pydantic model round-trips
# ---------------------------------------------------------------------------


def test_script_minimal():
    s = Script(script_id="script_s1", language="Python")
    assert s.script_id == "script_s1"
    assert s.script_type is None
    assert s.identifier is None


def test_script_full():
    s = Script(
        identifier="doi:10.1/p1#script1",
        script_id="Supplementary Script 1",
        script_type=ScriptType.analysis,
        language="Python",
        purpose="Compute differential abundance using DESeq2 wrapper.",
        repository_url="https://github.com/example/repo",
        content_url="https://github.com/example/repo/blob/main/analysis.py",
        commit_sha="a1b2c3d4",
        source_doi="10.1/p1",
        is_supplementary=True,
    )
    assert s.script_type == ScriptType.analysis
    assert s.commit_sha == "a1b2c3d4"
    assert s.is_supplementary is True


def test_script_type_all_values():
    for st in ScriptType:
        s = Script(script_id="x", script_type=st)
        assert s.script_type == st


def test_dataset_minimal():
    d = DataAsset(asset_id="dataset_s1")
    assert d.asset_id == "dataset_s1"
    assert d.dataset_type is None
    assert d.identifier is None


def test_dataset_full():
    d = DataAsset(
        identifier="https://zenodo.org/record/12345",
        asset_id="Supplementary Dataset 1",
        dataset_type=DatasetType.spectral,
        data_format="mzML",
        accession="10.5281/zenodo.12345",
        repository="zenodo",
        content_url="https://zenodo.org/record/12345/files/data.mzML",
        source_doi="10.1/p1",
        n_samples=120,
        is_supplementary=True,
    )
    assert d.dataset_type == DatasetType.spectral
    assert d.data_format == "mzML"
    assert d.n_samples == 120


def test_dataset_type_all_values():
    for dt in DatasetType:
        d = DataAsset(asset_id="x", dataset_type=dt)
        assert d.dataset_type == dt


def test_evidence_with_script():
    src = Source(identifier="doi:10.1/p1")
    scr = Script(
        script_id="Script S1",
        script_type=ScriptType.workflow,
        language="Snakemake",
        source_doi="10.1/p1",
    )
    ev = Evidence(
        evidence_type=EvidenceType.data,
        source_type=SourceType.code,
        quote="The pipeline was implemented as a Snakemake workflow (Script S1).",
        of_source=src,
        for_claim="claim-001",
        of_script=scr,
    )
    assert ev.of_script is not None
    assert ev.of_script.script_type == ScriptType.workflow
    assert ev.source_type == SourceType.code
    assert ev.of_figure is None
    assert ev.of_dataset is None


def test_evidence_with_dataset():
    src = Source(identifier="doi:10.1/p1")
    ds = DataAsset(
        asset_id="GEO:GSE123456",
        dataset_type=DatasetType.sequence,
        data_format="FASTQ",
        accession="GSE123456",
        repository="geo",
        source_doi="10.1/p1",
    )
    ev = Evidence(
        evidence_type=EvidenceType.data,
        source_type=SourceType.data,
        quote="Raw reads deposited in GEO under accession GSE123456.",
        of_source=src,
        for_claim="claim-002",
        of_dataset=ds,
    )
    assert ev.of_dataset is not None
    assert ev.of_dataset.dataset_type == DatasetType.sequence
    assert ev.source_type == SourceType.data
    assert ev.of_script is None


def test_evidence_backward_compat_no_script_or_dataset():
    """Existing Evidence records without of_script/of_dataset remain valid."""
    ev = Evidence(
        evidence_type=EvidenceType.citation,
        source_type=SourceType.text,
        of_source=Source(identifier="doi:10.2/p2"),
        for_claim="claim-003",
    )
    assert ev.of_script is None
    assert ev.of_dataset is None
    assert ev.of_figure is None


# ---------------------------------------------------------------------------
# IRI bindings
# ---------------------------------------------------------------------------


def test_script_type_iri_covers_all_values():
    for st in ScriptType:
        assert st.value in SCRIPT_TYPE_IRI, (
            f"ScriptType.{st.value} missing from SCRIPT_TYPE_IRI"
        )


def test_dataset_type_iri_covers_all_values():
    for dt in DatasetType:
        assert dt.value in DATASET_TYPE_IRI, (
            f"DatasetType.{dt.value} missing from DATASET_TYPE_IRI"
        )


def test_script_type_iri_values_are_fabio():
    for name, iri_curie in SCRIPT_TYPE_IRI.items():
        assert iri_curie == "fabio:ComputerProgram", (
            f"ScriptType.{name} should map to fabio:ComputerProgram, got {iri_curie!r}"
        )


def test_dataset_type_iri_values_are_dcat():
    for name, iri_curie in DATASET_TYPE_IRI.items():
        assert iri_curie == "dcat:Dataset", (
            f"DatasetType.{name} should map to dcat:Dataset, got {iri_curie!r}"
        )


def test_expand_curie_dcat():
    assert expand_curie("dcat:Dataset") == "http://www.w3.org/ns/dcat#Dataset"
    assert expand_curie("dcat:Distribution") == "http://www.w3.org/ns/dcat#Distribution"


def test_known_repositories_nonempty():
    assert len(KNOWN_REPOSITORIES) >= 5
    assert "geo" in KNOWN_REPOSITORIES
    assert "zenodo" in KNOWN_REPOSITORIES
    assert "pride" in KNOWN_REPOSITORIES


def test_source_type_code_and_data_expand():
    """SourceType.code and .data CURIEs must be expandable."""
    assert expand_curie("fabio:ComputerProgram").startswith("http://purl.org/spar/fabio/")
    assert expand_curie("dcat:Dataset").startswith("http://www.w3.org/ns/dcat#")
