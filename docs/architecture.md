# visualflow Architecture

> Final design for the ASCII DAG visualization library.

**Version**: 1.0
**Status**: Ready for Implementation

---

## Design Philosophy

**Keep options open, start with simplest viable path.**

1. **Two-engine architecture**: Grandalf for positions, Graphviz for edge hints
2. **Pluggable design**: Easy to swap or combine engines
3. **Real data validation**: Test with actual Mission Control task data
4. **Iterate to flawless**: Start simple, refine until diagrams look hand-crafted
5. **Unicode-ready**: Design for future Unicode support (emojis in content, rich box-drawing characters for edges)

---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Public API                            │
│                                                              │
│   render_dag(dag) -> str   DAG.add_node() / add_edge()      │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      Layout Engine                           │
│                                                              │
│   ┌───────────────┐              ┌───────────────┐          │
│   │   Grandalf    │     OR       │   Graphviz    │          │
│   │  (positions)  │    BOTH      │(pos + edges)  │          │
│   └───────┬───────┘              └───────┬───────┘          │
│           └──────────────┬───────────────┘                  │
│                          ▼                                   │
│                  ┌───────────────┐                          │
│                  │ LayoutResult  │                          │
│                  │ • positions   │                          │
│                  │ • canvas size │                          │
│                  └───────┬───────┘                          │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      Edge Router                             │
│                                                              │
│   ┌───────────────┐              ┌───────────────┐          │
│   │    Simple     │     OR       │   Graphviz    │          │
│   │  (geometric)  │              │ (spline-based)│          │
│   └───────┬───────┘              └───────┬───────┘          │
│           └──────────────┬───────────────┘                  │
│                          ▼                                   │
│                  ┌───────────────┐                          │
│                  │  EdgePaths    │                          │
│                  └───────┬───────┘                          │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                        Canvas                                │
│         Place pre-made boxes, draw edge connections          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │ ASCII String│
                    └─────────────┘
```

---

## Engine Comparison (from PoC 0)

| Capability | Grandalf | Graphviz |
|------------|----------|----------|
| Node positions | ✓ Float (x, y) | ✓ Float (inches) |
| Custom dimensions | ✓ VertexView.w/h | ✓ fixedsize=true |
| Edge routing | ✗ None | ✓ Spline points |
| Integration | Pure Python | Subprocess |
| Speed | Fast (~0.03s) | Slower (~2.79s) |

**Strategy**:
- **MVP**: Grandalf positions + Simple geometric edge routing
- **Enhanced**: Add Graphviz edge hints if simple routing isn't good enough
- **Both engines remain available** throughout development

---

## Data Models

```python
# src/visualflow/models.py

from pydantic import BaseModel, Field, computed_field

class Node(BaseModel):
    """A node in the DAG.

    The `content` field is the COMPLETE box from task's `diagram` field,
    including borders. Width and height are computed from content.
    """
    id: str
    content: str          # Complete box with borders (from task.diagram)

    @computed_field
    @property
    def width(self) -> int:
        """Box width = length of first line."""
        lines = self.content.split('\n')
        return len(lines[0]) if lines else 0

    @computed_field
    @property
    def height(self) -> int:
        """Box height = number of lines."""
        return len(self.content.split('\n'))

class Edge(BaseModel):
    """A directed edge between nodes."""
    source: str
    target: str

class DAG(BaseModel):
    """Directed Acyclic Graph."""
    nodes: dict[str, Node] = Field(default_factory=dict)
    edges: list[Edge] = Field(default_factory=list)

    def add_node(self, id: str, content: str) -> None:
        self.nodes[id] = Node(id=id, content=content)

    def add_edge(self, source: str, target: str) -> None:
        self.edges.append(Edge(source=source, target=target))

class NodePosition(BaseModel):
    """Computed position for a node."""
    node: Node
    x: int      # Left edge (characters)
    y: int      # Top edge (lines)

class LayoutResult(BaseModel):
    """Layout engine output."""
    positions: dict[str, NodePosition]
    width: int
    height: int

class EdgePath(BaseModel):
    """Computed path for an edge."""
    source_id: str
    target_id: str
    segments: list[tuple[int, int, int, int]] = Field(default_factory=list)  # (x1, y1, x2, y2)
