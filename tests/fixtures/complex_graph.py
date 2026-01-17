"""Fixture 7: Complex Graph (real-world mix of patterns)."""

from visualflow.models import DAG

from tests.fixtures.boxes import (
    BOX_POC1, BOX_POC3, BOX_POC8, make_simple_box, make_detailed_box
)


def create_complex_graph() -> DAG:
    """Create complex fixture: mix of patterns from core milestone.

    poc-1 -> poc-3
    poc-1 -> poc-8 -> poc-9 -> poc-11, poc-12, pydantic
                               poc-12 -> poc-13 -> poc-14
    """
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-8", BOX_POC8)
    dag.add_node("poc-9", make_detailed_box("PoC 9", "MIGRATION", "Complete"))
    dag.add_node("poc-11", make_simple_box("PoC 11", width=15))
    dag.add_node("poc-12", make_simple_box("PoC 12", width=15))
    dag.add_node("pydantic", make_simple_box("PYDANTIC", width=15))
    dag.add_node("poc-13", make_simple_box("PoC 13", width=15))
    dag.add_node("poc-14", make_simple_box("PoC 14", width=15))

    # Edges
    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-1", "poc-8")
    dag.add_edge("poc-8", "poc-9")
    dag.add_edge("poc-9", "poc-11")
    dag.add_edge("poc-9", "poc-12")
    dag.add_edge("poc-9", "pydantic")
    dag.add_edge("poc-12", "poc-13")
    dag.add_edge("poc-13", "poc-14")

    return dag
