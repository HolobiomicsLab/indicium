# Contributing

Indicium is a versioned standard: a change to the vocabulary is a change to
identifiers that published data embeds. Read the release and versioning policy in
the README before proposing one.

## Set up

```bash
uv sync --frozen --extra codegen --extra docs
uv run --frozen pytest -q
make lint
```

## Kinds of change

- **Documentation, tests, tooling.** Open a pull request against `main`.
- **A new class, slot or enum value** (minor). Edit `src/indicium/schema/indicium.yaml`,
  run `make schema-assets` and commit the regenerated files with the schema. Add a
  `CHANGELOG.md` entry under the next version heading. Term IRIs are derived from
  the schema; choose names you can keep.
- **An IRI change, a slot removal or a tighter cardinality** (major). Open an issue
  first; published data embeds the current IRIs, so this needs a migration note and a
  major version.
- **Domain-specific shapes and vocabularies** belong to a domain adapter package, not
  to this repository.

## Before you open a pull request

```bash
uv run --frozen pytest -q
make lint
make schema-assets && git status --short
uv run --frozen mkdocs build --strict
```

`git status --short` must print nothing after `make schema-assets`: the generated
artefacts are committed and CI fails when a second run differs. A version lives in
three files (`pyproject.toml`, `src/indicium/schema/indicium.yaml`, `CITATION.cff`);
`tests/test_schema_version.py` fails while they disagree. Maintainers bump the
version; contributors leave it alone.

Describe in the pull request what changed and how you checked it. Keep one concern
per pull request.

## Releases

Releases are cut by the maintainers from `main` following `RELEASING.md`.

## Licence

Contributions are accepted under the repository's MIT licence.
