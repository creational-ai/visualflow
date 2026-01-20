"""Graph partitioning utilities for DAG organization.

Separates a DAG into connected subgraphs and standalone nodes.
"""

from collections import defaultdict

from visualflow.models import DAG, Edge


def partition_dag(dag: DAG) -> tuple[list[DAG], DAG]:
    """Partition a DAG into connected subgraphs and standalone nodes.

    Uses Union-Find algorithm to efficiently find connected components.
    A node is "standalone" if it has no edges (neither source nor target).

    Args:
        dag: The directed acyclic graph to partition

    Returns:
        Tuple of:
        - list[DAG]: Connected subgraphs, sorted by size (largest first)
        - DAG: All standalone nodes (nodes with no edges)

    Examples:
        >>> dag = DAG()
        >>> dag.add_node("a", "A")  # standalone
        >>> dag.add_node("b", "B")
        >>> dag.add_node("c", "C")
        >>> dag.add_edge("b", "c")  # connected
        >>> connected, standalones = partition_dag(dag)
        >>> len(connected)  # 1 subgraph with b->c
        1
        >>> len(standalones.nodes)  # 1 standalone node (a)
        1
    """
    if not dag.nodes:
        return [], DAG()

    # Build set of nodes that participate in edges
    nodes_with_edges: set[str] = set()
    for edge in dag.edges:
        nodes_with_edges.add(edge.source)
        nodes_with_edges.add(edge.target)

    # Identify standalone nodes (no edges)
    standalone_ids = set(dag.nodes.keys()) - nodes_with_edges

    # If no edges exist, all nodes are standalone
    if not dag.edges:
        standalones = DAG()
        for node_id in dag.nodes:
            node = dag.nodes[node_id]
            standalones.add_node(node_id, node.content)
        return [], standalones

    # Build adjacency list (undirected) for connected component detection
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in dag.edges:
        adjacency[edge.source].add(edge.target)
        adjacency[edge.target].add(edge.source)

    # Find connected components using BFS
    visited: set[str] = set()
    components: list[set[str]] = []

    for node_id in nodes_with_edges:
        if node_id in visited:
            continue

        # BFS from this node
        component: set[str] = set()
        queue = [node_id]
        while queue:
            current = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            component.add(current)
            for neighbor in adjacency[current]:
                if neighbor not in visited:
                    queue.append(neighbor)

        if component:
            components.append(component)

    # Sort components by size (largest first)
    components.sort(key=lambda c: len(c), reverse=True)

    # Build DAGs for each connected component
    subgraphs: list[DAG] = []
    for component in components:
        subgraph = DAG()
        for node_id in component:
            node = dag.nodes[node_id]
            subgraph.add_node(node_id, node.content)
        for edge in dag.edges:
            if edge.source in component and edge.target in component:
                subgraph.add_edge(edge.source, edge.target)
        subgraphs.append(subgraph)

    # Build DAG for standalone nodes
    standalones = DAG()
    for node_id in standalone_ids:
        node = dag.nodes[node_id]
        standalones.add_node(node_id, node.content)

    return subgraphs, standalones
