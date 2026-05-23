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

## Adapters

### ASTRA (`indicium.adapters.astra`)

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
