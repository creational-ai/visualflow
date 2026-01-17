# visual-poc2 Implementation Plan

> **Track Progress**: See `docs/visual-poc2-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-16T17:26:37-0800 |
| **Name** | Edge Routing and Canvas Unicode Fix |
| **Type** | PoC |
| **Proves** | SimpleRouter can produce clean ASCII edge paths connecting positioned boxes |
| **Production-Grade Because** | Real geometric routing algorithms; wcwidth-based unicode handling; protocol-based extensibility |

---

## Deliverables

Concrete capabilities this task delivers:

- Unicode-aware `place_box()` that handles emoji and CJK characters correctly
- `EdgeRouter` protocol defining the edge routing interface
- `SimpleRouter` implementation for geometric edge routing (vertical + Z-shapes)
- `Canvas.draw_edge()` method for rendering edge paths with box-drawing characters
- Updated `render_dag()` with optional `router` parameter
- All 7 fixtures render with connected edges

---

## Prerequisites

Complete these BEFORE starting implementation steps.

### 1. Identify Affected Tests

**Why Needed**: Run only affected tests during implementation (not full suite)

**Affected test files**:
- `tests/test_canvas.py` - Canvas placement and rendering (Step 1, 3)
- `tests/test_integration.py` - End-to-end render_dag tests (Step 4)
- `tests/test_routing.py` - New file for router tests (Step 2, 3)

**Baseline verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_canvas.py tests/test_integration.py -v --tb=short
# Expected: All pass (establishes baseline - 34 tests)
```

### 2. Verify wcwidth Dependency

**Why Needed**: Canvas unicode fix requires wcwidth for accurate column counting

**Verification** (inline OK for prerequisites):
```bash
python -c "from wcwidth import wcwidth, wcswidth; print('wcwidth available')"
# Expected: "wcwidth available"
```

### 3. Verify Current Test Count

**Why Needed**: Ensure all 167 existing tests pass before modifications

**Commands**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: 167 tests pass
```

---

## Success Criteria

From `docs/visual-poc2-overview.md`:

- [ ] All 167 existing tests pass after each step
- [ ] Box with emoji renders at correct column positions
- [ ] Box with CJK characters renders correctly
- [ ] SimpleRouter computes paths for simple_chain fixture
- [ ] SimpleRouter computes paths for diamond fixture (merge pattern)
- [ ] All edge segments are valid integers within canvas bounds
- [ ] Edges render correctly with box-drawing characters
- [ ] No character collisions between edges and boxes
- [ ] All 7 fixtures render with connected edges
- [ ] Performance <1s for complex_graph

---

## Architecture

### File Structure
```
src/visualflow/
├── __init__.py                    # Updated: add router parameter to render_dag
├── models.py                      # Existing: EdgePath already defined
├── engines/
│   ├── __init__.py
│   ├── base.py                    # Existing: LayoutEngine protocol
│   ├── grandalf.py
│   └── graphviz.py
├── render/
│   ├── __init__.py                # Updated: export Canvas
│   └── canvas.py                  # Updated: unicode fix + draw_edge
└── routing/                       # NEW directory
    ├── __init__.py                # Export EdgeRouter, SimpleRouter
    ├── base.py                    # EdgeRouter protocol
    └── simple.py                  # SimpleRouter implementation
tests/
├── test_canvas.py                 # Updated: unicode and edge tests
├── test_routing.py                # NEW: router tests
└── test_integration.py            # Updated: edge rendering tests
```

### Design Principles
1. **OOP Design**: Use classes with single responsibility and clear interfaces
2. **Pydantic Models**: EdgePath already defined in models.py with proper typing
3. **Strong Typing**: Type hints on all functions, methods, and class attributes
4. **Protocol Pattern**: EdgeRouter follows same pattern as LayoutEngine

---

## Implementation Steps

**Approach**: Build bottom-up: fix canvas unicode first, then add routing protocol and implementation, then integrate edge drawing, finally update render_dag.

> Each step includes its tests. Write code, write tests, run tests, verify all pass--then move on. Never separate code and tests into different steps.

### Step 0: Verify Baseline

**Goal**: Confirm all existing tests pass before modifications

**Tasks**:
- [ ] Run full test suite
- [ ] Verify 167 tests pass

**Commands**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
```

