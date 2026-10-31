"""Give generated RDF stable blank-node identifiers before Turtle serialization."""

import sys
from pathlib import Path

from rdflib import Graph
from rdflib.compare import to_canonical_graph


def canonicalize(path):
    """Rewrite a Turtle file deterministically without changing its RDF graph."""
    original = Graph().parse(path, format="turtle")
    canonical = Graph()
    for prefix, namespace in original.namespaces():
        canonical.bind(prefix, namespace)
    canonical += to_canonical_graph(original)
    path.write_text(canonical.serialize(format="turtle"))


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        canonicalize(Path(argument))
