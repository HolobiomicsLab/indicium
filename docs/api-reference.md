# API Reference

## Package root (`indicium`)

::: indicium
    options:
      members:
        - validate_graph
        - claim_to_insight
        - claim_to_evidence_snippet
        - claim_jsonld
        - MEM_NS

## Vocabulary bases (`indicium.iri_bindings`)

Import these instead of spelling the IRIs; see the [URI scheme](uri-scheme.md).

::: indicium.iri_bindings
    options:
      members:
        - ASB_BASE
        - INDICIUM_BASE
        - asb_term

## Quote verification (`indicium.verify`)

::: indicium.verify
    options:
      members:
        - verify_quote
        - VerificationResult

## ASTRA bridge (`indicium.astra_bridge`)

Typed conversion between `Claim` objects and ASTRA insights. Needs the `astra` extra.

::: indicium.astra_bridge
    options:
      members:
        - claim_to_insight
        - insight_to_claim
        - load_astra_findings
        - load_astra_prior_insights

## Adapters

### ASTRA, dict-based (`indicium.adapters.astra`, deprecated)

::: indicium.adapters.astra
    options:
      members:
        - claim_to_insight

### SciTask (`indicium.adapters.scitask`)

::: indicium.adapters.scitask
    options:
      members:
        - claim_to_evidence_snippet

### KGmemory (`indicium.adapters.kgmemory`)

::: indicium.adapters.kgmemory
    options:
      members:
        - claim_jsonld
        - MEM_NS

## Validation (`indicium.validate`)

::: indicium.validate
    options:
      members:
        - validate_graph
