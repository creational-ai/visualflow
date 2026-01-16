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
