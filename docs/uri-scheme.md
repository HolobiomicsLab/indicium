# Indicium URI scheme

The stable namespace bases are `https://w3id.org/indicium/` and
`https://w3id.org/asb#`. Import `INDICIUM_BASE` and `ASB_BASE` from `indicium`
when producing RDF. The namespace registration is prepared separately; a
namespace prefix does not imply that its HTTP redirect is already registered.

## Vocabulary and RDF bindings

The deposit describes the LinkML schema at `https://holobiomicslab.eu/ns/indicium/`,
with HTML, Turtle, JSON-LD and the packaged context. The prepared `/indicium`
w3id entry will redirect to those files after owner submission and approval.

Generated OWL describes local LinkML schema elements, including
`indicium:Claim`. Instance RDF follows each element's `class_uri` or `slot_uri`
in the schema: for example, a Claim is typed `asb:Claim`, and Evidence is typed
`sepio:0000002`. Local schema-element IRIs do not override these RDF bindings.

## Instance identifiers

Producers may use identity IRIs such as:

```text
https://w3id.org/indicium/claim/<uuid>
https://w3id.org/indicium/evidence/<uuid>
https://w3id.org/indicium/source/<uuid>
https://w3id.org/indicium/software-entity/<uuid>
```

The producing system allocates and stores its instances. Indicium does not
provide a central store or a resolver for individual UUIDs. The namespace
landing page can explain these paths; it cannot return the latest entity or
establish that a cited instance exists.

Some consumers use `<identity>@sha256:<hex>` as an immutable citation identifier.
The hash is meaningful only with the producer's documented canonicalization
and preserved payload. Sorting JSON keys is not by itself a standard RDF
canonicalization contract. Indicium does not currently implement this resolver
or verify these content hashes.

The KGmemory adapter separately emits `urn:indicium:claim:<id>`. URNs are
identifiers, not HTTP addresses. Its `http://kgmemory.org/ns#` base is a legacy
external dependency; consumers should not infer current ownership or
availability from its presence in an export.

ASB collection identifiers may also use
`https://w3id.org/holobiomicslab/asb-skill/` or
`https://w3id.org/holobiomicslab/asb-tool/`. Their registration and content are
owned by the ASB collection release, separately from this deposit.

## Loading the context before publication

Use the installed package instead of a prospective remote URL:

```python
import json
from importlib.resources import files

context = json.loads(files("indicium.schema").joinpath("context.jsonld").read_text())
```

`docs/context.jsonld` links to that same packaged file for the MkDocs build.
Once deployed and registered, the prepared remote entry point is
`https://w3id.org/indicium/context.jsonld`. Pin the package version when exact
context semantics matter.
