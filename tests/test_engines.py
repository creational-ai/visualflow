"""Tests for layout engines."""

import pytest

from visualflow.models import DAG, LayoutResult, NodePosition
from visualflow.engines import LayoutEngine, GrandalfEngine, GraphvizEngine
from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class MockEngine:
    """Mock engine that implements LayoutEngine protocol."""

    def compute(self, dag: DAG) -> LayoutResult:
        """Simple mock layout: stack nodes vertically."""
        positions: dict[str, NodePosition] = {}
        y = 0
        for node_id, node in dag.nodes.items():
            positions[node_id] = NodePosition(node=node, x=0, y=y)
            y += node.height + 2
        return LayoutResult(
            positions=positions,
            width=max((n.width for n in dag.nodes.values()), default=0),
            height=y,
        )


class TestLayoutEngineProtocol:
    """Tests for LayoutEngine protocol."""

    def test_mock_engine_implements_protocol(self) -> None:
        """MockEngine satisfies LayoutEngine protocol."""
        engine: LayoutEngine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Node A")
        result = engine.compute(dag)
        assert isinstance(result, LayoutResult)

    def test_protocol_requires_compute_method(self) -> None:
        """LayoutEngine requires compute method."""
        # This is a compile-time check via type hints
        # Runtime verification that protocol works
        engine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Test")
        result = engine.compute(dag)
        assert "a" in result.positions


class TestGrandalfEngineBasic:
    """Basic tests for GrandalfEngine."""

    def test_engine_creation(self) -> None:
        """GrandalfEngine can be created."""
        engine = GrandalfEngine()
        assert engine.horizontal_spacing == 4
        assert engine.vertical_spacing == 2

    def test_engine_custom_spacing(self) -> None:
        """GrandalfEngine accepts custom spacing."""
        engine = GrandalfEngine(horizontal_spacing=8, vertical_spacing=4)
        assert engine.horizontal_spacing == 8
        assert engine.vertical_spacing == 4

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty result."""
        engine = GrandalfEngine()
        dag = DAG()
        result = engine.compute(dag)
        assert len(result.positions) == 0
        assert result.width == 0
        assert result.height == 0

    def test_single_node(self) -> None:
        """Single node is positioned."""
        engine = GrandalfEngine()
        dag = DAG()
        dag.add_node("a", "Test Node")
        result = engine.compute(dag)
        assert "a" in result.positions
        assert result.positions["a"].x >= 0
        assert result.positions["a"].y >= 0


class TestGrandalfEngineSimpleChain:
    """Tests for GrandalfEngine with simple chain fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert len(result.positions) == 3
        assert "a" in result.positions
        assert "b" in result.positions
        assert "c" in result.positions

    def test_level_ordering(self) -> None:
        """Parent nodes are above child nodes (smaller y)."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        y_a = result.positions["a"].y
        y_b = result.positions["b"].y
        y_c = result.positions["c"].y
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_canvas_size_positive(self) -> None:
        """Canvas has positive dimensions."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert result.width > 0
        assert result.height > 0

    def test_positions_are_integers(self) -> None:
        """Positions are integer coordinates."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        for pos in result.positions.values():
            assert isinstance(pos.x, int)
            assert isinstance(pos.y, int)


class TestGrandalfEngineDiamond:
    """Tests for GrandalfEngine with diamond fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        assert len(result.positions) == 4

    def test_roots_above_children(self) -> None:
        """Root nodes are above their children."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc2 = result.positions["poc-2"].y
        y_poc3 = result.positions["poc-3"].y
        assert y_poc1 < y_poc3, "poc-1 should be above poc-3"
        assert y_poc2 < y_poc3, "poc-2 should be above poc-3"

    def test_siblings_same_level(self) -> None:
        """Sibling nodes at same level have similar y."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc2 = result.positions["poc-2"].y
        # Allow some tolerance
        assert abs(y_poc1 - y_poc2) < 10, f"poc-1 and poc-2 should be same level"


