# PoC 3: Box Connectors & Smart Routing

## Executive Summary

PoC 3 enhances edge routing with three features:
1. **Box connectors** - Place `┬` on box bottom borders where edges exit
2. **Trunk-and-split** - Same-layer targets share trunk before splitting
3. **Merge routing** - Multiple sources merge at junction before reaching target

## Current State (PoC 2)

```
SimpleRouter._route_edge()
├── Exit point: always box center (box.x + width // 2)
├── Entry point: target center top
├── Routes: vertical, Z-shape, or L-shape
└── Returns: EdgePath with segments

Canvas.draw_edge()
├── Draws segments (|, -)
├── Places corners (┌┐└┘)
└── Combines into T-junctions (┬┴├┤)
```

**Limitations:**
1. All edges from same source exit from same center point
2. No `┬` connector on box borders
3. No awareness of which edges should share a trunk

**Test coverage:** 223 tests passing, 27 in `test_real_diagrams.py`

---

## Problems to Solve

### Problem 1: Box Connectors

| Before | After |
|--------|-------|
| `└───────────┘` | `└─────┬─────┘` |
| `      \|      ` | `      \|      ` |

The `┬` connector visually integrates the edge with the box border.

### Non-Problem: Basic Fan-out (Z-shape)

The current routing uses Z-shapes from center - this already works:

```
     ┌───────────┐
     │   PoC 0   │
     └───────────┘
          |
 ┌--------┴--------┐
 v        v        v
```

Each edge independently routes from center using Z-shape. No changes needed.

### Problem 2: Trunk-and-Split (Cleaner Fan-out)

**Optional enhancement**: For same-layer targets (nodes at same y-position/rank), use a shared vertical trunk before splitting horizontally. Produces cleaner diagrams:

```
     ┌───────────┐
     │   PoC 0   │
     └─────┬─────┘
           |
    ┌──────┴──────┐
    v             v
  PoC 1         PoC 2
```

### Problem 3: Merge Routing (Fan-in)

Multiple sources merging into one target:

```
┌─────────────┐          ┌─────────────┐
│    poc-1    │          │    poc-2    │
└──┬─────┬────┘          └──────┬──────┘
   │     │                      │
   │     └──────────┬───────────┘  ← MERGE
   │                │
   v                v
┌─────────────┐  ┌─────────────┐
│    poc-8    │  │    poc-3    │
└─────────────┘  └─────────────┘
```

**Key requirements:**
- poc-1 has TWO exit points (one independent, one merge)
- Merge edges meet at `┬` junction above poc-3
- Single vertical line drops to target

---

## Research Findings

We investigated whether Grandalf or Graphviz provide solutions for these problems.

### Available but Unused

| Tool | Feature | Why Not Using |
|------|---------|---------------|
| Grandalf | `sug.layers` | Available but not exposed by GrandalfEngine - could add if needed |
| Grandalf | `route_with_lines` | Single-edge only, not multi-exit |
| Grandalf | `route_with_splines` | Bezier curves, not ASCII grid |
| Graphviz | Edge spline points | Bezier curves, ignored in parser |

**Note**: For same-layer detection, we can use y-position comparison from existing positions dict instead of `sug.layers`.

### Conclusion

**Custom implementation required.** Neither library handles:
- Multiple exit points from same box
- Trunk-and-split patterns
- Merge routing optimization
- ASCII box connector placement

These are character-grid specific problems. We'll use y-position comparison from the existing positions dict for layer grouping and implement routing ourselves.

---

## Solution Design

### Routing Decision Tree

```
For each edge:
├── Is target shared by multiple sources?
│   └── YES → Merge routing
│             Route to merge point, join edges, single drop
│
├── Does source have multiple edges to same-layer targets?
│   └── YES → Trunk-and-split
│             Shared trunk, horizontal split, individual drops
│
└── Default → Basic routing (existing Z-shape or L-shape)
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `analyze_edges()` | Group by source, identify target layers |
| `analyze_merges()` | Detect edges to same target |
| `calculate_exit_points()` | Space exits on box border |
| `route_trunk_split()` | Fan-out: shared trunk → split |
| `route_merge_edges()` | Fan-in: merge → single drop |
| `place_box_connectors()` | Add `┬` on box borders |

### Exit Point Calculation

```python
def calculate_exit_points(source_pos, num_exits):
    """Space exit points evenly on box bottom border."""
    if num_exits == 1:
        return [source_pos.x + source_pos.node.width // 2]  # Center

    box_left = source_pos.x + 1
    box_right = source_pos.x + source_pos.node.width - 2
    usable_width = box_right - box_left
    spacing = usable_width // (num_exits + 1)
    return [box_left + spacing * (i + 1) for i in range(num_exits)]
```

---

## Implementation Plan

### Files to Modify

| File | Changes |
|------|---------|
| `routing/simple.py` | Add analysis, exit points, trunk-split, merge routing |
| `render/canvas.py` | Add `place_box_connectors()` |
| `__init__.py` | Update `render_dag()` to call connector placement |

### Implementation Steps

1. Add `analyze_edges()` - group edges by source, identify target layers
2. Add `analyze_merges()` - detect edges to same target from different sources
3. Add `calculate_exit_points()` - compute x-offsets for multi-exit
4. Modify `_route_edge()` to accept exit_x parameter
5. Add `_route_trunk_split()` for fan-out
6. Add `_route_merge_edges()` for fan-in
7. Add `place_box_connectors()` to canvas
8. Update `render_dag()` to call connector placement

---

## Validation Tests

Create `tests/test_poc3_routing.py` with these test classes:

| Class | Problem | Tests |
|-------|---------|-------|
| `TestBoxConnectors` | 1 | Connector at center, aligns with edge |
| `TestTrunkAndSplit` | 2 | Same-layer share trunk, junction char |
| `TestMergeRouting` | 3 | Two sources merge, merge + independent |
| `TestEdgesDontCrossBoxes` | All | Diamond preserves box content |

### Test Execution

```bash
# Before implementation (establish baseline - all fail)
uv run pytest tests/test_poc3_routing.py -v

# During implementation (track progress)
uv run pytest tests/test_poc3_routing.py -v --tb=short

# After implementation (all pass)
uv run pytest tests/ -v
```

### Sample Test

```python
def test_single_edge_has_connector_at_center(self):
    """Single outgoing edge has ┬ at center of box bottom."""
    dag = DAG()
    dag.add_node("a", "┌─────┐\n│  A  │\n└─────┘")
    dag.add_node("b", "┌─────┐\n│  B  │\n└─────┘")
    dag.add_edge("a", "b")

    result = render_dag(dag)
    assert "└──┬──┘" in result, "Expected ┬ connector on box bottom"
```

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing routing | High | Run all 223 tests after each change |
| Exit points outside box | Medium | Clamp to border bounds, min 2 char spacing |
| Overlapping lines | Medium | Use existing junction logic |

---

## Success Criteria

- [ ] `┬` connectors on box bottom borders at edge exit points
- [ ] Same-layer targets share trunk before splitting (Problem 2)
- [ ] Multiple sources merge at `┬` junction above target (Problem 3)
- [ ] All 223+ existing tests pass
- [ ] No edges route through box content
- [ ] Validation tests pass

---

## Open Questions

| Question | Status |
|----------|--------|
| Boxes too narrow for multiple exits? | Clamp to border, min 2 char spacing |
| Trunk-split for 3+ same-layer targets? | Yes, detect via y-position comparison |
| Route around intermediate boxes? | Deferred - not in PoC 3 scope |

---

*Status:* Research complete, ready for implementation
*Created:* January 2026
