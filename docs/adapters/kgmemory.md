# KGmemory Adapter

!!! note "In preparation"
    The KGmemory adapter documentation will be published here when the
    KGmemory standard is publicly released.

A `claim_jsonld()` adapter for KGmemory is implemented in
`src/indicium/adapters/kgmemory.py` and ships with this package.
It emits a JSON-LD node referencing the KGmemory namespace
(`http://kgmemory.org/ns#SemanticMemory`) so an Indicium claim is
ingestible when KGmemory adopts the vocabulary.
