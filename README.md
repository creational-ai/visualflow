# visualflow

DAG visualization library for rendering directed acyclic graphs as text diagrams with variable-sized boxes.

## Installation

```bash
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
           └─────────┘
    ┌--------------------┐
    v                    v
┌─────────┐          ┌─────────┐
│  Node B │          │  Node C │
└─────────┘          └─────────┘
```

## Features

- Variable-sized boxes with any content
- Unicode support (emoji, CJK characters)
- Box-drawing corners (`┌ ┐ └ ┘`) for clean routing
- T-junctions (`┬ ┴ ├ ┤`) for merging edges
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

Visual inspection tests include:
- `test_print_linear_chain` - PoC 0 → PoC 1 → PoC 2
- `test_print_diamond` - Fan-out and merge pattern
- `test_print_full_milestone` - Complete 4-node chain

### Test Categories

| Test Class | Description |
|------------|-------------|
| `TestLinearChain` | Vertical chains (2, 3, 4 nodes) |
| `TestFanOut` | One-to-many patterns |
| `TestFanIn` | Many-to-one merges |
| `TestDiamondPattern` | Fan-out + fan-in |
| `TestSkipLevel` | Mixed depth connections |
| `TestDisconnected` | Multiple components |
| `TestSingleNode` | Single node rendering |
| `TestContentPreservation` | Unicode, emoji, box borders |
| `TestEdgeCharacters` | Pipes, arrows, corners |
| `TestVisualInspection` | Print diagrams for review |

## Architecture

```
Input DAG → Layout Engine → Edge Router → Canvas → Text Output
```

- **Layout Engine**: Grandalf (Sugiyama algorithm) computes node positions
- **Edge Router**: SimpleRouter computes edge paths with Z-shaped routing
- **Canvas**: Places boxes and draws edges with box-drawing characters
