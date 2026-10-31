"""Generate the packaged JSON-LD context from LinkML RDF bindings."""

import json
from pathlib import Path

from linkml_runtime.utils.schemaview import SchemaView

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "src/indicium/schema/indicium.yaml"
TARGET = SCHEMA.with_name("context.jsonld")


def enum_context(view, range_name):
    """Return scoped term mappings for an enum's explicit RDF meanings."""
    enum = view.all_enums().get(range_name)
    if enum is None:
        return {}
    return {name: str(value.meaning) for name, value in enum.permissible_values.items() if value.meaning}


def slot_context(view, slot):
    """Return the slot URI, reference coercion and any scoped enum vocabulary."""
    entry = {"@id": view.get_uri(slot)}
    range_name = slot.range or view.schema.default_range
    if range_name in view.all_classes() or range_name in {"uri", "uriorcurie"}:
        entry["@type"] = "@id"
    if range_name == "float":
        entry["@type"] = "http://www.w3.org/2001/XMLSchema#float"
    meanings = enum_context(view, range_name)
    if meanings:
        entry.update({"@type": "@vocab", "@context": meanings})
    if slot.multivalued:
        entry["@container"] = "@set"
    return entry


def generate_context(view):
    """Build a context with schema mappings and the documented ASB prefixes."""
    context = {"@version": 1.1}
    for name, prefix in view.schema.prefixes.items():
        iri = str(prefix.prefix_reference)
        context[name] = {"@id": iri, "@prefix": True} if iri.endswith("_") else iri
    context.update({
        "eco": context["ECO"], "iao": context["IAO"],
        "ro": {"@id": "http://purl.obolibrary.org/obo/RO_", "@prefix": True},
        "asbval": "https://w3id.org/asb/validation#", "edam": "http://edamontology.org/",
    })
    context.update({name: view.get_uri(cls) for name, cls in view.all_classes().items()})
    context.update({name: slot_context(view, slot) for name, slot in view.all_slots().items()})
    context["id"] = "@id"
    return {"@context": context}


if __name__ == "__main__":
    payload = generate_context(SchemaView(str(SCHEMA)))
    TARGET.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    print(f"Generated {TARGET.relative_to(ROOT)} ({len(payload['@context'])} context entries)")
