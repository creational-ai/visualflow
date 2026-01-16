# PoC 0 Comparison Matrix

> Layout engine evaluation results for Visual Milestone

**Created**: 2026-01-16
**Based on**: 66 tests across 3 layout engines with 7 standardized graph scenarios

---

## Test Results Summary

| Scenario | Grandalf | Graphviz | ascii-dag |
|----------|----------|----------|-----------|
| 1. Simple chain (A->B->C) | PASS | PASS | N/A* |
| 2. Diamond (A->B/C->D) | PASS | PASS | N/A* |
| 3. Multiple roots (A/B->C) | PASS | PASS | N/A* |
| 4. Skip-level (A->B->C + A->C) | PASS | PASS | N/A* |
| 5. Wide graph (A->B/C/D/E) | PASS | PASS | N/A* |
| 6. Deep graph (6 levels) | PASS | PASS | N/A* |
| 7. Complex (mixed patterns) | PASS | PASS | N/A* |

*\*ascii-dag cannot be tested with custom scenarios without Rust code changes. However, built-in examples demonstrate equivalent patterns (simple chain, diamond, skip-level, wide, deep, complex).*

**Test Counts**:
- Grandalf: 18 tests (all passing)
- Graphviz: 19 tests (all passing)
- ascii-dag: 19 tests (all passing - testing built artifacts and capabilities)
- Fixtures: 10 tests (all passing)
- **Total: 66 tests passing**

---

## Capability Matrix

| Capability | Grandalf | Graphviz | ascii-dag |
|------------|----------|----------|-----------|
| **Custom node dimensions** | Yes (VertexView.w, h) | Yes (width/height + fixedsize=true) | Yes (Rust API only) |
| **Coordinate output** | Float (x, y) | Float (inches, 72 DPI) | Character grid (direct ASCII) |
| **Edge routing hints** | NO | YES (spline control points) | YES (built-in, sophisticated) |
| **Disconnected components** | Yes (graph.C list) | Yes (automatic) | Yes (demonstrated in examples) |
| **Python native** | YES (pip install) | NO (subprocess to `dot`) | NO (subprocess to binary) |
| **Final ASCII output** | NO (need render step) | NO (need render step) | YES (direct output) |
| **Custom input easy** | YES (Python API) | YES (DOT format string) | NO (requires Rust code changes) |
| **Level ordering correct** | YES | YES | YES (demonstrated) |
| **Horizontal spread** | YES | YES | YES (demonstrated) |

---

## Integration Complexity

| Engine | Integration Method | Complexity | Effort Estimate | Notes |
|--------|-------------------|------------|-----------------|-------|
| **Grandalf** | Python import | **LOW** | 1 day | Pure Python, pip install, well-documented API |
| **Graphviz** | subprocess + DOT | **MEDIUM** | 2-3 days | Requires `dot` CLI, parse plain output, handle units |
| **ascii-dag** | subprocess + Rust | **HIGH** | 1-2 weeks | Requires Rust toolchain, modify source code, or build Python bindings |

**Complexity Breakdown**:

| Task | Grandalf | Graphviz | ascii-dag |
|------|----------|----------|-----------|
| Install | `pip install grandalf` | `brew install graphviz` | `cargo build --release` |
| Input format | Python objects | DOT string | Rust code modification |
| Execute | `sug.draw()` | `subprocess.run(["dot", "-Tplain"])` | `subprocess.run([binary])` |
| Parse output | Access `vertex.view.xy` | Parse plain text format | Already ASCII (no parsing) |
| Edge routing | Must compute ourselves | Parse spline points, convert | Built-in, already rendered |
| ASCII render | Must build ourselves | Must build ourselves | Already done |

---

## Value vs. Complexity Assessment

| Engine | Unique Value | Integration Complexity | Value/Complexity Score |
|--------|--------------|----------------------|------------------------|
| **Grandalf** | Pure Python, fast integration, correct level/position calculation | LOW | **HIGH** |
| **Graphviz** | Industry standard, edge spline points, battle-tested (30+ years) | MEDIUM | **MEDIUM-HIGH** |
| **ascii-dag** | Direct ASCII output, sophisticated edge routing, highest visual quality | HIGH | **LOW** (for our use case) |

**Analysis**:
1. **Grandalf** provides the best value/complexity ratio for **node positioning**
2. **Graphviz** provides additional value with **edge routing information**
3. **ascii-dag** provides the best **final output quality** but requires significant integration work

---

## Quality Assessment

| Engine | Can Produce Flawless Output? | Notes |
|--------|------------------------------|-------|
| **Grandalf** | YES (for positioning) | Correct level ordering, horizontal spread, custom dimensions |
| **Graphviz** | YES (for positioning + edge hints) | Adds spline control points for edge routing |
| **ascii-dag** | YES (for final ASCII) | Highest quality ASCII output demonstrated |

