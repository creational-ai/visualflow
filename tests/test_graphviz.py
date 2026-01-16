"""Graphviz layout engine evaluation tests.

Graphviz is an industry-standard graph visualization tool (30+ years).
This test suite evaluates its capabilities via `dot -Tplain` output.

Key findings to document:
- Custom node dimensions: Yes (via width/height attributes in DOT)
- Coordinate system: Float coordinates in inches (72 DPI)
- Edge routing hints: Yes (spline control points in plain output)
- Disconnected components: Handled automatically
- Integration: Subprocess call to `dot` CLI
"""

import shutil
import subprocess
from dataclasses import dataclass

import pytest

from conftest import TestGraph


def is_graphviz_installed() -> bool:
    """Check if Graphviz is installed."""
    return shutil.which("dot") is not None


# Skip all tests in this module if Graphviz not installed
pytestmark = pytest.mark.skipif(
    not is_graphviz_installed(),
    reason="Graphviz not installed (run: brew install graphviz)",
)


@dataclass
class PlainNode:
    """Parsed node from Graphviz plain output."""

    name: str
    x: float  # Center x in inches
    y: float  # Center y in inches
    width: float  # Width in inches
    height: float  # Height in inches
    label: str


@dataclass
class PlainEdge:
    """Parsed edge from Graphviz plain output."""

    source: str
    target: str
    points: list[tuple[float, float]]  # Spline control points


@dataclass
class PlainGraph:
    """Parsed Graphviz plain output."""

    scale: float
    width: float
    height: float
    nodes: dict[str, PlainNode]
    edges: list[PlainEdge]


def build_dot_input(test_graph: TestGraph) -> str:
    """Convert TestGraph to DOT format."""
    lines = ["digraph G {"]
    lines.append("  rankdir=TB;")  # Top to bottom

    for node in test_graph.nodes:
        # Convert character dimensions to inches (assuming 10 chars = 1 inch)
        width_inches = node.width / 10.0
        height_inches = node.height / 2.0  # Assuming 2 lines = 1 inch
        lines.append(
            f'  {node.id} [label="{node.label}" '
            f'width={width_inches} height={height_inches} fixedsize=true];'
        )

    for edge in test_graph.edges:
        lines.append(f"  {edge.source} -> {edge.target};")

    lines.append("}")
    return "\n".join(lines)


