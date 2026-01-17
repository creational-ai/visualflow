# visual-poc1 Implementation Plan

> **Track Progress**: See `docs/visual-poc1-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-16T13:47:18-0800 |
| **Name** | Design & Architecture Implementation |
| **Type** | PoC |
| **Proves** | Core data models, canvas rendering, and layout engines work together to produce positioned ASCII diagrams |
| **Production-Grade Because** | Uses real architecture patterns (Protocol classes, Pydantic models), production dependencies (Grandalf, Graphviz), and is testable with real Mission Control task data |

---

## Deliverables

Concrete capabilities this task delivers:

- Data models: `Node`, `Edge`, `DAG`, `NodePosition`, `LayoutResult`, `EdgePath`
- Canvas class that places pre-made boxes at computed positions
- `GrandalfEngine` layout engine with character coordinate output
- `GraphvizEngine` layout engine with character coordinate output
- 7 test fixtures based on real Mission Control patterns
- Both engines tested and compared on all 7 fixtures

---

## Prerequisites

Complete these BEFORE starting implementation steps.

### 1. Identify Affected Tests

**Why Needed**: Run only affected tests during implementation (not full suite)

**Affected test files**:
- `tests/test_models.py` - New file for data model tests
- `tests/test_canvas.py` - New file for canvas tests
- `tests/test_engines.py` - New file for layout engine tests
- `tests/conftest.py` - Existing, will add new fixtures

**Baseline verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_grandalf.py tests/test_graphviz.py tests/test_fixtures.py -v --tb=short
# Expected: All pass (establishes baseline for existing tests)
```

### 2. Add Pydantic Dependency

**Why Needed**: Pydantic is required for data models with validation

**Steps**:
1. Add Pydantic to pyproject.toml dependencies
2. Run uv sync to install

**Commands**:
```bash
# Add pydantic>=2.0 to pyproject.toml dependencies section, then:
cd "/Users/docchang/Development/visualflow" && uv sync
```

**Verification** (inline OK for prerequisites):
```bash
cd "/Users/docchang/Development/visualflow" && uv run python -c "from pydantic import BaseModel; print('Pydantic OK')"
# Expected: "Pydantic OK"
```

### 3. Verify Layout Dependencies Installed

**Why Needed**: Grandalf and Graphviz are required for layout engines

**Steps**:
1. Verify Grandalf is in pyproject.toml (already present)
2. Verify Graphviz CLI is installed

**Commands**:
```bash
# Verify Grandalf is importable
cd "/Users/docchang/Development/visualflow" && uv run python -c "import grandalf; print('Grandalf OK')"

# Verify Graphviz is installed
which dot && dot -V
```

**Verification** (inline OK for prerequisites):
```bash
cd "/Users/docchang/Development/visualflow" && uv run python -c "from grandalf.graphs import Graph; print('Grandalf import OK')"
# Expected: "Grandalf import OK"
```

### 4. Existing Package Structure

**Why Needed**: Need to understand what already exists

**Current structure** (after Prerequisites completed):
```
visualflow/
├── pyproject.toml          # Has grandalf>=0.8, pydantic>=2.0, pytest (dev)
├── src/
│   └── visualflow/
│       └── __init__.py     # Version only
└── tests/
    ├── __init__.py         # Test package marker
    ├── conftest.py         # TestNode, TestEdge, TestGraph, 7 fixtures
    ├── test_fixtures.py    # Fixture validation tests
    ├── test_grandalf.py    # Grandalf exploration tests
    └── test_graphviz.py    # Graphviz exploration tests
```

**Note**: Existing tests use `TestNode`, `TestEdge`, `TestGraph` dataclasses in conftest.py. Our new models will be Pydantic BaseModel classes in `src/visualflow/models.py` with proper content handling and built-in validation.

**Note**: pyproject.toml has `pythonpath = ["src", "tests"]` so imports from both directories work.

---

## Success Criteria

From `docs/architecture.md`:

- [ ] Data models (Node, Edge, DAG, NodePosition, LayoutResult, EdgePath) implemented
- [ ] Canvas places pre-made boxes at computed positions
- [ ] GrandalfEngine computes positions in character coordinates
- [ ] GraphvizEngine computes positions in character coordinates
- [ ] All 7 test fixtures pass with both engines
- [ ] No overlapping boxes in layout output
- [ ] Correct level ordering (parents above children)

---

## Architecture

### File Structure
```
visualflow/
├── src/
│   └── visualflow/
│       ├── __init__.py           # Public API exports
│       ├── models.py             # Node, Edge, DAG, NodePosition, LayoutResult, EdgePath
│       ├── engines/
│       │   ├── __init__.py       # Engine exports
│       │   ├── base.py           # LayoutEngine protocol
│       │   ├── grandalf.py       # GrandalfEngine
│       │   └── graphviz.py       # GraphvizEngine
│       └── render/
│           ├── __init__.py       # Render exports
│           └── canvas.py         # Canvas class
└── tests/
    ├── conftest.py               # Updated with new fixtures
    ├── fixtures/                 # New directory
    │   ├── __init__.py
    │   ├── simple_chain.py       # Fixture 1
    │   ├── diamond.py            # Fixture 2
    │   ├── wide_fanout.py        # Fixture 3
    │   ├── merge_branch.py       # Fixture 4
    │   ├── skip_level.py         # Fixture 5
    │   ├── standalone.py         # Fixture 6
    │   └── complex_graph.py      # Fixture 7
    ├── test_models.py            # Model tests
    ├── test_canvas.py            # Canvas tests
    └── test_engines.py           # Engine tests
```

### Design Principles
1. **OOP Design**: Use classes with single responsibility and clear interfaces
2. **Pydantic Models**: All data structures use Pydantic `BaseModel` with built-in validation
3. **Protocol Classes**: Layout engines implement `LayoutEngine` protocol
4. **Strong Typing**: Type hints on all functions, methods, and class attributes

---

## Implementation Steps

**Approach**: Build bottom-up from data models, then canvas, then engines. Each step is independently testable.

> Each step includes its tests. Write code, write tests, run tests, verify all pass - then move on. Never separate code and tests into different steps.

### Step 0: Create Package Structure

**Goal**: Create directory structure and empty files

**Tasks**:
- [ ] Create `src/visualflow/engines/` directory
- [ ] Create `src/visualflow/render/` directory
- [ ] Create `tests/fixtures/` directory
- [ ] Create `__init__.py` files

**Code**:
```bash
cd "/Users/docchang/Development/visualflow"

# Create directories
mkdir -p src/visualflow/engines
mkdir -p src/visualflow/render
mkdir -p tests/fixtures

# Create __init__.py files
touch src/visualflow/engines/__init__.py
touch src/visualflow/render/__init__.py
touch tests/fixtures/__init__.py
```

