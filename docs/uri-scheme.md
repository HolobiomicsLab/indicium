# Indicium stable URI scheme

**Status:** Reference. Stable as of indicium v1.6.0.

Indicium emits two URI forms per entity: a **mutable identity URI** and an immutable **content-hash citation URI**. ASB-Skills and other external consumers target the identity URI for live links and the content-hash URI for citation.

## Identity form (mutable)

```
indicium:claim/<uuid>
indicium:evidence/<uuid>
indicium:source/<uuid>
indicium:software-entity/<uuid>
```

Resolved at `https://w3id.org/indicium/claim/<uuid>` (etc.) once the w3id PR registering `/indicium/` lands.

- `<uuid>` is a UUIDv4 minted by the producing pipeline. Indicium does NOT centrally allocate UUIDs.
- The URI continues to resolve to the latest version of the entity. Editing a Claim does not break the URI.

## Citation form (content-addressed, immutable)

```
indicium:claim/<uuid>@sha256:<hex>
indicium:evidence/<uuid>@sha256:<hex>
```

- `<hex>` is the SHA-256 of the canonical JSON-LD form of the entity (deterministic JCS-style ordering; spec deferred to v1.7 but the hash is computed today by serialising with sorted keys + UTF-8 + no whitespace).
- Citation form is what manuscripts and `metadata.claims` IRIs in SKILL.md frontmatter SHOULD use, so the cited assertion cannot drift.

## Cross-reference to other w3id namespaces

| Namespace | Owner | Resolves to |
|---|---|---|
| `w3id.org/indicium/` | this repo | indicium-served entity URIs |
| `w3id.org/holobiomicslab/asb-skill/...` | `asb-skill-collections` | ASB-Skill IRIs (Plan 3a) |
| `w3id.org/holobiomicslab/asb-tool/...` | `asb-skill-collections` | ASB-Tool IRIs |

ASB-Tool IRIs MAY appear as the `SoftwareEntity.identifier` value, allowing an ASB-Tool to live simultaneously as an indicium entity (graph node) and an ASB release artefact (citable software record).

## w3id PR (coordination, not done in this plan)

This plan generates `docs/context.jsonld` (Task 11) at the path the w3id redirect WILL serve, but does not submit the [perma-id/w3id.org](https://github.com/perma-id/w3id.org) PR itself. Submission is coordinated with ASB's `holobiomicslab/` registration; tracked in the IDEAS.md "Phase 2" backlog.

Until w3id is live, downstream consumers SHOULD pin to a versioned GitHub Pages URL:

```
https://holobiomicslab.github.io/indicium/context.jsonld
```

This file is auto-published by the existing `mkdocs` build (Task 11 places `context.jsonld` under `docs/` so mkdocs copies it into the published site).
