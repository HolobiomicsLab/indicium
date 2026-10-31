<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/assets/brand/indicium-mark-dark.svg">
    <source media="(prefers-color-scheme: light)" srcset="docs/assets/brand/indicium-mark.svg">
    <img src="https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/docs/assets/brand/indicium-mark.svg" width="120" alt="Indicium mark">
  </picture>
</p>

<h1 align="center">Indicium</h1>

<p align="center">A versioned standard for a typed scientific claim bound to the evidence that grounds it.</p>

<p align="center">
  <a href="https://github.com/HolobiomicsLab/indicium/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-00284b" alt="License: MIT"></a>
  <a href="https://github.com/HolobiomicsLab/indicium/blob/main/pyproject.toml"><img src="https://img.shields.io/badge/python-3.11%2B-00284b" alt="Python 3.11+"></a>
  <!-- Uncomment once the repository is public (RELEASING.md, follow-ups):
  <a href="https://github.com/HolobiomicsLab/indicium/actions/workflows/ci.yml"><img src="https://github.com/HolobiomicsLab/indicium/actions/workflows/ci.yml/badge.svg" alt="Tests"></a>
  -->
  <!-- Uncomment once indicium-standard is on PyPI (RELEASING.md, follow-ups):
  <a href="https://pypi.org/project/indicium-standard/"><img src="https://img.shields.io/pypi/v/indicium-standard?color=00284b" alt="PyPI"></a>
  -->
</p>

---

## What it is

Indicium is a small, standalone, versioned **standard for a typed scientific claim
bound to the evidence that grounds it.** One LinkML source of truth generates pydantic
models, JSON Schema, SHACL shapes and OWL. It reuses community ontologies rather than
reinventing them:

| Axis | Standard |
|------|----------|
| Evidence type | **ECO** (Evidence & Conclusion Ontology) |
| Claim to citation relation | **CiTO** |
| Source and document type | **DoCO** and **IAO** |
| Article type | **FaBiO** |
| Assertion and evidence structure | **SEPIO** |
| Provenance | **PROV-O** |
| Claim structure | **Bucur et al.** 5-slot SuperPattern (K-CAP 2021) |

The one thing Indicium mints is the **binding**: a claim, its typed evidence, and the
source that evidence points to, provenance-stamped. That binding is the load-bearing
contribution. The claim structure is borrowed from Bucur; the value Indicium
standardizes is the *typed grounding of claims in evidence.*

Indicium is a vocabulary and a standard, not a tool and not a store. Every tool that
mints claims imports it, so a claim minted by any of them is structurally identical to
one minted by another, merges with it, and never travels without its evidence trace.

| Part | Where |
|------|-------|
| LinkML schema, the source of truth | `src/indicium/schema/indicium.yaml` |
| Pydantic models (`Claim`, `Evidence`, `Source`, `CitationLink`, `ClaimLink`, `IndiciumDocument`, ...) | `indicium.generated.model`, re-exported from `indicium` |
| SHACL shapes, OWL ontology, JSON Schema | `src/indicium/generated/`, copied to `docs/schema-assets/` |
| JSON-LD context | `src/indicium/schema/context.jsonld` |
| SHACL validation | `indicium.validate_graph` |
| Quote verification kernel | `indicium.verify_quote` |
| Projections to SciTask, ASTRA and KGmemory | `indicium.adapters`, `indicium.astra_bridge` |

### The name

*Indicium* (Latin) is "a sign or mark that points to the truth"; in law, the
evidentiary indication. The package is named for what it standardizes: every claim
carries its **indicia**, the traces that justify believing it.

- **`indicium`** (singular) is the standard and this package.
- **indicia** (plural) is the body of evidence attached to a claim, and the term
  consumer APIs use for the produced collection.

## Install

Requires Python 3.11 or newer. The command below is for the public release;
until 2.0.0 is published, install a wheel supplied by the maintainers.

```bash
pip install indicium-standard      # distribution name
python -c "import indicium"        # import name
```

Optional extras:

```bash
pip install "indicium-standard[astra]"     # ASTRA bridge (PyYAML)
pip install "indicium-standard[codegen]"   # regenerate the artefacts from the LinkML source
```

