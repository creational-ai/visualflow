# Visual Milestone Details

> **Last Updated**: 2026-01-17
>
> This document provides a comprehensive overview of the Visual Milestone accomplishments for visualflow - a Python library for generating ASCII diagrams of directed acyclic graphs with variable-sized boxes.

---

## Executive Summary

**Visual Milestone Status**: 🔄 IN PROGRESS (4 of 5 tasks)

| Task | Status | What It Proved |
|------|--------|----------------|
| PoC 0 | ✅ Complete | Grandalf (pure Python, ~0.03s) and Graphviz (~2.79s) can compute node positions for variable-sized boxes |
| PoC 1 | ✅ Complete | Core data models, canvas rendering, and layout engines work together to produce positioned ASCII diagrams |
| PoC 2 | ✅ Complete | SimpleRouter produces clean ASCII edge paths connecting positioned boxes with unicode-aware rendering |
| PoC 3 | ✅ Complete | Smart routing with box connectors, trunk-and-split, merge patterns, and configurable theme system |
| PoC 4 | 📋 Planned | Add LICENSE, update pyproject.toml and README, create git tag for GitHub install |

**Current State**: The visualflow library has complete ASCII DAG visualization with smart edge routing and a configurable theme system. Production-ready Pydantic data models (`DAG`, `Node`, `Edge`, `LayoutResult`, `NodePosition`, `EdgePath`, `EdgeTheme`) are implemented with full validation. Two layout engines (`GrandalfEngine` for speed, `GraphvizEngine` for future edge hints) compute node positions in character coordinates. The `SimpleRouter` computes geometric edge paths with smart patterns: trunk-and-split for fan-out, merge routing for fan-in, and box connectors at exit points. Four theme presets (DEFAULT, LIGHT, ROUNDED, HEAVY) are available and configurable via `.env` file with python-dotenv integration. All 293 tests pass with 0.002s render time for complex graphs. The library is ready for PoC 4: GitHub Release.

---

## Current System Architecture

```
VISUALFLOW ARCHITECTURE (POST-POC 3)
===============================================================================

                         ┌─────────────────────────────────────┐
                         │            Public API               │
                         │  render_dag(dag, engine, router,    │
                         │             theme)                  │
                         │  - DAG, Node, Edge                  │
                         │  - GrandalfEngine, GraphvizEngine   │
                         │  - SimpleRouter                     │
                         │  - EdgeTheme, settings              │
                         │  - Canvas                           │
                         └────────────────┬────────────────────┘
                                          │
           ┌──────────────────────────────┼──────────────────────────────┐
           │                              │                              │
           ▼                              ▼                              ▼
  ┌──────────────┐              ┌──────────────┐               ┌──────────────┐
  │   models.py  │              │   engines/   │               │   routing/   │
  │              │              │              │               │              │
  │ • Node       │              │ • base.py    │               │ • base.py    │
  │ • Edge       │              │   Protocol   │               │   EdgeRouter │
  │ • DAG        │              │              │               │              │
  │ • NodePos    │              │ • grandalf   │               │ • simple.py  │
  │ • LayoutRes  │              │ • graphviz   │               │   SmartRtr   │
  │ • EdgePath   │              │              │               │   TrunkSplit │
  │ • EdgeTheme  │              │              │               │   MergeRoute │
  └──────────────┘              └──────────────┘               └──────────────┘
           │                           │                              │
           │            ┌──────────────┴──────────────┐               │
           │            │                             │               │
           ▼            ▼                             ▼               │
  ┌──────────────┐ ┌────────────────┐       ┌────────────────┐       │
  │ settings.py  │ │   Grandalf     │       │   Graphviz     │       │
  │              │ │   Library      │       │   CLI (dot)    │       │
  │ • Settings   │ │   Pure Python  │       │   Subprocess   │       │
  │ • .env load  │ │   ~0.03s       │       │   ~2.79s       │       │
  │ • THEME_MAP  │ └────────────────┘       └────────────────┘       │
  └──────────────┘                                                   │
                       ┌─────────────────────────────────────────────┘
                       │
                       ▼
              ┌──────────────┐
              │   render/    │
              │              │
              │ • canvas.py  │
              │   Canvas     │
              │   place_box  │
              │   draw_edge  │
              │   fix_junct  │
              │   place_conn │
              │   render     │
              └──────────────┘

THEME SYSTEM
===============================================================================
┌────────────┬──────────┬────────────┬─────────┬───────┐
│   Theme    │ Vertical │ Horizontal │ Corners │ Arrow │
├────────────┼──────────┼────────────┼─────────┼───────┤
│ DEFAULT    │    |     │     -      │  ┌┐└┘   │   v   │
│ LIGHT      │    │     │     ─      │  ┌┐└┘   │   ▼   │
│ ROUNDED    │    │     │     ─      │  ╭╮╰╯   │   ▼   │
│ HEAVY      │    ┃     │     ━      │  ┏┓┗┛   │   ▼   │
└────────────┴──────────┴────────────┴─────────┴───────┘

EXTERNAL DEPENDENCIES
===============================================================================
• grandalf>=0.8      - Pure Python Sugiyama layout algorithm
• pydantic>=2.0      - Data validation and serialization
• wcwidth>=0.2       - Unicode width calculation (emoji, CJK)
• python-dotenv      - .env file configuration loading
• graphviz CLI       - Optional, for GraphvizEngine
```