```

---

## Component Interfaces

### Layout Engine Protocol

```python
# src/visualflow/engines/base.py

from typing import Protocol

class LayoutEngine(Protocol):
    """Interface for layout computation."""

    def compute(self, dag: DAG) -> LayoutResult:
        """Compute node positions.

        Returns:
            LayoutResult with positions in character coordinates
        """
        ...
```

**Implementations**:
- `GrandalfEngine` - Pure Python, fast, positions only
- `GraphvizEngine` - Subprocess, positions + edge hints

### Edge Router Protocol

```python
# src/visualflow/routing/base.py

from typing import Protocol

class EdgeRouter(Protocol):
    """Interface for edge path computation."""

    def route(
        self,
        positions: dict[str, NodePosition],
        edges: list[Edge],
    ) -> list[EdgePath]:
        """Compute paths for all edges."""
        ...
```

**Implementations**:
- `SimpleRouter` - Geometric routing (vertical + L-shapes)
- `GraphvizRouter` - Uses Graphviz spline control points

---

## Edge Cases (from archived skill)

These patterns MUST be supported for real-world diagrams:

### 1. Dual/Multi Dependency (Many-to-One Merge)

Task depends on multiple parents:

```
┌──────────┐       ┌──────────┐
│  poc-1   │       │  poc-2   │
│  Schema  │       │  Server  │
└────┬─────┘       └────┬─────┘
     │                  │
     └────────┬─────────┘   ← MERGE
              │
              ▼
       ┌──────────┐
       │  poc-3   │         poc-3 depends on BOTH poc-1 AND poc-2
       │   CRUD   │
       └──────────┘
```

### 2. Merge with Independent Branch

One parent merges with another AND has its own independent child:

```
┌──────────────────────────┐                ┌──────────────────────────┐
│          poc-1           │                │          poc-2           │
│         Schema           │                │         Server           │
└─────────┬────┬───────────┘                └────────────┬─────────────┘
          │    │                                         │
          │    └─────────────────────┬───────────────────┘   ← MERGE
          │                          │
          ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│          poc-8           │  │          poc-3           │
│   Database Abstraction   │  │           CRUD           │
│    (only from poc-1)     │  │   (merged from both)     │
└──────────────────────────┘  └──────────────────────────┘
```

### 3. Standalone Tasks

Tasks with no dependencies AND nothing depends on them:

```
═══════════════════════════════════════════════════════════════════════
                           STANDALONE TASKS
═══════════════════════════════════════════════════════════════════════

┌──────────────────────────┐    ┌──────────────────────────┐
│    structured-text       │    │       delete-tools       │
│    (no connections)      │    │    (no connections)      │
└──────────────────────────┘    └──────────────────────────┘
```

### 4. Skip-Level with Sibling

Parent has both direct child AND skip-level connection:

```
┌──────────────────────────┐
│            A             │───────────────────┐
│           Root           │                   │
└─────────────┬────────────┘                   │
              │                                │
              ▼                                │
┌──────────────────────────┐                   │
│            B             │                   │
│          Middle          │                   │
└─────────────┬────────────┘                   │
              │                                │
              ▼                                ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│           C1             │    │           C2             │
