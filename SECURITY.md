# Security policy

## Supported versions

| Version | Supported |
|---|---|
| 2.x | yes |
| 1.x | no |

Fixes ship as a new patch release on PyPI (`indicium-standard`); published releases
are never modified.

## Reporting a vulnerability

Indicium is a vocabulary and a validation library. It reads RDF, JSON-LD and YAML
with rdflib, pyshacl and PyYAML and makes no network calls of its own. A
vulnerability here would typically be an input that makes `validate_graph` or the
loaders misbehave, or a published artefact that does not match its source.

Report it privately to louis-felix.nothias@cnrs.fr with the version, a minimal input
and what you observed. Do not open a public issue for a report that could be
exploited before a fix is available. You will receive an acknowledgement within a
week and a fix or a decision within a month; the changelog credits reporters who
want to be named.

Dependency advisories are handled by Dependabot pull requests on this repository.