**Verification** (inline OK for Step 0):
```bash
cd "/Users/docchang/Development/visualflow" && ls -la src/visualflow/engines/ src/visualflow/render/ tests/fixtures/
# Expected: Shows directories with __init__.py files
```

**Output**: Package structure created

---

### Step 1: Data Models

**Goal**: Implement core data models in `models.py` using Pydantic

**Tasks**:
- [ ] Create `Node` Pydantic model with content and computed width/height properties
- [ ] Create `Edge` Pydantic model
- [ ] Create `DAG` Pydantic model with add_node/add_edge methods
- [ ] Create `NodePosition` Pydantic model
- [ ] Create `LayoutResult` Pydantic model
- [ ] Create `EdgePath` Pydantic model
- [ ] Write tests for all models

**Code** (create `src/visualflow/models.py`):
```python
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
```

**Tests** (create `tests/test_models.py`):
```python
"""Tests for data models."""

import pytest

from visualflow.models import Node, Edge, DAG, NodePosition, LayoutResult, EdgePath


class TestNode:
    """Tests for Node model."""

    def test_node_creation(self) -> None:
        """Node can be created with id and content."""
        node = Node(id="test", content="Hello")
        assert node.id == "test"
        assert node.content == "Hello"

    def test_node_width_single_line(self) -> None:
        """Width is length of first line."""
        node = Node(id="test", content="Hello World")
        assert node.width == 11

    def test_node_width_multiline(self) -> None:
        """Width is length of first line for multiline content."""
        content = "Line 1 longer\nLine 2\nLine 3"
        node = Node(id="test", content=content)
        assert node.width == 13  # "Line 1 longer"

    def test_node_height_single_line(self) -> None:
        """Height is 1 for single line content."""
        node = Node(id="test", content="Hello")
        assert node.height == 1

    def test_node_height_multiline(self) -> None:
        """Height is number of lines."""
        content = "Line 1\nLine 2\nLine 3"
        node = Node(id="test", content=content)
        assert node.height == 3

    def test_node_empty_content(self) -> None:
        """Empty content has zero dimensions."""
        node = Node(id="test", content="")
        assert node.width == 0
        assert node.height == 1  # Empty string splits to ['']

    def test_node_box_content(self) -> None:
        """Node with box content has correct dimensions."""
        content = "\n".join([
            "+----------+",
            "| Task A   |",
            "+----------+",
        ])
        node = Node(id="task-a", content=content)
        assert node.width == 12
        assert node.height == 3

    def test_node_width_with_emoji(self) -> None:
        """Width correctly counts emoji as 2 columns."""
        # Emoji typically occupy 2 terminal columns
        node = Node(id="test", content="Hello 🎉 World")
        # "Hello " (6) + "🎉" (2) + " World" (6) = 14 columns
        assert node.width == 14

    def test_node_width_with_cjk(self) -> None:
        """Width correctly counts CJK characters as 2 columns."""
        node = Node(id="test", content="Hello 世界")
        # "Hello " (6) + "世" (2) + "界" (2) = 10 columns
        assert node.width == 10


class TestEdge:
    """Tests for Edge model."""

    def test_edge_creation(self) -> None:
        """Edge can be created with source and target."""
        edge = Edge(source="a", target="b")
        assert edge.source == "a"
        assert edge.target == "b"


class TestDAG:
    """Tests for DAG model."""

    def test_dag_creation_empty(self) -> None:
        """Empty DAG has no nodes or edges."""
        dag = DAG()
        assert len(dag.nodes) == 0
        assert len(dag.edges) == 0

    def test_dag_add_node(self) -> None:
        """add_node adds a node to the DAG."""
        dag = DAG()
        dag.add_node("a", "Node A")
        assert len(dag.nodes) == 1
        assert dag.nodes["a"].id == "a"
        assert dag.nodes["a"].content == "Node A"

    def test_dag_add_edge(self) -> None:
        """add_edge adds an edge to the DAG."""
        dag = DAG()
        dag.add_node("a", "Node A")
        dag.add_node("b", "Node B")
        dag.add_edge("a", "b")
        assert len(dag.edges) == 1
        assert dag.edges[0].source == "a"
        assert dag.edges[0].target == "b"

    def test_dag_get_node_exists(self) -> None:
        """get_node returns node when it exists."""
        dag = DAG()
        dag.add_node("a", "Node A")
        node = dag.get_node("a")
        assert node is not None
        assert node.id == "a"

    def test_dag_get_node_not_found(self) -> None:
        """get_node returns None when node doesn't exist."""
        dag = DAG()
        node = dag.get_node("nonexistent")
        assert node is None

    def test_dag_multiple_nodes_and_edges(self) -> None:
        """DAG can hold multiple nodes and edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        assert len(dag.nodes) == 3
        assert len(dag.edges) == 2


class TestNodePosition:
    """Tests for NodePosition model."""

    def test_node_position_creation(self) -> None:
        """NodePosition can be created with node and coordinates."""
        node = Node(id="test", content="Test")
        pos = NodePosition(node=node, x=10, y=5)
        assert pos.node == node
        assert pos.x == 10
        assert pos.y == 5


class TestLayoutResult:
    """Tests for LayoutResult model."""

    def test_layout_result_creation(self) -> None:
        """LayoutResult can be created with positions and dimensions."""
        node = Node(id="test", content="Test")
        pos = NodePosition(node=node, x=0, y=0)
        result = LayoutResult(
            positions={"test": pos},
            width=100,
            height=50,
        )
        assert len(result.positions) == 1
        assert result.width == 100
        assert result.height == 50


class TestEdgePath:
    """Tests for EdgePath model."""

    def test_edge_path_creation_empty(self) -> None:
        """EdgePath can be created with no segments."""
        path = EdgePath(source_id="a", target_id="b")
        assert path.source_id == "a"
        assert path.target_id == "b"
        assert len(path.segments) == 0

    def test_edge_path_with_segments(self) -> None:
        """EdgePath can hold line segments."""
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(10, 5, 10, 10), (10, 10, 20, 10)],
        )
        assert len(path.segments) == 2
        assert path.segments[0] == (10, 5, 10, 10)
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_models.py -v
```

**Output**: 18/18 tests passing

---

### Step 2: LayoutEngine Protocol

**Goal**: Define the LayoutEngine protocol interface

**Tasks**:
- [ ] Create `base.py` with `LayoutEngine` Protocol class
- [ ] Write tests for protocol compliance checking

**Code** (create `src/visualflow/engines/base.py`):
```python
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
```

**Update** `src/visualflow/engines/__init__.py`:
```python
"""Layout engine implementations."""

from visualflow.engines.base import LayoutEngine

__all__ = ["LayoutEngine"]
```

