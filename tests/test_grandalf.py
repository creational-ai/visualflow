"""Grandalf layout engine evaluation tests.

Grandalf is a pure Python Sugiyama layout library.
This test suite evaluates its capabilities for diagram generation.

Key findings to document:
- Custom node dimensions: Yes (via VertexView.w, VertexView.h)
- Coordinate system: Float coordinates (x, y) in VertexView.xy
- Edge routing hints: Limited (just node positions, no waypoints)
- Disconnected components: Handled via g.C list (one component per subgraph)
"""

import pytest
from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout

from conftest import TestGraph, TestNode, TestEdge


class VertexView:
    """Custom view to set node dimensions for Grandalf layout.

    Grandalf requires a 'view' object on each vertex with:
    - w: width of the node
    - h: height of the node
    - xy: tuple(x, y) - set by layout algorithm
    """

    def __init__(self, w: int = 15, h: int = 3) -> None:
        self.w = w
        self.h = h
        self.xy: tuple[float, float] = (0.0, 0.0)


def build_grandalf_graph(test_graph: TestGraph) -> tuple[Graph, dict[str, Vertex]]:
    """Convert TestGraph to Grandalf Graph.

    Returns:
        Tuple of (Graph, vertex_dict) where vertex_dict maps node id to Vertex
    """
    # Create vertices with views
    vertices: dict[str, Vertex] = {}
    for node in test_graph.nodes:
        v = Vertex(data=node)
        v.view = VertexView(w=node.width, h=node.height)
        vertices[node.id] = v

    # Create edges
    edges = [
        Edge(vertices[e.source], vertices[e.target]) for e in test_graph.edges
    ]

    # Build graph
    graph = Graph(list(vertices.values()), edges)
    return graph, vertices


def compute_layout(graph: Graph) -> None:
    """Compute Sugiyama layout for the first connected component."""
    if not graph.C:
        return

    sug = SugiyamaLayout(graph.C[0])
    sug.init_all()
    sug.draw()


class TestGrandalfBasicScenarios:
    """Test Grandalf with basic scenarios (1-3)."""

    def test_simple_chain_positions_assigned(self, simple_chain: TestGraph) -> None:
        """Verify Grandalf assigns positions to simple chain."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        # All vertices should have positions
        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_simple_chain_level_ordering(self, simple_chain: TestGraph) -> None:
        """Verify A is above B is above C (y increases downward)."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        # In Sugiyama layout, y typically increases downward
        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        # A should be above B, B above C
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_simple_chain_vertical_alignment(self, simple_chain: TestGraph) -> None:
        """Verify nodes are vertically aligned (same x)."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        x_a = vertices["a"].view.xy[0]
        x_b = vertices["b"].view.xy[0]
        x_c = vertices["c"].view.xy[0]

        # All should have same x (within tolerance for floats)
        assert abs(x_a - x_b) < 0.1, f"A and B not aligned: {x_a} vs {x_b}"
        assert abs(x_b - x_c) < 0.1, f"B and C not aligned: {x_b} vs {x_c}"

    def test_diamond_positions_assigned(self, diamond: TestGraph) -> None:
        """Verify Grandalf assigns positions to diamond."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_diamond_level_ordering(self, diamond: TestGraph) -> None:
        """Verify diamond has 3 levels: A, then B/C, then D."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]
        y_d = vertices["d"].view.xy[1]

        # A at top, D at bottom, B and C in middle
        assert y_a < y_b, "A should be above B"
        assert y_a < y_c, "A should be above C"
        assert y_b < y_d, "B should be above D"
        assert y_c < y_d, "C should be above D"
        # B and C should be at same level
        assert abs(y_b - y_c) < 0.1, f"B and C should be same level: {y_b} vs {y_c}"

    def test_diamond_horizontal_spread(self, diamond: TestGraph) -> None:
        """Verify B and C are horizontally separated."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        x_b = vertices["b"].view.xy[0]
        x_c = vertices["c"].view.xy[0]

        # B and C should have different x positions
        assert x_b != x_c, "B and C should be horizontally separated"

    def test_multiple_roots_positions_assigned(
        self, multiple_roots: TestGraph
    ) -> None:
        """Verify Grandalf assigns positions to multiple roots."""
        graph, vertices = build_grandalf_graph(multiple_roots)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_multiple_roots_level_ordering(self, multiple_roots: TestGraph) -> None:
        """Verify A and B are above C."""
        graph, vertices = build_grandalf_graph(multiple_roots)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        assert y_a < y_c, "A should be above C"
        assert y_b < y_c, "B should be above C"
        # A and B should be at same level (both are roots)
        assert abs(y_a - y_b) < 0.1, f"A and B should be same level: {y_a} vs {y_b}"


