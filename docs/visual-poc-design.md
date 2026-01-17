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

Note: We call these "text diagrams" not "ASCII diagrams" since we support full Unicode (emoji, box-drawing characters, CJK).

We have three layout engines, ascii-dag's sophisticated edge routing logic, and the ability to iterate. There is no excuse for subpar output. If something doesn't look right, we fix it until it does.

## PoC Dependency Diagram

```
┌──────────────────────────────────────┐
│  PoC 0: Exploration         ✅      │
│  Test all 3 layout engines           │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 1: Architecture Foundation ✅  │
│  LayoutEngine + Canvas (boxes only)  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 2: Edge Routing         ✅     │
│  SimpleRouter + box-drawing corners  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 3: Box Connectors & Routing ○  │
│  ┬ connectors + smart routing        │
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
visualflow/
├── tests/
│   ├── conftest.py              # Shared fixtures (graph scenarios)
│   ├── test_grandalf.py         # Grandalf tests
│   ├── test_ascii_dag.py        # ascii-dag tests (via subprocess)
│   └── test_graphviz.py         # Graphviz tests (via dot -Tplain)
└── docs/
    └── poc0-comparison-matrix.md  # Findings document
```

---

### PoC 1: Architecture Foundation ✅ Complete

**Proves**: We can build a flexible, well-tested foundation for diagram generation with box positioning.

**Unlocks**: PoC 2 - provides positioned boxes for edge routing.

**Depends On**: PoC 0 (engine selection, coordinate understanding)

**Scope**:
- `LayoutEngine` protocol with two implementations (Grandalf, Graphviz)
- `Canvas` class with box rendering (place_box, render)
- Data models (Node, Edge, DAG, NodePosition, LayoutResult, EdgePath)
- `render_dag()` function for boxes-only output
- Comprehensive test suite (167 tests)

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
visualflow/
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

### PoC 2: Edge Routing ✅ Complete

**Proves**: We can connect positioned boxes with clean edge lines, producing complete diagrams.

**Unlocks**: PoC 3 - provides complete rendering (boxes + edges) for box connector integration.

**Depends On**: PoC 1 (box positioning infrastructure)

**Scope**:
- Fix canvas unicode handling (wide characters via wcwidth)
- `EdgeRouter` protocol with `SimpleRouter` implementation
- `Canvas.draw_edge()` for rendering edge paths
- Box-drawing corners: `┌`, `┐`, `└`, `┘` for 90-degree turns
- T-junctions: `┬`, `┴`, `├`, `┤` for merging edges
- Z-shape and L-shape routing for offset nodes

**Delivered**:
- 220 tests passing (up from 167)
- All 7 fixtures render with edges
- Real diagram test suite (`test_real_diagrams.py`) with 24 tests
- Proper corner character selection based on direction
- Junction combining for fan-out/fan-in patterns

**Deliverables**:
```
visualflow/
├── src/
│   └── visualflow/
│       └── routing/
│           ├── __init__.py
│           ├── base.py          # EdgeRouter protocol
│           └── simple.py        # SimpleRouter
└── tests/
    ├── test_routing.py
    └── test_real_diagrams.py    # Real PoC diagram tests
```

---

### PoC 3: Box Connectors & Smart Routing

**Proves**: Edge connections are visually integrated with box borders, and complex routing patterns (trunk-and-split, merge) render cleanly.

**Unlocks**: PoC 4 (Interface Layer) - polished diagrams ready for MC integration.

**Depends On**: PoC 2 (edge routing infrastructure)

**Features**:
1. Box connectors - `┬` on box bottom borders where edges exit
2. Trunk-and-split - same-layer targets share trunk before splitting (optional cleaner fan-out)
3. Merge routing - multiple sources merge at junction before reaching target

**Problem**: Currently edges end with `v` arrows pointing at boxes, but there's no visual connection ON the box itself:
```
┌───────────┐
│   Node A  │
└───────────┘
      |
      v
┌───────────┐
│   Node B  │
└───────────┘
```

**Solution**: Add `┬` connector on the bottom border where edges exit:
```
┌───────────┐
│   Node A  │
└─────┬─────┘
      |
      v
┌───────────┐
│   Node B  │
└───────────┘
```

The bottom box has no `┬` since it has no outgoing edges.

**Complex Example - Diamond + Independent Branch:**

Input edges:
- PoC 0 → PoC 1 (diamond)
- PoC 0 → PoC 2 (diamond)
- PoC 1 → PoC 3 (diamond merge)
- PoC 2 → PoC 3 (diamond merge)
- PoC 0 → PoC 4 (independent)

