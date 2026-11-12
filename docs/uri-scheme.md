# URI scheme

This page records which IRIs Indicium uses, which of them resolve today, and what the
pending registration will add. Every status below was measured on 2026-10-30.

## Namespaces

| Prefix | Namespace | What it names | Resolves today |
|---|---|---|---|
| `asb:` | `https://w3id.org/asb#` | `asb:Claim` and eight slot IRIs: the SuperPattern slots `asb:context`, `asb:subject`, `asb:qualifier`, `asb:relation`, `asb:object`, and `asb:domainQualifier`, `asb:sourceTaskKind`, `asb:workflowCoupling` | Yes |
| `asbval:` | `https://w3id.org/asb/validation#` | Validation assertion terms used by ASB beside `asb:`. Not a prefix of this schema | Yes |
| `indicium:` | `https://w3id.org/indicium/` | The LinkML schema `id`, the `indicium` prefix of the JSON-LD context, and every class and slot without its own `class_uri` or `slot_uri`: claim metadata (`claim_status`, `claim_type`, `source_excerpt`), the evidence and source slots (`eco_code`, `quote_exact`, `for_claim`, `of_source`, ...), `ClaimLink`, `CitationLink` and `IndiciumDocument`. Of the 87 distinct IRIs used as SHACL paths, 75 are under this namespace, and the OWL artefact names every class and slot under it | No (404) |

Code never needs to spell these strings. The bases are exported:

```python
from indicium import ASB_BASE, INDICIUM_BASE, asb_term

ASB_BASE           # 'https://w3id.org/asb#'
INDICIUM_BASE      # 'https://w3id.org/indicium/'
asb_term("Claim")  # 'https://w3id.org/asb#Claim'
```

### `https://w3id.org/asb#` and `https://w3id.org/asb/validation#`