│   (depends on B only)    │    │  (depends on A directly) │
└──────────────────────────┘    └──────────────────────────┘
```

### Edge Case Summary

| Pattern | Routing Challenge |
|---------|-------------------|
| Dual dependency | Two lines must merge cleanly |
| Merge + branch | Split then partial merge |
| Standalone | Separate section, no connections |
| Skip-level | Route around intermediate boxes |

---

## Actual Input Data (per task `diagram` field)

Each task's `diagram` field contains the **complete box with borders already drawn**. The engine does NOT draw boxes - it only:
1. **Measures** the box (width/height from the input)
2. **Positions** boxes in the layout
3. **Routes** edges between boxes

This means the engine's job is purely **layout and routing** - the visual content is pre-made.

### Input Example 1: poc-1 (Schema)

```
┌─────────────────────────┐
│        PoC 1            │
│        SCHEMA           │
│      ✅ Complete        │
│                         │
│ Database                │
│   • projects (18 cols)  │
│   • project_history     │
│                         │
│ Infrastructure          │
│   • config.py           │
│   • db.py (client)      │
│   • seed_data.py        │
└─────────────────────────┘
```

### Input Example 2: poc-3 (CRUD)

```
┌─────────────────────────┐
│        PoC 3            │
│         CRUD            │
│      ✅ Complete        │
│                         │
│ Tools                   │
│   • list_projects       │
│   • get_project         │
│   • create_project      │
│   • update_project      │
│                         │
│ Patterns                │
│   • ToolResponse<T>     │
│   • Auto-slug           │
└─────────────────────────┘
```

### Input Example 3: hierarchy-b (Phase B)

```
┌─────────────────────────────┐
│   HIERARCHY REFACTOR        │
│       PHASE B               │
│      ✅ Complete            │
│                             │
│ New Milestones Layer        │
│   • 24-column table         │
│   • Strategic fields        │
│   • JSONB flexibility       │
│                             │
│ Tasks Updated               │
│   • milestone_id FK         │
│   • Filter by milestone     │
│   • Link/unlink support     │
│                             │
│ Projects Enhanced           │
│   • 6 strategic fields      │
│   • Business context        │
│                             │
│ Tools                       │
│   • 5 milestone tools       │
│   • 24 total registered     │
└─────────────────────────────┘
```

### Input Example 4: delete-tools (Standalone)

```
┌─────────────────────────┐
│    DELETE TOOLS         │
│      ✅ Complete        │
│                         │
│ delete_milestone        │
│   • Removes milestone   │
│   • Tasks unlinked      │
│     (SET NULL)          │
│   • Returns count       │
│                         │
│ delete_task             │
│   • Dependency check    │
│   • Blocks if depended  │
│   • force=True override │
│   • Cleans depends_on   │
└─────────────────────────┘
```

**Key observations**:
- Input is the **complete box** with borders already drawn
- Engine measures width/height by parsing the input
- Engine does NOT modify box content - only positions it
- Width = length of first line (or any line, they're all equal)
- Height = number of lines

---

## End-to-End Usage Example

### Step 1: Get tasks from Mission Control

```python
tasks = list_tasks(project_slug="mission-control")
# Returns list of task dicts with: slug, name, depends_on, diagram, ...
```

### Step 2: Build DAG via MC Adapter

```python
from visualflow.adapters.mission_control import from_tasks

dag = from_tasks(tasks)

# Internally does:
# - For each task: dag.add_node(id=task.slug, content=task.diagram)
# - For each task with depends_on: dag.add_edge(source=dep, target=task.slug)
```

### Step 3: Render

```python
from visualflow import render_dag

output = render_dag(dag)
print(output)
```

### Step 4: Output

```
┌─────────────────────────┐       ┌─────────────────────────┐
│        PoC 1            │       │        PoC 2            │
│        SCHEMA           │       │        SERVER           │
│      ✅ Complete        │       │      ✅ Complete        │
│         ...             │       │         ...             │
└────────────┬────────────┘       └────────────┬────────────┘
             │                                 │
             └──────────────┬──────────────────┘
                            │
                            ▼
                  ┌─────────────────────────┐
                  │        PoC 3            │
                  │         CRUD            │
                  │      ✅ Complete        │
                  │         ...             │
                  └─────────────────────────┘
```

**Alignment verification** (box width=27, center=13):
- `┬` at position 13 in bottom border (12 dashes before, 12 after)
- `│` directly below `┬`
- `▼` directly above target box center
- Target box centered under merge point

---

## Test Fixtures from Real Data

Based on actual Mission Control tasks, here are 7 test scenarios covering all routing patterns.

**Note**: Diagrams below show simplified boxes for layout illustration. Actual fixtures use full `diagram` field content from tasks.

### Fixture 1: Simple Chain (visual milestone)

```
visual-poc0 → visual-poc1 → visual-poc2

┌──────────────────┐
│ visual-poc0      │
│ Exploration      │
│ ○ planned        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ visual-poc1      │
│ Design & Arch    │
│ ○ planned        │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ visual-poc2      │
│ Interface Layer  │
│ ○ planned        │
└──────────────────┘
```

**Tests**: Vertical alignment, correct level ordering

---

### Fixture 2: Diamond Pattern (PoC merge)

```
poc-1, poc-2 → poc-3 → poc-5, poc-6 → poc-7

