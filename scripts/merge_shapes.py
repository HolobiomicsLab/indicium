"""Write the published SHACL file: the generated shapes plus the supplemental ones.

``validate_graph`` applies both; the release asset must too, so pyshacl on the
published file and the package give the same verdict.
"""

import sys
from pathlib import Path

from rdflib import Graph

from canonicalize_rdf import canonicalize


def merge(target, sources):
    """Write the RDF union of the Turtle sources to target, canonicalized."""
    graph = Graph()
    for source in sources:
        graph.parse(source, format="turtle")
    target.write_text(graph.serialize(format="turtle"))
    canonicalize(target)


if __name__ == "__main__":
    merge(Path(sys.argv[1]), [Path(argument) for argument in sys.argv[2:]])
