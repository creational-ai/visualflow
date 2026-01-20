"""Test rendering the Mission Control core milestone tasks."""

import json
from pathlib import Path

import pytest

from visualflow import DAG, render_dag, settings


@pytest.fixture
def core_tasks() -> list[dict]:
    """Load core tasks from JSON."""
    json_path = Path(__file__).parent.parent / "docs" / "core-tasks.json"
    with open(json_path) as f:
        return json.load(f)


class TestCoreMilestone:
    """Tests for rendering the core milestone DAG."""

    def test_render_full_milestone(self, core_tasks) -> None:
        """Render all tasks - render_dag auto-organizes connected vs standalone."""
        dag = DAG()

        # Add all nodes with diagrams
        for task in core_tasks:
            if task["diagram"]:
                dag.add_node(task["slug"], task["diagram"])

        # Add edges from dependencies
        for task in core_tasks:
            if task["depends_on"]:
                for dep_slug in task["depends_on"]:
                    if task["diagram"] and dep_slug in dag.nodes:
                        dag.add_edge(dep_slug, task["slug"])

        # render_dag automatically organizes:
        # - Connected subgraphs first (largest first)
        # - Standalone nodes at bottom
        result = render_dag(dag)

        print("\n" + "=" * 100)
        print(f"CORE MILESTONE ({settings.theme.__class__.__name__}): {len(dag.nodes)} tasks, {len(dag.edges)} edges")
        print("=" * 100)
        print(result)
        print("=" * 100)

        # Verify connected tasks rendered
        assert "PoC 1" in result
        assert "SCHEMA" in result
        assert "PoC 3" in result
        assert "CRUD" in result

        # Verify standalone tasks also rendered (if any exist)
        # These appear at the bottom automatically
