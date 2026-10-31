# Notes for the w3id /indicium request

`.htaccess` and `README.md` in this directory are the two files of a pull request to
[perma-id/w3id.org](https://github.com/perma-id/w3id.org), copied into `ids/indicium/`.
They are not part of the documentation site.

## Prerequisites

Do not open the pull request before both hold. A permanent identifier that redirects to
404 pages is worse than none.

1. **The repository `HolobiomicsLab/indicium` is public.** Every RDF target is a
   `raw.githubusercontent.com` URL in this repository, and raw files of a private
   repository return 404 to anonymous readers.
2. **GitHub Pages is enabled and the docs site is deployed.** The HTML target is
   `https://holobiomicslab.github.io/indicium/`. Pages is not enabled today
   (the Pages API returns 404 for the repository, measured 2026-10-30).

The versioned rules (`/indicium/<X.Y.Z>/...`) also need the tag `v<X.Y.Z>` to exist;
submit after `v2.0.0` is pushed.

## Where the targets point, and the alternative

HTML goes to the documentation site on GitHub Pages. The RDF and JSON-LD files go to
`raw.githubusercontent.com`, for two reasons: a raw URL can name a release tag, so
`/indicium/<X.Y.Z>/<file>` resolves to a fixed document, and raw files are served as
soon as the repository is public, without depending on a successful docs deploy.

The cost is the media type. Measured on 2026-10-30:

| Host | `.ttl` | `.jsonld` |
|---|---|---|
| `raw.githubusercontent.com` | `text/plain; charset=utf-8` | `text/plain; charset=utf-8` |
| GitHub Pages (`w3c.github.io`, `linkml.io`, both `server: GitHub.com`) | `text/turtle; charset=utf-8` | `application/ld+json` |

Most RDF tooling picks a parser from the file extension or an explicit format argument,
so `text/plain` works in practice (the OBO Relation Ontology,
`http://purl.obolibrary.org/obo/ro.owl`, resolves to `raw.githubusercontent.com` as
`text/plain` too). A client that dispatches on `Content-Type` alone does better with
Pages. An earlier note in the development hub recorded Pages serving these files as
`application/octet-stream` (measured 2026-07-30); that no longer holds.

The site built by `docs.yml` contains `context.jsonld` and `schema-assets/*.ttl`
(checked in a local `mkdocs build`). To serve the unversioned files from Pages with the
correct media types, replace the four `main` targets with:

```apache
RewriteRule ^context\.jsonld$ https://holobiomicslab.github.io/indicium/context.jsonld [R=302,L]
RewriteRule ^(indicium\.owl\.ttl|indicium\.shapes\.ttl|indicium\.schema\.json)$ https://holobiomicslab.github.io/indicium/schema-assets/$1 [R=302,L]
```

and the two negotiated targets with
`https://holobiomicslab.github.io/indicium/schema-assets/indicium.owl.ttl` and
`https://holobiomicslab.github.io/indicium/context.jsonld`. The tagged rules stay on raw.
Either way the identifiers do not change; only the targets in `.htaccess` do.

## Rule behaviour

Measured on 2026-10-30 against a local Apache 2.4.66 with `mod_rewrite`, the directory
served at `/indicium/`. Not yet measured on w3id.org itself.

| Request | Accept | Result |
|---|---|---|
| `/indicium/` | `text/turtle` | 303 to `indicium.owl.ttl` (raw, main) |
| `/indicium/` | `application/ld+json` | 303 to `src/indicium/schema/context.jsonld` (raw, main) |
| `/indicium/` | `text/html` or other | 303 to the documentation site |
| `/indicium/IndiciumDocument` | `text/turtle` | 303 to `indicium.owl.ttl` |
| `/indicium/context.jsonld` | any | 302 to `src/indicium/schema/context.jsonld` (raw, main) |
| `/indicium/indicium.owl.ttl`, `indicium.shapes.ttl`, `indicium.schema.json` | any | 302 to `docs/schema-assets/<file>` (raw, main) |
| `/indicium/2.0.0/indicium.owl.ttl` | any | 302 to the same file at tag `v2.0.0` |
| `/indicium/claim/<uuid>` | any | 404: no service resolves claim instances |

## Before submitting

1. Check each target returns 200 for an anonymous reader:

   ```bash
   for u in \
     https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/src/indicium/schema/context.jsonld \
     https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/docs/schema-assets/indicium.owl.ttl \
     https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/docs/schema-assets/indicium.shapes.ttl \
     https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/docs/schema-assets/indicium.schema.json \
     https://raw.githubusercontent.com/HolobiomicsLab/indicium/v2.0.0/docs/schema-assets/indicium.owl.ttl \
     https://holobiomicslab.github.io/indicium/ ; do
     curl -sS -o /dev/null -w "%{http_code} $u\n" "$u"
   done
   ```

   A 200 is not enough for the context: `docs/context.jsonld` is a symlink, and
   `raw.githubusercontent.com` serves a symlink as its link text with status 200. The
   rules therefore point at `src/indicium/schema/context.jsonld`. Check the content:

   ```bash
   curl -sL https://raw.githubusercontent.com/HolobiomicsLab/indicium/main/src/indicium/schema/context.jsonld | python3 -m json.tool >/dev/null && echo ok
   ```

2. Bring the fork up to date first. On the `/asb` request (perma-id/w3id.org#7017,
   merged 2026-10-29) the reviewer asked that the fork `lfnothias/w3id.org` be synced
   before the next pull request.
3. Add `ids/indicium/.htaccess` and `ids/indicium/README.md` on a new branch of the
   fork and open the pull request. Suggested title: `Register /indicium`.
4. After the merge, run the link-rot guard; the `indicium` case then passes, and its
   `xfail` marker must be removed (the marker is strict, so the run fails until it is):

   ```bash
   INDICIUM_NETWORK_TESTS=1 uv run pytest tests/test_namespace_resolves.py -v
   ```