**Tests** (create `tests/test_engines.py`, initial protocol test):
```python
"""Tests for layout engines."""

import pytest

from visualflow.models import DAG, LayoutResult, NodePosition
from visualflow.engines import LayoutEngine


class MockEngine:
    """Mock engine that implements LayoutEngine protocol."""

    def compute(self, dag: DAG) -> LayoutResult:
        """Simple mock layout: stack nodes vertically."""
        positions: dict[str, NodePosition] = {}
        y = 0
        for node_id, node in dag.nodes.items():
            positions[node_id] = NodePosition(node=node, x=0, y=y)
            y += node.height + 2  # 2 lines spacing
        return LayoutResult(
            positions=positions,
            width=max((n.width for n in dag.nodes.values()), default=0),
            height=y,
        )


class TestLayoutEngineProtocol:
    """Tests for LayoutEngine protocol."""

    def test_mock_engine_implements_protocol(self) -> None:
        """MockEngine satisfies LayoutEngine protocol."""
        engine: LayoutEngine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Node A")
        result = engine.compute(dag)
        assert isinstance(result, LayoutResult)

    def test_protocol_requires_compute_method(self) -> None:
        """LayoutEngine requires compute method."""
        # This is a compile-time check via type hints
        # Runtime verification that protocol works
        engine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Test")
        result = engine.compute(dag)
        assert "a" in result.positions
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_engines.py::TestLayoutEngineProtocol -v
```

**Output**: 2/2 tests passing

---

### Step 3: Canvas Class

**Goal**: Create Canvas class that places pre-made boxes at positions

**Tasks**:
- [ ] Create `Canvas` class with width/height and 2D character grid
- [ ] Implement `place_box` method to place a box at (x, y)
- [ ] Implement `render` method to output final string
- [ ] Write tests for canvas operations

**Code** (create `src/visualflow/render/canvas.py`):
```python
"""Canvas for ASCII rendering.

The Canvas class manages a 2D character grid where boxes are placed.
Boxes come pre-made with borders - the canvas just positions them.
"""

from pydantic import BaseModel, Field, PrivateAttr, model_validator


class Canvas(BaseModel):
    """2D character grid for ASCII rendering.

    Coordinates: x = column (0 = left), y = row (0 = top)
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
        """
        lines = content.split("\n")
        for row_offset, line in enumerate(lines):
            canvas_y = y + row_offset
            if canvas_y < 0 or canvas_y >= self.height:
                continue
            for col_offset, char in enumerate(line):
                canvas_x = x + col_offset
                if canvas_x < 0 or canvas_x >= self.width:
                    continue
                self._grid[canvas_y][canvas_x] = char

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
        """
        # Join rows, stripping trailing spaces from each line
        lines = ["".join(row).rstrip() for row in self._grid]
        # Remove trailing empty lines
        while lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines)
```

**Update** `src/visualflow/render/__init__.py`:
```python
"""Rendering components."""

from visualflow.render.canvas import Canvas

__all__ = ["Canvas"]
```

**Tests** (create `tests/test_canvas.py`):
```python
"""Tests for Canvas class."""

import pytest

from visualflow.render import Canvas


class TestCanvasCreation:
    """Tests for Canvas creation."""

    def test_canvas_creation(self) -> None:
        """Canvas can be created with dimensions."""
        canvas = Canvas(width=80, height=24)
        assert canvas.width == 80
        assert canvas.height == 24

    def test_canvas_initialized_with_spaces(self) -> None:
        """Canvas is initialized with space characters."""
        canvas = Canvas(width=5, height=3)
        for y in range(3):
            for x in range(5):
                assert canvas.get_char(x, y) == " "


class TestCanvasPutChar:
    """Tests for put_char method."""

    def test_put_char_valid_position(self) -> None:
        """put_char places character at valid position."""
        canvas = Canvas(width=10, height=10)
        canvas.put_char("X", 5, 3)
        assert canvas.get_char(5, 3) == "X"

    def test_put_char_out_of_bounds_ignored(self) -> None:
        """put_char ignores out of bounds positions."""
        canvas = Canvas(width=10, height=10)
        canvas.put_char("X", -1, 0)  # No error
        canvas.put_char("X", 10, 0)  # No error
        canvas.put_char("X", 0, -1)  # No error
        canvas.put_char("X", 0, 10)  # No error


class TestCanvasPlaceBox:
    """Tests for place_box method."""

    def test_place_box_simple(self) -> None:
        """place_box places a simple box."""
        canvas = Canvas(width=20, height=10)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=2, y=1)

        # Check first line of box
        assert canvas.get_char(2, 1) == "+"
        assert canvas.get_char(3, 1) == "-"
        assert canvas.get_char(6, 1) == "+"

        # Check middle line
        assert canvas.get_char(2, 2) == "|"
        assert canvas.get_char(4, 2) == "A"
        assert canvas.get_char(6, 2) == "|"

    def test_place_box_at_origin(self) -> None:
        """place_box at (0,0) works correctly."""
        canvas = Canvas(width=10, height=5)
        box = "AB\nCD"
        canvas.place_box(box, x=0, y=0)
        assert canvas.get_char(0, 0) == "A"
        assert canvas.get_char(1, 0) == "B"
        assert canvas.get_char(0, 1) == "C"
        assert canvas.get_char(1, 1) == "D"

    def test_place_box_partial_clip_right(self) -> None:
        """place_box clips content that extends past right edge."""
        canvas = Canvas(width=5, height=5)
        box = "ABCDEFGH"  # 8 chars, only 3 will fit starting at x=2
        canvas.place_box(box, x=2, y=0)
        assert canvas.get_char(2, 0) == "A"
        assert canvas.get_char(4, 0) == "C"
        # D, E, F, G, H are clipped

    def test_place_box_partial_clip_bottom(self) -> None:
        """place_box clips content that extends past bottom."""
        canvas = Canvas(width=10, height=2)
        box = "A\nB\nC\nD"  # 4 lines, only 2 will fit
        canvas.place_box(box, x=0, y=0)
        assert canvas.get_char(0, 0) == "A"
        assert canvas.get_char(0, 1) == "B"
        # C, D are clipped

    def test_place_multiple_boxes(self) -> None:
        """Multiple boxes can be placed on canvas."""
        canvas = Canvas(width=30, height=10)
        box1 = "+--+\n|A |\n+--+"
        box2 = "+--+\n|B |\n+--+"
        canvas.place_box(box1, x=0, y=0)
        canvas.place_box(box2, x=10, y=0)

        # First box
        assert canvas.get_char(1, 1) == "A"
        # Second box
        assert canvas.get_char(11, 1) == "B"


class TestCanvasRender:
    """Tests for render method."""

    def test_render_empty_canvas(self) -> None:
        """Empty canvas renders to empty string."""
        canvas = Canvas(width=5, height=3)
        result = canvas.render()
        # All spaces get stripped, so empty
        assert result == ""

    def test_render_single_char(self) -> None:
        """Canvas with single char renders correctly."""
        canvas = Canvas(width=10, height=5)
        canvas.put_char("X", 3, 2)
        result = canvas.render()
        lines = result.split("\n")
        assert len(lines) == 3  # Rows 0, 1, 2
        assert lines[2] == "   X"  # 3 spaces then X

    def test_render_box(self) -> None:
        """Canvas with box renders correctly."""
        canvas = Canvas(width=20, height=5)
        box = "+---+\n| A |\n+---+"
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "+---+"
        assert lines[1] == "| A |"
        assert lines[2] == "+---+"

    def test_render_strips_trailing_spaces(self) -> None:
        """Render strips trailing spaces from lines."""
        canvas = Canvas(width=20, height=5)
        canvas.put_char("X", 0, 0)
        result = canvas.render()
        lines = result.split("\n")
        assert lines[0] == "X"  # No trailing spaces

    def test_render_unicode_box(self) -> None:
        """Canvas handles Unicode box-drawing characters."""
        canvas = Canvas(width=20, height=5)
        box = "\n".join([
            "\u250c\u2500\u2500\u2500\u2510",
            "\u2502 A \u2502",
            "\u2514\u2500\u2500\u2500\u2518",
        ])
        canvas.place_box(box, x=0, y=0)
        result = canvas.render()
        assert "\u250c" in result  # Top-left corner
        assert "\u2518" in result  # Bottom-right corner
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_canvas.py -v
```

