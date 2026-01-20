"""Tests for partition_dag function."""

import pytest

from visualflow.models import DAG
from visualflow.partition import partition_dag


class TestPartitionDagEmpty:
    """Tests for partition_dag with empty or minimal DAGs."""

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty subgraphs and empty standalones."""
        dag = DAG()
        connected, standalones = partition_dag(dag)
        assert connected == []
        assert len(standalones.nodes) == 0

    def test_single_standalone_node(self) -> None:
        """Single node with no edges is standalone."""
        dag = DAG()
        dag.add_node("a", "Node A")
        connected, standalones = partition_dag(dag)
        assert connected == []
        assert len(standalones.nodes) == 1
        assert "a" in standalones.nodes


class TestPartitionDagAllConnected:
    """Tests for DAGs where all nodes are connected (Scenario D)."""

    def test_simple_chain_all_connected(self) -> None:
        """A -> B -> C: all connected, no standalones."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 3
        assert len(standalones.nodes) == 0

    def test_diamond_all_connected(self) -> None:
        """Diamond pattern: A -> B, A -> C, B -> D, C -> D."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_node("d", "D")
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 4
        assert len(standalones.nodes) == 0


class TestPartitionDagAllStandalone:
    """Tests for DAGs where all nodes are standalone (Scenario E)."""

    def test_multiple_standalones_no_edges(self) -> None:
        """Multiple nodes with no edges: all standalone."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_node("d", "D")
        dag.add_node("e", "E")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 0
        assert len(standalones.nodes) == 5


class TestPartitionDagMixed:
    """Tests for DAGs with mixed connected and standalone nodes (Scenario A/B)."""

    def test_one_connected_pair_one_standalone(self) -> None:
        """A -> B connected, C standalone."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 2
        assert "a" in connected[0].nodes
        assert "b" in connected[0].nodes
        assert len(standalones.nodes) == 1
        assert "c" in standalones.nodes

    def test_mixed_seven_connected_three_standalone(self) -> None:
        """7 connected nodes, 3 standalone - per TODO example."""
        dag = DAG()
        # Connected graph: A -> B -> C -> D -> E, B -> F, C -> G
        for node_id in ["a", "b", "c", "d", "e", "f", "g"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")
        dag.add_edge("b", "f")
        dag.add_edge("c", "g")

        # Standalone nodes
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_node("z", "Z")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 7
        assert len(standalones.nodes) == 3


class TestPartitionDagMultipleSubgraphs:
    """Tests for DAGs with multiple disconnected subgraphs (Scenario C)."""

    def test_two_disconnected_subgraphs(self) -> None:
        """A->B->C (3 nodes) and X->Y (2 nodes) - sorted by size."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        # Largest first
        assert len(connected[0].nodes) == 3
        assert len(connected[1].nodes) == 2
        assert len(standalones.nodes) == 0

    def test_multiple_subgraphs_with_standalones(self) -> None:
        """A->B->C->D->E (5) + X->Y (2) + P, Q, R (3 standalone)."""
        dag = DAG()
        # Large subgraph
        for node_id in ["a", "b", "c", "d", "e"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")

        # Small subgraph
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        # Standalones
        dag.add_node("p", "P")
        dag.add_node("q", "Q")
        dag.add_node("r", "R")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        assert len(connected[0].nodes) == 5  # Largest first
        assert len(connected[1].nodes) == 2
        assert len(standalones.nodes) == 3

    def test_subgraphs_sorted_by_size_descending(self) -> None:
        """Subgraphs should be sorted largest to smallest."""
        dag = DAG()
        # Small subgraph (added first)
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        # Large subgraph (added second)
        for node_id in ["a", "b", "c", "d", "e"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        # Should still be largest first regardless of insertion order
        assert len(connected[0].nodes) == 5
        assert len(connected[1].nodes) == 2


class TestPartitionDagEdgePreservation:
    """Tests that edges are correctly preserved in subgraphs."""

    def test_edges_preserved_in_subgraph(self) -> None:
        """Subgraph should contain all relevant edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("a", "c")  # Skip-level edge

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        subgraph = connected[0]
        assert len(subgraph.edges) == 3
        edge_pairs = {(e.source, e.target) for e in subgraph.edges}
        assert ("a", "b") in edge_pairs
        assert ("b", "c") in edge_pairs
        assert ("a", "c") in edge_pairs

    def test_standalones_have_no_edges(self) -> None:
        """Standalone DAG should have no edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_edge("a", "b")
        dag.add_node("c", "C")  # standalone

        connected, standalones = partition_dag(dag)
        assert len(standalones.edges) == 0


class TestPartitionDagExport:
    """Tests for partition_dag export from visualflow package."""

    def test_partition_dag_importable_from_package(self) -> None:
        """partition_dag can be imported from visualflow."""
        from visualflow import partition_dag
        assert callable(partition_dag)

    def test_partition_dag_in_all(self) -> None:
        """partition_dag is in __all__."""
        import visualflow
        assert "partition_dag" in visualflow.__all__
