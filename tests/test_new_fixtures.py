"""Tests for new fixtures with real box content."""

import pytest

from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class TestSimpleChainFixture:
    """Tests for simple_chain fixture."""

    def test_has_three_nodes(self) -> None:
        """Simple chain has 3 nodes."""
        dag = create_simple_chain()
        assert len(dag.nodes) == 3

    def test_has_two_edges(self) -> None:
        """Simple chain has 2 edges."""
        dag = create_simple_chain()
        assert len(dag.edges) == 2

    def test_nodes_have_content(self) -> None:
        """All nodes have box content."""
        dag = create_simple_chain()
        for node in dag.nodes.values():
            assert node.content
            assert node.width > 0
            assert node.height > 0


class TestDiamondFixture:
    """Tests for diamond fixture."""

    def test_has_four_nodes(self) -> None:
        """Diamond has 4 nodes."""
        dag = create_diamond()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Diamond has 3 edges."""
        dag = create_diamond()
        assert len(dag.edges) == 3


class TestWideFanoutFixture:
    """Tests for wide_fanout fixture."""

    def test_has_six_nodes(self) -> None:
        """Wide fanout has 6 nodes."""
        dag = create_wide_fanout()
        assert len(dag.nodes) == 6

    def test_has_five_edges(self) -> None:
        """Wide fanout has 5 edges from single parent."""
        dag = create_wide_fanout()
        assert len(dag.edges) == 5
        # All edges should come from poc-3
        for edge in dag.edges:
            assert edge.source == "poc-3"


class TestMergeBranchFixture:
    """Tests for merge_branch fixture."""

    def test_has_four_nodes(self) -> None:
        """Merge branch has 4 nodes."""
        dag = create_merge_branch()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Merge branch has 3 edges."""
        dag = create_merge_branch()
        assert len(dag.edges) == 3


class TestSkipLevelFixture:
    """Tests for skip_level fixture."""

    def test_has_four_nodes(self) -> None:
        """Skip level has 4 nodes."""
        dag = create_skip_level()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Skip level has 3 edges including skip edge."""
        dag = create_skip_level()
        assert len(dag.edges) == 3

    def test_has_skip_edge(self) -> None:
        """Skip level has direct a->c2 edge."""
        dag = create_skip_level()
        skip_edges = [e for e in dag.edges if e.source == "a" and e.target == "c2"]
        assert len(skip_edges) == 1


class TestStandaloneFixture:
    """Tests for standalone fixture."""

    def test_has_two_nodes(self) -> None:
        """Standalone has 2 nodes."""
        dag = create_standalone()
        assert len(dag.nodes) == 2

    def test_has_no_edges(self) -> None:
        """Standalone has no edges."""
        dag = create_standalone()
        assert len(dag.edges) == 0


class TestComplexGraphFixture:
    """Tests for complex_graph fixture."""

    def test_has_nine_nodes(self) -> None:
        """Complex graph has 9 nodes."""
        dag = create_complex_graph()
        assert len(dag.nodes) == 9

    def test_has_eight_edges(self) -> None:
        """Complex graph has 8 edges."""
        dag = create_complex_graph()
        assert len(dag.edges) == 8

    def test_nodes_have_varying_sizes(self) -> None:
        """Nodes have different box sizes."""
        dag = create_complex_graph()
        widths = set(n.width for n in dag.nodes.values())
        # Should have at least 2 different widths
        assert len(widths) >= 2
