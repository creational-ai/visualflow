# visual-poc3 Implementation Plan

> **Track Progress**: See `docs/visual-poc3-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-16T21:15:03-0800 |
| **Name** | Box Connectors and Smart Routing |
| **Type** | PoC |
| **Proves** | SimpleRouter can place box connectors and use trunk-and-split/merge routing patterns for cleaner diagrams |
| **Production-Grade Because** | Real geometric calculations; pluggable enhancement to existing router; all 223+ tests continue passing |

---

## Deliverables

Concrete capabilities this task delivers:

- Box connectors (`┬`) placed on box bottom borders at edge exit points
- Trunk-and-split routing for fan-out to same-layer targets
- Merge routing for fan-in from multiple sources to single target
- Exit point calculation for multiple outgoing edges from same node
- All existing tests pass (non-breaking enhancement)

---

## Prerequisites

Complete these BEFORE starting implementation steps.

### 1. Identify Affected Tests

**Why Needed**: Run only affected tests during implementation (not full suite)

**Affected test files**:
- `tests/test_routing.py` - SimpleRouter tests (Steps 1, 2, 3)
- `tests/test_canvas.py` - Canvas edge drawing tests (Step 4)
- `tests/test_integration.py` - End-to-end render_dag tests (Step 5)
- `tests/test_real_diagrams.py` - Real diagram tests (Step 5)
- `tests/test_poc3_routing.py` - NEW: PoC 3 specific tests (all steps)

**Baseline verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py tests/test_canvas.py tests/test_integration.py tests/test_real_diagrams.py -v --tb=short
# Expected: All pass (establishes baseline)
```

### 2. Verify Current Test Count

**Why Needed**: Ensure all 223 existing tests pass before modifications

**Commands**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ --tb=short -q
# Expected: 223 tests pass
```

### 3. Review Current Router Implementation

**Why Needed**: Understand existing code structure for extension

**Key files**:
- `src/visualflow/routing/simple.py` - Current SimpleRouter
- `src/visualflow/render/canvas.py` - Current Canvas with draw_edge
- `src/visualflow/__init__.py` - render_dag function

**Verification** (inline OK for prerequisites):
```bash
python -c "from visualflow.routing import SimpleRouter; from visualflow.render import Canvas; print('Imports OK')"
# Expected: "Imports OK"
```

---

## Success Criteria

From `docs/visual-poc3-overview.md`:

- [ ] Box connectors (`┬`) placed on box bottom borders at edge exit points
- [ ] Same-layer targets share trunk before splitting (trunk-and-split)
- [ ] Multiple sources merge at `┬` junction above target (merge routing)
- [ ] All 223+ existing tests pass
- [ ] No edges route through box content
- [ ] Validation tests pass

---

## Traceability Matrix

Maps overview problems to implementation steps and validation tests.

### Problems → Steps

| Overview Problem | Implementation Step | Validation |
|------------------|---------------------|------------|
| Problem 1: Box Connectors | Step 5: Box Connector Placement | Visual: `┬` appears on box bottom |
| Problem 2: Trunk-and-Split | Step 3: Trunk-and-Split Routing | Visual: shared trunk, horizontal split |
| Problem 3: Merge Routing (Basic) | Step 4: Merge Routing | Visual: edges converge at junction |
| Problem 3: Mixed Routing (Full) | Step 4b: Mixed Routing | Visual: independent + merge from same source |
| (Supporting) Edge Analysis | Step 1: Edge Analysis Functions | Unit tests for grouping |
| (Supporting) Exit Points | Step 2: Exit Point Calculation | Unit tests for spacing |
| (Integration) render_dag | Step 6: Integration | End-to-end diagram tests |
| (Integration) Smart Routing | Step 6b: Smart Routing Integration | Connectors match edge routing pattern |

### Key Functions → Steps

| Overview Function | Implementation Method | Step |
|-------------------|----------------------|------|
| `analyze_edges()` | `SimpleRouter._analyze_edges()` | Step 1 |
| `analyze_merges()` | `SimpleRouter._find_merge_targets()` | Step 1 |
| `calculate_exit_points()` | `SimpleRouter._calculate_exit_points()` | Step 2 |
| `route_trunk_split()` | `SimpleRouter._route_trunk_split()` | Step 3 |
| `route_merge_edges()` | `SimpleRouter._route_merge_edges()` | Step 4 |
| `classify_edges()` | `SimpleRouter._classify_edges()` | Step 4b |
| `allocate_exit_points()` | `SimpleRouter._allocate_exit_points()` | Step 4b |
| `route_mixed()` | `SimpleRouter._route_mixed()` | Step 4b |
| `place_box_connectors()` | `Canvas.place_box_connectors()` | Step 5 |
| `route()` (smart) | `SimpleRouter.route()` | Step 6b |
| `_find_same_layer_targets()` | `Canvas._find_same_layer_targets()` | Step 6b |

### Validation Test Classes (from Overview)

| Test Class | Problem | Where Implemented |
|------------|---------|-------------------|
| `TestBoxConnectorPlacement` | 1 | Step 5 + Step 6 + Step 6b |
| `TestTrunkAndSplitRouting` | 2 | Step 3 + Step 6b |
| `TestMergeRouting` | 3 (Basic) | Step 4 + Step 6 |
| `TestMixedRouting` | 3 (Full) | Step 4b |
| `TestEdgesDontCrossBoxes` | All | Step 7 |

---

## Architecture

### File Structure
```
src/visualflow/
├── __init__.py                    # Updated: call connector placement
├── routing/
│   ├── __init__.py
│   ├── base.py
│   └── simple.py                  # Updated: analysis + smart routing
└── render/
    ├── __init__.py
    └── canvas.py                  # Updated: place_box_connectors
tests/
├── test_routing.py                # Updated: new routing tests
├── test_canvas.py                 # Updated: connector tests
├── test_integration.py            # Existing
├── test_real_diagrams.py          # Existing
└── test_poc3_routing.py           # NEW: PoC 3 specific tests
```

### Design Principles
1. **OOP Design**: Extend SimpleRouter class, Canvas class
2. **Non-breaking**: Add alongside existing methods, don't replace
3. **Strong Typing**: Type hints on all new functions and methods
4. **Self-contained**: Each problem can be tested independently

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

> **Note**: This PoC implements the routing methods as standalone functions (`_route_trunk_split()`, `_route_merge_edges()`, `_route_mixed()`). Integration into the main `route()` method to automatically select routing patterns is deferred to future work. The current scope focuses on box connectors (integrated via `place_box_connectors()`) and building the analysis and routing primitives.

---

## Implementation Steps

**Approach**: Build incrementally - first edge analysis, then exit points, then trunk-split, then merge, then connectors. Each step is independently testable.

> Each step includes its tests. Write code, write tests, run tests, verify all pass - then move on. Never separate code and tests into different steps.

### Step 0: Create Test File and Verify Baseline

**Goal**: Create the PoC 3 test file and confirm all existing tests pass

**Tasks**:
- [ ] Create `tests/test_poc3_routing.py` with test structure
- [ ] Run full test suite to verify baseline

**Code** (create `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
"""Tests for PoC 3: Box Connectors and Smart Routing.

Tests cover:
- Problem 1: Box connectors (┬ on box bottom)
- Problem 2: Trunk-and-split (fan-out to same-layer targets)
- Problem 3: Merge routing (fan-in from multiple sources)
"""

import pytest

