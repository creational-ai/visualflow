# Future Improvements

> **Status**: Backlog items for future development
> **Created**: 2026-01-17

---

## TODO 1: Remove ascii-dag References ✅ DONE

### Problem

The `ascii-dag/` directory is in `.gitignore` but:
- `tests/test_ascii_dag.py` exists and references it
- 16 files mention "ascii-dag" (mostly docs from PoC 0 evaluation)
- If someone clones the repo, tests will skip (not fail), but it's confusing

### Current State

```
.gitignore:47  → ascii-dag/
tests/test_ascii_dag.py → 320 lines, all tests skip if not built
```

The test file uses `pytest.mark.skipif` so it won't break builds:
```python
pytestmark = pytest.mark.skipif(
    not is_ascii_dag_built(),
    reason="ascii-dag not built (run: cd ascii-dag && cargo build --release --examples)",
)
```

### Options

| Option | Pros | Cons |
|--------|------|------|
| **A. Delete test file** | Clean, no confusion | Lose historical reference |
| **B. Move to `docs/archive/`** | Preserves research | Still exists in repo |
| **C. Keep as-is** | Zero effort | Confusing for contributors |

### Recommendation

**Option A: Delete `tests/test_ascii_dag.py`**

Rationale:
- ascii-dag was evaluated and rejected in PoC 0
- The research findings are already documented in `docs/visual-poc0-results.md`
- The test file serves no purpose - it just skips
- Doc references are fine (historical context), but dead test code isn't

### Action Items

- [x] Delete `tests/test_ascii_dag.py`
- [x] Remove `ascii-dag/` from `.gitignore` (no longer needed)
- [x] Delete `ascii-dag/` folder
- [x] Keep doc references (they explain why we chose Grandalf)
- [x] Verify all tests pass (275 passing)

---

## TODO 2: Smart Graph Organization

### Problem

When rendering a DAG with mixed connected and standalone nodes, the standalone nodes appear in random positions, making the diagram harder to read.

Example: 10 tasks where 7 are connected (have dependencies) and 3 are standalone. Currently, standalone nodes scatter randomly among the connected graph.

### Two-Part Solution

#### Part 1: Smart Default in `render_dag()`

`render_dag(dag)` should automatically organize output:
- Connected subgraphs at top (largest first)
- Standalone nodes grouped at bottom

**User code** (unchanged):
```python
print(render_dag(dag))
```

**New behavior**:
```
┌─────────┐
│ Task A  │        ← Largest connected graph
└────┬────┘
     │
     ▼
┌─────────┐
│ Task B  │
└─────────┘

┌─────────┐
│ Task X  │        ← Second connected graph (if any)
└────┬────┘
     │
     ▼
┌─────────┐
│ Task Y  │
└─────────┘

┌───────────┐  ┌───────────┐  ┌───────────┐
│Standalone1│  │Standalone2│  │Standalone3│   ← Standalones at bottom
└───────────┘  └───────────┘  └───────────┘
```

#### Part 2: `partition_dag()` Utility for Advanced Users

```python
connected_graphs, standalones = partition_dag(dag)
```

| Return | Type | Description |
|--------|------|-------------|
| `connected_graphs` | `list[DAG]` | Connected subgraphs, sorted by size (largest first) |
| `standalones` | `DAG` | All nodes with no edges |

**Advanced user code**:
```python
connected_graphs, standalones = partition_dag(dag)

# Render only the main graph
print(render_dag(connected_graphs[0]))

# Or render with custom headers
print("## Main Graph")
print(render_dag(connected_graphs[0]))

if len(connected_graphs) > 1:
    print("\n## Secondary Graphs")
    for g in connected_graphs[1:]:
        print(render_dag(g))

if standalones.nodes:
    print("\n## Standalone Tasks")
    print(render_dag(standalones))
```

### Scenarios

#### Scenario A: Simple User - Just Wants a Diagram
```python
dag = DAG()
# ... adds 10 nodes (7 connected, 3 standalone) ...
print(render_dag(dag))  # Just works - organized automatically
```

#### Scenario B: Advanced User - Custom Rendering
```python
connected_graphs, standalones = partition_dag(dag)
# Full control over how to render each part
```

#### Scenario C: Multiple Disconnected Subgraphs
Input: A→B→C→D→E (5 nodes) + X→Y (2 nodes) + P, Q, R (3 standalone)

```python
connected_graphs, standalones = partition_dag(dag)

len(connected_graphs)        # 2
len(connected_graphs[0].nodes)  # 5 (largest first)
len(connected_graphs[1].nodes)  # 2
len(standalones.nodes)       # 3
```

#### Scenario D: All Connected (Common Case)
```python
connected_graphs, standalones = partition_dag(dag)

len(connected_graphs)     # 1
len(standalones.nodes)    # 0
```

#### Scenario E: All Standalone
```python
connected_graphs, standalones = partition_dag(dag)

len(connected_graphs)     # 0
len(standalones.nodes)    # 5
```

### Implementation Location

- `partition_dag()`: New function in `src/visualflow/__init__.py` or `src/visualflow/models.py`
- `render_dag()`: Update to use `partition_dag()` internally for smart organization

### Action Items

- [ ] Implement `partition_dag(dag)` → `(list[DAG], DAG)`
- [ ] Update `render_dag()` to organize: connected graphs (largest first), then standalones
- [ ] Add tests for `partition_dag()`
- [ ] Add tests for new `render_dag()` organization behavior
- [ ] Export `partition_dag` in `__all__`
- [ ] Update README with example

---

## Priority

| TODO | Priority | Effort | Impact | Status |
|------|----------|--------|--------|--------|
| Remove ascii-dag | Low | 5 min | Cleaner repo | ✅ Done |
| Smart graph organization | Medium | 1-2 hrs | Better UX for mixed graphs | Pending |

---

*Last Updated*: 2026-01-20
