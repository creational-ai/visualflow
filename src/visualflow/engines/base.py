"""Layout engine protocol definition.

Defines the interface that all layout engines must implement.
"""

from typing import Protocol

from visualflow.models import DAG, LayoutResult


class LayoutEngine(Protocol):
    """Interface for layout computation.

    Layout engines compute node positions for a DAG.
    All coordinates are in character units (x = columns, y = rows).
    """

    def compute(self, dag: DAG) -> LayoutResult:
        """Compute node positions for the given DAG.

        Args:
            dag: The directed acyclic graph to lay out

        Returns:
            LayoutResult with positions in character coordinates
        """
        ...