from visualflow import DAG, render_dag, GrandalfEngine
from visualflow.models import Node, Edge, NodePosition
from visualflow.routing import SimpleRouter
from visualflow.render import Canvas


def make_test_box(label: str, width: int = 15, height: int = 3) -> str:
    """Create a simple test box with label.

    Args:
        label: Text to display in box
        width: Total width including borders
        height: Total height (default 3)

    Returns:
        Multi-line string box with borders
    """
    inner_width = width - 2
    lines = []
    lines.append("+" + "-" * inner_width + "+")
    for _ in range((height - 2) // 2):
        lines.append("|" + " " * inner_width + "|")
    lines.append("|" + label.center(inner_width) + "|")
    for _ in range((height - 2) - (height - 2) // 2):
        lines.append("|" + " " * inner_width + "|")
    lines.append("+" + "-" * inner_width + "+")
    return "\n".join(lines)


# =============================================================================
# STEP 0: BASELINE TESTS
# =============================================================================

class TestPoc3Baseline:
    """Baseline tests - existing functionality still works."""

    def test_existing_simple_chain_renders(self) -> None:
        """Simple chain still renders correctly."""
        dag = DAG()
        dag.add_node("a", make_test_box("A"))
        dag.add_node("b", make_test_box("B"))
        dag.add_edge("a", "b")
        result = render_dag(dag)
        assert "A" in result
        assert "B" in result

    def test_existing_diamond_renders(self) -> None:
        """Diamond pattern still renders correctly."""
        dag = DAG()
        dag.add_node("a", make_test_box("A"))
        dag.add_node("b", make_test_box("B"))
        dag.add_node("c", make_test_box("C"))
        dag.add_node("d", make_test_box("D"))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")
        result = render_dag(dag)
        assert "A" in result
        assert "D" in result
```

**Verification**:
```bash
# Run new test file
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py -v --tb=short
# Expected: 2/2 tests pass

# Run full suite to confirm baseline
cd /Users/docchang/Development/visualflow && uv run pytest tests/ --tb=short -q
# Expected: 225 tests pass (223 + 2 new)
```

**Output**: Baseline established, 225/225 tests passing

**Visual Diagram Verification** (Step 0 wrap-up):
```python
# Quick visual check that baseline renders correctly
def test_step0_visual_baseline():
    """Visual verification: baseline diagram renders without errors."""
    dag = DAG()
    dag.add_node("a", "+-------+\n|   A   |\n+-------+")
    dag.add_node("b", "+-------+\n|   B   |\n+-------+")
    dag.add_node("c", "+-------+\n|   C   |\n+-------+")
    dag.add_edge("a", "b")
    dag.add_edge("a", "c")
    dag.add_edge("b", "c")

    result = render_dag(dag)
    print("\n=== Step 0: Baseline Diamond ===")
    print(result)
    print("=" * 40)

    # Verify structure
    assert "A" in result
    assert "B" in result
    assert "C" in result
    assert "|" in result  # Has edges
```

---

### Step 1: Edge Analysis Functions

**Goal**: Add functions to analyze edge patterns (same-source edges, same-target edges, same-layer detection)

**Tasks**:
- [ ] Add `_analyze_edges()` method to SimpleRouter
- [ ] Add `_find_same_layer_targets()` helper
- [ ] Add `_find_merge_targets()` helper
- [ ] Write tests for analysis functions

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Add these methods to the SimpleRouter class (after existing methods):

```python
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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 1: EDGE ANALYSIS TESTS
# =============================================================================

class TestEdgeAnalysis:
    """Tests for edge analysis functions."""

    def test_analyze_edges_groups_by_source(self) -> None:
        """analyze_edges groups edges by source node."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))
        node_b = Node(id="b", content=make_test_box("B"))
        node_c = Node(id="c", content=make_test_box("C"))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=0, y=10),
            "c": NodePosition(node=node_c, x=20, y=10),
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
        ]

        by_source, by_target = router._analyze_edges(positions, edges)

        assert "a" in by_source
        assert len(by_source["a"]) == 2

    def test_analyze_edges_groups_by_target(self) -> None:
        """analyze_edges groups edges by target node."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))
        node_b = Node(id="b", content=make_test_box("B"))
        node_c = Node(id="c", content=make_test_box("C"))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=20, y=0),
            "c": NodePosition(node=node_c, x=10, y=10),
        }
        edges = [
            Edge(source="a", target="c"),
            Edge(source="b", target="c"),
        ]

        by_source, by_target = router._analyze_edges(positions, edges)

        assert "c" in by_target
        assert len(by_target["c"]) == 2

    def test_find_same_layer_targets_identifies_common_y(self) -> None:
        """find_same_layer_targets returns targets at same y position."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))
        node_b = Node(id="b", content=make_test_box("B"))
        node_c = Node(id="c", content=make_test_box("C"))
        node_d = Node(id="d", content=make_test_box("D"))

        positions = {
            "a": NodePosition(node=node_a, x=20, y=0),
            "b": NodePosition(node=node_b, x=0, y=10),   # Same y
            "c": NodePosition(node=node_c, x=20, y=10),  # Same y
            "d": NodePosition(node=node_d, x=40, y=10),  # Same y
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
            Edge(source="a", target="d"),
        ]

        same_layer = router._find_same_layer_targets(positions, edges)

        assert len(same_layer) == 3
        assert set(same_layer) == {"b", "c", "d"}

    def test_find_same_layer_targets_returns_empty_for_single(self) -> None:
        """find_same_layer_targets returns empty if only one target per layer."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))
        node_b = Node(id="b", content=make_test_box("B"))
        node_c = Node(id="c", content=make_test_box("C"))

        positions = {
            "a": NodePosition(node=node_a, x=10, y=0),
            "b": NodePosition(node=node_b, x=0, y=10),   # Different y
            "c": NodePosition(node=node_c, x=20, y=20),  # Different y
        }
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
        ]

        same_layer = router._find_same_layer_targets(positions, edges)

        assert same_layer == []

    def test_find_merge_targets_identifies_fan_in(self) -> None:
        """find_merge_targets returns targets with multiple incoming edges."""
        router = SimpleRouter()

        edges_by_target = {
            "a": [Edge(source="x", target="a")],           # Single source
            "b": [Edge(source="x", target="b"),
                  Edge(source="y", target="b")],           # Multiple sources
        }

        merge_targets = router._find_merge_targets(edges_by_target)

        assert merge_targets == ["b"]
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestEdgeAnalysis -v --tb=short
# Expected: 5/5 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All existing routing tests still pass
```

**Output**: Analysis tests passing, existing tests still pass

**Visual Diagram Verification** (Step 1 wrap-up):
```python
def test_step1_visual_analysis():
    """Visual verification: edge analysis correctly identifies patterns."""
    router = SimpleRouter()

    # Create fan-out scenario (1 source -> 3 targets at same layer)
    node_a = Node(id="a", content=make_test_box("ROOT", width=15))
    node_b = Node(id="b", content=make_test_box("B", width=9))
    node_c = Node(id="c", content=make_test_box("C", width=9))
    node_d = Node(id="d", content=make_test_box("D", width=9))

    positions = {
        "a": NodePosition(node=node_a, x=15, y=0),
        "b": NodePosition(node=node_b, x=0, y=8),
        "c": NodePosition(node=node_c, x=15, y=8),
        "d": NodePosition(node=node_d, x=30, y=8),
    }
    edges = [
        Edge(source="a", target="b"),
        Edge(source="a", target="c"),
        Edge(source="a", target="d"),
    ]

    by_source, by_target = router._analyze_edges(positions, edges)
    same_layer = router._find_same_layer_targets(positions, edges)

    print("\n=== Step 1: Edge Analysis ===")
    print(f"Edges by source 'a': {len(by_source.get('a', []))} edges")
    print(f"Same-layer targets: {same_layer}")
    print("=" * 40)

    assert len(by_source["a"]) == 3
    assert set(same_layer) == {"b", "c", "d"}
