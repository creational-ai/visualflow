# Milestone: Visual

**Status**: Planning
**Project**: Mission Control
**Location**: `diagram/`

---

## Executive Summary

This milestone adds visual diagram generation capabilities to Mission Control, enabling automatic ASCII visualization of task dependencies. The goal is to transform abstract task relationships into clear, readable diagrams that help users understand project structure and dependencies at a glance.

The approach is methodical: explore existing layout engines, architect a flexible foundation, then build our interface layer. We prioritize understanding over speed - zero guessing, zero unanswered questions. Each PoC builds on proven findings from the previous one.

**Key Principle**: Engineer a flexible, well-tested solution by exploring options first, then architecting from evidence.

---

## Goal

Build a diagram generation system that visualizes Mission Control task dependencies as ASCII diagrams with variable-sized boxes.

**What This Milestone Proves**:
- Layout engines (Grandalf, ascii-dag, Graphviz) can compute positions for our DAG structures
- Variable-sized ASCII boxes can be rendered at computed positions
- Edge routing works reliably for task dependency graphs
- The solution integrates cleanly with Mission Control's `list_tasks` MCP tool
- The architecture is flexible enough for future enhancements

**What This Milestone Does NOT Include**:
- Interactive diagram editing
- Image/SVG export (ASCII only)
- Real-time diagram updates
- Diagram persistence/caching
- Integration with Claude skill (comes after foundation is solid)

---

## Architecture Overview

### High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Mission Control MCP                       │
│                      list_tasks()                            │
└─────────────────────┬───────────────────────────────────────┘
                      │ Task data with dependencies
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Interface Layer (PoC2)                     │
│         Parse tasks → Build dependency graph                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ Graph structure
                      ▼
┌─────────────────────────────────────────────────────────────┐
│         Layout Engine (evaluated PoC0, abstracted PoC1)      │
│                                                              │
│   ┌───────────┐   ┌───────────┐   ┌───────────┐            │
│   │ Grandalf  │   │ ascii-dag │   │ Graphviz  │            │
│   │  (Python) │   │  (Rust)   │   │   (dot)   │            │
│   └─────┬─────┘   └─────┬─────┘   └─────┬─────┘            │
│         └───────────────┼───────────────┘                   │
│                         │                                    │
│                    Positions (x, y, w, h)                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   ASCII Renderer (PoC1)                      │
│         Draw boxes → Route edges → Output string             │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Layout Engines** (under evaluation):
- Grandalf: Pure Python, Sugiyama algorithm, `pip install grandalf`
- ascii-dag: Rust, Sugiyama + edge routing, compiled binary
- Graphviz: C, `dot -Tplain` for coordinates, `brew install graphviz`

**Python Environment**:
- uv: Package management
- pytest + pytest-cov: Testing framework with coverage
- Python >=3.11: Runtime (3.14 installed locally)

**Rendering**:
- Custom ASCII renderer (Python)
- Variable-sized box support
- Edge routing with ASCII characters

### Cost Structure

- **Development**: No additional costs (all tools are free/open-source)
- **Runtime**: Zero cost (pure computation, no external APIs)
- **Dependencies**:
  - Grandalf: MIT license
  - ascii-dag: MIT license
  - Graphviz: EPL license

---

## Core Components Design

### 1. Layout Engine Abstraction

**Purpose**: Provide a unified interface to multiple layout engines, allowing us to use the best tool for each job.

**Features**:
- Common interface for all three engines
- Engine-specific adapters
- Position output normalization
- Error handling per engine

**System Flow**:
```
Graph Input (nodes, edges)
         │
         ▼
┌─────────────────┐
│ LayoutEngine    │ ← Abstract interface
│ .compute()      │
└────────┬────────┘
         │
    ┌────┴────┬────────────┐
    ▼         ▼            ▼
Grandalf  ascii-dag   Graphviz
Adapter    Adapter     Adapter
    │         │            │
    └────┬────┴────────────┘
         │
         ▼
  LayoutResult(positions, edges)
```

**Technical Design**:
- Abstract base class `LayoutEngine`
- Concrete adapters: `GrandalfAdapter`, `AsciiDagAdapter`, `GraphvizAdapter`
- Common `LayoutResult` dataclass with positions and edge routing
- Factory function to select engine by name

**Integration Points**:
- Grandalf: Direct Python import
- ascii-dag: Run compiled examples for testing; JSON CLI wrapper if needed for production
- Graphviz: Subprocess call to `dot -Tplain`, parse output

### 2. ASCII Box Renderer

**Purpose**: Render variable-sized ASCII boxes at specified positions on a character grid.

**Features**:
- Variable width based on content
- Variable height (3-6 lines typical)
- Box content formatting (slug, name, status)
- Unicode box-drawing characters

**Box Format**:
```
┌─────────────────┐
│ poc-1           │  ← slug
│ Foundation      │  ← name (truncated if needed)
│ ✓ complete      │  ← status indicator
└─────────────────┘
```

