"""SHACL validation over the generated shapes plus any supplemental shapes."""
from __future__ import annotations

from importlib.resources import files
import rdflib
from pyshacl import validate as _shacl_validate


def _shapes_graph() -> rdflib.Graph:
    g = rdflib.Graph()
    gen = files("indicium.generated")
    g.parse(gen.joinpath("shapes.ttl").open("rb"), format="turtle")
    aug = files("indicium.augmentation").joinpath("supplemental-shapes.ttl")
    g.parse(aug.open("rb"), format="turtle")
    return g


def validate_graph(data: rdflib.Graph) -> tuple[bool, str]:
    conforms, _, report = _shacl_validate(
        data_graph=data, shacl_graph=_shapes_graph(),
        inference="none", abort_on_first=False, meta_shacl=False,
    )
    return conforms, report
