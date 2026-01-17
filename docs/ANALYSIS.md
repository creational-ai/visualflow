# Layout Engine Analysis for Mission Control Diagrams

## Executive Summary

We need a **layout engine** to compute (x, y) coordinates for task dependency diagrams, then render our own variable-sized ASCII boxes at those positions.

**Recommended: Grandalf** - Pure Python Sugiyama layout library (~600 lines), no external dependencies.

---

## Layout Engine Comparison

| Engine | Language | Install | Integration | Maturity |
|--------|----------|---------|-------------|----------|
| **Grandalf** | Pure Python | `pip install grandalf` | Native | Good (maintained) |
| ascii-dag | Rust | Compile or WASM | CLI/FFI bridge | New (v0.6) |
| Graphviz | C | `brew install graphviz` | PyGraphviz | 30+ years |

### Grandalf (Recommended)

- **Pure Python** - no compilation, no external dependencies
- **Sugiyama algorithm** - same as Graphviz `dot`
- **~600 lines** - simple, readable, hackable
- **Just computes coordinates** - doesn't try to render

```python
from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout

# Build graph
V = [Vertex(data=task) for task in tasks]
E = [Edge(v1, v2) for v1, v2 in dependencies]
g = Graph(V, E)

# Compute layout
sug = SugiyamaLayout(g.C[0])  # Connected component
sug.init_all()
sug.draw()

# Get positions
for v in V:
    x, y = v.view.xy
    w, h = v.view.w, v.view.h
    print(f"{v.data.slug}: ({x}, {y}) size {w}x{h}")
```

### ascii-dag (Alternative)

Rust library we just analyzed. More sophisticated edge routing but requires:
- Rust compilation, or
- WASM bridge, or
- CLI subprocess

Good fallback if Grandalf doesn't handle edge cases well.

---

## What ascii-dag Provides

### 1. Layout Algorithm (Sugiyama)

| Phase | Implementation | Purpose |
|-------|----------------|---------|
| Level Assignment | Iterative Longest Path | Assigns each node to a vertical level |
| Crossing Reduction | Median Heuristic | Minimizes edge crossings |
| X-Coordinate Assignment | Sequential with spacing | Positions nodes horizontally |
| Edge Routing | Dummy nodes + Side-channels | Routes skip-level edges cleanly |

### 2. Layout IR (Intermediate Representation)

The `compute_layout()` function returns a `LayoutIR` with:

```rust
// Node positioning
pub struct LayoutNode<'a> {
    pub id: usize,
    pub label: &'a str,
    pub x: usize,      // X coordinate (left edge, in character cells)
    pub y: usize,      // Y coordinate (top edge, in lines)
    pub width: usize,  // Width in character cells
    pub center_x: usize,
    pub level: usize,
}

// Edge routing
pub struct LayoutEdge {
    pub from_id: usize,
    pub to_id: usize,
    pub from_x: usize, pub from_y: usize,
    pub to_x: usize,   pub to_y: usize,
    pub path: EdgePath,
}

pub enum EdgePath {
    Direct,                           // Straight vertical line
    Corner { horizontal_y: usize },   // L-shaped connection
    SideChannel { channel_x, start_y, end_y },  // Skip-level via side
    MultiSegment { waypoints: Vec<(usize, usize)> },  // Through dummy nodes
}
```

### 3. Canvas Dimensions

```rust
let ir = dag.compute_layout();
ir.width()       // Total canvas width in chars
ir.height()      // Total canvas height in lines
ir.level_count() // Number of vertical levels
```

---

## The Gap: Fixed-Size vs Variable-Size Nodes

### What ascii-dag Does

```
[Root]          <- Fixed width: label length + 2 (brackets)
   │
[ChildA]        <- All nodes are single-line
```

### What We Need

```
┌─────────────────┐
│ poc-1           │     <- Variable height (3-6 lines)
│ Foundation      │     <- Variable width (based on content)
│ ✓ complete      │
└─────────────────┘
        │
        ▼
┌─────────────────────┐
│ poc-2               │
│ Supabase Integration│
│ ✓ complete          │
└─────────────────────┘
```

---

## Integration Strategy: Hybrid Approach

### Option A: Use IR Coordinates Only

1. **Build DAG** with simple labels (task slugs)
2. **Call `compute_layout()`** to get node positions
3. **Use positions as layout hints** for our renderer
4. **Render our own boxes** at those positions with scaling

```
ascii-dag Layout          Our Renderer
──────────────────        ──────────────────
[poc-1] at (0,0)    →     ┌─────────┐ at (0,0)
                          │ poc-1   │
                          │ Found.. │
                          └─────────┘

[poc-2] at (0,3)    →     ┌─────────┐ at (0,6)  <- scaled Y
                          │ poc-2   │
                          └─────────┘
```

**Scaling Factor:**
- X: `node_x * horizontal_scale` (where scale accounts for max box width)
- Y: `node_level * (box_height + edge_lines)`

### Option B: Custom Width via `add_node_with_width()`

ascii-dag supports explicit node widths:

```rust
dag.add_node_with_width(1, "poc-1", 20);  // Width = 20 chars
```

We can:
1. Pre-calculate our box widths
2. Tell ascii-dag about them
3. Get layout with proper spacing

