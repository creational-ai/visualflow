"""Test fan-out patterns with real Mission Control task data.

Tests basic fan-out routing:
- 1-1: Single source → single target
- 1-2: Single source → two targets
- 1-3: Single source → three targets
"""

import json
from pathlib import Path

import pytest

from visualflow import DAG, render_dag


@pytest.fixture
def core_tasks() -> dict[str, dict]:
    """Load core tasks as dict keyed by slug."""
    json_path = Path(__file__).parent.parent / "docs" / "core-tasks.json"
    with open(json_path) as f:
        tasks = json.load(f)
    return {t["slug"]: t for t in tasks}


class TestFanOutPatterns:
    """Test fan-out routing with increasing target counts."""

    def test_fanout_1_to_1(self, core_tasks) -> None:
        """1-1: Single source → single target (poc-1 → poc-8)."""
        dag = DAG()

        # poc-1 (Schema) → poc-8 (Abstraction)
        dag.add_node("poc-1", core_tasks["poc-1"]["diagram"])
        dag.add_node("poc-8", core_tasks["poc-8"]["diagram"])
        dag.add_edge("poc-1", "poc-8")

        result = render_dag(dag)

        print("\n" + "=" * 80)
        print("FAN-OUT 1→1: poc-1 (Schema) → poc-8 (Abstraction)")
        print("=" * 80)
        print(result)
        print("=" * 80)

        assert "PoC 1" in result
        assert "PoC 8" in result
        assert "SCHEMA" in result
        assert "ABSTRACTION" in result
        # Single vertical path
        assert "|" in result
        assert "v" in result

    def test_fanout_1_to_2(self, core_tasks) -> None:
        """1-2: Single source → two targets (poc-3 → {poc-5, poc-6})."""
        dag = DAG()

        # poc-3 (CRUD) → poc-5 (Workflow), poc-6 (Analysis)
        dag.add_node("poc-3", core_tasks["poc-3"]["diagram"])
        dag.add_node("poc-5", core_tasks["poc-5"]["diagram"])
        dag.add_node("poc-6", core_tasks["poc-6"]["diagram"])
        dag.add_edge("poc-3", "poc-5")
        dag.add_edge("poc-3", "poc-6")

        result = render_dag(dag)

        print("\n" + "=" * 80)
        print("FAN-OUT 1→2: poc-3 (CRUD) → {poc-5 (Workflow), poc-6 (Analysis)}")
        print("=" * 80)
        print(result)
        print("=" * 80)

        assert "PoC 3" in result
        assert "PoC 5" in result
        assert "PoC 6" in result
        assert "CRUD" in result
        assert "WORKFLOW" in result
        assert "ANALYSIS" in result
        # Should have trunk-and-split pattern
        assert "┬" in result  # Box connector
        assert result.count("v") >= 2  # Two arrows

    def test_fanout_1_to_3(self, core_tasks) -> None:
        """1-3: Single source → three targets (poc-9 → {poc-11, poc-12, pydantic})."""
        dag = DAG()

        # poc-9 (Migration) → poc-11 (Dev Activity), poc-12 (Milestones DB), pydantic
        dag.add_node("poc-9", core_tasks["poc-9"]["diagram"])
        dag.add_node("poc-11", core_tasks["poc-11"]["diagram"])
        dag.add_node("poc-12", core_tasks["poc-12"]["diagram"])
        dag.add_node("pydantic", core_tasks["pydantic"]["diagram"])
        dag.add_edge("poc-9", "poc-11")
        dag.add_edge("poc-9", "poc-12")
        dag.add_edge("poc-9", "pydantic")

        result = render_dag(dag)

        print("\n" + "=" * 80)
        print("FAN-OUT 1→3: poc-9 (Migration) → {poc-11, poc-12, pydantic}")
        print("=" * 80)
        print(result)
        print("=" * 80)

        assert "PoC 9" in result
        assert "PoC 11" in result
        assert "PoC 12" in result
        assert "MIGRATION" in result
        assert "DEV ACTIVITY" in result
        assert "MILESTONES DB" in result
        assert "PYDANTIC" in result
        # Should have box connector and multiple arrows
        assert "┬" in result  # Box connector
        assert result.count("v") >= 3  # Three arrows