---

## Progress Overview Diagram

```
                        VISUAL MILESTONE PROGRESS (IN PROGRESS)
===============================================================================

    PoC 0                   PoC 1                   PoC 2                   PoC 3                   PoC 4
    EXPLORATION             ARCHITECTURE            EDGE ROUTING            SMART ROUTING           INTERFACE
    -------------           -------------           -------------           -------------           -------------
    ✅ Complete             ✅ Complete             ✅ Complete             ✅ Complete             📋 Planned

    ┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐         ┌─────────────┐
    │ Engine      │         │ Foundation  │         │ Routing     │         │ Smart       │         │ Public API  │
    │ Comparison  │────────▶│ • Models    │────────▶│ • Router    │────────▶│ • Connectors│────────▶│ • README    │
    │ • Grandalf  │         │ • Canvas    │         │ • Segments  │         │ • TrunkSplit│         │ • PyPI      │
    │ • Graphviz  │         │ • Engines   │         │ • Unicode   │         │ • MergeRoute│         │ • License   │
    │ • Perf test │         │ • render()  │         │ • draw_edge │         │ • Themes    │         │ • Examples  │
    └─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘         └─────────────┘
```

---

## What PoC 0 Delivered: Engine Exploration

**Duration**: 2026-01-15

PoC 0 validated that both Grandalf (pure Python Sugiyama) and Graphviz (external CLI) can compute node positions for variable-sized ASCII boxes. Performance comparison showed Grandalf is ~93x faster than Graphviz, making it the default choice. Both engines respect node dimensions and produce hierarchical layouts suitable for DAG visualization.

### 1. Engine Performance Comparison

```
LAYOUT ENGINE BENCHMARKS
==================================================================

Engine      Time (avg)     Method              Edge Routing
-----------------------------------------------------------------
Grandalf    ~0.03s         Pure Python         None (manual)
Graphviz    ~2.79s         subprocess          Spline hints

Winner: Grandalf for speed (~93x faster)
Note: Graphviz provides edge spline hints for future PoC 2 use
```

### 2. Layout Algorithm Findings

Both engines implement Sugiyama-style hierarchical layout:
- **Layer Assignment**: Nodes assigned to levels based on DAG depth
- **Crossing Minimization**: Reorder nodes within levels to reduce edge crossings
- **Position Assignment**: Compute x,y coordinates respecting node dimensions

Key finding: Both engines return positions as floats (Graphviz in inches, Grandalf in arbitrary units). Conversion to character coordinates required for ASCII rendering.

### 3. Test Coverage Established

Seven test fixtures covering edge cases:
1. `simple_chain` - A -> B -> C (vertical alignment)
2. `diamond` - Converging paths
3. `multiple_roots` - A -> C, B -> C
4. `skip_level` - Mixed depth connections (routing challenge)
5. `wide_graph` - 1 -> 4 children (horizontal spread)
6. `deep_graph` - 6 vertical levels
7. `complex_graph` - Real-world combination

### 4. Lessons Learned

```
KEY LESSONS FROM POC 0
==================================================================

1. Grandalf requires a `view` object on each Vertex with w, h, xy attributes.
   The layout algorithm mutates xy directly during draw().

2. Graphviz node IDs must be alphanumeric - hyphens converted to underscores.
   Plain output format: node <name> <x> <y> <width> <height> <label>

3. Performance: Grandalf ~0.03s vs Graphviz ~2.79s (~93x difference).
   Use Grandalf for interactive use, Graphviz for edge hints only.

4. Both engines handle disconnected components, but positioning varies.
   May need manual offset to prevent overlap.
```

