"""Fixture 6: Standalone Tasks (no connections)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_STANDALONE_A, BOX_STANDALONE_B


def create_standalone() -> DAG:
    """Create standalone fixture: two disconnected nodes."""
    dag = DAG()

    dag.add_node("standalone-a", BOX_STANDALONE_A)
    dag.add_node("standalone-b", BOX_STANDALONE_B)

    # No edges - these are standalone tasks

    return dag
