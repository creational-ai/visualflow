# visualflow

ASCII DAG visualization library for rendering directed acyclic graphs as text diagrams with variable-sized boxes.

## Visual Milestone Example

Boxes can contain anything: status indicators, bullet points, emoji (✅), Unicode symbols (•, ─, │), multi-line content. This is the actual task data from this project:

```bash
# .env
VISUALFLOW_THEME=ROUNDED
```

```
┌───────────────────────────┐
│          PoC 0            │
│       EXPLORATION         │
│       ✅ Complete         │
│                           │
│ Engines Evaluated         │
│   • Grandalf (Python)     │
│   • Graphviz (C)          │
│   • ascii-dag (Rust)      │
│                           │
│ Decision                  │
│   • 2 engines selected    │
│   • Grandalf: positioning │
│   • Graphviz: edge hints  │
└─────────────┬─────────────┘
              │
              │
              ▼
  ┌───────────────────────┐
  │        PoC 1          │
  │        LAYOUT         │
  │      ✅ Complete      │
  │                       │
  │ Data Models           │
  │   • 6 Pydantic models │
  │   • wcwidth Unicode   │
  │                       │
  │ Engines               │
  │   • Grandalf (fast)   │
  │   • Graphviz (CLI)    │
  │                       │
  │ Architecture          │
  │   • Protocol pattern  │
  │   • Canvas rendering  │
  └───────────┬───────────┘
              │
              │
              ▼
  ┌───────────────────────┐
  │        PoC 2          │
  │       ROUTING         │
  │     ✅ Complete       │
  │                       │
  │ Capabilities          │
  │   • Edge routing      │
  │   • Unicode (emoji)   │
  │   • All 7 fixtures    │
  │                       │
  │ Architecture          │
  │   • EdgeRouter proto  │
  │   • SimpleRouter      │
  │   • Canvas.draw_edge  │
  │                       │
  │ Performance           │
  │   • 0.002s render     │
  └───────────┬───────────┘
              │
              │
              ▼
  ┌───────────────────────┐
  │        PoC 3          │
  │     SMART ROUTING     │
  │      ✅ Complete      │
  │                       │
  │ Edge Patterns         │
  │   • Box connectors    │
  │   • Trunk-and-split   │
  │   • Merge routing     │
  │                       │
  │ Theme System          │
  │   • 4 presets         │
  │   • .env config       │
  │   • fix_junctions()   │
  └───────────┬───────────┘
              │
              │
              ▼
   ┌─────────────────────┐
   │       PoC 4         │
   │       RELEASE       │
   │    ✅ Complete      │
   │                     │
   │ Packaging           │
   │   • MIT License     │
   │   • Metadata        │
   │                     │
   │ Documentation       │
   │   • GitHub install  │
   │   • Themes docs     │
   │   • .env config     │
   │                     │
   │ Release             │
   │   • v0.1.0 tag      │
   │   • Versioned deps  │
   └─────────────────────┘
```

*This is the actual visual milestone from Mission Control, rendered by visualflow from [docs/visual-tasks.json](docs/visual-tasks.json).*

## Installation

### From GitHub (recommended)

```bash
# With uv
uv add git+https://github.com/creational-ai/visualflow.git

# With pip
pip install git+https://github.com/creational-ai/visualflow.git

# Specific version
uv add git+https://github.com/creational-ai/visualflow.git@v0.1.0
```

### For Development

```bash
git clone https://github.com/creational-ai/visualflow.git
cd visualflow
uv sync --all-extras
```

## Usage

```python
from visualflow import DAG, render_dag

# Create a DAG
dag = DAG()

# Add nodes with pre-made ASCII boxes
dag.add_node('a', '''┌─────────┐
│  Node A │
└─────────┘''')

dag.add_node('b', '''┌─────────┐
│  Node B │
└─────────┘''')

dag.add_node('c', '''┌─────────┐
│  Node C │
└─────────┘''')

# Add edges
dag.add_edge('a', 'b')
dag.add_edge('a', 'c')

# Render to text
print(render_dag(dag))
```

