from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = False,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'indicium',
     'default_range': 'string',
     'description': 'Shared claim/evidence standard — '
                    'ECO/CiTO/DoCO/FaBiO/SEPIO/PROV-O + Bucur SuperPattern.',
     'id': 'https://w3id.org/indicium',
     'imports': ['linkml:types'],
     'name': 'indicium',
     'prefixes': {'ECO': {'prefix_prefix': 'ECO',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/ECO_'},
                  'IAO': {'prefix_prefix': 'IAO',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/IAO_'},
                  'asb': {'prefix_prefix': 'asb',
                          'prefix_reference': 'https://asb.holobiomics.org/ns/asb#'},
                  'cito': {'prefix_prefix': 'cito',
                           'prefix_reference': 'http://purl.org/spar/cito/'},
                  'dcat': {'prefix_prefix': 'dcat',
                           'prefix_reference': 'http://www.w3.org/ns/dcat#'},
                  'dct': {'prefix_prefix': 'dct',
                          'prefix_reference': 'http://purl.org/dc/terms/'},
                  'doco': {'prefix_prefix': 'doco',
                           'prefix_reference': 'http://purl.org/spar/doco/'},
                  'fabio': {'prefix_prefix': 'fabio',
                            'prefix_reference': 'http://purl.org/spar/fabio/'},
                  'indicium': {'prefix_prefix': 'indicium',
                               'prefix_reference': 'https://w3id.org/indicium/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'oa': {'prefix_prefix': 'oa',
                         'prefix_reference': 'http://www.w3.org/ns/oa#'},
                  'prov': {'prefix_prefix': 'prov',
                           'prefix_reference': 'http://www.w3.org/ns/prov#'},
                  'sepio': {'prefix_prefix': 'sepio',
                            'prefix_reference': 'http://purl.obolibrary.org/obo/SEPIO_'}},
     'source_file': 'src/indicium/schema/indicium.yaml'} )

class ClaimType(str, Enum):
    explicit = "explicit"
    implicit = "implicit"


class SuperPatternQualifier(str, Enum):
    """
    20-term Bucur et al. (K-CAP 2021) qualifier vocabulary.
    """
    causes = "causes"
    prevents = "prevents"
    inhibits = "inhibits"
    activates = "activates"
    increases = "increases"
    decreases = "decreases"
    correlates_with = "correlates_with"
    is_associated_with = "is_associated_with"
    predicts = "predicts"
    interacts_with = "interacts_with"
    produces = "produces"
    requires = "requires"
    enables = "enables"
    treats = "treats"
    enhances = "enhances"
    reduces = "reduces"
    has_property = "has_property"
    is_part_of = "is_part_of"
    is_a = "is_a"
    consistent_with = "consistent_with"


class EvidenceType(str, Enum):
    data = "data"
    citation = "citation"
    knowledge = "knowledge"
    inference = "inference"
    speculation = "speculation"


class SourceType(str, Enum):
    text = "text"
    figure = "figure"
    table = "table"
    image = "image"
    code = "code"
    data = "data"


class ClaimStatus(str, Enum):
    """
    Lifecycle state of a Claim.
    """
    draft = "draft"
    verified = "verified"
    published = "published"
    retracted = "retracted"
    superseded = "superseded"


class LinkType(str, Enum):
    supports = "supports"
    disputes = "disputes"
    qualifies = "qualifies"
    citesForInformation = "citesForInformation"
    contradicts = "contradicts"
    refines = "refines"
    extends = "extends"
    agreesWith = "agreesWith"
    disagreesWith = "disagreesWith"
    updates = "updates"
    corrects = "corrects"
    usesDataFrom = "usesDataFrom"
    usesMethodIn = "usesMethodIn"


class FigureType(str, Enum):
    """
    FaBiO-aligned classification of figure and display item types found in scholarly publications. Values map to FaBiO sub-classes of fabio:Figure and fabio:Table.
    """
    data_plot = "data_plot"
    graph = "graph"
    photograph = "photograph"
    plate = "plate"
    diagram = "diagram"
    flowchart = "flowchart"
    table = "table"
    generic = "generic"


class ScriptType(str, Enum):
    """
    Role-based classification of code artefacts in scholarly publications. All values map to fabio:ComputerProgram; the enum value itself conveys the functional role within the paper's methodology.
    """
    analysis = "analysis"
    visualization = "visualization"
    workflow = "workflow"
    notebook = "notebook"
    utility = "utility"
    generic = "generic"


