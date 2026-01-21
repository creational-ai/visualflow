"""visualflow - ASCII DAG visualization library.

Generate flawless ASCII diagrams of directed acyclic graphs
with variable-sized boxes.
"""

from visualflow.models import (
    DAG, Node, Edge, LayoutResult, NodePosition, EdgePath,
    EdgeTheme, DEFAULT_THEME, LIGHT_THEME, ROUNDED_THEME, HEAVY_THEME,
)
from visualflow.engines import LayoutEngine, GrandalfEngine, GraphvizEngine
from visualflow.render import Canvas
from visualflow.routing import EdgeRouter, SimpleRouter
from visualflow.settings import settings
from visualflow.partition import partition_dag

__version__ = "0.1.0"


def render_dag(
    dag: DAG,
    engine: LayoutEngine | None = None,
    router: EdgeRouter | None = None,
    theme: EdgeTheme | None = None,
) -> str:
    """Render a DAG to ASCII string.

    Automatically organizes output:
    - Connected subgraphs at top (largest first)
    - Standalone nodes grouped at bottom

    Args:
        dag: The directed acyclic graph to render
        engine: Layout engine to use (defaults to GrandalfEngine)
        router: Edge router to use (defaults to SimpleRouter if edges exist)
        theme: Edge theme for line/arrow characters (defaults to ASCII theme)

    Returns:
        Multi-line ASCII string representation
    """
    if engine is None:
        engine = GrandalfEngine()
    if theme is None:
        theme = settings.theme

    # Partition DAG into connected subgraphs and standalones
    subgraphs, standalones = partition_dag(dag)

    rendered_parts: list[str] = []

    # Render connected subgraphs (largest first)
    for subgraph in subgraphs:
        rendered = _render_single_dag(subgraph, engine, router, theme)
        if rendered:
            rendered_parts.append(rendered)

    # Render standalones (if any)
    if standalones.nodes:
        rendered = _render_single_dag(standalones, engine, router, theme)
        if rendered:
            rendered_parts.append(rendered)

    # Join with blank line separator, strip leading newlines from final output
    return "\n".join(rendered_parts).lstrip("\n")


def _render_single_dag(
    dag: DAG,
    engine: LayoutEngine,
    router: EdgeRouter | None,
    theme: EdgeTheme,
) -> str:
    """Render a single DAG (internal helper).

    Args:
        dag: The DAG to render
        engine: Layout engine to use
        router: Edge router to use
        theme: Edge theme for characters

    Returns:
        Multi-line ASCII string representation
    """
    # Compute layout
    layout = engine.compute(dag)

    if not layout.positions:
        return ""

    # Create canvas with theme
    canvas = Canvas(width=layout.width, height=layout.height, theme=theme)

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

        # Fix junction characters based on actual neighbors
        canvas.fix_junctions()

    return canvas.render()


__all__ = [
    # Models
    "DAG",
    "Node",
    "Edge",
    "LayoutResult",
    "NodePosition",
    "EdgePath",
    # Theming
    "EdgeTheme",
    "DEFAULT_THEME",
    "LIGHT_THEME",
    "ROUNDED_THEME",
    "HEAVY_THEME",
    # Settings
    "settings",
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
    # Partitioning
    "partition_dag",
]