### PoC 0 Artifacts

| File | Purpose | Lines |
|------|---------|-------|
| `tests/test_grandalf.py` | Grandalf exploration tests | ~200 |
| `tests/test_graphviz.py` | Graphviz exploration tests | ~180 |
| `tests/test_fixtures.py` | Fixture validation tests | ~100 |
| `tests/conftest.py` | Test fixtures (TestNode, TestEdge, TestGraph) | ~150 |
| `docs/visual-poc0-results.md` | PoC 0 findings | ~200 |

---

## What PoC 1 Delivered: Architecture Foundation

**Duration**: 2026-01-16T16:24:11-0800 to 2026-01-16T16:46:11-0800 (~22 minutes)

PoC 1 built the complete foundation for ASCII DAG visualization. All data models use Pydantic for validation. Two production-ready layout engines compute positions. The Canvas class renders positioned boxes. The `render_dag()` function provides a clean public API. 167 tests verify correctness including no-overlap and level ordering guarantees.

### 1. Data Models Structure

```
PYDANTIC DATA MODELS (src/visualflow/models.py)
==================================================================

┌─────────────────────────────────────────────────────────────────┐
│  Node                                                           │
│  ├── id: str                                                    │
│  ├── content: str          # Complete ASCII box with borders    │
│  ├── width: int            # Computed via wcwidth               │
│  └── height: int           # Computed from line count           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Edge                                                           │
│  ├── source: str                                                │
│  └── target: str                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  DAG                                                            │
│  ├── nodes: dict[str, Node]                                     │
│  ├── edges: list[Edge]                                          │
│  ├── add_node(id, content)                                      │
│  ├── add_edge(source, target)                                   │
│  └── get_node(id) -> Node | None                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  NodePosition                                                   │
│  ├── node: Node                                                 │
│  ├── x: int               # Left edge (characters)              │
│  └── y: int               # Top edge (lines)                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  LayoutResult                                                   │
│  ├── positions: dict[str, NodePosition]                         │
│  ├── width: int           # Canvas width                        │
│  └── height: int          # Canvas height                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  EdgePath                                                       │
│  ├── source_id: str                                             │
│  ├── target_id: str                                             │
│  └── segments: list[tuple[int, int, int, int]]                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Layout Engine Protocol

```
LAYOUT ENGINE ARCHITECTURE
==================================================================

                    ┌────────────────────┐
                    │   LayoutEngine     │
                    │     (Protocol)     │
                    │                    │
                    │ compute(dag: DAG)  │
                    │   -> LayoutResult  │
                    └─────────┬──────────┘
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
    ┌──────────────────┐           ┌──────────────────┐
    │  GrandalfEngine  │           │  GraphvizEngine  │
    │                  │           │                  │
    │  • Pure Python   │           │  • CLI subprocess│
    │  • ~0.03s        │           │  • ~2.79s        │
    │  • Default       │           │  • Edge hints    │
    │  • No deps       │           │  • Requires dot  │
    └──────────────────┘           └──────────────────┘
```

### 3. Canvas Rendering

```
CANVAS CLASS (src/visualflow/render/canvas.py)
==================================================================

Canvas(width, height)
│
├── _grid: list[list[str]]      # 2D character array (private)
│
├── place_box(content, x, y)    # Place pre-made box at position
│   └── Handles clipping at canvas edges
│
├── put_char(char, x, y)        # Place single character
│   └── Out-of-bounds silently ignored
│
├── get_char(x, y) -> str       # Read character at position
│   └── Returns space if out of bounds
│
└── render() -> str             # Output final ASCII string
    ├── Strips trailing spaces per line
    └── Strips trailing empty lines
```

### 4. Test Coverage Summary (PoC 1)

```
TEST COVERAGE (167 tests passing)
==================================================================

Test File               Tests   Coverage
----------------------------------------------------------------
test_models.py           20     All 6 Pydantic models
test_canvas.py           14     All canvas methods
test_engines.py          30     Both engines, all fixtures
test_new_fixtures.py     17     7 fixture validations
test_integration.py      20     End-to-end rendering
test_fixtures.py         10     Original fixtures (baseline)
test_grandalf.py         19     Grandalf exploration (baseline)
test_graphviz.py         18     Graphviz exploration (baseline)
test_ascii_dag.py        19     ASCII rendering (baseline)
----------------------------------------------------------------
TOTAL                   167     All passing
```

### 5. Visual Output Example

```
SIMPLE CHAIN RENDERED (GRANDALF)
==================================================================

    +-------------+
    |    Task A   |
    +-------------+

    +-------------+
    |    Task B   |
    +-------------+

    +-------------+
    |    Task C   |
    +-------------+