```

---

### Step 2: Exit Point Calculation

**Goal**: Calculate multiple exit points on box bottom border for fan-out

**Tasks**:
- [ ] Add `_calculate_exit_points()` method to SimpleRouter
- [ ] Handle edge cases (single exit, narrow boxes)
- [ ] Write tests for exit point calculation

**Code** (add to `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Add this method to the SimpleRouter class:

```python
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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 2: EXIT POINT CALCULATION TESTS
# =============================================================================

class TestExitPointCalculation:
    """Tests for exit point calculation."""

    def test_single_exit_at_center(self) -> None:
        """Single exit point is at box center."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A", width=15))
        pos = NodePosition(node=node, x=0, y=0)

        exits = router._calculate_exit_points(pos, 1)

        assert len(exits) == 1
        assert exits[0] == 7  # center of 15-wide box at x=0

    def test_two_exits_left_and_right(self) -> None:
        """Two exits are spaced left and right of center."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A", width=15))
        pos = NodePosition(node=node, x=0, y=0)

        exits = router._calculate_exit_points(pos, 2)

        assert len(exits) == 2
        assert exits[0] < exits[1]  # Left before right
        # Should be roughly at 1/3 and 2/3 of usable width
        assert exits[0] >= 1  # Not at corner
        assert exits[1] <= 13  # Not at corner

    def test_three_exits_evenly_spaced(self) -> None:
        """Three exits are evenly spaced across box."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A", width=21))  # Wide box
        pos = NodePosition(node=node, x=0, y=0)

        exits = router._calculate_exit_points(pos, 3)

        assert len(exits) == 3
        # Check even spacing
        spacing1 = exits[1] - exits[0]
        spacing2 = exits[2] - exits[1]
        assert spacing1 == spacing2

    def test_narrow_box_clamps_to_center(self) -> None:
        """Narrow box with many exits falls back to center."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A", width=7))  # Narrow
        pos = NodePosition(node=node, x=0, y=0)

        exits = router._calculate_exit_points(pos, 5)  # More exits than space

        assert len(exits) == 5
        # All should be at center when box is too narrow
        assert all(x == exits[0] for x in exits)

    def test_zero_exits_returns_empty(self) -> None:
        """Zero exits returns empty list."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A"))
        pos = NodePosition(node=node, x=0, y=0)

        exits = router._calculate_exit_points(pos, 0)

        assert exits == []

    def test_exit_points_with_offset_position(self) -> None:
        """Exit points account for box x offset."""
        router = SimpleRouter()
        node = Node(id="a", content=make_test_box("A", width=15))
        pos = NodePosition(node=node, x=10, y=0)  # Offset by 10

        exits = router._calculate_exit_points(pos, 1)

        assert exits[0] == 17  # 10 + 7 (center of 15-wide box)
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestExitPointCalculation -v --tb=short
# Expected: 6/6 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All existing routing tests still pass
```

**Output**: Exit point tests passing, existing tests still pass

**Visual Diagram Verification** (Step 2 wrap-up):
```python
def test_step2_visual_exit_points():
    """Visual verification: exit points are correctly spaced on box bottom."""
    router = SimpleRouter()

    # Box with width=21 (usable width = 19 after corners)
    node = Node(id="a", content=make_test_box("ROUTER", width=21))
    pos = NodePosition(node=node, x=0, y=0)

    # Calculate exit points for 1, 2, and 3 exits
    exits_1 = router._calculate_exit_points(pos, 1)
    exits_2 = router._calculate_exit_points(pos, 2)
    exits_3 = router._calculate_exit_points(pos, 3)

    print("\n=== Step 2: Exit Point Calculation ===")
    print(f"Box width: 21, usable: 19")
    print(f"1 exit:  {exits_1} (center)")
    print(f"2 exits: {exits_2} (left/right thirds)")
    print(f"3 exits: {exits_3} (evenly spaced)")

    # Visual representation of exit points on box bottom
    box_bottom = list("+-------------------+")
    for x in exits_3:
        if 0 <= x < len(box_bottom):
            box_bottom[x] = "┬"
    print(f"Visual:  {''.join(box_bottom)}")
    print("=" * 40)

    assert len(exits_1) == 1
    assert len(exits_2) == 2
    assert len(exits_3) == 3
```

---

### Step 3: Trunk-and-Split Routing

**Goal**: Implement trunk-and-split routing for same-layer fan-out

**Tasks**:
- [ ] Add `_route_trunk_split()` method to SimpleRouter
- [ ] Write tests for trunk-and-split pattern

**Note**: This method is standalone. Integration into the main `route()` method is deferred to future work.

**Code** (add to `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Add this method to the SimpleRouter class:

```python
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

        # Calculate trunk endpoint (row above targets)
        target_y = target_positions[0][1].y
        trunk_end_y = target_y - 1

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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 3: TRUNK-AND-SPLIT ROUTING TESTS
# =============================================================================

class TestTrunkAndSplitRouting:
    """Tests for trunk-and-split routing pattern."""

    def test_trunk_split_creates_paths_for_all_targets(self) -> None:
        """Trunk-split creates a path for each target."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))
        node_c = Node(id="c", content=make_test_box("C", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=20, y=0),
            "b": NodePosition(node=node_b, x=0, y=10),
            "c": NodePosition(node=node_c, x=40, y=10),
        }

        paths = router._route_trunk_split(
            positions, "a", ["b", "c"], exit_x=27  # center of A
        )

        assert len(paths) == 2
        assert paths[0].source_id == "a"
        assert paths[1].source_id == "a"
        target_ids = {p.target_id for p in paths}
        assert target_ids == {"b", "c"}

    def test_trunk_split_has_vertical_and_horizontal_segments(self) -> None:
        """Trunk-split paths have correct segment structure."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))
        node_c = Node(id="c", content=make_test_box("C", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=20, y=0),
            "b": NodePosition(node=node_b, x=0, y=10),
            "c": NodePosition(node=node_c, x=40, y=10),
        }

        paths = router._route_trunk_split(
            positions, "a", ["b", "c"], exit_x=27
        )

        # Each path should have segments
        for path in paths:
            assert len(path.segments) >= 1
            # Verify segments are valid (x1,y1,x2,y2 tuples)
            for seg in path.segments:
                assert len(seg) == 4
                assert all(isinstance(coord, int) for coord in seg)

    def test_trunk_split_handles_single_target(self) -> None:
        """Trunk-split with single target just routes normally."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=10, y=0),
            "b": NodePosition(node=node_b, x=10, y=10),
        }

        paths = router._route_trunk_split(
            positions, "a", ["b"], exit_x=17
        )

        assert len(paths) == 1

    def test_trunk_split_empty_targets_returns_empty(self) -> None:
        """Trunk-split with no targets returns empty list."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
        }

        paths = router._route_trunk_split(
            positions, "a", [], exit_x=7
        )

        assert paths == []

    def test_trunk_split_missing_source_returns_empty(self) -> None:
        """Trunk-split with missing source returns empty list."""
        router = SimpleRouter()
        node_b = Node(id="b", content=make_test_box("B"))

        positions = {
            "b": NodePosition(node=node_b, x=0, y=10),
        }

        paths = router._route_trunk_split(
            positions, "nonexistent", ["b"], exit_x=7
        )

        assert paths == []
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestTrunkAndSplitRouting -v --tb=short
# Expected: 5/5 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All existing routing tests still pass
```

**Output**: Trunk-split tests passing, existing tests still pass

**Visual Diagram Verification** (Step 3 wrap-up):
```python
def test_step3_visual_trunk_split():
    """Visual verification: trunk-split pattern renders correctly.

    Expected pattern (from overview Problem 2):
         ┌───────────┐
         │   ROOT    │
         └─────┬─────┘
               |
        ┌──────┴──────┐
        v             v
      PoC 1         PoC 2
    """
    dag = DAG()
    dag.add_node("root", make_test_box("ROOT", width=15))
    dag.add_node("left", make_test_box("LEFT", width=11))
    dag.add_node("right", make_test_box("RIGHT", width=11))
    dag.add_edge("root", "left")
    dag.add_edge("root", "right")

    result = render_dag(dag)
    print("\n=== Step 3: Trunk-and-Split Pattern ===")
    print(result)
    print("=" * 40)

    # Verify structure
    assert "ROOT" in result
    assert "LEFT" in result
    assert "RIGHT" in result
    # After Step 6 integration, should have ┬ connector
