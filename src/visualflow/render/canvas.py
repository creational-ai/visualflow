"""Canvas for ASCII rendering.

The Canvas class manages a 2D character grid where boxes are placed.
Boxes come pre-made with borders - the canvas just positions them.
"""

from pydantic import BaseModel, PrivateAttr, model_validator
from wcwidth import wcwidth

from visualflow.models import EdgePath


class Canvas(BaseModel):
    """2D character grid for ASCII rendering.

    Coordinates: x = column (0 = left), y = row (0 = top)

    Note:
        Wide characters (emoji, CJK) occupy 2 terminal columns but are
        stored as a single character followed by an empty string placeholder.
    """

    width: int
    height: int
    _grid: list[list[str]] = PrivateAttr(default_factory=list)

    @model_validator(mode="after")
    def _init_grid(self) -> "Canvas":
        """Initialize the character grid with spaces."""
        self._grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        return self

    def place_box(self, content: str, x: int, y: int) -> None:
        """Place a pre-made box at the given position.

        Args:
            content: The complete box content (with borders)
            x: Left edge column
            y: Top edge row

        Note:
            Uses wcwidth for accurate column positioning. Wide characters
            (emoji, CJK) occupy 2 columns and leave a placeholder in the
            second column.
        """
        lines = content.split("\n")
        for row_offset, line in enumerate(lines):
            canvas_y = y + row_offset
            if canvas_y < 0 or canvas_y >= self.height:
                continue
            # Track column position (not character index)
            col = 0
            for char in line:
                canvas_x = x + col
                if canvas_x < 0 or canvas_x >= self.width:
                    # Character starts out of bounds, but still advance column
                    char_width = wcwidth(char)
                    col += max(1, char_width if char_width >= 0 else 1)
                    continue
                self._grid[canvas_y][canvas_x] = char
                # Handle wide characters (occupy 2 columns)
                char_width = wcwidth(char)
                if char_width == 2 and canvas_x + 1 < self.width:
                    self._grid[canvas_y][canvas_x + 1] = ""  # Placeholder
                col += max(1, char_width if char_width >= 0 else 1)

    def put_char(self, char: str, x: int, y: int) -> None:
        """Place a single character at the given position.

        Args:
            char: Single character to place
            x: Column
            y: Row
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            self._grid[y][x] = char

    def get_char(self, x: int, y: int) -> str:
        """Get the character at the given position.

        Args:
            x: Column
            y: Row

        Returns:
            Character at position, or space if out of bounds
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self._grid[y][x]
        return " "

    def render(self) -> str:
        """Render the canvas to a string.

        Returns:
            Multi-line string representation of the canvas

        Note:
            Skips empty string placeholders (wide char continuations).
        """
        lines = []
        for row in self._grid:
            # Skip empty string placeholders (wide char continuations)
            line = "".join(char for char in row if char != "")
            lines.append(line.rstrip())
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)

    def draw_edge(self, path: EdgePath) -> None:
        """Draw edge path on canvas using box-drawing characters.

        Args:
            path: EdgePath with segments to draw

        Characters used:
            - Vertical: |
            - Horizontal: -
            - Corners: + (intersection)
            - Arrow: v (at target)
        """
        if not path.segments:
            return

        for i, (x1, y1, x2, y2) in enumerate(path.segments):
            is_last_segment = i == len(path.segments) - 1

            if x1 == x2:
                # Vertical segment
                start_y = min(y1, y2)
                end_y = max(y1, y2)
                for y in range(start_y, end_y + 1):
                    if y == end_y and is_last_segment:
                        # Arrow at target
                        self._safe_put_edge_char("v", x1, y)
                    else:
                        self._safe_put_edge_char("|", x1, y)
            elif y1 == y2:
                # Horizontal segment
                start_x = min(x1, x2)
                end_x = max(x1, x2)
                for x in range(start_x, end_x + 1):
                    self._safe_put_edge_char("-", x, y1)

        # Place corners/junctions at segment connection points
        for i in range(len(path.segments) - 1):
            seg1_x1, seg1_y1, seg1_x2, seg1_y2 = path.segments[i]
            seg2_x1, seg2_y1, seg2_x2, seg2_y2 = path.segments[i + 1]
            # The end of segment i should connect to start of segment i+1
            if seg1_x2 == seg2_x1 and seg1_y2 == seg2_y1:
                corner = self._get_corner_char(
                    seg1_x1, seg1_y1, seg1_x2, seg1_y2,
                    seg2_x1, seg2_y1, seg2_x2, seg2_y2
                )
                self._safe_put_edge_char(corner, seg1_x2, seg1_y2)

    def _get_corner_char(
        self,
        x1: int, y1: int, x2: int, y2: int,  # First segment
        x3: int, y3: int, x4: int, y4: int,  # Second segment
    ) -> str:
        """Determine the correct corner character for a junction.

        Args:
            x1, y1, x2, y2: First segment (incoming)
            x3, y3, x4, y4: Second segment (outgoing)

        Returns:
            Corner character: ┌ ┐ └ ┘
        """
        # Determine incoming direction
        if x1 == x2:  # Vertical incoming
            from_above = y2 > y1
            from_below = y2 < y1
        else:  # Horizontal incoming
            from_left = x2 > x1
            from_right = x2 < x1

        # Determine outgoing direction
        if x3 == x4:  # Vertical outgoing
            going_down = y4 > y3
            going_up = y4 < y3
        else:  # Horizontal outgoing
            going_right = x4 > x3
            going_left = x4 < x3

        # Select corner based on directions
        if x1 == x2:  # Came from vertical
            if from_above:  # Coming from above
                if x4 > x3:  # Going right
                    return "└"
                else:  # Going left
                    return "┘"
            else:  # Coming from below
                if x4 > x3:  # Going right
                    return "┌"
                else:  # Going left
                    return "┐"
        else:  # Came from horizontal
            if from_left:  # Coming from left
                if y4 > y3:  # Going down
                    return "┐"
                else:  # Going up
                    return "┘"
            else:  # Coming from right
                if y4 > y3:  # Going down
                    return "┌"
                else:  # Going up
                    return "└"

    def _safe_put_edge_char(self, char: str, x: int, y: int) -> None:
        """Place edge character, avoiding overwriting box content.

        Args:
            char: Edge character to place
            x: Column
            y: Row
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        existing = self._grid[y][x]

        # Combine corners when they overlap (e.g., fan-out/fan-in junctions)
        corner_chars = "┌┐└┘"
        if existing in corner_chars and char in corner_chars:
            # Two corners at same point = T-junction or cross
            # └ + ┘ = ┴ (both coming from above, going left and right)
            # ┌ + ┐ = ┬ (both going down, coming from left and right)
            # └ + ┌ = ├ (vertical line, horizontal going right)
            # ┘ + ┐ = ┤ (vertical line, horizontal going left)
            combo = existing + char
            if combo in ("└┘", "┘└"):
                self._grid[y][x] = "┴"
            elif combo in ("┌┐", "┐┌"):
                self._grid[y][x] = "┬"
            elif combo in ("└┌", "┌└"):
                self._grid[y][x] = "├"
            elif combo in ("┘┐", "┐┘"):
                self._grid[y][x] = "┤"
            else:
                self._grid[y][x] = "┼"  # Full cross for other combos
            return

        # Handle line meeting existing corner (T-junctions)
        # Only when a LINE char (|/-) is placed on an existing CORNER
        # This happens when edges from different paths cross
        # | on existing corner: corner becomes T-junction
        # - on existing corner: corner becomes T-junction
        if char == "|" and existing in corner_chars:
            if existing in "┌└":  # Right-pointing corners + vertical = ├
                self._grid[y][x] = "├"
            else:  # Left-pointing corners (┐┘) + vertical = ┤
                self._grid[y][x] = "┤"
            return
        if char == "-" and existing in corner_chars:
            if existing in "┌┐":  # Down-pointing corners + horizontal = ┬
                self._grid[y][x] = "┬"
            else:  # Up-pointing corners (└┘) + horizontal = ┴
                self._grid[y][x] = "┴"
            return

        # Only overwrite spaces or simple edge characters
        # Don't let basic edge chars (|- ) overwrite corners/junctions
        basic_edge_chars = "|-"
        corner_junction_chars = "┌┐└┘┬┴├┤┼"
        if char in basic_edge_chars:
            # Basic edge chars can only overwrite spaces or other basic chars
            if existing == " " or existing in basic_edge_chars:
                self._grid[y][x] = char
        else:
            # Corner/junction chars and arrows can overwrite anything except boxes
            if existing == " " or existing in "|-+v" + corner_junction_chars:
                self._grid[y][x] = char

    def place_box_connector(self, x: int, y: int) -> None:
        """Place a box connector at the given position.

        This replaces box border characters with a down-pointing
        T-junction to visually connect edges to the box.

        Handles both ASCII (-+) and Unicode (─) box-drawing characters.

        Args:
            x: Column position
            y: Row position (should be on box bottom border)
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        existing = self._grid[y][x]
        # Replace ASCII box border characters
        if existing in "-+":
            self._grid[y][x] = "┬"
        # Replace Unicode horizontal line (box-drawing)
        elif existing == "─":
            self._grid[y][x] = "┬"
        # If already a vertical line, convert to T-junction
        elif existing == "|":
            self._grid[y][x] = "┬"
        # If already an up-pointing T, combine to cross
        elif existing == "┴":
            # T from below + T from above = cross
            self._grid[y][x] = "┼"

    def place_box_connectors(
        self,
        positions: dict[str, "NodePosition"],
        edges: list["Edge"],
    ) -> None:
        """Place box connectors on all boxes that have outgoing edges.

        For each source box with outgoing edges, places T-junction characters
        on the box bottom border at the edge exit points.

        Uses the same routing logic as SimpleRouter:
        - Same-layer targets: single connector at center (trunk-and-split)
        - Different-layer targets: multiple connectors (individual routing)

        Args:
            positions: Node positions keyed by node ID
            edges: List of edges in the DAG
        """
        from visualflow.models import NodePosition, Edge

        # Group edges by source
        edges_by_source: dict[str, list[Edge]] = {}
        for edge in edges:
            if edge.source not in edges_by_source:
                edges_by_source[edge.source] = []
            edges_by_source[edge.source].append(edge)

        # For each source, place connectors based on routing pattern
        for source_id, source_edges in edges_by_source.items():
            source_pos = positions.get(source_id)
            if not source_pos:
                continue

            exit_y = source_pos.y + source_pos.node.height - 1  # Bottom border

            if len(source_edges) == 1:
                # Single edge - connector at center
                center_x = source_pos.x + source_pos.node.width // 2
                self.place_box_connector(center_x, exit_y)
            else:
                # Multiple edges - check for same-layer targets
                same_layer_targets = self._find_same_layer_targets(positions, source_edges)

                if same_layer_targets and len(same_layer_targets) == len(source_edges):
                    # ALL targets on same layer - single connector at center
                    center_x = source_pos.x + source_pos.node.width // 2
                    self.place_box_connector(center_x, exit_y)
                else:
                    # Mixed layers - multiple connectors at calculated exit points
                    exit_points = self._calculate_exit_points(source_pos, len(source_edges))
                    for exit_x in exit_points:
                        self.place_box_connector(exit_x, exit_y)

    def _find_same_layer_targets(
        self,
        positions: dict[str, "NodePosition"],
        edges: list["Edge"],
    ) -> list[str]:
        """Find target nodes that are at the same y-level.

        Mirrors SimpleRouter._find_same_layer_targets() logic.

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

    def _calculate_exit_points(
        self,
        source_pos: "NodePosition",
        num_exits: int,
    ) -> list[int]:
        """Calculate x positions for exit points on box bottom.

        Matches SimpleRouter._calculate_exit_points() logic exactly.

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
            # Box too narrow - use center for all
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