```

### 6. Lessons Learned

```
KEY LESSONS FROM POC 1
==================================================================

1. Grandalf VertexView must be plain class - Grandalf mutates the xy
   attribute directly during sug.draw(), so Pydantic frozen models fail.
   Use plain Python class with mutable attributes.

2. Grandalf disconnected components overlap by default - Each component
   in graph.C is laid out with origin at (0,0). Must manually offset
   components horizontally using component.sV to access vertices.

3. Grandalf returns center coordinates as floats - Conversion to top-left
   integer coords: int(center_x - width/2 - min_x) + spacing.
   Missing center-to-corner adjustment causes box overlap.

4. Graphviz Y-axis is inverted - Origin is bottom-left while terminal
   origin is top-left. Flip Y: max_y - node_y during conversion.

5. DOT format requires sanitized node IDs - Hyphens break parsing.
   Convert poc-1 to poc_1 for DOT, map back when parsing results.

6. wcwidth returns -1 for non-printable chars - Always fallback to
   len() when wcwidth.wcswidth() returns negative values.
```

### PoC 1 Artifacts

| File | Purpose | Lines |
|------|---------|-------|
| `src/visualflow/models.py` | Pydantic data models | ~80 |
| `src/visualflow/engines/__init__.py` | Engine exports | ~10 |
| `src/visualflow/engines/base.py` | LayoutEngine protocol | ~25 |
| `src/visualflow/engines/grandalf.py` | GrandalfEngine implementation | ~110 |
| `src/visualflow/engines/graphviz.py` | GraphvizEngine implementation | ~130 |
| `src/visualflow/render/__init__.py` | Render exports | ~5 |
| `src/visualflow/render/canvas.py` | Canvas class | ~75 |
| `src/visualflow/__init__.py` | Public API | ~45 |
| `tests/fixtures/boxes.py` | Box content helpers | ~75 |
| `tests/fixtures/simple_chain.py` | Fixture 1 | ~20 |
| `tests/fixtures/diamond.py` | Fixture 2 | ~20 |
| `tests/fixtures/wide_fanout.py` | Fixture 3 | ~25 |
| `tests/fixtures/merge_branch.py` | Fixture 4 | ~20 |
| `tests/fixtures/skip_level.py` | Fixture 5 | ~25 |
| `tests/fixtures/standalone.py` | Fixture 6 | ~15 |
| `tests/fixtures/complex_graph.py` | Fixture 7 | ~35 |
| `tests/test_models.py` | Model tests | ~120 |
| `tests/test_canvas.py` | Canvas tests | ~100 |
| `tests/test_engines.py` | Engine tests | ~250 |
| `tests/test_new_fixtures.py` | Fixture tests | ~85 |
| `tests/test_integration.py` | Integration tests | ~150 |

---

## What PoC 2 Delivered: Edge Routing

**Duration**: 2026-01-16T17:33:31-0800 to 2026-01-16T17:46:11-0800 (~13 minutes)

PoC 2 implemented edge routing and canvas unicode fix to produce complete ASCII diagrams with boxes connected by edges. The `EdgeRouter` protocol defines the routing interface. `SimpleRouter` computes geometric edge paths using vertical and Z-shaped patterns. The canvas now handles wide characters (emoji, CJK) correctly and can draw edges with box-drawing characters. All 196 tests pass with 0.002s render time for complex graphs.

### 1. Edge Router Architecture

```
EDGE ROUTER ARCHITECTURE
==================================================================

                    ┌────────────────────┐
                    │    EdgeRouter      │
                    │     (Protocol)     │
                    │                    │
                    │ route(positions,   │
                    │       edges)       │
                    │   -> list[EdgePath]│
                    └─────────┬──────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │   SimpleRouter   │
                    │                  │
                    │  • Vertical line │
                    │    (aligned)     │
                    │  • Z-shape       │
                    │    (offset)      │
                    │  • Integer coords│
                    └──────────────────┘

ROUTING STRATEGY
==================================================================
1. Exit from bottom center of source box
2. Enter at top center of target box
3. Use vertical line if aligned, Z-shape if offset

Z-SHAPE PATTERN
==================================================================
    Source
    +-----+
    |     |
    +-----+
        |         <- Vertical segment down
        +-----    <- Horizontal segment across
              |   <- Vertical segment down
        +-----+
        |Target|
        +-----+