def run_graphviz(dot_input: str) -> str:
    """Run Graphviz and return plain output."""
    result = subprocess.run(
        ["dot", "-Tplain"],
        input=dot_input,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz failed: {result.stderr}")
    return result.stdout


def parse_plain_output(plain: str) -> PlainGraph:
    """Parse Graphviz plain output format.

    Format:
        graph scale width height
        node name x y width height label style shape color fillcolor
        edge tail head n x1 y1 ... xn yn [label xl yl] style color
        stop
    """
    nodes: dict[str, PlainNode] = {}
    edges: list[PlainEdge] = []
    scale = width = height = 0.0

    for line in plain.strip().split("\n"):
        parts = line.split()
        if not parts:
            continue

        if parts[0] == "graph":
            scale = float(parts[1])
            width = float(parts[2])
            height = float(parts[3])

        elif parts[0] == "node":
            name = parts[1]
            x = float(parts[2])
            y = float(parts[3])
            w = float(parts[4])
            h = float(parts[5])
            label = parts[6] if len(parts) > 6 else name
            nodes[name] = PlainNode(name=name, x=x, y=y, width=w, height=h, label=label)

        elif parts[0] == "edge":
            source = parts[1]
            target = parts[2]
            n_points = int(parts[3])
            points = []
            for i in range(n_points):
                px = float(parts[4 + i * 2])
                py = float(parts[5 + i * 2])
                points.append((px, py))
            edges.append(PlainEdge(source=source, target=target, points=points))

    return PlainGraph(
        scale=scale, width=width, height=height, nodes=nodes, edges=edges
    )


def layout_graph(test_graph: TestGraph) -> PlainGraph:
    """Run full Graphviz pipeline for a test graph."""
    dot_input = build_dot_input(test_graph)
    plain_output = run_graphviz(dot_input)
    return parse_plain_output(plain_output)


class TestGraphvizBasicScenarios:
    """Test Graphviz with basic scenarios (1-3)."""

    def test_simple_chain_positions_assigned(self, simple_chain: TestGraph) -> None:
        """Verify Graphviz assigns positions to simple chain."""
        result = layout_graph(simple_chain)

        assert len(result.nodes) == 3
        for node_id in ["a", "b", "c"]:
            assert node_id in result.nodes
            node = result.nodes[node_id]
            assert isinstance(node.x, float)
            assert isinstance(node.y, float)

    def test_simple_chain_level_ordering(self, simple_chain: TestGraph) -> None:
        """Verify A is above B is above C.

        Note: Graphviz y-axis has origin at bottom, so higher y = higher position.
        With rankdir=TB, A should have highest y.
        """
        result = layout_graph(simple_chain)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        # In Graphviz with TB, higher y = closer to top
        assert y_a > y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b > y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_simple_chain_has_edges(self, simple_chain: TestGraph) -> None:
        """Verify edges are present with routing points."""
        result = layout_graph(simple_chain)

        assert len(result.edges) == 2

        # Find a->b edge
        ab_edge = next((e for e in result.edges if e.source == "a"), None)
        assert ab_edge is not None
        assert ab_edge.target == "b"
        assert len(ab_edge.points) > 0, "Edge should have routing points"

    def test_diamond_positions_assigned(self, diamond: TestGraph) -> None:
        """Verify Graphviz assigns positions to diamond."""
        result = layout_graph(diamond)

        assert len(result.nodes) == 4
        for node_id in ["a", "b", "c", "d"]:
            assert node_id in result.nodes

    def test_diamond_level_ordering(self, diamond: TestGraph) -> None:
        """Verify diamond levels: A top, B/C middle, D bottom."""
        result = layout_graph(diamond)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y
        y_d = result.nodes["d"].y

        # A at top (highest y), D at bottom (lowest y)
        assert y_a > y_b, "A should be above B"
        assert y_a > y_c, "A should be above C"
        assert y_b > y_d, "B should be above D"
        assert y_c > y_d, "C should be above D"

    def test_diamond_has_four_edges(self, diamond: TestGraph) -> None:
        """Verify diamond has all 4 edges with routing."""
        result = layout_graph(diamond)

        assert len(result.edges) == 4
        for edge in result.edges:
            assert len(edge.points) > 0, f"Edge {edge.source}->{edge.target} has no points"

    def test_multiple_roots_positions_assigned(
        self, multiple_roots: TestGraph
    ) -> None:
        """Verify Graphviz assigns positions to multiple roots."""
        result = layout_graph(multiple_roots)

        assert len(result.nodes) == 3
        for node_id in ["a", "b", "c"]:
            assert node_id in result.nodes

    def test_multiple_roots_level_ordering(self, multiple_roots: TestGraph) -> None:
        """Verify A and B are above C."""
        result = layout_graph(multiple_roots)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        assert y_a > y_c, "A should be above C"
        assert y_b > y_c, "B should be above C"


class TestGraphvizAdvancedScenarios:
    """Test Graphviz with advanced scenarios (4-7)."""

    def test_skip_level_positions(self, skip_level: TestGraph) -> None:
        """Verify skip-level graph positions."""
        result = layout_graph(skip_level)

        assert len(result.nodes) == 3
        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        assert y_a > y_b, "A should be above B"
        assert y_b > y_c, "B should be above C"

    def test_skip_level_has_three_edges(self, skip_level: TestGraph) -> None:
        """Verify skip-level has all 3 edges including skip edge."""
        result = layout_graph(skip_level)

        assert len(result.edges) == 3
        # Check for direct a->c skip edge
        skip_edge = next(
            (e for e in result.edges if e.source == "a" and e.target == "c"), None
        )
        assert skip_edge is not None, "Skip edge a->c should exist"

    def test_wide_graph_horizontal_spread(self, wide_graph: TestGraph) -> None:
        """Verify wide graph has horizontal spread for children."""
        result = layout_graph(wide_graph)

        # Children should have different x positions
        child_xs = [result.nodes[c].x for c in ["b", "c", "d", "e"]]
        unique_xs = set(round(x, 2) for x in child_xs)
        assert len(unique_xs) == 4, "All 4 children should have unique x positions"

    def test_deep_graph_level_count(self, deep_graph: TestGraph) -> None:
        """Verify deep graph has 6 distinct levels."""
        result = layout_graph(deep_graph)

        ys = [result.nodes[n].y for n in ["a", "b", "c", "d", "e", "f"]]

        # Each should be below the previous (smaller y)
        for i in range(1, len(ys)):
            assert ys[i] < ys[i - 1], f"Level {i} should be below level {i-1}"

    def test_complex_graph_positions(self, complex_graph: TestGraph) -> None:
        """Verify complex graph assigns all positions."""
        result = layout_graph(complex_graph)

        assert len(result.nodes) == 6
        for node_id in ["a", "b", "c", "d", "e", "f"]:
            assert node_id in result.nodes

    def test_complex_graph_edge_count(self, complex_graph: TestGraph) -> None:
        """Verify complex graph has all 7 edges."""
        result = layout_graph(complex_graph)

        assert len(result.edges) == 7


class TestGraphvizCustomDimensions:
    """Test Graphviz's custom dimension capabilities."""

    def test_custom_dimensions_in_output(self, simple_chain: TestGraph) -> None:
        """Verify custom dimensions are reflected in output."""
        # Modify widths
        simple_chain.nodes[0].width = 20
        simple_chain.nodes[1].width = 30
        simple_chain.nodes[2].width = 25

        result = layout_graph(simple_chain)

        # Dimensions should be close to what we specified (in inches)
        # We specified width/10, so 20 chars -> 2.0 inches
        assert abs(result.nodes["a"].width - 2.0) < 0.1
        assert abs(result.nodes["b"].width - 3.0) < 0.1
        assert abs(result.nodes["c"].width - 2.5) < 0.1


class TestGraphvizCapabilities:
    """Document Graphviz's capabilities and features."""

    def test_coordinate_system_is_inches(self, simple_chain: TestGraph) -> None:
        """Document: Graphviz uses inches for coordinates."""
        result = layout_graph(simple_chain)

        # Coordinates are in inches (small positive numbers)
        for node in result.nodes.values():
            assert 0 <= node.x < 100, f"x={node.x} seems unreasonable for inches"
            assert 0 <= node.y < 100, f"y={node.y} seems unreasonable for inches"

    def test_edge_routing_provides_spline_points(self, diamond: TestGraph) -> None:
        """Document: Graphviz provides spline control points for edges."""
        result = layout_graph(diamond)

        for edge in result.edges:
            # Edges have multiple control points (usually 4+ for bezier)
            assert len(edge.points) >= 2, f"Edge should have at least 2 points"

            # Points are float coordinates
            for x, y in edge.points:
                assert isinstance(x, float)
                assert isinstance(y, float)

    def test_graph_bounding_box_provided(self, simple_chain: TestGraph) -> None:
        """Document: Graphviz provides graph bounding box."""
        result = layout_graph(simple_chain)

        assert result.width > 0, "Graph width should be positive"
        assert result.height > 0, "Graph height should be positive"
        assert result.scale > 0, "Graph scale should be positive"

    def test_disconnected_components_handled(self) -> None:
        """Document: Graphviz handles disconnected components automatically."""
        # Create graph with two disconnected parts
        dot_input = """digraph G {
            a -> b;
            c -> d;
        }"""

        plain_output = run_graphviz(dot_input)
        result = parse_plain_output(plain_output)

        # All 4 nodes should be present
        assert len(result.nodes) == 4
        assert "a" in result.nodes
        assert "c" in result.nodes
