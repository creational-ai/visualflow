# visual-poc1 Overview

> **Purpose**: High-level design for PoC 1 - Design & Architecture
>
> **Important**: Each implementation step must be self-contained (works independently; doesn't break existing functionality and existing tests)

## Executive Summary

**Goal**: Build the core data models, canvas rendering, and layout engine infrastructure for ASCII DAG visualization.

**Strategy**: Bottom-up implementation - start with data models, add canvas rendering, then integrate layout engines. Each layer is independently testable.

**Migration Approach**: This is greenfield development. No existing production code to migrate - building from exploration tests (PoC 0).

---

## Current Architecture

### What We Have Today

**1. Project Structure (from PoC 0 Exploration)**
- `src/visualflow/__init__.py` - Empty package placeholder
- `tests/conftest.py` - Test fixtures with `TestNode`, `TestEdge`, `TestGraph` dataclasses
- `tests/test_grandalf.py` - Grandalf exploration tests (passing)
- `tests/test_graphviz.py` - Graphviz exploration tests (passing)
- `tests/test_fixtures.py` - Fixture validation tests (passing)

**2. PoC 0 Findings (from `docs/visual-poc0-results.md`)**
- Grandalf: Pure Python, fast (~0.03s), positions only, no edge routing
- Graphviz: Subprocess, slower (~2.79s), positions + edge spline hints
- Both engines can compute node positions for variable-sized boxes

**3. Current Dependencies**
- `grandalf>=0.8` - Layout algorithm
- `pydantic>=2.0` - Data validation
- `wcwidth>=0.2` - Unicode width calculation

**4. Limitations**
- No production data models (test fixtures use simple dataclasses)
- No canvas for rendering
- No layout engine abstraction
- Cannot generate ASCII output yet

---

## Target Architecture

### Desired State

```
                    ┌─────────────┐
                    │    DAG      │
                    │ (Pydantic)  │
                    └──────┬──────┘
                           │
                           ▼
              ┌────────────────────────┐
              │    LayoutEngine        │
              │    (Protocol)          │
              └───────────┬────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
   ┌─────────────────┐       ┌─────────────────┐
   │ GrandalfEngine  │       │ GraphvizEngine  │
   │   (fast)        │       │ (edge hints)    │
   └────────┬────────┘       └────────┬────────┘
            │                         │
            └───────────┬─────────────┘
                        │
                        ▼
              ┌─────────────────┐
              │  LayoutResult   │
              │  (positions)    │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │     Canvas      │
              │ (2D char grid)  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  ASCII Output   │
              │   (string)      │
              └─────────────────┘
```

### Key Design Principles

1. **Pydantic Models**: All data structures use Pydantic `BaseModel` with validation
2. **Protocol Classes**: Layout engines implement `LayoutEngine` protocol
3. **Strong Typing**: Type hints on all functions, methods, attributes
4. **Pluggable Engines**: Easy to add new layout engines
5. **Pre-made Boxes**: Nodes contain complete ASCII boxes (borders included)

---

## What Needs to Change

### 1. Data Models (New File)

#### `src/visualflow/models.py`
**Current**: Does not exist

**New**: Core data structures
- `Node` - Contains complete ASCII box content, computes width/height
- `Edge` - Directed (source, target) pair
- `DAG` - Container with `add_node()` and `add_edge()` methods
- `NodePosition` - Computed position for a node (x, y in characters)
- `LayoutResult` - Engine output: positions dict + canvas dimensions
- `EdgePath` - Router output for PoC 2 (placeholder)

**Validation**: Unit tests for all model operations

---

### 2. Layout Engine Protocol (New File)

#### `src/visualflow/engines/base.py`
**Current**: Does not exist

**New**: Protocol interface
- `LayoutEngine` Protocol with `compute(dag: DAG) -> LayoutResult`

**Validation**: Type checking ensures implementations satisfy protocol

---

### 3. Grandalf Engine (New File)

#### `src/visualflow/engines/grandalf.py`
**Current**: Tests exist but no production adapter

**New**: Production adapter
- `GrandalfEngine` implementing `LayoutEngine`
- Converts DAG to Grandalf format
- Converts float positions to character coordinates
- Handles disconnected components

**Validation**: All 7 test fixtures produce correct layouts

---

### 4. Graphviz Engine (New File)

#### `src/visualflow/engines/graphviz.py`
**Current**: Tests exist but no production adapter

**New**: Production adapter
- `GraphvizEngine` implementing `LayoutEngine`
- Generates DOT format, runs `dot -Tplain`
- Parses plain output, converts to character coordinates
- Node ID sanitization (hyphens to underscores)

**Validation**: All 7 test fixtures produce correct layouts

---

### 5. Canvas (New File)

#### `src/visualflow/render/canvas.py`
**Current**: Does not exist

**New**: ASCII rendering surface
- `Canvas` class with 2D character grid
- `place_box()` - Place pre-made box at position
- `put_char()` - Place single character
- `get_char()` - Read character at position
- `render()` - Output final string

**Validation**: Unit tests for all canvas operations

---

### 6. Public API (Modify)

#### `src/visualflow/__init__.py`
**Current**: Version only

**New**: Public API exports
- Export all models: `DAG`, `Node`, `Edge`, etc.
- Export engines: `LayoutEngine`, `GrandalfEngine`, `GraphvizEngine`
- Export rendering: `Canvas`
- Export helper: `render_dag()` function

**Validation**: Can import and use from `visualflow` package

---

### 7. Test Fixtures (New Directory)

#### `tests/fixtures/`
**Current**: Simple dataclasses in conftest.py

**New**: Realistic box content fixtures
- `boxes.py` - Helper functions to create boxes
- `simple_chain.py` - A → B → C
- `diamond.py` - Merge pattern
- `wide_fanout.py` - One parent, many children
- `merge_branch.py` - Multiple roots merging
- `skip_level.py` - Direct connections skipping levels
- `standalone.py` - Disconnected nodes
- `complex_graph.py` - Real-world combination

**Validation**: All fixtures create valid DAGs with proper dimensions

---

## Task Breakdown

### Step 0: Package Structure
- Create directory structure
- Create `__init__.py` files
- No code yet, just scaffolding

### Step 1: Data Models
- Implement all Pydantic models in `models.py`
- Include `wcwidth` for Unicode width calculation
- Write comprehensive unit tests

### Step 2: LayoutEngine Protocol
- Define `LayoutEngine` Protocol in `base.py`
- Create mock engine for testing
- Write protocol compliance tests

### Step 3: Canvas Class
- Implement `Canvas` in `canvas.py`
- Handle box placement and rendering
- Write canvas operation tests

### Step 4: Test Fixtures
- Create realistic box content fixtures
- Replace simple dataclass fixtures
- Write fixture validation tests

### Step 5: GrandalfEngine
- Implement production adapter
- Convert positions to character coordinates
- Write engine tests with all fixtures

### Step 6: GraphvizEngine
- Implement production adapter
- Parse plain output format
- Write engine tests with all fixtures

### Step 7: Integration
- Update `__init__.py` with public API
- Create `render_dag()` helper function
- Write end-to-end integration tests
- Visual inspection tests

---

## Implementation Approaches

### Option A: Bottom-Up (Recommended)

**Approach**: Build foundation first (models → canvas → engines → integration)

**Pros**:
- Each layer testable independently
- Clear dependencies
- Easy to debug issues
- Follows standard software architecture patterns

**Cons**:
- Can't see end-to-end results until Step 7
- May need to adjust early layers based on later findings

---

### Option B: Top-Down

**Approach**: Start with integration, stub out components

**Pros**:
- See end-to-end flow early
- Can validate API design quickly

**Cons**:
- More refactoring as details emerge
- Harder to test individual components
- Mocks can hide integration issues

---

### Option C: Vertical Slice

**Approach**: Implement one fixture end-to-end, then expand

**Pros**:
- Working system quickly
- Validates entire pipeline early

**Cons**:
- May miss edge cases initially
- Could lead to tightly coupled code
- Harder to test comprehensively

---

## Recommended Approach

**Bottom-Up (Option A)** for these reasons:

1. **Testability**: Each component has clear inputs/outputs that can be unit tested
2. **Debugging**: When something fails, we know which layer to investigate
3. **Pydantic Validation**: Models must exist before anything can use them
4. **Canvas Independence**: Canvas doesn't need engines - can test with manual positions
5. **Engine Independence**: Engines don't need canvas - output is just coordinates
6. **Clean Architecture**: Follows dependency inversion principle

---

## Files Requiring Changes

| File | Change Type | Complexity | Step |
|------|-------------|------------|------|
| `src/visualflow/engines/__init__.py` | Create | Low | 0 |
| `src/visualflow/render/__init__.py` | Create | Low | 0 |
| `tests/fixtures/__init__.py` | Create | Low | 0 |
| `src/visualflow/models.py` | Create | Medium | 1 |
| `tests/test_models.py` | Create | Medium | 1 |
| `src/visualflow/engines/base.py` | Create | Low | 2 |
| `tests/test_engines.py` | Create | Medium | 2-6 |
| `src/visualflow/render/canvas.py` | Create | Medium | 3 |
| `tests/test_canvas.py` | Create | Medium | 3 |
| `tests/fixtures/boxes.py` | Create | Low | 4 |
| `tests/fixtures/*.py` (7 files) | Create | Low | 4 |
| `tests/test_new_fixtures.py` | Create | Low | 4 |
| `src/visualflow/engines/grandalf.py` | Create | High | 5 |
| `src/visualflow/engines/graphviz.py` | Create | High | 6 |
| `src/visualflow/__init__.py` | Modify | Medium | 7 |
| `tests/test_integration.py` | Create | Medium | 7 |

**Total Estimated Effort**: 7 steps, ~22 files

---

## Testing Strategy

### 1. Unit Tests (Per Component)

| Component | Test File | Coverage Target |
|-----------|-----------|-----------------|
| Models | `test_models.py` | All model operations |
| Canvas | `test_canvas.py` | All canvas methods |
| Engines | `test_engines.py` | All 7 fixtures per engine |
| Fixtures | `test_new_fixtures.py` | Fixture validity |

### 2. Integration Tests

| Test | What It Verifies |
|------|------------------|
| `render_dag()` | End-to-end rendering works |
| Visual inspection | Output looks correct (manual) |
| No overlap | Boxes don't collide |
| Level ordering | Parents above children |

### 3. Fixture Coverage

All 7 fixtures tested with both engines:
1. `simple_chain` - Vertical alignment
2. `diamond` - Merge paths
3. `wide_fanout` - Horizontal spread
4. `merge_branch` - Multiple roots
5. `skip_level` - Cross-level edges
6. `standalone` - Disconnected components
7. `complex_graph` - Real-world combination

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Grandalf position conversion inaccurate | Medium | Extensive tests, visual inspection |
| Graphviz not installed on system | Medium | Skip tests with clear message, document requirement |
| Box overlap in complex layouts | Low | Explicit no-overlap tests for all fixtures |
| Unicode width calculation incorrect | Low | Test with emoji and CJK characters |
| Performance issues with large graphs | Low | **Deferred to PoC 2**. Current focus is correctness |

---

## Design Decisions Made

1. ✅ **Pydantic over dataclasses**: Provides validation, serialization, computed fields
2. ✅ **Protocol over ABC**: More Pythonic, better for structural typing
3. ✅ **Pre-made boxes**: Nodes contain complete ASCII boxes, not just labels
4. ✅ **wcwidth for Unicode**: Accurate width calculation for emoji/CJK
5. ✅ **Two engines**: Grandalf (fast) + Graphviz (edge hints for PoC 2)
6. ✅ **Character coordinates**: All positions in characters/lines, not inches/pixels
7. ✅ **No edge routing in PoC 1**: Focus on box positioning, edges are PoC 2

---

## Open Questions (For Later)

1. **Edge routing algorithm**: Will be decided in PoC 2 based on PoC 1 results
2. **Unicode edge characters**: Rich characters (╭╮╰╯) planned for PoC 2
3. **Performance optimization**: Will profile if needed after correctness proven

---

## Next Steps

1. ✅ Review this overview and confirm approach
2. ✅ Implementation plan already exists: `docs/visual-poc1-implementation.md`
3. → Execute implementation using Stage 3 workflow
4. → After completion, proceed to PoC 2 (Edge Routing)

---

*Document Status*: Ready for Implementation
*Last Updated*: 2026-01-16