Registered on w3id.org on 29 October 2026
([perma-id/w3id.org#7017](https://github.com/perma-id/w3id.org/pull/7017)). The
redirects lead to documents hosted by the lab, which negotiate the representation:

| Request | Redirect chain | Final response |
|---|---|---|
| `https://w3id.org/asb`, `Accept: text/turtle` | 301 to `/asb/`, 303 to `https://holobiomicslab.eu/ns/asb`, 303 to `asb.ttl` | 200 `text/turtle` |
| `https://w3id.org/asb`, `Accept: application/ld+json` | same, ending at `asb.jsonld` | 200 `application/ld+json` |
| `https://w3id.org/asb`, `Accept: text/html` | same, ending at `asb.html` | 200 `text/html` |
| `https://w3id.org/asb/validation`, `Accept: text/turtle` | 303 to `https://holobiomicslab.eu/ns/asbval`, 303 to `asbval.ttl` | 200 `text/turtle` |
| `https://w3id.org/asb/validation`, `Accept: text/html` | same, ending at `asbval.html` | 200 `text/html` |

The fragment of a hash IRI never reaches the server: `https://w3id.org/asb#Claim` is
looked up in the document returned for `https://w3id.org/asb`. Cite the w3id IRIs, not
the `holobiomicslab.eu` addresses behind them; the redirect target can change, the
identifier does not.

### `https://w3id.org/indicium/`

Not registered. `https://w3id.org/indicium/` and every IRI under it return 404. The
request files are ready in the repository, under `docs/release/w3id-indicium/`, and
wait on two prerequisites: the repository must be public and GitHub Pages must be
enabled. `RELEASING.md` lists the order.

The request files propose the rules below. They take effect only when the
registration is merged, and they can change until then:

| IRI | `Accept` | Target |
|---|---|---|
| `https://w3id.org/indicium/` and single-segment terms, for example `.../IndiciumDocument` | `text/turtle` | `docs/schema-assets/indicium.owl.ttl` on the `main` branch, via `raw.githubusercontent.com` |
| same | `application/ld+json` | `src/indicium/schema/context.jsonld` on `main`, via `raw.githubusercontent.com` |
| same | anything else | the documentation site, `https://holobiomicslab.github.io/indicium/` |
| `.../context.jsonld` | any | `src/indicium/schema/context.jsonld` on `main`, via `raw.githubusercontent.com` |
| `.../indicium.owl.ttl`, `.../indicium.shapes.ttl`, `.../indicium.schema.json` | any | the file in `docs/schema-assets/` on `main`, via `raw.githubusercontent.com` |
| `.../<X.Y.Z>/<one of those files>` | any | the file at the tag `v<X.Y.Z>` |
| `.../claim/<uuid>` and other multi-segment paths | any | 404 (no service resolves instances) |

### Two names for one class in the generated artefacts

The SHACL shapes and the pydantic model use the `class_uri` and `slot_uri` of the
LinkML source. They bind `Claim` and seven of its distinct slots to `asb:` IRIs,
and `Evidence.workflow_coupling` adds the eighth `asb:` path. `Evidence`, `Source`,
`Figure`, `Script` and `DataAsset` use SEPIO, FaBiO, DoCO and DCAT classes;
`SoftwareEntity` keeps its `indicium:` class. The two selectors use Web Annotation
(`oa:`) and `SSSOMMapping` uses `sssom:Mapping`. A few slots use Dublin Core, PROV
and SEPIO properties; every other class and slot uses its `indicium:` IRI.

Repeated constraints can use the same path, so the number of `sh:path` statements
is larger than the distinct vocabulary footprint:

| Shapes graph | Statements | `indicium:` | `asb:` | Other | Distinct total | Distinct `indicium:` | Distinct `asb:` | Distinct other |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `src/indicium/generated/shapes.ttl` | 108 | 86 | 10 | 12 | 87 | 75 | 8 | 4 |
| `docs/schema-assets/indicium.shapes.ttl` | 110 | 86 | 12 | 12 | 87 | 75 | 8 | 4 |

The published asset adds the supplemental qualifier-presence constraint, whose two
paths are under `asb:`.

The OWL artefact, `indicium.owl.ttl`, is generated with the LinkML default that names
each class and slot by its schema-native IRI under `indicium:`, including those bound
elsewhere: it declares 60 IRIs typed `owl:Class` (classes, enums and enum values), 58
`owl:DatatypeProperty` and 34 `owl:ObjectProperty` under `https://w3id.org/indicium/`.
The ontology document itself is `https://w3id.org/indicium`.
Each class bound elsewhere carries `skos:exactMatch` to that IRI (`indicium:Claim` to
`asb:Claim`, `indicium:Evidence` to `SEPIO_0000002`, ...); the slots carry no such
mapping. Validate data against the SHACL shapes. Most properties they check are
`indicium:` IRIs, so the pending `/indicium` registration matters for claim and
evidence data, not only for document-level terms.

## Entity identifiers

Producers mint their own identifiers; Indicium does not allocate them. Producers may
use identity IRIs such as:

```
https://w3id.org/indicium/claim/<uuid>
https://w3id.org/indicium/evidence/<uuid>
https://w3id.org/indicium/source/<uuid>
https://w3id.org/indicium/software-entity/<uuid>
```

- `<uuid>` is a UUIDv4 from the producing pipeline.
- The producing system allocates and stores its instances. Indicium provides no
  central store and no resolver for individual UUIDs. These IRIs are names, not
  addresses: no service dereferences them, and the proposed `/indicium` rules leave
  multi-segment paths unserved.
- Some consumers cite `<identity>@sha256:<hex>` as an immutable citation identifier.
  The hash is meaningful only with the producer's documented canonicalization and
  the preserved payload; sorting JSON keys is not by itself a standard RDF
  canonicalization. This package does not compute or verify these hashes.

The KGmemory adapter separately emits `urn:indicium:claim:<id>`. URNs are
identifiers, not HTTP addresses. Its `http://kgmemory.org/ns#` base is a legacy
external dependency; do not infer current ownership or availability from its
presence in an export.

## JSON-LD context

The context is `docs/context.jsonld` in the repository, identical to
`src/indicium/schema/context.jsonld`, which ships in the wheel. It is generated from
the `class_uri`, `slot_uri` and enum meanings of the LinkML source (`make context`), so
its term IRIs are the ones the SHACL shapes check. No public URL serves it today.
Until one does, load it from the installed package:

```python
from importlib.resources import files

context = (files("indicium") / "schema" / "context.jsonld").read_text()
```

After the release it will be served by the documentation site at
`https://holobiomicslab.github.io/indicium/context.jsonld` and, once registered, at
`https://w3id.org/indicium/context.jsonld`.

## Related identifiers of the same lab

| Namespace | Owner | Resolves today |
|---|---|---|
| `https://w3id.org/holobiomicslab/asb-skill/...` | [asb-skill-collections](https://github.com/HolobiomicsLab/asb-skill-collections) | Yes. Registry, contributors, leaderboard and collection paths have their own rules; every other path redirects (302) to the repository |
| `https://w3id.org/holobiomicslab/asb-tool/...` | asb-skill-collections | Redirects (302) to the same repository; there is no dedicated rule yet |

An ASB-Tool IRI may appear as the value of `SoftwareEntity.identifier`, so one tool can
be both a node in an Indicium graph and a citable release record.

## Stability

- A term IRI never changes after a tagged release. Published data embeds it.
- Adding a class, a slot or an enum value is a minor version.
- Changing an IRI, removing a slot, or tightening a cardinality is a major version.
  This is why the move of the `asb:` base to `https://w3id.org/asb#` was 2.0.0.