**Technical Design**:
- `Canvas` class: 2D character array with bounds checking
- `draw_box(canvas, x, y, w, h, content)`: Render single box
- Content truncation with ellipsis for overflow
- Status symbols: ✓ complete, ● active, ○ planned

**Integration Points**:
- Layout engine provides (x, y) positions
- Task data provides content (slug, name, status)

### 3. Edge Router

**Purpose**: Draw connecting lines between boxes representing dependencies.

**Features**:
- Vertical lines for direct descendants
- Corner routing for offset connections
- Multi-segment paths for complex layouts
- Avoid box collisions

**Edge Characters**:
```
│  Vertical line
─  Horizontal line
┌  Top-left corner
┐  Top-right corner
└  Bottom-left corner
┘  Bottom-right corner
├  T-junction left
┤  T-junction right
┬  T-junction top
┴  T-junction bottom
┼  Cross
▼  Arrow down (connection point)
```

**Technical Design**:
- Input: source box position, target box position, edge type
- A* or simple pathfinding to avoid obstacles
- Character selection based on direction changes
- Collision detection with existing characters

**Integration Points**:
- Layout engine provides edge routing hints
- Canvas provides collision detection
- ascii-dag's `EdgePath` types inform our routing strategy

### 4. Graph Builder

**Purpose**: Transform Mission Control task data into graph structure for layout engines.

**Features**:
- Parse `list_tasks` output
- Build node list with dimensions
- Build edge list from `depends_on`
- Handle disconnected components

**System Flow**:
```
list_tasks() response
         │
         ▼
Parse JSON/dict
         │
         ▼
Calculate box dimensions per task
         │
         ▼
Build nodes: [(id, slug, width, height), ...]
         │
         ▼
Build edges: [(from_id, to_id), ...]
         │
         ▼
Graph ready for layout engine
```

**Technical Design**:
- `Task` dataclass matching MCP response
- `calculate_box_size(task)`: Compute width/height from content
- `build_graph(tasks)`: Return nodes and edges
- Handle missing dependencies gracefully

---

## Implementation Phases

### PoC0: Exploration

**Objective**: Understand capabilities and limitations of all three layout engines through hands-on testing.

**Deliverables**:
- Test suite for Grandalf with various graph structures
- Test suite for ascii-dag with same structures
- Test suite for Graphviz with same structures
- Comparison matrix documenting findings

**Test Scenarios**:
1. Simple chain: A → B → C
2. Diamond: A → B, A → C, B → D, C → D
3. Multiple roots: A → C, B → C
4. Skip-level: A → B → C, A → C (direct)
5. Wide graph: A → B, A → C, A → D, A → E
6. Deep graph: A → B → C → D → E → F
7. Complex: Combination of above

**Success Criteria**:
- ✅ All three engines produce valid positions for all test scenarios
- ✅ Document which engine handles which scenario best
- ✅ Identify any blocking limitations
- ✅ Understand edge routing capabilities of each

### PoC1: Design and Architecture

**Objective**: Establish solid, well-tested foundation based on PoC0 findings.

**Deliverables**:
- `LayoutEngine` abstract base class
- Adapters for selected engine(s)
- `Canvas` class with box rendering
- `EdgeRouter` with basic routing
- Comprehensive test suite (>90% coverage)

**Architecture Decisions** (to be finalized after PoC0):
- Primary layout engine selection
- Fallback engine (if any)
- Coordinate scaling strategy
- Edge routing algorithm

**Success Criteria**:
- ✅ Can render simple dependency graph as ASCII
- ✅ All unit tests pass
- ✅ No unanswered technical questions
- ✅ Clean, documented API

### PoC2: Interface Layer

**Objective**: Connect diagram system to Mission Control's `list_tasks` MCP tool.

**Deliverables**:
- `GraphBuilder` that parses task data
- Box dimension calculator
- End-to-end pipeline: tasks → diagram
- Integration tests with real MC data

**Interface Design**:
```python
def generate_diagram(
    tasks: list[dict],           # From list_tasks()
    milestone_slug: str = None,  # Filter to specific milestone
    engine: str = "grandalf",    # Layout engine choice
) -> str:                        # ASCII diagram
```

**Success Criteria**:
- ✅ Can generate diagram from `list_tasks` output
- ✅ Handles all task statuses correctly
- ✅ Filters by milestone work
- ✅ Output is readable and accurate

---

## Success Metrics

### Technical Quality

**Test Coverage**:
- Target: >90% code coverage
- Measured: pytest-cov
- Why: Foundation must be rock-solid

**Layout Accuracy**:
- Target: 100% correct topology (all dependencies shown)
- Measured: Visual inspection + automated topology checks
- Why: Wrong diagram is worse than no diagram

### Usability

**Readability**:
- Target: Diagram understandable without explanation
- Measured: User feedback
- Why: Primary purpose is communication

**Performance**:
- Target: <1 second for graphs up to 50 nodes
- Measured: pytest benchmarks
- Why: Must feel instant in conversation

---

## Key Outcomes

