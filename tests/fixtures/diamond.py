"""Fixture 2: Diamond Pattern (merge and fan-out)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC1, BOX_POC2, BOX_POC3, BOX_POC7


def create_diamond() -> DAG:
    """Create diamond fixture: poc-1, poc-2 -> poc-3 -> poc-7."""
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-2", BOX_POC2)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-7", BOX_POC7)

    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-2", "poc-3")
    dag.add_edge("poc-3", "poc-7")

    return dag
