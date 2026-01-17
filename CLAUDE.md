# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**visualflow** is a Python library for generating ASCII diagrams of directed acyclic graphs with variable-sized boxes. Spin-off from Mission Control to handle task dependency visualization.

## Development Commands

Package manager: `uv` - **always use `uv run` prefix for commands**

```bash
# Run all tests
uv run pytest tests/

# Run with coverage
uv run pytest --cov=src tests/

# Run specific test file
uv run pytest tests/test_grandalf.py

# Run tests matching pattern
uv run pytest tests/ -k simple_chain

# Sync dependencies
uv sync --all-extras
```

## Architecture

### Two-Engine + Pluggable Design

```
Input DAG → Layout Engine → Edge Router → Canvas → ASCII Output
```

**Layout Engines** (compute node positions):
- **Grandalf** (`src/visualflow/engines/grandalf.py`) - Pure Python Sugiyama, fast (~0.03s), positions only
- **Graphviz** (`src/visualflow/engines/graphviz.py`) - Subprocess, slower (~2.79s), positions + edge hints

**Edge Routers** (compute edge paths between boxes):
- **Simple Router** - Geometric Z-shaped routing
- **Graphviz Router** - Uses spline points from Graphviz output

**Canvas** - Places pre-made boxes at positions, draws edges

### Key Data Flow

1. Nodes contain pre-made ASCII boxes (complete with borders from Mission Control's `task.diagram` field)
2. Layout engine computes (x, y) positions for each box
3. Edge router computes line segments between boxes
4. Canvas assembles final ASCII string

### Core Data Models (planned in `src/visualflow/models.py`)

- `Node` - Contains complete ASCII box content, calculates width/height from content
- `Edge` - Directed (source, target) pair
- `DAG` - Container with `add_node()` and `add_edge()` methods
- `LayoutResult` - Engine output: positions dict + canvas dimensions
- `EdgePath` - Router output: line segments as (x1, y1, x2, y2) tuples

## Test Scenarios

Seven fixtures in `tests/conftest.py` cover all edge cases:
1. `simple_chain` - A → B → C (vertical alignment)
2. `diamond` - Converging paths
3. `multiple_roots` - A → C, B → C
4. `skip_level` - Mixed depth connections (routing challenge)
5. `wide_graph` - 1 → 4 children (horizontal spread)
6. `deep_graph` - 6 vertical levels
7. `complex_graph` - Real-world combination

## Key Documentation

- `docs/architecture.md` - Final design spec, component interfaces, implementation order
- `docs/visual-poc0-results.md` - PoC 0 findings (engine comparison)
- `docs/visual-poc1-implementation.md` - PoC 1 detailed plan

## Grandalf Integration Notes

Grandalf requires a `view` object on each Vertex:
```python
class VertexView:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.xy: tuple[float, float] = (0.0, 0.0)  # Set by layout
```

Layout computation:
```python
sug = SugiyamaLayout(graph.C[0])  # First connected component
sug.init_all()
sug.draw()
# Positions now in vertex.view.xy as floats
```

Grandalf does NOT provide edge routing - must compute separately.

## Unicode Support

- **PoC 1**: Emoji/wide character width - uses `wcwidth` for accurate width calculation in `Node.width`
- **PoC 2**: Rich edge characters - rounded corners (`╭╮╰╯`), double lines (`║═`), arrows (`→▼`)

See `docs/architecture.md` for details.

---

## Mission Control Integration

**This project is the `visual` milestone under Mission Control.**

When using Mission Control MCP tools (`mcp__mission-control__*`) to manage tasks, milestones, or project status, you are acting as the **PM (Project Manager) role**. Read these docs to understand the workflow, timestamp conventions, and scope:

- **Project Slug:** `mission-control`
- **Milestone Slug:** `visual`
- **Role:** PM (Project Manager)
- **Read 1st:** [PM_GUIDE.md](file:///Users/docchang/Development/Mission%20Control/docs/PM_GUIDE.md)
- **Read 2nd:** [MCP_TOOLS_REFERENCE.md](file:///Users/docchang/Development/Mission%20Control/docs/MCP_TOOLS_REFERENCE.md)

**IMPORTANT: Do NOT update project-level fields** (`update_project` for phase, next_action, notes, etc.). This repo is a milestone within Mission Control, not a standalone project. Only update:
- Tasks within the `visual` milestone (`create_task`, `update_task`, `complete_task`)
- The `visual` milestone itself (`update_milestone`, `complete_milestone`)

---
