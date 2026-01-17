# visualflow

ASCII DAG visualization library for rendering directed acyclic graphs as text diagrams with variable-sized boxes.

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

### Environment Variable

Set the default theme via environment variable:

```bash
export VISUALFLOW_THEME=rounded
```

Or in a `.env` file:

```
VISUALFLOW_THEME=rounded
```

Valid values: `default`, `light`, `rounded`, `heavy`

### Programmatic Configuration

```python
from visualflow import settings, HEAVY_THEME

# Set global theme
settings.theme = HEAVY_THEME

# Reset to default
settings.reset()
```

## Features

- Variable-sized boxes with any content
- Unicode support (emoji, CJK characters)
- Box connectors that integrate edges with box borders
- T-junctions for merging/splitting edges
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