┌──────────┐       ┌──────────┐
│  poc-1   │       │  poc-2   │
│  Schema  │       │  Server  │
└────┬─────┘       └────┬─────┘
     │                  │
     └────────┬─────────┘
              │
              ▼
       ┌──────────┐
       │  poc-3   │
       │   CRUD   │
       └────┬─────┘
            │
     ┌──────┴──────┐
     │             │
     ▼             ▼
┌──────────┐ ┌──────────┐
│  poc-5   │ │  poc-6   │
│ Workflow │ │ Analysis │
└────┬─────┘ └────┬─────┘
     │             │
     └──────┬──────┘
            │
            ▼
       ┌──────────┐
       │  poc-7   │
       │   E2E    │
       └──────────┘
```

**Tests**: Multiple roots merge, fan-out, fan-in

---

### Fixture 3: Wide Fan-out (poc-3 children)

```
poc-3 → poc-4, poc-5, poc-6, bugs

                    ┌──────────┐
                    │  poc-3   │
                    │   CRUD   │
                    └────┬─────┘
                         │
     ┌───────────┬───────┼───────┬───────────┐
     │           │       │       │           │
     ▼           ▼       ▼       ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ poc-4  │ │ poc-5  │ │ poc-6  │ │  bugs  │ │pydantic│
│History │ │Workflow│ │Analysis│ │12-29   │ │refactor│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
```

**Tests**: 5-way fan-out, horizontal edge distribution

---

### Fixture 4: Merge with Independent Branch (poc-1 pattern)

```
poc-1 → poc-3 (shared with poc-2) AND poc-1 → poc-8 (independent)

┌──────────────────────────┐                ┌──────────────────────────┐
│          poc-1           │                │          poc-2           │
│         Schema           │                │         Server           │
└─────────┬────┬───────────┘                └────────────┬─────────────┘
          │    │                                         │
          │    └─────────────────────┬───────────────────┘
          │                          │
          ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│          poc-8           │  │          poc-3           │
│   Database Abstraction   │  │           CRUD           │
└──────────────────────────┘  └──────────────────────────┘
```

**Tests**: Split from one parent, partial merge with another, independent branch

---

### Fixture 5: Skip-level with Sibling (mock)

```
A → B → C1 with A → C2 direct edge (skip-level)

┌──────────────────────────┐
│            A             │───────────────────┐
│           Root           │                   │
└─────────────┬────────────┘                   │
              │                                │
              ▼                                │
┌──────────────────────────┐                   │
│            B             │                   │
│          Middle          │                   │
└─────────────┬────────────┘                   │
              │                                │
              ▼                                ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│           C1             │    │           C2             │
│   (depends on B only)    │    │  (depends on A directly) │
└──────────────────────────┘    └──────────────────────────┘
```

**Tests**: Skip-level routing around intermediate box, sibling at same level

---

### Fixture 6: Standalone Tasks

```
Tasks with no dependencies AND nothing depends on them

═══════════════════════════════════════════════════════════════════════
                           STANDALONE TASKS
═══════════════════════════════════════════════════════════════════════

┌──────────────────────────┐    ┌──────────────────────────┐
│    structured-text       │    │       delete-tools       │
│      ✓ complete          │    │       ✓ complete         │
└──────────────────────────┘    └──────────────────────────┘
```

**Tests**: Detect standalone, render in separate section, no edge routing

---

### Fixture 7: Complex Graph (core milestone subset)

```
poc-1 → poc-8 → poc-9 → poc-11, poc-12, pydantic
                              ↓
                           poc-13 → poc-14 → hierarchy-a → hierarchy-b

┌──────────┐
│  poc-1   │
│  Schema  │
└────┬─────┘
     │
     ├─────────────────────────┐
     │                         │
     ▼                         ▼
┌──────────┐             ┌──────────┐
│  poc-3   │             │  poc-8   │
│   CRUD   │             │ Abstract │
└──────────┘             └────┬─────┘
                              │
                              ▼
                        ┌──────────┐
                        │  poc-9   │
                        │ Migration│
                        └────┬─────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
    ┌──────────┐       ┌──────────┐       ┌──────────┐
    │  poc-11  │       │  poc-12  │       │ pydantic │
    │   Dev    │       │ MS DB    │       │ refactor │
    └──────────┘       └────┬─────┘       └──────────┘
                            │
                            ▼
                      ┌──────────┐
                      │  poc-13  │
                      │ MS Tools │
                      └────┬─────┘
                           │
                           ▼
                      ┌──────────┐
                      │  poc-14  │
                      │  Integ   │
                      └────┬─────┘
                           │
                           ▼
                      ┌──────────┐
                      │hierarch-a│
                      │  Phase A │
                      └────┬─────┘
                           │
                           ▼
                      ┌──────────┐
                      │hierarch-b│
                      │  Phase B │
                      └──────────┘
