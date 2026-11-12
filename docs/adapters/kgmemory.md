# KGmemory Adapter

!!! note "In preparation"
    The KGmemory adapter documentation will be published here when the
    KGmemory standard is publicly released.

A `claim_jsonld()` adapter for KGmemory is implemented in
`src/indicium/adapters/kgmemory.py` and ships with this package.
It emits a JSON-LD node referencing the KGmemory namespace
(`http://kgmemory.org/ns#SemanticMemory`) while typing the same node as
`https://w3id.org/asb#Claim` and expressing its five SuperPattern fields in
the canonical `https://w3id.org/asb#` vocabulary. The result can therefore be
validated with Indicium's Claim shape and remains ingestible when KGmemory
adopts the vocabulary.
