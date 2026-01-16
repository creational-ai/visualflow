# Visual Milestone PoC Design

## Milestone Overview

This milestone proves we can generate **flawless** ASCII diagrams of task dependencies. Not "good enough" - flawless. We have all the tools (Grandalf, ascii-dag, Graphviz) and the knowledge to solve this properly. No compromises on diagram quality.

## Project

Mission Control - [visual-milestone.md](./visual-milestone.md)

## Core Principle: Quality First

**The diagram must be flawless.**

- No ugly edge routing
- No overlapping boxes
- No misaligned connections
- No unreadable output
- Every diagram should look like a human carefully drew it

We have three layout engines, ascii-dag's sophisticated edge routing logic, and the ability to iterate. There is no excuse for subpar output. If something doesn't look right, we fix it until it does.

## PoC Dependency Diagram

```
┌──────────────────────────────────────┐
│  PoC 0: Exploration                  │
│  Test all 3 layout engines           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 1: Design & Architecture        │
│  LayoutEngine + Canvas + EdgeRouter  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 2: Interface Layer              │
│  list_tasks → ASCII diagram          │
└──────────────────────────────────────┘
```

**Parallel tracks**: None - strictly sequential. Each PoC depends on findings/artifacts from the previous.

**Note**: This is a plan - NO status indicators in diagram.

---

## PoCs

### PoC 0: Exploration

**Proves**: We understand what each layout engine excels at and what combination (all 3? 2? just 1?) provides the best value vs. complexity trade-off.

**Unlocks**: PoC 1 - provides evidence-based understanding of which engines to use and how they complement each other.

**Key Question**: Do we need all 3 engines, or is one/two enough?
- Maybe Grandalf does layout, ascii-dag informs edge routing design
- Maybe Graphviz is overkill for our needs
- Maybe one engine does everything well enough
- **We don't mind using all 3 IF the value justifies the complexity**

**Scope**:
- Test suite for Grandalf with 7 graph scenarios
- Test suite for ascii-dag with same scenarios
- Test suite for Graphviz with same scenarios
- **Value vs. Complexity matrix** for each engine

**Test Scenarios**:
1. Simple chain: A → B → C
2. Diamond: A → B, A → C, B → D, C → D
3. Multiple roots: A → C, B → C
4. Skip-level: A → B → C, A → C (direct)
5. Wide graph: A → B, A → C, A → D, A → E
6. Deep graph: A → B → C → D → E → F
7. Complex: Combination of above

**What to Evaluate Per Engine**:
- Can it accept custom node dimensions (width, height)?
- What coordinate system does it output?
- Does it provide edge routing hints?
- How does it handle disconnected components?
- Performance with 50+ nodes?
- **Integration complexity** (Python native vs subprocess vs FFI)
- **What unique value does it provide that others don't?**

**Success Criteria**:
- All three engines tested with all 7 scenarios
- Clear understanding of each engine's strengths/weaknesses
- **Decision matrix**: which engine(s) to use and why
- Answer: "Do we need 3, 2, or 1 engine(s)?"
- **Quality gate**: Identify which engine(s) can produce flawless output for each scenario

**Deliverables**:
```
diagram/
├── tests/
│   ├── conftest.py              # Shared fixtures (graph scenarios)
│   ├── test_grandalf.py         # Grandalf tests
│   ├── test_ascii_dag.py        # ascii-dag tests (via subprocess)
│   └── test_graphviz.py         # Graphviz tests (via dot -Tplain)
└── docs/
    └── poc0-comparison-matrix.md  # Findings document
```

---

### PoC 1: Design & Architecture

**Proves**: We can build a flexible, well-tested foundation for diagram generation with >90% code coverage.

**Unlocks**: PoC 2 - provides the rendering infrastructure for end-to-end pipeline.

**Depends On**: PoC 0 (engine selection, coordinate understanding)

**Scope**:
- `LayoutEngine` abstract base class
- Adapter(s) for selected engine(s) from PoC 0
- `Canvas` class with box rendering
- `EdgeRouter` with basic routing
- Comprehensive test suite

**Core Components**:

1. **LayoutEngine Abstraction**
   ```python
   class LayoutEngine(ABC):
       @abstractmethod
       def compute(self, nodes: list[Node], edges: list[Edge]) -> LayoutResult
   ```

2. **Canvas**
   - 2D character array
   - `draw_box(x, y, w, h, content)`
   - Bounds checking
   - Character collision handling

3. **EdgeRouter**
   - Vertical lines for aligned boxes
   - Corner routing for offset boxes
   - Basic collision avoidance

**Architecture Decisions** (finalized from PoC 0):
- Primary layout engine: [TBD after PoC 0]
- Coordinate scaling strategy: [TBD]
- Edge routing approach: [TBD]

**Success Criteria**:
- Can render simple dependency graph (3-5 nodes) as **flawless** ASCII
- All unit tests pass
- Code coverage >90%
- Clean, documented API
- No unanswered technical questions
- **Quality gate**: Every test scenario produces a diagram that looks hand-crafted

**Deliverables**:
```
diagram/
├── src/
│   └── visualflow/              # PyPI package name
│       ├── __init__.py
│       ├── engines/
│       │   ├── __init__.py
│       │   ├── base.py          # LayoutEngine ABC
│       │   └── grandalf.py      # GrandalfAdapter (or selected engine)
│       ├── render/
│       │   ├── __init__.py
│       │   ├── canvas.py        # Canvas class
│       │   └── edge_router.py   # EdgeRouter class
│       └── models.py            # Node, Edge, LayoutResult dataclasses
├── tests/
│   ├── test_canvas.py
│   ├── test_edge_router.py
│   └── test_layout_engine.py
└── docs/
    └── poc1-architecture.md     # Architecture decisions doc
```