```

### 2. Canvas Edge Drawing

```
CANVAS EDGE DRAWING (draw_edge method)
==================================================================

Characters Used:
  • Vertical:    |
  • Horizontal:  -
  • Corners:     + (junction)
  • Arrow:       v (at target)

Edge Protection:
  • _safe_put_edge_char() prevents overwriting box content
  • Only overwrites spaces or existing edge characters
  • Out-of-bounds coordinates safely ignored
```

### 3. Unicode Support

```
CANVAS UNICODE HANDLING
==================================================================

Problem: Wide characters (emoji, CJK) occupy 2 terminal columns
         but are 1 Python character

Solution: Column tracking using wcwidth
  • Track column position, not character index
  • Wide chars: place char at col, empty "" at col+1
  • render() skips empty string placeholders

Example:
  String "AB" has 3 chars but 4 columns
  Old:  at col 0, A at col 1, B at col 2 (WRONG)
  New:  at col 0, A at col 2, B at col 3 (CORRECT)
```

### 4. Test Coverage Summary (PoC 2)

```
TEST COVERAGE (196 tests passing)
==================================================================

Test File               Tests   New in PoC 2   Coverage
----------------------------------------------------------------
test_canvas.py           25     +11           Unicode + edge drawing
test_routing.py           9     +9            Router protocol, patterns
test_integration.py      29     +9            Edge rendering integration
[other existing]        133      -            Unchanged
----------------------------------------------------------------
TOTAL                   196     +29           All passing

Performance: 0.002s for complex_graph (target: <1s)
```

### 5. Visual Output Example (With Edges)

```
DIAMOND PATTERN WITH EDGES
==================================================================

    +-------------+
    |    Root     |
    +-------------+
        |
        +----+----+
        |         |
        v         v
    +-------+ +-------+
    | Left  | | Right |
    +-------+ +-------+
        |         |
        +----+----+
             |
             v
    +-------------+
    |   Merge     |
    +-------------+
```

### 6. Lessons Learned

```
KEY LESSONS FROM POC 2
==================================================================

1. wcwidth returns -1 for control chars - Use max(1, wcwidth(char))
   to avoid negative column offsets.

2. Empty string placeholder for wide chars - Using "" as placeholder
   for continuation cells allows render() to skip them naturally.

3. Column tracking essential for wide chars - Iterating by Python
   character index fails; must track column position separately.

4. Safe edge char helper prevents corruption - Check if cell contains
   box content before overwriting; only replace spaces/edge chars.

5. Out-of-bounds edge coords safely ignored - Allowing segments to
   extend beyond canvas simplifies routing logic.
```

### PoC 2 Artifacts

| File | Purpose | Lines |
|------|---------|-------|
| `src/visualflow/routing/__init__.py` | Routing exports | 6 |
| `src/visualflow/routing/base.py` | EdgeRouter protocol | 32 |
| `src/visualflow/routing/simple.py` | SimpleRouter implementation | 90 |
| `src/visualflow/render/canvas.py` | Canvas (updated with unicode + draw_edge) | 167 |
| `src/visualflow/__init__.py` | Public API (updated with router) | ~55 |
| `tests/test_routing.py` | Router tests | 214 |
| `tests/test_canvas.py` | Canvas tests (updated) | 312 |
| `tests/test_integration.py` | Integration tests (updated) | 287 |

---

## What PoC 3 Delivered: Smart Routing and Themes

**Duration**: 2026-01-16T21:44:42-0800 to 2026-01-16T22:39:23-0800 (~55 minutes)

PoC 3 implemented smart routing patterns for cleaner diagrams and a configurable theme system. Box connectors mark edge exit points on boxes. Trunk-and-split routing handles fan-out to same-layer targets. Merge routing handles fan-in from multiple sources. The `EdgeTheme` model provides 4 pre-built themes (DEFAULT, LIGHT, ROUNDED, HEAVY) configurable via `.env` file with python-dotenv integration. The `fix_junctions()` post-processor ensures correct junction characters. All 293 tests pass.

### 1. Smart Routing Patterns

```
SMART ROUTING ARCHITECTURE
==================================================================

                    ┌────────────────────────┐
                    │     SimpleRouter       │
                    │     (Enhanced)         │
                    │                        │
                    │ route(positions, edges)│
                    │   -> list[EdgePath]    │
                    └───────────┬────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ _route_basic  │      │ _route_trunk_ │      │ _route_merge_ │
