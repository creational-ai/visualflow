"""Integration tests for end-to-end rendering."""

import pytest

from visualflow import render_dag, GrandalfEngine, GraphvizEngine
from tests.fixtures import (
    create_simple_chain,
    create_diamond,
    create_wide_fanout,
    create_merge_branch,
    create_skip_level,
    create_standalone,
    create_complex_graph,
)


class TestRenderDagGrandalf:
    """Integration tests using GrandalfEngine."""

    def test_render_simple_chain(self) -> None:
        """Render simple chain produces output."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "Task A" in result
        assert "Task B" in result
        assert "Task C" in result

    def test_render_diamond(self) -> None:
        """Render diamond produces output."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 1" in result
        assert "PoC 3" in result

    def test_render_wide_fanout(self) -> None:
        """Render wide fanout produces output."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 3" in result

    def test_render_merge_branch(self) -> None:
        """Render merge branch produces output."""
        dag = create_merge_branch()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 1" in result
        assert "PoC 8" in result

    def test_render_skip_level(self) -> None:
        """Render skip level produces output."""
        dag = create_skip_level()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "Root A" in result
        assert "Child C1" in result
        assert "Child C2" in result

    def test_render_standalone(self) -> None:
        """Render standalone produces output."""
        dag = create_standalone()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "STRUCTURED TEXT" in result
        assert "DELETE TOOLS" in result

    def test_render_complex_graph(self) -> None:
        """Render complex graph produces output."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        assert result
        assert "PoC 1" in result
        assert "PoC 14" in result

    def test_render_empty_dag(self) -> None:
        """Render empty DAG returns empty string."""
        from visualflow.models import DAG
        dag = DAG()
        result = render_dag(dag, GrandalfEngine())
        assert result == ""


@pytest.mark.skipif(
    not GraphvizEngine.is_available(),
    reason="Graphviz not installed",
)
class TestRenderDagGraphviz:
    """Integration tests using GraphvizEngine."""

    def test_render_simple_chain(self) -> None:
        """Render simple chain produces output."""
        dag = create_simple_chain()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "Task A" in result

    def test_render_diamond(self) -> None:
        """Render diamond produces output."""
        dag = create_diamond()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "PoC 1" in result

    def test_render_wide_fanout(self) -> None:
        """Render wide fanout produces output."""
        dag = create_wide_fanout()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "PoC 3" in result

    def test_render_merge_branch(self) -> None:
        """Render merge branch produces output."""
        dag = create_merge_branch()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "PoC 1" in result

    def test_render_skip_level(self) -> None:
        """Render skip level produces output."""
        dag = create_skip_level()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "Root A" in result

    def test_render_standalone(self) -> None:
        """Render standalone produces output."""
        dag = create_standalone()
        result = render_dag(dag, GraphvizEngine())
        assert result
        assert "STRUCTURED TEXT" in result

    def test_render_complex_graph(self) -> None:
        """Render complex graph produces output."""
        dag = create_complex_graph()
        result = render_dag(dag, GraphvizEngine())
        assert result


class TestRenderDagDefaultEngine:
    """Tests for render_dag with default engine."""

    def test_default_engine_is_grandalf(self) -> None:
        """Default engine is GrandalfEngine."""
        dag = create_simple_chain()
        result = render_dag(dag)
        assert result
        assert "Task A" in result


class TestRenderDagWithEdges:
    """Integration tests for render_dag with edge routing."""

    def test_simple_chain_has_edges(self) -> None:
        """Simple chain renders with edge characters."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        # Should have vertical edge characters
        assert "|" in result or "v" in result

    def test_diamond_has_edges(self) -> None:
        """Diamond pattern renders with edge characters."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        # Should have edge characters
        assert "|" in result or "-" in result or "v" in result

    def test_render_with_explicit_router(self) -> None:
        """render_dag works with explicitly provided router."""
        from visualflow.routing import SimpleRouter
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine(), SimpleRouter())
        assert result
        assert "Task A" in result

    def test_render_preserves_box_content(self) -> None:
        """Edges do not corrupt box content."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        # All box content should be intact
        assert "Task A" in result
        assert "Task B" in result
        assert "Task C" in result

    def test_all_fixtures_render_with_edges(self) -> None:
        """All 7 fixtures render successfully with edges."""
        fixtures = [
            create_simple_chain(),
            create_diamond(),
            create_wide_fanout(),
            create_merge_branch(),
            create_skip_level(),
            create_standalone(),
            create_complex_graph(),
        ]
        for dag in fixtures:
            result = render_dag(dag, GrandalfEngine())
            assert result  # Non-empty output


class TestVisualInspectionWithEdges:
    """Visual inspection tests with edges - for manual review."""

    def test_print_simple_chain_with_edges(self) -> None:
        """Print simple chain with edges for visual inspection."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Simple Chain with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_diamond_with_edges(self) -> None:
        """Print diamond with edges for visual inspection."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Diamond with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_wide_fanout_with_edges(self) -> None:
        """Print wide fanout with edges for visual inspection."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Wide Fanout with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_complex_with_edges(self) -> None:
        """Print complex graph with edges for visual inspection."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Complex Graph with Edges:")
        print("=" * 60)
        print(result)
        print("=" * 60)


class TestVisualInspection:
    """Visual inspection tests - always pass, output for manual review."""

    def test_print_simple_chain(self) -> None:
        """Print simple chain for visual inspection."""
        dag = create_simple_chain()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Simple Chain (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_diamond(self) -> None:
        """Print diamond for visual inspection."""
        dag = create_diamond()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Diamond (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_wide_fanout(self) -> None:
        """Print wide fanout for visual inspection."""
        dag = create_wide_fanout()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Wide Fanout (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)

    def test_print_complex(self) -> None:
        """Print complex graph for visual inspection."""
        dag = create_complex_graph()
        result = render_dag(dag, GrandalfEngine())
        print("\n" + "=" * 60)
        print("Complex Graph (Grandalf):")
        print("=" * 60)
        print(result)
        print("=" * 60)


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