**Quality Evidence**:
- Grandalf: All 7 scenarios produce correct level ordering and horizontal positioning
- Graphviz: All 7 scenarios produce correct positions plus edge routing information
- ascii-dag: Built-in examples show flawless ASCII rendering with proper box drawing characters

---

## Decision

### Question: Do we need 3, 2, or 1 engine(s)?

### Answer: **2 engines (Grandalf + Graphviz) - with option to add ascii-dag later**

### Rationale

**Why not 1 engine (Grandalf only)?**
- Grandalf does NOT provide edge routing information
- We would need to compute edge paths ourselves based on node positions
- This is non-trivial for skip-level edges and complex graphs
- Risk: Our edge routing could be suboptimal, leading to visual quality issues

**Why not 1 engine (Graphviz only)?**
- Subprocess overhead for every diagram
- Coordinate system in inches requires conversion to character grid
- More complex integration than Grandalf
- We would still need Grandalf-level understanding of the layout algorithm for debugging

**Why not 3 engines?**
- ascii-dag integration complexity is too high for initial milestone
- No Python API means we cannot dynamically generate diagrams from our graph data
- Would require either:
  - Building Python bindings (PyO3) - 1-2 weeks effort
  - Creating a Rust CLI that accepts input - still significant effort
- Marginal benefit over Graphviz for edge routing

**Why 2 engines (Grandalf + Graphviz)?**
1. **Grandalf for primary layout**: Pure Python, fast integration, correct positioning
2. **Graphviz for edge routing reference**: Industry-standard edge routing via spline points
3. **Combined approach**: Use Grandalf positions + Graphviz edge hints for optimal results
4. **Fallback option**: Can use Graphviz-only if needed (proven to work)

**Future Option**:
- ascii-dag can be added later if we need highest-quality edge routing
- Would require building Python bindings or CLI wrapper
- Not blocking for MVP

---

## Recommended Architecture

Based on this evaluation, the recommended architecture for the Visual Milestone is:

```
                    +-----------------+
                    |   Input Graph   |
                    | (nodes, edges)  |
                    +--------+--------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
    +------------------+         +--------------------+
    |    Grandalf      |         |     Graphviz       |
    | (node positions) |         | (edge routing)     |
    +--------+---------+         +---------+----------+
              |                             |
              |   +-----------------+       |
              +-->| Layout Merger   |<------+
                  | (combine both)  |
                  +--------+--------+
                           |
                           v
                  +------------------+
                  |  ASCII Renderer  |
                  | (our own code)   |
                  +--------+---------+
                           |
                           v
                  +------------------+
                  |  ASCII Diagram   |
                  |    Output        |
                  +------------------+
```

**Components**:
1. **Input Graph**: Our TestGraph/node/edge model
2. **Grandalf Layout**: Compute node positions (x, y coordinates)
3. **Graphviz Layout**: Compute edge spline points (for routing reference)
4. **Layout Merger**: Combine Grandalf positions with Graphviz edge routing hints
5. **ASCII Renderer**: Convert coordinates to character grid, render boxes and edges

**Alternative (Simpler)**:
If edge routing complexity is too high, start with Grandalf-only:
- Use Grandalf for node positions
- Implement simple straight-line edge routing
- Upgrade to Graphviz edge hints if needed

---

## Implementation Implications for PoC 1

Based on this decision, PoC 1 (Design & Architecture) should:

1. **Define interfaces**:
   - `LayoutEngine` protocol with `compute_layout(graph) -> NodePositions`
   - `EdgeRouter` protocol with `compute_routes(graph, positions) -> EdgePaths`
   - `AsciiRenderer` protocol with `render(positions, paths) -> str`

2. **Implement adapters**:
   - `GrandalfLayoutEngine` - wraps Grandalf for node positioning
   - `GraphvizEdgeRouter` - wraps Graphviz for edge routing hints
   - `SimpleEdgeRouter` - fallback using straight lines

3. **Build renderer**:
   - Character grid allocation
   - Box rendering with Unicode characters
   - Edge path rendering with proper corners/crossings

4. **Design for extensibility**:
   - ascii-dag adapter can be added later without architecture changes
   - Multiple renderers possible (ASCII, Unicode, SVG)

---

## Summary

| Aspect | Decision |
|--------|----------|
| **Number of engines** | 2 (Grandalf + Graphviz) |
| **Primary layout** | Grandalf (positions) |
| **Edge routing** | Graphviz (spline hints) |
| **ASCII rendering** | Custom (our own code) |
| **Future option** | ascii-dag for highest quality |

**Key Insight**: The evaluation revealed that no single engine provides everything we need:
- Grandalf: Best integration, but no edge routing
- Graphviz: Edge routing, but requires subprocess/conversion
- ascii-dag: Best output quality, but no Python API

The 2-engine approach (Grandalf + Graphviz) provides the best balance of integration simplicity and output quality for the initial milestone.

---

*Generated from PoC 0 test results (66 tests across 3 engines)*
*Last updated: 2026-01-16*
