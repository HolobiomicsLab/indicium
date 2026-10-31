# SEPIO evidence links and skill reliance

Indicium 2.0.0 corrects two SEPIO bindings before its first package release.
The JSON keys stay the same; their RDF predicates change. The LinkML schema
defines both bindings, and the packaged JSON-LD context is generated from it.

| JSON key | RDF predicate in 2.0.0 | Meaning |
|---|---|---|
| `supports_claim` | `sepio:0000427` (`is_evidence_line_for`) | Evidence line → the Claim it evaluates |
| `for_claim` | `indicium:for_claim` | Local evidence-line-to-Claim link |
| `asserts` | `indicium:asserts` | Downstream skill or consuming resource → a Claim it relies on |

Here `sepio:`, `ro:` and `eco:` expand to
`http://purl.obolibrary.org/obo/SEPIO_`, `http://purl.obolibrary.org/obo/RO_`
and `http://purl.obolibrary.org/obo/ECO_`. The packaged context marks these
underscore-ending bases with `@prefix: true` for JSON-LD 1.1 expansion.

## Why these bindings fit

The [SEPIO ontology](https://raw.githubusercontent.com/monarch-initiative/SEPIO-ontology/master/sepio.owl),
whose version IRI is the 2023-06-13 release, declares `sepio:0000006`
(`has_evidence_line`) as the inverse of `sepio:0000427`. Its domain is the union
of proposition (`sepio:0000000`) and assertion (`sepio:0000001`); its range is
evidence line (`sepio:0000002`). Reversing that relation therefore gives an
evidence line → proposition or assertion link. Indicium's Evidence already
binds to the evidence-line class, and a Claim describes the scientific
proposition being evaluated. This selection does not add an OWL equivalence
between `asb:Claim` and either SEPIO class.

The old `supports_claim` binding, `sepio:0000007`
(`has_supporting_evidence_line`), is a subproperty of `has_evidence_line` and
runs in the other direction. `sepio:0000376` (`evidence_item_for`) links an
evidence item to an evidence line, so it does not fit an Evidence → Claim
edge. `sepio:0000440` and `sepio:0000441` also run from an assertion toward
evidence, rather than from an evidence line toward a Claim.

The old `asserts` binding, `sepio:0000130` (`authored_by`), concerns the agent
that generated information. A skill can rely on a Claim without authoring it.
`sepio:0000030` (`asserts_proposition`) requires a SEPIO assertion as its
subject, while `sepio:0000109` (`expresses`) describes a document stating a
proposition or assertion in its content. Neither captures reliance alone.
`indicium:asserts` consequently has no external equivalence or close mapping.
It is a schema-declared extension slot with range Claim; the core model does
not introduce a Skill class or attach this slot to Claim.

The regression fixture in `tests/fixtures/sepio/` preserves the relevant OWL
axioms and lists its source version, SHA-256 and CC BY 3.0 attribution.

## Target and evidence direction

`supports_claim` retains its historical name and its LinkML alias `for_claim`.
They refer to the same intended target but remain two independent JSON fields
and two distinct RDF predicates. If both are populated, callers should use the
same Claim IRI. The generated model does not copy one field into the other or
enforce agreement. Neither field alone establishes supporting polarity.

Direction belongs on the evidence line as `sepio:0000183`, with one of:

| Value | Direction |
|---|---|
| `sepio:0000403` | supporting |
| `sepio:0000404` | disputing |
| `sepio:0000405` | inconclusive |

For example, a disputing line still identifies the Claim it evaluates:

```turtle
@prefix asb: <https://w3id.org/asb#> .
@prefix indicium: <https://w3id.org/indicium/> .
@prefix sepio: <http://purl.obolibrary.org/obo/SEPIO_> .

<urn:example:claim> a asb:Claim ;
    asb:context "in vitro" ; asb:subject "A" ;
    asb:qualifier "inhibits" ; asb:relation "inhibits" ; asb:object "B" .
<urn:example:evidence> a sepio:0000002 ;
    sepio:0000427 <urn:example:claim> ;
    sepio:0000183 sepio:0000404 ;
    indicium:quote_exact "A does not inhibit B" .
<urn:example:skill> indicium:asserts <urn:example:claim> .
```

A SEPIO exporter may additionally emit the inverse
`claim sepio:0000006 evidence`. Only when the evidence direction is known to
be supporting may it use `claim sepio:0000007 evidence`. Do not reverse an old
incorrect triple mechanically and infer support from the JSON key's name.
An absent direction remains unspecified.

## ASB validation annotations

ASB's validation bridge already emits `sepio:0000183` with the three direction
values above, and `ro:0002558` → `eco:0000501` for automatic assertion evidence.
These annotations are unchanged. They are separate from Indicium's Claim
lifecycle (`claim_status`) and ECO evidence classification (`eco_code`).

```turtle
@prefix asbval: <https://w3id.org/asb/validation#> .
@prefix sepio: <http://purl.obolibrary.org/obo/SEPIO_> .
@prefix ro: <http://purl.obolibrary.org/obo/RO_> .
@prefix eco: <http://purl.obolibrary.org/obo/ECO_> .

<urn:example:assessment> a asbval:ClaimAssessment ;
    sepio:0000183 sepio:0000403 ;
    ro:0002558 eco:0000501 .
```

The core LinkML model has no dedicated ASB assessment class or direction
slot. Non-closed SHACL permits these external annotations but does not validate
their values on assessment nodes. ASB owns that validation contract and its
assessment-class alignment to SEPIO's evidence-line domain. Passing Indicium
SHACL does not certify an ASB validation record. `sepio:0000174` denotes the
statement class, not a qualifier property.

`https://w3id.org/indicium/context.jsonld` does not resolve yet; the
[URI scheme](uri-scheme.md) page says where to load the context from until it does.

## Updating consumers

Keep JSON keys `supports_claim`, `for_claim` and `asserts`. Refresh embedded
context copies from `indicium-standard` 2.0.0, then regenerate RDF that was
expanded with the earlier context. In such old RDF, Evidence → Claim edges
using `SEPIO_0000007` need `SEPIO_0000427`, and skill-reliance edges using
`SEPIO_0000130` need `indicium:asserts`. Restrict any migration to those known
uses: legitimate claim-side support and authorship triples must retain their
SEPIO predicates. Records referring to the central context need no key rewrite;
their expanded RDF and any cached context still need refreshing.

The packaged context is available without an HTTP request through
`importlib.resources.files('indicium.schema').joinpath('context.jsonld')`.
See [URI scheme](uri-scheme.md) for namespace documentation and instance IDs.