Output:
```
                   ┌─────────┐
                   │  Node A │
                   └────┬────┘
                        │
                        │
         ╭──────────────┴───────────────╮
         │                              │
         │                              │
         ▼                              ▼
    ┌─────────┐                    ┌─────────┐
    │  Node B │                    │  Node C │
    └─────────┘                    └─────────┘
```

## Themes

visualflow includes 4 built-in themes for edge rendering:

| Theme | Vertical | Horizontal | Corners | Arrow |
|-------|----------|------------|---------|-------|
| `DEFAULT` | `\|` | `-` | `╭╮╰╯` | `v` |
| `LIGHT` | `│` | `─` | `┌┐└┘` | `▼` |
| `ROUNDED` | `│` | `─` | `╭╮╰╯` | `▼` |
| `HEAVY` | `┃` | `━` | `┏┓┗┛` | `▼` |

### Using Themes

```python
from visualflow import DAG, render_dag, HEAVY_THEME, ROUNDED_THEME

# Pass theme to render_dag
print(render_dag(dag, theme=HEAVY_THEME))

# Or set global theme
from visualflow import settings
settings.theme = ROUNDED_THEME
print(render_dag(dag))  # Uses ROUNDED_THEME
```

## Configuration

```python
from visualflow import settings, HEAVY_THEME

# Set global theme
settings.theme = HEAVY_THEME

# Reset to default
settings.reset()
```

## Graph Organization

`render_dag()` automatically organizes mixed graphs:
- Connected subgraphs render first (largest first)
- Standalone nodes render at the bottom

```python
from visualflow import DAG, render_dag

dag = DAG()

# Connected subgraph (A -> B -> C)
dag.add_node('a', '┌───┐\n│ A │\n└───┘')
dag.add_node('b', '┌───┐\n│ B │\n└───┘')
dag.add_node('c', '┌───┐\n│ C │\n└───┘')
dag.add_edge('a', 'b')
dag.add_edge('b', 'c')

# Standalone nodes (no edges)
dag.add_node('x', '┌───┐\n│ X │\n└───┘')
dag.add_node('y', '┌───┐\n│ Y │\n└───┘')

print(render_dag(dag))
# Connected chain (A->B->C) renders first
# Standalones (X, Y) render at bottom
```

### Advanced: partition_dag()

For custom rendering of disconnected components:

```python
from visualflow import DAG, partition_dag

dag = DAG()
# ... add nodes and edges ...

# Returns (list[DAG], DAG)
# - subgraphs: connected components sorted by size (largest first)
# - standalones: DAG containing only standalone nodes
subgraphs, standalones = partition_dag(dag)

# Custom rendering logic
for i, subgraph in enumerate(subgraphs):
    print(f"=== Subgraph {i+1} ({len(subgraph.nodes)} nodes) ===")
    print(render_dag(subgraph))

if standalones.nodes:
    print("=== Standalone Nodes ===")
    print(render_dag(standalones))
```

## Features

- Variable-sized boxes with any content
- Unicode support (emoji, CJK characters)
- Box connectors that integrate edges with box borders
- T-junctions for merging/splitting edges
- Smart graph organization (connected subgraphs first, standalones at bottom)
- `partition_dag()` for advanced custom rendering
- 4 built-in themes (DEFAULT, LIGHT, ROUNDED, HEAVY)
- Environment-based configuration via `.env`
- Automatic layout via Sugiyama algorithm (Grandalf)

## Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run with coverage
uv run pytest --cov=src tests/
```

### Visual Diagram Tests

The `test_real_diagrams.py` suite uses actual PoC diagrams to test all routing patterns.

```bash
# Run real diagram tests
uv run pytest tests/test_real_diagrams.py -v

# Run with visual output (see the rendered diagrams)
uv run pytest tests/test_real_diagrams.py -v -s

# Run only the visual inspection tests (prints diagrams to console)
uv run pytest tests/test_real_diagrams.py::TestVisualInspection -v -s
```

## Architecture

```
Input DAG -> Layout Engine -> Edge Router -> Canvas -> Text Output
```

- **Layout Engine**: Grandalf (Sugiyama algorithm) computes node positions
- **Edge Router**: SimpleRouter computes edge paths with Z-shaped routing
- **Canvas**: Places boxes and draws edges with box-drawing characters

## License

MIT License - see [LICENSE](LICENSE) for details.
