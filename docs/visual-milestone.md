# Milestone: Visual

**Status**: Complete
**Project**: Mission Control
**Location**: `visualflow/`

---

## Executive Summary

This milestone adds visual diagram generation capabilities to Mission Control, enabling automatic ASCII visualization of task dependencies. The goal is to transform abstract task relationships into clear, readable diagrams that help users understand project structure and dependencies at a glance.

**Current State**: All PoCs complete. ASCII DAG visualization library with smart routing, theme system, 293 passing tests, and GitHub-based installation.

---

## Goal

Build a diagram generation system that visualizes Mission Control task dependencies as ASCII diagrams with variable-sized boxes.

**What This Milestone Proves**:
- Layout engines (Grandalf, Graphviz) can compute positions for our DAG structures
- Variable-sized ASCII boxes can be rendered at computed positions
- Edge routing works reliably for task dependency graphs
- The solution integrates cleanly with Mission Control's `list_tasks` MCP tool
- The architecture is flexible enough for future enhancements

**What This Milestone Does NOT Include**:
- Interactive diagram editing
- Image/SVG export (ASCII only)
- Real-time diagram updates
- Diagram persistence/caching

---

## Architecture (Implemented)

### Render Pipeline

```
Input DAG --> Layout Engine --> Edge Router --> Canvas --> ASCII Output
```

**Layout Engines** (compute node positions):
- **Grandalf** - Pure Python Sugiyama, fast (~0.03s), positions only
- **Graphviz** - Subprocess, slower (~2.79s), positions + edge hints

**Edge Router** (compute edge paths between boxes):
- **SimpleRouter** - Geometric routing with smart patterns:
  - Trunk-and-split for fan-out (1→N)
  - Merge routing for fan-in (N→1)
  - Box connectors at exit points

**Canvas** - Places pre-made boxes at positions, draws edges, fixes junctions

### Theme System

Four pre-built themes configurable via `.env`:

```bash
# .env
VISUALFLOW_THEME=ROUNDED  # DEFAULT, LIGHT, ROUNDED, HEAVY
```

| Theme | Vertical | Horizontal | Corners | Arrow |
|-------|----------|------------|---------|-------|
| DEFAULT | `\|` | `-` | `┌┐└┘` | `v` |
| LIGHT | `│` | `─` | `┌┐└┘` | `▼` |
| ROUNDED | `│` | `─` | `╭╮╰╯` | `▼` |
| HEAVY | `┃` | `━` | `┏┓┗┛` | `▼` |

### Technology Stack

- **Python 3.14** with uv package manager
- **Pydantic** for data models with validation
- **wcwidth** for Unicode width calculation (emoji, CJK)
- **python-dotenv** for .env configuration
- **pytest** with 293 tests, >90% coverage

---

## Implementation Phases

### PoC 0: Exploration ✅ Complete

**Objective**: Evaluate layout engines to determine optimal combination.

**Results**:
- Evaluated Grandalf, Graphviz, ascii-dag
- Selected two-engine architecture:
  - Grandalf: Fast positioning (~0.03s)
  - Graphviz: Edge routing hints (optional)
- ascii-dag rejected (Rust compilation complexity)

### PoC 1: Layout ✅ Complete

**Objective**: Build foundation with layout engine abstraction and canvas rendering.

**Delivered**:
- 6 Pydantic data models (DAG, Node, Edge, LayoutResult, NodePosition, EdgePath)
- LayoutEngine protocol with GrandalfEngine and GraphvizEngine
- Canvas class with box placement
- wcwidth Unicode support for emoji/CJK width

### PoC 2: Routing ✅ Complete

**Objective**: Implement edge routing to connect boxes.

**Delivered**:
- EdgeRouter protocol with SimpleRouter implementation
- Canvas.draw_edge() for path rendering
- All 7 test fixtures passing
- 0.002s render performance

### PoC 3: Smart Routing ✅ Complete

**Objective**: Implement smart routing patterns for cleaner diagrams.

**Delivered**:
- Box connectors (┬) at exit points
- Trunk-and-split pattern for fan-out scenarios
- Merge routing for fan-in scenarios
- fix_junctions() post-processing for correct junction characters
- EdgeTheme system with 4 presets (DEFAULT, LIGHT, ROUNDED, HEAVY)
- .env configuration via VISUALFLOW_THEME

### PoC 4: GitHub Release ✅ Complete

**Objective**: Package for GitHub-based installation.

**Delivered**:
- MIT LICENSE file
- pyproject.toml with authors, license, keywords
- README with GitHub install, themes, .env config
- Git tag v0.1.0

**Install via**:
```bash
uv add git+https://github.com/creational-ai/visualflow.git
```

---

## Success Metrics

### Technical Quality ✅

- **Test Coverage**: 293 tests passing, >90% coverage
- **Layout Accuracy**: 100% correct topology
- **Performance**: 0.002s render (target was <1s)

### Usability

- **Readability**: Diagrams understandable without explanation
- **Theme Support**: 4 built-in themes, configurable via .env

---

## File Structure

```
visualflow/
├── pyproject.toml           # uv project config
├── .env                     # Theme configuration
├── src/visualflow/
│   ├── __init__.py          # Public API: render_dag(), DAG, themes
│   ├── models.py            # Pydantic models, EdgeTheme
│   ├── settings.py          # Global settings, .env loading
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── base.py          # LayoutEngine protocol
│   │   ├── grandalf.py      # GrandalfEngine
│   │   └── graphviz.py      # GraphvizEngine
│   ├── render/
│   │   ├── __init__.py
│   │   └── canvas.py        # Canvas, box/edge rendering
│   └── routing/
│       ├── __init__.py
│       └── simple.py        # SimpleRouter
├── tests/
│   ├── conftest.py          # 7 test fixtures
│   ├── test_canvas.py
│   ├── test_grandalf.py
│   ├── test_graphviz.py
│   ├── test_integration.py
│   ├── test_real_diagrams.py
│   ├── test_fanout_patterns.py
│   ├── test_routing.py
│   └── test_core_milestone.py
└── docs/
    ├── visual-milestone.md  # This document
    ├── architecture.md
    └── visual-poc*-*.md     # PoC documentation
```

---

## Usage

```python
from visualflow import DAG, render_dag

# Create DAG
dag = DAG()
dag.add_node("task-1", "┌─────────┐\n│ Task 1  │\n└─────────┘")
dag.add_node("task-2", "┌─────────┐\n│ Task 2  │\n└─────────┘")
dag.add_edge("task-1", "task-2")

# Render
print(render_dag(dag))
```

**Theme Override**:
```python
from visualflow import render_dag, HEAVY_THEME

print(render_dag(dag, theme=HEAVY_THEME))
```

**Global Theme**:
```python
from visualflow import settings, ROUNDED_THEME

settings.theme = ROUNDED_THEME
# All subsequent render_dag() calls use ROUNDED_THEME
```

---

## Related Documents

- [Architecture](./architecture.md) - Detailed component design
- [PoC 0 Results](./visual-poc0-results.md) - Engine evaluation
- [PoC 1 Implementation](./visual-poc1-implementation.md) - Layout foundation
- [PoC 2 Implementation](./visual-poc2-implementation.md) - Edge routing

---

*Last Updated*: January 2026