**Verification** (inline OK for Step 0):
```bash
# Quick check that baseline is solid
python -c "from visualflow import render_dag, DAG; print('Import works')"
# Expected: "Import works"
```

**Output**: 167/167 tests passing

---

### Step 1: Canvas Unicode Fix

**Goal**: Make `place_box()` column-aware using wcwidth for accurate wide character positioning

**Tasks**:
- [ ] Update `place_box()` to track column position instead of character index
- [ ] Use empty string `""` as placeholder for wide character continuation cells
- [ ] Update `render()` to skip placeholder cells
- [ ] Write tests for emoji and CJK character boxes

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/render/canvas.py`):
```python
"""Canvas for ASCII rendering.

The Canvas class manages a 2D character grid where boxes are placed.
Boxes come pre-made with borders - the canvas just positions them.
"""

from pydantic import BaseModel, PrivateAttr, model_validator
from wcwidth import wcwidth


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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_canvas.py`):
```python
class TestCanvasUnicode:
    """Tests for Canvas unicode handling."""

    def test_place_box_with_emoji(self) -> None:
        """Box containing emoji renders at correct column position."""
        canvas = Canvas(width=20, height=5)
        # Emoji takes 2 columns
        box = "+-----+\n| \U0001F680  |\n+-----+"  # rocket emoji
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+-----+"
        assert "\U0001F680" in lines[1]
        assert lines[2] == "+-----+"

    def test_place_box_with_cjk(self) -> None:
        """Box containing CJK characters renders correctly."""
        canvas = Canvas(width=20, height=5)
        # Each CJK char takes 2 columns
        box = "+------+\n| \u4e2d\u6587 |\n+------+"  # Chinese chars
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+------+"
        assert "\u4e2d" in lines[1]
        assert "\u6587" in lines[1]
        assert lines[2] == "+------+"

    def test_multiple_boxes_with_emoji_alignment(self) -> None:
        """Multiple boxes with emoji align correctly."""
        canvas = Canvas(width=40, height=5)
        box1 = "+-----+\n| \U0001F680  |\n+-----+"  # rocket
        box2 = "+-----+\n| OK  |\n+-----+"
        canvas.place_box(box1, x=0, y=0)
        canvas.place_box(box2, x=10, y=0)
        result = canvas.render()
        # Second box should start at column 10
        assert result.count("+-----+") == 4  # 2 boxes x 2 lines each

    def test_get_char_returns_placeholder_as_empty(self) -> None:
        """get_char returns empty string for wide char placeholder."""
        canvas = Canvas(width=10, height=3)
        canvas.place_box("\U0001F680", x=0, y=0)  # rocket at 0,0
        # The emoji is at column 0, placeholder at column 1
        assert canvas.get_char(0, 0) == "\U0001F680"
        assert canvas.get_char(1, 0) == ""  # placeholder

    def test_wide_char_near_boundary(self) -> None:
        """Wide character near canvas boundary is handled."""
        canvas = Canvas(width=5, height=3)
        # Emoji at column 3 would need column 4 for placeholder
        canvas.place_box("...\U0001F680", x=0, y=0)
        result = canvas.render()
        # Should render without error
        assert "..." in result
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_canvas.py -v --tb=short
# Expected: All tests pass (existing + new unicode tests)
```

**Output**: Canvas tests passing including new unicode tests

---

### Step 2: EdgeRouter Protocol and SimpleRouter

**Goal**: Create the routing module with EdgeRouter protocol and SimpleRouter implementation

**Tasks**:
- [ ] Create `src/visualflow/routing/` directory
- [ ] Create `base.py` with EdgeRouter protocol
- [ ] Create `simple.py` with SimpleRouter implementation
- [ ] Create `__init__.py` with exports
- [ ] Write tests for SimpleRouter

**Code** (create `/Users/docchang/Development/visualflow/src/visualflow/routing/__init__.py`):
```python
"""Edge routing components."""

from visualflow.routing.base import EdgeRouter
from visualflow.routing.simple import SimpleRouter

