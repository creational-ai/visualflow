# visual-feature-partition-dag Implementation Plan

> **Track Progress**: See `docs/visual-feature-partition-dag-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-20T12:47:40-0800 |
| **Name** | Smart Graph Organization (partition_dag) |
| **Type** | Feature |
| **Proves** | DAGs with mixed connected/standalone nodes render organized: connected subgraphs at top (largest first), standalones at bottom |
| **Production-Grade Because** | Uses real graph traversal algorithms (BFS/DFS), Pydantic models, full type hints, and integrates into existing render_dag() without breaking changes |

---

## Deliverables

Concrete capabilities this feature delivers:

- `partition_dag()` function that separates a DAG into connected subgraphs and standalone nodes
- Updated `render_dag()` that automatically organizes output: connected graphs (largest first), then standalones
- Support for multiple disconnected subgraphs (sorted by size)
- Backward-compatible behavior (existing code continues to work)
- Full test coverage for all scenarios (A through E from design)

---

## Prerequisites

Complete these BEFORE starting implementation steps.

### 1. Identify Affected Tests

**Why Needed**: Run only affected tests during implementation (not full suite)

**Affected test files**:
- `tests/test_models.py` - DAG model tests (ensure no breakage)
- `tests/test_integration.py` - render_dag integration tests (add organized output tests)
- `tests/test_partition.py` - NEW: partition_dag function tests
- `tests/test_new_fixtures.py` - TestStandaloneFixture tests (ensure no breakage)

**Baseline verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_models.py tests/test_integration.py tests/test_engines.py tests/test_new_fixtures.py -v --tb=short
# Expected: All pass (establishes baseline)
```

### 2. Understand Current Disconnected Component Handling

**Why Needed**: Current GrandalfEngine already handles disconnected components via `graph.C` list. The partition_dag function needs to work at the DAG level (before engine) to organize output.

**Current behavior** (from `src/visualflow/engines/grandalf.py`):
- `graph.C` contains connected components after Grandalf graph creation
- Components are laid out side-by-side with `x_offset`
- No distinction between "standalone nodes" (zero edges) and "small connected subgraphs"

**New behavior**:
- `partition_dag()` operates on the DAG model before any engine
- Separates nodes into: connected subgraphs (list[DAG]) and standalones (DAG)
- `render_dag()` uses partition_dag internally to organize output

---

## Success Criteria

From `docs/TODO-future-improvements.md`:

- [ ] `partition_dag(dag)` returns `(list[DAG], DAG)` - connected subgraphs sorted by size, standalones
- [ ] `render_dag()` organizes output: connected graphs at top, standalones at bottom
- [ ] Scenario A works: simple user gets organized diagram automatically
- [ ] Scenario B works: advanced user can access `partition_dag()` for custom rendering
- [ ] Scenario C works: multiple disconnected subgraphs sorted by size (largest first)
- [ ] Scenario D works: all-connected graph returns single subgraph, empty standalones
- [ ] Scenario E works: all-standalone graph returns empty subgraphs list, all in standalones

---

## Architecture

### File Structure
```
src/visualflow/
├── __init__.py           # Updated: add partition_dag export, update render_dag
├── models.py             # Existing (no changes needed)
└── partition.py          # NEW: partition_dag function

tests/
├── test_partition.py     # NEW: tests for partition_dag
└── test_integration.py   # Updated: tests for new render_dag behavior
```

### Design Principles
1. **OOP Design**: `partition_dag` is a pure function, but works with Pydantic DAG models
2. **Pydantic Models**: Uses existing DAG, Node, Edge models (no raw dicts)
3. **Strong Typing**: Full type hints including return type `tuple[list[DAG], DAG]`
4. **Backward Compatible**: Existing code using `render_dag()` gets organized output automatically

### Algorithm Design

**partition_dag algorithm**:
1. Build adjacency set from edges (undirected - source and target both connect)
2. Find nodes with zero edges (standalones)
3. For remaining nodes, use Union-Find or BFS to find connected components
4. Return subgraphs sorted by node count (descending), and standalone DAG

---

## Implementation Steps

