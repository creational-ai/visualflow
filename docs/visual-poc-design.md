# Visual Milestone PoC Design

## Milestone Overview

This milestone proves we can generate **flawless** ASCII diagrams of task dependencies. Not "good enough" - flawless. We have all the tools (Grandalf, Graphviz) and the knowledge to solve this properly. No compromises on diagram quality.

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

We have two layout engines, sophisticated edge routing logic, a theme system, and the ability to iterate. There is no excuse for subpar output. If something doesn't look right, we fix it until it does.

## PoC Dependency Diagram

```
┌──────────────────────────────────────┐
│  PoC 0: Exploration         ✅      │
│  Test layout engines                 │
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
│  PoC 3: Smart Routing        ✅     │
│  Connectors + themes + fix_junctions │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│  PoC 4: GitHub Release       ✅     │
│  LICENSE + README + Git tag          │
└──────────────────────────────────────┘
```

**Parallel tracks**: None - strictly sequential. Each PoC depends on findings/artifacts from the previous.

---

## PoCs

### PoC 0: Exploration ✅ Complete

**Proves**: We understand what each layout engine excels at and what combination provides the best value vs. complexity trade-off.

**Results**:
- Evaluated Grandalf, Graphviz, ascii-dag
- Selected two-engine architecture:
  - Grandalf: Fast positioning (~0.03s)
  - Graphviz: Edge routing hints (optional, ~2.79s)
- ascii-dag rejected (Rust compilation complexity)

**Test Scenarios** (all passing):
1. Simple chain: A → B → C
2. Diamond: A → B, A → C, B → D, C → D
3. Multiple roots: A → C, B → C
4. Skip-level: A → B → C, A → C (direct)
5. Wide graph: A → B, A → C, A → D, A → E
6. Deep graph: A → B → C → D → E → F
7. Complex: Combination of above

---

### PoC 1: Architecture Foundation ✅ Complete

**Proves**: We can build a flexible, well-tested foundation for diagram generation with box positioning.

**Delivered**:
- `LayoutEngine` protocol with two implementations (Grandalf, Graphviz)
- `Canvas` class with box rendering (place_box, render)
- Data models (Node, Edge, DAG, NodePosition, LayoutResult, EdgePath)
- `render_dag()` function for boxes-only output
- wcwidth Unicode support for emoji/CJK width
- 167 tests passing

**Architecture Decisions**:
- Primary engine: Grandalf (pure Python, fast)
- Fallback engine: Graphviz (subprocess, provides edge hints)
- Coordinate scaling: Engine-specific, normalized to character grid
- Pydantic models for validation

---

### PoC 2: Edge Routing ✅ Complete

**Proves**: We can connect positioned boxes with clean edge lines, producing complete diagrams.

**Delivered**:
- `EdgeRouter` protocol with `SimpleRouter` implementation
- `Canvas.draw_edge()` for rendering edge paths
- Box-drawing corners: `┌`, `┐`, `└`, `┘` for 90-degree turns
- T-junctions: `┬`, `┴`, `├`, `┤` for merging edges
- Z-shape and L-shape routing for offset nodes
- 220 tests passing
- 0.002s render performance

---

### PoC 3: Smart Routing ✅ Complete

**Proves**: Edge connections are visually integrated with box borders, and complex routing patterns render cleanly.

**Delivered**:
- Box connectors (`┬`) on box bottom borders where edges exit
- Trunk-and-split pattern for fan-out (1→N) scenarios
- Merge routing for fan-in (N→1) scenarios
- `fix_junctions()` post-processing for correct junction characters
- **Theme system** with 4 presets:
  - DEFAULT: ASCII (`|`, `-`, `v`)
  - LIGHT: Unicode lines (`│`, `─`, `▼`)
  - ROUNDED: Rounded corners (`╭`, `╮`, `╰`, `╯`, `▼`)
  - HEAVY: Bold lines (`┃`, `━`, `▼`)
- `.env` configuration via `VISUALFLOW_THEME`
- python-dotenv integration
- 293 tests passing

**Example Output (ROUNDED theme)**:
```
┌───────────────────────────┐
│          PoC 0            │
└─────────────┬─────────────┘
              │
              │
   ╭──────────┴──────────╮
   │                     │
   ▼                     ▼
┌─────────────┐   ┌─────────────┐
│    PoC 1    │   │    PoC 2    │
└──────┬──────┘   └──────┬──────┘
       │                 │
       ╰────────┬────────╯
                │
                ▼
       ┌─────────────┐
       │    PoC 3    │
       └─────────────┘
```

---

### PoC 4: GitHub Release ✅ Complete

**Proves**: The library is properly packaged and installable from GitHub.

