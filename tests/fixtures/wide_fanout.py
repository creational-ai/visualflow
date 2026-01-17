"""Fixture 3: Wide Fan-out (one parent, many children)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC3, BOX_POC4, BOX_POC5, BOX_POC6, make_simple_box


def create_wide_fanout() -> DAG:
    """Create wide fan-out fixture: poc-3 -> poc-4, poc-5, poc-6, bugs, pydantic."""
    dag = DAG()

    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-4", BOX_POC4)
    dag.add_node("poc-5", BOX_POC5)
    dag.add_node("poc-6", BOX_POC6)
    dag.add_node("bugs", make_simple_box("BUGS", width=15))
    dag.add_node("pydantic", make_simple_box("PYDANTIC", width=15))

    dag.add_edge("poc-3", "poc-4")
    dag.add_edge("poc-3", "poc-5")
    dag.add_edge("poc-3", "poc-6")
    dag.add_edge("poc-3", "bugs")
    dag.add_edge("poc-3", "pydantic")

    return dag