```

**Tests**: Mix of all patterns, real-world complexity

---

## Edge Routing Strategies

### Strategy 1: Simple Geometric (MVP)

```python
def route_simple(source: NodePosition, target: NodePosition) -> list[Segment]:
    """Route using simple geometric rules."""
    src_x = source.x + source.node.width // 2  # Bottom center
    src_y = source.y + source.node.height

    tgt_x = target.x + target.node.width // 2  # Top center
    tgt_y = target.y

    if src_x == tgt_x:
        # Straight vertical
        return [(src_x, src_y, tgt_x, tgt_y)]
    else:
        # Z-shape: down, horizontal, down
        mid_y = (src_y + tgt_y) // 2
        return [
            (src_x, src_y, src_x, mid_y),      # Down from source
            (src_x, mid_y, tgt_x, mid_y),      # Horizontal
            (tgt_x, mid_y, tgt_x, tgt_y),      # Down to target
        ]
```

### Strategy 2: Graphviz Spline (Enhanced)

```python
def route_graphviz(
    source: NodePosition,
    target: NodePosition,
    spline_points: list[tuple[float, float]],
) -> list[Segment]:
    """Convert Graphviz bezier spline to line segments."""
    # Sample spline at regular intervals
    # Convert to character coordinates
    # Return as line segments
```

---

## Edge Connection Points

**Critical**: Off-by-one errors break visual alignment. Use these exact calculations.

### Box Geometry

```
          x (left edge)
          │
          ▼
     ┌────────────┐  ← y (top edge)
     │   content  │
     │   content  │
     └─────┬──────┘  ← y + height - 1 (bottom edge)
           │
           │ ← exit_x = x + width // 2
           │
```

### Connection Point Calculations

```python
# Box properties
box_x = position.x           # Left edge
box_y = position.y           # Top edge
box_w = node.width           # Total width including borders
box_h = node.height          # Total height including borders

# Exit point (bottom center) - where edge leaves source box
exit_x = box_x + box_w // 2  # Integer division
exit_y = box_y + box_h       # One below bottom border

# Entry point (top center) - where edge enters target box
entry_x = box_x + box_w // 2
entry_y = box_y - 1          # One above top border
```

**Even vs Odd Widths**:
- Odd width (e.g., 13): center at position 6, symmetric
- Even width (e.g., 12): center at position 6, one less dash on right

```
Odd (13):  └─────┬─────┘   (5 dashes, ┬, 5 dashes) ← symmetric
Even (12): └─────┬────┘    (5 dashes, ┬, 4 dashes) ← asymmetric but consistent
```

**Rule**: Always use `width // 2` for center. Vertical lines MUST align with this position.

### Border Character Placement

When a box has an outgoing edge, replace the bottom border `─` with `┬`:

```python
# For box width = 12 (including borders)
# └──────────┘  (no edge)
# └─────┬────┘  (with edge at center)

center_offset = box_w // 2  # = 6 for width 12
# Character at position center_offset in bottom border becomes ┬
```

**Example** (width=12):
```
Position: 0  1  2  3  4  5  6  7  8  9  10 11
  Normal: └  ─  ─  ─  ─  ─  ─  ─  ─  ─  ─  ┘
 W/Edge:  └  ─  ─  ─  ─  ─  ┬  ─  ─  ─  ─  ┘
                            ↑
                      center (6)
```

### Vertical Alignment Verification

The `│` and `▼` must align exactly with `┬`:

```
┌──────────┐      width=12, center=6
│  poc-1   │
└─────┬────┘      ┬ at column x+6
      │           │ at column x+6
      │           │ at column x+6
      ▼           ▼ at column x+6
┌──────────┐      target box centered under edge
│  poc-2   │
└──────────┘
```

### Merge Point Alignment

