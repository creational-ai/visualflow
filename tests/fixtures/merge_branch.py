"""Fixture 4: Merge with Independent Branch."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC1, BOX_POC2, BOX_POC3, BOX_POC8


def create_merge_branch() -> DAG:
    """Create merge + branch fixture.

    poc-1 -> poc-3 (merged with poc-2)
    poc-1 -> poc-8 (independent branch)
    """
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-2", BOX_POC2)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-8", BOX_POC8)

    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-2", "poc-3")
    dag.add_edge("poc-1", "poc-8")

    return dag
