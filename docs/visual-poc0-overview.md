# Visual-PoC0 Overview

> **Purpose**: Plan the exploration phase to evaluate Grandalf, ascii-dag, and Graphviz layout engines
>
> **Important**: Each task must be self-contained (works independently; doesn't break existing functionality)

## Executive Summary

**Goal**: Determine the optimal combination of layout engines (3, 2, or 1) for generating flawless ASCII diagrams of task dependencies.

**Strategy**: Test all three engines against 7 standardized graph scenarios, evaluate their capabilities, and create a decision matrix that weighs value vs. complexity for each engine.

**Approach**: Build pytest-based test suites that are repeatable and document findings systematically. No guessing - evidence-based evaluation only.

---

## Current Architecture

### What We Have Today

**1. Grandalf (Python)**
- Pure Python Sugiyama layout library (~600 lines)
- Installed via `pip install grandalf`
- Native Python integration - no subprocess needed
- Provides (x, y) coordinates and can accept custom node dimensions

```toml
# pyproject.toml
[project]
name = "visualflow"
dependencies = [
    "grandalf>=0.8",
    "pytest>=9.0.2",
    "pytest-cov>=7.0.0",
]
```

**2. ascii-dag (Rust)**
- Rust library with Sugiyama algorithm + sophisticated edge routing
- Cloned to `diagram/ascii-dag/`, compiled with `cargo build --release`
- Requires subprocess or FFI bridge for Python integration
- Has Layout IR with `LayoutNode`, `LayoutEdge`, and `EdgePath` types

```
diagram/ascii-dag/
├── src/
│   ├── graph.rs       # DAG structure
│   ├── layout.rs      # Sugiyama algorithm
│   ├── ir/mod.rs      # Layout IR (LayoutNode, LayoutEdge)
│   └── render/ascii.rs # ASCII rendering
└── target/release/    # Compiled binary
```

**3. Graphviz (C)**
- Industry standard graph visualization (30+ years)
- Installed via `brew install graphviz`
- `dot -Tplain` outputs coordinate data in plain text format
- External dependency - requires subprocess call

```bash
# Verify installation
which dot  # /opt/homebrew/bin/dot or /usr/local/bin/dot
dot -V     # Shows version
```

**4. Current Test Infrastructure**
- `tests/` directory does not exist yet
- pytest and pytest-cov are installed
- No test scenarios defined

---

## Target Architecture

### Desired State (PoC 0 Deliverables)

```
diagram/
├── pyproject.toml              # name = "visualflow"
├── src/
│   └── visualflow/             # Package (expanded in PoC 1)
│       └── __init__.py
├── tests/
│   ├── conftest.py              # Shared fixtures (7 graph scenarios)
│   ├── test_grandalf.py         # Grandalf evaluation tests
│   ├── test_ascii_dag.py        # ascii-dag evaluation tests
│   └── test_graphviz.py         # Graphviz evaluation tests
└── docs/
    └── poc0-comparison-matrix.md  # Decision matrix document
```

### Test Scenarios (Shared Fixtures)

All three engines tested against identical scenarios:

| # | Scenario | Graph Structure | Tests |
|---|----------|-----------------|-------|
| 1 | Simple chain | A → B → C | Basic vertical flow |
| 2 | Diamond | A → B, A → C, B → D, C → D | Converging paths |
| 3 | Multiple roots | A → C, B → C | Multiple entry points |
| 4 | Skip-level | A → B → C, A → C (direct) | Mixed depth edges |
| 5 | Wide graph | A → B, A → C, A → D, A → E | Horizontal spread |
| 6 | Deep graph | A → B → C → D → E → F | Many levels |
| 7 | Complex | Combination of above patterns | Real-world complexity |

### Evaluation Criteria Per Engine

| Criterion | What to Evaluate |
|-----------|------------------|
| Custom dimensions | Can it accept width/height per node? |
| Coordinate system | What units? How to scale? |
| Edge routing hints | Does it provide waypoints? |
| Disconnected components | How handled? |
| Performance | Time for 50+ nodes |
| Integration complexity | Python native vs subprocess vs FFI |
| Unique value | What does it provide that others don't? |

---

## What Needs to Change

### 1. Test Infrastructure (3 files)

#### `tests/conftest.py`
**Current**: Does not exist
**New**: Shared pytest fixtures for all 7 graph scenarios

```python
# tests/conftest.py
import pytest
from dataclasses import dataclass

@dataclass
class TestNode:
    """Node for test scenarios."""
    id: str
    label: str
    width: int = 15  # Default box width
    height: int = 3  # Default box height

@dataclass
class TestEdge:
    """Edge for test scenarios."""
    source: str
    target: str

@dataclass
class TestGraph:
    """Graph scenario for testing."""
    name: str
    nodes: list[TestNode]
    edges: list[TestEdge]

@pytest.fixture
def simple_chain() -> TestGraph:
    """Scenario 1: A → B → C"""
    return TestGraph(
        name="simple_chain",
        nodes=[
            TestNode("a", "Task A"),
            TestNode("b", "Task B"),
            TestNode("c", "Task C"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("b", "c"),
        ]
    )

@pytest.fixture
def diamond() -> TestGraph:
    """Scenario 2: A → B, A → C, B → D, C → D"""
    return TestGraph(
        name="diamond",
        nodes=[
            TestNode("a", "Root"),
            TestNode("b", "Left"),
            TestNode("c", "Right"),
            TestNode("d", "Merge"),
        ],
        edges=[
            TestEdge("a", "b"),
            TestEdge("a", "c"),
            TestEdge("b", "d"),
            TestEdge("c", "d"),
        ]
    )

# ... remaining fixtures for scenarios 3-7
```

**Validation**: `pytest tests/conftest.py --collect-only` shows all fixtures

---

#### `tests/test_grandalf.py`
**Current**: Does not exist
**New**: Grandalf evaluation tests

```python
# tests/test_grandalf.py
from grandalf.graphs import Graph, Vertex, Edge
from grandalf.layouts import SugiyamaLayout

class VertexView:
    """Custom view to set node dimensions."""
    def __init__(self, w: int = 15, h: int = 3):
        self.w = w
        self.h = h
        self.xy = (0, 0)

def test_grandalf_simple_chain(simple_chain):
    """Test Grandalf with simple chain scenario."""
    # Build graph
    vertices = {n.id: Vertex(data=n) for n in simple_chain.nodes}
    for v in vertices.values():
        v.view = VertexView(v.data.width, v.data.height)

    edges = [Edge(vertices[e.source], vertices[e.target])
             for e in simple_chain.edges]

    g = Graph(list(vertices.values()), edges)

    # Compute layout
    sug = SugiyamaLayout(g.C[0])
    sug.init_all()
    sug.draw()

    # Verify positions assigned
    for v in vertices.values():
        assert v.view.xy is not None
        x, y = v.view.xy
        assert isinstance(x, (int, float))
        assert isinstance(y, (int, float))

    # Verify level ordering (A above B above C)
    assert vertices["a"].view.xy[1] < vertices["b"].view.xy[1]
    assert vertices["b"].view.xy[1] < vertices["c"].view.xy[1]
```

**Validation**: `pytest tests/test_grandalf.py -v` shows all tests pass

---

#### `tests/test_ascii_dag.py`
**Current**: Does not exist
**New**: ascii-dag evaluation tests (via subprocess)

```python
# tests/test_ascii_dag.py
import subprocess
import json
from pathlib import Path

ASCII_DAG_BINARY = Path(__file__).parent.parent / "ascii-dag/target/release/examples"

def run_ascii_dag_example(example_name: str) -> str:
    """Run an ascii-dag example and capture output."""
    binary = ASCII_DAG_BINARY / example_name
    if not binary.exists():
        pytest.skip(f"ascii-dag example {example_name} not built")

    result = subprocess.run([str(binary)], capture_output=True, text=True)
    return result.stdout

def test_ascii_dag_builds():
    """Verify ascii-dag compiled successfully."""
    cargo_toml = Path(__file__).parent.parent / "ascii-dag/Cargo.toml"
    assert cargo_toml.exists(), "ascii-dag not cloned"

    release_dir = Path(__file__).parent.parent / "ascii-dag/target/release"
    assert release_dir.exists(), "ascii-dag not built (run: cargo build --release)"

def test_ascii_dag_basic_example():
    """Test ascii-dag's basic example produces output."""
    output = run_ascii_dag_example("basic")
    assert output, "No output from basic example"
    assert "[" in output or "─" in output, "Output doesn't look like ASCII diagram"
```

**Validation**: `pytest tests/test_ascii_dag.py -v` shows tests pass

---

#### `tests/test_graphviz.py`
**Current**: Does not exist
**New**: Graphviz evaluation tests

```python
# tests/test_graphviz.py
import subprocess
import shutil

def test_graphviz_installed():
    """Verify Graphviz is installed."""
    dot_path = shutil.which("dot")
    assert dot_path is not None, "Graphviz not installed (run: brew install graphviz)"

def test_graphviz_plain_output(simple_chain):
    """Test Graphviz plain output format."""
    # Build DOT input
    dot_input = "digraph G {\n"
    for node in simple_chain.nodes:
        dot_input += f'  {node.id} [label="{node.label}"];\n'
    for edge in simple_chain.edges:
        dot_input += f'  {edge.source} -> {edge.target};\n'
    dot_input += "}\n"

    # Run dot -Tplain
    result = subprocess.run(
        ["dot", "-Tplain"],
        input=dot_input,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"Graphviz failed: {result.stderr}"

    # Parse plain output
    lines = result.stdout.strip().split("\n")
    assert lines[0].startswith("graph"), "Expected 'graph' line"

    # Count nodes
    node_lines = [l for l in lines if l.startswith("node")]
    assert len(node_lines) == 3, f"Expected 3 nodes, got {len(node_lines)}"
```

**Validation**: `pytest tests/test_graphviz.py -v` shows tests pass

---

### 2. Comparison Matrix Document (1 file)

#### `docs/poc0-comparison-matrix.md`
**Current**: Does not exist
**New**: Decision matrix documenting findings

Template structure:
```markdown
# PoC 0 Comparison Matrix

## Test Results Summary

| Scenario | Grandalf | ascii-dag | Graphviz |
|----------|----------|-----------|----------|
| 1. Simple chain | ✓/✗ | ✓/✗ | ✓/✗ |
| 2. Diamond | ✓/✗ | ✓/✗ | ✓/✗ |
| ... | ... | ... | ... |

## Capability Matrix

| Capability | Grandalf | ascii-dag | Graphviz |
|------------|----------|-----------|----------|
| Custom node dimensions | Yes/No | Yes/No | Yes/No |
| Edge routing hints | Yes/No | Yes/No | Yes/No |
| ... | ... | ... | ... |

## Value vs. Complexity

| Engine | Value Score | Complexity Score | Recommendation |
|--------|-------------|------------------|----------------|
| Grandalf | [1-5] | [1-5] | Use/Skip |
| ascii-dag | [1-5] | [1-5] | Use/Skip |
| Graphviz | [1-5] | [1-5] | Use/Skip |

## Decision

[Answer: Do we need 3, 2, or 1 engine(s)?]
[Rationale based on evidence]
```

---

## Task Breakdown

### Task 1: Test Infrastructure Setup

**Prerequisites**: None

**Implementation Steps**:
1. Create `tests/` directory
2. Create `conftest.py` with all 7 graph scenario fixtures
3. Verify fixtures work: `pytest --collect-only`

**Success Criteria**:
- [ ] `tests/conftest.py` exists with 7 fixtures
- [ ] All fixtures can be collected by pytest
- [ ] `TestNode`, `TestEdge`, `TestGraph` dataclasses defined

---

### Task 2: Grandalf Evaluation

**Depends on**: Task 1

**Implementation Steps**:
1. Create `test_grandalf.py`
2. Test all 7 scenarios
3. Document: custom dimensions, coordinate system, edge hints
4. Evaluate quality of layout output

**Success Criteria**:
- [ ] All 7 scenarios tested
- [ ] Positions verified for correctness
- [ ] Capability findings documented
- [ ] Quality assessment: Can it produce flawless diagrams?

---

### Task 3: ascii-dag Evaluation

**Depends on**: Task 1

**Implementation Steps**:
1. Create `test_ascii_dag.py`
2. Test existing examples (basic, complex, etc.)
3. Evaluate Layout IR output format
4. Assess integration complexity (subprocess vs custom CLI)

**Success Criteria**:
- [ ] Compiled binary tested
- [ ] Output format understood
- [ ] Edge routing capabilities documented
- [ ] Quality assessment: Can it produce flawless diagrams?

---

### Task 4: Graphviz Evaluation

**Depends on**: Task 1

**Implementation Steps**:
1. Create `test_graphviz.py`
2. Test `dot -Tplain` output parsing
3. Test all 7 scenarios
4. Document coordinate system and scaling

**Success Criteria**:
- [ ] All 7 scenarios tested
- [ ] Plain output format parsed correctly
- [ ] Capability findings documented
- [ ] Quality assessment: Can it produce flawless diagrams?

---

### Task 5: Comparison Matrix & Decision

**Depends on**: Tasks 2, 3, 4

**Implementation Steps**:
1. Create `docs/poc0-comparison-matrix.md`
2. Compile test results from all three engines
3. Fill capability matrix
4. Calculate value vs. complexity scores
5. Make decision: 3, 2, or 1 engine(s)?

**Success Criteria**:
- [ ] All test results documented
- [ ] Capability matrix complete
- [ ] Value vs. complexity assessed
- [ ] Clear decision with rationale
- [ ] Quality gate: Which engine(s) can produce flawless output?

---

## Implementation Approaches

### Option A: Sequential Testing (Recommended)

**Pros**:
- Learn from each engine before moving to next
- Can adjust test scenarios based on findings
- Lower risk of wasted effort

**Cons**:
- Takes longer to complete full evaluation

---

### Option B: Parallel Testing

**Pros**:
- Faster completion
- Direct side-by-side comparison

**Cons**:
- May miss opportunities to refine scenarios
- Higher cognitive load

---

### Option C: Focus on Most Promising First

**Pros**:
- Quickly validates best candidate
- Can skip less promising engines

**Cons**:
- May miss unexpected strengths
- Violates "keep open mind" principle

---

## Recommended Approach

**Sequential Testing (Option A)** for these reasons:

1. **Evidence-based**: Each engine evaluation informs the next
2. **Quality-focused**: Can refine test scenarios to ensure flawless output detection
3. **Lower risk**: If Grandalf is sufficient, can reduce scope of later evaluations
4. **Matches principle**: "Keep an open mind" - don't pre-judge any engine

**Suggested order**: Grandalf → Graphviz → ascii-dag
- Grandalf first (simplest integration, pure Python)
- Graphviz second (well-documented, external but reliable)
- ascii-dag last (most sophisticated but highest integration complexity)

---

## Files Requiring Changes

| File | Change Type | Complexity | Task |
|------|-------------|------------|------|
| `tests/conftest.py` | Create | Medium | Task 1 |
| `tests/test_grandalf.py` | Create | Medium | Task 2 |
| `tests/test_ascii_dag.py` | Create | Medium | Task 3 |
| `tests/test_graphviz.py` | Create | Medium | Task 4 |
| `docs/poc0-comparison-matrix.md` | Create | Low | Task 5 |

**Total Estimated Effort**: 5 tasks

---

## Testing Strategy

### 1. Pytest-Based Evaluation

```bash
# Run all tests
cd diagram && uv run pytest tests/ -v

# Run specific engine tests
uv run pytest tests/test_grandalf.py -v
uv run pytest tests/test_graphviz.py -v
uv run pytest tests/test_ascii_dag.py -v

# Coverage report
uv run pytest tests/ --cov=. --cov-report=term-missing
```

### 2. Visual Inspection

Each test should output the actual diagram (or coordinates) for manual quality assessment:
- Are nodes at expected positions?
- Is level ordering correct?
- Are there any overlaps?
- Does the edge routing look clean?

---

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| No engine handles variable node sizes well | Medium | Test all three; hybrid approach if needed |
| ascii-dag subprocess integration too complex | Low | Fall back to Grandalf + Graphviz only |
| Graphviz plain output hard to parse | Low | Well-documented format; examples available |
| Tests don't reveal real quality issues | Medium | Include visual inspection in evaluation |

---

## Design Decisions Made

1. ✅ **Use pytest for all evaluations**: Repeatable, structured, documented findings
2. ✅ **7 standardized scenarios**: Same tests across all engines for fair comparison
3. ✅ **Value vs. Complexity matrix**: Objective decision criteria
4. ✅ **Sequential evaluation order**: Grandalf → Graphviz → ascii-dag

---

## Open Questions (To Answer in PoC 0)

1. **How does Grandalf handle edge routing?**: Does it provide waypoints or just node positions?
2. **Can ascii-dag output JSON Layout IR?**: Need to check if CLI exists or must be built
3. **What's Graphviz's default node spacing?**: May need to adjust for our box sizes
4. **Performance with 50+ nodes**: Is any engine too slow for real-time generation?

---

## Next Steps

1. Review this overview and confirm approach
2. Create implementation plan using Stage 2 (planning guide)
3. Implement Task 1 (test infrastructure)
4. Proceed through Tasks 2-5 sequentially
5. Complete `poc0-comparison-matrix.md` with decision

---

*Document Status*: Ready for Implementation Planning
*Last Updated*: January 2026
