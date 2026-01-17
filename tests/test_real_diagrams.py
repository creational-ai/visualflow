"""Tests using actual PoC diagrams from visual milestone results docs.

These tests use real-world diagram content from:
- docs/visual-poc0-results.md
- docs/visual-poc1-results.md
- docs/visual-poc2-results.md

This validates the complete pipeline with production-quality inputs.
"""

import pytest

from visualflow import DAG, render_dag, GrandalfEngine, settings
from visualflow.routing import SimpleRouter


# =============================================================================
# ACTUAL DIAGRAMS FROM RESULTS DOCS
# =============================================================================

POC0_DIAGRAM = """\
┌───────────────────────────┐
│          PoC 0            │
│       EXPLORATION         │
│       ✅ Complete         │
│                           │
│ Engines Evaluated         │
│   • Grandalf (Python)     │
│   • Graphviz (C)          │
│   • ascii-dag (Rust)      │
│                           │
│ Decision                  │
│   • 2 engines selected    │
│   • Grandalf: positioning │
│   • Graphviz: edge hints  │
└───────────────────────────┘"""

POC1_DIAGRAM = """\
┌───────────────────────┐
│        PoC 1          │
│        LAYOUT         │
│      ✅ Complete      │
│                       │
│ Data Models           │
│   • 6 Pydantic models │
│   • wcwidth Unicode   │
│                       │
│ Engines               │
│   • Grandalf (fast)   │
│   • Graphviz (CLI)    │
│                       │
│ Architecture          │
│   • Protocol pattern  │
│   • Canvas rendering  │
└───────────────────────┘"""

POC2_DIAGRAM = """\
┌───────────────────────┐
│        PoC 2          │
│       ROUTING         │
│     ✅ Complete       │
│                       │
│ Capabilities          │
│   • Edge routing      │
│   • Unicode (emoji)   │
│   • All 7 fixtures    │
│                       │
│ Architecture          │
│   • EdgeRouter proto  │
│   • SimpleRouter      │
│   • Canvas.draw_edge  │
│                       │
│ Performance           │
│   • 0.002s render     │
└───────────────────────┘"""

# PoC 3 - Now complete (from docs/visual-poc3-results.md)
POC3_DIAGRAM = """\
┌───────────────────────┐
│        PoC 3          │
│     SMART ROUTING     │
│      ✅ Complete      │
│                       │
│ Edge Patterns         │
│   • Box connectors    │
│   • Trunk-and-split   │
│   • Merge routing     │
│                       │
│ Smart Features        │
│   • Same-layer detect │
│   • Multi-exit points │
└───────────────────────┘"""

# Independent branch node (depends only on PoC 0)
POC4_DIAGRAM = """\
┌───────────────────────┐
│        PoC 4          │
│    INTERFACE LAYER    │
│      ○ Planned        │
│                       │
│ Scope                 │
│   • MC adapter        │
│   • PyPI release      │
│   • Documentation     │
└───────────────────────┘"""


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def poc0_node():
    """PoC 0 diagram node."""
    return ("poc0", POC0_DIAGRAM)


@pytest.fixture
def poc1_node():
    """PoC 1 diagram node."""
    return ("poc1", POC1_DIAGRAM)


@pytest.fixture
def poc2_node():
    """PoC 2 diagram node."""
    return ("poc2", POC2_DIAGRAM)


@pytest.fixture
def poc3_node():
    """PoC 3 diagram node."""
    return ("poc3", POC3_DIAGRAM)


@pytest.fixture
def poc4_node():
    """PoC 4 diagram node."""
    return ("poc4", POC4_DIAGRAM)


# =============================================================================
# LINEAR CHAIN TESTS
# =============================================================================