│               │      │    split      │      │    edges      │
│ • Vertical    │      │               │      │               │
│ • Z-shape     │      │ • Shared trunk│      │ • Converge    │
│ • Single edge │      │ • Split line  │      │ • Single drop │
└───────────────┘      │ • Same layer  │      │ • Fan-in      │
                       └───────────────┘      └───────────────┘

PATTERN EXAMPLES
==================================================================

Trunk-and-Split (Fan-out to same layer):
    +-------+
    | Root  |
    +---┬---+           <- single connector at center
        |               <- shared trunk
   -----┴-----          <- split junction
+---+     +---+
| A |     | B |
+---+     +---+

Merge Routing (Fan-in from multiple sources):
+---+     +---+
| A |     | B |
+-┬-+     +-┬-+
  |         |
  ----┬------          <- merge junction
      |
      v
  +-------+
  | Target|
  +-------+
```

### 2. Box Connector Placement

```
BOX CONNECTOR SYSTEM
==================================================================

Placement: After boxes, before edge drawing
Character: ┬ (T-junction pointing down)

Exit Point Calculation:
  • 1 exit:  Center of box bottom
  • 2 exits: 1/3 and 2/3 spacing (balanced)
  • N exits: Evenly spaced across box bottom

Narrow Box Handling:
  • Clamps to center when insufficient space
  • Maintains logical correctness over visual overlap

Canvas Methods:
  • place_box_connector(x, y) - Single connector
  • place_box_connectors(positions, edges) - All connectors
```

### 3. Theme System

```
THEME SYSTEM ARCHITECTURE
==================================================================

┌─────────────────────────────────────────────────────────────────┐
│  EdgeTheme (Pydantic Model)                                     │
│  ├── vertical: str         # | or │ or ┃                        │
│  ├── horizontal: str       # - or ─ or ━                        │
│  ├── corner_tl: str        # ┌ or ╭ or ┏                        │
│  ├── corner_tr: str        # ┐ or ╮ or ┓                        │
│  ├── corner_bl: str        # └ or ╰ or ┗                        │
│  ├── corner_br: str        # ┘ or ╯ or ┛                        │
│  ├── tee_down: str         # ┬ or ┳                             │
│  ├── tee_up: str           # ┴ or ┻                             │
│  ├── tee_right: str        # ├ or ┣                             │
│  ├── tee_left: str         # ┤ or ┫                             │
│  ├── cross: str            # ┼ or ╋                             │
│  └── arrow_down: str       # v or ▼                             │
└─────────────────────────────────────────────────────────────────┘

PRE-BUILT THEMES
==================================================================

┌────────────┬──────────┬────────────┬─────────┬───────┐
│   Theme    │ Vertical │ Horizontal │ Corners │ Arrow │
├────────────┼──────────┼────────────┼─────────┼───────┤
│ DEFAULT    │    |     │     -      │  ┌┐└┘   │   v   │
│ LIGHT      │    │     │     ─      │  ┌┐└┘   │   ▼   │
│ ROUNDED    │    │     │     ─      │  ╭╮╰╯   │   ▼   │
│ HEAVY      │    ┃     │     ━      │  ┏┓┗┛   │   ▼   │
└────────────┴──────────┴────────────┴─────────┴───────┘

CONFIGURATION
==================================================================

Via .env file:
  VISUALFLOW_THEME=rounded

Via settings:
  from visualflow import settings, ROUNDED_THEME
  settings.theme = ROUNDED_THEME

Via render_dag():
  render_dag(dag, theme=HEAVY_THEME)  # Override per-call
```

### 4. Junction Fix Post-Processing

```
JUNCTION FIX SYSTEM
==================================================================

Problem: Drawing edges sequentially may place wrong junction chars
         (e.g., corner when T-junction needed)

Solution: fix_junctions() post-processing
  • Scans all junction characters after edge drawing
  • Checks actual neighbors (up, down, left, right)
  • Replaces with correct character based on connections

Character Selection:
  • 4 connections → cross (┼)
  • 3 connections → appropriate tee (┬┴├┤)
  • 2 connections → appropriate corner (┌┐└┘)
  • 1 connection → line (| or -)
```

### 5. Test Coverage Summary (PoC 3)

```
TEST COVERAGE (293 tests passing)
==================================================================