class DatasetType(str, Enum):
    """
    Content-type classification of data artefacts in scholarly publications. Values map to dcat:Dataset; the enum value conveys the domain/format category of the data.
    """
    tabular = "tabular"
    sequence = "sequence"
    spectral = "spectral"
    image_stack = "image_stack"
    network = "network"
    model = "model"
    generic = "generic"



class IndiciumDocument(ConfiguredBaseModel):
    """
    Top-level container for a serialisable Indicium document. Holds all entity collections; enables full round-trip JSON/YAML/RDF I/O.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/indicium', 'tree_root': True})

    claims: Optional[dict[str, Claim]] = Field(default=None, description="""All Claim entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    evidences: Optional[list[Evidence]] = Field(default=None, description="""All Evidence entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    sources: Optional[list[Source]] = Field(default=None, description="""All Source entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    figures: Optional[list[Figure]] = Field(default=None, description="""All Figure entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    scripts: Optional[list[Script]] = Field(default=None, description="""All Script entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    datasets: Optional[list[DataAsset]] = Field(default=None, description="""All DataAsset entities in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    claim_links: Optional[list[ClaimLink]] = Field(default=None, description="""All ClaimLink edges in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })
    citation_links: Optional[list[CitationLink]] = Field(default=None, description="""All CitationLink edges in this document.""", json_schema_extra = { "linkml_meta": {'domain_of': ['IndiciumDocument']} })


class Claim(ConfiguredBaseModel):
    """
    A scientific claim using the Bucur 5-slot SuperPattern.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'asb:Claim', 'from_schema': 'https://w3id.org/indicium'})

    id: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'dct:identifier'} })
    context: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'asb:context'} })
    subject: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'asb:subject'} })
    qualifier: SuperPatternQualifier = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'asb:qualifier'} })
    relation: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'asb:relation'} })
    object: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Claim'], 'slot_uri': 'asb:object'} })
    claim_type: Optional[ClaimType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Claim']} })
    source_excerpt: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Claim']} })
    claim_status: Optional[ClaimStatus] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Claim']} })
    asserted_by: Optional[str] = Field(default=None, description="""IRI or identifier of the agent (human ORCID, pipeline run ID, etc.) that asserted this item.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Claim', 'Evidence'], 'slot_uri': 'prov:wasAttributedTo'} })
    astra_insight_ref: Optional[str] = Field(default=None, description="""Reference to the originating ASTRA insight in 'analysis_id/insight_id' format.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Claim']} })
    superseded_by: Optional[str] = Field(default=None, description="""URI of the Claim that supersedes this one. Must be set when claim_status is 'superseded'. Allows external Claim IRIs for cross-document lineage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Claim']} })


class Evidence(ConfiguredBaseModel):
    """
    An evidence line linking a Claim to a Source (SEPIO EvidenceLine).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'sepio:0000002', 'from_schema': 'https://w3id.org/indicium'})

    evidence_type: Optional[EvidenceType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    source_type: Optional[SourceType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    quote: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    confidence: Optional[float] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    of_source: Optional[Source] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    for_claim: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    of_figure: Optional[Figure] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    of_script: Optional[Script] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    of_dataset: Optional[DataAsset] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    text_selector: Optional[TextQuoteSelector] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    fragment_selector: Optional[FragmentSelector] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'Figure']} })
    decision_context: Optional[list[str]] = Field(default=None, description="""ASTRA-style 'decision_id.option_id' tags scoping this evidence item to a specific methodological universe. Empty list = universally applicable.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence']} })
    asserted_by: Optional[str] = Field(default=None, description="""IRI or identifier of the agent (human ORCID, pipeline run ID, etc.) that asserted this item.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Claim', 'Evidence'], 'slot_uri': 'prov:wasAttributedTo'} })

    @field_validator('decision_context')
    def pattern_decision_context(cls, v):
        pattern=re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*\.[a-zA-Z_][a-zA-Z0-9_]*$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid decision_context format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid decision_context format: {v}"
            raise ValueError(err_msg)
        return v


class Source(ConfiguredBaseModel):
    """
    A cited source/paper with stable identity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'fabio:Expression', 'from_schema': 'https://w3id.org/indicium'})

    identifier: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure', 'Script', 'DataAsset'],
         'slot_uri': 'dct:identifier'} })
    title: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source'], 'slot_uri': 'dct:title'} })
    authors: Optional[list[str]] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source']} })
    license_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source']} })


