# SEPIO binding axioms

`binding-axioms.ttl` is an excerpt of the SEPIO ontology by the Monarch
Initiative's SEPIO contributors, licensed under
[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
`provenance.json` records the source URL, ontology version and SHA-256 hashes.
The source copy was supplied by the caller and read on 2026-09-14 UTC.

Only type, label, domain, range, subproperty and inverse axioms for the candidate
bindings are retained, with the blank-node lists needed to express unions.
No domain, range, inverse or class-alignment axiom is inferred or added to the
fixture. In particular, the domain/range of `is_evidence_line_for` follow from
the explicit inverse axiom on `has_evidence_line`; they are not directly
declared on that inverse property in SEPIO.

`test_sepio_bindings.py` uses this independent fixture to check the schema's
Evidence → Claim direction and keep skill reliance separate from authorship.
It also checks JSON-LD expansion, SHACL paths and all three evidence directions.
