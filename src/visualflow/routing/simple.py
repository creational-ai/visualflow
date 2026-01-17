"""Simple geometric edge router.

Routes edges using basic geometric patterns:
- Straight vertical lines when source and target are aligned
- Z-shaped paths for offset nodes
"""

from visualflow.models import Edge, EdgePath, NodePosition


class SimpleRouter:
    """Geometric edge router using vertical and Z-shaped paths.

    Routing strategy:
    1. Exit from bottom center of source box
    2. Enter at top center of target box
    3. Use vertical line if aligned, Z-shape if offset
    """

    def route(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge],
    ) -> list[EdgePath]:
        """Compute paths for all edges.

        Uses smart routing:
        - Same-layer targets: trunk-and-split pattern (single exit, shared trunk)
        - Different-layer targets: individual Z-shaped routing (multiple exits)

        Args:
            positions: Node positions keyed by node ID
            edges: List of edges to route

        Returns:
            List of EdgePath objects with computed segments
        """
        paths: list[EdgePath] = []

        # Group edges by source
        edges_by_source: dict[str, list[Edge]] = {}
        for edge in edges:
            if edge.source not in edges_by_source:
                edges_by_source[edge.source] = []
            edges_by_source[edge.source].append(edge)

        # Route each source's edges
        for source_id, source_edges in edges_by_source.items():
            source_pos = positions.get(source_id)
            if not source_pos:
                continue

            if len(source_edges) == 1:
                # Single edge - simple routing from center
                path = self._route_edge(positions, source_edges[0])
                if path:
                    paths.append(path)
                continue

            # Multiple edges - check for same-layer targets
            same_layer_targets = self._find_same_layer_targets(positions, source_edges)

            if same_layer_targets and len(same_layer_targets) == len(source_edges):
                # ALL targets on same layer - use trunk-and-split
                center_x = source_pos.x + source_pos.node.width // 2
                trunk_paths = self._route_trunk_split(
                    positions, source_id, same_layer_targets, center_x
                )
                paths.extend(trunk_paths)
            else:
                # Mixed layers or no same-layer - use individual exit points
                exit_points = self._calculate_exit_points(source_pos, len(source_edges))

                # Sort edges by target x position for left-to-right assignment
                sorted_edges = sorted(
                    source_edges,
                    key=lambda e: positions.get(e.target, source_pos).x
                )

                for i, edge in enumerate(sorted_edges):
                    exit_x = exit_points[i] if i < len(exit_points) else exit_points[-1]
                    path = self._route_edge(positions, edge, exit_x=exit_x)
                    if path:
                        paths.append(path)

        return paths

    def _route_edge(
        self,
        positions: dict[str, NodePosition],
        edge: Edge,
        exit_x: int | None = None,
    ) -> EdgePath | None:
        """Route a single edge.

        Args:
            positions: Node positions keyed by node ID
            edge: Edge to route
            exit_x: Optional x coordinate for exit point (defaults to center)

        Returns:
            EdgePath with segments, or None if positions missing
        """
        source_pos = positions.get(edge.source)
        target_pos = positions.get(edge.target)
        if not source_pos or not target_pos:
            return None

        # Compute connection points
        # Source: use provided exit_x or default to center
        if exit_x is not None:
            source_x = exit_x
        else:
            source_x = source_pos.x + source_pos.node.width // 2
        source_y = source_pos.y + source_pos.node.height  # Bottom edge (just below box)

        # Target: top center of box
        target_x = target_pos.x + target_pos.node.width // 2
        target_y = target_pos.y - 1  # Just above box

        segments: list[tuple[int, int, int, int]] = []

        if source_x == target_x:
            # Straight vertical line
            segments.append((source_x, source_y, target_x, target_y))
        else:
            # Z-shape: down, across, down
            # Midpoint Y between source bottom and target top
            mid_y = (source_y + target_y) // 2

            # Ensure mid_y creates valid segments (not zero-length)
            # Need at least 1 row for vertical segment before horizontal turn
            if mid_y <= source_y:
                mid_y = source_y + 1
            # Also ensure room for vertical segment after horizontal turn
            if mid_y >= target_y:
                mid_y = target_y - 1

            # Check if we have room for Z-shape
            if source_y < mid_y < target_y:
                # Full Z-shape: down, across, down
                segments.append((source_x, source_y, source_x, mid_y))
                segments.append((source_x, mid_y, target_x, mid_y))
                segments.append((target_x, mid_y, target_x, target_y))
            elif source_y < target_y:
                # Not enough room for Z, use L-shape: across at source level, then down
                segments.append((source_x, source_y, target_x, source_y))
                segments.append((target_x, source_y, target_x, target_y))
            else:
                # Boxes too close or inverted, just draw horizontal
                segments.append((source_x, source_y, target_x, source_y))

        return EdgePath(
            source_id=edge.source,
            target_id=edge.target,
            segments=segments,
        )

    def _analyze_edges(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge],
    ) -> tuple[dict[str, list[Edge]], dict[str, list[Edge]]]:
        """Analyze edges for routing patterns.

        Groups edges by source and by target to identify:
        - Fan-out: multiple edges from same source
        - Fan-in: multiple edges to same target

        Args:
            positions: Node positions keyed by node ID
            edges: List of edges to analyze

        Returns:
            Tuple of (edges_by_source, edges_by_target)
        """
        edges_by_source: dict[str, list[Edge]] = {}
        edges_by_target: dict[str, list[Edge]] = {}

        for edge in edges:
            # Group by source
            if edge.source not in edges_by_source:
                edges_by_source[edge.source] = []
            edges_by_source[edge.source].append(edge)

            # Group by target
            if edge.target not in edges_by_target:
                edges_by_target[edge.target] = []
            edges_by_target[edge.target].append(edge)

        return edges_by_source, edges_by_target

    def _find_same_layer_targets(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge],
    ) -> list[str]:
        """Find target nodes that are at the same y-level.

        Used for trunk-and-split routing where all targets
        share a vertical trunk before splitting horizontally.

        Args:
            positions: Node positions keyed by node ID
            edges: Edges from a single source

        Returns:
            List of target node IDs at the same layer (most common y)
        """
        if not edges:
            return []

        # Group targets by y position
        targets_by_y: dict[int, list[str]] = {}
        for edge in edges:
            target_pos = positions.get(edge.target)
            if target_pos:
                y = target_pos.y
                if y not in targets_by_y:
                    targets_by_y[y] = []
                targets_by_y[y].append(edge.target)

        # Return targets at most common y (if more than one)
        if not targets_by_y:
            return []
        most_common_y = max(targets_by_y, key=lambda y: len(targets_by_y[y]))
        same_layer = targets_by_y[most_common_y]
        return same_layer if len(same_layer) > 1 else []

    def _find_merge_targets(
        self,
        edges_by_target: dict[str, list[Edge]],
    ) -> list[str]:
        """Find targets that have multiple incoming edges (merge points).

        Args:
            edges_by_target: Edges grouped by target node ID

        Returns:
            List of target node IDs with multiple incoming edges
        """
        return [
            target for target, target_edges in edges_by_target.items()
            if len(target_edges) > 1
        ]

    def _calculate_exit_points(
        self,
        source_pos: NodePosition,
        num_exits: int,
    ) -> list[int]:
        """Calculate x positions for multiple exit points on box bottom.

        Exit points are spaced evenly across the box bottom border,
        avoiding the corner characters.

        Args:
            source_pos: Position of the source node
            num_exits: Number of exit points needed

        Returns:
            List of x coordinates for exit points
        """
        if num_exits <= 0:
            return []

        if num_exits == 1:
            # Single exit at center
            return [source_pos.x + source_pos.node.width // 2]

        # Multiple exits - space evenly, avoid corners
        box_left = source_pos.x + 1  # Skip left corner
        box_right = source_pos.x + source_pos.node.width - 2  # Skip right corner
        usable_width = box_right - box_left

        # Minimum spacing of 2 characters between exits
        min_spacing = 2
        if usable_width < min_spacing * (num_exits - 1):
            # Box too narrow - clamp to what fits
            # Just use center for all (they'll overlap visually but work)
            center = source_pos.x + source_pos.node.width // 2
            return [center] * num_exits

        # Space evenly
        if num_exits == 2:
            # Two exits - left third and right third
            spacing = usable_width // 3
            return [box_left + spacing, box_right - spacing]

        # Three or more - distribute evenly
        spacing = usable_width // (num_exits - 1)
        return [box_left + spacing * i for i in range(num_exits)]

    def _route_trunk_split(
        self,
        positions: dict[str, NodePosition],
        source_id: str,
        target_ids: list[str],
        exit_x: int,
    ) -> list[EdgePath]:
        """Route with trunk-and-split pattern for same-layer targets.

        Pattern:
        1. Vertical trunk from source exit point
        2. Horizontal split line at target layer
        3. Individual vertical drops to each target

        Args:
            positions: Node positions keyed by node ID
            source_id: ID of source node
            target_ids: IDs of target nodes (all at same y)
            exit_x: X coordinate for trunk exit

        Returns:
            List of EdgePath objects for all routed edges
        """
        if not target_ids:
            return []

        source_pos = positions.get(source_id)
        if not source_pos:
            return []

        paths: list[EdgePath] = []

        # Get target positions and sort by x
        target_positions = []
        for target_id in target_ids:
            target_pos = positions.get(target_id)
            if target_pos:
                target_positions.append((target_id, target_pos))

        if not target_positions:
            return []

        target_positions.sort(key=lambda t: t[1].x)

        # Calculate trunk endpoint (4 rows above targets for arrow space)
        target_y = target_positions[0][1].y
        trunk_end_y = target_y - 4  # Leave room for arrow below split

        # Calculate horizontal split range
        leftmost_x = min(tp[1].x + tp[1].node.width // 2 for tp in target_positions)
        rightmost_x = max(tp[1].x + tp[1].node.width // 2 for tp in target_positions)

        # Source exit point
        source_y = source_pos.y + source_pos.node.height

        # Create path for each target
        for target_id, target_pos in target_positions:
            segments: list[tuple[int, int, int, int]] = []
            target_x = target_pos.x + target_pos.node.width // 2
            target_entry_y = target_pos.y - 1

            # Segment 1: Vertical trunk from source
            if source_y < trunk_end_y:
                segments.append((exit_x, source_y, exit_x, trunk_end_y))

            # Segment 2: Horizontal to target column
            if exit_x != target_x:
                segments.append((exit_x, trunk_end_y, target_x, trunk_end_y))

            # Segment 3: Vertical drop to target (if any gap)
            if trunk_end_y < target_entry_y:
                segments.append((target_x, trunk_end_y, target_x, target_entry_y))
            elif trunk_end_y == target_entry_y:
                # Target is right below split - just one combined segment
                pass

            # If no segments were created, at least make a minimal path
            if not segments:
                segments.append((exit_x, source_y, target_x, target_entry_y))

            paths.append(EdgePath(
                source_id=source_id,
                target_id=target_id,
                segments=segments,
            ))

        return paths

    def _route_merge_edges(
        self,
        positions: dict[str, NodePosition],
        source_ids: list[str],
        target_id: str,
    ) -> list[EdgePath]:
        """Route multiple sources merging into single target.

        Pattern:
        1. Each source routes down to a merge row
        2. Horizontal segments join at merge junction
        3. Single vertical line drops to target

        Args:
            positions: Node positions keyed by node ID
            source_ids: IDs of source nodes
            target_id: ID of target node

        Returns:
            List of EdgePath objects for all routed edges
        """
        if not source_ids:
            return []

        target_pos = positions.get(target_id)
        if not target_pos:
            return []

        paths: list[EdgePath] = []

        # Get source positions
        source_positions = []
        for source_id in source_ids:
            source_pos = positions.get(source_id)
            if source_pos:
                source_positions.append((source_id, source_pos))

        if not source_positions:
            return []

        # Calculate merge point
        # Y: midpoint between lowest source and target
        lowest_source_y = max(sp[1].y + sp[1].node.height for sp in source_positions)
        target_entry_y = target_pos.y - 1
        merge_y = (lowest_source_y + target_entry_y) // 2

        # Ensure merge_y is valid
        if merge_y <= lowest_source_y:
            merge_y = lowest_source_y + 1

        # Ensure at least 4 rows before target for arrow visibility
        max_merge_y = target_entry_y - 4
        if merge_y > max_merge_y:
            merge_y = max_merge_y

        if merge_y >= target_entry_y:
            merge_y = target_entry_y - 1

        # X: target center
        target_x = target_pos.x + target_pos.node.width // 2

        # Create path for each source
        for source_id, source_pos in source_positions:
            segments: list[tuple[int, int, int, int]] = []

            source_x = source_pos.x + source_pos.node.width // 2
            source_y = source_pos.y + source_pos.node.height

            # Segment 1: Vertical from source to merge row
            if source_y < merge_y:
                segments.append((source_x, source_y, source_x, merge_y))

            # Segment 2: Horizontal to target column
            if source_x != target_x:
                segments.append((source_x, merge_y, target_x, merge_y))

            # Segment 3: Vertical from merge to target
            if merge_y < target_entry_y:
                segments.append((target_x, merge_y, target_x, target_entry_y))

            # If no valid segments (edge case), create direct path
            if not segments:
                segments.append((source_x, source_y, target_x, target_entry_y))

            paths.append(EdgePath(
                source_id=source_id,
                target_id=target_id,
                segments=segments,
            ))

        return paths

    def _classify_edges(
        self,
        edges_by_source: dict[str, list[Edge]],
        edges_by_target: dict[str, list[Edge]],
    ) -> dict[str, dict[str, list[Edge]]]:
        """Classify edges as 'independent' or 'merge' for each source.

        An edge is a 'merge' edge if its target has multiple incoming edges.
        Otherwise it's an 'independent' edge.

        Args:
            edges_by_source: Edges grouped by source node ID
            edges_by_target: Edges grouped by target node ID

        Returns:
            Dict[source_id, {"independent": [...], "merge": [...]}]
        """
        classification: dict[str, dict[str, list[Edge]]] = {}

        for source_id, source_edges in edges_by_source.items():
            classification[source_id] = {"independent": [], "merge": []}

            for edge in source_edges:
                target_edges = edges_by_target.get(edge.target, [])
                if len(target_edges) > 1:
                    # Multiple sources to this target = merge edge
                    classification[source_id]["merge"].append(edge)
                else:
                    # Single source to this target = independent edge
                    classification[source_id]["independent"].append(edge)

        return classification

    def _allocate_exit_points(
        self,
        source_pos: NodePosition,
        classification: dict[str, list[Edge]],
    ) -> dict[str, int]:
        """Allocate exit points for independent and merge edges.

        Independent edges get left exit points, merge edges get right exit points.

        Args:
            source_pos: Position of source node
            classification: {"independent": [...], "merge": [...]}

        Returns:
            Dict mapping edge target_id to exit x-coordinate
        """
        independent = classification["independent"]
        merge = classification["merge"]
        total_exits = len(independent) + len(merge)

        if total_exits == 0:
            return {}

        # Calculate all exit points
        exit_xs = self._calculate_exit_points(source_pos, total_exits)

        # Assign: independent edges get leftmost, merge edges get rightmost
        allocation: dict[str, int] = {}
        idx = 0

        # Independent edges first (left side)
        for edge in independent:
            allocation[edge.target] = exit_xs[idx]
            idx += 1

        # Merge edges second (right side)
        for edge in merge:
            allocation[edge.target] = exit_xs[idx]
            idx += 1

        return allocation

    def _route_mixed(
        self,
        positions: dict[str, NodePosition],
        source_id: str,
        classification: dict[str, list[Edge]],
        exit_allocation: dict[str, int],
    ) -> list[EdgePath]:
        """Route both independent and merge edges from a single source.

        Args:
            positions: Node positions keyed by node ID
            source_id: ID of source node
            classification: {"independent": [...], "merge": [...]}
            exit_allocation: Target ID -> exit x-coordinate

        Returns:
            List of EdgePath objects for all edges from this source
        """
        paths: list[EdgePath] = []
        source_pos = positions.get(source_id)
        if not source_pos:
            return []

        source_y = source_pos.y + source_pos.node.height

        # Route independent edges (simple vertical/Z-shape)
        for edge in classification["independent"]:
            target_pos = positions.get(edge.target)
            if not target_pos:
                continue

            exit_x = exit_allocation.get(edge.target, source_pos.x + source_pos.node.width // 2)
            target_x = target_pos.x + target_pos.node.width // 2
            target_y = target_pos.y - 1

            segments: list[tuple[int, int, int, int]] = []

            if exit_x == target_x:
                # Straight vertical
                segments.append((exit_x, source_y, target_x, target_y))
            else:
                # Z-shape
                mid_y = (source_y + target_y) // 2
                if mid_y <= source_y:
                    mid_y = source_y + 1
                if mid_y >= target_y:
                    mid_y = target_y - 1

                if source_y < mid_y < target_y:
                    segments.append((exit_x, source_y, exit_x, mid_y))
                    segments.append((exit_x, mid_y, target_x, mid_y))
                    segments.append((target_x, mid_y, target_x, target_y))
                else:
                    segments.append((exit_x, source_y, target_x, source_y))
                    segments.append((target_x, source_y, target_x, target_y))

            paths.append(EdgePath(
                source_id=source_id,
                target_id=edge.target,
                segments=segments,
            ))

        # Route merge edges (converge at target)
        for edge in classification["merge"]:
            target_pos = positions.get(edge.target)
            if not target_pos:
                continue

            exit_x = exit_allocation.get(edge.target, source_pos.x + source_pos.node.width // 2)
            target_x = target_pos.x + target_pos.node.width // 2
            target_y = target_pos.y - 1

            # Merge routing: down to merge row, across to target, down to target
            merge_y = (source_y + target_y) // 2
            if merge_y <= source_y:
                merge_y = source_y + 1
            if merge_y >= target_y:
                merge_y = target_y - 1

            segments: list[tuple[int, int, int, int]] = []

            if source_y < merge_y:
                segments.append((exit_x, source_y, exit_x, merge_y))
            if exit_x != target_x:
                segments.append((exit_x, merge_y, target_x, merge_y))
            if merge_y < target_y:
                segments.append((target_x, merge_y, target_x, target_y))

            if not segments:
                segments.append((exit_x, source_y, target_x, target_y))

            paths.append(EdgePath(
                source_id=source_id,
                target_id=edge.target,
                segments=segments,
            ))

        return paths