**Approach**: Build bottom-up: partition_dag function first, then integrate into render_dag. Tests at each step.

> **Each step includes its tests.** Write code, write tests, run tests, verify all pass - then move on. Never separate code and tests into different steps.

### Step 0: Verify Baseline

**Goal**: Ensure existing tests pass before making changes

**Tasks**:
- [ ] Run affected tests to establish baseline
- [ ] Verify current render_dag behavior with standalone fixture

**Commands**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_models.py tests/test_integration.py -v --tb=short
```

**Verification** (inline OK for Step 0):
```bash
cd /Users/docchang/Development/visualflow && uv run python -c "from visualflow import render_dag; from tests.fixtures import create_standalone; print(render_dag(create_standalone()))"
# Expected: Two boxes rendered (current behavior - may be scattered)
```

**Output**: All baseline tests passing

---

### Step 1: Create partition_dag Function

**Goal**: Implement the core `partition_dag()` function with tests

**Tasks**:
- [ ] Create `src/visualflow/partition.py` with `partition_dag` function
- [ ] Implement algorithm to find connected components and standalones
- [ ] Write comprehensive tests for all scenarios

**Code** (create `src/visualflow/partition.py`):
```python
"""Graph partitioning utilities for DAG organization.

Separates a DAG into connected subgraphs and standalone nodes.
"""

from collections import defaultdict

from visualflow.models import DAG, Edge