```

---

### Step 4: Merge Routing

**Goal**: Implement merge routing for fan-in from multiple sources

**Tasks**:
- [ ] Add `_route_merge_edges()` method to SimpleRouter
- [ ] Calculate merge junction point
- [ ] Write tests for merge routing pattern

**Note**: This method is standalone. Integration into the main `route()` method is deferred to future work.

**Code** (add to `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Add this method to the SimpleRouter class:

```python
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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 4: MERGE ROUTING TESTS
# =============================================================================

class TestMergeRouting:
    """Tests for merge routing pattern (fan-in)."""

    def test_merge_creates_paths_for_all_sources(self) -> None:
        """Merge routing creates a path for each source."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))
        node_c = Node(id="c", content=make_test_box("C", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=30, y=0),
            "c": NodePosition(node=node_c, x=15, y=15),
        }

        paths = router._route_merge_edges(
            positions, ["a", "b"], "c"
        )

        assert len(paths) == 2
        source_ids = {p.source_id for p in paths}
        assert source_ids == {"a", "b"}
        assert all(p.target_id == "c" for p in paths)

    def test_merge_paths_have_segments(self) -> None:
        """Merge paths have valid segment structure."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))
        node_c = Node(id="c", content=make_test_box("C", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=30, y=0),
            "c": NodePosition(node=node_c, x=15, y=15),
        }

        paths = router._route_merge_edges(
            positions, ["a", "b"], "c"
        )

        for path in paths:
            assert len(path.segments) >= 1
            for seg in path.segments:
                assert len(seg) == 4
                assert all(isinstance(coord, int) for coord in seg)

    def test_merge_converges_at_target_x(self) -> None:
        """Merge paths converge at target x coordinate."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A", width=15))
        node_b = Node(id="b", content=make_test_box("B", width=15))
        node_c = Node(id="c", content=make_test_box("C", width=15))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=30, y=0),
            "c": NodePosition(node=node_c, x=15, y=15),  # center at x=22
        }

        paths = router._route_merge_edges(
            positions, ["a", "b"], "c"
        )

        target_center_x = 15 + 7  # 22
        for path in paths:
            # Last segment should end at target center
            last_seg = path.segments[-1]
            assert last_seg[2] == target_center_x or last_seg[0] == target_center_x

    def test_merge_empty_sources_returns_empty(self) -> None:
        """Merge with no sources returns empty list."""
        router = SimpleRouter()
        node_c = Node(id="c", content=make_test_box("C"))

        positions = {
            "c": NodePosition(node=node_c, x=10, y=10),
        }

        paths = router._route_merge_edges(positions, [], "c")

        assert paths == []

    def test_merge_missing_target_returns_empty(self) -> None:
        """Merge with missing target returns empty list."""
        router = SimpleRouter()
        node_a = Node(id="a", content=make_test_box("A"))

        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
        }

        paths = router._route_merge_edges(
            positions, ["a"], "nonexistent"
        )

        assert paths == []
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestMergeRouting -v --tb=short
# Expected: 5/5 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All existing routing tests still pass
```

**Output**: Merge routing tests passing, existing tests still pass

**Visual Diagram Verification** (Step 4 wrap-up):
```python
def test_step4_visual_merge_routing():
    """Visual verification: merge routing pattern renders correctly.

    Expected pattern (from overview Problem 3):
    ┌─────────────┐          ┌─────────────┐
    │    src-1    │          │    src-2    │
    └──────┬──────┘          └──────┬──────┘
           │                        │
           └──────────┬─────────────┘  ← MERGE
                      │
                      v
               ┌─────────────┐
               │   target    │
               └─────────────┘
    """
    dag = DAG()
    dag.add_node("src1", make_test_box("SOURCE-1", width=15))
    dag.add_node("src2", make_test_box("SOURCE-2", width=15))
    dag.add_node("target", make_test_box("TARGET", width=15))
    dag.add_edge("src1", "target")
    dag.add_edge("src2", "target")

    result = render_dag(dag)
    print("\n=== Step 4: Merge Routing Pattern ===")
    print(result)
    print("=" * 40)

    # Verify structure
    assert "SOURCE-1" in result
    assert "SOURCE-2" in result
    assert "TARGET" in result
    # Edges should converge - look for junction characters
    assert "|" in result  # Has vertical edges
```

---

### Step 4b: Mixed Routing (Independent + Merge from Same Source)

**Goal**: Handle the full Problem 3 scenario where a source has BOTH independent edges AND merge edges

**Problem 3 from Overview**:
```
┌─────────────┐          ┌─────────────┐
│    poc-1    │          │    poc-2    │
└──┬─────┬────┘          └──────┬──────┘
   │     │                      │
   │     └──────────┬───────────┘  ← MERGE (poc-1 + poc-2 → poc-3)
   │                │
   v                v
┌─────────────┐  ┌─────────────┐
│    poc-8    │  │    poc-3    │
└─────────────┘  └─────────────┘
```

**Key requirements**:
- poc-1 has TWO exit points (one independent to poc-8, one merge to poc-3)
- poc-2 has ONE exit point (merge to poc-3)
- Merge edges meet at `┬` junction above poc-3
- Independent edge poc-1→poc-8 routes separately

**Tasks**:
- [ ] Add `_classify_edges()` method to identify independent vs. merge edges per source
- [ ] Add `_allocate_exit_points()` to assign exit points based on edge classification
- [ ] Add `_route_mixed()` to route both independent and merge edges from same source
- [ ] Write tests for mixed routing pattern