Test File                 Tests   New in PoC 3   Coverage
----------------------------------------------------------------
test_poc3_routing.py       50     +50           Smart routing tests
test_fanout_patterns.py    16     +16           Fan-out pattern tests
test_core_milestone.py      4     +4            Milestone validation
test_canvas.py             25     (updated)     Theme + connectors
test_routing.py             9     (updated)     Extended routing
test_integration.py        29     (updated)     Theme integration
test_real_diagrams.py      27     (updated)     Real diagram tests
[other existing]          133      -            Unchanged
----------------------------------------------------------------
TOTAL                     293     +70           All passing

Performance: 0.002s for complex_graph (unchanged)
```

### 6. Visual Output Examples

```
SIMPLE CHAIN WITH BOX CONNECTOR
==================================================================

    +---------------+
    |     Task A    |
    |               |
    +-------┬-------+
            |
            v
    +---------------+
    |     Task B    |
    |               |
    +---------------+

DIAMOND PATTERN WITH SMART ROUTING
==================================================================

                     +-------------+
                     |    Start    |
                     |             |
                     +------┬------+
                            |
           -----------------┴------------------
    +-------------+                    +-------------+
    |     Left    |                    |    Right    |
    |             |                    |             |
    +------┬------+                    +------┬------+
           -----------------┬------------------
                            v
                     +-------------+
                     |     End     |
                     |             |
                     +-------------+
```

### 7. Lessons Learned

```
KEY LESSONS FROM POC 3
==================================================================

1. Render pipeline order matters - The sequence boxes -> connectors ->
   edges ensures proper layering; connectors must be placed after
   boxes but before edge drawing to prevent overwriting.

2. Connector and routing logic must match - Placing connectors at
   multiple exit points while routing edges from center creates
   visual mismatch. Both must use the same decision logic.

3. Thirds spacing for two exits - For two exit points from a box,
   using 1/3 and 2/3 positioning produces better visual balance.

4. Graceful degradation for narrow boxes - When a box is too narrow
   for multiple exit points, placing all exits at center maintains
   logical correctness even though they overlap visually.

5. Y midpoint prevents edge-box overlap - For merge routing,
   calculating the merge row at the Y midpoint between lowest source
   bottom and target top ensures edges don't overlap with boxes.

6. Edge classification by target incoming count - Checking how many
   edges point to each target cleanly separates independent edges
   from merge edges without complex graph analysis.
```

### PoC 3 Artifacts

| File | Purpose | Lines |
|------|---------|-------|
| `src/visualflow/routing/simple.py` | SimpleRouter (smart routing) | 667 |
| `src/visualflow/render/canvas.py` | Canvas (connectors + themes) | 556 |
| `src/visualflow/models.py` | Models (EdgeTheme added) | 175 |
| `src/visualflow/settings.py` | Global settings + .env loading | 79 |
| `src/visualflow/__init__.py` | Public API (themes exported) | 99 |
| `tests/test_poc3_routing.py` | PoC 3 routing tests | 1127 |
| `tests/test_fanout_patterns.py` | Fan-out pattern tests | 113 |
| `tests/test_core_milestone.py` | Milestone validation tests | 111 |

---

## What's Built (Visual In Progress)

```
MILESTONE COMPLETION MAP
==================================================================

✅ Data Models (Pydantic)
├── Node with computed width/height (wcwidth for Unicode)
├── Edge for directed relationships
├── DAG container with add/get methods
├── NodePosition with integer coordinates
├── LayoutResult with positions + canvas size
├── EdgePath with segments for routing
└── EdgeTheme for configurable edge characters

✅ Layout Engines
├── LayoutEngine Protocol (structural typing)
├── GrandalfEngine (default, ~0.03s, pure Python)
├── GraphvizEngine (~2.79s, optional CLI dependency)
├── Character coordinate conversion
├── Disconnected component handling
└── No-overlap guarantees

✅ Edge Routing
├── EdgeRouter Protocol (structural typing)
├── SimpleRouter (smart routing)
├── Basic routing (vertical, Z-shape)
├── Trunk-and-split for fan-out (1->N same layer)
├── Merge routing for fan-in (N->1)
├── Exit point calculation (1/3, 2/3 spacing)
└── Integer coordinate segments

✅ Canvas Rendering
├── 2D character grid with Pydantic model
├── place_box() with unicode support (emoji, CJK)
├── place_box_connectors() for exit points
├── draw_edge() with theme-aware characters
├── fix_junctions() post-processing
├── put_char()/get_char() for single characters
├── render() with trailing space stripping
└── Wide character placeholder handling

