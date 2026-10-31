SCHEMA=src/indicium/schema/indicium.yaml
GEN=src/indicium/generated
ASSETS=docs/schema-assets
CHANGELOG=CHANGELOG.md
DOCS_CHANGELOG=docs/changelog.md
SUPPLEMENTAL=src/indicium/augmentation/supplemental-shapes.ttl

.PHONY: gen context schema-assets docs-changelog lint

gen:
	mkdir -p $(GEN)
	uv run --frozen gen-pydantic $(SCHEMA) > $(GEN)/model.py
	# Patch: preserve enum members so StrEnum .value attribute is accessible.
	uv run --frozen python -c 'from pathlib import Path; p = Path("$(GEN)/model.py"); p.write_text(p.read_text().replace("use_enum_values = True", "use_enum_values = False"))'
	uv run --frozen gen-shacl --non-closed $(SCHEMA) > $(GEN)/shapes.ttl
	uv run --frozen gen-owl --ontology-uri-suffix '' $(SCHEMA) > $(GEN)/ontology.ttl
	uv run --frozen gen-json-schema $(SCHEMA) > $(GEN)/schema.json
	uv run --frozen python scripts/canonicalize_rdf.py $(GEN)/shapes.ttl $(GEN)/ontology.ttl

context:
	uv run --frozen python scripts/generate_context.py

lint:
	uv run --frozen ruff check src scripts

# The rendered changelog is a copy of the maintained one, never edited by hand.
docs-changelog:
	cp $(CHANGELOG) $(DOCS_CHANGELOG)

schema-assets: gen context docs-changelog
	mkdir -p $(ASSETS)
	cp $(GEN)/schema.json $(ASSETS)/indicium.schema.json
	cp $(GEN)/ontology.ttl $(ASSETS)/indicium.owl.ttl
	# The published shapes are the ones validate_graph applies: generated plus supplemental.
	uv run --frozen python scripts/merge_shapes.py $(ASSETS)/indicium.shapes.ttl $(GEN)/shapes.ttl $(SUPPLEMENTAL)
