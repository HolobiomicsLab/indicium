from pathlib import Path
import rdflib

GEN = Path(__file__).parents[1] / "src/indicium/generated"


def test_pydantic_model_imports_and_builds_a_claim():
    import importlib.util
    spec = importlib.util.spec_from_file_location("gen_model", GEN / "model.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    c = mod.Claim(context="ctx", subject="s", qualifier="causes",
                  relation="leads to", object="o")
    assert c.qualifier == "causes"


def test_shacl_and_owl_parse():
    for fn in ("shapes.ttl", "ontology.ttl"):
        g = rdflib.Graph()
        g.parse(GEN / fn, format="turtle")
        assert len(g) > 0


def test_json_schema_present():
    assert (GEN / "schema.json").stat().st_size > 0