The 2.0.0 upload to PyPI is pending ([RELEASING.md](https://github.com/HolobiomicsLab/indicium/blob/main/RELEASING.md)). Until
`pip install indicium-standard` finds it, install from the repository:

```bash
pip install "git+https://github.com/HolobiomicsLab/indicium"
```

> **The distribution is `indicium-standard`; the import package is `indicium`.**
> The PyPI name `indicium` belongs to an unrelated, abandoned key-value-store
> package that also ships a top-level `indicium` module. Installing both into the
> same environment will clobber the import. Always depend on `indicium-standard`.

## Quickstart

Validate a claim against the SHACL shapes (adapted from `tests/test_validate.py`):

```python
import rdflib
from indicium import ASB_BASE, validate_graph

claim = f"""
@prefix asb: <{ASB_BASE}> .
<urn:claim:1> a asb:Claim ;
    asb:context "in vitro" ;
    asb:subject "compound A" ;
    asb:qualifier "inhibits" ;
    asb:relation "inhibits growth of" ;
    asb:object "cell line B" .
"""
conforms, report = validate_graph(rdflib.Graph().parse(data=claim, format="turtle"))
print(conforms)  # True

incomplete = f"""
@prefix asb: <{ASB_BASE}> .
<urn:claim:2> a asb:Claim ; asb:context "in vitro" .
"""
conforms, report = validate_graph(rdflib.Graph().parse(data=incomplete, format="turtle"))
print(conforms)  # False
```

`report` names each missing slot. The [quickstart](https://holobiomicslab.github.io/indicium/quickstart/) continues with
the typed model and the adapters; every Python example in this README and on the Home,
Quickstart and URI scheme pages runs in the test suite (`tests/test_docs_examples.py`).

## Vocabulary and IRIs

Import the namespace bases; never copy the IRI string into your own code. A
hardcoded base keeps pointing at the old namespace when the standard moves, and
the SHACL shapes then match nothing: every graph validates as `conforms=True`
while no constraint is actually checked.

```python
from indicium import ASB_BASE, INDICIUM_BASE, asb_term

asb_term("Claim")   # 'https://w3id.org/asb#Claim'
```

```python
ASB = "https://w3id.org/asb#"   # don't: silently dead after a move
```

| Prefix | Namespace | Names | Resolves (measured 2026-10-30) |
|--------|-----------|-------|------------------|
| `asb:` | `https://w3id.org/asb#` | `asb:Claim` and its SuperPattern slots (`context`, `subject`, `qualifier`, `relation`, `object`), plus `domainQualifier`, `sourceTaskKind` and `workflowCoupling` | Yes. Registered on w3id.org on 29 October 2026; 303 to `holobiomicslab.eu/ns/asb`, which serves Turtle, JSON-LD and HTML |
| `asbval:` | `https://w3id.org/asb/validation#` | Validation assertion terms used beside `asb:` by ASB | Yes. Same registration; 303 to `holobiomicslab.eu/ns/asbval` |
| `indicium:` | `https://w3id.org/indicium/` | The schema id, the JSON-LD context prefix, and every class and slot without its own IRI binding: claim metadata, the evidence and source slots, `ClaimLink`, `CitationLink`, `IndiciumDocument` | No (404). Not registered yet; the request files are in [`docs/release/w3id-indicium/`](https://github.com/HolobiomicsLab/indicium/tree/main/docs/release/w3id-indicium) |

[`docs/uri-scheme.md`](https://holobiomicslab.github.io/indicium/uri-scheme/) has the redirect chains, the identifier
conventions for claims and evidence, and what the `/indicium` registration will point
at. `tests/test_namespace_resolves.py` fetches each namespace when
`INDICIUM_NETWORK_TESTS=1` is set.

## Ecosystem

Indicium is the shared layer; the projects below mint, store or consume its claims.

| Project | What it is | Relation to Indicium |
|---------|------------|----------------------|
| [ASTRA](https://astra-spec.org) | A declarative YAML format for scientific analyses: inputs, outputs, decisions and evidence ([astra-spec](https://github.com/LightconeResearch/astra-spec)) | `indicium.astra_bridge` turns claims into ASTRA insights and reads ASTRA findings back as claims |
| AgenticScienceBuilder (ASB) | Turns research articles into SciTask cards, capsules and skills | Depends on `indicium-standard>=2.0.0,<3`; its claims use the `asb:` vocabulary |
| [asb-skill-collections](https://github.com/HolobiomicsLab/asb-skill-collections) | Registry and release tooling of the ASB skill collections | Released collections carry Indicium claim documents (`collections/<domain>/v<N>/indicium/`) |
| `asb-skills-<domain>` | The skill collections, one repository per domain | Built by ASB; same vocabulary |
| [Perspicacité](https://github.com/HolobiomicsLab/Perspicacite-AI) | Local-first retrieval-augmented system for searching and organizing the scientific literature | Uses the Indicium stack, when installed, for claim validation, the claim graph and the ASTRA export |
| Scriptorium | Manuscript authoring | Depends on `indicium-standard>=2.0.0,<3` and the adapters |
| KGmemory | Where claims are stored and reasoned over | `indicium.adapters.kgmemory` emits a JSON-LD node typed `mem:SemanticMemory` |
| `indicium-adapters` | The `DomainAdapter` and `SHACLProvider` protocols and entry-point discovery | Domain shapes reach `validate_graph(..., extra_shapes=...)` |
| `indicium-adapters-<domain>` | Domain bundles: agentic-ai, astronomy, epigenomics, genomics, metabarcoding, metabolomics, metagenomics, multi-omics, proteomics, transcriptomics | Ontology terms and SHACL shapes per domain |

AgenticScienceBuilder, Scriptorium, KGmemory, the `asb-skills-<domain>` collections
and the `indicium-adapters` family are not public yet.

## Development

```bash
uv sync --frozen --extra codegen --extra docs
uv run pytest -q              # includes the conformance suite (parity with the Scriptorium SHACL)
make lint                     # ruff over src/ and scripts/
make gen                      # regenerate model.py, shapes.ttl, ontology.ttl, schema.json
make context                  # regenerate the packaged JSON-LD context from the LinkML URI bindings
make schema-assets            # make gen and make context, then copy the artefacts and the changelog into docs/
uv run mkdocs build --strict  # the documentation site, as docs.yml deploys it
```

`docs/changelog.md` is a copy of `CHANGELOG.md` (`make docs-changelog`); edit only the
latter. `make gen` writes canonical Turtle, so a second run is byte-identical to the
committed files; `release.yml` fails when it is not.

Namespace bases are stable identifiers. Their registration and the vocabulary site are
prepared separately from the Python release; they do not provide an instance store.
Read the [URI scheme](https://holobiomicslab.github.io/indicium/uri-scheme/) and the
[SEPIO compatibility notes](https://holobiomicslab.github.io/indicium/sepio-assertion/)
before exporting RDF.

## Release and versioning policy

Indicium follows [Semantic Versioning](https://semver.org/), read for a vocabulary:

- **Term IRIs are immutable after a tagged release.** Published data embeds them.
- **Additive changes are minor:** a new class, slot or enum value.
- **An IRI change or a slot removal is major,** as is a tighter cardinality. This is
  why the move of the `asb:` base to `https://w3id.org/asb#` is 2.0.0.

A tag `v<version>` that matches `pyproject.toml` and a dated `CHANGELOG.md` section
runs the release (`.github/workflows/release.yml`): the checks, tests, documentation
build and installed-wheel check first, then the upload of the wheel and the sdist to
PyPI through Trusted Publishing, then the GitHub release with the same files and the
three schema artefacts.
[RELEASING.md](https://github.com/HolobiomicsLab/indicium/blob/main/RELEASING.md) is the maintainer checklist. Changes are listed in
[CHANGELOG.md](https://github.com/HolobiomicsLab/indicium/blob/main/CHANGELOG.md).

## Citation

[CITATION.cff](https://github.com/HolobiomicsLab/indicium/blob/main/CITATION.cff) holds the citation metadata, which GitHub offers as
"Cite this repository". No DOI exists yet. BibTeX, derived from that file with
`cffconvert -f bibtex` (citation key renamed):

```bibtex
@misc{nothias_indicium,
  author = {Nothias, Louis-Félix},
  title  = {Indicium: a standard for typed scientific claims bound to their evidence},
  url    = {https://github.com/HolobiomicsLab/indicium}
}
```

## License

MIT, see [LICENSE](https://github.com/HolobiomicsLab/indicium/blob/main/LICENSE). Developed at the Holobiomics Lab, CNRS / Université Côte
d'Azur.