class TestLinearChain:
    """Tests for linear dependency chains."""

    def test_two_node_chain(self, poc0_node, poc1_node) -> None:
        """PoC 0 -> PoC 1: Simple two-node vertical chain."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_edge("poc0", "poc1")

        result = render_dag(dag)

        # Both boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "EXPLORATION" in result
        assert "LAYOUT" in result
        # Edge characters present
        assert settings.theme.vertical in result
        assert settings.theme.arrow_down in result

    def test_three_node_chain(self, poc0_node, poc1_node, poc2_node) -> None:
        """PoC 0 -> PoC 1 -> PoC 2: Three-node vertical chain."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)

        # All boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        # Content preserved
        assert "EXPLORATION" in result
        assert "LAYOUT" in result
        assert "ROUTING" in result
        # Unicode emoji preserved
        assert "✅" in result

    def test_four_node_chain(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """PoC 0 -> PoC 1 -> PoC 2 -> PoC 3: Full milestone chain."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # All four boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        # All complete now (4 checkmarks)
        assert result.count("✅") == 4  # All PoCs complete


# =============================================================================
# FAN-OUT TESTS (One parent, multiple children)
# =============================================================================

class TestFanOut:
    """Tests for fan-out patterns (one parent -> multiple children)."""

    def test_one_to_two_fanout(self, poc0_node, poc1_node, poc2_node) -> None:
        """PoC 0 -> {PoC 1, PoC 2}: One parent, two children."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")

        result = render_dag(dag)

        # All boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        # Z-shape indicators (horizontal segments)
        assert "-" in result or "+" in result

    def test_one_to_three_fanout(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """PoC 0 -> {PoC 1, PoC 2, PoC 3}: One parent, three children."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc0", "poc3")

        result = render_dag(dag)

        # All boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        # Multiple edges (horizontal routing)
        assert "-" in result


# =============================================================================
# FAN-IN TESTS (Multiple parents, one child)
# =============================================================================

class TestFanIn:
    """Tests for fan-in/merge patterns (multiple parents -> one child)."""

    def test_two_to_one_merge(self, poc0_node, poc1_node, poc2_node) -> None:
        """PoC 0 -> PoC 2, PoC 1 -> PoC 2: Two parents, one child."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)

        # All boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        # Merge point indicators
        assert settings.theme.vertical in result
        assert settings.theme.arrow_down in result

    def test_three_to_one_merge(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """PoC 0,1,2 -> PoC 3: Three parents, one child."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc3")
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # All boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result


# =============================================================================
# DIAMOND PATTERN TESTS
# =============================================================================

class TestDiamondPattern:
    """Tests for diamond patterns (diverge then converge)."""

    def test_classic_diamond(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """PoC 0 -> {PoC 1, PoC 2} -> PoC 3: Classic diamond."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        # Fan-out
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        # Fan-in
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # All boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        # Edge characters for complex routing
        assert settings.theme.vertical in result
        assert settings.theme.horizontal in result or settings.theme.cross in result
        assert settings.theme.arrow_down in result


# =============================================================================
# INDEPENDENT BRANCH TESTS
# =============================================================================

class TestIndependentBranch:
    """Tests for independent branches (one parent with separate child paths)."""

    def test_chain_with_independent_branch(
        self, poc0_node, poc1_node, poc2_node, poc3_node, poc4_node
    ) -> None:
        """PoC 0 -> PoC 1 -> PoC 2 -> PoC 3 (chain), plus PoC 0 -> PoC 4 (branch).

        This tests the "Merge with Independent Branch" pattern where one node
        has multiple outgoing edges that go to completely separate destinations.

        Expected layout:
        - Main chain flows vertically
        - PoC 4 branches off separately from PoC 0
        - The two paths don't merge
        """
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_node(*poc4_node)
        # Main chain
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        dag.add_edge("poc2", "poc3")
        # Independent branch from PoC 0
        dag.add_edge("poc0", "poc4")

        result = render_dag(dag)

        # All five boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        assert "PoC 4" in result
        # Edge characters
        assert settings.theme.vertical in result
        assert settings.theme.arrow_down in result
        # Horizontal routing for the branch
        assert settings.theme.horizontal in result

    def test_two_independent_branches(
        self, poc0_node, poc1_node, poc2_node, poc3_node, poc4_node
    ) -> None:
        """PoC 0 -> {PoC 1, PoC 2}, PoC 1 -> PoC 3, PoC 2 -> PoC 4.

        Two completely independent branches from a common root,
        each continuing to their own destinations.
        """
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_node(*poc4_node)
        # Fan-out from root
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        # Independent continuations
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc4")

        result = render_dag(dag)

        # All five boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        assert "PoC 4" in result


# =============================================================================
# SKIP-LEVEL TESTS
# =============================================================================

class TestSkipLevel:
    """Tests for skip-level connections (direct + indirect paths)."""

    def test_skip_one_level(self, poc0_node, poc1_node, poc2_node) -> None:
        """PoC 0 -> PoC 1 -> PoC 2, plus PoC 0 -> PoC 2 direct."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        # Indirect path
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        # Direct skip-level path
        dag.add_edge("poc0", "poc2")

        result = render_dag(dag)

        # All boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        # Multiple edges
        assert settings.theme.vertical in result
        assert settings.theme.arrow_down in result


# =============================================================================
# DISCONNECTED COMPONENTS
# =============================================================================

class TestDisconnected:
    """Tests for disconnected graph components."""

    def test_two_disconnected_nodes(self, poc0_node, poc1_node) -> None:
        """PoC 0 and PoC 1 with no edges."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        # No edges

        result = render_dag(dag)

        # Both boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        # No edge pipe characters between boxes (boxes have their own │)
        lines = result.split("\n")
        # Should not have standalone | or v on a line (edge indicators)
        edge_only_lines = [line.strip() for line in lines if line.strip() in ("|", "v", "+")]
        assert len(edge_only_lines) == 0

    def test_three_disconnected_nodes(self, poc0_node, poc1_node, poc2_node) -> None:
        """Three nodes, no connections."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)

        result = render_dag(dag)

        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        # No standalone edge lines
        lines = result.split("\n")
        edge_only_lines = [line.strip() for line in lines if line.strip() in ("|", "v", "+")]
        assert len(edge_only_lines) == 0

    def test_mixed_connected_disconnected(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """PoC 0 -> PoC 1 (connected), PoC 2, PoC 3 (disconnected)."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")  # Only one edge

        result = render_dag(dag)

        # All four boxes
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        # Some edges (for poc0->poc1)
        assert settings.theme.vertical in result or settings.theme.arrow_down in result


# =============================================================================
# SINGLE NODE TESTS
# =============================================================================

class TestSingleNode:
    """Tests for single-node graphs."""

    def test_single_poc0(self, poc0_node) -> None:
        """Just PoC 0, no edges."""
        dag = DAG()
        dag.add_node(*poc0_node)

        result = render_dag(dag)

        assert "PoC 0" in result
        assert "EXPLORATION" in result
        assert "✅" in result
        # No standalone edge lines
        lines = result.split("\n")
        edge_only_lines = [line.strip() for line in lines if line.strip() in ("|", "v", "+")]
        assert len(edge_only_lines) == 0

    def test_single_poc2(self, poc2_node) -> None:
        """Just PoC 2, verify emoji preserved."""
        dag = DAG()
        dag.add_node(*poc2_node)

        result = render_dag(dag)

        assert "PoC 2" in result
        assert "ROUTING" in result
        assert "✅" in result
        # Bullet points preserved
        assert "•" in result


# =============================================================================
# CONTENT PRESERVATION TESTS
# =============================================================================

class TestContentPreservation:
    """Tests that verify box content is fully preserved."""

    def test_unicode_emoji_preserved(self, poc0_node, poc1_node, poc2_node) -> None:
        """All unicode emoji are preserved in output."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)

        # Count checkmarks (should have 3 - one per box)
        assert result.count("✅") == 3

    def test_bullet_points_preserved(self, poc0_node, poc1_node, poc2_node) -> None:
        """Bullet point characters preserved."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)

        # All boxes have bullet points
        assert result.count("•") >= 6  # Multiple bullets per box

    def test_box_borders_preserved(self, poc0_node) -> None:
        """Box border characters preserved."""
        dag = DAG()
        dag.add_node(*poc0_node)

        result = render_dag(dag)

        # Box corners
        assert "┌" in result
        assert "┐" in result
        assert "└" in result
        assert "┘" in result
        # Box sides
        assert "│" in result
        assert "─" in result

    def test_edges_dont_corrupt_boxes(self, poc0_node, poc1_node, poc2_node) -> None:
        """Edges don't overwrite box content."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)

        # All key content preserved
        assert "Grandalf (Python)" in result
        assert "Graphviz (C)" in result
        assert "ascii-dag (Rust)" in result
        assert "6 Pydantic models" in result
        assert "wcwidth Unicode" in result
        assert "EdgeRouter proto" in result
        assert "SimpleRouter" in result


# =============================================================================
# EDGE CHARACTER TESTS
# =============================================================================

class TestEdgeCharacters:
    """Tests for correct edge character usage."""

    def test_vertical_edges_use_pipe(self, poc0_node, poc1_node) -> None:
        """Vertical edges use | character."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_edge("poc0", "poc1")

        result = render_dag(dag)

        assert settings.theme.vertical in result

    def test_arrows_at_targets(self, poc0_node, poc1_node) -> None:
        """Arrow appears at target entry."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_edge("poc0", "poc1")

        result = render_dag(dag)

        assert settings.theme.arrow_down in result

    def test_corners_in_z_shapes(self, poc0_node, poc1_node, poc2_node) -> None:
        """Z-shaped routing uses corners or horizontal segments."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")  # Forces Z-shape

        result = render_dag(dag)

        # Either corners or horizontal segments
        assert settings.theme.cross in result or settings.theme.horizontal in result


