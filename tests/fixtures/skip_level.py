"""Fixture 5: Skip-level with Sibling."""

from visualflow.models import DAG

from tests.fixtures.boxes import make_simple_box


def create_skip_level() -> DAG:
    """Create skip-level fixture.

    A -> B -> C1
    A -> C2 (skip-level, directly to bottom row)
    """
    dag = DAG()

    dag.add_node("a", make_simple_box("Root A", width=20))
    dag.add_node("b", make_simple_box("Middle B", width=20))
    dag.add_node("c1", make_simple_box("Child C1", width=20))
    dag.add_node("c2", make_simple_box("Child C2", width=20))

    dag.add_edge("a", "b")
    dag.add_edge("b", "c1")
    dag.add_edge("a", "c2")  # Skip-level edge

    return dag
