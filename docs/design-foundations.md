# visualflow Design Foundations

> Consolidated findings from PoC 0 that shape the fundamental design of the `visualflow` library.

**Source**: 66 tests across 3 layout engines (Grandalf, Graphviz, ascii-dag) with 7 graph scenarios

---

## Key Decision

**2 engines: Grandalf (primary) + Graphviz (edge routing)**

| Role | Engine | Why |
|------|--------|-----|
| **Node Positioning** | Grandalf | Pure Python, lowest integration complexity, correct level ordering |
| **Edge Routing Hints** | Graphviz | Provides spline control points that Grandalf lacks |
| **Deferred** | ascii-dag | No Python API; requires Rust code changes for custom input |

---

## Engine Capabilities Reference

### Grandalf (Primary Layout Engine)

**Integration Pattern**:
```python
from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout

class VertexView:
    """Required: Grandalf needs view object with w, h, xy attributes."""
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.xy: tuple[float, float] = (0.0, 0.0)

# Build graph
vertex = Vertex(data=node_data)
vertex.view = VertexView(w=15, h=3)  # REQUIRED

graph = Graph([vertices...], [edges...])

# Compute layout (operates on connected components)
sug = SugiyamaLayout(graph.C[0])  # graph.C[0] = first component
sug.init_all()
sug.draw()

# Access positions
x, y = vertex.view.xy  # Float coordinates
```

**Key Characteristics**:
| Property | Value | Notes |
|----------|-------|-------|
| Coordinate type | `float` | Access via `vertex.view.xy` tuple |
| Y-axis direction | **Increases downward** | Standard Sugiyama convention |
| Custom dimensions | Yes | Via `VertexView.w` and `VertexView.h` |
| Edge routing | **NO** | Only node positions; must compute edges ourselves |
| Disconnected graphs | Via `graph.C` list | Each component laid out separately |

**Critical Requirement**: Every `Vertex` must have a `view` object with `w`, `h`, and `xy` attributes. Without this, `SugiyamaLayout` silently fails to compute positions.

---

### Graphviz (Edge Routing Reference)

**Integration Pattern**:
```python
import subprocess

def build_dot_input(nodes, edges) -> str:
    lines = ["digraph G {", "  rankdir=TB;"]
    for node in nodes:
        # IMPORTANT: fixedsize=true required for custom dimensions
        w_inches = node.width / 10.0  # chars to inches
        h_inches = node.height / 2.0
        lines.append(f'  {node.id} [label="{node.label}" '
                     f'width={w_inches} height={h_inches} fixedsize=true];')
    for edge in edges:
        lines.append(f"  {edge.source} -> {edge.target};")
    lines.append("}")
    return "\n".join(lines)

# Execute
result = subprocess.run(
    ["dot", "-Tplain"],
    input=dot_input,
    capture_output=True,
    text=True
)
```

**Plain Output Format**:
```
graph scale width height
node name x y width height label style shape color fillcolor
edge tail head n x1 y1 ... xn yn [label xl yl] style color
stop
```

**Key Characteristics**:
| Property | Value | Notes |
|----------|-------|-------|
| Coordinate type | `float` (inches) | 72 DPI standard |
| Y-axis direction | **Origin at bottom** | Higher y = closer to top (opposite of Grandalf) |
| Custom dimensions | Yes | Requires `fixedsize=true` attribute |
| Edge routing | **YES** | Spline control points (4+ points per edge) |
| Disconnected graphs | Automatic | All nodes laid out regardless of connectivity |

**Critical Requirement**: Without `fixedsize=true` in DOT input, Graphviz ignores custom width/height and auto-sizes based on label.

---

## Coordinate System Normalization

The two engines use **opposite Y-axis conventions**:

| Engine | Y-axis | "Top" is |
|--------|--------|----------|
| Grandalf | Increases downward | Lower y values |
| Graphviz | Increases upward | Higher y values |

**Normalization Strategy**:
```
Grandalf coordinates → Character grid (direct mapping)
Graphviz coordinates → Flip Y-axis, convert inches to characters

Character grid:
- Origin: top-left (0, 0)
- X increases rightward
- Y increases downward
- Unit: characters (not pixels, not inches)
```

**Conversion Formulas**:
```python
# Grandalf → Character grid
char_x = int(grandalf_x / scale_x)
char_y = int(grandalf_y / scale_y)

# Graphviz → Character grid (flip Y)
char_x = int(graphviz_x * chars_per_inch)
char_y = int((max_y - graphviz_y) * chars_per_inch)  # Flip Y
```

---

## Data Models