**Code** (add to `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Add these methods to the SimpleRouter class:

```python
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
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 4b: MIXED ROUTING TESTS (Independent + Merge from Same Source)
# =============================================================================

class TestMixedRouting:
    """Tests for mixed routing - independent + merge edges from same source.

    This is the full Problem 3 scenario from the overview.
    """

    def test_classify_edges_identifies_merge_vs_independent(self) -> None:
        """Edges to multi-source targets are classified as merge."""
        router = SimpleRouter()

        # poc-1 -> poc-8 (independent), poc-1 -> poc-3 (merge with poc-2)
        edges_by_source = {
            "poc-1": [
                Edge(source="poc-1", target="poc-8"),
                Edge(source="poc-1", target="poc-3"),
            ],
            "poc-2": [
                Edge(source="poc-2", target="poc-3"),
            ],
        }
        edges_by_target = {
            "poc-8": [Edge(source="poc-1", target="poc-8")],
            "poc-3": [
                Edge(source="poc-1", target="poc-3"),
                Edge(source="poc-2", target="poc-3"),
            ],
        }

        classification = router._classify_edges(edges_by_source, edges_by_target)

        # poc-1 should have 1 independent, 1 merge
        assert len(classification["poc-1"]["independent"]) == 1
        assert len(classification["poc-1"]["merge"]) == 1
        assert classification["poc-1"]["independent"][0].target == "poc-8"
        assert classification["poc-1"]["merge"][0].target == "poc-3"

        # poc-2 should have 0 independent, 1 merge
        assert len(classification["poc-2"]["independent"]) == 0
        assert len(classification["poc-2"]["merge"]) == 1

    def test_allocate_exit_points_separates_independent_and_merge(self) -> None:
        """Independent edges get left exits, merge edges get right exits."""
        router = SimpleRouter()
        node = Node(id="poc-1", content=make_test_box("POC-1", width=21))
        pos = NodePosition(node=node, x=0, y=0)

        classification = {
            "independent": [Edge(source="poc-1", target="poc-8")],
            "merge": [Edge(source="poc-1", target="poc-3")],
        }

        allocation = router._allocate_exit_points(pos, classification)

        assert "poc-8" in allocation
        assert "poc-3" in allocation
        # Independent (poc-8) should be left of merge (poc-3)
        assert allocation["poc-8"] < allocation["poc-3"]

    def test_route_mixed_creates_paths_for_both_types(self) -> None:
        """Mixed routing creates paths for both independent and merge edges."""
        router = SimpleRouter()

        node_poc1 = Node(id="poc-1", content=make_test_box("POC-1", width=21))
        node_poc3 = Node(id="poc-3", content=make_test_box("POC-3", width=15))
        node_poc8 = Node(id="poc-8", content=make_test_box("POC-8", width=15))

        positions = {
            "poc-1": NodePosition(node=node_poc1, x=0, y=0),
            "poc-3": NodePosition(node=node_poc3, x=25, y=15),
            "poc-8": NodePosition(node=node_poc8, x=0, y=15),
        }

        classification = {
            "independent": [Edge(source="poc-1", target="poc-8")],
            "merge": [Edge(source="poc-1", target="poc-3")],
        }
        exit_allocation = {"poc-8": 5, "poc-3": 15}

        paths = router._route_mixed(positions, "poc-1", classification, exit_allocation)

        assert len(paths) == 2
        target_ids = {p.target_id for p in paths}
        assert target_ids == {"poc-8", "poc-3"}

    def test_full_problem3_scenario(self) -> None:
        """Full Problem 3: poc-1 has independent (poc-8) and merge (poc-3) edges."""
        router = SimpleRouter()

        # Create the exact Problem 3 scenario
        node_poc1 = Node(id="poc-1", content=make_test_box("poc-1", width=15))
        node_poc2 = Node(id="poc-2", content=make_test_box("poc-2", width=15))
        node_poc3 = Node(id="poc-3", content=make_test_box("poc-3", width=15))
        node_poc8 = Node(id="poc-8", content=make_test_box("poc-8", width=15))

        positions = {
            "poc-1": NodePosition(node=node_poc1, x=0, y=0),
            "poc-2": NodePosition(node=node_poc2, x=25, y=0),
            "poc-3": NodePosition(node=node_poc3, x=25, y=12),
            "poc-8": NodePosition(node=node_poc8, x=0, y=12),
        }

        edges = [
            Edge(source="poc-1", target="poc-8"),  # Independent
            Edge(source="poc-1", target="poc-3"),  # Merge
            Edge(source="poc-2", target="poc-3"),  # Merge
        ]

        # Analyze
        by_source, by_target = router._analyze_edges(positions, edges)
        classification = router._classify_edges(by_source, by_target)

        # Verify classification
        assert len(classification["poc-1"]["independent"]) == 1
        assert len(classification["poc-1"]["merge"]) == 1
        assert len(classification["poc-2"]["merge"]) == 1

        # Route poc-1's mixed edges
        poc1_pos = positions["poc-1"]
        allocation = router._allocate_exit_points(poc1_pos, classification["poc-1"])
        paths = router._route_mixed(positions, "poc-1", classification["poc-1"], allocation)

        assert len(paths) == 2
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestMixedRouting -v --tb=short
# Expected: 4/4 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py -v --tb=short
# Expected: All existing routing tests still pass
```

**Output**: Mixed routing tests passing, existing tests still pass

**Visual Diagram Verification** (Step 4b wrap-up):
```python
def test_step4b_visual_problem3_full():
    """Visual verification: Problem 3 with independent + merge from same source.

    Expected pattern (from overview Problem 3):
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
    """
    dag = DAG()
    dag.add_node("poc-1", make_test_box("poc-1", width=15))
    dag.add_node("poc-2", make_test_box("poc-2", width=15))
    dag.add_node("poc-3", make_test_box("poc-3", width=15))
    dag.add_node("poc-8", make_test_box("poc-8", width=15))

    # poc-1 has TWO edges: independent to poc-8, merge to poc-3
    dag.add_edge("poc-1", "poc-8")  # Independent
    dag.add_edge("poc-1", "poc-3")  # Merge with poc-2
    dag.add_edge("poc-2", "poc-3")  # Merge with poc-1

    result = render_dag(dag)
    print("\n=== Step 4b: Problem 3 - Mixed Routing ===")
    print("poc-1 has independent edge to poc-8 AND merge edge to poc-3")
    print("=" * 50)
    print(result)
    print("=" * 50)

    # Verify all nodes present
    assert "poc-1" in result
    assert "poc-2" in result
    assert "poc-3" in result
    assert "poc-8" in result

    # Verify edges exist
    assert "|" in result, "Expected vertical edge segments"

    # After full integration, should have multiple connectors on poc-1
```

---

### Step 5: Box Connector Placement

**Goal**: Add `┬` connectors on box bottom borders at edge exit points

**Tasks**:
- [ ] Add `place_box_connector()` method to Canvas
- [ ] Add `place_box_connectors()` to process all edges
- [ ] Write tests for connector placement

**Code** (add to `/Users/docchang/Development/visualflow/src/visualflow/render/canvas.py`):

Add these methods to the Canvas class:

```python
    def place_box_connector(self, x: int, y: int) -> None:
        """Place a box connector (┬) at the given position.

        This replaces box border characters (- or +) with ┬
        to visually connect edges to the box.

        Args:
            x: Column position
            y: Row position (should be on box bottom border)
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        existing = self._grid[y][x]
        # Only replace box border characters
        if existing in "-+":
            self._grid[y][x] = "┬"
        # If already a junction or connector, might need to combine
        elif existing == "|":
            self._grid[y][x] = "┬"
        elif existing == "┴":
            # T from below + T from above = cross
            self._grid[y][x] = "┼"

    def place_box_connectors(
        self,
        positions: dict[str, "NodePosition"],
        edges: list["Edge"],
    ) -> None:
        """Place box connectors on all boxes that have outgoing edges.

        For each source box with outgoing edges, places ┬ characters
        on the box bottom border at the edge exit points.

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

        # For each source, place connectors
        for source_id, source_edges in edges_by_source.items():
            source_pos = positions.get(source_id)
            if not source_pos:
                continue

            # Calculate exit points (simplified - center for each edge)
            num_exits = len(source_edges)
            if num_exits == 1:
                # Single exit at center
                exit_x = source_pos.x + source_pos.node.width // 2
                exit_y = source_pos.y + source_pos.node.height - 1  # Bottom border
                self.place_box_connector(exit_x, exit_y)
            else:
                # Multiple exits - space evenly
                box_left = source_pos.x + 1
                box_right = source_pos.x + source_pos.node.width - 2
                usable_width = box_right - box_left
                exit_y = source_pos.y + source_pos.node.height - 1

                if num_exits == 2:
                    spacing = usable_width // 3
                    self.place_box_connector(box_left + spacing, exit_y)
                    self.place_box_connector(box_right - spacing, exit_y)
                else:
                    spacing = usable_width // (num_exits - 1) if num_exits > 1 else 0
                    for i in range(num_exits):
                        exit_x = box_left + spacing * i
                        self.place_box_connector(exit_x, exit_y)
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 5: BOX CONNECTOR PLACEMENT TESTS
# =============================================================================

class TestBoxConnectorPlacement:
    """Tests for box connector placement."""

    def test_single_connector_at_center(self) -> None:
        """Single outgoing edge places connector at box center."""
        canvas = Canvas(width=20, height=10)
        box = "+-------------+\n|      A      |\n+-------------+"
        canvas.place_box(box, x=0, y=0)

        node = Node(id="a", content=box)
        positions = {"a": NodePosition(node=node, x=0, y=0)}
        edges = [Edge(source="a", target="b")]

        canvas.place_box_connectors(positions, edges)

        result = canvas.render()
        assert "┬" in result

    def test_connector_replaces_dash(self) -> None:
        """Connector replaces - character on box border."""
        canvas = Canvas(width=20, height=10)
        box = "+-------------+\n|      A      |\n+-------------+"
        canvas.place_box(box, x=0, y=0)

        node = Node(id="a", content=box)
        positions = {"a": NodePosition(node=node, x=0, y=0)}
        edges = [Edge(source="a", target="b")]

        # Before: has dashes
        result_before = canvas.render()
        assert "-------------" in result_before

        canvas.place_box_connectors(positions, edges)

        # After: has connector
        result_after = canvas.render()
        assert "┬" in result_after

    def test_two_connectors_for_two_edges(self) -> None:
        """Two outgoing edges place two connectors."""
        canvas = Canvas(width=25, height=10)
        box = "+---------------------+\n|          A          |\n+---------------------+"
        canvas.place_box(box, x=0, y=0)

        node = Node(id="a", content=box)
        positions = {"a": NodePosition(node=node, x=0, y=0)}
        edges = [
            Edge(source="a", target="b"),
            Edge(source="a", target="c"),
        ]

        canvas.place_box_connectors(positions, edges)

        result = canvas.render()
        assert result.count("┬") == 2

    def test_no_connector_for_no_edges(self) -> None:
        """No edges means no connectors."""
        canvas = Canvas(width=20, height=10)
        box = "+-------------+\n|      A      |\n+-------------+"
        canvas.place_box(box, x=0, y=0)

        node = Node(id="a", content=box)
        positions = {"a": NodePosition(node=node, x=0, y=0)}
        edges: list[Edge] = []  # No edges

        canvas.place_box_connectors(positions, edges)

        result = canvas.render()
        assert "┬" not in result

    def test_connector_on_target_not_source(self) -> None:
        """Connectors only on source boxes, not targets."""
        canvas = Canvas(width=20, height=15)
        box_a = "+-------+\n|   A   |\n+-------+"
        box_b = "+-------+\n|   B   |\n+-------+"
        canvas.place_box(box_a, x=0, y=0)
        canvas.place_box(box_b, x=0, y=8)

        node_a = Node(id="a", content=box_a)
        node_b = Node(id="b", content=box_b)
        positions = {
            "a": NodePosition(node=node_a, x=0, y=0),
            "b": NodePosition(node=node_b, x=0, y=8),
        }
        edges = [Edge(source="a", target="b")]

        canvas.place_box_connectors(positions, edges)

        result = canvas.render()
        lines = result.split("\n")
        # Connector should be on line 2 (bottom of box A), not line 10 (bottom of box B)
        assert "┬" in lines[2]
        assert "┬" not in lines[10] if len(lines) > 10 else True
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestBoxConnectorPlacement -v --tb=short
# Expected: 5/5 tests pass

cd /Users/docchang/Development/visualflow && uv run pytest tests/test_canvas.py -v --tb=short
# Expected: All existing canvas tests still pass
```

**Output**: Connector tests passing, existing tests still pass

**Visual Diagram Verification** (Step 5 wrap-up):
```python
def test_step5_visual_box_connectors():
    """Visual verification: box connectors appear on box bottom border.

    Expected pattern (from overview Problem 1):
    Before: └───────────┘
    After:  └─────┬─────┘
                  |
    """
    canvas = Canvas(width=20, height=8)
    box = "+-------------+\n|    TEST    |\n+-------------+"
    canvas.place_box(box, x=0, y=0)

    node = Node(id="a", content=box)
    positions = {"a": NodePosition(node=node, x=0, y=0)}
    edges = [Edge(source="a", target="b")]

    canvas.place_box_connectors(positions, edges)

    result = canvas.render()
    print("\n=== Step 5: Box Connector Placement ===")
    print(result)
    print("=" * 40)

    # Verify connector is present
    assert "┬" in result, "Expected ┬ connector on box bottom"

    # Verify it replaced a dash, not corrupted content
    assert "TEST" in result
```

---

### Step 6: Integration - Update render_dag

**Goal**: Integrate connector placement into render_dag pipeline

**Tasks**:
- [ ] Update `render_dag()` to call `place_box_connectors()`
- [ ] Ensure backward compatibility
- [ ] Write integration tests

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/__init__.py`):

