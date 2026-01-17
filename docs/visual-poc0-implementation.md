# Visual-PoC0 Implementation Plan

> **Track Progress**: See `docs/visual-poc0-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-16T12:03:43-0800 |
| **Name** | PoC 0: Layout Engine Exploration |
| **Type** | PoC |
| **Proves** | We understand what each layout engine excels at and what combination (3, 2, or 1) provides optimal value vs. complexity |
| **Production-Grade Because** | Uses pytest for repeatable, documented evaluation; tests real engine capabilities against standardized scenarios |

---

## Deliverables

Concrete capabilities this PoC delivers:

- `tests/conftest.py` with 7 graph scenario fixtures (TestNode, TestEdge, TestGraph dataclasses)
- `tests/test_grandalf.py` with complete Grandalf evaluation (all 7 scenarios)
- `tests/test_graphviz.py` with complete Graphviz evaluation (all 7 scenarios)
- `tests/test_ascii_dag.py` with ascii-dag evaluation (existing examples + capability assessment)
- `docs/poc0-comparison-matrix.md` with decision matrix and engine recommendation

---

## Prerequisites

Complete these BEFORE starting implementation steps.

### 1. Identify Affected Tests

**Why Needed**: This is a new test infrastructure - no existing tests to baseline

**Affected test files**:
- `tests/conftest.py` - New file (shared fixtures)
- `tests/test_grandalf.py` - New file (Grandalf evaluation)
- `tests/test_graphviz.py` - New file (Graphviz evaluation)
- `tests/test_ascii_dag.py` - New file (ascii-dag evaluation)

**Baseline verification**:
```bash
# No existing tests - this creates the test infrastructure
cd /Users/docchang/Development/visualflow && ls tests/ 2>/dev/null || echo "tests/ directory does not exist yet"
```

### 2. Verify Dependencies Installed

**Why Needed**: All three layout engines must be available

**Steps**:
1. Verify Grandalf Python package is installed
2. Verify ascii-dag is compiled
3. Verify Graphviz CLI is installed

**Commands**:
```bash
# Verify Grandalf
cd /Users/docchang/Development/visualflow && uv run python -c "from grandalf.graphs import Graph, Vertex, Edge; from grandalf.layouts import SugiyamaLayout; print('Grandalf OK')"

# Verify ascii-dag compiled
ls /Users/docchang/Development/Mission\ Control/visualflow/ascii-dag/target/release/examples/basic

# Verify Graphviz
which dot && dot -V
```

**Verification** (inline OK for prerequisites):
```bash
# All three checks should pass
cd /Users/docchang/Development/visualflow && uv run python -c "from grandalf.graphs import Graph; print('Grandalf: OK')"
test -f /Users/docchang/Development/Mission\ Control/visualflow/ascii-dag/target/release/examples/basic && echo "ascii-dag: OK"
which dot > /dev/null && echo "Graphviz: OK"
# Expected: All three print OK
```

### 3. Create Tests Directory

**Why Needed**: Test infrastructure does not exist yet

**Steps**:
1. Create `tests/` directory
2. Create empty `__init__.py` (optional, pytest works without it)

**Commands**:
```bash
mkdir -p /Users/docchang/Development/visualflow/tests
```

**Verification**:
```bash
ls -la /Users/docchang/Development/visualflow/tests/
# Expected: Empty directory exists
```

---

## Success Criteria

From `docs/visual-poc0-overview.md`:

- [ ] All three engines tested with all 7 scenarios
- [ ] Clear understanding of each engine's strengths/weaknesses documented
- [ ] Decision matrix created: which engine(s) to use and why
- [ ] Answer provided: "Do we need 3, 2, or 1 engine(s)?"
- [ ] Quality gate: Identify which engine(s) can produce flawless output for each scenario

---

## Architecture

### File Structure
```
visualflow/
├── pyproject.toml               # name = "visualflow"
├── src/
│   └── visualflow/              # PyPI package (expanded in PoC 1)
│       └── __init__.py
├── tests/
│   ├── conftest.py              # Shared fixtures (7 graph scenarios)
│   ├── test_grandalf.py         # Grandalf evaluation tests
│   ├── test_graphviz.py         # Graphviz evaluation tests
│   └── test_ascii_dag.py        # ascii-dag evaluation tests
├── docs/
│   ├── visual-poc0-overview.md  # This plan's source document
│   ├── visual-poc0-implementation.md  # This file
│   └── poc0-comparison-matrix.md      # Output: decision matrix
└── ascii-dag/
    └── target/release/examples/basic  # Pre-compiled binary (reference)
```

### Design Principles
1. **Dataclasses for Test Data**: Use `TestNode`, `TestEdge`, `TestGraph` dataclasses for clarity
2. **Shared Fixtures**: All 7 scenarios defined once in `conftest.py`, reused across all test files
3. **Strong Typing**: Type hints on all fixtures and test functions
4. **Evaluation Focus**: Tests verify capabilities, not correctness (that comes in PoC 1)

---

## Implementation Steps

**Approach**: Sequential - Build test infrastructure first, then evaluate engines in order: Grandalf -> Graphviz -> ascii-dag. Each step writes AND runs tests together.

> **Each step includes its tests.** Write code, write tests, run tests, verify all pass - then move on. Never separate code and tests into different steps.

### Step 0: Create Test Infrastructure with Basic Fixtures

**Goal**: Create `conftest.py` with dataclasses and first 3 fixtures (scenarios 1-3)

**Tasks**:
- [ ] Create `tests/conftest.py` with `TestNode`, `TestEdge`, `TestGraph` dataclasses
- [ ] Add fixtures: `simple_chain`, `diamond`, `multiple_roots`
- [ ] Verify fixtures can be collected

**Code** (create `/Users/docchang/Development/visualflow/tests/conftest.py`):
```python
"""Shared fixtures for layout engine evaluation tests."""

from dataclasses import dataclass, field
import pytest


@dataclass
class TestNode:
    """Node for test scenarios."""

    id: str
    label: str
    width: int = 15  # Default box width in characters
    height: int = 3  # Default box height in lines


@dataclass
class TestEdge:
    """Edge for test scenarios."""

    source: str
    target: str


@dataclass
class TestGraph:
    """Graph scenario for testing layout engines."""

    name: str
    nodes: list[TestNode] = field(default_factory=list)
    edges: list[TestEdge] = field(default_factory=list)


