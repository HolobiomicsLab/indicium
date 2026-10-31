"""Link-rot guard: the namespaces this standard mints must dereference.

A term IRI that returns 404 is a broken standard however good the schema is,
and nothing else in the suite notices: SHACL validation never fetches the
namespace. This module fetches each namespace document with
``Accept: text/turtle``, follows the redirects, and expects HTTP 200.

It needs the network, so it runs only when ``INDICIUM_NETWORK_TESTS=1``::

    INDICIUM_NETWORK_TESTS=1 uv run pytest tests/test_namespace_resolves.py -v

The namespaces come from the generated prefix map, so a prefix added to or
moved in the LinkML schema is checked without editing this file.
"""

from __future__ import annotations

import os
import urllib.error
import urllib.request

import pytest

from indicium.generated.model import linkml_meta

NETWORK = os.environ.get("INDICIUM_NETWORK_TESTS") == "1"
needs_network = pytest.mark.skipif(
    not NETWORK, reason="network test; set INDICIUM_NETWORK_TESTS=1 to run"
)

# Namespaces this project owns: the asb: vocabulary and the indicium: schema id.
OWNED_ROOTS = ("https://w3id.org/asb", "https://w3id.org/indicium")

# Not a prefix of this schema, but registered in the same w3id /asb directory
# and used beside asb: by ASB's validation assertions.
EXTRA_NAMESPACES = {"asbval": "https://w3id.org/asb/validation#"}

# Registered on w3id.org? Only these are expected to fail today.
PENDING = {
    "indicium": (
        "https://w3id.org/indicium/ is not registered yet; the request files are in "
        "docs/release/w3id-indicium/ and wait for the repository to be public "
        "(RELEASING.md, follow-ups)"
    ),
}


def owned_namespaces() -> dict[str, str]:
    """Return {prefix: namespace IRI} for every namespace this project owns."""
    prefixes = linkml_meta.root["prefixes"]
    owned = {
        name: entry["prefix_reference"]
        for name, entry in prefixes.items()
        if entry["prefix_reference"].startswith(OWNED_ROOTS)
    }
    return {**owned, **EXTRA_NAMESPACES}


def document_iri(namespace: str) -> str:
    """Return the IRI a client dereferences for a namespace.

    The fragment of a hash namespace never reaches the server, so the document of
    ``https://w3id.org/asb#`` is ``https://w3id.org/asb``.
    """
    return namespace[:-1] if namespace.endswith("#") else namespace


def fetch_status(iri: str) -> tuple[int, str]:
    """Return (final HTTP status, final URL) after following redirects."""
    request = urllib.request.Request(
        iri, headers={"Accept": "text/turtle", "User-Agent": "indicium-link-rot-guard"}
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.url
    except urllib.error.HTTPError as error:
        return error.code, error.url


def test_owned_namespaces_are_the_expected_ones() -> None:
    """A renamed prefix must not silently drop out of the guard."""
    assert set(owned_namespaces()) == {"asb", "indicium", "asbval"}


@needs_network
@pytest.mark.parametrize(
    "prefix, namespace",
    [
        pytest.param(
            prefix,
            namespace,
            id=prefix,
            marks=[pytest.mark.xfail(strict=True, reason=PENDING[prefix])]
            if prefix in PENDING
            else [],
        )
        for prefix, namespace in sorted(owned_namespaces().items())
    ],
)
def test_namespace_dereferences_to_turtle(prefix: str, namespace: str) -> None:
    status, final_url = fetch_status(document_iri(namespace))
    assert status == 200, f"{prefix}: {namespace} -> HTTP {status} at {final_url}"