__all__ = ["EdgeRouter", "SimpleRouter"]
```

**Code** (create `/Users/docchang/Development/visualflow/src/visualflow/routing/base.py`):
```python
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
```

**Code** (create `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):
```python
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

        Args:
            positions: Node positions keyed by node ID
            edges: List of edges to route

        Returns:
            List of EdgePath objects with computed segments
        """
        paths: list[EdgePath] = []
        for edge in edges:
            path = self._route_edge(positions, edge)
            if path:
                paths.append(path)
        return paths

    def _route_edge(
        self,
        positions: dict[str, NodePosition],
        edge: Edge,
    ) -> EdgePath | None:
        """Route a single edge.

        Args:
            positions: Node positions keyed by node ID
            edge: Edge to route

        Returns:
            EdgePath with segments, or None if positions missing
        """
        source_pos = positions.get(edge.source)
        target_pos = positions.get(edge.target)
        if not source_pos or not target_pos:
            return None

        # Compute connection points
        # Source: bottom center of box
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

            # Vertical segment from source
            segments.append((source_x, source_y, source_x, mid_y))
            # Horizontal segment
            segments.append((source_x, mid_y, target_x, mid_y))
            # Vertical segment to target
            segments.append((target_x, mid_y, target_x, target_y))

        return EdgePath(
            source_id=edge.source,
            target_id=edge.target,
            segments=segments,
        )
```

**Tests** (create `/Users/docchang/Development/visualflow/tests/test_routing.py`):
```python
"""Tests for edge routing."""

import pytest

from visualflow.models import DAG, Edge, NodePosition, Node
from visualflow.routing import SimpleRouter, EdgeRouter


def make_test_node(id: str, width: int = 10, height: int = 3) -> Node:
    """Create a test node with specified dimensions."""
    content = "+" + "-" * (width - 2) + "+\n"
    content += "|" + " " * (width - 2) + "|\n"
    content += "+" + "-" * (width - 2) + "+"
    return Node(id=id, content=content)


class TestSimpleRouterProtocol:
    """Tests that SimpleRouter implements EdgeRouter protocol."""

    def test_implements_edge_router(self) -> None:
        """SimpleRouter implements EdgeRouter protocol."""
        router = SimpleRouter()
        # Protocol check - should have route method with correct signature
        assert hasattr(router, "route")
        assert callable(router.route)


class TestSimpleRouterVertical:
    """Tests for vertical edge routing."""

    def test_vertical_aligned_nodes(self) -> None:
        """Aligned nodes get straight vertical edge."""
        router = SimpleRouter()

        # Create two vertically aligned nodes
        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),   # Top node
            "b": NodePosition(node=node_b, x=5, y=6),   # Below with gap
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        assert len(paths) == 1
        path = paths[0]
        assert path.source_id == "a"
        assert path.target_id == "b"
        # Single vertical segment
        assert len(path.segments) == 1
        x1, y1, x2, y2 = path.segments[0]
        assert x1 == x2  # Vertical line

    def test_simple_chain_routing(self) -> None:
        """Simple chain A -> B -> C routes vertically."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)
        node_c = make_test_node("c", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
            "b": NodePosition(node=node_b, x=5, y=5),
            "c": NodePosition(node=node_c, x=5, y=10),
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="b", target="c"),
        ]

        paths = router.route(positions, edges)

        assert len(paths) == 2


class TestSimpleRouterZShape:
    """Tests for Z-shaped edge routing."""

    def test_offset_nodes_z_shape(self) -> None:
        """Horizontally offset nodes get Z-shaped edge."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),   # Left
            "b": NodePosition(node=node_b, x=20, y=6), # Right and below
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        assert len(paths) == 1
        path = paths[0]
        # Z-shape has 3 segments: down, across, down
        assert len(path.segments) == 3

        # First segment is vertical (down from source)
        x1, y1, x2, y2 = path.segments[0]
        assert x1 == x2  # Vertical

        # Second segment is horizontal
        x1, y1, x2, y2 = path.segments[1]
        assert y1 == y2  # Horizontal

        # Third segment is vertical (down to target)
        x1, y1, x2, y2 = path.segments[2]
        assert x1 == x2  # Vertical


class TestSimpleRouterDiamond:
    """Tests for diamond pattern routing (merge)."""

    def test_diamond_pattern(self) -> None:
        """Diamond pattern routes correctly with merge."""
        router = SimpleRouter()

        # Diamond: A -> B, A -> C, B -> D, C -> D
        node_a = make_test_node("a", width=10, height=3)
        node_b = make_test_node("b", width=10, height=3)
        node_c = make_test_node("c", width=10, height=3)
        node_d = make_test_node("d", width=10, height=3)

        positions = {
            "a": NodePosition(node=node_a, x=15, y=0),   # Top center
            "b": NodePosition(node=node_b, x=5, y=6),    # Left middle
            "c": NodePosition(node=node_c, x=25, y=6),   # Right middle
            "d": NodePosition(node=node_d, x=15, y=12),  # Bottom center
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
            Edge(source="b", target="d"),
            Edge(source="c", target="d"),
        ]

        paths = router.route(positions, edges)

        assert len(paths) == 4
        # All paths should have valid segments
        for path in paths:
            assert len(path.segments) >= 1
            for seg in path.segments:
                assert len(seg) == 4  # (x1, y1, x2, y2)


class TestSimpleRouterEdgeCases:
    """Tests for edge cases."""

    def test_missing_source_node(self) -> None:
        """Edge with missing source returns no path."""
        router = SimpleRouter()

        node_b = make_test_node("b", width=10, height=3)
        positions = {
            "b": NodePosition(node=node_b, x=5, y=6),
        }
        edges = [Edge(source="a", target="b")]  # 'a' not in positions

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_missing_target_node(self) -> None:
        """Edge with missing target returns no path."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
        }
        edges = [Edge(source="a", target="b")]  # 'b' not in positions

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_empty_edges(self) -> None:
        """Empty edges list returns empty paths."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=10, height=3)
        positions = {
            "a": NodePosition(node=node_a, x=5, y=0),
        }
        edges: list[Edge] = []

        paths = router.route(positions, edges)

        assert len(paths) == 0

    def test_segments_have_integer_coords(self) -> None:
        """All segment coordinates are integers."""
        router = SimpleRouter()

        node_a = make_test_node("a", width=15, height=5)  # Odd dimensions
        node_b = make_test_node("b", width=15, height=5)

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=10, y=10),
        }
        edges = [Edge(source="a", target="b")]

        paths = router.route(positions, edges)

        for path in paths:
            for seg in path.segments:
                for coord in seg:
                    assert isinstance(coord, int)
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All routing tests pass
```

