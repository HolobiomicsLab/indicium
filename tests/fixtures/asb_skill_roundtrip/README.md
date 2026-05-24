# ASB-Skill round-trip fixture

Canonical JSON-LD example of an indicium document that an ASB-Skill would target.

**Used by:**
- `tests/test_slot_audit_wave1.py::test_fixture_loads_against_schema` (this repo) — schema-validity smoke test.
- `indicium-adapters` round-trip CI test (Plan 1c) — verifies the ASB → indicium adapter round-trips this fixture without information loss.

**What it covers:**
- A Claim using the spec names (`predicate`, `super_pattern`) alongside the required originals (`relation`, `qualifier`).
- An Evidence using the spec names (`eco_code`, `quote_exact`, `quote_location`, `supports_claim`).
- A Source with `doi` + `paragraph_id`.
- A SoftwareEntity with EDAM + bio.tools cross-ref.

**Stability:** Pinned. Changing any IRI in this file is a breaking change for Plan 1c.