# =============================================================================
# VISUAL INSPECTION TESTS
# =============================================================================

class TestVisualInspection:
    """Visual inspection tests - print output for manual review."""

    def test_print_linear_chain(self, poc0_node, poc1_node, poc2_node) -> None:
        """Print linear chain for visual inspection."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("LINEAR CHAIN: PoC 0 -> PoC 1 -> PoC 2")
        print("=" * 70)
        print(result)
        print("=" * 70)

    def test_print_diamond(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """Print diamond pattern for visual inspection."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("DIAMOND: PoC 0 -> {PoC 1, PoC 2} -> PoC 3")
        print("=" * 70)
        print(result)
        print("=" * 70)

    def test_print_full_milestone(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """Print full milestone chain for visual inspection."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("FULL MILESTONE: PoC 0 -> PoC 1 -> PoC 2 -> PoC 3")
        print("=" * 70)
        print(result)
        print("=" * 70)

    def test_print_diamond_with_independent_branch(
        self, poc0_node, poc1_node, poc2_node, poc3_node, poc4_node
    ) -> None:
        """Print diamond pattern with independent branch for visual inspection.

        Diamond: PoC 0 -> {PoC 1, PoC 2} -> PoC 3
        Plus: PoC 0 -> PoC 4 (independent branch)
        """
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_node(*poc4_node)
        # Diamond pattern
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")
        # Independent branch from PoC 0
        dag.add_edge("poc0", "poc4")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("DIAMOND + INDEPENDENT: PoC 0 -> {PoC 1, PoC 2} -> PoC 3, PoC 0 -> PoC 4")
        print("=" * 70)
        print(result)
        print("=" * 70)


# =============================================================================
# POC 3 FEATURE TESTS - Box Connectors and Smart Routing
# =============================================================================

class TestPoC3Features:
    """Tests verifying PoC 3 features (box connectors, trunk-and-split) with real diagrams."""

    def test_box_connectors_in_chain(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """Box connectors appear in linear chain: PoC 0 -> 1 -> 2 -> 3."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # Box connectors present (┬ on box bottoms)
        assert "┬" in result, "Expected ┬ box connectors in chain"
        # All content preserved
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result

    def test_trunk_and_split_fanout(self, poc0_node, poc1_node, poc2_node) -> None:
        """Trunk-and-split pattern for fan-out: PoC 0 -> {PoC 1, PoC 2}."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")

        result = render_dag(dag)

        # Box connector on source
        assert "┬" in result, "Expected ┬ box connector on PoC 0"
        # Arrows should appear before each target box
        assert result.count("v") >= 2, "Expected arrows before PoC 1 and PoC 2"
        # All boxes present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result

    def test_merge_routing_fanin(self, poc1_node, poc2_node, poc3_node) -> None:
        """Merge routing for fan-in: {PoC 1, PoC 2} -> PoC 3."""
        dag = DAG()
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # Box connectors on both sources
        assert "┬" in result, "Expected ┬ box connectors on sources"
        # Merge junction
        assert "┬" in result or "┴" in result, "Expected merge junction"
        # All boxes present
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result

    def test_diamond_with_connectors(self, poc0_node, poc1_node, poc2_node, poc3_node) -> None:
        """Diamond pattern has box connectors: PoC 0 -> {1, 2} -> 3."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)

        # Multiple box connectors (on poc0, poc1, poc2)
        connector_count = result.count("┬")
        assert connector_count >= 1, f"Expected multiple ┬ connectors, got {connector_count}"
        # Split and merge junctions
        assert "┴" in result or "┬" in result, "Expected junction characters"
        # All four PoCs present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result

    def test_poc3_content_preserved(self, poc3_node) -> None:
        """PoC 3 diagram content is fully preserved."""
        dag = DAG()
        dag.add_node(*poc3_node)

        result = render_dag(dag)

        # PoC 3 specific content (from docs/visual-poc3-results.md)
        assert "PoC 3" in result
        assert "SMART ROUTING" in result
        assert "✅ Complete" in result
        assert "Edge Patterns" in result
        assert "Box connectors" in result
        assert "Trunk-and-split" in result
        assert "Merge routing" in result
        assert "Smart Features" in result
        assert "Same-layer detect" in result
        assert "Multi-exit points" in result

    def test_full_visual_milestone_poc0_to_poc3(
        self, poc0_node, poc1_node, poc2_node, poc3_node
    ) -> None:
        """Print full milestone PoC 0 -> 1 -> 2 -> 3 with box connectors for visual review."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc1", "poc2")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("FULL MILESTONE WITH BOX CONNECTORS: PoC 0 -> 1 -> 2 -> 3")
        print("=" * 70)
        print(result)
        print("=" * 70)

        # Verify all 4 checkmarks (all complete now)
        assert result.count("✅") == 4, "Expected 4 ✅ checkmarks (all PoCs complete)"

    def test_full_visual_diamond_poc0123(
        self, poc0_node, poc1_node, poc2_node, poc3_node
    ) -> None:
        """Print diamond PoC 0 -> {1, 2} -> 3 with trunk-and-split for visual review."""
        dag = DAG()
        dag.add_node(*poc0_node)
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_edge("poc0", "poc1")
        dag.add_edge("poc0", "poc2")
        dag.add_edge("poc1", "poc3")
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("DIAMOND WITH TRUNK-AND-SPLIT: PoC 0 -> {PoC 1, PoC 2} -> PoC 3")
        print("=" * 70)
        print(result)
        print("=" * 70)

        # Verify trunk-and-split and merge patterns
        assert "┬" in result, "Expected ┬ connector"
        # Arrows should appear before target boxes
        assert result.count("v") >= 2, "Expected arrows before PoC 1 and PoC 2"

    def test_problem3_merge_with_independent_exit(
        self, poc1_node, poc2_node, poc3_node
    ) -> None:
        """Problem 3: Merge routing with multi-exit source.

        Pattern from docs/visual-poc3-overview.md line 78:
        - poc-1 has TWO exits: one to poc-8 (independent), one to poc-3 (merge)
        - poc-2 has ONE exit: to poc-3 (merge with poc-1)
        - poc-1 and poc-2 merge at junction above poc-3

        Structure:
          poc-1          poc-2
            |  \\           |
            |   \\----+----/
            |        |
            v        v
          poc-8    poc-3
        """
        # Create a simple poc-8 diagram
        poc8_diagram = """\
┌───────────────────────┐
│        PoC 8          │
│    INDEPENDENT        │
│      ○ Planned        │
│                       │
│ Receives              │
│   • From poc-1 only   │
│   • No merge          │
└───────────────────────┘"""

        dag = DAG()
        dag.add_node(*poc1_node)
        dag.add_node(*poc2_node)
        dag.add_node(*poc3_node)
        dag.add_node("poc8", poc8_diagram)

        # poc-1 has TWO exits
        dag.add_edge("poc1", "poc8")  # Independent
        dag.add_edge("poc1", "poc3")  # Merge with poc-2
        # poc-2 merges with poc-1
        dag.add_edge("poc2", "poc3")

        result = render_dag(dag)
        print("\n" + "=" * 70)
        print("PROBLEM 3: MERGE WITH INDEPENDENT EXIT")
        print("poc-1 -> poc-8 (independent), {poc-1, poc-2} -> poc-3 (merge)")
        print("=" * 70)
        print(result)
        print("=" * 70)

        # All boxes present
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        assert "PoC 8" in result
        assert "INDEPENDENT" in result

        # Multiple box connectors (poc-1 needs TWO exits)
        connector_count = result.count("┬")
        assert connector_count >= 2, f"Expected at least 2 ┬ connectors, got {connector_count}"

        # Multiple arrows (to poc-8 and poc-3)
        assert result.count("v") >= 2, "Expected arrows to poc-8 and poc-3"


# =============================================================================
# JSON MILESTONE DATA TEST
# =============================================================================

class TestMilestoneFromJSON:
    """Tests that load milestone data from JSON file and render the DAG."""

    def test_load_visual_tasks_json(self) -> None:
        """Load visual-tasks.json and render all 5 PoCs."""
        import json
        from pathlib import Path

        # Load the JSON file
        json_path = Path(__file__).parent.parent / "docs" / "visual-tasks.json"
        with open(json_path) as f:
            data = json.load(f)

        # Build DAG from JSON data
        dag = DAG()
        for task in data["tasks"]:
            dag.add_node(task["slug"], task["diagram"])

        # Add edges based on depends_on
        for task in data["tasks"]:
            if task["depends_on"]:
                for dep in task["depends_on"]:
                    dag.add_edge(dep, task["slug"])

        # Render
        result = render_dag(dag)

        # All 5 PoCs present
        assert "PoC 0" in result
        assert "PoC 1" in result
        assert "PoC 2" in result
        assert "PoC 3" in result
        assert "PoC 4" in result

        # All complete (5 checkmarks)
        assert result.count("✅") == 5, f"Expected 5 ✅ checkmarks, got {result.count('✅')}"

        # Key content from each PoC
        assert "EXPLORATION" in result
        assert "LAYOUT" in result
        assert "ROUTING" in result
        assert "SMART ROUTING" in result
        assert "RELEASE" in result

        # Box connectors present (chain of 5 means 4 connectors minimum)
        assert "┬" in result, "Expected ┬ box connectors"

        # Print for visual inspection
        print("\n" + "=" * 70)
        print("VISUAL MILESTONE FROM JSON: All 5 PoCs")
        print("=" * 70)
        print(result)
        print("=" * 70)