### Input Models (from tests/conftest.py)

```python
@dataclass
class Node:
    """Graph node with dimensions."""
    id: str
    label: str
    width: int = 15   # Characters
    height: int = 3   # Lines

@dataclass
class Edge:
    """Directed edge between nodes."""
    source: str  # Node id
    target: str  # Node id

@dataclass
class Graph:
    """Complete graph structure."""
    name: str
    nodes: list[Node]
    edges: list[Edge]
```

### Output Models (to be created)

```python
@dataclass
class NodePosition:
    """Computed position for a node."""
    node_id: str
    x: int       # Character column (left edge of box)
    y: int       # Character row (top edge of box)
    width: int   # Box width in characters
    height: int  # Box height in lines

@dataclass
class EdgePath:
    """Computed path for an edge."""
    source_id: str
    target_id: str
    waypoints: list[tuple[int, int]]  # Character coordinates

@dataclass
class LayoutResult:
    """Complete layout computation result."""
    positions: dict[str, NodePosition]  # node_id → position
    edges: list[EdgePath]
    canvas_width: int   # Total width needed
    canvas_height: int  # Total height needed
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                   Input                          │
│        Graph(nodes, edges)                       │
└─────────────────┬───────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
    ▼                           ▼
┌─────────────┐         ┌─────────────┐
│  Grandalf   │         │  Graphviz   │
│  Adapter    │         │  Adapter    │
│             │         │             │
│ Positions   │         │ Edge hints  │
└──────┬──────┘         └──────┬──────┘
       │                       │
       └───────────┬───────────┘
                   ▼
         ┌─────────────────┐
         │  LayoutResult   │
         │                 │
         │ • positions     │
         │ • edge paths    │
         │ • canvas size   │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │     Canvas      │
         │                 │
         │ 2D char array   │
         │ draw_box()      │
         │ draw_edge()     │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  ASCII String   │
         └─────────────────┘
```

---

## Component Specifications

### 1. LayoutEngine Protocol

```python
from abc import ABC, abstractmethod

class LayoutEngine(ABC):
    """Abstract interface for layout computation."""

    @abstractmethod
    def compute(self, graph: Graph) -> LayoutResult:
        """Compute node positions and canvas size.

        Returns:
            LayoutResult with normalized character coordinates
        """
        pass
```

**Implementations needed**:
- `GrandalfEngine` - Primary layout (positions)
- `GraphvizEngine` - Optional, for edge routing reference

### 2. EdgeRouter Protocol

```python
class EdgeRouter(ABC):
    """Abstract interface for edge path computation."""

    @abstractmethod
    def route(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge]
    ) -> list[EdgePath]:
        """Compute paths for all edges.

        Args:
            positions: Node positions from layout engine
            edges: Edges to route

        Returns:
            List of edge paths with waypoints
        """
        pass
```

**Implementations needed**:
- `SimpleEdgeRouter` - Straight lines with minimal corners (MVP)
- `GraphvizEdgeRouter` - Uses Graphviz spline hints (enhanced)

### 3. Canvas

```python
class Canvas:
    """2D character grid for ASCII rendering."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: list[list[str]] = [[' '] * width for _ in range(height)]

    def draw_box(self, x: int, y: int, w: int, h: int, content: list[str]) -> None:
        """Draw a box with content at position."""
        pass

    def draw_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a line between two points."""
        pass

    def render(self) -> str:
        """Convert grid to string."""
        return '\n'.join(''.join(row).rstrip() for row in self.grid)
```

---

## Box Drawing Characters

```
Box corners and edges:
┌ ─ ┐      Top-left, horizontal, top-right
│   │      Vertical
└ ─ ┘      Bottom-left, horizontal, bottom-right

T-junctions (for edge connections):
├          Left T (edge enters from left)
┤          Right T (edge enters from right)
┬          Top T (edge exits downward)
┴          Bottom T (edge enters from below)
┼          Cross (edges cross)

Connection points:
▼          Arrow down (dependency flows to)
│          Vertical line
─          Horizontal line
```

**Box Format**:
```
┌─────────────────┐
│ task-slug       │  ← Line 1: slug
│ Task Name       │  ← Line 2: name (truncate with ...)
│ ✓ complete      │  ← Line 3: status
└─────────────────┘
```

**Status Indicators**:
- `✓` - complete
- `●` - active
- `○` - planned
- `⊘` - blocked
- `◇` - deferred

---

## Validated Graph Scenarios

All 7 scenarios pass with Grandalf and Graphviz:

| # | Name | Structure | Nodes | Edges | Key Test |
|---|------|-----------|-------|-------|----------|
| 1 | Simple chain | A → B → C | 3 | 2 | Linear vertical flow |
| 2 | Diamond | A → B/C → D | 4 | 4 | Converging paths |
| 3 | Multiple roots | A/B → C | 3 | 2 | Multiple entry points |
| 4 | Skip-level | A → B → C + A → C | 3 | 3 | Mixed depth edges |
| 5 | Wide graph | A → B/C/D/E | 5 | 4 | Horizontal spread |
| 6 | Deep graph | A→B→C→D→E→F | 6 | 5 | Many levels |
| 7 | Complex | Mixed patterns | 6 | 7 | Real-world complexity |

---

## Performance Baseline

From PoC 0 test runs:

| Operation | Time | Notes |
|-----------|------|-------|
| Full test suite (66 tests) | 3.52s | Includes subprocess calls |
| Grandalf tests (18 tests) | 0.03s | Pure Python, fast |
| Graphviz tests (19 tests) | 2.79s | Subprocess overhead |

**Target**: <1 second for graphs up to 50 nodes

**Implication**: Grandalf is fast enough for real-time use. Graphviz edge hints should be optional/cached due to subprocess overhead.

---

## Quality Requirements

From visual-poc-design.md:

> **The diagram must be flawless.**
> - No ugly edge routing
> - No overlapping boxes
> - No misaligned connections
> - No unreadable output
> - Every diagram should look like a human carefully drew it

**Quality Gates**:
1. All 7 scenarios render correctly
2. Level ordering preserved (parent above children)
3. No box overlaps
4. Edges connect at correct points
5. Text fits within boxes (truncate with `...` if needed)

---

## Open Questions for PoC 1

### Answered by PoC 0

| Question | Answer |
|----------|--------|
| How many engines? | 2 (Grandalf + Graphviz) |
| Which engine for positioning? | Grandalf (pure Python, fast) |
| Which engine for edge routing? | Graphviz (spline points) or custom |
| Can engines handle variable sizes? | Yes, both support custom dimensions |
| Any blocking limitations? | No - all scenarios pass |

### To Determine in PoC 1

| Question | Approach |
|----------|----------|
| Minimum readable box width? | Test with real task data |
| Best coordinate scaling factor? | Experiment with different values |
| Edge collision handling? | Start simple, iterate |
| Design for extensibility or simplicity? | Start simple (single engine API), add extensibility if needed |

---

## File Structure for PoC 1

```
visualflow/
├── src/
│   └── visualflow/
│       ├── __init__.py          # Public API
│       ├── models.py            # Node, Edge, Graph, LayoutResult
│       ├── engines/
│       │   ├── __init__.py
│       │   ├── base.py          # LayoutEngine ABC
│       │   └── grandalf.py      # GrandalfEngine
│       ├── routing/
│       │   ├── __init__.py
│       │   ├── base.py          # EdgeRouter ABC
│       │   └── simple.py        # SimpleEdgeRouter
│       └── render/
│           ├── __init__.py
│           ├── canvas.py        # Canvas class
│           └── box.py           # Box rendering helpers
├── tests/
│   ├── conftest.py              # Existing fixtures (7 scenarios)
│   ├── test_grandalf.py         # Existing (keep as reference)
│   ├── test_graphviz.py         # Existing (keep as reference)
│   ├── test_models.py           # New: model tests
│   ├── test_engine.py           # New: GrandalfEngine tests
│   ├── test_router.py           # New: EdgeRouter tests
│   └── test_canvas.py           # New: Canvas tests
└── docs/
    ├── design-foundations.md    # This document
    └── poc0-comparison-matrix.md
```

---

## Summary

**What we learned**:
1. Grandalf is the right choice for positioning (pure Python, fast, correct)
2. Graphviz provides edge routing hints we can use for enhanced quality
3. Both engines handle all 7 graph scenarios correctly
4. Coordinate systems differ (must normalize to character grid)
5. Custom dimensions work in both engines (with specific requirements)

**What we build**:
1. `LayoutEngine` protocol with `GrandalfEngine` implementation
2. `EdgeRouter` protocol with `SimpleEdgeRouter` implementation
3. `Canvas` class for 2D character grid rendering
4. Data models (`Node`, `Edge`, `Graph`, `LayoutResult`, etc.)

**Quality bar**: Flawless ASCII diagrams that look hand-crafted.

---

*Document Status*: Ready for PoC 1 Implementation
*Created*: 2026-01-16
*Source*: visual-poc0-results.md, poc0-comparison-matrix.md