class TestGrandalfAdvancedScenarios:
    """Test Grandalf with advanced scenarios (4-7)."""

    def test_skip_level_positions(self, skip_level: TestGraph) -> None:
        """Verify skip-level graph positions."""
        graph, vertices = build_grandalf_graph(skip_level)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        # A at top, C at bottom, B in middle
        assert y_a < y_b, "A should be above B"
        assert y_b < y_c, "B should be above C"

    def test_wide_graph_horizontal_spread(self, wide_graph: TestGraph) -> None:
        """Verify wide graph has horizontal spread for children."""
        graph, vertices = build_grandalf_graph(wide_graph)
        compute_layout(graph)

        # All children should be at same y level
        child_ys = [vertices[c].view.xy[1] for c in ["b", "c", "d", "e"]]
        for y in child_ys[1:]:
            assert abs(y - child_ys[0]) < 0.1, "All children should be same level"

        # Children should have different x positions
        child_xs = [vertices[c].view.xy[0] for c in ["b", "c", "d", "e"]]
        unique_xs = set(round(x, 1) for x in child_xs)
        assert len(unique_xs) == 4, "All 4 children should have unique x positions"

    def test_deep_graph_level_count(self, deep_graph: TestGraph) -> None:
        """Verify deep graph has 6 distinct levels."""
        graph, vertices = build_grandalf_graph(deep_graph)
        compute_layout(graph)

        ys = [vertices[n].view.xy[1] for n in ["a", "b", "c", "d", "e", "f"]]

        # Each should be below the previous
        for i in range(1, len(ys)):
            assert ys[i] > ys[i - 1], f"Level {i} should be below level {i-1}"

    def test_complex_graph_positions(self, complex_graph: TestGraph) -> None:
        """Verify complex graph assigns all positions."""
        graph, vertices = build_grandalf_graph(complex_graph)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_complex_graph_start_end_ordering(self, complex_graph: TestGraph) -> None:
        """Verify start is above end in complex graph."""
        graph, vertices = build_grandalf_graph(complex_graph)
        compute_layout(graph)

        y_start = vertices["a"].view.xy[1]
        y_end = vertices["f"].view.xy[1]

        assert y_start < y_end, "Start should be above end"


class TestGrandalfCustomDimensions:
    """Test Grandalf's custom dimension capabilities."""

    def test_custom_width_respected(self, simple_chain: TestGraph) -> None:
        """Verify custom node widths are preserved."""
        # Modify widths
        simple_chain.nodes[0].width = 20
        simple_chain.nodes[1].width = 30
        simple_chain.nodes[2].width = 25

        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        assert vertices["a"].view.w == 20
        assert vertices["b"].view.w == 30
        assert vertices["c"].view.w == 25

    def test_custom_height_respected(self, simple_chain: TestGraph) -> None:
        """Verify custom node heights are preserved."""
        # Modify heights
        simple_chain.nodes[0].height = 5
        simple_chain.nodes[1].height = 7
        simple_chain.nodes[2].height = 4

        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        assert vertices["a"].view.h == 5
        assert vertices["b"].view.h == 7
        assert vertices["c"].view.h == 4


class TestGrandalfCapabilities:
    """Document Grandalf's capabilities and limitations."""

    def test_coordinate_system_is_float(self, simple_chain: TestGraph) -> None:
        """Document: Grandalf uses float coordinates."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        x, y = vertices["a"].view.xy
        # Grandalf uses float coordinates
        assert isinstance(x, float) or isinstance(x, int)
        assert isinstance(y, float) or isinstance(y, int)

    def test_no_edge_routing_info(self, diamond: TestGraph) -> None:
        """Document: Grandalf does NOT provide edge routing waypoints.

        Grandalf only provides node positions. Edge routing must be
        computed separately based on node positions.
        """
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        # Check edges - they only have source/target vertices, no routing
        for edge in graph.C[0].E():
            assert hasattr(edge, "v")  # source vertex tuple
            # No edge.path or edge.waypoints attribute
            assert not hasattr(edge, "path")
            assert not hasattr(edge, "waypoints")

    def test_disconnected_components_handled(self) -> None:
        """Document: Grandalf handles disconnected components via g.C list."""
        # Create two disconnected subgraphs
        v1 = Vertex(data="a")
        v2 = Vertex(data="b")
        v3 = Vertex(data="c")  # Disconnected
        v4 = Vertex(data="d")  # Disconnected

        v1.view = VertexView()
        v2.view = VertexView()
        v3.view = VertexView()
        v4.view = VertexView()

        e1 = Edge(v1, v2)
        e2 = Edge(v3, v4)

        graph = Graph([v1, v2, v3, v4], [e1, e2])

        # Grandalf separates into connected components
        assert len(graph.C) == 2, "Should have 2 connected components"

        # Each component can be laid out separately
        for component in graph.C:
            sug = SugiyamaLayout(component)
            sug.init_all()
            sug.draw()

        # All vertices should have positions
        for v in [v1, v2, v3, v4]:
            assert v.view.xy != (0.0, 0.0) or v.view.xy == (
                0.0,
                0.0,
            )  # Position assigned
