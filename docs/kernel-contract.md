# indicium kernel contract

A *kernel* is a small, shared, dependency-light module other projects build on
(the reference example is `src/indicium/verify.py`, `verify_quote`). New kernels
must meet this bar.

## Required properties

1. **Pure-Python, dependency-light.** Standard library only (`re`,
   `dataclasses`, `difflib`, `typing`). No third-party imports, no I/O, no
   network, no global state.
2. **Never raises.** A kernel function returns a typed result for every input,
   including degenerate ones (empty, `None`, wrong-typed entries are coerced or
   mapped to a benign result). Defensive coercion is the *only* try/except, and
   it lives at one documented boundary — not scattered.
3. **One clear job, one frozen result type.** A single public function (or a
   tiny set) and a `@dataclass(frozen=True)` result whose fields are documented
   inline. Structural invariants are stated (e.g. "unverified ⇒ matched_index /
   quote_exact are None").
4. **Additive / non-invasive.** A kernel adds a *verb*; it must not edit
   `generated/model.py`, the SHACL shapes, or any enum. New result fields are
   appended with defaults so existing callers keep working.
5. **Backward-compatible evolution.** New behavior is opt-in (a defaulted
   keyword param) and new outputs are defaulted fields. Existing callers' tests
   pass unchanged across the upgrade.
6. **WHY-not-WHAT comments; tight docstrings.** Comments explain a non-obvious
   invariant or a coercion's reason. Docstrings state the current contract, not
   change history or commit hashes.

## Worked example: `verify_quote`

- ~165 lines, stdlib-only, one public function + one frozen `VerificationResult`.
- Three outcomes (`verified` / `repaired` / `unverified`) with a stated tie-break
  and a documented "unverified ⇒ None span" invariant.
- The only `try/except`-shaped defense is the `None`/non-str candidate coercion,
  with a comment explaining it preserves `matched_index` alignment.
- 1.9.0 added `char_span` (defaulted field) and `punctuation_flexible` (defaulted
  param) additively — prior tests passed unchanged; the suite now covers the
  additions (17 tests).

## Checklist for a new kernel

- [ ] stdlib-only; no I/O / network / globals
- [ ] returns a typed result for every input; never raises
- [ ] single responsibility; frozen result type; invariants documented
- [ ] no edits to model.py / SHACL / enums
- [ ] new behavior opt-in, new outputs defaulted
- [ ] WHY-comments; contract-only docstrings
- [ ] full unit coverage incl. degenerate inputs