Expected output:
```
                         ┌───────────────────────────┐
                         │          PoC 0            │
                         └─────────┬───────┬─────────┘
                                   │       │
                                   │       └──────────────────────────────────┐
                                   │                                          │
                    ┌──────────────┴──────────────┐                           │
                    │                             │                           │
                    v                             v                           v
         ┌─────────────────┐           ┌─────────────────┐         ┌─────────────────┐
         │      PoC 1      │           │      PoC 2      │         │      PoC 4      │
         └────────┬────────┘           └────────┬────────┘         └─────────────────┘
                  │                             │
                  └──────────────┬──────────────┘
                                 │
                                 v
                     ┌─────────────────┐
                     │      PoC 3      │
                     └─────────────────┘
```

Key routing requirements:
- Left `┬`: Single trunk goes down, then fans out to PoC 1 and PoC 2
- Right `┬`: Separate independent path to PoC 4
- Bottom `┬`: PoC 1 and PoC 2 edges merge into PoC 3
- Edges from same source to same-layer targets share a trunk before splitting

**Reference Example - Merge with Independent Branch (from architecture.md):**

One parent merges with another AND has its own independent child:

Input edges:
- poc-1 → poc-8 (independent)
- poc-1 → poc-3 (merge with poc-2)
- poc-2 → poc-3 (merge with poc-1)

Expected output:
```
┌──────────────────────────┐                ┌──────────────────────────┐
│          poc-1           │                │          poc-2           │
│         Schema           │                │         Server           │
└─────────┬────┬───────────┘                └────────────┬─────────────┘
          │    │                                         │
          │    └─────────────────────┬───────────────────┘   ← MERGE
          │                          │
          ▼                          ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│          poc-8           │  │          poc-3           │
│   Database Abstraction   │  │           CRUD           │
│    (only from poc-1)     │  │   (merged from both)     │
└──────────────────────────┘  └──────────────────────────┘
```

Key routing requirements:
- poc-1 has TWO exit points (`┬────┬`)
- Left exit: straight down to poc-8 (independent)
- Right exit: merges with poc-2's edge going to poc-3
- The merge uses `┬` junction where the two paths combine

**Scope**:
- Modify `Canvas` or post-processing to add `┬` on box bottom borders at edge exit points
- **Alignment**: `┬` must be at exact same x-coordinate as edge line
- Handle multiple exit points (fan-out): `└──┬──┬──┬──┘`
- **Multi-edge exit routing**: Multiple edges from same source get separate x-offsets
  - Currently all edges exit from center (`box.x + box.width // 2`)
  - Need to space exit points evenly on bottom border
  - Enables "independent branch" pattern from architecture.md example 2
- Preserve box content integrity
- Update test suite

**Success Criteria**:
- All diagrams show `┬` connectors where edges exit boxes
- Fan-out patterns show multiple `┬` characters
- Box content and borders remain intact
- All existing tests pass

**Deliverables**:
```
visualflow/
├── src/
│   └── visualflow/
│       └── render/
│           └── canvas.py        # Updated with connector logic
└── tests/
    └── test_connectors.py       # Connector-specific tests
```

---

### PoC 4: Interface Layer (Future)

**Proves**: The core library works as a **standalone open-source package** that can be easily consumed by Mission Control (and others).

**Unlocks**: Open-source release, Claude skill integration, other projects using the library.

**Depends On**: PoC 3 (polished diagrams)

**Scope**:
- Clean public API for the library
- Adapter layer for Mission Control's `list_tasks` (separate from core lib)
- End-to-end validation with real MC data
- Documentation for open-source release
- Optional: Rounded corners (`╭`, `╮`, `╰`, `╯`), line style options

**Library Interface** (already implemented):
```python
from visualflow import DAG, render_dag

dag = DAG()
dag.add_node("a", "┌─────┐\n│  A  │\n└─────┘")
dag.add_node("b", "┌─────┐\n│  B  │\n└─────┘")
dag.add_edge("a", "b")

diagram = render_dag(dag)
```

**Mission Control Adapter** (future):
```python
from visualflow.adapters.mission_control import from_tasks

tasks = list_tasks(project_slug="my-project")
diagram = from_tasks(tasks, milestone_filter="core")
```

**Success Criteria**:
- MC adapter validates library with real data
- Documentation sufficient for external users
- Performance <1 second for 30 nodes
- PyPI publishable

---

## Execution Order

1. **PoC 0 - Exploration** ✅ Complete
   - Create test infrastructure
   - Test all three engines
   - Document findings

