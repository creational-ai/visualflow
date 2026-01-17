"""Tests for data models."""

import pytest

from visualflow.models import Node, Edge, DAG, NodePosition, LayoutResult, EdgePath


class TestNode:
    """Tests for Node model."""

    def test_node_creation(self) -> None:
        """Node can be created with id and content."""
        node = Node(id="test", content="Hello")
        assert node.id == "test"
        assert node.content == "Hello"

    def test_node_width_single_line(self) -> None:
        """Width is length of first line."""
        node = Node(id="test", content="Hello World")
        assert node.width == 11

    def test_node_width_multiline(self) -> None:
        """Width is length of first line for multiline content."""
        content = "Line 1 longer\nLine 2\nLine 3"
        node = Node(id="test", content=content)
        assert node.width == 13  # "Line 1 longer"

    def test_node_height_single_line(self) -> None:
        """Height is 1 for single line content."""
        node = Node(id="test", content="Hello")
        assert node.height == 1

    def test_node_height_multiline(self) -> None:
        """Height is number of lines."""
        content = "Line 1\nLine 2\nLine 3"
        node = Node(id="test", content=content)
        assert node.height == 3

    def test_node_empty_content(self) -> None:
        """Empty content has zero dimensions."""
        node = Node(id="test", content="")
        assert node.width == 0
        assert node.height == 1  # Empty string splits to ['']

    def test_node_box_content(self) -> None:
        """Node with box content has correct dimensions."""
        content = "\n".join([
            "+----------+",
            "| Task A   |",
            "+----------+",
        ])
        node = Node(id="task-a", content=content)
        assert node.width == 12
        assert node.height == 3

    def test_node_width_with_emoji(self) -> None:
        """Width correctly counts emoji as 2 columns."""
        # Emoji typically occupy 2 terminal columns
        node = Node(id="test", content="Hello \U0001f389 World")
        # "Hello " (6) + "U0001f389" (2) + " World" (6) = 14 columns
        assert node.width == 14

    def test_node_width_with_cjk(self) -> None:
        """Width correctly counts CJK characters as 2 columns."""
        node = Node(id="test", content="Hello \u4e16\u754c")
        # "Hello " (6) + "\u4e16" (2) + "\u754c" (2) = 10 columns
        assert node.width == 10


class TestEdge:
    """Tests for Edge model."""

    def test_edge_creation(self) -> None:
        """Edge can be created with source and target."""
        edge = Edge(source="a", target="b")
        assert edge.source == "a"
        assert edge.target == "b"


class TestDAG:
    """Tests for DAG model."""

    def test_dag_creation_empty(self) -> None:
        """Empty DAG has no nodes or edges."""
        dag = DAG()
        assert len(dag.nodes) == 0
        assert len(dag.edges) == 0

    def test_dag_add_node(self) -> None:
        """add_node adds a node to the DAG."""
        dag = DAG()
        dag.add_node("a", "Node A")
        assert len(dag.nodes) == 1
        assert dag.nodes["a"].id == "a"
        assert dag.nodes["a"].content == "Node A"

    def test_dag_add_edge(self) -> None:
        """add_edge adds an edge to the DAG."""
        dag = DAG()
        dag.add_node("a", "Node A")
        dag.add_node("b", "Node B")
        dag.add_edge("a", "b")
        assert len(dag.edges) == 1
        assert dag.edges[0].source == "a"
        assert dag.edges[0].target == "b"

    def test_dag_get_node_exists(self) -> None:
        """get_node returns node when it exists."""
        dag = DAG()
        dag.add_node("a", "Node A")
        node = dag.get_node("a")
        assert node is not None
        assert node.id == "a"

    def test_dag_get_node_not_found(self) -> None:
        """get_node returns None when node doesn't exist."""
        dag = DAG()
        node = dag.get_node("nonexistent")
        assert node is None

    def test_dag_multiple_nodes_and_edges(self) -> None:
        """DAG can hold multiple nodes and edges."""
        dag = DAG()
        dag.add_node("a", "A")
        dag.add_node("b", "B")
        dag.add_node("c", "C")
        dag.add_edge("a", "b")
        dag.add_edge("b", "c")
        assert len(dag.nodes) == 3
        assert len(dag.edges) == 2


class TestNodePosition:
    """Tests for NodePosition model."""

    def test_node_position_creation(self) -> None:
        """NodePosition can be created with node and coordinates."""
        node = Node(id="test", content="Test")
        pos = NodePosition(node=node, x=10, y=5)
        assert pos.node == node
        assert pos.x == 10
        assert pos.y == 5


class TestLayoutResult:
    """Tests for LayoutResult model."""

    def test_layout_result_creation(self) -> None:
        """LayoutResult can be created with positions and dimensions."""
        node = Node(id="test", content="Test")
        pos = NodePosition(node=node, x=0, y=0)
        result = LayoutResult(
            positions={"test": pos},
            width=100,
            height=50,
        )
        assert len(result.positions) == 1
        assert result.width == 100
        assert result.height == 50


class TestEdgePath:
    """Tests for EdgePath model."""

    def test_edge_path_creation_empty(self) -> None:
        """EdgePath can be created with no segments."""
        path = EdgePath(source_id="a", target_id="b")
        assert path.source_id == "a"
        assert path.target_id == "b"
        assert len(path.segments) == 0

    def test_edge_path_with_segments(self) -> None:
        """EdgePath can hold line segments."""
        path = EdgePath(
            source_id="a",
            target_id="b",
            segments=[(10, 5, 10, 10), (10, 10, 20, 10)],
        )
        assert len(path.segments) == 2
        assert path.segments[0] == (10, 5, 10, 10)
