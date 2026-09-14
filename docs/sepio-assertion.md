# SEPIO assertions and Indicium compatibility

The ASB validation bridge uses the following external annotations. They are
separate from Indicium's claim lifecycle (`claim_status`) and its ECO evidence
classification (`eco_code`). The ASB namespace is
`https://w3id.org/asb/validation#`.

| Annotation | Predicate | Values |
|---|---|---|
| Evidence direction | `sepio:0000183` | `sepio:0000403` supporting, `sepio:0000404` disputing, `sepio:0000405` inconclusive |
| Automatic assertion evidence | `ro:0002558` | `eco:0000501` |

Here `sepio:`, `ro:` and `eco:` expand to
`http://purl.obolibrary.org/obo/SEPIO_`, `http://purl.obolibrary.org/obo/RO_`
and `http://purl.obolibrary.org/obo/ECO_`. The packaged JSON-LD context marks
these underscore-ending bases with `@prefix: true` so compact IRIs expand.

```turtle
@prefix asbval: <https://w3id.org/asb/validation#> .
@prefix sepio: <http://purl.obolibrary.org/obo/SEPIO_> .
@prefix ro: <http://purl.obolibrary.org/obo/RO_> .
@prefix eco: <http://purl.obolibrary.org/obo/ECO_> .

<urn:example:assessment> a asbval:ClaimAssessment ;
    sepio:0000183 sepio:0000403 ;
    ro:0002558 eco:0000501 .
```

The core LinkML model has no dedicated ASB assessment class or direction slot.
Its non-closed SHACL shapes permit these additional annotations, but do not
validate their values on ASB assessment nodes. Passing Indicium SHACL therefore
does not certify an ASB validation record. ASB owns that validation contract.
SEPIO defines evidence direction on an evidence line; ASB's assessment class
must supply its own alignment to that model.

## Legacy bindings requiring a release decision

The [SEPIO ontology, release 2023-06-13](https://raw.githubusercontent.com/monarch-initiative/SEPIO-ontology/master/sepio.owl)
confirms three conflicts in the earlier reference page:

| Existing Indicium use | Actual SEPIO meaning | Smallest migration |
|---|---|---|
| `Evidence.supports_claim` uses `sepio:0000007` from evidence to claim | `has_supporting_evidence_line` runs from a proposition to evidence | Use the existing local `for_claim` slot for evidence-to-claim links; export the SEPIO triple in the other direction. A removal or rebinding of the legacy slot needs a consumer migration. |
| Context alias `asserts` uses `sepio:0000130` from skill to claim | `authored_by` runs from information content to its author | Deprecate the alias for reliance. Authorship should be claim-to-agent; reliance needs a separately chosen predicate, because relying on a claim does not make a skill its author. |
| The old page calls `sepio:0000174` a qualifier property | It is the `statement` class | Remove that property recommendation. |

The first two legacy URI bindings remain available for compatibility. They are
not recommended SEPIO export patterns. The third error was documentation only
and has been removed. The current ASB direction/ECO/RO annotations above do not
use any of these conflicting terms.

## Evidence links

The schema's `Evidence` class binds to the SEPIO evidence-line class
`sepio:0000002`. Its distinct local slots include `indicium:quote`,
`indicium:quote_exact`, `indicium:of_source` and `indicium:for_claim`. They must
not be silently moved into `asb:` or collapsed into one property.

A correctly directed SEPIO support triple is:

```turtle
@prefix asb: <https://w3id.org/asb#> .
@prefix indicium: <https://w3id.org/indicium/> .
@prefix sepio: <http://purl.obolibrary.org/obo/SEPIO_> .

<urn:example:claim> a asb:Claim ;
    asb:context "in vitro" ; asb:subject "A" ;
    asb:qualifier "inhibits" ; asb:relation "inhibits" ; asb:object "B" ;
    sepio:0000007 <urn:example:evidence> .
<urn:example:evidence> a sepio:0000002 ;
    indicium:for_claim <urn:example:claim> ;
    indicium:quote_exact "A inhibits B" .
```

The packaged context is available without an HTTP request through
`importlib.resources.files('indicium.schema').joinpath('context.jsonld')`.
See [URI scheme](uri-scheme.md) for the namespace deposit and instance identifiers.