Update the render_dag function:

```python
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

    # Place box connectors (before edge drawing)
    if dag.edges:
        canvas.place_box_connectors(layout.positions, dag.edges)

    # Route and draw edges
    if dag.edges:
        if router is None:
            router = SimpleRouter()
        paths = router.route(layout.positions, dag.edges)
        for path in paths:
            canvas.draw_edge(path)

    return canvas.render()
```

**Tests** (add to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 6: INTEGRATION TESTS
# =============================================================================

class TestPoc3Integration:
    """Integration tests for PoC 3 features."""

    def test_render_dag_includes_connectors(self) -> None:
        """render_dag includes box connectors."""
        dag = DAG()
        dag.add_node("a", make_test_box("A", width=15))
        dag.add_node("b", make_test_box("B", width=15))
        dag.add_edge("a", "b")

        result = render_dag(dag)

        assert "┬" in result, "Expected box connector in output"

    def test_render_dag_fan_out_has_connectors(self) -> None:
        """Fan-out diagram has multiple connectors."""
        dag = DAG()
        dag.add_node("root", make_test_box("ROOT", width=21))
        dag.add_node("a", make_test_box("A"))
        dag.add_node("b", make_test_box("B"))
        dag.add_node("c", make_test_box("C"))
        dag.add_edge("root", "a")
        dag.add_edge("root", "b")
        dag.add_edge("root", "c")

        result = render_dag(dag)

        # Should have at least one connector for the root box
        assert "┬" in result

    def test_render_dag_preserves_box_content(self) -> None:
        """Connectors don't corrupt box content."""
        dag = DAG()
        dag.add_node("a", make_test_box("IMPORTANT", width=15))
        dag.add_node("b", make_test_box("DATA", width=15))
        dag.add_edge("a", "b")

        result = render_dag(dag)

        assert "IMPORTANT" in result
        assert "DATA" in result

    def test_render_dag_diamond_pattern(self) -> None:
        """Diamond pattern renders with connectors."""
        dag = DAG()
        dag.add_node("a", make_test_box("A", width=15))
        dag.add_node("b", make_test_box("B", width=15))
        dag.add_node("c", make_test_box("C", width=15))
        dag.add_node("d", make_test_box("D", width=15))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")

        result = render_dag(dag)

        assert "A" in result
        assert "D" in result
        assert "┬" in result

    def test_complex_graph_still_renders(self) -> None:
        """Complex graph pattern still renders correctly."""
        dag = DAG()
        dag.add_node("a", make_test_box("Start", width=15))
        dag.add_node("b", make_test_box("Process 1", width=15))
        dag.add_node("c", make_test_box("Process 2", width=15))
        dag.add_node("d", make_test_box("Merge 1", width=15))
        dag.add_node("e", make_test_box("Merge 2", width=15))
        dag.add_node("f", make_test_box("End", width=15))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "e")
        dag.add_edge("d", "e")
        dag.add_edge("e", "f")

        result = render_dag(dag)

        # All nodes should be present
        assert "Start" in result
        assert "End" in result
        assert "┬" in result  # Should have connectors
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestPoc3Integration -v --tb=short
# Expected: 5/5 tests pass