**Output**: 14/14 tests passing

---

### Step 4: Test Fixtures with Real Box Content

**Goal**: Create 7 test fixtures with realistic box content (not just labels)

**Tasks**:
- [ ] Create fixture module structure
- [ ] Create fixtures with actual box-drawing content
- [ ] Write tests to validate fixtures

**Code** (create `tests/fixtures/boxes.py` - shared box content):
```python
"""Pre-made box content for test fixtures.

These represent the kind of content that comes from Mission Control
task `diagram` fields - complete boxes with borders.
"""


def make_simple_box(label: str, width: int = 15) -> str:
    """Create a simple box with label.

    Args:
        label: Text to display in box
        width: Total width including borders

    Returns:
        Multi-line string box
    """
    inner_width = width - 2  # Account for borders
    top = "+" + "-" * inner_width + "+"
    middle = "|" + label.center(inner_width) + "|"
    bottom = "+" + "-" * inner_width + "+"
    return "\n".join([top, middle, bottom])


def make_detailed_box(title: str, subtitle: str, status: str, width: int = 25) -> str:
    """Create a detailed box like Mission Control tasks.

    Args:
        title: Main title
        subtitle: Subtitle line
        status: Status indicator
        width: Total width including borders

    Returns:
        Multi-line string box
    """
    inner = width - 2
    lines = [
        "+" + "-" * inner + "+",
        "|" + title.center(inner) + "|",
        "|" + subtitle.center(inner) + "|",
        "|" + status.center(inner) + "|",
        "+" + "-" * inner + "+",
    ]
    return "\n".join(lines)


# Pre-made boxes for fixtures (realistic Mission Control style)
BOX_POC1 = """\
+-------------------------+
|         PoC 1           |
|        SCHEMA           |
|      Complete           |
+-------------------------+"""

BOX_POC2 = """\
+-------------------------+
|         PoC 2           |
|        SERVER           |
|      Complete           |
+-------------------------+"""

BOX_POC3 = """\
+-------------------------+
|         PoC 3           |
|          CRUD           |
|      Complete           |
+-------------------------+"""

BOX_POC4 = """\
+-------------------------+
|         PoC 4           |
|        HISTORY          |
|      Complete           |
+-------------------------+"""

BOX_POC5 = """\
+-------------------------+
|         PoC 5           |
|       WORKFLOW          |
|      Complete           |
+-------------------------+"""

BOX_POC6 = """\
+-------------------------+
|         PoC 6           |
|       ANALYSIS          |
|      Complete           |
+-------------------------+"""

BOX_POC7 = """\
+-------------------------+
|         PoC 7           |
|          E2E            |
|      Complete           |
+-------------------------+"""

BOX_POC8 = """\
+-------------------------+
|         PoC 8           |
|       ABSTRACT          |
|      Complete           |
+-------------------------+"""

BOX_STANDALONE_A = """\
+-------------------------+
|    STRUCTURED TEXT      |
|      Complete           |
+-------------------------+"""

BOX_STANDALONE_B = """\
+-------------------------+
|     DELETE TOOLS        |
|      Complete           |
+-------------------------+"""
```

**Code** (create `tests/fixtures/simple_chain.py`):
```python
"""Fixture 1: Simple Chain (A -> B -> C)."""

from visualflow.models import DAG

from tests.fixtures.boxes import make_simple_box


def create_simple_chain() -> DAG:
    """Create simple chain fixture: A -> B -> C."""
    dag = DAG()

    dag.add_node("a", make_simple_box("Task A", width=15))
    dag.add_node("b", make_simple_box("Task B", width=15))
    dag.add_node("c", make_simple_box("Task C", width=15))

    dag.add_edge("a", "b")
    dag.add_edge("b", "c")

    return dag
```

**Code** (create `tests/fixtures/diamond.py`):
```python
"""Fixture 2: Diamond Pattern (merge and fan-out)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC1, BOX_POC2, BOX_POC3, BOX_POC7


def create_diamond() -> DAG:
    """Create diamond fixture: poc-1, poc-2 -> poc-3 -> poc-7."""
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-2", BOX_POC2)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-7", BOX_POC7)

    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-2", "poc-3")
    dag.add_edge("poc-3", "poc-7")

    return dag
```

**Code** (create `tests/fixtures/wide_fanout.py`):
```python
"""Fixture 3: Wide Fan-out (one parent, many children)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC3, BOX_POC4, BOX_POC5, BOX_POC6, make_simple_box


def create_wide_fanout() -> DAG:
    """Create wide fan-out fixture: poc-3 -> poc-4, poc-5, poc-6, bugs, pydantic."""
    dag = DAG()

    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-4", BOX_POC4)
    dag.add_node("poc-5", BOX_POC5)
    dag.add_node("poc-6", BOX_POC6)
    dag.add_node("bugs", make_simple_box("BUGS", width=15))
    dag.add_node("pydantic", make_simple_box("PYDANTIC", width=15))

    dag.add_edge("poc-3", "poc-4")
    dag.add_edge("poc-3", "poc-5")
    dag.add_edge("poc-3", "poc-6")
    dag.add_edge("poc-3", "bugs")
    dag.add_edge("poc-3", "pydantic")

    return dag
```

**Code** (create `tests/fixtures/merge_branch.py`):
```python
"""Fixture 4: Merge with Independent Branch."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_POC1, BOX_POC2, BOX_POC3, BOX_POC8


def create_merge_branch() -> DAG:
    """Create merge + branch fixture.

    poc-1 -> poc-3 (merged with poc-2)
    poc-1 -> poc-8 (independent branch)
    """
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-2", BOX_POC2)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-8", BOX_POC8)

    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-2", "poc-3")
    dag.add_edge("poc-1", "poc-8")

    return dag
```

