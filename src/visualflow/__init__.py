"""visualflow - ASCII DAG visualization library.

Generate flawless ASCII diagrams of directed acyclic graphs
with variable-sized boxes.
"""

from visualflow.models import DAG, Node, Edge, LayoutResult, NodePosition, EdgePath
from visualflow.engines import LayoutEngine, GrandalfEngine, GraphvizEngine
from visualflow.render import Canvas
from visualflow.routing import EdgeRouter, SimpleRouter

__version__ = "0.1.0"


def render_dag(
    dag: DAG,
    engine: LayoutEngine | None = None,
    router: EdgeRouter | None = None,
) -> str:
    """Render a DAG to ASCII string.

    Args:
        dag: The directed acyclic graph to render
        engine: Layout engine to use (defaults to GrandalfEngine)
        router: Edge router to use (defaults to SimpleRouter if edges exist)

    Returns:
        Multi-line ASCII string representation
    """
    if engine is None:
        engine = GrandalfEngine()

    # Compute layout
    layout = engine.compute(dag)

    if not layout.positions:
        return ""

    # Create canvas
    canvas = Canvas(width=layout.width, height=layout.height)

    # Place boxes
    for node_id, pos in layout.positions.items():
        canvas.place_box(pos.node.content, pos.x, pos.y)

    # Place box connectors (before edge drawing)
    if dag.edges:
        canvas.place_box_connectors(layout.positions, dag.edges)

    # Route and draw edges
    if dag.edges:
        if router is None:
            router = SimpleRouter()
        paths = router.route(layout.positions, dag.edges)
        for path in paths:
            canvas.draw_edge(path)

    return canvas.render()


__all__ = [
    # Models
    "DAG",
    "Node",
    "Edge",
    "LayoutResult",
    "NodePosition",
    "EdgePath",
    # Engines
    "LayoutEngine",
    "GrandalfEngine",
    "GraphvizEngine",
    # Routing
    "EdgeRouter",
    "SimpleRouter",
    # Rendering
    "Canvas",
    "render_dag",
]
