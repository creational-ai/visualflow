"""Tests for PoC 3: Box Connectors and Smart Routing.

Tests cover:
- Problem 1: Box connectors (on box bottom)
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

    def test_step0_visual_baseline(self) -> None:
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

    def test_step1_visual_analysis(self) -> None:
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

    def test_step2_visual_exit_points(self) -> None:
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
                box_bottom[x] = "T"  # Use T instead of unicode for visual
        print(f"Visual:  {''.join(box_bottom)}")
        print("=" * 40)

        assert len(exits_1) == 1
        assert len(exits_2) == 2
        assert len(exits_3) == 3


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

    def test_step3_visual_trunk_split(self) -> None:
        """Visual verification: trunk-split pattern renders correctly.

        Expected pattern (from overview Problem 2):
             +-------------+
             |   ROOT      |
             +------+------+
                    |
             +------+------+
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
        # After Step 6 integration, should have connector


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

    def test_step4_visual_merge_routing(self) -> None:
        """Visual verification: merge routing pattern renders correctly.

        Expected pattern (from overview Problem 3):
        +-----------+          +-----------+
        |   src-1   |          |   src-2   |
        +-----+-----+          +-----+-----+
              |                      |
              +----------+-----------+  <- MERGE
                         |
                         v
                  +-----------+
                  |   target  |
                  +-----------+
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

    def test_step5_visual_box_connectors(self) -> None:
        """Visual verification: box connectors appear on box bottom border.

        Expected pattern (from overview Problem 1):
        Before: +-------------+
        After:  +------┬------+
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
        assert "┬" in result, "Expected connector on box bottom"

        # Verify it replaced a dash, not corrupted content
        assert "TEST" in result


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

        # Content should be preserved
        assert "IMPORTANT" in result
        assert "DATA" in result
        # Connector should exist
        assert "┬" in result

    def test_render_dag_no_edges_no_connectors(self) -> None:
        """DAG without edges has no connectors."""
        dag = DAG()
        dag.add_node("a", make_test_box("SINGLE"))

        result = render_dag(dag)

        # No edges means no connectors
        assert "┬" not in result
        assert "SINGLE" in result

    def test_render_dag_backward_compatible(self) -> None:
        """render_dag still works with existing patterns."""
        dag = DAG()
        dag.add_node("a", "+-------+\n|   A   |\n+-------+")
        dag.add_node("b", "+-------+\n|   B   |\n+-------+")
        dag.add_node("c", "+-------+\n|   C   |\n+-------+")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")

        result = render_dag(dag)

        # All nodes present
        assert "A" in result
        assert "B" in result
        assert "C" in result
        # Edges exist (vertical lines)
        assert "|" in result
        # Connectors placed (new behavior)
        assert "┬" in result

    def test_step6_visual_full_integration(self) -> None:
        """Visual verification: complete diagram with all PoC 3 features.

        This test creates a diagram that exercises:
        - Problem 1: Box connectors (on box bottom)
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
        assert "┬" in result, "Expected connectors on box bottoms"

        # Verify edges exist
        assert "|" in result, "Expected vertical edge segments"


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
