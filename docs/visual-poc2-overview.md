# visual-poc2 Overview

> **Purpose**: Add edge routing to produce complete ASCII DAG diagrams with connections between boxes
>
> **Important**: Each step must be self-contained (works independently; doesn't break existing functionality and existing tests)

## Executive Summary

**Goal**: Implement edge routing that connects positioned boxes with clean ASCII lines, producing flawless diagrams that look hand-crafted.

**Strategy**:
1. First, fix canvas unicode handling so wide characters (emoji, CJK) render correctly
2. Then implement SimpleRouter for geometric edge routing
3. Finally, integrate edge rendering into the canvas

**Migration Approach**: Add new routing module alongside existing code. Existing `render_dag()` continues working (boxes only) while new edge routing is added incrementally.

---

## Current Architecture

### What We Have Today (Post-PoC 1)

**1. Data Models (`src/visualflow/models.py`)**
- `Node`, `Edge`, `DAG` - Core data structures
- `NodePosition`, `LayoutResult` - Layout output
- `EdgePath` - Edge routing output (defined but unused)
- `Node.width` uses `wcwidth` for accurate width measurement

**2. Layout Engines (`src/visualflow/engines/`)**
- `GrandalfEngine` - Pure Python, fast (~0.03s), positions only
- `GraphvizEngine` - Subprocess, slower (~2.79s), positions + edge hints
- Both produce `LayoutResult` with box positions

**3. Canvas (`src/visualflow/render/canvas.py`)**
- `place_box()` - Places pre-made boxes at positions
- `put_char()` - Places single characters
- `render()` - Outputs final ASCII string

**4. Integration (`src/visualflow/__init__.py`)**
- `render_dag(dag, engine)` - Computes layout, places boxes, returns string
- Currently produces positioned boxes WITHOUT edge connections

### Current Limitation: Canvas Unicode Bug

The canvas has a bug with wide characters in `place_box()`:

```python
# Current code (canvas.py:39-43)
for col_offset, char in enumerate(line):
    canvas_x = x + col_offset
    self._grid[canvas_y][canvas_x] = char
```

**Problem**: This iterates by character index, not column position. Wide characters (emoji, CJK) occupy 2 terminal columns but are 1 Python character:
- String `"🚀AB"` has 3 characters but 4 columns (🚀=2, A=1, B=1)
- Current code places `🚀` at column 0, `A` at column 1, `B` at column 2
- Should place `🚀` at column 0, `A` at column 2, `B` at column 3

This must be fixed FIRST before edge routing, otherwise edge positions will be wrong for boxes containing wide characters.

---

## Target Architecture

### Desired State

```
┌─────────────────────────────────────────────────────────────┐
│                        Public API                            │
│                                                              │
│   render_dag(dag, engine, router) -> str                    │
└──────────────────────────────┬──────────────────────────────┘
                               │
            ┌──────────────────┴──────────────────┐
            ▼                                      ▼
┌───────────────────────┐              ┌───────────────────────┐
│    Layout Engine       │              │     Edge Router        │
│    (positions)         │              │    (connections)       │
└───────────┬────────────┘              └───────────┬────────────┘
            │                                       │
            └──────────────────┬────────────────────┘
                               ▼
                    ┌───────────────────────┐
                    │        Canvas          │
                    │  • place_box (unicode) │
                    │  • draw_edge (NEW)     │
                    └───────────┬────────────┘
                               │
                               ▼
                        ┌─────────────┐
                        │ ASCII String│
                        └─────────────┘
```

### New Components

1. **Unicode-aware Canvas** - `place_box()` tracks column positions using wcwidth
2. **EdgeRouter Protocol** - Interface for edge path computation
3. **SimpleRouter** - Geometric routing (vertical + Z-shapes)
4. **Canvas.draw_edge()** - Renders edge paths as ASCII characters

---

## What Needs to Change

### 1. Canvas Unicode Fix (`src/visualflow/render/canvas.py`)

#### `place_box()` method
**Current**: Iterates by character index
```python
for col_offset, char in enumerate(line):
    canvas_x = x + col_offset
    self._grid[canvas_y][canvas_x] = char
```

**New**: Track column position using wcwidth
```python
from wcwidth import wcwidth

col = 0
for char in line:
    canvas_x = x + col
    if 0 <= canvas_x < self.width and 0 <= canvas_y < self.height:
        self._grid[canvas_y][canvas_x] = char
        # Mark next cell as continuation if wide char
        char_width = wcwidth(char)
        if char_width == 2 and canvas_x + 1 < self.width:
            self._grid[canvas_y][canvas_x + 1] = ""  # Placeholder
    col += max(1, wcwidth(char))
```

**Also update `render()` method**:
```python
def render(self) -> str:
    """Render the canvas to a string."""
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

**Validation**:
- Existing tests pass
- New unicode placement test with emoji boxes

---

### 2. Edge Router Protocol (`src/visualflow/routing/base.py`) - NEW

```python
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

---

### 3. Simple Router (`src/visualflow/routing/simple.py`) - NEW

Geometric routing with three patterns:
1. **Straight vertical** - When source and target centers align
2. **Z-shape** - Down from source, horizontal, down to target
3. **Merge handling** - Multiple sources converging to one target

---

### 4. Canvas Edge Drawing (`src/visualflow/render/canvas.py`)

Add `draw_edge()` method:
```python
def draw_edge(self, path: EdgePath) -> None:
    """Draw edge path on canvas using box-drawing characters."""
    for x1, y1, x2, y2 in path.segments:
        # Draw line segment with appropriate characters
        ...
```

Character selection:
- Vertical: `│`
- Horizontal: `─`
- Corners: `┌`, `┐`, `└`, `┘`
- Connectors: `┬`, `┴`, `├`, `┤`, `┼`
- Arrow: `▼` (at target entry point)

---

## PoC Breakdown

### Step 1: Canvas Unicode Fix

**Prerequisites**:
- PoC 1 complete (167 tests passing)
- `wcwidth` already installed

**Implementation**:
1. Update `place_box()` to use column-aware positioning
2. Handle wide character placeholders in grid
3. Update `render()` to skip placeholder cells

**Design Decision**: Use empty string `""` as placeholder for wide char continuation

To keep Step 1 self-contained and non-breaking:
- **Keep** existing `place_box()` behavior for ASCII-only content
- **Add** wide character handling alongside
- **Why**: Ensures all existing tests pass without modification
- **Migration path**: Step 2+ builds on unicode-correct foundation

**Success Criteria**:
- [ ] All 167 existing tests pass
- [ ] New test: box with emoji renders correctly
- [ ] New test: box with CJK characters renders correctly
- [ ] Edge positions calculated correctly for wide-char boxes

---

### Step 2: EdgeRouter Protocol & SimpleRouter

**Depends on**: Step 1

**Implementation**:
1. Create `src/visualflow/routing/` directory
2. Create `EdgeRouter` protocol in `base.py`
3. Implement `SimpleRouter` in `simple.py`
4. Handle straight vertical and Z-shape patterns

**Success Criteria**:
- [ ] SimpleRouter computes paths for simple_chain fixture
- [ ] SimpleRouter computes paths for diamond fixture (merge)
- [ ] All segments are valid (integers, within canvas bounds)
- [ ] All existing tests still pass

---

### Step 3: Canvas Edge Drawing

**Depends on**: Step 2

**Implementation**:
1. Add `draw_edge(path: EdgePath)` method to Canvas
2. Implement character selection for line segments
3. Handle intersections (use `┼` when lines cross)
4. Add arrow `▼` at target entry point

**Success Criteria**:
- [ ] Edges render correctly for simple_chain
- [ ] Edges render correctly for diamond (merge lines)
- [ ] No character collisions with boxes
- [ ] All existing tests still pass

---

### Step 4: Integration & Visual Verification

**Depends on**: Step 3

**Implementation**:
1. Update `render_dag()` to accept optional `router` parameter
2. Default to `SimpleRouter` if edges exist
3. Visual verification on all 7 fixtures
4. Iterate on edge routing quality

**Success Criteria**:
- [ ] All 7 fixtures render with edges
- [ ] Diagrams look "hand-crafted" (quality bar)
- [ ] No overlapping edges with boxes
- [ ] Performance <1s for complex_graph

---

## Implementation Approaches

### Option A: Simple Geometric Router (Recommended)

**Pros**:
- Pure Python, no external dependencies
- Fast execution
- Easy to debug and iterate
- Sufficient for most DAG patterns

**Cons**:
- May produce suboptimal paths for complex graphs
- Limited collision avoidance

---

### Option B: Graphviz-based Router

**Pros**:
- Professional-grade routing algorithm
- Handles complex edge crossings

**Cons**:
- Requires subprocess call (slower)
- Spline-to-ASCII conversion is lossy
- Added complexity

---

### Option C: Hybrid (Simple + Graphviz fallback)

**Pros**:
- Best of both worlds
- Can use Graphviz for specific complex patterns

**Cons**:
- More code to maintain
- Complexity in deciding when to use each

---

## Recommended Approach

**Option A (Simple Geometric Router)** for these reasons:

1. **Simplicity**: Pure Python, easy to understand and modify
2. **Speed**: No subprocess overhead
3. **Iteration**: Easy to refine routing rules based on visual output
4. **Coverage**: Handles all 7 fixtures (simple chain, diamond, fan-out, etc.)
5. **Extensibility**: Can add Graphviz router later if needed

---

## Files Requiring Changes

| File | Change Type | Complexity | Step |
|------|-------------|------------|------|
| `src/visualflow/render/canvas.py` | Modify | Medium | 1, 3 |
| `src/visualflow/routing/__init__.py` | Create | Low | 2 |
| `src/visualflow/routing/base.py` | Create | Low | 2 |
| `src/visualflow/routing/simple.py` | Create | Medium | 2 |
| `src/visualflow/__init__.py` | Modify | Low | 4 |
| `tests/test_canvas.py` | Modify | Low | 1 |
| `tests/test_routing.py` | Create | Medium | 2, 3 |
| `tests/test_integration.py` | Modify | Low | 4 |

**Total Estimated Effort**: 4 steps in PoC 2

---

## Testing Strategy

### 1. Unit Tests for Canvas Unicode

```python
def test_place_box_with_emoji():
    """Box containing emoji renders at correct position."""
    canvas = Canvas(width=30, height=5)
    box = "┌─────┐\n│ 🚀  │\n└─────┘"
    canvas.place_box(box, 0, 0)
    # Verify emoji occupies correct columns

def test_place_box_with_cjk():
    """Box containing CJK characters renders correctly."""
    canvas = Canvas(width=30, height=5)
    box = "┌─────┐\n│ 中文 │\n└─────┘"
    canvas.place_box(box, 0, 0)
    # Verify CJK chars occupy 2 columns each
```

### 2. Unit Tests for Edge Routing

```python
def test_simple_router_vertical():
    """Aligned boxes get straight vertical edge."""

def test_simple_router_z_shape():
    """Offset boxes get Z-shaped edge."""

def test_simple_router_merge():
    """Multiple parents merge correctly."""
```

### 3. Integration Tests

```python
def test_render_with_edges_simple_chain():
    """Simple chain renders with vertical edges."""

def test_render_with_edges_diamond():
    """Diamond pattern renders with merge edges."""
```

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Wide char handling breaks existing tests | Low | Run full test suite after each change |
| Edge routing produces ugly diagrams | Medium | Iterate on routing rules; visual inspection |
| Edge-box collisions | Medium | Route edges through gaps; add collision detection |
| Merge point calculation errors | Low | Explicit tests for merge patterns |

---

## Design Decisions Made

1. **Use empty string as wide-char placeholder**: Simpler than sentinel values, `render()` can filter them out
2. **SimpleRouter first, Graphviz later if needed**: Start simple, add complexity only if required
3. **Box-drawing characters for edges**: `│`, `─`, `┌`, `┐`, etc. for clean appearance
4. **Arrow at target only**: `▼` indicates direction without cluttering
5. **Z-shape as default non-vertical routing**: Simple, predictable, readable

---

## Open Questions (For Later)

1. **Unicode edge characters**: Should we support rounded corners (`╭╮╰╯`) in this PoC or defer to PoC 3?
2. **Edge style configuration**: Should `RenderStyle` enum be added now or later?
3. **Collision avoidance complexity**: How sophisticated should edge-box collision handling be?

---

## Next Steps

1. Review this overview and confirm approach
2. Create implementation plan using `/dev-plan visual-poc2`
3. Implement and test each step
4. Visual verification on all 7 fixtures
