"""Graphviz-based layout engine.

Uses the Graphviz CLI (dot command) to compute node positions,
then converts to character coordinates.
"""

import shutil
import subprocess

from pydantic import BaseModel

from visualflow.models import DAG, LayoutResult, NodePosition


class _PlainNode(BaseModel):
    """Parsed node from Graphviz plain output."""

    name: str
    x: float  # Center x in inches
    y: float  # Center y in inches
    width: float  # Width in inches
    height: float  # Height in inches


class GraphvizEngine:
    """Layout engine using Graphviz's dot command.

    Converts DAG to DOT format, runs Graphviz, parses output,
    and converts positions to character coordinates.

    Note:
        Node IDs should be alphanumeric (letters, numbers, underscores).
        Hyphens are automatically converted to underscores for DOT compatibility.
        Other special characters may cause parsing issues.
    """

    # Conversion factor: characters per inch (width)
    CHARS_PER_INCH = 10.0
    # Conversion factor: lines per inch (height)
    LINES_PER_INCH = 2.0

    def __init__(
        self,
        horizontal_spacing: int = 4,
        vertical_spacing: int = 2,
    ) -> None:
        """Initialize engine with spacing parameters.

        Args:
            horizontal_spacing: Characters between nodes horizontally
            vertical_spacing: Lines between nodes vertically
        """
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    @staticmethod
    def is_available() -> bool:
        """Check if Graphviz is installed."""
        return shutil.which("dot") is not None

    def compute(self, dag: DAG) -> LayoutResult:
        """Compute layout positions for the DAG.

        Args:
            dag: The directed acyclic graph to lay out

        Returns:
            LayoutResult with positions in character coordinates

        Raises:
            RuntimeError: If Graphviz is not installed or fails
        """
        if not dag.nodes:
            return LayoutResult(positions={}, width=0, height=0)

        if not self.is_available():
            raise RuntimeError("Graphviz not installed (run: brew install graphviz)")

        # Generate DOT input
        dot_input = self._generate_dot(dag)

        # Run Graphviz
        plain_output = self._run_graphviz(dot_input)

        # Parse output
        plain_nodes = self._parse_plain_output(plain_output)

        # Convert to character coordinates
        positions = self._convert_positions(dag, plain_nodes)

        # Calculate canvas size
        width, height = self._calculate_canvas_size(positions)

        return LayoutResult(positions=positions, width=width, height=height)

    def _generate_dot(self, dag: DAG) -> str:
        """Generate DOT format input for Graphviz.

        Args:
            dag: Source DAG

        Returns:
            DOT format string
        """
        lines = ["digraph G {"]
        lines.append("  rankdir=TB;")  # Top to bottom

        for node_id, node in dag.nodes.items():
            # Convert character dimensions to inches
            width_inches = node.width / self.CHARS_PER_INCH
            height_inches = node.height / self.LINES_PER_INCH
            # Quote node ID and escape special characters
            safe_id = node_id.replace("-", "_")
            lines.append(
                f'  {safe_id} [label="{node_id}" '
                f"width={width_inches:.2f} height={height_inches:.2f} fixedsize=true];"
            )

        for edge in dag.edges:
            safe_source = edge.source.replace("-", "_")
            safe_target = edge.target.replace("-", "_")
            lines.append(f"  {safe_source} -> {safe_target};")

        lines.append("}")
        return "\n".join(lines)

    def _run_graphviz(self, dot_input: str) -> str:
        """Run Graphviz and return plain output.

        Args:
            dot_input: DOT format input

        Returns:
            Plain format output

        Raises:
            RuntimeError: If Graphviz fails
        """
        result = subprocess.run(
            ["dot", "-Tplain"],
            input=dot_input,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Graphviz failed: {result.stderr}")
        return result.stdout

    def _parse_plain_output(self, plain: str) -> dict[str, _PlainNode]:
        """Parse Graphviz plain output format.

        Args:
            plain: Plain format output

        Returns:
            Dict mapping node name to PlainNode
        """
        nodes: dict[str, _PlainNode] = {}

        for line in plain.strip().split("\n"):
            parts = line.split()
            if not parts:
                continue

            if parts[0] == "node":
                name = parts[1]
                x = float(parts[2])
                y = float(parts[3])
                w = float(parts[4])
                h = float(parts[5])
                nodes[name] = _PlainNode(name=name, x=x, y=y, width=w, height=h)

        return nodes

    def _convert_positions(
        self, dag: DAG, plain_nodes: dict[str, _PlainNode]
    ) -> dict[str, NodePosition]:
        """Convert Graphviz positions to character coordinates.

        Graphviz provides positions with origin at bottom-left.
        We need origin at top-left with integer coordinates.

        Args:
            dag: Original DAG with node data
            plain_nodes: Parsed Graphviz nodes

        Returns:
            Dict mapping node ID to NodePosition
        """
        positions: dict[str, NodePosition] = {}

        if not plain_nodes:
            return positions

        # Find max y for coordinate flip
        max_y = max(n.y + n.height / 2 for n in plain_nodes.values())

        for node_id, node in dag.nodes.items():
            safe_id = node_id.replace("-", "_")
            if safe_id not in plain_nodes:
                positions[node_id] = NodePosition(node=node, x=0, y=0)
                continue

            plain = plain_nodes[safe_id]

            # Convert inches to characters
            cx = plain.x * self.CHARS_PER_INCH
            # Flip y axis (Graphviz origin is bottom-left)
            cy = (max_y - plain.y) * self.LINES_PER_INCH

            # Convert center to top-left
            x = int(cx - node.width / 2) + self.horizontal_spacing
            y = int(cy - node.height / 2) + self.vertical_spacing

            # Ensure non-negative
            x = max(0, x)
            y = max(0, y)

            positions[node_id] = NodePosition(node=node, x=x, y=y)

        return positions

    def _calculate_canvas_size(
        self, positions: dict[str, NodePosition]
    ) -> tuple[int, int]:
        """Calculate canvas dimensions to fit all nodes.

        Args:
            positions: Node positions

        Returns:
            Tuple of (width, height) in characters
        """
        if not positions:
            return (0, 0)

        max_x = 0
        max_y = 0
        for pos in positions.values():
            right = pos.x + pos.node.width
            bottom = pos.y + pos.node.height
            max_x = max(max_x, right)
            max_y = max(max_y, bottom)

        return (max_x + self.horizontal_spacing, max_y + self.vertical_spacing)