**Unlocks**: `uv add git+https://github.com/creational-ai/visualflow.git` for any project.

**Depends On**: PoC 3 (polished diagrams)

**Delivered**:
- MIT LICENSE file
- pyproject.toml with authors, license, keywords
- README with GitHub install, themes, .env config
- Git tag v0.1.0

---

## Execution Order

1. **PoC 0 - Exploration** ✅ Complete
   - Created test infrastructure
   - Tested Grandalf, Graphviz, ascii-dag
   - Selected two-engine architecture

2. **PoC 1 - Architecture Foundation** ✅ Complete
   - Built core components (models, engines, canvas)
   - 167 tests passing

3. **PoC 2 - Edge Routing** ✅ Complete
   - SimpleRouter with Z-shape and L-shape routing
   - Box-drawing corners and T-junctions
   - 220 tests passing

4. **PoC 3 - Smart Routing** ✅ Complete
   - Box connectors at exit points
   - Trunk-and-split and merge patterns
   - Theme system with 4 presets
   - .env configuration
   - 293 tests passing

5. **PoC 4 - GitHub Release** ✅ Complete
   - LICENSE, pyproject.toml, README updates
   - Git tag v0.1.0

---

## Integration Points

**PoC 0 → PoC 1**:
- Comparison matrix informed engine selection
- Test scenarios became regression tests
- Coordinate system understanding informed Canvas design

**PoC 1 → PoC 2**:
- `LayoutEngine.compute()` provides node positions
- `Canvas.place_box()` positions boxes correctly
- `EdgePath` model ready for routing output

**PoC 2 → PoC 3**:
- `EdgeRouter` computes edge paths with exit points
- `Canvas.draw_edge()` renders connections
- Edge exit coordinates available for connector placement

**PoC 3 → PoC 4**:
- Library complete and tested (293 tests)
- Just needs packaging metadata and PyPI publish

---

## Risk Assessment

| PoC | Risk Level | Risk | Mitigation |
|-----|------------|------|------------|
| PoC 0 | ✅ Resolved | No engine handles variable node sizes well | Grandalf handles it well |
| PoC 0 | ✅ Resolved | ascii-dag subprocess integration complex | Not needed, Grandalf sufficient |
| PoC 1 | ✅ Resolved | 90% coverage hard to achieve | Achieved with 167 tests |
| PoC 2 | ✅ Resolved | Edge routing produces ugly diagrams | Box-drawing corners look clean |
| PoC 2 | ✅ Resolved | Canvas unicode handling breaks tests | wcwidth integration works |
| PoC 3 | ✅ Resolved | Connector placement affects box content | Post-process after box placement |
| PoC 3 | ✅ Resolved | Multiple connectors on narrow boxes | Thirds spacing, center fallback |
| PoC 3 | ✅ Resolved | Junction characters incorrect | fix_junctions() post-processing |
| PoC 4 | Low | GitHub repo not public | Ensure repo is public before tagging |

---

## Key Questions Answered

**PoC 0** ✅:
- Do we need all 3 engines? → No, 2 engines (Grandalf + Graphviz)
- What unique value does each provide? → Grandalf: speed, Graphviz: edge hints
- Coordinate system? → Character grid with engine-specific scaling

**PoC 1** ✅:
- Minimum readable box width? → Content-dependent, handled by wcwidth
- Edge collisions? → `_safe_put_edge_char` preserves box content
- Extensibility? → Protocol pattern allows multiple engines

**PoC 2** ✅:
- Routing algorithm? → SimpleRouter with Z-shape and L-shape
- Edge-box collisions? → Preserve box content, draw around
- Unicode needed? → Box-drawing sufficient, but added theme system

**PoC 3** ✅:
- Edge exit points? → Calculate from edge source positions
- Connectors: during or post? → During `place_box_connectors()`, before edges
- Multiple edges from same source? → Thirds spacing for 2, center for 3+
- Routing awareness? → Same-layer detection for trunk-and-split

**PoC 4** (remaining):
- What license? → MIT
- GitHub org? → creational-ai

---

## Success Definition

**Milestone Complete When**:
1. ✅ PoC 0-3 pass their success criteria
2. ✅ Diagram quality is flawless - no compromises
3. ✅ Standalone library works independently of Mission Control
4. ✅ Architecture documented and >90% tested (293 tests)
5. ✅ No unanswered technical questions
6. ✅ Tagged release on GitHub (PoC 4)

**Quality Standard**: If a diagram doesn't look like it was carefully hand-drawn by a human, it's not done.

---

*Document Status*: All PoCs Complete - Milestone Done
*Last Updated*: January 2026