2. **PoC 1 - Architecture Foundation** ✅ Complete
   - Implement based on PoC 0 findings
   - Build core components (models, engines, canvas)
   - 167 tests passing

3. **PoC 2 - Edge Routing** ✅ Complete
   - Fix canvas unicode handling (wcwidth)
   - Implement SimpleRouter with Z-shape and L-shape routing
   - Box-drawing corners (`┌┐└┘`) and T-junctions (`┬┴├┤`)
   - 220 tests passing

4. **PoC 3 - Box Connectors** (requires PoC 2)
   - Add `┬` on box bottom borders where edges exit
   - Handle fan-out with multiple connectors
   - Polish diagram appearance

5. **PoC 4 - Interface Layer** (requires PoC 3, future)
   - Mission Control adapter
   - PyPI release preparation
   - Documentation

---

## Integration Points

**PoC 0 → PoC 1**:
- Comparison matrix informs engine selection
- Test scenarios become regression tests
- Coordinate system understanding informs Canvas design

**PoC 1 → PoC 2**:
- `LayoutEngine.compute()` provides node positions
- `Canvas.place_box()` positions boxes correctly
- `EdgePath` model ready for routing output

**PoC 2 → PoC 3**:
- `EdgeRouter` computes edge paths with exit points
- `Canvas.draw_edge()` renders connections
- Edge exit coordinates available for connector placement

**PoC 3 → PoC 4**:
- Polished diagrams with integrated connectors
- `render_dag()` produces publication-quality output
- Ready for MC adapter integration

**PoC 4 → Future**:
- `render_dag()` function is the public API
- Claude skill will call this function
- Output string can be displayed directly in conversation

---

## Risk Assessment

| PoC | Risk Level | Risk | Mitigation |
|-----|------------|------|------------|
| PoC 0 | ~~Medium~~ | ~~No engine handles variable node sizes well~~ | ✅ Grandalf handles it well |
| PoC 0 | ~~Low~~ | ~~ascii-dag subprocess integration complex~~ | ✅ Not needed, Grandalf sufficient |
| PoC 1 | ~~Low~~ | ~~90% coverage hard to achieve~~ | ✅ Achieved with 167 tests |
| PoC 2 | ~~Medium~~ | ~~Edge routing produces ugly diagrams~~ | ✅ Box-drawing corners look clean |
| PoC 2 | ~~Medium~~ | ~~Canvas unicode handling breaks tests~~ | ✅ wcwidth integration works |
| PoC 3 | Low | Connector placement affects box content | Post-process after box placement |
| PoC 3 | Low | Multiple connectors on narrow boxes | Center connectors, handle edge cases |
| PoC 4 | Low | list_tasks output format changes | Use snapshot tests; adapt as needed |
| PoC 4 | Low | Performance issues with large graphs | Add filtering; set 50-node limit |

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

**PoC 2 must answer**: ✅ Answered
- ~~What routing algorithm handles all 7 fixtures well?~~ → SimpleRouter with Z-shape and L-shape
- ~~How to handle edge-box collisions?~~ → `_safe_put_edge_char` preserves box content
- ~~Are unicode edge characters (╭╮╰╯) needed or can we use basic box-drawing?~~ → Basic box-drawing (`┌┐└┘┬┴├┤`) is sufficient

**PoC 3 must answer**:
- How to identify edge exit points on box borders?
- Should connectors be added during box placement or as post-processing?
- How to handle variable box widths for connector centering?
- How to calculate x-offsets for multiple edges from same source?
- Should routing be aware of edge grouping (e.g., diamond targets vs independent)?

**PoC 4 must answer**:
- ~~What should we name the library?~~ → `visualflow` (decided)
- ~~Fork ascii-dag or build inspired-by?~~ → Inspired-by (decided)
- How to structure adapters for different data sources?
- What's the minimal public API for v1.0?

---

## Success Definition

**Milestone Complete When**:
1. All PoCs pass their success criteria (PoC 0-3 core, PoC 4 optional)
2. **Diagram quality is flawless** - no compromises
3. Standalone library works independently of Mission Control
4. MC adapter validates library with real `list_tasks` data
5. Architecture documented and >90% tested
6. No unanswered technical questions
7. Library ready for open-source release (PyPI-publishable)
8. Ready for Claude skill integration in future milestone

**Quality Standard**: If a diagram doesn't look like it was carefully hand-drawn by a human, it's not done.

---

*Document Status*: PoC 0-2 Complete, Ready for PoC 3
*Last Updated*: January 2026
