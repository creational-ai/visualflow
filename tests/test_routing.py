"""Tests for edge routing."""

import pytest

from visualflow.models import DAG, Edge, NodePosition, Node
from visualflow.routing import SimpleRouter, EdgeRouter


def make_test_node(id: str, width: int = 10, height: int = 3) -> Node:
    """Create a test node with specified dimensions."""
    content = "+" + "-" * (width - 2) + "+\n"
    content += "|" + " " * (width - 2) + "|\n"
    content += "+" + "-" * (width - 2) + "+"
    return Node(id=id, content=content)


class TestSimpleRouterProtocol:
    """Tests that SimpleRouter implements EdgeRouter protocol."""

    def test_implements_edge_router(self) -> None:
        """SimpleRouter implements EdgeRouter protocol."""
        router = SimpleRouter()
        # Protocol check - should have route method with correct signature
        assert hasattr(router, "route")
        assert callable(router.route)


class TestSimpleRouterVertical:
    """Tests for vertical edge routing."""

    def test_vertical_aligned_nodes(self) -> None:
        """Aligned nodes get straight vertical edge."""
        router = SimpleRouter()

        # Create two vertically aligned nodes
        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),   # Top node
            "b": NodePosition(node=node_b, x=5, y=6),   # Below with gap
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        assert len(paths) == 1
        path = paths[0]
        assert path.source_id == "a"
        assert path.target_id == "b"
        # Single vertical segment
        assert len(path.segments) == 1
        x1, y1, x2, y2 = path.segments[0]
        assert x1 == x2  # Vertical line

    def test_simple_chain_routing(self) -> None:
        """Simple chain A -> B -> C routes vertically."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)
        node_c = make_test_node("c", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
            "b": NodePosition(node=node_b, x=5, y=5),
            "c": NodePosition(node=node_c, x=5, y=10),
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="b", target="c"),
        ]

        paths = router.route(positions, edges)

        assert len(paths) == 2


class TestSimpleRouterZShape:
    """Tests for Z-shaped edge routing."""

    def test_offset_nodes_z_shape(self) -> None:
        """Horizontally offset nodes get Z-shaped edge."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),   # Left
            "b": NodePosition(node=node_b, x=20, y=6), # Right and below
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        assert len(paths) == 1
        path = paths[0]
        # Z-shape has 3 segments: down, across, down
        assert len(path.segments) == 3

        # First segment is vertical (down from source)
        x1, y1, x2, y2 = path.segments[0]
        assert x1 == x2  # Vertical

        # Second segment is horizontal
        x1, y1, x2, y2 = path.segments[1]
        assert y1 == y2  # Horizontal

        # Third segment is vertical (down to target)
        x1, y1, x2, y2 = path.segments[2]
        assert x1 == x2  # Vertical


class TestSimpleRouterDiamond:
    """Tests for diamond pattern routing (merge)."""

    def test_diamond_pattern(self) -> None:
        """Diamond pattern routes correctly with merge."""
        router = SimpleRouter()

        # Diamond: A -> B, A -> C, B -> D, C -> D
        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)
        node_c = make_test_node("c", width=10, height=3)
        node_d = make_test_node("d", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=15, y=0),   # Top center
            "b": NodePosition(node=node_b, x=5, y=6),    # Left middle
            "c": NodePosition(node=node_c, x=25, y=6),   # Right middle
            "d": NodePosition(node=node_d, x=15, y=12),  # Bottom center
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
            Edge(source="b", target="d"),
            Edge(source="c", target="d"),
        ]

        paths = router.route(positions, edges)

        assert len(paths) == 4
        # All paths should have valid segments
        for path in paths:
            assert len(path.segments) >= 1
            for seg in path.segments:
                assert len(seg) == 4  # (x1, y1, x2, y2)


class TestSimpleRouterEdgeCases:
    """Tests for edge cases."""

    def test_missing_source_node(self) -> None:
        """Edge with missing source returns no path."""
        router = SimpleRouter()

        node_b = make_test_node("b", width=10, height=3)
        positions = {
            "b": NodePosition(node=node_b, x=5, y=6),
        }
        edges = [Edge(source="a", target="b")]  # 'a' not in positions

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_missing_target_node(self) -> None:
        """Edge with missing target returns no path."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
        }
        edges = [Edge(source="a", target="b")]  # 'b' not in positions

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_empty_edges(self) -> None:
        """Empty edges list returns empty paths."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
        }
        edges: list[Edge] = []

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_segments_have_integer_coords(self) -> None:
        """All segment coordinates are integers."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=15, height=5)  # Odd dimensions
        node_b = make_test_node("b", width=15, height=5)

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=10, y=10),
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        for path in paths:
            for seg in path.segments:
                for coord in seg:
                    assert isinstance(coord, int)