def partition_dag(dag: DAG) -> tuple[list[DAG], DAG]:
    """Partition a DAG into connected subgraphs and standalone nodes.

    Uses Union-Find algorithm to efficiently find connected components.
    A node is "standalone" if it has no edges (neither source nor target).

    Args:
        dag: The directed acyclic graph to partition

    Returns:
        Tuple of:
        - list[DAG]: Connected subgraphs, sorted by size (largest first)
        - DAG: All standalone nodes (nodes with no edges)

    Examples:
        >>> dag = DAG()
        >>> dag.add_node("a", "A")  # standalone
        >>> dag.add_node("b", "B")
        >>> dag.add_node("c", "C")
        >>> dag.add_edge("b", "c")  # connected
        >>> connected, standalones = partition_dag(dag)
        >>> len(connected)  # 1 subgraph with b->c
        1
        >>> len(standalones.nodes)  # 1 standalone node (a)
        1
    """
    if not dag.nodes:
        return [], DAG()

    # Build set of nodes that participate in edges
    nodes_with_edges: set[str] = set()
    for edge in dag.edges:
        nodes_with_edges.add(edge.source)
        nodes_with_edges.add(edge.target)

    # Identify standalone nodes (no edges)
    standalone_ids = set(dag.nodes.keys()) - nodes_with_edges

    # If no edges exist, all nodes are standalone
    if not dag.edges:
        standalones = DAG()
        for node_id in dag.nodes:
            node = dag.nodes[node_id]
            standalones.add_node(node_id, node.content)
        return [], standalones

    # Build adjacency list (undirected) for connected component detection
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in dag.edges:
        adjacency[edge.source].add(edge.target)
        adjacency[edge.target].add(edge.source)

    # Find connected components using BFS
    visited: set[str] = set()
    components: list[set[str]] = []

    for node_id in nodes_with_edges:
        if node_id in visited:
            continue

        # BFS from this node
        component: set[str] = set()
        queue = [node_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

        if component:
            components.append(component)

    # Sort components by size (largest first)
    components.sort(key=lambda c: len(c), reverse=True)

    # Build DAGs for each connected component
    subgraphs: list[DAG] = []
    for component in components:
        subgraph = DAG()
        for node_id in component:
            node = dag.nodes[node_id]
            subgraph.add_node(node_id, node.content)
        for edge in dag.edges:
            if edge.source in component and edge.target in component:
                subgraph.add_edge(edge.source, edge.target)
        subgraphs.append(subgraph)

    # Build DAG for standalone nodes
    standalones = DAG()
    for node_id in standalone_ids:
        node = dag.nodes[node_id]
        standalones.add_node(node_id, node.content)

    return subgraphs, standalones
```

**Tests** (create `tests/test_partition.py`):
```python
"""Tests for partition_dag function."""

import pytest

from visualflow.models import DAG
from visualflow.partition import partition_dag


class TestPartitionDagEmpty:
    """Tests for partition_dag with empty or minimal DAGs."""

    def test_empty_dag(self) -> None:
        """Empty DAG returns empty subgraphs and empty standalones."""
        dag = DAG()
        connected, standalones = partition_dag(dag)
        assert connected == []
        assert len(standalones.nodes) == 0

    def test_single_standalone_node(self) -> None:
        """Single node with no edges is standalone."""
        dag = DAG()
        dag.add_node("a", "Node A")
        connected, standalones = partition_dag(dag)
        assert connected == []
        assert len(standalones.nodes) == 1
        assert "a" in standalones.nodes


class TestPartitionDagAllConnected:
    """Tests for DAGs where all nodes are connected (Scenario D)."""

    def test_simple_chain_all_connected(self) -> None:
        """A -> B -> C: all connected, no standalones."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 3
        assert len(standalones.nodes) == 0

    def test_diamond_all_connected(self) -> None:
        """Diamond pattern: A -> B, A -> C, B -> D, C -> D."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_node("d", "D")
        dag.add_edge("a", "b")
        dag.add_edge("a", "c")
        dag.add_edge("b", "d")
        dag.add_edge("c", "d")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 4
        assert len(standalones.nodes) == 0


class TestPartitionDagAllStandalone:
    """Tests for DAGs where all nodes are standalone (Scenario E)."""

    def test_multiple_standalones_no_edges(self) -> None:
        """Multiple nodes with no edges: all standalone."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_node("d", "D")
        dag.add_node("e", "E")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 0
        assert len(standalones.nodes) == 5


class TestPartitionDagMixed:
    """Tests for DAGs with mixed connected and standalone nodes (Scenario A/B)."""

    def test_one_connected_pair_one_standalone(self) -> None:
        """A -> B connected, C standalone."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 2
        assert "a" in connected[0].nodes
        assert "b" in connected[0].nodes
        assert len(standalones.nodes) == 1
        assert "c" in standalones.nodes

    def test_mixed_seven_connected_three_standalone(self) -> None:
        """7 connected nodes, 3 standalone - per TODO example."""
        dag = DAG()
        # Connected graph: A -> B -> C -> D -> E, B -> F, C -> G
        for node_id in ["a", "b", "c", "d", "e", "f", "g"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")
        dag.add_edge("b", "f")
        dag.add_edge("c", "g")

        # Standalone nodes
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_node("z", "Z")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        assert len(connected[0].nodes) == 7
        assert len(standalones.nodes) == 3


class TestPartitionDagMultipleSubgraphs:
    """Tests for DAGs with multiple disconnected subgraphs (Scenario C)."""

    def test_two_disconnected_subgraphs(self) -> None:
        """A->B->C (3 nodes) and X->Y (2 nodes) - sorted by size."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        # Largest first
        assert len(connected[0].nodes) == 3
        assert len(connected[1].nodes) == 2
        assert len(standalones.nodes) == 0

    def test_multiple_subgraphs_with_standalones(self) -> None:
        """A->B->C->D->E (5) + X->Y (2) + P, Q, R (3 standalone)."""
        dag = DAG()
        # Large subgraph
        for node_id in ["a", "b", "c", "d", "e"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")

        # Small subgraph
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        # Standalones
        dag.add_node("p", "P")
        dag.add_node("q", "Q")
        dag.add_node("r", "R")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        assert len(connected[0].nodes) == 5  # Largest first
        assert len(connected[1].nodes) == 2
        assert len(standalones.nodes) == 3

    def test_subgraphs_sorted_by_size_descending(self) -> None:
        """Subgraphs should be sorted largest to smallest."""
        dag = DAG()
        # Small subgraph (added first)
        dag.add_node("x", "X")
        dag.add_node("y", "Y")
        dag.add_edge("x", "y")

        # Large subgraph (added second)
        for node_id in ["a", "b", "c", "d", "e"]:
            dag.add_node(node_id, node_id.upper())
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("c", "d")
        dag.add_edge("d", "e")

        connected, standalones = partition_dag(dag)
        assert len(connected) == 2
        # Should still be largest first regardless of insertion order
        assert len(connected[0].nodes) == 5
        assert len(connected[1].nodes) == 2


class TestPartitionDagEdgePreservation:
    """Tests that edges are correctly preserved in subgraphs."""

    def test_edges_preserved_in_subgraph(self) -> None:
        """Subgraph should contain all relevant edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        dag.add_edge("a", "c")  # Skip-level edge

        connected, standalones = partition_dag(dag)
        assert len(connected) == 1
        subgraph = connected[0]
        assert len(subgraph.edges) == 3
        edge_pairs = {(e.source, e.target) for e in subgraph.edges}
        assert ("a", "b") in edge_pairs
        assert ("b", "c") in edge_pairs
        assert ("a", "c") in edge_pairs

    def test_standalones_have_no_edges(self) -> None:
        """Standalone DAG should have no edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_edge("a", "b")
        dag.add_node("c", "C")  # standalone

        connected, standalones = partition_dag(dag)
        assert len(standalones.edges) == 0
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_partition.py -v
```

**Output**: All partition_dag tests passing

---

### Step 2: Export partition_dag and Integrate Imports

**Goal**: Export `partition_dag` in `__init__.py` and prepare for render_dag integration

**Tasks**:
- [ ] Add import and export for `partition_dag` in `__init__.py`
- [ ] Add `partition_dag` to `__all__`
- [ ] Write import test

**Code** (update `src/visualflow/__init__.py`):

Add import at top (after existing imports):
```python
from visualflow.partition import partition_dag
```

Add to `__all__` list:
```python
    "partition_dag",
```

**Tests** (add to `tests/test_partition.py`):
```python
class TestPartitionDagExport:
    """Tests for partition_dag export from visualflow package."""

    def test_partition_dag_importable_from_package(self) -> None:
        """partition_dag can be imported from visualflow."""
        from visualflow import partition_dag
        assert callable(partition_dag)

    def test_partition_dag_in_all(self) -> None:
        """partition_dag is in __all__."""
        import visualflow
        assert "partition_dag" in visualflow.__all__
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_partition.py::TestPartitionDagExport -v
```

**Output**: Export tests passing

---

### Step 3: Update render_dag for Smart Organization

**Goal**: Update `render_dag()` to use `partition_dag()` internally for organized output

**Tasks**:
- [ ] Modify `render_dag()` to partition the DAG first
- [ ] Render connected subgraphs (largest first), then standalones
- [ ] Combine outputs vertically with proper spacing
- [ ] Write integration tests for new behavior

**Code** (update `src/visualflow/__init__.py` - replace `render_dag` function):
```python
def render_dag(
    dag: DAG,
    engine: LayoutEngine | None = None,
    router: EdgeRouter | None = None,
    theme: EdgeTheme | None = None,
) -> str:
    """Render a DAG to ASCII string.

    Automatically organizes output:
    - Connected subgraphs at top (largest first)
    - Standalone nodes grouped at bottom

    Args:
        dag: The directed acyclic graph to render
        engine: Layout engine to use (defaults to GrandalfEngine)
        router: Edge router to use (defaults to SimpleRouter if edges exist)
        theme: Edge theme for line/arrow characters (defaults to ASCII theme)

    Returns:
        Multi-line ASCII string representation
    """
    if engine is None:
        engine = GrandalfEngine()
    if theme is None:
        theme = settings.theme

    # Partition DAG into connected subgraphs and standalones
    subgraphs, standalones = partition_dag(dag)

    rendered_parts: list[str] = []

    # Render connected subgraphs (largest first)
    for subgraph in subgraphs:
        rendered = _render_single_dag(subgraph, engine, router, theme)
        if rendered:
            rendered_parts.append(rendered)

    # Render standalones (if any)
    if standalones.nodes:
        rendered = _render_single_dag(standalones, engine, router, theme)
        if rendered:
            rendered_parts.append(rendered)

    # Join with blank line separator
    return "\n".join(rendered_parts)


def _render_single_dag(
    dag: DAG,
    engine: LayoutEngine,
    router: EdgeRouter | None,
    theme: EdgeTheme,
) -> str:
    """Render a single DAG (internal helper).

    Args:
        dag: The DAG to render
        engine: Layout engine to use
        router: Edge router to use
        theme: Edge theme for characters

    Returns:
        Multi-line ASCII string representation
    """
    # Compute layout
    layout = engine.compute(dag)

    if not layout.positions:
        return ""

    # Create canvas with theme
    canvas = Canvas(width=layout.width, height=layout.height, theme=theme)

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

        # Fix junction characters based on actual neighbors
        canvas.fix_junctions()

    return canvas.render()
```

**Tests** (add new test class to `tests/test_integration.py` - do not replace existing tests):
```python
class TestRenderDagOrganization:
    """Tests for render_dag smart organization behavior."""

    def test_mixed_dag_standalones_after_connected(self) -> None:
        """Standalones should appear after connected nodes in output."""
        from visualflow import render_dag
        from visualflow.models import DAG

        dag = DAG()
        # Connected pair
        dag.add_node("a", "+---+\n| A |\n+---+")
        dag.add_node("b", "+---+\n| B |\n+---+")
        dag.add_edge("a", "b")
        # Standalone
        dag.add_node("x", "+---+\n| X |\n+---+")

        result = render_dag(dag)

        # Both should be present
        assert "A" in result
        assert "B" in result
        assert "X" in result

        # Find positions in output
        a_pos = result.find("A")
        b_pos = result.find("B")
        x_pos = result.find("X")

        # X (standalone) should appear after connected nodes
        # Since output is line-by-line, standalone section is at bottom
        assert x_pos > a_pos or x_pos > b_pos

    def test_multiple_subgraphs_largest_first(self) -> None:
        """Larger subgraphs should appear before smaller ones."""
        from visualflow import render_dag
        from visualflow.models import DAG

        dag = DAG()
        # Small subgraph (2 nodes)
        dag.add_node("x", "+---+\n| X |\n+---+")
        dag.add_node("y", "+---+\n| Y |\n+---+")
        dag.add_edge("x", "y")

        # Large subgraph (3 nodes)
        dag.add_node("a", "+---+\n| A |\n+---+")
        dag.add_node("b", "+---+\n| B |\n+---+")
        dag.add_node("c", "+---+\n| C |\n+---+")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        result = render_dag(dag)

        # Large subgraph (A-B-C) should appear before small (X-Y)
        a_pos = result.find("A")
        x_pos = result.find("X")
        assert a_pos < x_pos, "Larger subgraph should render first"

    def test_all_connected_single_output(self) -> None:
        """All-connected DAG should render as single block."""
        from visualflow import render_dag
        from tests.fixtures import create_simple_chain

        dag = create_simple_chain()
        result = render_dag(dag)

        # Should have all nodes
        assert "Task A" in result
        assert "Task B" in result
        assert "Task C" in result

    def test_all_standalones_grouped(self) -> None:
        """All-standalone DAG should render all nodes."""
        from visualflow import render_dag
        from visualflow.models import DAG

        dag = DAG()
        dag.add_node("a", "+---+\n| A |\n+---+")
        dag.add_node("b", "+---+\n| B |\n+---+")
        dag.add_node("c", "+---+\n| C |\n+---+")

        result = render_dag(dag)
        assert "A" in result
        assert "B" in result
        assert "C" in result

    def test_existing_fixtures_still_work(self) -> None:
        """All existing fixtures should still render correctly."""
        from visualflow import render_dag
        from tests.fixtures import (
            create_simple_chain,
            create_diamond,
            create_wide_fanout,
            create_merge_branch,
            create_skip_level,
            create_standalone,
            create_complex_graph,
        )

        fixtures = [
            ("simple_chain", create_simple_chain()),
            ("diamond", create_diamond()),
            ("wide_fanout", create_wide_fanout()),
            ("merge_branch", create_merge_branch()),
            ("skip_level", create_skip_level()),
            ("standalone", create_standalone()),
            ("complex_graph", create_complex_graph()),
        ]

        for name, dag in fixtures:
            result = render_dag(dag)
            assert result, f"{name} should produce output"
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_integration.py::TestRenderDagOrganization -v
```

**Output**: Organization tests passing

---

### Step 4: Full Integration and Regression Testing

**Goal**: Verify all tests pass and no regressions

**Tasks**:
- [ ] Run all affected tests
- [ ] Run full test suite
- [ ] Verify visual output with print tests

**Verification**:
```bash
# Run affected tests
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_partition.py tests/test_integration.py tests/test_models.py -v --tb=short

# Run full suite
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
```

**Output**: All tests passing

---

## Test Summary

### Affected Tests (Run These)

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `tests/test_partition.py` | ~20 | partition_dag function - all scenarios |
| `tests/test_integration.py` | ~30 | render_dag integration including new organization |
| `tests/test_models.py` | ~20 | DAG model basics (ensure no breakage) |

**Affected tests: ~70 tests**

**Full suite**: ~275 tests (run at end to verify no regressions)

---

## Production-Grade Checklist

Before marking feature complete, verify:

- [ ] **OOP Design**: Uses existing Pydantic models (DAG, Node, Edge)
- [ ] **Pydantic Models**: partition_dag works with Pydantic DAG model
- [ ] **Strong Typing**: Full type hints including `tuple[list[DAG], DAG]` return
- [ ] **No mock data**: Uses real DAG structures in tests
- [ ] **Real integrations**: Works with actual GrandalfEngine layout
- [ ] **Error handling**: Empty DAG handled gracefully
- [ ] **Scalable patterns**: BFS algorithm is O(V+E), works for any DAG size
- [ ] **Tests in same step**: Each step writes AND runs its tests
- [ ] **Config externalized**: No hardcoded values
- [ ] **Clean separation**: partition.py has single responsibility
- [ ] **Self-contained**: Works independently; backward compatible

---

## What "Done" Looks Like

```bash
# 1. Affected tests pass
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_partition.py tests/test_integration.py -v --tb=short
# Expected: All pass

# 2. Full suite passes
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: All pass (~275 tests)

# 3. partition_dag works as documented
python -c "
from visualflow import partition_dag
from visualflow.models import DAG

dag = DAG()
dag.add_node('a', 'A')
dag.add_node('b', 'B')
dag.add_node('c', 'C')
dag.add_edge('a', 'b')

connected, standalones = partition_dag(dag)
print(f'Connected subgraphs: {len(connected)}')
print(f'  - First subgraph nodes: {len(connected[0].nodes)}')
print(f'Standalone nodes: {len(standalones.nodes)}')
"
# Expected:
# Connected subgraphs: 1
#   - First subgraph nodes: 2
# Standalone nodes: 1

# 4. render_dag produces organized output
python -c "
from visualflow import render_dag
from visualflow.models import DAG

dag = DAG()
dag.add_node('a', '+-----+\n|  A  |\n+-----+')
dag.add_node('b', '+-----+\n|  B  |\n+-----+')
dag.add_node('c', '+-----+\n|  C  |\n+-----+')
dag.add_edge('a', 'b')
# c is standalone

print(render_dag(dag))
"
# Expected: A->B connected graph at top, C standalone at bottom
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `src/visualflow/partition.py` | Create | partition_dag function |
| `src/visualflow/__init__.py` | Modify | Add import/export, update render_dag |
| `tests/test_partition.py` | Create | Tests for partition_dag |
| `tests/test_integration.py` | Modify | Add render_dag organization tests |

---

## Dependencies

No new dependencies required. Uses existing:
- `pydantic` - DAG model
- `grandalf` - Layout engine (via GrandalfEngine)

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Breaking existing render_dag behavior | Low | Refactored to use internal helper; same output for connected DAGs |
| Performance with large DAGs | Low | BFS is O(V+E); tested with complex_graph fixture |
| Edge cases with empty DAGs | Low | Explicit empty handling in partition_dag |

---

## Next Steps After Completion

1. Verify all tests pass (~275 tests)
2. Verify partition_dag works with all scenarios (A-E)
3. Verify render_dag produces organized output
4. Update README with usage example (if requested)
5. Proceed to next feature or task
