SCHEMA=src/indicium/schema/indicium.yaml
GEN=src/indicium/generated

.PHONY: gen
gen:
	mkdir -p $(GEN)
	uv run gen-pydantic $(SCHEMA) > $(GEN)/model.py
	uv run gen-shacl --non-closed $(SCHEMA) > $(GEN)/shapes.ttl
	uv run gen-owl $(SCHEMA) > $(GEN)/ontology.ttl
	uv run gen-json-schema $(SCHEMA) > $(GEN)/schema.json