When two edges merge, the horizontal connector must land exactly:

```
┌──────────┐           ┌──────────┐
│  poc-1   │           │  poc-2   │
└─────┬────┘           └─────┬────┘
      │                      │
      └──────────┬───────────┘   ← horizontal at same y
                 │
                 ▼
           ┌──────────┐
           │  poc-3   │
           └──────────┘
```

**Merge calculation**:
```python
merge_y = (src1_exit_y + target_entry_y) // 2
merge_x = (src1_exit_x + src2_exit_x) // 2  # Center between sources
```

---

## Box Handling

**Important**: The engine does NOT draw boxes. Boxes come pre-made from the task's `diagram` field.

### What the Engine Does

1. **Measure**: Parse box to get width (line length) and height (line count)
2. **Position**: Place box at computed (x, y) coordinates on canvas
3. **Detect connection points**: Find center of bottom edge for exit, top edge for entry
4. **Modify for routing**: Replace `─` with `┬` at exit point in bottom border

### Connection Point Detection

The engine must find the center of the bottom border for edge routing:

```python
def find_exit_point(box_content: str, box_x: int, box_y: int) -> tuple[int, int]:
    """Find the exit point (bottom center) of a pre-made box."""
    lines = box_content.split('\n')
    width = len(lines[0])
    height = len(lines)

    exit_x = box_x + width // 2
    exit_y = box_y + height - 1  # Bottom border line
    return exit_x, exit_y
```

### Modifying Bottom Border for Edges

When a box has an outgoing edge, replace the `─` at center with `┬`:

```python
def add_exit_connector(box_content: str) -> str:
    """Add ┬ connector at bottom center of box."""
    lines = box_content.split('\n')
    bottom = list(lines[-1])
    center = len(bottom) // 2
    bottom[center] = '┬'
    lines[-1] = ''.join(bottom)
    return '\n'.join(lines)
```

**Before**: `└─────────────────────────┘`
**After**:  `└────────────┬────────────┘`

---

## File Structure

```
visualflow/
├── pyproject.toml
├── src/
│   └── visualflow/
│       ├── __init__.py           # Public API
│       ├── models.py             # DAG, Node, Edge, etc.
│       ├── engines/
│       │   ├── __init__.py
│       │   ├── base.py           # LayoutEngine protocol
│       │   ├── grandalf.py       # GrandalfEngine
│       │   └── graphviz.py       # GraphvizEngine
│       ├── routing/
│       │   ├── __init__.py
│       │   ├── base.py           # EdgeRouter protocol
│       │   ├── simple.py         # SimpleRouter
│       │   └── graphviz.py       # GraphvizRouter
│       ├── render/
│       │   ├── __init__.py
│       │   └── canvas.py         # Canvas: place boxes, draw edges (not box drawing)
│       └── adapters/
│           ├── __init__.py
│           └── mission_control.py # MC list_tasks adapter
└── tests/
    ├── conftest.py               # Existing + new fixtures
    ├── fixtures/
    │   ├── simple_chain.py       # Fixture 1: visual milestone (3 nodes)
    │   ├── diamond.py            # Fixture 2: poc merge pattern (6 nodes)
    │   ├── wide_fanout.py        # Fixture 3: poc-3 children (6 nodes)
    │   ├── merge_branch.py       # Fixture 4: merge + independent branch (4 nodes)
    │   ├── skip_level.py         # Fixture 5: skip-level with sibling (4 nodes)
    │   ├── standalone.py         # Fixture 6: standalone tasks (2 nodes)
    │   └── complex.py            # Fixture 7: core subset (12 nodes)
    ├── test_grandalf.py          # Existing
    ├── test_graphviz.py          # Existing
    ├── test_models.py
    ├── test_engines.py
    ├── test_routing.py
    ├── test_canvas.py
    └── test_render.py            # End-to-end with all 7 fixtures
```

---

## Implementation Order

### Phase 1: Foundation

