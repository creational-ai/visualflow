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
