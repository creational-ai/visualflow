"""Test rendering the Mission Control core milestone tasks."""

import json
from pathlib import Path

import pytest

from visualflow import DAG, render_dag


@pytest.fixture
def core_tasks() -> list[dict]:
    """Load core tasks from JSON."""
    json_path = Path(__file__).parent.parent / "docs" / "core-tasks.json"
    with open(json_path) as f:
        return json.load(f)


def separate_connected_and_standalone(tasks: list[dict]) -> tuple[list[dict], list[dict]]:
    """Separate tasks into connected (in dependency graph) and standalone.

    Connected: has depends_on OR is depended upon by another task
    Standalone: no depends_on AND no other task depends on it
    """
    # Build set of all slugs that are depended upon
    depended_upon = set()
    for task in tasks:
        if task["depends_on"]:
            for dep in task["depends_on"]:
                depended_upon.add(dep)

    connected = []
    standalone = []

    for task in tasks:
        has_dependencies = bool(task["depends_on"])
        is_depended_upon = task["slug"] in depended_upon

        if has_dependencies or is_depended_upon:
            connected.append(task)
        else:
            standalone.append(task)

    return connected, standalone


class TestCoreMilestone:
    """Tests for rendering the core milestone DAG."""

    def test_render_main_diagram(self, core_tasks) -> None:
        """Render the main connected dependency graph."""
        connected, standalone = separate_connected_and_standalone(core_tasks)

        dag = DAG()

        # Add nodes with diagrams
        for task in connected:
            if task["diagram"]:
                dag.add_node(task["slug"], task["diagram"])

        # Add edges
        for task in connected:
            if task["depends_on"]:
                for dep_slug in task["depends_on"]:
                    if task["diagram"] and dep_slug in dag.nodes:
                        dag.add_edge(dep_slug, task["slug"])

        result = render_dag(dag)

        print("\n" + "=" * 100)
        print(f"MAIN DIAGRAM: {len(dag.nodes)} connected tasks, {len(dag.edges)} edges")
        print(f"(Excluded {len(standalone)} standalone tasks)")
        print("=" * 100)
        print(result)
        print("=" * 100)

        # Verify key content from connected tasks
        assert "PoC 1" in result
        assert "SCHEMA" in result
        assert "PoC 3" in result
        assert "CRUD" in result

    def test_render_standalone_tasks(self, core_tasks) -> None:
        """Render standalone tasks (no dependencies, not depended upon)."""
        connected, standalone = separate_connected_and_standalone(core_tasks)

        # Filter to those with diagrams
        standalone_with_diagrams = [t for t in standalone if t["diagram"]]

        if not standalone_with_diagrams:
            print("\n" + "=" * 100)
            print("STANDALONE TASKS: None")
            print("=" * 100)
            return

        dag = DAG()
        for task in standalone_with_diagrams:
            dag.add_node(task["slug"], task["diagram"])

        # No edges for standalone tasks

        result = render_dag(dag)

        print("\n" + "=" * 100)
        print(f"STANDALONE TASKS: {len(dag.nodes)} tasks (no dependencies)")
        print("=" * 100)
        print(result)
        print("=" * 100)

        # Verify standalone tasks rendered (check diagram content, not task name)
        assert "STRUCTURED TEXT FIELDS" in result or "DELETE TOOLS" in result