✅ Theme System
├── EdgeTheme Pydantic model
├── 4 pre-built themes (DEFAULT, LIGHT, ROUNDED, HEAVY)
├── .env configuration via VISUALFLOW_THEME
├── python-dotenv integration
├── Global settings.theme
└── Per-call theme override

✅ Public API
├── render_dag(dag, engine, router, theme) helper
├── All models exported from package root
├── Both engines exported
├── Router protocol and SimpleRouter exported
├── All themes exported
├── Settings exported
└── Canvas exported

✅ Test Coverage
├── 293 tests passing
├── 7 fixture patterns covering edge cases
├── No-overlap verification tests
├── Level ordering verification tests
├── Edge routing verification tests
├── Smart routing pattern tests
├── Theme integration tests
└── Visual inspection tests

📋 Pending (PoC 4)
├── Add LICENSE file (MIT)
├── Update pyproject.toml (authors, license)
├── Update README (GitHub install, themes, .env config)
└── Create git tag v0.1.0
```

---

## Key Decisions Made

| Decision | Made In | Rationale |
|----------|---------|-----------|
| **Pydantic over dataclasses** | PoC 1 | Built-in validation, serialization, computed fields |
| **Protocol over ABC** | PoC 1 | More Pythonic, better for structural typing |
| **Pre-made boxes** | Design | Nodes contain complete ASCII boxes from Mission Control task.diagram |
| **wcwidth for Unicode** | PoC 1 | Accurate width calculation for emoji and CJK characters |
| **Two engines** | PoC 0 | Grandalf (fast default) + Graphviz (edge hints for future) |
| **Character coordinates** | PoC 1 | All positions in characters/lines, not inches/pixels |
| **GrandalfEngine default** | PoC 1 | Pure Python, no external deps, ~93x faster than Graphviz |
| **SimpleRouter default** | PoC 2 | Automatic edge routing when DAG has edges |
| **Offset disconnected components** | PoC 1 | Prevents overlapping boxes in standalone fixtures |
| **Empty string as wide-char placeholder** | PoC 2 | Simpler than sentinel values, render() filters naturally |
| **Single connector for trunk-split** | PoC 3 | Connector and routing must use same decision logic |
| **Thirds spacing for two exits** | PoC 3 | 1/3 and 2/3 gives better visual balance than halves |
| **fix_junctions() post-processing** | PoC 3 | Ensures correct junction characters after sequential drawing |
| **EdgeTheme Pydantic model** | PoC 3 | Type-safe theme configuration with validation |
| **python-dotenv integration** | PoC 3 | Standard .env configuration pattern |

---

## Next Steps

**Visual Milestone: IN PROGRESS** (4 of 5 tasks complete)

PoC 0 (Engine Exploration), PoC 1 (Architecture Foundation), PoC 2 (Edge Routing), and PoC 3 (Smart Routing and Themes) are complete. The library can render complete ASCII DAG diagrams with positioned boxes, smart edge routing, and configurable themes.

**Next Task: PoC 4 - GitHub Release**
1. Add LICENSE file (MIT)
2. Update pyproject.toml (authors, license, keywords)
3. Update README (GitHub install, themes, .env config)
4. Create git tag: `git tag -a v0.1.0 -m "Initial release"`
5. Push tag: `git push origin v0.1.0`

**Install via**: `uv add git+https://github.com/creational-ai/visualflow.git`

**Future Considerations:**
- Graphviz spline hints for smoother routing
- Edge collision avoidance for complex graphs
- Performance optimization for large graphs (>100 nodes)
- Entry connectors on target boxes

---

## References

- [PoC 0 Overview](./visual-poc0-overview.md)
- [PoC 0 Implementation](./visual-poc0-implementation.md)
- [PoC 0 Results](./visual-poc0-results.md)
- [PoC 1 Overview](./visual-poc1-overview.md)
- [PoC 1 Implementation](./visual-poc1-implementation.md)
- [PoC 1 Results](./visual-poc1-results.md)
- [PoC 2 Overview](./visual-poc2-overview.md)
- [PoC 2 Implementation](./visual-poc2-implementation.md)
- [PoC 2 Results](./visual-poc2-results.md)
- [PoC 3 Overview](./visual-poc3-overview.md)
- [PoC 3 Implementation](./visual-poc3-implementation.md)
- [PoC 3 Results](./visual-poc3-results.md)
- [Architecture](./architecture.md)
- [PoC Design](./visual-poc-design.md)
- [Visual Milestone](./visual-milestone.md)
