"""Fixture 1: Simple Chain (A -> B -> C)."""

from visualflow.models import DAG

from tests.fixtures.boxes import make_simple_box


def create_simple_chain() -> DAG:
    """Create simple chain fixture: A -> B -> C."""
    dag = DAG()

    dag.add_node("a", make_simple_box("Task A", width=15))
    dag.add_node("b", make_simple_box("Task B", width=15))
    dag.add_node("c", make_simple_box("Task C", width=15))

    dag.add_edge("a", "b")
    dag.add_edge("b", "c")

    return dag