**Code** (create `tests/fixtures/skip_level.py`):
```python
"""Fixture 5: Skip-level with Sibling."""

from visualflow.models import DAG

from tests.fixtures.boxes import make_simple_box


def create_skip_level() -> DAG:
    """Create skip-level fixture.

    A -> B -> C1
    A -> C2 (skip-level, directly to bottom row)
    """
    dag = DAG()

    dag.add_node("a", make_simple_box("Root A", width=20))
    dag.add_node("b", make_simple_box("Middle B", width=20))
    dag.add_node("c1", make_simple_box("Child C1", width=20))
    dag.add_node("c2", make_simple_box("Child C2", width=20))

    dag.add_edge("a", "b")
    dag.add_edge("b", "c1")
    dag.add_edge("a", "c2")  # Skip-level edge

    return dag
```

**Code** (create `tests/fixtures/standalone.py`):
```python
"""Fixture 6: Standalone Tasks (no connections)."""

from visualflow.models import DAG

from tests.fixtures.boxes import BOX_STANDALONE_A, BOX_STANDALONE_B


def create_standalone() -> DAG:
    """Create standalone fixture: two disconnected nodes."""
    dag = DAG()

    dag.add_node("standalone-a", BOX_STANDALONE_A)
    dag.add_node("standalone-b", BOX_STANDALONE_B)

    # No edges - these are standalone tasks

    return dag
```

**Code** (create `tests/fixtures/complex_graph.py`):
```python
"""Fixture 7: Complex Graph (real-world mix of patterns)."""

from visualflow.models import DAG

from tests.fixtures.boxes import (
    BOX_POC1, BOX_POC3, BOX_POC8, make_simple_box, make_detailed_box
)


def create_complex_graph() -> DAG:
    """Create complex fixture: mix of patterns from core milestone.

    poc-1 -> poc-3
    poc-1 -> poc-8 -> poc-9 -> poc-11, poc-12, pydantic
                               poc-12 -> poc-13 -> poc-14
    """
    dag = DAG()

    dag.add_node("poc-1", BOX_POC1)
    dag.add_node("poc-3", BOX_POC3)
    dag.add_node("poc-8", BOX_POC8)
    dag.add_node("poc-9", make_detailed_box("PoC 9", "MIGRATION", "Complete"))
    dag.add_node("poc-11", make_simple_box("PoC 11", width=15))
    dag.add_node("poc-12", make_simple_box("PoC 12", width=15))
    dag.add_node("pydantic", make_simple_box("PYDANTIC", width=15))
    dag.add_node("poc-13", make_simple_box("PoC 13", width=15))
    dag.add_node("poc-14", make_simple_box("PoC 14", width=15))

    # Edges
    dag.add_edge("poc-1", "poc-3")
    dag.add_edge("poc-1", "poc-8")
    dag.add_edge("poc-8", "poc-9")
    dag.add_edge("poc-9", "poc-11")
    dag.add_edge("poc-9", "poc-12")
    dag.add_edge("poc-9", "pydantic")
    dag.add_edge("poc-12", "poc-13")
    dag.add_edge("poc-13", "poc-14")

    return dag
```

**Update** `tests/fixtures/__init__.py`:
```python
"""Test fixtures with realistic box content."""

from tests.fixtures.simple_chain import create_simple_chain
from tests.fixtures.diamond import create_diamond
from tests.fixtures.wide_fanout import create_wide_fanout
from tests.fixtures.merge_branch import create_merge_branch
from tests.fixtures.skip_level import create_skip_level
from tests.fixtures.standalone import create_standalone
from tests.fixtures.complex_graph import create_complex_graph

__all__ = [
    "create_simple_chain",
    "create_diamond",
    "create_wide_fanout",
    "create_merge_branch",
    "create_skip_level",
    "create_standalone",
    "create_complex_graph",
]
```

**Tests** (create `tests/test_new_fixtures.py`):
```python
"""Tests for new fixtures with real box content."""

import pytest

from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class TestSimpleChainFixture:
    """Tests for simple_chain fixture."""

    def test_has_three_nodes(self) -> None:
        """Simple chain has 3 nodes."""
        dag = create_simple_chain()
        assert len(dag.nodes) == 3

    def test_has_two_edges(self) -> None:
        """Simple chain has 2 edges."""
        dag = create_simple_chain()
        assert len(dag.edges) == 2

    def test_nodes_have_content(self) -> None:
        """All nodes have box content."""
        dag = create_simple_chain()
        for node in dag.nodes.values():
            assert node.content
            assert node.width > 0
            assert node.height > 0


class TestDiamondFixture:
    """Tests for diamond fixture."""

    def test_has_four_nodes(self) -> None:
        """Diamond has 4 nodes."""
        dag = create_diamond()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Diamond has 3 edges."""
        dag = create_diamond()
        assert len(dag.edges) == 3


class TestWideFanoutFixture:
    """Tests for wide_fanout fixture."""

    def test_has_six_nodes(self) -> None:
        """Wide fanout has 6 nodes."""
        dag = create_wide_fanout()
        assert len(dag.nodes) == 6

    def test_has_five_edges(self) -> None:
        """Wide fanout has 5 edges from single parent."""
        dag = create_wide_fanout()
        assert len(dag.edges) == 5
        # All edges should come from poc-3
        for edge in dag.edges:
            assert edge.source == "poc-3"


class TestMergeBranchFixture:
    """Tests for merge_branch fixture."""

    def test_has_four_nodes(self) -> None:
        """Merge branch has 4 nodes."""
        dag = create_merge_branch()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Merge branch has 3 edges."""
        dag = create_merge_branch()
        assert len(dag.edges) == 3


class TestSkipLevelFixture:
    """Tests for skip_level fixture."""

    def test_has_four_nodes(self) -> None:
        """Skip level has 4 nodes."""
        dag = create_skip_level()
        assert len(dag.nodes) == 4

    def test_has_three_edges(self) -> None:
        """Skip level has 3 edges including skip edge."""
        dag = create_skip_level()
        assert len(dag.edges) == 3

    def test_has_skip_edge(self) -> None:
        """Skip level has direct a->c2 edge."""
        dag = create_skip_level()
        skip_edges = [e for e in dag.edges if e.source == "a" and e.target == "c2"]
        assert len(skip_edges) == 1


class TestStandaloneFixture:
    """Tests for standalone fixture."""

    def test_has_two_nodes(self) -> None:
        """Standalone has 2 nodes."""
        dag = create_standalone()
        assert len(dag.nodes) == 2

    def test_has_no_edges(self) -> None:
        """Standalone has no edges."""
        dag = create_standalone()
        assert len(dag.edges) == 0


class TestComplexGraphFixture:
    """Tests for complex_graph fixture."""

    def test_has_nine_nodes(self) -> None:
        """Complex graph has 9 nodes."""
        dag = create_complex_graph()
        assert len(dag.nodes) == 9

    def test_has_eight_edges(self) -> None:
        """Complex graph has 8 edges."""
        dag = create_complex_graph()
        assert len(dag.edges) == 8

    def test_nodes_have_varying_sizes(self) -> None:
        """Nodes have different box sizes."""
        dag = create_complex_graph()
        widths = set(n.width for n in dag.nodes.values())
        # Should have at least 2 different widths
        assert len(widths) >= 2
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_new_fixtures.py -v
```

