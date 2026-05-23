SCHEMA=src/indicium/schema/indicium.yaml
GEN=src/indicium/generated
ASSETS=docs/schema-assets

.PHONY: gen schema-assets

gen:
	mkdir -p $(GEN)
	uv run gen-pydantic $(SCHEMA) > $(GEN)/model.py
	# Patch: preserve enum members so StrEnum .value attribute is accessible.
	sed -i '' 's/use_enum_values = True/use_enum_values = False/' $(GEN)/model.py
	uv run gen-shacl --non-closed $(SCHEMA) > $(GEN)/shapes.ttl
	uv run gen-owl $(SCHEMA) > $(GEN)/ontology.ttl
	uv run gen-json-schema $(SCHEMA) > $(GEN)/schema.json

schema-assets: gen
	mkdir -p $(ASSETS)
	cp $(GEN)/schema.json $(ASSETS)/indicium.schema.json
	cp $(GEN)/ontology.ttl $(ASSETS)/indicium.owl.ttl
	cp $(GEN)/shapes.ttl $(ASSETS)/indicium.shapes.ttl