class TestGrandalfEngineWideFanout:
    """Tests for GrandalfEngine with wide fanout fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All 6 nodes get positions."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        assert len(result.positions) == 6

    def test_children_below_parent(self) -> None:
        """All children are below parent."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        y_parent = result.positions["poc-3"].y
        for child_id in ["poc-4", "poc-5", "poc-6", "bugs", "pydantic"]:
            y_child = result.positions[child_id].y
            assert y_child > y_parent, f"{child_id} should be below poc-3"

    def test_children_spread_horizontally(self) -> None:
        """Children have different x positions."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        x_positions = [
            result.positions[c].x
            for c in ["poc-4", "poc-5", "poc-6", "bugs", "pydantic"]
        ]
        unique_xs = set(x_positions)
        assert len(unique_xs) >= 2, "Children should be spread horizontally"


class TestGrandalfEngineStandalone:
    """Tests for GrandalfEngine with standalone fixture."""

    def test_disconnected_nodes_positioned(self) -> None:
        """Disconnected nodes still get positions."""
        engine = GrandalfEngine()
        dag = create_standalone()
        result = engine.compute(dag)
        assert len(result.positions) == 2
        assert "standalone-a" in result.positions
        assert "standalone-b" in result.positions


class TestGrandalfEngineNoOverlap:
    """Tests that verify no boxes overlap."""

    def _boxes_overlap(
        self, pos1: NodePosition, pos2: NodePosition
    ) -> bool:
        """Check if two positioned boxes overlap."""
        # Box 1 bounds
        x1_min, x1_max = pos1.x, pos1.x + pos1.node.width
        y1_min, y1_max = pos1.y, pos1.y + pos1.node.height

        # Box 2 bounds
        x2_min, x2_max = pos2.x, pos2.x + pos2.node.width
        y2_min, y2_max = pos2.y, pos2.y + pos2.node.height

        # Check for overlap
        x_overlap = x1_min < x2_max and x1_max > x2_min
        y_overlap = y1_min < y2_max and y1_max > y2_min

        return x_overlap and y_overlap

    def test_simple_chain_no_overlap(self) -> None:
        """Simple chain has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_diamond_no_overlap(self) -> None:
        """Diamond has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_complex_graph_no_overlap(self) -> None:
        """Complex graph has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_complex_graph()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2), (
                    f"{pos1.node.id} overlaps {pos2.node.id}"
                )


class TestGraphvizEngineAvailability:
    """Tests for Graphviz availability check."""

    def test_is_available_returns_bool(self) -> None:
        """is_available returns boolean."""
        result = GraphvizEngine.is_available()
        assert isinstance(result, bool)


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineBasic:
    """Basic tests for GraphvizEngine."""

    def test_engine_creation(self) -> None:
        """GraphvizEngine can be created."""
        engine = GraphvizEngine()
        assert engine.horizontal_spacing == 4
        assert engine.vertical_spacing == 2

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty result."""
        engine = GraphvizEngine()
        dag = DAG()
        result = engine.compute(dag)
        assert len(result.positions) == 0

    def test_single_node(self) -> None:
        """Single node is positioned."""
        engine = GraphvizEngine()
        dag = DAG()
        dag.add_node("a", "Test Node")
        result = engine.compute(dag)
        assert "a" in result.positions


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineSimpleChain:
    """Tests for GraphvizEngine with simple chain fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert len(result.positions) == 3

    def test_level_ordering(self) -> None:
        """Parent nodes are above child nodes (smaller y)."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        y_a = result.positions["a"].y
        y_b = result.positions["b"].y
        y_c = result.positions["c"].y
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineDiamond:
    """Tests for GraphvizEngine with diamond fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GraphvizEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        assert len(result.positions) == 4

    def test_roots_above_children(self) -> None:
        """Root nodes are above their children."""
        engine = GraphvizEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc3 = result.positions["poc-3"].y
        assert y_poc1 < y_poc3, "poc-1 should be above poc-3"


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineNoOverlap:
    """Tests that verify no boxes overlap with Graphviz."""

    def _boxes_overlap(
        self, pos1: NodePosition, pos2: NodePosition
    ) -> bool:
        """Check if two positioned boxes overlap."""
        x1_min, x1_max = pos1.x, pos1.x + pos1.node.width
        y1_min, y1_max = pos1.y, pos1.y + pos1.node.height
        x2_min, x2_max = pos2.x, pos2.x + pos2.node.width
        y2_min, y2_max = pos2.y, pos2.y + pos2.node.height
        x_overlap = x1_min < x2_max and x1_max > x2_min
        y_overlap = y1_min < y2_max and y1_max > y2_min
        return x_overlap and y_overlap

    def test_simple_chain_no_overlap(self) -> None:
        """Simple chain has no overlapping boxes."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_complex_graph_no_overlap(self) -> None:
        """Complex graph has no overlapping boxes."""
        engine = GraphvizEngine()
        dag = create_complex_graph()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)