# Run all affected tests
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_routing.py tests/test_canvas.py tests/test_integration.py -v --tb=short
# Expected: All pass
```

**Output**: Integration tests passing

**Visual Diagram Verification** (Step 6 wrap-up):
```python
def test_step6_visual_full_integration():
    """Visual verification: complete diagram with all PoC 3 features.

    This test creates a diagram that exercises:
    - Problem 1: Box connectors (┬ on box bottom)
    - Problem 2: Fan-out pattern
    - Problem 3: Fan-in/merge pattern
    """
    dag = DAG()

    # Layer 0: Single root
    dag.add_node("root", make_test_box("ROOT", width=17))

    # Layer 1: Fan-out to two children
    dag.add_node("left", make_test_box("LEFT", width=13))
    dag.add_node("right", make_test_box("RIGHT", width=13))
    dag.add_edge("root", "left")
    dag.add_edge("root", "right")

    # Layer 2: Fan-in/merge to single target
    dag.add_node("merge", make_test_box("MERGE", width=15))
    dag.add_edge("left", "merge")
    dag.add_edge("right", "merge")

    result = render_dag(dag)
    print("\n=== Step 6: Full Integration (Diamond with Connectors) ===")
    print(result)
    print("=" * 50)

    # Verify all nodes present
    assert "ROOT" in result
    assert "LEFT" in result
    assert "RIGHT" in result
    assert "MERGE" in result

    # Verify connectors
    assert "┬" in result, "Expected ┬ connectors on box bottoms"

    # Verify edges exist
    assert "|" in result, "Expected vertical edge segments"
```

---

### Step 6b: Smart Routing Integration

**Goal**: Integrate trunk-and-split routing for same-layer targets, ensuring connectors and edge routing are coordinated

**Why Needed**: After Step 6, connectors were placed at multiple exit points but edges still routed from center. This step makes routing "smart" - detecting same-layer targets and using trunk-and-split pattern.

**Tasks**:
- [x] Update `SimpleRouter.route()` to detect same-layer targets
- [x] Use `_route_trunk_split()` for all same-layer targets
- [x] Use multi-exit routing for mixed-layer targets
- [x] Update `Canvas.place_box_connectors()` to match routing logic
- [x] Add `_find_same_layer_targets()` to Canvas for consistency

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/routing/simple.py`):

Update the `route()` method to use smart routing:

```python
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
```

**Code** (update `/Users/docchang/Development/visualflow/src/visualflow/render/canvas.py`):

Update `place_box_connectors()` to match routing logic:

```python
def place_box_connectors(
    self,
    positions: dict[str, "NodePosition"],
    edges: list["Edge"],
) -> None:
    """Place box connectors on all boxes that have outgoing edges.

    Uses the same routing logic as SimpleRouter:
    - Same-layer targets: single connector at center (trunk-and-split)
    - Different-layer targets: multiple connectors (individual routing)
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
```

Also add `_find_same_layer_targets()` method to Canvas (mirrors SimpleRouter logic).

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: All 267 tests pass
```

**Visual Results**:

Same-layer targets now use trunk-and-split (single connector):
```
    +-------+
    | Root  |
    +---┬---+   ← single connector at center
        |       ← shared trunk
   -----┴-----  ← split junction
+---+     +---+
| A |     | B |
```

Mixed-layer targets use multi-exit (multiple connectors):
```
    +-------+
    |   A   |
    +--┬-┬--+   ← two connectors for two edges
       | |      ← separate routing paths
```

**Output**: Smart routing integrated, 267 tests pass

---

### Step 7: Final Verification and Full Test Suite

**Goal**: Verify all tests pass and visual output meets quality bar

**Tasks**:
- [ ] Run full test suite
- [ ] Visual inspection of diagrams
- [ ] Verify no regressions

**Tests** (add visual inspection tests to `/Users/docchang/Development/visualflow/tests/test_poc3_routing.py`):
```python
# =============================================================================
# STEP 7: VISUAL INSPECTION TESTS
# =============================================================================