**Output**: 14/14 tests passing

---

### Step 5: GrandalfEngine Implementation

**Goal**: Implement GrandalfEngine that computes positions using Grandalf library

**Tasks**:
- [ ] Create `GrandalfEngine` class implementing `LayoutEngine` protocol
- [ ] Convert DAG to Grandalf graph format
- [ ] Convert float positions to character coordinates
- [ ] Handle disconnected components
- [ ] Write comprehensive tests

**Code** (create `src/visualflow/engines/grandalf.py`):
```python
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
        vertical_spacing: int = 2,
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

        # Layout each connected component
        for component in graph.C:
            sug = SugiyamaLayout(component)
            sug.init_all()
            sug.draw()

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
```

**Update** `src/visualflow/engines/__init__.py`:
```python
"""Layout engine implementations."""

from visualflow.engines.base import LayoutEngine
from visualflow.engines.grandalf import GrandalfEngine

__all__ = ["LayoutEngine", "GrandalfEngine"]
```

**Tests** (add to `tests/test_engines.py`):
```python
"""Tests for layout engines."""

import pytest

from visualflow.models import DAG, LayoutResult, NodePosition
from visualflow.engines import LayoutEngine, GrandalfEngine
from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class MockEngine:
    """Mock engine that implements LayoutEngine protocol."""

    def compute(self, dag: DAG) -> LayoutResult:
        """Simple mock layout: stack nodes vertically."""
        positions: dict[str, NodePosition] = {}
        y = 0
        for node_id, node in dag.nodes.items():
            positions[node_id] = NodePosition(node=node, x=0, y=y)
            y += node.height + 2
        return LayoutResult(
            positions=positions,
            width=max((n.width for n in dag.nodes.values()), default=0),
            height=y,
        )


class TestLayoutEngineProtocol:
    """Tests for LayoutEngine protocol."""

    def test_mock_engine_implements_protocol(self) -> None:
        """MockEngine satisfies LayoutEngine protocol."""
        engine: LayoutEngine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Node A")
        result = engine.compute(dag)
        assert isinstance(result, LayoutResult)

    def test_protocol_requires_compute_method(self) -> None:
        """LayoutEngine requires compute method."""
        engine = MockEngine()
        dag = DAG()
        dag.add_node("a", "Test")
        result = engine.compute(dag)
        assert "a" in result.positions


class TestGrandalfEngineBasic:
    """Basic tests for GrandalfEngine."""

    def test_engine_creation(self) -> None:
        """GrandalfEngine can be created."""
        engine = GrandalfEngine()
        assert engine.horizontal_spacing == 4
        assert engine.vertical_spacing == 2

    def test_engine_custom_spacing(self) -> None:
        """GrandalfEngine accepts custom spacing."""
        engine = GrandalfEngine(horizontal_spacing=8, vertical_spacing=4)
        assert engine.horizontal_spacing == 8
        assert engine.vertical_spacing == 4

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty result."""
        engine = GrandalfEngine()
        dag = DAG()
        result = engine.compute(dag)
        assert len(result.positions) == 0
        assert result.width == 0
        assert result.height == 0

    def test_single_node(self) -> None:
        """Single node is positioned."""
        engine = GrandalfEngine()
        dag = DAG()
        dag.add_node("a", "Test Node")
        result = engine.compute(dag)
        assert "a" in result.positions
        assert result.positions["a"].x >= 0
        assert result.positions["a"].y >= 0


class TestGrandalfEngineSimpleChain:
    """Tests for GrandalfEngine with simple chain fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert len(result.positions) == 3
        assert "a" in result.positions
        assert "b" in result.positions
        assert "c" in result.positions

    def test_level_ordering(self) -> None:
        """Parent nodes are above child nodes (smaller y)."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        y_a = result.positions["a"].y
        y_b = result.positions["b"].y
        y_c = result.positions["c"].y
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_canvas_size_positive(self) -> None:
        """Canvas has positive dimensions."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert result.width > 0
        assert result.height > 0

    def test_positions_are_integers(self) -> None:
        """Positions are integer coordinates."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        for pos in result.positions.values():
            assert isinstance(pos.x, int)
            assert isinstance(pos.y, int)


class TestGrandalfEngineDiamond:
    """Tests for GrandalfEngine with diamond fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        assert len(result.positions) == 4

    def test_roots_above_children(self) -> None:
        """Root nodes are above their children."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc2 = result.positions["poc-2"].y
        y_poc3 = result.positions["poc-3"].y
        assert y_poc1 < y_poc3, "poc-1 should be above poc-3"
        assert y_poc2 < y_poc3, "poc-2 should be above poc-3"

    def test_siblings_same_level(self) -> None:
        """Sibling nodes at same level have similar y."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc2 = result.positions["poc-2"].y
        # Allow some tolerance
        assert abs(y_poc1 - y_poc2) < 10, f"poc-1 and poc-2 should be same level"


class TestGrandalfEngineWideFanout:
    """Tests for GrandalfEngine with wide fanout fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All 6 nodes get positions."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        assert len(result.positions) == 6

    def test_children_below_parent(self) -> None:
        """All children are below parent."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        y_parent = result.positions["poc-3"].y
        for child_id in ["poc-4", "poc-5", "poc-6", "bugs", "pydantic"]:
            y_child = result.positions[child_id].y
            assert y_child > y_parent, f"{child_id} should be below poc-3"

    def test_children_spread_horizontally(self) -> None:
        """Children have different x positions."""
        engine = GrandalfEngine()
        dag = create_wide_fanout()
        result = engine.compute(dag)
        x_positions = [
            result.positions[c].x
            for c in ["poc-4", "poc-5", "poc-6", "bugs", "pydantic"]
        ]
        unique_xs = set(x_positions)
        assert len(unique_xs) >= 2, "Children should be spread horizontally"


class TestGrandalfEngineStandalone:
    """Tests for GrandalfEngine with standalone fixture."""

    def test_disconnected_nodes_positioned(self) -> None:
        """Disconnected nodes still get positions."""
        engine = GrandalfEngine()
        dag = create_standalone()
        result = engine.compute(dag)
        assert len(result.positions) == 2
        assert "standalone-a" in result.positions
        assert "standalone-b" in result.positions


class TestGrandalfEngineNoOverlap:
    """Tests that verify no boxes overlap."""

    def _boxes_overlap(
        self, pos1: NodePosition, pos2: NodePosition
    ) -> bool:
        """Check if two positioned boxes overlap."""
        # Box 1 bounds
        x1_min, x1_max = pos1.x, pos1.x + pos1.node.width
        y1_min, y1_max = pos1.y, pos1.y + pos1.node.height

        # Box 2 bounds
        x2_min, x2_max = pos2.x, pos2.x + pos2.node.width
        y2_min, y2_max = pos2.y, pos2.y + pos2.node.height

        # Check for overlap
        x_overlap = x1_min < x2_max and x1_max > x2_min
        y_overlap = y1_min < y2_max and y1_max > y2_min

        return x_overlap and y_overlap

    def test_simple_chain_no_overlap(self) -> None:
        """Simple chain has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_diamond_no_overlap(self) -> None:
        """Diamond has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_complex_graph_no_overlap(self) -> None:
        """Complex graph has no overlapping boxes."""
        engine = GrandalfEngine()
        dag = create_complex_graph()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2), (
                    f"{pos1.node.id} overlaps {pos2.node.id}"
                )
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_engines.py -v
```