class Figure(ConfiguredBaseModel):
    """
    A figure, table, or other display item from a scholarly publication. Carries optional FaBiO sub-type classification (via figure_type) and provenance (source_doi). Linked from Evidence.of_figure when the evidence is grounded in a visual artefact rather than a text passage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'doco:Figure',
         'from_schema': 'https://w3id.org/indicium',
         'slot_usage': {'identifier': {'name': 'identifier', 'required': False}}})

    identifier: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure', 'Script', 'DataAsset'],
         'slot_uri': 'dct:identifier'} })
    figure_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    caption: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    figure_type: Optional[FigureType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    panel_label: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    page: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    media_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    content_url: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    source_doi: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    is_supplementary: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    fragment_selector: Optional[FragmentSelector] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'Figure']} })


class Script(ConfiguredBaseModel):
    """
    A code artefact (script, notebook, or pipeline) from a scholarly publication. Carries role classification (script_type), programming language, repository URL, and optional pinned commit. Linked from Evidence.of_script when the evidence is grounded in code rather than a text passage or figure.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'fabio:ComputerProgram',
         'from_schema': 'https://w3id.org/indicium',
         'slot_usage': {'identifier': {'name': 'identifier', 'required': False}}})

    identifier: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure', 'Script', 'DataAsset'],
         'slot_uri': 'dct:identifier'} })
    script_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    script_type: Optional[ScriptType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    language: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    purpose: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    repository_url: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    content_url: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    commit_sha: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Script']} })
    source_doi: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    is_supplementary: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })


class DataAsset(ConfiguredBaseModel):
    """
    A data artefact (dataset, supplementary file, or public repository deposit) from a scholarly publication. Carries content-type classification (dataset_type), file format, accession number, and hosting repository. Linked from Evidence.of_dataset when the evidence is grounded in data rather than a text passage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'dcat:Dataset',
         'from_schema': 'https://w3id.org/indicium',
         'slot_usage': {'identifier': {'name': 'identifier', 'required': False}}})

    identifier: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure', 'Script', 'DataAsset'],
         'slot_uri': 'dct:identifier'} })
    asset_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    dataset_type: Optional[DatasetType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    data_format: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    accession: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    repository: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    content_url: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    source_doi: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })
    n_samples: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['DataAsset']} })
    is_supplementary: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure', 'Script', 'DataAsset']} })


class CitationLink(ConfiguredBaseModel):
    """
    A typed link (CiTO) from a Source to a Claim.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/indicium'})

    of_source: Optional[Source] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    for_claim: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    link_type: Optional[LinkType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['CitationLink', 'ClaimLink']} })


class ClaimLink(ConfiguredBaseModel):
    """
    A typed semantic link between two Claims using CiTO predicates. Enables contradiction detection, argument graphs, and claim ledger navigation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/indicium'})

    from_claim: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ClaimLink']} })
    to_claim: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['ClaimLink']} })
    link_type: Optional[LinkType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['CitationLink', 'ClaimLink']} })


class TextQuoteSelector(ConfiguredBaseModel):
    """
    W3C TextQuoteSelector. Exact text + optional disambiguation context. Matches ASTRA's existing oa:TextQuoteSelector alignment.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'oa:TextQuoteSelector',
         'from_schema': 'https://w3id.org/indicium'})

    tqs_exact: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TextQuoteSelector']} })
    tqs_prefix: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TextQuoteSelector']} })
    tqs_suffix: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['TextQuoteSelector']} })


class FragmentSelector(ConfiguredBaseModel):
    """
    W3C FragmentSelector for PDF page location.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'oa:FragmentSelector', 'from_schema': 'https://w3id.org/indicium'})

    frag_value: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['FragmentSelector']} })
    frag_page: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['FragmentSelector']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
IndiciumDocument.model_rebuild()
Claim.model_rebuild()
Evidence.model_rebuild()
Source.model_rebuild()
Figure.model_rebuild()
Script.model_rebuild()
DataAsset.model_rebuild()
CitationLink.model_rebuild()
ClaimLink.model_rebuild()
TextQuoteSelector.model_rebuild()
FragmentSelector.model_rebuild()