**Output**: Routing tests passing

---

### Step 3: Canvas Edge Drawing

**Goal**: Add `draw_edge()` method to Canvas for rendering edge paths with box-drawing characters

**Tasks**:
- [ ] Add `draw_edge(path: EdgePath)` method to Canvas
- [ ] Implement character selection for vertical, horizontal, and corner segments
- [ ] Handle arrow rendering at target entry point
- [ ] Write tests for edge drawing

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/render/canvas.py` - add method and import):

Add import at top:
```python
from visualflow.models import EdgePath
```

Add method to Canvas class:
```python
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
            _, _, x1, y1 = path.segments[i]
            x2, y2, _, _ = path.segments[i + 1]
            # The end of segment i should connect to start of segment i+1
            if x1 == x2 and y1 == y2:
                self._safe_put_edge_char("+", x1, y1)

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
        # Only overwrite spaces or other edge characters
        if existing == " " or existing in "|-+v":
            self._grid[y][x] = char
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_canvas.py`):
```python
from visualflow.models import EdgePath


class TestCanvasDrawEdge:
    """Tests for Canvas.draw_edge method."""

    def test_draw_vertical_edge(self) -> None:
        """Vertical edge draws with | characters."""
        canvas = Canvas(width=10, height=10)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(5, 2, 5, 7)],  # Vertical from y=2 to y=7
        )
        canvas.draw_edge(path)

        # Check vertical line
        for y in range(2, 7):
            assert canvas.get_char(5, y) == "|"
        # Arrow at end
        assert canvas.get_char(5, 7) == "v"

    def test_draw_horizontal_edge(self) -> None:
        """Horizontal edge draws with - characters."""
        canvas = Canvas(width=15, height=5)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(2, 2, 10, 2)],  # Horizontal from x=2 to x=10
        )
        canvas.draw_edge(path)

        for x in range(2, 11):
            assert canvas.get_char(x, 2) == "-"

    def test_draw_z_shape_edge(self) -> None:
        """Z-shaped edge draws correctly with corner."""
        canvas = Canvas(width=20, height=15)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[
                (5, 3, 5, 6),    # Down
                (5, 6, 12, 6),   # Across
                (12, 6, 12, 10), # Down
            ],
        )
        canvas.draw_edge(path)

        # First vertical segment
        for y in range(3, 6):
            assert canvas.get_char(5, y) == "|"
        # Corner at (5, 6)
        assert canvas.get_char(5, 6) == "+"
        # Horizontal segment
        for x in range(6, 12):
            assert canvas.get_char(x, 6) == "-"
        # Corner at (12, 6)
        assert canvas.get_char(12, 6) == "+"
        # Second vertical segment with arrow
        for y in range(7, 10):
            assert canvas.get_char(12, y) == "|"
        assert canvas.get_char(12, 10) == "v"

    def test_edge_does_not_overwrite_box(self) -> None:
        """Edge drawing does not overwrite box characters."""
        canvas = Canvas(width=20, height=10)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=5, y=3)

        # Try to draw edge through box area
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(7, 0, 7, 8)],  # Vertical through box
        )
        canvas.draw_edge(path)

        # Box content should be preserved
        assert canvas.get_char(5, 3) == "+"
        assert canvas.get_char(7, 4) == "A"  # Box content not overwritten

    def test_empty_path_does_nothing(self) -> None:
        """Empty EdgePath does not modify canvas."""
        canvas = Canvas(width=10, height=10)
        path = EdgePath(source_id="a", target_id="b", segments=[])
        canvas.draw_edge(path)
        # Canvas should be unchanged (all spaces)
        assert canvas.render() == ""

    def test_edge_out_of_bounds_ignored(self) -> None:
        """Edge segments outside canvas bounds are ignored."""
        canvas = Canvas(width=5, height=5)
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(2, 2, 10, 2)],  # Extends beyond canvas
        )
        canvas.draw_edge(path)  # Should not raise
        # Only in-bounds portion drawn
        for x in range(2, 5):
            assert canvas.get_char(x, 2) == "-"
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_canvas.py::TestCanvasDrawEdge -v --tb=short
# Expected: All edge drawing tests pass
```

**Output**: Edge drawing tests passing

---

### Step 4: Integration - Update render_dag with Router

**Goal**: Update `render_dag()` to accept optional router parameter and render edges

**Tasks**:
- [ ] Update `render_dag()` signature to accept optional `router` parameter
- [ ] Import SimpleRouter and EdgeRouter
- [ ] Add edge routing and drawing logic
- [ ] Update `__all__` exports
- [ ] Write integration tests with edges

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/__init__.py`):
```python
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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_integration.py`):
```python
class TestRenderDagWithEdges:
    """Integration tests for render_dag with edge routing."""

    def test_simple_chain_has_edges(self) -> None:
        """Simple chain renders with edge characters."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        # Should have vertical edge characters
        assert "|" in result or "v" in result

    def test_diamond_has_edges(self) -> None:
        """Diamond pattern renders with edge characters."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        # Should have edge characters
        assert "|" in result or "-" in result or "v" in result

    def test_render_with_explicit_router(self) -> None:
        """render_dag works with explicitly provided router."""
        from visualflow.routing import SimpleRouter
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine(), SimpleRouter())
        assert result
        assert "Task A" in result

    def test_render_preserves_box_content(self) -> None:
        """Edges do not corrupt box content."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        # All box content should be intact
        assert "Task A" in result
        assert "Task B" in result
        assert "Task C" in result

    def test_all_fixtures_render_with_edges(self) -> None:
        """All 7 fixtures render successfully with edges."""
        fixtures = [
            create_simple_chain(),
            create_diamond(),
            create_wide_fanout(),
            create_merge_branch(),
            create_skip_level(),
            create_standalone(),
            create_complex_graph(),
        ]
        for dag in fixtures:
            result = render_dag(dag, GrandalfEngine())
            assert result  # Non-empty output


class TestVisualInspectionWithEdges:
    """Visual inspection tests with edges - for manual review."""

    def test_print_simple_chain_with_edges(self) -> None:
        """Print simple chain with edges for visual inspection."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Simple Chain with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_diamond_with_edges(self) -> None:
        """Print diamond with edges for visual inspection."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Diamond with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_wide_fanout_with_edges(self) -> None:
        """Print wide fanout with edges for visual inspection."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Wide Fanout with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_complex_with_edges(self) -> None:
        """Print complex graph with edges for visual inspection."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Complex Graph with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)
```

