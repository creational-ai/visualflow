# visualflow

ASCII DAG visualization library for rendering directed acyclic graphs as text diagrams with variable-sized boxes.

## Visual Milestone Example

Boxes can contain anything: status indicators, bullet points, emoji (✅), Unicode symbols (•, ─, │), multi-line content.

```bash
# .env
VISUALFLOW_THEME=ROUNDED
```

```
                           ┌─────────────────────────┐                                            ┌─────────────────────────┐
                           │        PoC 2            │                                            │        PoC 1            │
                           │        SERVER           │                                            │        SCHEMA           │
                           │      ✅ Complete        │                                            │      ✅ Complete        │
                           │                         │                                            │                         │
                           │ Transport               │                                            │ Database                │
                           │   • STDIO (prod)        │                                            │   • projects (18 cols)  │
                           │   • HTTP (test)         │                                            │   • project_history     │
                           │                         │                                            │                         │
                           │ Tools                   │                                            │ Infrastructure          │
                           │   • ping                │                                            │   • config.py           │
                           │   • list_projects       │                                            │   • db.py (client)      │
                           └────────────┬────────────┘                                            │   • seed_data.py        │
                                        │                                                         └────────────┬────────────┘
                                        │                                                                      │
                                        │                                                                      │
                                        ├──────────────────────────────────────────────────────────────────────┤
                                        │                                                                      │
                                        │                                                                      │
                                        ▼                                                                      ▼
                           ┌─────────────────────────┐                                            ┌─────────────────────────┐
                           │        PoC 3            │                                            │        PoC 8            │
                           │         CRUD            │                                            │      ABSTRACTION        │
                           │      ✅ Complete        │                                            │      ✅ Complete        │
                           │                         │                                            │                         │
                           │ Tools                   │                                            │ Adapters                │
                           │   • list_projects       │                                            │   • SupabaseAdapter     │
                           │   • get_project         │                                            │   • PostgresAdapter     │
                           │   • create_project      │                                            │                         │
                           │   • update_project      │                                            │ Patterns                │
                           │                         │                                            │   • Protocol typing     │
                           │ Patterns                │                                            │   • Dual-function       │
                           │   • ToolResponse<T>     │                                            │   • Parametrized tests  │
                           │   • Auto-slug           │                                            └────────────┬────────────┘
                           └────────────┬────────────┘                                                         │
                                        │                                                                      │
                                        │                                                                      │
                 ╭──────────────────────┴───────────────────────╮                                              │
                 │                                              │                                              │
                 │                                              │                                              │
                 │                                              ▼                                              ▼
                 ▼                                 ┌─────────────────────────┐                    ┌─────────────────────────┐
    ┌─────────────────────────┐                    │      BUG FIXES          │                    │        PoC 9            │
    │        PoC 6            │                    │     2025-12-29          │                    │       MIGRATION         │
    │       ANALYSIS          │                    │      ✅ Complete        │                    │      ✅ Complete        │
    │      ✅ Complete        │                    │                         │                    │                         │
    │                         │                    │ Bug 1: list_projects    │                    │ Tools Migrated          │
    │ Tools                   │                    │   • Default "active"→   │                    │   • list_projects       │
    │   • get_portfolio_summary│                   │     None (MCP protocol) │                    │   • get_project         │
    │   • get_blocked_projects│                    │                         │                    │   • create_project      │
    │   • search_projects     │                    │ Bug 2: search_projects  │                    │   • update_project      │
    │                         │                    │   • Added updated_at    │                    │   • analysis tools      │
    │ Patterns                │                    │   • Added dev_updated_at│                    │                         │
    │   • Pydantic models     │                    │                         │                    │ Patterns                │
    │   • Client-side search  │                    │ Bug 3: get_blocked      │                    │   • model_validate()    │
    └─────────────────────────┘                    │   • Already fixed       │                    │   • @computed_field     │
                                                   └─────────────────────────┘                    │   • Parametrized tests  │
                                                                                                  └────────────┬────────────┘
                                                                                                               │
                                                                                                               │
                                        ╭──────────────────────────────────────────────┬───────────────────────┴──────────────────────╮
                                        │                                              │                                              │
                                        │                                              │                                              │
                                        │                                              │                                              ▼
                                        │                                              │                                 ┌─────────────────────────┐
                                        │                                              ▼                                 │   PYDANTIC REFACTOR     │
                                        ▼                                 ┌─────────────────────────┐                    │      ✅ Complete        │
                           ┌─────────────────────────┐                    │        PoC 12           │                    │                         │
                           │        PoC 11           │                    │    MILESTONES DB        │                    │ Models Created          │
                           │      DEV ACTIVITY       │                    │      ✅ Complete        │                    │   • Project             │
                           │      ✅ Complete        │                    │                         │                    │   • ProjectSummary      │
                           │                         │                    │ Database                │                    │   • ToolResponse[T]     │
                           │ Field                   │                    │   • milestones table    │                    │   • ErrorDetail         │
                           │   • dev_updated_at      │                    │   • RLS policies        │                    │                         │
                           │                         │                    │   • CASCADE DELETE      │                    │ Enums                   │
                           │ Updated                 │                    │                         │                    │   • ProjectStatus       │
                           │   • Project model       │                    │ Models                  │                    │   • Priority            │
                           │   • ProjectSummary      │                    │   • Milestone           │                    │                         │
                           │   • list_projects       │                    │   • MilestoneSummary    │                    │ Benefits                │
                           │   • update_project      │                    │   • ActionableMilestone │                    │   • Type safety         │
                           └─────────────────────────┘                    └────────────┬────────────┘                    │   • Auto validation     │
                                                                                       │                                 │   • IDE autocomplete    │
                                                                                       │                                 │   • Self-documenting    │
                                                                                       │                                 └─────────────────────────┘
                                                                                       │
                                                                                       │
                                                                                       │
                                                                                       │
                                                                                       │
                                                                                       ▼
                                                                          ┌─────────────────────────┐
                                                                          │        PoC 13           │
                                                                          │   MILESTONE TOOLS       │
                                                                          │      ✅ Complete        │
                                                                          │                         │
                                                                          │ CRUD Tools              │
                                                                          │   • list_milestones     │
                                                                          │   • get_milestone       │
                                                                          │   • create_milestone    │
                                                                          │   • update_milestone    │
                                                                          │                         │
                                                                          │ Workflow Tools          │
                                                                          │   • complete_milestone  │
                                                                          │   • get_next_actions    │
                                                                          └─────────────────────────┘
```

*This is a subset of actual data, rendered by visualflow from [docs/visual-tasks.json](docs/visual-tasks.json).*

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
