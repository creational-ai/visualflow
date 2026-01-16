"""Tests to validate fixture infrastructure."""

import pytest
from conftest import TestGraph, TestNode, TestEdge


class TestFixtureValidation:
    """Validate all fixtures are correctly defined."""

    def test_simple_chain_structure(self, simple_chain: TestGraph) -> None:
        """Verify simple_chain has correct structure."""
        assert simple_chain.name == "simple_chain"
        assert len(simple_chain.nodes) == 3
        assert len(simple_chain.edges) == 2

    def test_diamond_structure(self, diamond: TestGraph) -> None:
        """Verify diamond has correct structure."""
        assert diamond.name == "diamond"
        assert len(diamond.nodes) == 4
        assert len(diamond.edges) == 4

    def test_multiple_roots_structure(self, multiple_roots: TestGraph) -> None:
        """Verify multiple_roots has correct structure."""
        assert multiple_roots.name == "multiple_roots"
        assert len(multiple_roots.nodes) == 3
        assert len(multiple_roots.edges) == 2

    def test_skip_level_structure(self, skip_level: TestGraph) -> None:
        """Verify skip_level has correct structure."""
        assert skip_level.name == "skip_level"
        assert len(skip_level.nodes) == 3
        assert len(skip_level.edges) == 3  # Includes skip edge

    def test_wide_graph_structure(self, wide_graph: TestGraph) -> None:
        """Verify wide_graph has correct structure."""
        assert wide_graph.name == "wide_graph"
        assert len(wide_graph.nodes) == 5
        assert len(wide_graph.edges) == 4

    def test_deep_graph_structure(self, deep_graph: TestGraph) -> None:
        """Verify deep_graph has correct structure."""
        assert deep_graph.name == "deep_graph"
        assert len(deep_graph.nodes) == 6
        assert len(deep_graph.edges) == 5

    def test_complex_graph_structure(self, complex_graph: TestGraph) -> None:
        """Verify complex_graph has correct structure."""
        assert complex_graph.name == "complex_graph"
        assert len(complex_graph.nodes) == 6
        assert len(complex_graph.edges) == 7

    def test_all_scenarios_count(self, all_scenarios: list[TestGraph]) -> None:
        """Verify all_scenarios contains all 7 scenarios."""
        assert len(all_scenarios) == 7
        names = [s.name for s in all_scenarios]
        assert "simple_chain" in names
        assert "diamond" in names
        assert "complex_graph" in names

    def test_node_defaults(self) -> None:
        """Verify TestNode has correct defaults."""
        node = TestNode("test", "Test Label")
        assert node.width == 15
        assert node.height == 3

    def test_node_custom_dimensions(self) -> None:
        """Verify TestNode accepts custom dimensions."""
        node = TestNode("test", "Test Label", width=20, height=5)
        assert node.width == 20
        assert node.height == 5