**Output**: ~20 tests passing

---

### Step 6: GraphvizEngine Implementation

**Goal**: Implement GraphvizEngine using Graphviz CLI for layout

**Tasks**:
- [ ] Create `GraphvizEngine` class implementing `LayoutEngine` protocol
- [ ] Generate DOT format input
- [ ] Parse plain output format
- [ ] Convert inch coordinates to character coordinates
- [ ] Write comprehensive tests

**Code** (create `src/visualflow/engines/graphviz.py`):
```python
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
```

**Update** `src/visualflow/engines/__init__.py`:
```python
"""Layout engine implementations."""

from visualflow.engines.base import LayoutEngine
from visualflow.engines.grandalf import GrandalfEngine
from visualflow.engines.graphviz import GraphvizEngine

__all__ = ["LayoutEngine", "GrandalfEngine", "GraphvizEngine"]
```

**Tests** (add to `tests/test_engines.py`):
```python
# Add these classes to existing test_engines.py

class TestGraphvizEngineAvailability:
    """Tests for Graphviz availability check."""

    def test_is_available_returns_bool(self) -> None:
        """is_available returns boolean."""
        result = GraphvizEngine.is_available()
        assert isinstance(result, bool)


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineBasic:
    """Basic tests for GraphvizEngine."""

    def test_engine_creation(self) -> None:
        """GraphvizEngine can be created."""
        engine = GraphvizEngine()
        assert engine.horizontal_spacing == 4
        assert engine.vertical_spacing == 2

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty result."""
        engine = GraphvizEngine()
        dag = DAG()
        result = engine.compute(dag)
        assert len(result.positions) == 0

    def test_single_node(self) -> None:
        """Single node is positioned."""
        engine = GraphvizEngine()
        dag = DAG()
        dag.add_node("a", "Test Node")
        result = engine.compute(dag)
        assert "a" in result.positions


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineSimpleChain:
    """Tests for GraphvizEngine with simple chain fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        assert len(result.positions) == 3

    def test_level_ordering(self) -> None:
        """Parent nodes are above child nodes (smaller y)."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        y_a = result.positions["a"].y
        y_b = result.positions["b"].y
        y_c = result.positions["c"].y
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineDiamond:
    """Tests for GraphvizEngine with diamond fixture."""

    def test_all_nodes_positioned(self) -> None:
        """All nodes get positions."""
        engine = GraphvizEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        assert len(result.positions) == 4

    def test_roots_above_children(self) -> None:
        """Root nodes are above their children."""
        engine = GraphvizEngine()
        dag = create_diamond()
        result = engine.compute(dag)
        y_poc1 = result.positions["poc-1"].y
        y_poc3 = result.positions["poc-3"].y
        assert y_poc1 < y_poc3, "poc-1 should be above poc-3"


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestGraphvizEngineNoOverlap:
    """Tests that verify no boxes overlap with Graphviz."""

    def _boxes_overlap(
        self, pos1: NodePosition, pos2: NodePosition
    ) -> bool:
        """Check if two positioned boxes overlap."""
        x1_min, x1_max = pos1.x, pos1.x + pos1.node.width
        y1_min, y1_max = pos1.y, pos1.y + pos1.node.height
        x2_min, x2_max = pos2.x, pos2.x + pos2.node.width
        y2_min, y2_max = pos2.y, pos2.y + pos2.node.height
        x_overlap = x1_min < x2_max and x1_max > x2_min
        y_overlap = y1_min < y2_max and y1_max > y2_min
        return x_overlap and y_overlap

    def test_simple_chain_no_overlap(self) -> None:
        """Simple chain has no overlapping boxes."""
        engine = GraphvizEngine()
        dag = create_simple_chain()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)

    def test_complex_graph_no_overlap(self) -> None:
        """Complex graph has no overlapping boxes."""
        engine = GraphvizEngine()
        dag = create_complex_graph()
        result = engine.compute(dag)
        positions = list(result.positions.values())
        for i, pos1 in enumerate(positions):
            for pos2 in positions[i + 1 :]:
                assert not self._boxes_overlap(pos1, pos2)
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_engines.py -v
```

**Output**: ~30 tests passing

---

### Step 7: Integration - Canvas with Layout Engine

**Goal**: Combine layout engine output with canvas rendering

**Tasks**:
- [ ] Create helper function to render DAG to string
- [ ] Test end-to-end rendering with both engines
- [ ] Visual inspection tests

**Code** (update `src/visualflow/__init__.py`):
```python
"""visualflow - ASCII DAG visualization library.

Generate flawless ASCII diagrams of directed acyclic graphs
with variable-sized boxes.
"""

from visualflow.models import DAG, Node, Edge, LayoutResult, NodePosition, EdgePath
from visualflow.engines import LayoutEngine, GrandalfEngine, GraphvizEngine
from visualflow.render import Canvas

__version__ = "0.1.0"


def render_dag(dag: DAG, engine: LayoutEngine | None = None) -> str:
    """Render a DAG to ASCII string.

    Args:
        dag: The directed acyclic graph to render
        engine: Layout engine to use (defaults to GrandalfEngine)

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
    # Rendering
    "Canvas",
    "render_dag",
]
```

