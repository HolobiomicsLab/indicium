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


def validate_graph(
    data: rdflib.Graph,
    extra_shapes: rdflib.Graph | None = None,
) -> tuple[bool, str]:
    """SHACL-validate *data* against indicium's base shapes.

    Args:
        data: The RDF graph to validate.
        extra_shapes: Optional additional SHACL shapes graph (e.g. from a
            DomainAdapter) merged with the base shapes before validation.
            Pass ``None`` (default) for identical behaviour to v0.1.

    Returns:
        ``(conforms, report_text)``
    """
    shapes = _shapes_graph()
    if extra_shapes is not None:
        shapes = shapes + extra_shapes
    conforms, _, report = _shacl_validate(
        data_graph=data, shacl_graph=shapes,
        inference="none", abort_on_first=False, meta_shacl=False,
    )
    return conforms, report