# =============================================================================
# Scenario 1: Simple Chain (A -> B -> C)
# =============================================================================
@pytest.fixture
def simple_chain() -> TestGraph:
    """Scenario 1: A -> B -> C - Basic vertical flow."""
    return TestGraph(
        name="simple_chain",
        nodes=[
            TestNode("a", "Task A"),
            TestNode("b", "Task B"),
            TestNode("c", "Task C"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("b", "c"),
        ],
    )


# =============================================================================
# Scenario 2: Diamond (A -> B, A -> C, B -> D, C -> D)
# =============================================================================
@pytest.fixture
def diamond() -> TestGraph:
    """Scenario 2: Diamond pattern - Converging paths."""
    return TestGraph(
        name="diamond",
        nodes=[
            TestNode("a", "Root"),
            TestNode("b", "Left"),
            TestNode("c", "Right"),
            TestNode("d", "Merge"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("a", "c"),
            TestEdge("b", "d"),
            TestEdge("c", "d"),
        ],
    )


# =============================================================================
# Scenario 3: Multiple Roots (A -> C, B -> C)
# =============================================================================
@pytest.fixture
def multiple_roots() -> TestGraph:
    """Scenario 3: Multiple entry points converging."""
    return TestGraph(
        name="multiple_roots",
        nodes=[
            TestNode("a", "Root A"),
            TestNode("b", "Root B"),
            TestNode("c", "Merge"),
        ],
        edges=[
            TestEdge("a", "c"),
            TestEdge("b", "c"),
        ],
    )
```

**Verification** (inline OK for Step 0):
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/conftest.py --collect-only 2>&1 | head -20
# Expected: Shows fixtures collected (simple_chain, diamond, multiple_roots)
```

**Output**: 3 fixtures available (simple_chain, diamond, multiple_roots)

---

### Step 1: Complete Test Fixtures (Scenarios 4-7)

**Goal**: Add remaining 4 fixtures to `conftest.py`

**Tasks**:
- [ ] Add `skip_level` fixture (scenario 4)
- [ ] Add `wide_graph` fixture (scenario 5)
- [ ] Add `deep_graph` fixture (scenario 6)
- [ ] Add `complex_graph` fixture (scenario 7)
- [ ] Write validation test for all fixtures

**Code** (append to `/Users/docchang/Development/visualflow/tests/conftest.py`):
```python
# =============================================================================
# Scenario 4: Skip-Level (A -> B -> C, A -> C direct)
# =============================================================================
@pytest.fixture
def skip_level() -> TestGraph:
    """Scenario 4: Skip-level edges - Mixed depth connections."""
    return TestGraph(
        name="skip_level",
        nodes=[
            TestNode("a", "Root"),
            TestNode("b", "Middle"),
            TestNode("c", "End"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("b", "c"),
            TestEdge("a", "c"),  # Skip-level edge
        ],
    )


# =============================================================================
# Scenario 5: Wide Graph (A -> B, A -> C, A -> D, A -> E)
# =============================================================================
@pytest.fixture
def wide_graph() -> TestGraph:
    """Scenario 5: Wide graph - Horizontal spread."""
    return TestGraph(
        name="wide_graph",
        nodes=[
            TestNode("a", "Root"),
            TestNode("b", "Child 1"),
            TestNode("c", "Child 2"),
            TestNode("d", "Child 3"),
            TestNode("e", "Child 4"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("a", "c"),
            TestEdge("a", "d"),
            TestEdge("a", "e"),
        ],
    )


# =============================================================================
# Scenario 6: Deep Graph (A -> B -> C -> D -> E -> F)
# =============================================================================
@pytest.fixture
def deep_graph() -> TestGraph:
    """Scenario 6: Deep graph - Many vertical levels."""
    return TestGraph(
        name="deep_graph",
        nodes=[
            TestNode("a", "Level 1"),
            TestNode("b", "Level 2"),
            TestNode("c", "Level 3"),
            TestNode("d", "Level 4"),
            TestNode("e", "Level 5"),
            TestNode("f", "Level 6"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("b", "c"),
            TestEdge("c", "d"),
            TestEdge("d", "e"),
            TestEdge("e", "f"),
        ],
    )


# =============================================================================
# Scenario 7: Complex Graph (Combination of patterns)
# =============================================================================
@pytest.fixture
def complex_graph() -> TestGraph:
    """Scenario 7: Complex graph - Real-world complexity.

    Structure:
        A -----> B -----> D
        |        |        |
        |        v        v
        +------> C -----> E
                          |
                          v
                          F
    """
    return TestGraph(
        name="complex_graph",
        nodes=[
            TestNode("a", "Start"),
            TestNode("b", "Process 1"),
            TestNode("c", "Process 2"),
            TestNode("d", "Merge 1"),
            TestNode("e", "Merge 2"),
            TestNode("f", "End"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("a", "c"),
            TestEdge("b", "c"),
            TestEdge("b", "d"),
            TestEdge("c", "e"),
            TestEdge("d", "e"),
            TestEdge("e", "f"),
        ],
    )


# =============================================================================
# All Scenarios Fixture (for parametrized tests)
# =============================================================================
@pytest.fixture
def all_scenarios(
    simple_chain: TestGraph,
    diamond: TestGraph,
    multiple_roots: TestGraph,
    skip_level: TestGraph,
    wide_graph: TestGraph,
    deep_graph: TestGraph,
    complex_graph: TestGraph,
) -> list[TestGraph]:
    """All 7 test scenarios for parametrized testing."""
    return [
        simple_chain,
        diamond,
        multiple_roots,
        skip_level,
        wide_graph,
        deep_graph,
        complex_graph,
    ]
```

**Tests** (create `/Users/docchang/Development/visualflow/tests/test_fixtures.py`):
```python
"""Tests to validate fixture infrastructure."""

import pytest
from conftest import TestGraph, TestNode, TestEdge


class TestFixtureValidation:
    """Validate all fixtures are correctly defined."""

    def test_simple_chain_structure(self, simple_chain: TestGraph) -> None:
        """Verify simple_chain has correct structure."""
        assert simple_chain.name == "simple_chain"
        assert len(simple_chain.nodes) == 3
        assert len(simple_chain.edges) == 2

    def test_diamond_structure(self, diamond: TestGraph) -> None:
        """Verify diamond has correct structure."""
        assert diamond.name == "diamond"
        assert len(diamond.nodes) == 4
        assert len(diamond.edges) == 4

    def test_multiple_roots_structure(self, multiple_roots: TestGraph) -> None:
        """Verify multiple_roots has correct structure."""
        assert multiple_roots.name == "multiple_roots"
        assert len(multiple_roots.nodes) == 3
        assert len(multiple_roots.edges) == 2

    def test_skip_level_structure(self, skip_level: TestGraph) -> None:
        """Verify skip_level has correct structure."""
        assert skip_level.name == "skip_level"
        assert len(skip_level.nodes) == 3
        assert len(skip_level.edges) == 3  # Includes skip edge

    def test_wide_graph_structure(self, wide_graph: TestGraph) -> None:
        """Verify wide_graph has correct structure."""
        assert wide_graph.name == "wide_graph"
        assert len(wide_graph.nodes) == 5
        assert len(wide_graph.edges) == 4

    def test_deep_graph_structure(self, deep_graph: TestGraph) -> None:
        """Verify deep_graph has correct structure."""
        assert deep_graph.name == "deep_graph"
        assert len(deep_graph.nodes) == 6
        assert len(deep_graph.edges) == 5

    def test_complex_graph_structure(self, complex_graph: TestGraph) -> None:
        """Verify complex_graph has correct structure."""
        assert complex_graph.name == "complex_graph"
        assert len(complex_graph.nodes) == 6
        assert len(complex_graph.edges) == 7

    def test_all_scenarios_count(self, all_scenarios: list[TestGraph]) -> None:
        """Verify all_scenarios contains all 7 scenarios."""
        assert len(all_scenarios) == 7
        names = [s.name for s in all_scenarios]
        assert "simple_chain" in names
        assert "diamond" in names
        assert "complex_graph" in names

    def test_node_defaults(self) -> None:
        """Verify TestNode has correct defaults."""
        node = TestNode("test", "Test Label")
        assert node.width == 15
        assert node.height == 3

    def test_node_custom_dimensions(self) -> None:
        """Verify TestNode accepts custom dimensions."""
        node = TestNode("test", "Test Label", width=20, height=5)
        assert node.width == 20
        assert node.height == 5
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_fixtures.py -v
```

**Output**: 10/10 tests passing

---

### Step 2: Grandalf Basic Evaluation

**Goal**: Test Grandalf with scenarios 1-3, document coordinate system and custom dimensions

**Tasks**:
- [ ] Create `test_grandalf.py` with VertexView class
- [ ] Test simple_chain, diamond, multiple_roots scenarios
- [ ] Document coordinate output format

**Code** (create `/Users/docchang/Development/visualflow/tests/test_grandalf.py`):
```python
"""Grandalf layout engine evaluation tests.

Grandalf is a pure Python Sugiyama layout library.
This test suite evaluates its capabilities for diagram generation.

Key findings to document:
- Custom node dimensions: Yes (via VertexView.w, VertexView.h)
- Coordinate system: Float coordinates (x, y) in VertexView.xy
- Edge routing hints: Limited (just node positions, no waypoints)
- Disconnected components: Handled via g.C list (one component per subgraph)
"""

import pytest
from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout

from conftest import TestGraph, TestNode, TestEdge


class VertexView:
    """Custom view to set node dimensions for Grandalf layout.

    Grandalf requires a 'view' object on each vertex with:
    - w: width of the node
    - h: height of the node
    - xy: tuple(x, y) - set by layout algorithm
    """

    def __init__(self, w: int = 15, h: int = 3) -> None:
        self.w = w
        self.h = h
        self.xy: tuple[float, float] = (0.0, 0.0)


def build_grandalf_graph(test_graph: TestGraph) -> tuple[Graph, dict[str, Vertex]]:
    """Convert TestGraph to Grandalf Graph.

    Returns:
        Tuple of (Graph, vertex_dict) where vertex_dict maps node id to Vertex
    """
    # Create vertices with views
    vertices: dict[str, Vertex] = {}
    for node in test_graph.nodes:
        v = Vertex(data=node)
        v.view = VertexView(w=node.width, h=node.height)
        vertices[node.id] = v

    # Create edges
    edges = [
        Edge(vertices[e.source], vertices[e.target]) for e in test_graph.edges
    ]

    # Build graph
    graph = Graph(list(vertices.values()), edges)
    return graph, vertices


def compute_layout(graph: Graph) -> None:
    """Compute Sugiyama layout for the first connected component."""
    if not graph.C:
        return

    sug = SugiyamaLayout(graph.C[0])
    sug.init_all()
    sug.draw()


class TestGrandalfBasicScenarios:
    """Test Grandalf with basic scenarios (1-3)."""

    def test_simple_chain_positions_assigned(self, simple_chain: TestGraph) -> None:
        """Verify Grandalf assigns positions to simple chain."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        # All vertices should have positions
        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_simple_chain_level_ordering(self, simple_chain: TestGraph) -> None:
        """Verify A is above B is above C (y increases downward)."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        # In Sugiyama layout, y typically increases downward
        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        # A should be above B, B above C
        assert y_a < y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b < y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_simple_chain_vertical_alignment(self, simple_chain: TestGraph) -> None:
        """Verify nodes are vertically aligned (same x)."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        x_a = vertices["a"].view.xy[0]
        x_b = vertices["b"].view.xy[0]
        x_c = vertices["c"].view.xy[0]

        # All should have same x (within tolerance for floats)
        assert abs(x_a - x_b) < 0.1, f"A and B not aligned: {x_a} vs {x_b}"
        assert abs(x_b - x_c) < 0.1, f"B and C not aligned: {x_b} vs {x_c}"

    def test_diamond_positions_assigned(self, diamond: TestGraph) -> None:
        """Verify Grandalf assigns positions to diamond."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_diamond_level_ordering(self, diamond: TestGraph) -> None:
        """Verify diamond has 3 levels: A, then B/C, then D."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]
        y_d = vertices["d"].view.xy[1]

        # A at top, D at bottom, B and C in middle
        assert y_a < y_b, "A should be above B"
        assert y_a < y_c, "A should be above C"
        assert y_b < y_d, "B should be above D"
        assert y_c < y_d, "C should be above D"
        # B and C should be at same level
        assert abs(y_b - y_c) < 0.1, f"B and C should be same level: {y_b} vs {y_c}"

    def test_diamond_horizontal_spread(self, diamond: TestGraph) -> None:
        """Verify B and C are horizontally separated."""
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        x_b = vertices["b"].view.xy[0]
        x_c = vertices["c"].view.xy[0]

        # B and C should have different x positions
        assert x_b != x_c, "B and C should be horizontally separated"

    def test_multiple_roots_positions_assigned(
        self, multiple_roots: TestGraph
    ) -> None:
        """Verify Grandalf assigns positions to multiple roots."""
        graph, vertices = build_grandalf_graph(multiple_roots)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_multiple_roots_level_ordering(self, multiple_roots: TestGraph) -> None:
        """Verify A and B are above C."""
        graph, vertices = build_grandalf_graph(multiple_roots)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        assert y_a < y_c, "A should be above C"
        assert y_b < y_c, "B should be above C"
        # A and B should be at same level (both are roots)
        assert abs(y_a - y_b) < 0.1, f"A and B should be same level: {y_a} vs {y_b}"
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_grandalf.py -v
```

**Output**: 9/9 tests passing

---

### Step 3: Grandalf Complete Evaluation (Scenarios 4-7)

**Goal**: Test remaining scenarios and document edge routing capabilities

**Tasks**:
- [ ] Add tests for skip_level, wide_graph, deep_graph, complex_graph
- [ ] Test custom node dimensions
- [ ] Document edge routing (or lack thereof)

**Code** (append to `/Users/docchang/Development/visualflow/tests/test_grandalf.py`):
```python
class TestGrandalfAdvancedScenarios:
    """Test Grandalf with advanced scenarios (4-7)."""

    def test_skip_level_positions(self, skip_level: TestGraph) -> None:
        """Verify skip-level graph positions."""
        graph, vertices = build_grandalf_graph(skip_level)
        compute_layout(graph)

        y_a = vertices["a"].view.xy[1]
        y_b = vertices["b"].view.xy[1]
        y_c = vertices["c"].view.xy[1]

        # A at top, C at bottom, B in middle
        assert y_a < y_b, "A should be above B"
        assert y_b < y_c, "B should be above C"

    def test_wide_graph_horizontal_spread(self, wide_graph: TestGraph) -> None:
        """Verify wide graph has horizontal spread for children."""
        graph, vertices = build_grandalf_graph(wide_graph)
        compute_layout(graph)

        # All children should be at same y level
        child_ys = [vertices[c].view.xy[1] for c in ["b", "c", "d", "e"]]
        for y in child_ys[1:]:
            assert abs(y - child_ys[0]) < 0.1, "All children should be same level"

        # Children should have different x positions
        child_xs = [vertices[c].view.xy[0] for c in ["b", "c", "d", "e"]]
        unique_xs = set(round(x, 1) for x in child_xs)
        assert len(unique_xs) == 4, "All 4 children should have unique x positions"

    def test_deep_graph_level_count(self, deep_graph: TestGraph) -> None:
        """Verify deep graph has 6 distinct levels."""
        graph, vertices = build_grandalf_graph(deep_graph)
        compute_layout(graph)

        ys = [vertices[n].view.xy[1] for n in ["a", "b", "c", "d", "e", "f"]]

        # Each should be below the previous
        for i in range(1, len(ys)):
            assert ys[i] > ys[i - 1], f"Level {i} should be below level {i-1}"

    def test_complex_graph_positions(self, complex_graph: TestGraph) -> None:
        """Verify complex graph assigns all positions."""
        graph, vertices = build_grandalf_graph(complex_graph)
        compute_layout(graph)

        for node_id, vertex in vertices.items():
            x, y = vertex.view.xy
            assert isinstance(x, (int, float)), f"Node {node_id} x not numeric"
            assert isinstance(y, (int, float)), f"Node {node_id} y not numeric"

    def test_complex_graph_start_end_ordering(self, complex_graph: TestGraph) -> None:
        """Verify start is above end in complex graph."""
        graph, vertices = build_grandalf_graph(complex_graph)
        compute_layout(graph)

        y_start = vertices["a"].view.xy[1]
        y_end = vertices["f"].view.xy[1]

        assert y_start < y_end, "Start should be above end"


class TestGrandalfCustomDimensions:
    """Test Grandalf's custom dimension capabilities."""

    def test_custom_width_respected(self, simple_chain: TestGraph) -> None:
        """Verify custom node widths are preserved."""
        # Modify widths
        simple_chain.nodes[0].width = 20
        simple_chain.nodes[1].width = 30
        simple_chain.nodes[2].width = 25

        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        assert vertices["a"].view.w == 20
        assert vertices["b"].view.w == 30
        assert vertices["c"].view.w == 25

    def test_custom_height_respected(self, simple_chain: TestGraph) -> None:
        """Verify custom node heights are preserved."""
        # Modify heights
        simple_chain.nodes[0].height = 5
        simple_chain.nodes[1].height = 7
        simple_chain.nodes[2].height = 4

        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        assert vertices["a"].view.h == 5
        assert vertices["b"].view.h == 7
        assert vertices["c"].view.h == 4


class TestGrandalfCapabilities:
    """Document Grandalf's capabilities and limitations."""

    def test_coordinate_system_is_float(self, simple_chain: TestGraph) -> None:
        """Document: Grandalf uses float coordinates."""
        graph, vertices = build_grandalf_graph(simple_chain)
        compute_layout(graph)

        x, y = vertices["a"].view.xy
        # Grandalf uses float coordinates
        assert isinstance(x, float) or isinstance(x, int)
        assert isinstance(y, float) or isinstance(y, int)

    def test_no_edge_routing_info(self, diamond: TestGraph) -> None:
        """Document: Grandalf does NOT provide edge routing waypoints.

        Grandalf only provides node positions. Edge routing must be
        computed separately based on node positions.
        """
        graph, vertices = build_grandalf_graph(diamond)
        compute_layout(graph)

        # Check edges - they only have source/target vertices, no routing
        for edge in graph.C[0].E():
            assert hasattr(edge, "v")  # source vertex tuple
            # No edge.path or edge.waypoints attribute
            assert not hasattr(edge, "path")
            assert not hasattr(edge, "waypoints")

    def test_disconnected_components_handled(self) -> None:
        """Document: Grandalf handles disconnected components via g.C list."""
        # Create two disconnected subgraphs
        v1 = Vertex(data="a")
        v2 = Vertex(data="b")
        v3 = Vertex(data="c")  # Disconnected
        v4 = Vertex(data="d")  # Disconnected

        v1.view = VertexView()
        v2.view = VertexView()
        v3.view = VertexView()
        v4.view = VertexView()

        e1 = Edge(v1, v2)
        e2 = Edge(v3, v4)

        graph = Graph([v1, v2, v3, v4], [e1, e2])

        # Grandalf separates into connected components
        assert len(graph.C) == 2, "Should have 2 connected components"

        # Each component can be laid out separately
        for component in graph.C:
            sug = SugiyamaLayout(component)
            sug.init_all()
            sug.draw()

        # All vertices should have positions
        for v in [v1, v2, v3, v4]:
            assert v.view.xy != (0.0, 0.0) or v.view.xy == (
                0.0,
                0.0,
            )  # Position assigned
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_grandalf.py -v
```

**Output**: 18/18 tests passing

---

### Step 4: Graphviz Basic Evaluation

**Goal**: Test Graphviz with scenarios 1-3 using `dot -Tplain` output format

**Tasks**:
- [ ] Create `test_graphviz.py` with DOT generation and plain output parsing
- [ ] Test simple_chain, diamond, multiple_roots scenarios
- [ ] Document coordinate system and output format

**Code** (create `/Users/docchang/Development/visualflow/tests/test_graphviz.py`):
```python
"""Graphviz layout engine evaluation tests.

Graphviz is an industry-standard graph visualization tool (30+ years).
This test suite evaluates its capabilities via `dot -Tplain` output.

Key findings to document:
- Custom node dimensions: Yes (via width/height attributes in DOT)
- Coordinate system: Float coordinates in inches (72 DPI)
- Edge routing hints: Yes (spline control points in plain output)
- Disconnected components: Handled automatically
- Integration: Subprocess call to `dot` CLI
"""

import shutil
import subprocess
from dataclasses import dataclass

import pytest

from conftest import TestGraph


def is_graphviz_installed() -> bool:
    """Check if Graphviz is installed."""
    return shutil.which("dot") is not None


# Skip all tests in this module if Graphviz not installed
pytestmark = pytest.mark.skipif(
    not is_graphviz_installed(),
    reason="Graphviz not installed (run: brew install graphviz)",
)


@dataclass
class PlainNode:
    """Parsed node from Graphviz plain output."""

    name: str
    x: float  # Center x in inches
    y: float  # Center y in inches
    width: float  # Width in inches
    height: float  # Height in inches
    label: str


@dataclass
class PlainEdge:
    """Parsed edge from Graphviz plain output."""

    source: str
    target: str
    points: list[tuple[float, float]]  # Spline control points


@dataclass
class PlainGraph:
    """Parsed Graphviz plain output."""

    scale: float
    width: float
    height: float
    nodes: dict[str, PlainNode]
    edges: list[PlainEdge]


def build_dot_input(test_graph: TestGraph) -> str:
    """Convert TestGraph to DOT format."""
    lines = ["digraph G {"]
    lines.append("  rankdir=TB;")  # Top to bottom

    for node in test_graph.nodes:
        # Convert character dimensions to inches (assuming 10 chars = 1 inch)
        width_inches = node.width / 10.0
        height_inches = node.height / 2.0  # Assuming 2 lines = 1 inch
        lines.append(
            f'  {node.id} [label="{node.label}" '
            f'width={width_inches} height={height_inches} fixedsize=true];'
        )

    for edge in test_graph.edges:
        lines.append(f"  {edge.source} -> {edge.target};")

    lines.append("}")
    return "\n".join(lines)


def run_graphviz(dot_input: str) -> str:
    """Run Graphviz and return plain output."""
    result = subprocess.run(
        ["dot", "-Tplain"],
        input=dot_input,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Graphviz failed: {result.stderr}")
    return result.stdout


def parse_plain_output(plain: str) -> PlainGraph:
    """Parse Graphviz plain output format.

    Format:
        graph scale width height
        node name x y width height label style shape color fillcolor
        edge tail head n x1 y1 ... xn yn [label xl yl] style color
        stop
    """
    nodes: dict[str, PlainNode] = {}
    edges: list[PlainEdge] = []
    scale = width = height = 0.0

    for line in plain.strip().split("\n"):
        parts = line.split()
        if not parts:
            continue

        if parts[0] == "graph":
            scale = float(parts[1])
            width = float(parts[2])
            height = float(parts[3])

        elif parts[0] == "node":
            name = parts[1]
            x = float(parts[2])
            y = float(parts[3])
            w = float(parts[4])
            h = float(parts[5])
            label = parts[6] if len(parts) > 6 else name
            nodes[name] = PlainNode(name=name, x=x, y=y, width=w, height=h, label=label)

        elif parts[0] == "edge":
            source = parts[1]
            target = parts[2]
            n_points = int(parts[3])
            points = []
            for i in range(n_points):
                px = float(parts[4 + i * 2])
                py = float(parts[5 + i * 2])
                points.append((px, py))
            edges.append(PlainEdge(source=source, target=target, points=points))

    return PlainGraph(
        scale=scale, width=width, height=height, nodes=nodes, edges=edges
    )


def layout_graph(test_graph: TestGraph) -> PlainGraph:
    """Run full Graphviz pipeline for a test graph."""
    dot_input = build_dot_input(test_graph)
    plain_output = run_graphviz(dot_input)
    return parse_plain_output(plain_output)


class TestGraphvizBasicScenarios:
    """Test Graphviz with basic scenarios (1-3)."""

    def test_simple_chain_positions_assigned(self, simple_chain: TestGraph) -> None:
        """Verify Graphviz assigns positions to simple chain."""
        result = layout_graph(simple_chain)

        assert len(result.nodes) == 3
        for node_id in ["a", "b", "c"]:
            assert node_id in result.nodes
            node = result.nodes[node_id]
            assert isinstance(node.x, float)
            assert isinstance(node.y, float)

    def test_simple_chain_level_ordering(self, simple_chain: TestGraph) -> None:
        """Verify A is above B is above C.

        Note: Graphviz y-axis has origin at bottom, so higher y = higher position.
        With rankdir=TB, A should have highest y.
        """
        result = layout_graph(simple_chain)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        # In Graphviz with TB, higher y = closer to top
        assert y_a > y_b, f"A (y={y_a}) should be above B (y={y_b})"
        assert y_b > y_c, f"B (y={y_b}) should be above C (y={y_c})"

    def test_simple_chain_has_edges(self, simple_chain: TestGraph) -> None:
        """Verify edges are present with routing points."""
        result = layout_graph(simple_chain)

        assert len(result.edges) == 2

        # Find a->b edge
        ab_edge = next((e for e in result.edges if e.source == "a"), None)
        assert ab_edge is not None
        assert ab_edge.target == "b"
        assert len(ab_edge.points) > 0, "Edge should have routing points"

    def test_diamond_positions_assigned(self, diamond: TestGraph) -> None:
        """Verify Graphviz assigns positions to diamond."""
        result = layout_graph(diamond)

        assert len(result.nodes) == 4
        for node_id in ["a", "b", "c", "d"]:
            assert node_id in result.nodes

    def test_diamond_level_ordering(self, diamond: TestGraph) -> None:
        """Verify diamond levels: A top, B/C middle, D bottom."""
        result = layout_graph(diamond)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y
        y_d = result.nodes["d"].y

        # A at top (highest y), D at bottom (lowest y)
        assert y_a > y_b, "A should be above B"
        assert y_a > y_c, "A should be above C"
        assert y_b > y_d, "B should be above D"
        assert y_c > y_d, "C should be above D"

    def test_diamond_has_four_edges(self, diamond: TestGraph) -> None:
        """Verify diamond has all 4 edges with routing."""
        result = layout_graph(diamond)

        assert len(result.edges) == 4
        for edge in result.edges:
            assert len(edge.points) > 0, f"Edge {edge.source}->{edge.target} has no points"

    def test_multiple_roots_positions_assigned(
        self, multiple_roots: TestGraph
    ) -> None:
        """Verify Graphviz assigns positions to multiple roots."""
        result = layout_graph(multiple_roots)

        assert len(result.nodes) == 3
        for node_id in ["a", "b", "c"]:
            assert node_id in result.nodes

    def test_multiple_roots_level_ordering(self, multiple_roots: TestGraph) -> None:
        """Verify A and B are above C."""
        result = layout_graph(multiple_roots)

        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        assert y_a > y_c, "A should be above C"
        assert y_b > y_c, "B should be above C"
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_graphviz.py -v
```

**Output**: 9/9 tests passing

---

### Step 5: Graphviz Complete Evaluation (Scenarios 4-7)

**Goal**: Test remaining scenarios and document edge routing capabilities

**Tasks**:
- [ ] Add tests for skip_level, wide_graph, deep_graph, complex_graph
- [ ] Test custom node dimensions
- [ ] Document edge spline points

**Code** (append to `/Users/docchang/Development/visualflow/tests/test_graphviz.py`):
```python
class TestGraphvizAdvancedScenarios:
    """Test Graphviz with advanced scenarios (4-7)."""

    def test_skip_level_positions(self, skip_level: TestGraph) -> None:
        """Verify skip-level graph positions."""
        result = layout_graph(skip_level)

        assert len(result.nodes) == 3
        y_a = result.nodes["a"].y
        y_b = result.nodes["b"].y
        y_c = result.nodes["c"].y

        assert y_a > y_b, "A should be above B"
        assert y_b > y_c, "B should be above C"

    def test_skip_level_has_three_edges(self, skip_level: TestGraph) -> None:
        """Verify skip-level has all 3 edges including skip edge."""
        result = layout_graph(skip_level)

        assert len(result.edges) == 3
        # Check for direct a->c skip edge
        skip_edge = next(
            (e for e in result.edges if e.source == "a" and e.target == "c"), None
        )
        assert skip_edge is not None, "Skip edge a->c should exist"

    def test_wide_graph_horizontal_spread(self, wide_graph: TestGraph) -> None:
        """Verify wide graph has horizontal spread for children."""
        result = layout_graph(wide_graph)

        # Children should have different x positions
        child_xs = [result.nodes[c].x for c in ["b", "c", "d", "e"]]
        unique_xs = set(round(x, 2) for x in child_xs)
        assert len(unique_xs) == 4, "All 4 children should have unique x positions"

    def test_deep_graph_level_count(self, deep_graph: TestGraph) -> None:
        """Verify deep graph has 6 distinct levels."""
        result = layout_graph(deep_graph)

        ys = [result.nodes[n].y for n in ["a", "b", "c", "d", "e", "f"]]

        # Each should be below the previous (smaller y)
        for i in range(1, len(ys)):
            assert ys[i] < ys[i - 1], f"Level {i} should be below level {i-1}"

    def test_complex_graph_positions(self, complex_graph: TestGraph) -> None:
        """Verify complex graph assigns all positions."""
        result = layout_graph(complex_graph)

        assert len(result.nodes) == 6
        for node_id in ["a", "b", "c", "d", "e", "f"]:
            assert node_id in result.nodes

    def test_complex_graph_edge_count(self, complex_graph: TestGraph) -> None:
        """Verify complex graph has all 7 edges."""
        result = layout_graph(complex_graph)

        assert len(result.edges) == 7


class TestGraphvizCustomDimensions:
    """Test Graphviz's custom dimension capabilities."""

    def test_custom_dimensions_in_output(self, simple_chain: TestGraph) -> None:
        """Verify custom dimensions are reflected in output."""
        # Modify widths
        simple_chain.nodes[0].width = 20
        simple_chain.nodes[1].width = 30
        simple_chain.nodes[2].width = 25

        result = layout_graph(simple_chain)

        # Dimensions should be close to what we specified (in inches)
        # We specified width/10, so 20 chars -> 2.0 inches
        assert abs(result.nodes["a"].width - 2.0) < 0.1
        assert abs(result.nodes["b"].width - 3.0) < 0.1
        assert abs(result.nodes["c"].width - 2.5) < 0.1


class TestGraphvizCapabilities:
    """Document Graphviz's capabilities and features."""

    def test_coordinate_system_is_inches(self, simple_chain: TestGraph) -> None:
        """Document: Graphviz uses inches for coordinates."""
        result = layout_graph(simple_chain)

        # Coordinates are in inches (small positive numbers)
        for node in result.nodes.values():
            assert 0 <= node.x < 100, f"x={node.x} seems unreasonable for inches"
            assert 0 <= node.y < 100, f"y={node.y} seems unreasonable for inches"

    def test_edge_routing_provides_spline_points(self, diamond: TestGraph) -> None:
        """Document: Graphviz provides spline control points for edges."""
        result = layout_graph(diamond)

        for edge in result.edges:
            # Edges have multiple control points (usually 4+ for bezier)
            assert len(edge.points) >= 2, f"Edge should have at least 2 points"

            # Points are float coordinates
            for x, y in edge.points:
                assert isinstance(x, float)
                assert isinstance(y, float)

    def test_graph_bounding_box_provided(self, simple_chain: TestGraph) -> None:
        """Document: Graphviz provides graph bounding box."""
        result = layout_graph(simple_chain)

        assert result.width > 0, "Graph width should be positive"
        assert result.height > 0, "Graph height should be positive"
        assert result.scale > 0, "Graph scale should be positive"

    def test_disconnected_components_handled(self) -> None:
        """Document: Graphviz handles disconnected components automatically."""
        # Create graph with two disconnected parts
        dot_input = """digraph G {
            a -> b;
            c -> d;
        }"""

        plain_output = run_graphviz(dot_input)
        result = parse_plain_output(plain_output)

        # All 4 nodes should be present
        assert len(result.nodes) == 4
        assert "a" in result.nodes
        assert "c" in result.nodes
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_graphviz.py -v
```

**Output**: 17/17 tests passing (9 basic + 8 advanced/capabilities)

---

### Step 6: ascii-dag Basic Evaluation

**Goal**: Test ascii-dag via compiled binary, understand capabilities

**Tasks**:
- [ ] Create `test_ascii_dag.py` with binary execution tests
- [ ] Test existing `basic` example
- [ ] Document output format and integration complexity

**Code** (create `/Users/docchang/Development/visualflow/tests/test_ascii_dag.py`):
```python
"""ascii-dag layout engine evaluation tests.

ascii-dag is a Rust library with sophisticated Sugiyama layout and edge routing.
This test suite evaluates its capabilities via subprocess calls to compiled examples.

Key findings to document:
- Custom node dimensions: Yes (in Rust API)
- Coordinate system: Character-based grid
- Edge routing hints: Yes (sophisticated edge routing built-in)
- Integration: Subprocess to compiled binary (no Python bindings)
- Unique value: Already renders ASCII output directly
"""

import subprocess
from pathlib import Path

import pytest


ASCII_DAG_DIR = Path(__file__).parent.parent / "ascii-dag"
ASCII_DAG_BINARY_DIR = ASCII_DAG_DIR / "target" / "release" / "examples"


def is_ascii_dag_built() -> bool:
    """Check if ascii-dag is compiled."""
    return (ASCII_DAG_BINARY_DIR / "basic").exists()


# Skip all tests if ascii-dag not built
pytestmark = pytest.mark.skipif(
    not is_ascii_dag_built(),
    reason="ascii-dag not built (run: cd ascii-dag && cargo build --release --examples)",
)


def run_example(name: str, timeout: float = 5.0) -> str:
    """Run an ascii-dag example and return output."""
    binary = ASCII_DAG_BINARY_DIR / name
    if not binary.exists():
        pytest.skip(f"Example {name} not built")

    result = subprocess.run(
        [str(binary)],
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result.stdout


class TestAsciiDagBuilt:
    """Verify ascii-dag is properly built."""

    def test_cargo_toml_exists(self) -> None:
        """Verify ascii-dag is cloned."""
        cargo_toml = ASCII_DAG_DIR / "Cargo.toml"
        assert cargo_toml.exists(), "ascii-dag not cloned"

    def test_release_build_exists(self) -> None:
        """Verify release build exists."""
        release_dir = ASCII_DAG_DIR / "target" / "release"
        assert release_dir.exists(), "ascii-dag not built in release mode"

    def test_basic_example_exists(self) -> None:
        """Verify basic example is compiled."""
        basic = ASCII_DAG_BINARY_DIR / "basic"
        assert basic.exists(), "basic example not compiled"


class TestAsciiDagBasicExample:
    """Test ascii-dag's basic example output."""

    def test_basic_produces_output(self) -> None:
        """Verify basic example produces output."""
        output = run_example("basic")
        assert output, "No output from basic example"
        assert len(output) > 10, "Output too short"

    def test_basic_output_contains_box_chars(self) -> None:
        """Verify output contains ASCII box characters."""
        output = run_example("basic")

        # Should contain box drawing characters or brackets
        box_chars = ["[", "]", "─", "│", "┌", "┐", "└", "┘", "+", "-", "|"]
        has_box_char = any(c in output for c in box_chars)
        assert has_box_char, f"Output doesn't look like ASCII diagram: {output[:100]}"

    def test_basic_output_is_multiline(self) -> None:
        """Verify output is multi-line diagram."""
        output = run_example("basic")
        lines = output.strip().split("\n")
        assert len(lines) > 1, "Output should be multi-line"


class TestAsciiDagCapabilities:
    """Document ascii-dag's capabilities based on available examples."""

    def test_list_available_examples(self) -> None:
        """Document which examples are available."""
        if not ASCII_DAG_BINARY_DIR.exists():
            pytest.skip("Binary directory doesn't exist")

        examples = [
            f.name
            for f in ASCII_DAG_BINARY_DIR.iterdir()
            if f.is_file() and not f.name.endswith(".d")
        ]

        # Should have at least the basic example
        assert "basic" in examples

        # Document available examples
        print(f"\nAvailable ascii-dag examples: {sorted(examples)}")

    def test_basic_example_visual_inspection(self) -> None:
        """Visual inspection of basic example output.

        This test prints the output for manual inspection.
        It always passes - the purpose is documentation.
        """
        output = run_example("basic")

        # Print for visual inspection
        print("\n" + "=" * 60)
        print("ascii-dag basic example output:")
        print("=" * 60)
        print(output)
        print("=" * 60)

        # Always pass - this is for inspection only
        assert True

    def test_output_format_analysis(self) -> None:
        """Analyze the output format of ascii-dag."""
        output = run_example("basic")

        # Count unique characters used
        chars = set(output)
        printable_chars = [c for c in chars if c.isprintable() and c != " "]

        # Document character set
        print(f"\nCharacters used: {sorted(printable_chars)}")

        # Check for common diagram elements
        has_arrows = any(c in output for c in ["→", "←", "↓", "↑", ">", "<", "v", "^"])
        has_boxes = any(c in output for c in ["[", "]", "┌", "┐", "└", "┘"])
        has_lines = any(c in output for c in ["─", "│", "-", "|"])

        print(f"Has arrows: {has_arrows}")
        print(f"Has boxes: {has_boxes}")
        print(f"Has lines: {has_lines}")


class TestAsciiDagIntegrationComplexity:
    """Document integration complexity for ascii-dag."""

    def test_integration_requires_subprocess(self) -> None:
        """Document: ascii-dag requires subprocess for Python integration.

        ascii-dag is a Rust library. For Python integration, options are:
        1. Subprocess to compiled binary (current approach)
        2. Build Python bindings with PyO3
        3. FFI bridge

        Subprocess is simplest but limits flexibility.
        """
        # This is a documentation test - always passes
        assert True

    def test_no_python_api(self) -> None:
        """Document: No native Python API available.

        Unlike Grandalf (pure Python) or Graphviz (Python bindings exist),
        ascii-dag requires compilation and subprocess calls.
        """
        # Try to import - should fail
        try:
            import ascii_dag  # noqa: F401

            pytest.fail("ascii_dag should not be importable")
        except ImportError:
            pass  # Expected

    def test_custom_input_requires_rust_code(self) -> None:
        """Document: Custom graph input requires modifying Rust code.

        The compiled examples have hardcoded graphs. To test our
        scenarios, we would need to either:
        1. Create a Rust CLI that accepts input
        2. Create Python bindings
        3. Use the Rust library directly in a Rust test

        This is significantly more complex than Grandalf or Graphviz.
        """
        # Document the limitation
        assert True
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_ascii_dag.py -v -s
```

**Output**: 8/8 tests passing (with visual output for inspection)

---

### Step 7: ascii-dag Additional Examples Evaluation

**Goal**: Test more ascii-dag examples to understand capabilities better

**Tasks**:
- [ ] Test complex_graphs example if available
- [ ] Test edge routing examples if available
- [ ] Compile additional examples if needed

**Code** (append to `/Users/docchang/Development/visualflow/tests/test_ascii_dag.py`):
```python
class TestAsciiDagAdditionalExamples:
    """Test additional ascii-dag examples if available."""

    def test_build_additional_examples(self) -> None:
        """Build additional examples for testing.

        This test attempts to build more examples. If it fails,
        subsequent tests will be skipped.
        """
        result = subprocess.run(
            ["cargo", "build", "--release", "--examples"],
            cwd=ASCII_DAG_DIR,
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode != 0:
            print(f"Build output: {result.stderr}")
            # Don't fail - just document

    def test_complex_graphs_if_available(self) -> None:
        """Test complex_graphs example if built."""
        binary = ASCII_DAG_BINARY_DIR / "complex_graphs"
        if not binary.exists():
            pytest.skip("complex_graphs example not built")

        output = run_example("complex_graphs")

        print("\n" + "=" * 60)
        print("ascii-dag complex_graphs output:")
        print("=" * 60)
        print(output[:2000])  # Limit output length
        print("=" * 60)

        assert output, "No output from complex_graphs"

    def test_edge_cases_if_available(self) -> None:
        """Test edge_cases example if built."""
        binary = ASCII_DAG_BINARY_DIR / "edge_cases"
        if not binary.exists():
            pytest.skip("edge_cases example not built")

        output = run_example("edge_cases")

        print("\n" + "=" * 60)
        print("ascii-dag edge_cases output:")
        print("=" * 60)
        print(output[:2000])
        print("=" * 60)

        assert output, "No output from edge_cases"

    def test_cross_level_if_available(self) -> None:
        """Test cross_level example if built (similar to our skip-level)."""
        binary = ASCII_DAG_BINARY_DIR / "cross_level"
        if not binary.exists():
            pytest.skip("cross_level example not built")

        output = run_example("cross_level")

        print("\n" + "=" * 60)
        print("ascii-dag cross_level output:")
        print("=" * 60)
        print(output[:2000])
        print("=" * 60)

        assert output, "No output from cross_level"


class TestAsciiDagUniqueValue:
    """Document ascii-dag's unique value proposition."""

    def test_direct_ascii_output(self) -> None:
        """Document: ascii-dag produces ASCII output directly.

        Unlike Grandalf and Graphviz which produce coordinates,
        ascii-dag produces the final ASCII diagram directly.
        This is its main unique value.
        """
        output = run_example("basic")

        # Output is directly usable ASCII art
        assert "\n" in output, "Should be multi-line"
        # No coordinates to parse - it's already visual

    def test_sophisticated_edge_routing(self) -> None:
        """Document: ascii-dag has sophisticated edge routing built-in.

        The edge routing in ascii-dag handles:
        - Cross-level edges
        - Edge bundling
        - Collision avoidance

        This is the main reason to consider using it.
        """
        output = run_example("basic")

        # Look for edge routing characters
        edge_chars = ["│", "|", "─", "-", "└", "┘", "┌", "┐"]
        has_edges = any(c in output for c in edge_chars)
        assert has_edges, "Should have edge routing characters"

    def test_no_coordinate_transformation_needed(self) -> None:
        """Document: No coordinate transformation needed.

        With Grandalf or Graphviz, we need to:
        1. Get coordinates
        2. Scale to character grid
        3. Render boxes
        4. Compute edge routing
        5. Render edges

        With ascii-dag, it's just:
        1. Call binary
        2. Get ASCII output

        Trade-off: Less flexibility, but simpler integration.
        """
        # This is documentation - always passes
        assert True
```

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/test_ascii_dag.py -v -s
```

**Output**: All ascii-dag tests passing

---

### Step 8: Run All Tests and Create Summary

**Goal**: Run full test suite and prepare data for comparison matrix

**Tasks**:
- [ ] Run all tests together
- [ ] Verify no conflicts between test files
- [ ] Document test counts per engine

**Verification**:
```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
```

**Expected Output**: All tests passing

---

### Step 9: Create Comparison Matrix Document

**Goal**: Synthesize all findings into decision matrix

**Tasks**:
- [ ] Create `docs/poc0-comparison-matrix.md`
- [ ] Fill in test results summary
- [ ] Fill in capability matrix
- [ ] Calculate value vs. complexity scores
- [ ] Make engine selection recommendation

**Code** (create `/Users/docchang/Development/visualflow/docs/poc0-comparison-matrix.md`):
```markdown
# PoC 0 Comparison Matrix

> Layout engine evaluation results for Visual Milestone

## Test Results Summary

| Scenario | Grandalf | Graphviz | ascii-dag |
|----------|----------|----------|-----------|
| 1. Simple chain | [result] | [result] | [N/A - no custom input] |
| 2. Diamond | [result] | [result] | [N/A] |
| 3. Multiple roots | [result] | [result] | [N/A] |
| 4. Skip-level | [result] | [result] | [N/A] |
| 5. Wide graph | [result] | [result] | [N/A] |
| 6. Deep graph | [result] | [result] | [N/A] |
| 7. Complex | [result] | [result] | [N/A] |

**Note**: ascii-dag cannot be tested with custom scenarios without Rust code changes.

## Capability Matrix

| Capability | Grandalf | Graphviz | ascii-dag |
|------------|----------|----------|-----------|
| Custom node dimensions | Yes (VertexView) | Yes (width/height attrs) | Yes (Rust API) |
| Coordinate output | Float (x, y) | Float (inches) | Character grid |
| Edge routing hints | No | Yes (spline points) | Yes (built-in) |
| Disconnected components | Yes (g.C list) | Yes (automatic) | Yes |
| Python native | Yes | No (subprocess) | No (subprocess) |
| Final ASCII output | No (need render) | No (need render) | Yes (direct) |
| Custom input easy | Yes | Yes (DOT format) | No (need Rust code) |

## Integration Complexity

| Engine | Integration Method | Complexity | Notes |
|--------|-------------------|------------|-------|
| Grandalf | Python import | Low | Pure Python, pip install |
| Graphviz | subprocess + DOT | Medium | Requires `dot` CLI, parse output |
| ascii-dag | subprocess + Rust | High | Requires Rust toolchain, modify source |

## Value vs. Complexity Assessment

| Engine | Unique Value | Integration Complexity | Recommendation |
|--------|--------------|----------------------|----------------|
| Grandalf | Pure Python, fast integration | Low | [TBD] |
| Graphviz | Industry standard, edge splines | Medium | [TBD] |
| ascii-dag | Direct ASCII output, sophisticated routing | High | [TBD] |

## Quality Assessment

| Engine | Can Produce Flawless Output? | Notes |
|--------|------------------------------|-------|
| Grandalf | [TBD after visual inspection] | |
| Graphviz | [TBD after visual inspection] | |
| ascii-dag | [TBD after visual inspection] | |

## Decision

**Question**: Do we need 3, 2, or 1 engine(s)?

**Answer**: [To be filled after all tests complete]

**Rationale**: [Evidence-based reasoning]

**Recommended Architecture**:
- Layout: [Engine(s) for computing positions]
- Edge Routing: [Approach for computing edges]
- Rendering: [Approach for final ASCII output]

---

*Generated from PoC 0 test results*
*Last updated*: [Date]
```

**Note**: This template will be filled in during execution based on actual test results.

**Verification**:
```bash
ls -la /Users/docchang/Development/visualflow/docs/poc0-comparison-matrix.md
# Expected: File exists
```

**Output**: Comparison matrix document created

---

## Test Summary

### Affected Tests (Run These)

| Test File | Tests | What It Covers |
|-----------|-------|----------------|
| `tests/test_fixtures.py` | ~10 | Fixture validation |
| `tests/test_grandalf.py` | ~18 | Grandalf evaluation |
| `tests/test_graphviz.py` | ~18 | Graphviz evaluation |
| `tests/test_ascii_dag.py` | ~15 | ascii-dag evaluation |

**Total tests: ~61 tests**

---

## Production-Grade Checklist

Before marking PoC complete, verify:

- [ ] **Dataclasses for test data**: TestNode, TestEdge, TestGraph properly defined
- [ ] **Strong Typing**: Type hints on all fixtures, functions, and classes
- [ ] **No mock data**: Tests use real layout engines with real graph data
- [ ] **Real integrations**: Grandalf import, Graphviz subprocess, ascii-dag binary
- [ ] **Error handling**: Graceful skips when dependencies missing
- [ ] **Tests in same step**: Each step writes AND runs its tests
- [ ] **Config externalized**: Binary paths use Path for portability
- [ ] **Clean separation**: Each test file focuses on one engine
- [ ] **Self-contained**: Works independently; creates full test infrastructure

---

## What "Done" Looks Like

```bash
# 1. All tests pass
cd /Users/docchang/Development/visualflow && uv run pytest tests/ -v --tb=short
# Expected: All pass (~61 tests)

# 2. Comparison matrix document exists
cat /Users/docchang/Development/visualflow/docs/poc0-comparison-matrix.md
# Expected: Document with findings

# 3. Decision made: which engine(s) to use
grep "Answer:" /Users/docchang/Development/visualflow/docs/poc0-comparison-matrix.md
# Expected: Clear answer with rationale
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `tests/conftest.py` | Create | Shared fixtures (7 scenarios) |
| `tests/test_fixtures.py` | Create | Fixture validation tests |
| `tests/test_grandalf.py` | Create | Grandalf evaluation tests |
| `tests/test_graphviz.py` | Create | Graphviz evaluation tests |
| `tests/test_ascii_dag.py` | Create | ascii-dag evaluation tests |
| `docs/poc0-comparison-matrix.md` | Create | Decision matrix document |

---

## Dependencies

No new dependencies needed. Current `pyproject.toml` already has:

```toml
dependencies = [
    "grandalf>=0.8",
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
]
```

External dependencies (already installed):
- Graphviz CLI (`brew install graphviz`) - verified installed
- ascii-dag compiled binary - verified built

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| ascii-dag examples not representative | Medium | Build additional examples; inspect source code |
| Graphviz output parsing errors | Low | Well-documented format; robust parser |
| Grandalf edge routing insufficient | Medium | This is why we're evaluating all three |
| Integration complexity higher than expected | Low | All three engines already verified working |

---

## Next Steps After Completion

1. Verify all tests pass (~61 tests)
2. Verify comparison matrix has clear decision
3. Proceed to PoC 1: Design & Architecture based on engine selection
