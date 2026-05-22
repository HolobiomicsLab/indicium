from pathlib import Path
import rdflib

AUG = Path(__file__).parents[1] / "src/indicium/augmentation"


def test_alignment_declares_owl_imports():
    g = rdflib.Graph()
    g.parse(AUG / "alignment.ttl", format="turtle")
    imports = list(g.objects(predicate=rdflib.OWL.imports))
    assert any("eco" in str(i) for i in imports)
    assert any("cito" in str(i) for i in imports)
    assert any("prov-o" in str(i) for i in imports)


def test_supplemental_shapes_parse():
    g = rdflib.Graph()
    g.parse(AUG / "supplemental-shapes.ttl", format="turtle")  # must not raise