**Tests** (create `tests/test_integration.py`):
```python
"""Integration tests for end-to-end rendering."""

import pytest

from visualflow import render_dag, GrandalfEngine, GraphvizEngine
from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class TestRenderDagGrandalf:
    """Integration tests using GrandalfEngine."""

    def test_render_simple_chain(self) -> None:
        """Render simple chain produces output."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "Task A" in result
        assert "Task B" in result
        assert "Task C" in result

    def test_render_diamond(self) -> None:
        """Render diamond produces output."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 1" in result
        assert "PoC 3" in result

    def test_render_wide_fanout(self) -> None:
        """Render wide fanout produces output."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 3" in result

    def test_render_standalone(self) -> None:
        """Render standalone produces output."""
        dag = create_standalone()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "STRUCTURED TEXT" in result
        assert "DELETE TOOLS" in result

    def test_render_complex_graph(self) -> None:
        """Render complex graph produces output."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 1" in result
        assert "PoC 14" in result

    def test_render_empty_dag(self) -> None:
        """Render empty DAG returns empty string."""
        from visualflow.models import DAG
        dag = DAG()
        result = render_dag(dag, GrandalfEngine())
        assert result == ""


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestRenderDagGraphviz:
    """Integration tests using GraphvizEngine."""

    def test_render_simple_chain(self) -> None:
        """Render simple chain produces output."""
        dag = create_simple_chain()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "Task A" in result

    def test_render_diamond(self) -> None:
        """Render diamond produces output."""
        dag = create_diamond()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "PoC 1" in result

    def test_render_complex_graph(self) -> None:
        """Render complex graph produces output."""
        dag = create_complex_graph()
        result = render_dag(dag, GraphvizEngine())
        assert result


class TestRenderDagDefaultEngine:
    """Tests for render_dag with default engine."""

    def test_default_engine_is_grandalf(self) -> None:
        """Default engine is GrandalfEngine."""
        dag = create_simple_chain()
        result = render_dag(dag)
        assert result
        assert "Task A" in result


class TestVisualInspection:
    """Visual inspection tests - always pass, output for manual review."""

    def test_print_simple_chain(self) -> None:
        """Print simple chain for visual inspection."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Simple Chain (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_diamond(self) -> None:
        """Print diamond for visual inspection."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Diamond (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_wide_fanout(self) -> None:
        """Print wide fanout for visual inspection."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Wide Fanout (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_complex(self) -> None:
        """Print complex graph for visual inspection."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Complex Graph (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)
```

**Verification**:
```bash
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_integration.py -v -s
```

**Output**: ~15 tests passing, visual output printed for inspection

---

## Test Summary

### Affected Tests (Run These)

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `tests/test_models.py` | ~18 | Data model classes |
| `tests/test_canvas.py` | ~14 | Canvas rendering |
| `tests/test_engines.py` | ~30 | Layout engine implementations |
| `tests/test_new_fixtures.py` | ~14 | Fixture validation |
| `tests/test_integration.py` | ~15 | End-to-end rendering |

**Affected tests: ~91 tests**

**Full suite**: ~100 tests (including existing tests)

---

## Production-Grade Checklist

Before marking PoC complete, verify:

- [ ] **OOP Design**: Classes with single responsibility and clear interfaces
- [ ] **Pydantic Models**: All data structures use Pydantic `BaseModel` with validation
- [ ] **Protocol Classes**: LayoutEngine is a Protocol for type checking
- [ ] **Strong Typing**: Type hints on all functions, methods, and class attributes
- [ ] **No mock data**: Fixtures use realistic box content
- [ ] **Real integrations**: Grandalf and Graphviz actually called
- [ ] **Error handling**: Graphviz availability checked, errors raised
- [ ] **Scalable patterns**: Engine abstraction allows easy addition of new engines
- [ ] **Tests in same step**: Each step writes AND runs its tests
- [ ] **Config externalized**: Spacing parameters configurable
- [ ] **Clean separation**: Models, engines, rendering in separate modules
- [ ] **Self-contained**: Works independently; positions boxes without edges (edge routing is PoC2)

---

## What "Done" Looks Like

```bash
# 1. All tests pass
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_models.py tests/test_canvas.py tests/test_engines.py tests/test_new_fixtures.py tests/test_integration.py -v --tb=short
# Expected: All pass (~91 tests)

# 2. Visual inspection shows positioned boxes
cd "/Users/docchang/Development/visualflow" && uv run pytest tests/test_integration.py::TestVisualInspection -v -s
# Expected: ASCII diagrams printed showing boxes in correct positions

# 3. render_dag works via Python
cd "/Users/docchang/Development/visualflow" && uv run python -c "
from visualflow import render_dag, DAG
dag = DAG()
dag.add_node('a', '+-----+\n|  A  |\n+-----+')
dag.add_node('b', '+-----+\n|  B  |\n+-----+')
dag.add_edge('a', 'b')
print(render_dag(dag))
"
# Expected: Two boxes rendered (no edges yet - that's PoC2)
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/visualflow/models.py` | Create | Data model classes |
| `src/visualflow/engines/__init__.py` | Create | Engine exports |
| `src/visualflow/engines/base.py` | Create | LayoutEngine protocol |
| `src/visualflow/engines/grandalf.py` | Create | GrandalfEngine |
| `src/visualflow/engines/graphviz.py` | Create | GraphvizEngine |
| `src/visualflow/render/__init__.py` | Create | Render exports |
| `src/visualflow/render/canvas.py` | Create | Canvas class |
| `src/visualflow/__init__.py` | Modify | Public API exports |
| `tests/fixtures/__init__.py` | Create | Fixture exports |
| `tests/fixtures/boxes.py` | Create | Shared box content |
| `tests/fixtures/simple_chain.py` | Create | Fixture 1 |
| `tests/fixtures/diamond.py` | Create | Fixture 2 |
| `tests/fixtures/wide_fanout.py` | Create | Fixture 3 |
| `tests/fixtures/merge_branch.py` | Create | Fixture 4 |
| `tests/fixtures/skip_level.py` | Create | Fixture 5 |
| `tests/fixtures/standalone.py` | Create | Fixture 6 |
| `tests/fixtures/complex_graph.py` | Create | Fixture 7 |
| `tests/test_models.py` | Create | Model tests |
| `tests/test_canvas.py` | Create | Canvas tests |
| `tests/test_engines.py` | Create | Engine tests |
| `tests/test_new_fixtures.py` | Create | Fixture tests |
| `tests/test_integration.py` | Create | Integration tests |

---

## Dependencies

Update `pyproject.toml` to add Pydantic and wcwidth:

```toml
dependencies = [
    "grandalf>=0.8",
    "pydantic>=2.0",  # Data models with validation
    "wcwidth>=0.2",   # Unicode width calculation (emoji, CJK)
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
]
```

Then run:
```bash
cd "/Users/docchang/Development/visualflow" && uv sync
```

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Grandalf position conversion off | M | Extensive tests, visual inspection |
| Graphviz not installed | M | Skip tests, clear error message |
| Box overlap in complex layouts | L | Explicit no-overlap tests |
| Unicode rendering issues | L | Test with Unicode box chars |

---

## Next Steps After Completion

1. Verify all ~91 tests pass
2. Verify visual inspection shows correct box positioning
3. Proceed to visual-poc2: Edge Routing Implementation