**Verification**:
```bash
# Run integration tests
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_integration.py -v --tb=short

# Run all affected tests
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_canvas.py tests/test_routing.py tests/test_integration.py -v --tb=short

# Visual inspection (optional)
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_integration.py::TestVisualInspectionWithEdges -v -s
```

**Output**: Integration tests passing, visual output shows connected edges

---

### Step 5: Final Verification and Full Test Suite

**Goal**: Verify all tests pass and visual output meets quality bar

**Tasks**:
- [ ] Run full test suite
- [ ] Visual inspection of all 7 fixtures
- [ ] Performance check on complex_graph

**Verification**:
```bash
# Full test suite
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short

# Performance check
cd /Users/docchang/Development/visualflow && uv run python -c "
import time
from tests.fixtures import create_complex_graph
from visualflow import render_dag, GrandalfEngine

dag = create_complex_graph()
start = time.time()
result = render_dag(dag, GrandalfEngine())
elapsed = time.time() - start
print(f'Complex graph render time: {elapsed:.3f}s')
assert elapsed < 1.0, 'Performance: should be <1s'
print('Performance OK')
"
```

**Output**: All tests passing, performance <1s

---

## Test Summary

### Affected Tests (Run These)

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `tests/test_canvas.py` | ~20 | Canvas placement, rendering, unicode, edges |
| `tests/test_routing.py` | ~12 | SimpleRouter protocol, vertical, Z-shape, diamond |
| `tests/test_integration.py` | ~25 | End-to-end render_dag with edges |

