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
        use_enum_values = True,
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


class LinkType(str, Enum):
    supports = "supports"
    disputes = "disputes"
    qualifies = "qualifies"
    citesForInformation = "citesForInformation"


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


class Source(ConfiguredBaseModel):
    """
    A cited source/paper with stable identity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'fabio:Expression', 'from_schema': 'https://w3id.org/indicium'})

    identifier: str = Field(default=..., json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure'], 'slot_uri': 'dct:identifier'} })
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

    identifier: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Source', 'Figure'], 'slot_uri': 'dct:identifier'} })
    figure_id: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    caption: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    figure_type: Optional[FigureType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    panel_label: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    page: Optional[int] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    media_type: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    content_url: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    source_doi: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })
    is_supplementary: Optional[bool] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Figure']} })


class CitationLink(ConfiguredBaseModel):
    """
    A typed link (CiTO) from a Source to a Claim.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/indicium'})

    of_source: Optional[Source] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    for_claim: Optional[str] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['Evidence', 'CitationLink']} })
    link_type: Optional[LinkType] = Field(default=None, json_schema_extra = { "linkml_meta": {'domain_of': ['CitationLink']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
Claim.model_rebuild()
Evidence.model_rebuild()
Source.model_rebuild()
Figure.model_rebuild()
CitationLink.model_rebuild()
