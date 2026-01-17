"""Data models for ASCII DAG visualization.

All data structures use Pydantic BaseModel with strong typing and built-in validation.
"""

from pydantic import BaseModel, Field, computed_field
from wcwidth import wcswidth


class Node(BaseModel):
    """A node in the DAG.

    The `content` field is the COMPLETE box from task's `diagram` field,
    including borders. Width and height are computed from content.

    Note:
        Width calculation uses wcwidth to correctly handle wide characters
        (emoji, CJK) which may occupy 2 terminal columns.
    """

    id: str
    content: str  # Complete box with borders (from task.diagram)

    @computed_field
    @property
    def width(self) -> int:
        """Box width accounting for wide characters (emoji, CJK).

        Uses wcswidth for accurate terminal column count.
        Falls back to len() if wcswidth returns -1 (non-printable chars).
        """
        lines = self.content.split("\n")
        if not lines:
            return 0
        w = wcswidth(lines[0])
        return w if w >= 0 else len(lines[0])

    @computed_field
    @property
    def height(self) -> int:
        """Box height = number of lines."""
        return len(self.content.split("\n"))


class Edge(BaseModel):
    """A directed edge between nodes."""

    source: str
    target: str


class DAG(BaseModel):
    """Directed Acyclic Graph."""

    nodes: dict[str, Node] = Field(default_factory=dict)
    edges: list[Edge] = Field(default_factory=list)

    def add_node(self, id: str, content: str) -> None:
        """Add a node with the given content."""
        self.nodes[id] = Node(id=id, content=content)

    def add_edge(self, source: str, target: str) -> None:
        """Add a directed edge from source to target."""
        self.edges.append(Edge(source=source, target=target))

    def get_node(self, id: str) -> Node | None:
        """Get a node by ID, or None if not found."""
        return self.nodes.get(id)


class NodePosition(BaseModel):
    """Computed position for a node."""

    node: Node
    x: int  # Left edge (characters)
    y: int  # Top edge (lines)


class LayoutResult(BaseModel):
    """Layout engine output."""

    positions: dict[str, NodePosition]
    width: int  # Canvas width in characters
    height: int  # Canvas height in lines


class EdgePath(BaseModel):
    """Computed path for an edge.

    Each segment is (x1, y1, x2, y2) representing a line from (x1,y1) to (x2,y2).
    """

    source_id: str
    target_id: str
    segments: list[tuple[int, int, int, int]] = Field(default_factory=list)
