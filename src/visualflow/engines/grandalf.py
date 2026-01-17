"""Grandalf-based layout engine.

Uses the Grandalf library (pure Python Sugiyama layout) to compute
node positions, then converts to character coordinates.
"""

from grandalf.graphs import Graph, Vertex, Edge as GEdge
from grandalf.layouts import SugiyamaLayout

from visualflow.models import DAG, LayoutResult, NodePosition


class _VertexView:
    """View object for Grandalf vertex with dimensions.

    Grandalf requires a 'view' object with w, h, and xy attributes.
    Note: This is a plain class (not Pydantic) because Grandalf mutates
    the xy attribute directly during layout computation.
    """

    def __init__(self, w: float, h: float) -> None:
        self.w = w  # Width (Grandalf uses float)
        self.h = h  # Height (Grandalf uses float)
        self.xy: tuple[float, float] = (0.0, 0.0)  # Position set by layout


class GrandalfEngine:
    """Layout engine using Grandalf's Sugiyama algorithm.

    Converts DAG to Grandalf format, runs layout, and converts
    positions back to character coordinates.
    """

    def __init__(
        self,
        horizontal_spacing: int = 4,
        vertical_spacing: int = 6,
    ) -> None:
        """Initialize engine with spacing parameters.

        Args:
            horizontal_spacing: Characters between nodes horizontally
            vertical_spacing: Lines between nodes vertically
        """
        self.horizontal_spacing = horizontal_spacing
        self.vertical_spacing = vertical_spacing

    def compute(self, dag: DAG) -> LayoutResult:
        """Compute layout positions for the DAG.

        Args:
            dag: The directed acyclic graph to lay out

        Returns:
            LayoutResult with positions in character coordinates
        """
        if not dag.nodes:
            return LayoutResult(positions={}, width=0, height=0)

        # Convert to Grandalf format
        vertices, edges = self._build_grandalf_graph(dag)
        graph = Graph(list(vertices.values()), edges)

        # Layout each connected component and offset to prevent overlap
        x_offset = 0.0
        for component in graph.C:
            sug = SugiyamaLayout(component)
            sug.yspace = self.vertical_spacing  # Override Grandalf's default (20)
            sug.init_all()
            sug.draw()

            # Find the bounds of this component
            min_x = float("inf")
            max_x = float("-inf")
            for v in component.sV:
                if hasattr(v, "view"):
                    cx = v.view.xy[0]
                    half_w = v.view.w / 2
                    min_x = min(min_x, cx - half_w)
                    max_x = max(max_x, cx + half_w)

            # Offset all vertices in this component
            if min_x != float("inf"):
                shift = x_offset - min_x
                for v in component.sV:
                    if hasattr(v, "view"):
                        cx, cy = v.view.xy
                        v.view.xy = (cx + shift, cy)
                # Update x_offset for next component
                component_width = max_x - min_x
                x_offset += component_width + self.horizontal_spacing * 4

        # Convert positions to character coordinates
        positions = self._convert_positions(dag, vertices)

        # Calculate canvas size
        width, height = self._calculate_canvas_size(positions)

        return LayoutResult(positions=positions, width=width, height=height)

    def _build_grandalf_graph(
        self, dag: DAG
    ) -> tuple[dict[str, Vertex], list[GEdge]]:
        """Convert DAG to Grandalf graph format.

        Args:
            dag: Source DAG

        Returns:
            Tuple of (vertex_dict, edge_list)
        """
        vertices: dict[str, Vertex] = {}

        for node_id, node in dag.nodes.items():
            v = Vertex(data=node_id)
            v.view = _VertexView(w=float(node.width), h=float(node.height))
            vertices[node_id] = v

        edges = []
        for edge in dag.edges:
            if edge.source in vertices and edge.target in vertices:
                edges.append(GEdge(vertices[edge.source], vertices[edge.target]))

        return vertices, edges

    def _convert_positions(
        self, dag: DAG, vertices: dict[str, Vertex]
    ) -> dict[str, NodePosition]:
        """Convert Grandalf positions to character coordinates.

        Grandalf provides float coordinates with node center at (x, y).
        We need integer coordinates with node top-left at (x, y).

        Args:
            dag: Original DAG with node data
            vertices: Grandalf vertices with computed positions

        Returns:
            Dict mapping node ID to NodePosition
        """
        positions: dict[str, NodePosition] = {}

        # Find min x and y to normalize to positive coordinates
        min_x = float("inf")
        min_y = float("inf")
        for v in vertices.values():
            if hasattr(v, "view") and v.view.xy != (0.0, 0.0):
                cx, cy = v.view.xy
                min_x = min(min_x, cx - v.view.w / 2)
                min_y = min(min_y, cy - v.view.h / 2)

        if min_x == float("inf"):
            min_x = 0
        if min_y == float("inf"):
            min_y = 0

        for node_id, vertex in vertices.items():
            node = dag.nodes[node_id]
            if hasattr(vertex, "view"):
                cx, cy = vertex.view.xy
                # Convert center to top-left and normalize
                x = int(cx - vertex.view.w / 2 - min_x) + self.horizontal_spacing
                y = int(cy - vertex.view.h / 2 - min_y) + self.vertical_spacing
                positions[node_id] = NodePosition(node=node, x=x, y=y)
            else:
                # Fallback for nodes without position
                positions[node_id] = NodePosition(node=node, x=0, y=0)

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

        # Add padding
        return (max_x + self.horizontal_spacing, max_y + self.vertical_spacing)