**Affected tests: ~57 tests**

**Full suite**: 167 existing + ~25 new = ~192 tests

---

## Production-Grade Checklist

Before marking PoC complete, verify:

- [ ] **OOP Design**: Classes with single responsibility and clear interfaces
- [ ] **Pydantic Models**: EdgePath already uses Pydantic; Canvas uses Pydantic BaseModel
- [ ] **Strong Typing**: Type hints on all functions, methods, and class attributes
- [ ] **No mock data**: All routing uses real position data from layout engines
- [ ] **Real integrations**: SimpleRouter actually computes geometric paths
- [ ] **Error handling**: Missing nodes return None, out-of-bounds ignored safely
- [ ] **Scalable patterns**: Router protocol allows adding new routers
- [ ] **Tests in same step**: Each step writes AND runs its tests
- [ ] **Config externalized**: No hardcoded values
- [ ] **Clean separation**: Routing in its own module, drawing in Canvas
- [ ] **Self-contained**: Works independently; all existing functionality still works

---

## What "Done" Looks Like

```bash
# 1. All tests pass
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: ~192 tests pass

# 2. Visual inspection shows connected edges
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_integration.py::TestVisualInspectionWithEdges::test_print_simple_chain_with_edges -v -s
# Expected: ASCII output with boxes connected by |, -, +, v characters

# 3. Performance check
cd /Users/docchang/Development/visualflow && uv run python -c "
import time
from tests.fixtures import create_complex_graph
from visualflow import render_dag
dag = create_complex_graph()
start = time.time()
result = render_dag(dag)
print(f'Time: {time.time()-start:.3f}s')
print(result)
"
# Expected: <1s, diagram with connected edges
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/visualflow/render/canvas.py` | Modify | Unicode fix + draw_edge method |
| `src/visualflow/routing/__init__.py` | Create | Export EdgeRouter, SimpleRouter |
| `src/visualflow/routing/base.py` | Create | EdgeRouter protocol |
| `src/visualflow/routing/simple.py` | Create | SimpleRouter implementation |
| `src/visualflow/__init__.py` | Modify | Add router parameter, exports |
| `tests/test_canvas.py` | Modify | Unicode and edge drawing tests |
| `tests/test_routing.py` | Create | Router tests |
| `tests/test_integration.py` | Modify | Edge rendering integration tests |

---

## Dependencies

No new dependencies required. `wcwidth` is already installed and used in `models.py`.

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Wide char handling breaks existing tests | Low | Run full test suite after Step 1 |
| Edge routing produces ugly diagrams | Medium | Visual inspection at each step; iterate on routing rules |
| Edge-box collisions | Medium | `_safe_put_edge_char` avoids overwriting box content |
| Merge point calculation errors | Low | Explicit tests for diamond pattern |
| Performance regression | Low | Performance check in Step 5 |

---

## Next Steps After Completion

1. Verify all ~192 tests pass
2. Verify visual output shows clean connected edges
3. Verify performance <1s for complex_graph
4. Proceed to next task: PoC 3 (Rich Unicode edges with rounded corners)
