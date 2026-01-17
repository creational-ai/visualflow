"""Edge router protocol definition.

Defines the interface that all edge routers must implement.
"""

from typing import Protocol

from visualflow.models import Edge, EdgePath, NodePosition


class EdgeRouter(Protocol):
    """Interface for edge path computation.

    Edge routers compute paths connecting nodes based on their positions.
    All coordinates are in character units (x = columns, y = rows).
    """

    def route(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge],
    ) -> list[EdgePath]:
        """Compute paths for all edges.

        Args:
            positions: Node positions keyed by node ID
            edges: List of edges to route

        Returns:
            List of EdgePath objects with computed segments
        """
        ...
