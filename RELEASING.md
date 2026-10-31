# Releasing indicium-standard

The checklist for the first public release, 2.0.0, and the steps that follow it. Run
the steps in order; each one says what to type and what you should see. The state
recorded here was measured on 2026-11-01.

| | State on 2026-11-01 |
|---|---|
| Repository `HolobiomicsLab/indicium` | private; branches `main`, `gh-pages`, four merged or superseded work branches and the wip-* branch (deleted before the flip, step 1) |
| GitHub Pages | not enabled (Pages API 404); `gh-pages` redeployed from `main` on 2026-10-31 by `docs.yml` |
| `docs.yml` | green since the 2.0.0 preparation merged (#6, #7) |
| Tags and GitHub releases | none |
| PyPI and TestPyPI, `indicium-standard` | 404 (name free) |
| GitHub environments | `pypi` exists with a tag-only deployment policy (`v*`); the required-reviewer rule is added after the flip (step 5), the plan does not allow it on a private repository |
| History scan (step 1) | secret formats: 0 over all refs; private names: 0 on `main`, 1 on the superseded branch of 2026-10-30 and on `refs/pull/5/head` (the same commit) |
| `https://w3id.org/asb`, `https://w3id.org/asb/validation`, `https://w3id.org/asb/indicium-ext` | the first two resolve (303, Turtle 200); the third is perma-id pull request 7042 |
| `https://w3id.org/indicium/` | 404, never requested |

Two steps cannot be undone: pushing the tag (step 7), which starts the PyPI upload,
and the upload itself. PyPI never accepts the same version twice, even after the file
is deleted. Making the repository public (step 1) can be reverted in the settings, but
whatever was read, cloned or forked while it was public stays out.

## Before you start

On `main`, with this branch merged:

```bash
uv sync --frozen --extra codegen --extra docs
uv run --frozen pytest -q
make lint
make schema-assets
git status --short
uv run --frozen mkdocs build --strict
uv run --frozen python scripts/check_release.py --tag v2.0.0 --allow-unreleased
gh run list -R HolobiomicsLab/indicium --workflow ci.yml -L 1
```

Expected: pytest reports no failure; `make lint` prints `All checks passed!`;
`git status --short` prints nothing, because `make schema-assets` regenerates the
committed artefacts byte for byte; mkdocs ends with `Documentation built`;
`check_release.py` prints `Release metadata verified for v2.0.0`; the last CI run on
`main` shows `success`.

## 1. Make the repository public

Every branch becomes public, not only `main`, and so does every pull-request ref
(`refs/pull/<n>/head`). A pull-request ref stays readable after its branch is deleted
and after the pull request is closed; only GitHub Support can purge it.

Before the flip, delete the branches you do not want published: the wip-* branch (a
machine-local work branch) and the superseded release-readiness branch of
2026-10-30. Then check the full history for private project names and common secret
formats. This check is required: do not change the visibility until it passes.

Run it in a fresh mirror clone, which fetches every branch, tag and pull-request ref.
The private names are not written in this repository: they are kept, one extended
regular expression per line, in the maintainers' private hub, in
`secrets/redaction-patterns.txt` of `agenticsciencebuilder_dev`. Set `PATTERNS` to
that file's path on your machine:

```bash
gh repo clone HolobiomicsLab/indicium indicium-audit.git -- --mirror
cd indicium-audit.git
PATTERNS=/path/to/agenticsciencebuilder_dev/secrets/redaction-patterns.txt
SECRETS='sk-ant-[A-Za-z0-9_-]{20}|gh[pousr]_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{22}|AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----'
scan_text() {
  git log --all -p --format='%an %ae %cn %ce%n%B'
  git for-each-ref --format='%(refname) %(taggername) %(contents)'
}
test -s "$PATTERNS" && scan_text | grep -c -i -E -f "$PATTERNS"
scan_text | grep -c -E "$SECRETS"
```

Expected: both counts print `0`. The log format keeps the author and committer lines
and the full commit messages next to the diffs, and `for-each-ref` adds the tag
messages. The secret pattern is written so that it does not match its own text: each
bracket expression stands where a literal key character would. `test -s` stops the
first count when the pattern file is missing or empty, so an empty result there is
not a pass.

If a count is not `0`, list the refs whose history matches, without printing the
matches (for the secret count, use `-E "$SECRETS"` in place of `-i -E -f "$PATTERNS"`):

```bash
for ref in $(git for-each-ref --format='%(refname)'); do
  n=$(git log -p --format='%an %ae %cn %ce%n%B' "$ref" | grep -c -i -E -f "$PATTERNS")
  [ "$n" -gt 0 ] && echo "$ref $n"
done
```

Every branch and tag listed must be deleted, and every `refs/pull/<n>` listed purged
through GitHub Support, before the flip. Then clone a fresh mirror and run the check
again.

Then:

```bash
gh repo edit HolobiomicsLab/indicium --visibility public --accept-visibility-change-consequences
gh api repos/HolobiomicsLab/indicium --jq .visibility
```

Expected: `public`.

## 2. Enable GitHub Pages from the `gh-pages` branch

```bash
gh api -X POST repos/HolobiomicsLab/indicium/pages \
  -f "source[branch]=gh-pages" -f "source[path]=/"
gh api repos/HolobiomicsLab/indicium/pages --jq '.html_url, .source'
```

Or in the browser: Settings > Pages > Build and deployment > Source "Deploy from a
branch" > Branch `gh-pages`, folder `/ (root)` > Save.

Expected: `https://holobiomicslab.github.io/indicium/` and
`{"branch":"gh-pages","path":"/"}`.

## 3. Deploy the documentation and check the site

`docs.yml` deploys on every push to `main`, and by hand:

```bash
gh workflow run docs.yml -R HolobiomicsLab/indicium --ref main
gh run watch -R HolobiomicsLab/indicium \
  "$(gh run list -R HolobiomicsLab/indicium --workflow docs.yml -L 1 --json databaseId --jq '.[0].databaseId')"
```

Expected: the run ends green. GitHub then runs its own "pages build and deployment"
job; allow a minute or two, then:

```bash
for p in "" changelog/ uri-scheme/ context.jsonld schema-assets/indicium.owl.ttl; do
  curl -sS -o /dev/null -w "%{http_code} %{content_type} /$p\n" "https://holobiomicslab.github.io/indicium/$p"
done
```

Expected: five lines starting with `200`. The `Homepage` and `Changelog` URLs in
`pyproject.toml` are the first two; they appear on the PyPI page from step 7 on.

## 4. Create the PyPI pending publisher

On pypi.org, logged in as the account that will own the project: Account settings >
Publishing (`https://pypi.org/manage/account/publishing/`) > "Add a new pending
publisher" > GitHub, with:

| Field | Value |
|---|---|
| PyPI Project Name | `indicium-standard` |
| Owner | `HolobiomicsLab` |
| Repository name | `indicium` |
| Workflow name | `release.yml` |
| Environment name | `pypi` |

Expected: the publisher is listed under "Pending publishers". It becomes a normal
trusted publisher at the first upload. No API token is created or stored.

## 5. Create the GitHub environment `pypi`

The environment exists since 2026-11-01, with deployments limited to `v*` tags:

```bash
gh api repos/HolobiomicsLab/indicium/environments --jq '.environments[].name'
gh api repos/HolobiomicsLab/indicium/environments/pypi/deployment-branch-policies --jq '.branch_policies[].name'
```

Expected: `pypi` and `v*`. Once the repository is public (step 1), make every upload
wait for your approval; the plan refuses this rule on a private repository:

```bash
echo '{"reviewers":[{"type":"User","id":22830047}],"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}' | gh api -X PUT repos/HolobiomicsLab/indicium/environments/pypi --input -
```

Expected: the response lists one required reviewer.

## 6. Optional: archive the release on Zenodo

Zenodo archives a GitHub release only if its GitHub integration was switched on for
the repository before the release was published. To give 2.0.0 itself a DOI, do
this now: on zenodo.org, Account > GitHub (`https://zenodo.org/account/settings/github/`),
sync, then switch on `HolobiomicsLab/indicium`. Otherwise the first archived version
is the next release.

## 7. Date the changelog, tag v2.0.0 and push the tag

The `## 2.0.0` heading of `CHANGELOG.md` carries the placeholder `YYYY-MM-DD`, which
`scripts/check_release.py` rejects without `--allow-unreleased`. Replace only the
placeholder with the release date, then refresh the documentation copy and check:

```bash
make docs-changelog
uv run --frozen python scripts/check_release.py --tag v2.0.0
git commit -am "chore(release): date 2.0.0"
git push origin main
```

Expected: `Release metadata verified for v2.0.0`. Once CI on `main` is green:

```bash
git switch main && git pull --ff-only
git tag -a v2.0.0 -m "indicium-standard 2.0.0"
git push origin v2.0.0
gh run watch -R HolobiomicsLab/indicium \
  "$(gh run list -R HolobiomicsLab/indicium --workflow release.yml -L 1 --json databaseId --jq '.[0].databaseId')"
```

Expected: job `build` checks the tag, the version and the changelog date, regenerates
the schema artefacts and finds no difference, runs the tests, lint and the strict
documentation build, builds the wheel and the sdist, runs `twine check --strict` and
checks the installed wheel; job `publish` then uploads to PyPI (after your approval,
if step 5 set a reviewer); job `github-release` last creates the GitHub release. All
three end green.

This step is irreversible once job `publish` has succeeded: 2.0.0 is then final, and a
fix ships as 2.0.1. Before that point:

- If job `build` fails, nothing is published. Fix the cause, delete the tag on the
  remote and locally, and tag again.
- If job `publish` fails, for example on a mistyped publisher field, correct the
  publisher on PyPI and re-run the failed job: `gh run rerun <run-id> --failed`.
- If only job `github-release` fails, PyPI already has the version; re-run that job.

## 8. Verify the release

```bash
gh release view v2.0.0 -R HolobiomicsLab/indicium --json assets --jq '.assets[].name'
```

Expected, in any order: `indicium_standard-2.0.0-py3-none-any.whl`,
`indicium_standard-2.0.0.tar.gz`, `indicium.schema.json`, `indicium.owl.ttl`,
`indicium.shapes.ttl`.

In a clean environment:

```bash
uv venv --python 3.11 /tmp/indicium-check
uv pip install --python /tmp/indicium-check/bin/python "indicium-standard==2.0.0"
/tmp/indicium-check/bin/python -c "import indicium; print(indicium.__version__, indicium.ASB_BASE)"
```

Expected: `2.0.0 https://w3id.org/asb#`. The page `https://pypi.org/project/indicium-standard/`
shows 2.0.0.

## Later versions

A version lives in three files: `version` in `pyproject.toml`, `version:` in
`src/indicium/schema/indicium.yaml` and `version:` in `CITATION.cff`. Bump all three, add a `CHANGELOG.md` section whose
date is the `YYYY-MM-DD` placeholder, and run `make schema-assets`, which writes the
version into the model, the JSON Schema and the OWL ontology (`pav:version`).
`tests/test_schema_version.py` fails while the three files disagree. Then run the
checks of "Before you start" and steps 7 and 8 with the new tag.

## 9. Follow-ups

1. **README and docs.** Uncomment the CI and PyPI badges at the top of `README.md`.
   Remove the "upload to PyPI is pending" paragraph from `README.md`, `docs/index.md`
   and `docs/quickstart.md`.
2. **Register `https://w3id.org/indicium/`.** The files and the procedure are in
   `docs/release/w3id-indicium/` (`NOTES.md`). After the merge, run
   `INDICIUM_NETWORK_TESTS=1 uv run pytest tests/test_namespace_resolves.py -v`; the
   `indicium` case turns from xfail to a failure until its `xfail` marker is removed.
3. **AgenticScienceBuilder.** Remove the `[tool.uv.sources]` path source
   `indicium-standard = { path = "../indicium", editable = true }` from its
   `pyproject.toml`, run `uv lock`, and check that a fresh clone of ASB alone resolves.
   This must come after step 7, never before: without the path source, ASB resolves
   `indicium-standard` from PyPI.
4. **DOI.** When Zenodo has archived a release, add the concept DOI to
   `CITATION.cff` (`doi:` and an `identifiers` entry) and a DOI badge to the README.
5. **Discovery.** Register the `asb` and `indicium` prefixes on prefix.cc and propose
   the vocabulary to LOV (Linked Open Vocabularies) and FAIRsharing. On 2026-10-30,
   prefix.cc served an expired TLS certificate.
6. **Next registration.** Sync the fork `lfnothias/w3id.org` before the next
   perma-id pull request, as the reviewer of #7017 asked.