| Step | Deliverable | Tests |
|------|-------------|-------|
| 1 | `models.py` - DAG, Node, Edge | test_models.py |
| 2 | `canvas.py` - place_box, draw_edge | test_canvas.py |
| 3 | 7 test fixtures from real data | fixtures/*.py |

### Phase 2: Layout Engines

| Step | Deliverable | Tests |
|------|-------------|-------|
| 4 | `GrandalfEngine` | test_engines.py (grandalf) |
| 5 | `GraphvizEngine` | test_engines.py (graphviz) |
| 6 | Compare both engines on 7 fixtures | visual comparison |

### Phase 3: Edge Routing

| Step | Deliverable | Tests |
|------|-------------|-------|
| 7 | `SimpleRouter` | test_routing.py (simple) |
| 8 | `GraphvizRouter` | test_routing.py (graphviz) |
| 9 | Compare both routers on 7 fixtures | visual comparison |

### Phase 4: Integration

| Step | Deliverable | Tests |
|------|-------------|-------|
| 10 | `render_dag()` function | test_render.py |
| 11 | MC adapter `from_tasks()` | test_mc_adapter.py |
| 12 | Polish and quality iteration | all 7 fixtures flawless |

---

## Decision Points

At each phase, we evaluate and decide:

| Phase | Decision | Criteria |
|-------|----------|----------|
| After Phase 2 | Use Grandalf only, Graphviz only, or both? | Position accuracy, speed |
| After Phase 3 | Use Simple routing, Graphviz routing, or hybrid? | Visual quality |
| After Phase 4 | Ready for release or needs iteration? | All 7 fixtures flawless |

---

## Quality Criteria

**Every diagram must**:
- [ ] Show correct parent-child relationships
- [ ] Have no overlapping boxes
- [ ] Have edges that connect at correct points
- [ ] Handle all 7 test fixtures correctly
- [ ] Support all edge cases:
  - [ ] Dual/multi dependency (merge pattern)
  - [ ] Merge with independent branch
  - [ ] Standalone tasks (separate section)
  - [ ] Skip-level with sibling
- [ ] Look like it was hand-drawn by a careful human

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Layout engines** | Both available (Grandalf + Graphviz) |
| **Edge routing** | Both available (Simple + Graphviz) |
| **Test data** | 7 fixtures from real MC tasks |
| **Approach** | Start simple, compare, iterate |
| **Quality bar** | Flawless on all 7 fixtures |

**Key Principles**:
1. **Open-minded**: Both engines and routers available, decide based on evidence
2. **Real data**: All fixtures derived from actual Mission Control tasks
3. **Edge cases covered**: Merge, branch, standalone, skip-level all designed in
4. **Quality first**: Every diagram must look hand-crafted

---

## Unicode Support

### PoC 1: Emoji/Wide Character Width (Implemented)

Node content may contain emojis and CJK characters that occupy 2 terminal columns:
- Uses `wcwidth` library for accurate width calculation
- `Node.width` property handles wide characters correctly
- Falls back to `len()` for non-printable characters

### PoC 2: Rich Edge Characters (Planned)

The initial implementation uses basic ASCII characters for edge routing. PoC 2 will add:

**Rich Box-Drawing Characters**
- Smooth corners: `╭`, `╮`, `╰`, `╯`
- Rounded connections for cleaner visual flow
- Thicker lines for emphasis: `┃`, `━`, `┏`, `┓`

**Edge Line Styles**
- Single: `│`, `─`, `┌`, `┐`, `└`, `┘`
- Double: `║`, `═`, `╔`, `╗`, `╚`, `╝`
- Rounded: `╭`, `╮`, `╰`, `╯`
- Arrows: `→`, `←`, `↑`, `↓`, `▶`, `▼`

**Implementation Notes**
- Consider a `RenderStyle` enum or config for line style selection
- Test rendering across different terminal emulators

---

## Fixture Summary

| # | Name | Pattern | Nodes | Edge Case |
|---|------|---------|-------|-----------|
| 1 | Simple Chain | A → B → C | 3 | Basic vertical |
| 2 | Diamond | Merge → Fan-out → Merge | 6 | Dual dependency |
| 3 | Wide Fan-out | 1 → 5 | 6 | Horizontal spread |
| 4 | Merge + Branch | Split + partial merge | 4 | Independent branch |
| 5 | Skip-level | A → B → C1, A → C2 | 4 | Route around box |
| 6 | Standalone | No connections | 2 | Separate section |
| 7 | Complex | Real-world mix | 12 | All patterns |

---

*Document Status*: Final - Ready for PoC 1 Implementation
*Created*: 2026-01-16