---

### PoC 2: Interface Layer

**Proves**: The core library works as a **standalone open-source package** that can be easily consumed by Mission Control (and others).

**Unlocks**: Open-source release, Claude skill integration, other projects using the library.

**Depends On**: PoC 1 (rendering infrastructure)

**Vision**: Build a standalone ASCII DAG visualization library
- **Not** Mission Control-specific code
- MC is just one consumer that validates the library works
- Consider: new PyPI package? Fork of ascii-dag? Python port inspired by both?
- Design for reusability from day one

**Scope**:
- Clean public API for the library
- Adapter layer for Mission Control's `list_tasks` (separate from core lib)
- End-to-end validation with real MC data
- Documentation for open-source release

**Library Interface** (generic, not MC-specific):
```python
from visualflow import DAG, render

# Core library - works with any data
dag = DAG()
dag.add_node("a", label="Task A", width=15, height=3)
dag.add_node("b", label="Task B", width=15, height=3)
dag.add_edge("a", "b")

diagram = render(dag)  # Returns ASCII string
```

**Mission Control Adapter** (separate layer):
```python
from visualflow.adapters.mission_control import from_tasks

# MC-specific adapter that uses the core library
tasks = list_tasks(project_slug="my-project")
diagram = from_tasks(tasks, milestone_filter="core")
```

**Open Source Considerations**:
- Name: `visualflow` (decided)
- Relationship to ascii-dag (Rust): Inspired-by (uses similar concepts)
- License: MIT (same as ascii-dag)
- PyPI publishing ready

**Success Criteria**:
- Core library works independently (no MC dependency)
- MC adapter validates library with real data
- Clean separation: core lib vs. adapters
- Documentation sufficient for external users
- All task statuses display correctly (✓ complete, ● active, ○ planned)
- Performance <1 second for 30 nodes
- **Quality gate**: Real MC data produces diagrams indistinguishable from hand-drawn

**Deliverables**:
```
diagram/
├── src/
│   └── visualflow/              # PyPI package name
│       ├── __init__.py          # Public API
│       ├── dag.py               # DAG class
│       ├── render.py            # render() function
│       ├── engines/             # Layout engine adapters (from PoC 1)
│       └── adapters/            # Data source adapters
│           ├── __init__.py
│           └── mission_control.py  # MC-specific adapter
├── tests/
│   ├── test_core_api.py         # Core library tests
│   └── test_mc_adapter.py       # MC adapter tests
└── docs/
    ├── poc2-results.md
    └── README.md                # Library documentation
```

---

## Execution Order

1. **PoC 0 - Exploration** (no dependencies)
   - Create test infrastructure
   - Test all three engines
   - Document findings

2. **PoC 1 - Design & Architecture** (requires PoC 0)
   - Implement based on PoC 0 findings
   - Build core components
   - Achieve coverage target

3. **PoC 2 - Interface Layer** (requires PoC 1)
   - Connect to Mission Control
   - End-to-end integration
   - Polish and document

---

## Integration Points

**PoC 0 → PoC 1**:
- Comparison matrix informs engine selection
- Test scenarios become regression tests
- Coordinate system understanding informs Canvas design

**PoC 1 → PoC 2**:
- `LayoutEngine.compute()` called by `GraphBuilder`
- `Canvas` + `EdgeRouter` render the final diagram
- `LayoutResult` contains positions for `GraphBuilder` to use

**PoC 2 → Future**:
- `generate_diagram()` function is the public API
- Claude skill will call this function
- Output string can be displayed directly in conversation

---

## Risk Assessment

| PoC | Risk Level | Risk | Mitigation |
|-----|------------|------|------------|
| PoC 0 | Medium | No engine handles variable node sizes well | Test all three; hybrid approach if needed |
| PoC 0 | Low | ascii-dag subprocess integration complex | Fall back to Grandalf + Graphviz only |
| PoC 1 | Medium | Edge routing produces ugly diagrams | Start simple; iterate until flawless; no compromises |
| PoC 1 | Low | 90% coverage hard to achieve | Focus on critical paths; document exclusions |
| PoC 2 | Low | list_tasks output format changes | Use snapshot tests; adapt as needed |
| PoC 2 | Low | Performance issues with large graphs | Add filtering; set 50-node limit |

---

## Key Questions to Answer

**PoC 0 must answer**:
- Do we need all 3 engines, 2, or just 1?
- What unique value does each engine provide?
- Is the complexity of multiple engines worth the benefit?
- What coordinate system should we normalize to?
- Any blocking limitations?

**PoC 1 must answer**:
- What's the minimum readable box width?
- How to handle edge collisions?
- What's the best coordinate scaling factor?
- Should we design for extensibility (multiple engines) or simplicity (one engine)?

**PoC 2 must answer**:
- ~~What should we name the library?~~ → `visualflow` (decided)
- ~~Fork ascii-dag or build inspired-by?~~ → Inspired-by (decided)
- How to structure adapters for different data sources?
- What's the minimal public API for v1.0?

---

## Success Definition

**Milestone Complete When**:
1. All three PoCs pass their success criteria
2. **Diagram quality is flawless** - no compromises
3. Standalone library works independently of Mission Control
4. MC adapter validates library with real `list_tasks` data
5. Architecture documented and >90% tested
6. No unanswered technical questions
7. Library ready for open-source release (PyPI-publishable)
8. Ready for Claude skill integration in future milestone

**Quality Standard**: If a diagram doesn't look like it was carefully hand-drawn by a human, it's not done.

---

*Document Status*: Ready for PoC 0 Implementation
*Last Updated*: January 2026