✅ **Layout engine evaluated and selected**
   - Clear understanding of Grandalf vs ascii-dag vs Graphviz trade-offs
   - Evidence-based selection, not guessing

✅ **Flexible architecture established**
   - Can swap layout engines if needed
   - Clean separation of concerns

✅ **ASCII rendering works reliably**
   - Variable-sized boxes render correctly
   - Edge routing handles common patterns

✅ **Integration path clear**
   - Knows exactly how to consume `list_tasks` data
   - Ready for Claude skill integration in future milestone

---

## Why This Approach?

**Exploration First**:
- Don't commit to a tool before understanding it
- Real tests reveal real limitations
- Evidence over assumptions

**Solid Foundation**:
- Well-tested code is maintainable code
- Zero technical debt from guessing
- Future features build on stable base

**Interface Last**:
- Design the core right before integrating
- Avoid coupling to specific data format too early
- Flexibility to adjust based on learnings

---

## Design Decisions & Rationale

### Why Three Layout Engines?

- **Grandalf**: Pure Python = easiest integration, good for prototyping
- **ascii-dag**: Best edge routing, but Rust compilation adds complexity
- **Graphviz**: Industry standard, but external dependency

**Decision**: Evaluate all three, select based on evidence from PoC0.

### Why pytest for Exploration?

- **Repeatable**: Tests document what we learned
- **Structured**: Organized test scenarios
- **Verifiable**: Can re-run after changes

**Alternative Considered**: Ad-hoc scripts (rejected - not repeatable)

### Why Variable-Sized Boxes?

- **Readability**: Show task info (slug, name, status) directly
- **Information Density**: More context without external lookup
- **Differentiation**: Unlike simple `[label]` nodes

**Alternative Considered**: Fixed-size nodes (rejected - loses information)

---

## Risks & Mitigation

### Risk: No Engine Handles Our Requirements

**Impact**: High - Would need custom layout algorithm
**Probability**: Low - Sugiyama is well-established
**Mitigation**:
- Test all three engines thoroughly in PoC0
- Have fallback: use engine for level assignment, custom x-positioning
- Worst case: fork ascii-dag and modify

### Risk: Edge Routing Too Complex

**Impact**: Medium - Diagrams may have crossing lines
**Probability**: Medium - Variable boxes complicate routing
**Mitigation**:
- Study ascii-dag's edge routing implementation
- Start with simple cases, iterate
- Accept some crossing for complex graphs (still useful)

### Risk: Performance Issues with Large Graphs

**Impact**: Low - Most milestones have <30 tasks
**Probability**: Low - Layout algorithms are O(n log n) typically
**Mitigation**:
- Benchmark during PoC1
- Add pagination/filtering if needed
- Set reasonable limits (50 nodes max)

---

## Open Questions

### Layout Engine

- **Which engine handles variable node sizes best?**
  - Decision: Determine in PoC0 through testing

- **Can we use Grandalf for layout + ascii-dag ideas for edge routing?**
  - Decision: Explore hybrid approach in PoC0

### Rendering

- **What's the minimum readable box width?**
  - Decision: Test with real task data in PoC1

- **How to handle very long task names?**
  - Decision: Truncate with ellipsis, test in PoC1

### Integration

- **Should we filter by milestone or show all tasks?**
  - Decision: Support both, milestone filter by default

---

## Next Steps

**Immediate** (PoC0 - Exploration):
1. Create pytest structure in `diagram/tests/`
2. Write test scenarios for Grandalf
3. Write same scenarios for ascii-dag
4. Write same scenarios for Graphviz
5. Document findings in comparison matrix

**After PoC0** (PoC1 - Architecture):
1. Select primary layout engine based on findings
2. Implement `LayoutEngine` abstraction
3. Build `Canvas` and box renderer
4. Implement edge routing
5. Achieve >90% test coverage

**After PoC1** (PoC2 - Interface):
1. Design `list_tasks` parser
2. Implement `GraphBuilder`
3. Create end-to-end pipeline
4. Test with real Mission Control data

---

## Related Documents

- [Layout Engine Analysis](./ANALYSIS.md) - Detailed analysis of ascii-dag
- [Research: Diagram Tools](./research-diagram-tools.md) - Initial research findings

---

## File Structure

```
diagram/
├── pyproject.toml          # uv project config (name = "visualflow")
├── .venv/                   # Python environment
├── ascii-dag/               # Cloned Rust library (reference)
├── docs/
│   ├── visual-milestone.md  # This document
│   ├── ANALYSIS.md          # Layout engine analysis
│   └── research-diagram-tools.md
├── src/
│   └── visualflow/          # PyPI package (import visualflow)
│       ├── __init__.py
│       ├── engines/         # Layout engine adapters
│       ├── render/          # ASCII rendering
│       └── graph/           # Graph building
└── tests/                   # pytest tests (PoC0+)
    ├── conftest.py          # Shared fixtures
    ├── test_grandalf.py
    ├── test_ascii_dag.py
    ├── test_graphviz.py
    └── test_render.py
```

---

*Document Status*: Planning - Ready for PoC0
*Last Updated*: January 2026