class TestPoc3VisualInspection:
    """Visual inspection tests - output for manual review."""

    def test_print_simple_with_connector(self) -> None:
        """Print simple chain with connector for visual inspection."""
        dag = DAG()
        dag.add_node("a", make_test_box("Task A", width=17))
        dag.add_node("b", make_test_box("Task B", width=17))
        dag.add_edge("a", "b")

        result = render_dag(dag)
        print("\n" + "=" * 60)
        print("Simple Chain with Box Connector:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_fan_out_with_connectors(self) -> None:
        """Print fan-out with multiple connectors for visual inspection."""
        dag = DAG()
        dag.add_node("root", make_test_box("ROOT", width=21))
        dag.add_node("a", make_test_box("Child A", width=15))
        dag.add_node("b", make_test_box("Child B", width=15))
        dag.add_node("c", make_test_box("Child C", width=15))
        dag.add_edge("root", "a")
        dag.add_edge("root", "b")
        dag.add_edge("root", "c")

        result = render_dag(dag)
        print("\n" + "=" * 60)
        print("Fan-out with Box Connectors:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_diamond_with_connectors(self) -> None:
        """Print diamond pattern for visual inspection."""
        dag = DAG()
        dag.add_node("a", make_test_box("Start", width=15))
        dag.add_node("b", make_test_box("Left", width=15))
        dag.add_node("c", make_test_box("Right", width=15))
        dag.add_node("d", make_test_box("End", width=15))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")

        result = render_dag(dag)
        print("\n" + "=" * 60)
        print("Diamond Pattern with Connectors:")
        print("=" * 60)
        print(result)
        print("=" * 60)


# =============================================================================
# STEP 7: EDGES DON'T CROSS BOXES (from Overview validation tests)
# =============================================================================

class TestEdgesDontCrossBoxes:
    """Verify edges don't route through box content.

    From overview: TestEdgesDontCrossBoxes | All | Diamond preserves box content
    """

    def test_diamond_preserves_all_box_content(self) -> None:
        """Diamond pattern edges don't corrupt any box content."""
        dag = DAG()
        dag.add_node("a", make_test_box("ALPHA", width=13))
        dag.add_node("b", make_test_box("BETA", width=13))
        dag.add_node("c", make_test_box("GAMMA", width=13))
        dag.add_node("d", make_test_box("DELTA", width=13))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")

        result = render_dag(dag)

        # All labels must be intact
        assert "ALPHA" in result, "Box A content corrupted"
        assert "BETA" in result, "Box B content corrupted"
        assert "GAMMA" in result, "Box C content corrupted"
        assert "DELTA" in result, "Box D content corrupted"

    def test_complex_graph_preserves_box_content(self) -> None:
        """Complex graph edges don't corrupt box content."""
        dag = DAG()
        dag.add_node("a", make_test_box("START", width=13))
        dag.add_node("b", make_test_box("PROC-1", width=13))
        dag.add_node("c", make_test_box("PROC-2", width=13))
        dag.add_node("d", make_test_box("MERGE", width=13))
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")
        dag.add_edge("b", "c")  # Cross-edge

        result = render_dag(dag)

        # All labels must be intact
        assert "START" in result
        assert "PROC-1" in result
        assert "PROC-2" in result
        assert "MERGE" in result

    def test_fan_out_preserves_box_borders(self) -> None:
        """Fan-out edges don't break box borders."""
        dag = DAG()
        dag.add_node("root", make_test_box("ROOT", width=21))
        dag.add_node("a", make_test_box("A", width=9))
        dag.add_node("b", make_test_box("B", width=9))
        dag.add_node("c", make_test_box("C", width=9))
        dag.add_edge("root", "a")
        dag.add_edge("root", "b")
        dag.add_edge("root", "c")

        result = render_dag(dag)

        # Check box borders are intact (+ corners still present)
        lines = result.split("\n")
        # At least one line should have box corners
        has_box_structure = any("+" in line for line in lines)
        assert has_box_structure, "Box borders corrupted"
```

**Verification**:
```bash
# Full test suite
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: All tests pass (223 original + ~46 new = ~269 tests)

# Visual inspection
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestPoc3VisualInspection -v -s
# Expected: ASCII diagrams with box connectors

# Edge-box crossing tests
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestEdgesDontCrossBoxes -v
# Expected: All box content preserved
```

**Output**: All tests passing, visual output shows connectors, no box corruption

---

## Test Summary

### New Test Classes (in `tests/test_poc3_routing.py`)

| Class | Tests | Maps to Overview |
|-------|-------|------------------|
| `TestPoc3Baseline` | 2 | Baseline verification |
| `TestEdgeAnalysis` | 5 | Step 1 unit tests |
| `TestExitPointCalculation` | 6 | Step 2 unit tests |
| `TestTrunkAndSplitRouting` | 5 | Step 3 + Problem 2 |
| `TestMergeRouting` | 5 | Step 4 + Problem 3 (Basic) |
| `TestMixedRouting` | 4 | Step 4b + Problem 3 (Full) |
| `TestBoxConnectorPlacement` | 5 | Step 5 + Problem 1 |
| `TestPoc3Integration` | 5 | Step 6 end-to-end |
| `TestPoc3VisualInspection` | 3 | Visual output review |
| `TestEdgesDontCrossBoxes` | 3 | Box content protection |

**Visual Diagram Verification Tests** (one per step):
- `test_step0_visual_baseline` - Baseline diamond renders
- `test_step1_visual_analysis` - Edge analysis output
- `test_step2_visual_exit_points` - Exit point spacing
- `test_step3_visual_trunk_split` - Trunk-split pattern
- `test_step4_visual_merge_routing` - Merge pattern (basic)
- `test_step4b_visual_problem3_full` - Mixed routing (independent + merge)
- `test_step5_visual_box_connectors` - Connector placement
- `test_step6_visual_full_integration` - Complete diamond with connectors

### Affected Tests (Run These)

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `tests/test_poc3_routing.py` | ~51 | New PoC 3 tests (43 unit + 8 visual) |
| `tests/test_routing.py` | ~15 | Existing routing tests |
| `tests/test_canvas.py` | ~25 | Canvas tests including connector |
| `tests/test_integration.py` | ~30 | End-to-end render_dag |
| `tests/test_real_diagrams.py` | ~27 | Real diagram tests |

**Affected tests: ~148 tests**

**Full suite**: 223 existing + ~51 new = ~274 tests

---

## Production-Grade Checklist

Before marking PoC complete, verify:

- [ ] **OOP Design**: Extend existing classes with new methods
- [ ] **Strong Typing**: Type hints on all new functions and methods
- [ ] **No mock data**: All routing uses real position data
- [ ] **Real integrations**: Geometric calculations, not stubs
- [ ] **Error handling**: Missing nodes handled gracefully
- [ ] **Scalable patterns**: Analysis functions work for any graph size
- [ ] **Tests in same step**: Each step writes AND runs its tests
- [ ] **Non-breaking**: All 223 existing tests still pass
- [ ] **Clean separation**: Analysis, routing, rendering in separate methods
- [ ] **Self-contained**: Works independently; connector is optional enhancement

---

## What "Done" Looks Like

```bash
# 1. All tests pass
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: ~274 tests pass (223 existing + ~51 new)

# 2. Visual inspection shows box connectors
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_poc3_routing.py::TestPoc3VisualInspection -v -s
# Expected: ASCII output with boxes connected by | and ┬ on box borders

# 3. Quick demo
cd /Users/docchang/Development/visualflow && uv run python -c "
from visualflow import DAG, render_dag
dag = DAG()
dag.add_node('a', '+-------+\n|   A   |\n+-------+')
dag.add_node('b', '+-------+\n|   B   |\n+-------+')
dag.add_edge('a', 'b')
print(render_dag(dag))
"
# Expected: Box A has ┬ connector, edge connects to box B
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/visualflow/routing/simple.py` | Modify | Add analysis and smart routing methods |
| `src/visualflow/render/canvas.py` | Modify | Add box connector placement |
| `src/visualflow/__init__.py` | Modify | Call connector placement in render_dag |
| `tests/test_poc3_routing.py` | Create | All PoC 3 tests |

---

## Dependencies

No new dependencies required.

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking existing tests | Medium | Run full suite after each step |
| Connector overwrites box content | Low | Only replace `-` and `+` characters |
| Exit point calculation off | Medium | Explicit tests with known positions |
| Merge routing produces ugly output | Medium | Visual inspection tests |
| Narrow boxes can't fit connectors | Low | Clamp to center when too narrow |

---

## Deferred Work

The following items from the overview are deferred to future PoCs:

| Overview Step | Description | Reason Deferred |
|---------------|-------------|-----------------|
| Step 4: Modify `_route_edge()` | Add `exit_x` parameter to accept custom exit point | Current PoC focuses on connector placement; routing methods are standalone |
| Route integration | Integrate `_route_trunk_split()`, `_route_merge_edges()`, `_route_mixed()` into main `route()` method | Requires architectural decision on when to use smart routing vs. basic Z-shape |

These items can be addressed in a follow-up PoC that focuses on "Smart Routing Integration" once the current connector and analysis primitives are validated.

---

## Next Steps After Completion

1. Verify all ~274 tests pass
2. Verify visual inspection shows clean connectors
3. Proceed to next task: PoC 4 (Interface Layer - MC adapter, PyPI release)