**Limitation:** Still assumes single-line height.

### Option C: Fork and Extend

Modify ascii-dag to support:
- `add_node_with_dimensions(id, label, width, height)`
- Adjust Y-coordinate calculation to use actual heights

**Pros:** Native support for variable heights
**Cons:** Maintenance burden, diverges from upstream

---

## Recommended Approach: Option A + Python Wrapper

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Python Tool                           │
├─────────────────────────────────────────────────────────┤
│  1. Build DAG from Mission Control tasks                │
│  2. Call ascii-dag (via CLI or WASM) for layout         │
│  3. Parse LayoutIR JSON output                          │
│  4. Calculate scaled positions for variable boxes       │
│  5. Render ASCII boxes at scaled positions              │
│  6. Route edges between boxes                           │
└─────────────────────────────────────────────────────────┘
```

### Why This Works

1. **Sugiyama algorithm handles the hard part:**
   - Level assignment (which tasks go on which row)
   - Crossing reduction (minimize tangled edges)
   - Horizontal ordering within levels

2. **We handle rendering:**
   - Variable-size boxes
   - Multi-line content
   - Custom edge characters

3. **Simple scaling math:**
   - Y position = `level * (max_box_height + connection_lines)`
   - X position = `position_in_level * (max_box_width + spacing)`

---

## Implementation Plan

### Phase 1: Build ascii-dag CLI/WASM Bridge

```bash
# Build ascii-dag as CLI tool that outputs JSON
cargo build --release --example layout_json

# Usage:
echo '{"nodes": [...], "edges": [...]}' | ascii-dag-layout
# Output: {"nodes": [...with positions...], "edges": [...with routing...]}
```

Or compile to WASM and call from Python via `wasmtime`.

### Phase 2: Python Layout Processor

```python
# visualflow/layout_engine.py

def compute_layout(tasks: list[Task]) -> LayoutResult:
    """Use ascii-dag to compute positions, then scale for boxes."""

    # 1. Build simple DAG
    dag_input = {
        "nodes": [(t.id, t.slug) for t in tasks],
        "edges": [(t.id, dep_id) for t in tasks for dep_id in t.depends_on]
    }

    # 2. Get layout from ascii-dag
    ir = call_ascii_dag(dag_input)

    # 3. Scale for variable-size boxes
    max_box_height = 5  # lines
    max_box_width = 25  # chars

    scaled_positions = {}
    for node in ir.nodes:
        scaled_positions[node.id] = Position(
            x = node.x * (max_box_width + 4) // node.width,
            y = node.level * (max_box_height + 3),
            width = calculate_box_width(tasks[node.id]),
            height = calculate_box_height(tasks[node.id])
        )

    return LayoutResult(positions=scaled_positions, edges=ir.edges)
```

### Phase 3: ASCII Box Renderer

```python
# visualflow/renderer.py

def render_diagram(layout: LayoutResult, tasks: list[Task]) -> str:
    """Render boxes and edges on ASCII canvas."""

    canvas = Canvas(layout.width, layout.height)

    # Draw boxes at computed positions
    for task in tasks:
        pos = layout.positions[task.id]
        draw_box(canvas, pos, task)

    # Route edges between boxes
    for edge in layout.edges:
        route_edge(canvas, edge, layout.positions)

    return canvas.to_string()
```

---

## Complexity Assessment

| Component | Effort | Notes |
|-----------|--------|-------|
| ascii-dag JSON CLI | Low | ~50 lines Rust |
| Python layout processor | Medium | ~100 lines |
| ASCII box renderer | Medium | ~150 lines |
| Edge routing | Medium-High | ~100 lines, may need iteration |
| **Total** | **~400 lines** | **1 PoC** |

---

## Edge Routing Challenge

The hardest part: routing edges around variable-size boxes.

### ascii-dag's Edge Types

| Type | When Used | Our Translation |
|------|-----------|-----------------|
| `Direct` | Vertically aligned | Straight `│` down |
| `Corner` | Adjacent levels, different X | `└──┐` shape |
| `MultiSegment` | Skip-level edges | Route around intermediate boxes |
| `SideChannel` | Complex routing | Go around the side |

### Our Edge Routing Strategy

1. **Get waypoints from ascii-dag** (it knows the topology)
2. **Scale waypoints to our grid**
3. **Draw ASCII lines** between scaled waypoints
4. **Handle collisions** with boxes (offset or route around)

```
ascii-dag says:           We render:
from (5,0) -> (5,6)       │
via (5,3)                 │
                          ├──┐
                          │  │
                          │  ▼
                          └──┤
```

---

## Next Steps

1. **Compile ascii-dag** to verify it works
2. **Create JSON output example** to understand exact IR format
3. **Prototype Python wrapper** with simple scaling
4. **Test edge routing** on real Mission Control task dependencies
5. **Integrate with Claude skill** for polish pass

---

## Files

```
visualflow/
├── ascii-dag/          # Cloned repository
├── ANALYSIS.md         # This document
├── layout_engine.py    # Python wrapper (TBD)
├── renderer.py         # ASCII box renderer (TBD)
└── cli.rs              # JSON CLI for ascii-dag (TBD)
```
