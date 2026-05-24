# SEPIO assertion pattern: how a skill asserts reliance on a claim

**Status:** Reference. Stable as of indicium v1.6.0.
**Scope:** Defines the standard pattern for `<external entity> --[relies-on]--> <indicium:Claim>` links, used by ASB-Skills, Scriptorium manuscripts, and any other consumer that needs to assert "X depends on claim Y" inside the indicium graph.

## Vocabulary

SEPIO (Scientific Evidence and Provenance Information Ontology) provides:

| Term | IRI | Used for |
|---|---|---|
| `sepio:0000002` | `EvidenceLine` | The `indicium:Evidence` class itself |
| `sepio:0000007` | `is evidence for` | `Evidence.supports_claim` slot — links Evidence to the Claim it backs |
| `sepio:0000130` | `is asserted by` | Skill / agent / pipeline → Claim |
| `sepio:0000174` | `qualified by` | Confidence / context qualifier on an assertion |

## The "skill asserts reliance on a claim" pattern

When an ASB-Skill (or any external artefact) declares it relies on a claim:

```turtle
# Subject IRI = the skill (external; not stored in indicium)
<https://w3id.org/holobiomicslab/asb-skill/feature-detection-lcms@sha256:abc>
    sepio:0000130 <https://w3id.org/indicium/claim/<uuid>> .

# The claim itself lives in indicium and follows the standard pattern
<https://w3id.org/indicium/claim/<uuid>> a asb:Claim ;
    asb:subject "MZmine 4 feature detector" ;
    asb:relation "produces" ;        # also exposed as `predicate`
    asb:qualifier "produces" ;        # SuperPattern qualifier (also: `super_pattern`)
    asb:object "feature table from LC-MS raw data" .

# Evidence backs the claim
_:ev1 a sepio:0000002 ;
    sepio:0000007 <https://w3id.org/indicium/claim/<uuid>> ;   # supports_claim
    indicium:eco_code "textual_quotation" ;                       # ECO:0000033
    indicium:quote_exact "...verbatim from §2.1..." ;
    indicium:quote_location "p-23" ;
    indicium:of_source <https://doi.org/10.1234/paper-1> .
```

## JSON-LD form (the form ASB and Scriptorium actually emit)

```json
{
  "@context": "https://w3id.org/indicium/context.jsonld",
  "@id": "https://w3id.org/holobiomicslab/asb-skill/feature-detection-lcms@sha256:abc",
  "asserts": [
    "https://w3id.org/indicium/claim/<uuid>"
  ]
}
```

The `asserts` JSON-LD term in `context.jsonld` is bound to `sepio:0000130`. Downstream consumers reading the JSON-LD see only `asserts`; the OWL reasoner sees `sepio:0000130`.

## Why this pattern (and not just CiTO)

`cito:usesMethodIn` / `cito:citesAsAuthority` are paper-to-paper. SEPIO is asserter-to-claim — the asserter can be a non-paper artefact (skill, pipeline, agent, dataset, manuscript). That matches ASB's "skill X relies on claim Y from paper Z" exactly.

## Constraints

1. **Asserter IRI is opaque to indicium.** A skill IRI is not registered in indicium; indicium only stores the Claim/Evidence/Source side.
2. **`asserts` is non-multivalued per skill ↔ claim pair.** A skill that relies on multiple claims emits multiple statements.
3. **The Claim being asserted MUST resolve in the indicium graph.** The round-trip CI test in `indicium-adapters` (Plan 1c) enforces this at release time.
4. **Cardinality of Evidence is unbounded:** one Claim can have N Evidence lines from M Sources. ASB typically emits 1–2 Evidence per Claim.

## Cross-reference

- `Evidence.supports_claim` (added Wave 1) — the SEPIO `is evidence for` slot, mapped explicitly so adapters don't have to guess the slot name.
- `Evidence.eco_code` (added Wave 1) — the ECO classification of the evidence line; ASB-subset enum lives in `EcoCodeAsbSubset`.
- See [`uri-scheme.md`](uri-scheme.md) for the `indicium:claim/<uuid>` form and the content-hash citation variant.
