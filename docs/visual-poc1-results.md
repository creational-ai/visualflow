# visual-poc1 Results

## Summary
| Attribute | Value |
|-----------|-------|
| **Status** | Complete |
| **Started** | 2026-01-16T16:24:11-0800 |
| **Completed** | 2026-01-16T16:46:11-0800 |
| **Proves** | Core data models, canvas rendering, and layout engines work together to produce positioned ASCII diagrams |

---

## Goal
Implement the architecture design: data models (Pydantic), canvas rendering, and layout engines (Grandalf, Graphviz) that together place pre-made ASCII boxes at computed positions.

---

## Success Criteria
From `docs/visual-poc1-implementation.md`:

- [x] Data models (Node, Edge, DAG, NodePosition, LayoutResult, EdgePath) implemented
- [x] Canvas places pre-made boxes at computed positions
- [x] GrandalfEngine computes positions in character coordinates
- [x] GraphvizEngine computes positions in character coordinates
- [x] All 7 test fixtures pass with both engines (verified via integration tests)
- [x] No overlapping boxes in layout output (verified for simple_chain, diamond, complex_graph)
- [x] Correct level ordering (parents above children) (verified for simple_chain, diamond, wide_fanout)

**ALL SUCCESS CRITERIA MET**

---

## Prerequisites Completed
- [x] Verify affected tests baseline - 47/47 tests passing
- [x] Pydantic dependency verified - Already installed, import works
- [x] Grandalf dependency verified - Import works
- [x] Graphviz CLI verified - dot v14.1.1 installed
- [x] Existing package structure verified

---

## Implementation Progress

### Step 0: Create Package Structure - COMPLETE
**Status**: Complete (2026-01-16T16:25:00-0800)
**Expected**: Directory structure and __init__.py files created

**Implementation**:
- Created `src/visualflow/engines/` directory with `__init__.py`
- Created `src/visualflow/render/` directory with `__init__.py`
- Created `tests/fixtures/` directory with `__init__.py`

**Test Results**: N/A (Step 0 has no tests, only structure verification)
```bash
$ ls -la src/visualflow/engines/ src/visualflow/render/ tests/fixtures/
# All directories exist with __init__.py files
```

**Verification**:
- Existing tests still pass: 47/47

**Issues**: None

**Lessons Learned**:
- Step 0 is simple directory setup - no code or tests needed
- Verification is just confirming structure exists and existing tests pass

**Result**: Package structure ready for implementation steps.

---

### Step 1: Data Models - COMPLETE
**Status**: Complete (2026-01-16T16:28:08-0800)
**Expected**: Node, Edge, DAG, NodePosition, LayoutResult, EdgePath Pydantic models

**Implementation**:
- Created `src/visualflow/models.py` with all 6 Pydantic models
- `Node`: id, content fields with computed `width` and `height` properties using wcwidth
- `Edge`: source, target fields for directed edges
- `DAG`: nodes dict, edges list, with `add_node()`, `add_edge()`, `get_node()` methods
- `NodePosition`: node reference with x, y integer coordinates
- `LayoutResult`: positions dict, canvas width/height
- `EdgePath`: source_id, target_id, segments list for edge routing (PoC2)

**Test Results**: 20/20 tests passing
```bash
$ uv run pytest tests/test_models.py -v
tests/test_models.py::TestNode::test_node_creation PASSED
tests/test_models.py::TestNode::test_node_width_single_line PASSED
tests/test_models.py::TestNode::test_node_width_multiline PASSED
tests/test_models.py::TestNode::test_node_height_single_line PASSED
tests/test_models.py::TestNode::test_node_height_multiline PASSED
tests/test_models.py::TestNode::test_node_empty_content PASSED
tests/test_models.py::TestNode::test_node_box_content PASSED
tests/test_models.py::TestNode::test_node_width_with_emoji PASSED
tests/test_models.py::TestNode::test_node_width_with_cjk PASSED
tests/test_models.py::TestEdge::test_edge_creation PASSED
tests/test_models.py::TestDAG::test_dag_creation_empty PASSED
tests/test_models.py::TestDAG::test_dag_add_node PASSED
tests/test_models.py::TestDAG::test_dag_add_edge PASSED
tests/test_models.py::TestDAG::test_dag_get_node_exists PASSED
tests/test_models.py::TestDAG::test_dag_get_node_not_found PASSED
tests/test_models.py::TestDAG::test_dag_multiple_nodes_and_edges PASSED
tests/test_models.py::TestNodePosition::test_node_position_creation PASSED
tests/test_models.py::TestLayoutResult::test_layout_result_creation PASSED
tests/test_models.py::TestEdgePath::test_edge_path_creation_empty PASSED
tests/test_models.py::TestEdgePath::test_edge_path_with_segments PASSED
============================== 20 passed in 0.10s ==============================
```

**Existing Tests**: 47/47 still passing (baseline preserved)

**Issues**: None

**Lessons Learned**:
- Pydantic `computed_field` with `@property` decorator works well for derived values like width/height
- `wcwidth.wcswidth()` returns -1 for strings with non-printable chars, so fallback to `len()` is necessary
- Empty string splits to `['']` so height=1 for empty content (edge case to be aware of)
- Pydantic models provide automatic validation - passing wrong types raises errors immediately

**Result**: All data models implemented and tested. Ready for Step 2 (LayoutEngine Protocol)

---

### Step 2: LayoutEngine Protocol - COMPLETE
**Status**: Complete (2026-01-16T16:29:48-0800)
**Expected**: LayoutEngine protocol interface

**Implementation**:
- Created `src/visualflow/engines/base.py` with `LayoutEngine` Protocol class
- Protocol defines single method `compute(dag: DAG) -> LayoutResult`
- All coordinates specified as character units (x = columns, y = rows)
- Updated `src/visualflow/engines/__init__.py` to export `LayoutEngine`

**Test Results**: 2/2 tests passing
```bash
$ uv run pytest tests/test_engines.py::TestLayoutEngineProtocol -v
tests/test_engines.py::TestLayoutEngineProtocol::test_mock_engine_implements_protocol PASSED
tests/test_engines.py::TestLayoutEngineProtocol::test_protocol_requires_compute_method PASSED
============================== 2 passed in 0.07s ==============================
```

**Existing Tests**: 20/20 model tests still passing (baseline preserved)

**Issues**: None

**Lessons Learned**:
- Python `Protocol` class (from typing module) enables structural subtyping - any class with matching method signatures satisfies the protocol
- MockEngine demonstrates protocol compliance without explicit inheritance
- Protocol approach allows adding new engine implementations without modifying base class
- Tests verify both type annotation compatibility and runtime behavior

**Result**: LayoutEngine Protocol defined. Ready for Step 3 (Canvas Class)

---

### Step 3: Canvas Class - COMPLETE
**Status**: Complete (2026-01-16T16:31:22-0800)
**Expected**: Canvas class for ASCII rendering

**Implementation**:
- Created `src/visualflow/render/canvas.py` with Canvas Pydantic model
- `width`, `height` properties for canvas dimensions
- `_grid` as PrivateAttr - 2D character array initialized via `@model_validator`
- `place_box(content, x, y)` - places pre-made box at position, handles clipping
- `put_char(char, x, y)` - places single character, ignores out-of-bounds
- `get_char(x, y)` - retrieves character at position
- `render()` - outputs final string with trailing spaces stripped
- Updated `src/visualflow/render/__init__.py` to export `Canvas`

**Test Results**: 14/14 tests passing
```bash
$ uv run pytest tests/test_canvas.py -v
tests/test_canvas.py::TestCanvasCreation::test_canvas_creation PASSED
tests/test_canvas.py::TestCanvasCreation::test_canvas_initialized_with_spaces PASSED
tests/test_canvas.py::TestCanvasPutChar::test_put_char_valid_position PASSED
tests/test_canvas.py::TestCanvasPutChar::test_put_char_out_of_bounds_ignored PASSED
tests/test_canvas.py::TestCanvasPlaceBox::test_place_box_simple PASSED
tests/test_canvas.py::TestCanvasPlaceBox::test_place_box_at_origin PASSED
tests/test_canvas.py::TestCanvasPlaceBox::test_place_box_partial_clip_right PASSED
tests/test_canvas.py::TestCanvasPlaceBox::test_place_box_partial_clip_bottom PASSED
tests/test_canvas.py::TestCanvasPlaceBox::test_place_multiple_boxes PASSED
tests/test_canvas.py::TestCanvasRender::test_render_empty_canvas PASSED
tests/test_canvas.py::TestCanvasRender::test_render_single_char PASSED
tests/test_canvas.py::TestCanvasRender::test_render_box PASSED
tests/test_canvas.py::TestCanvasRender::test_render_strips_trailing_spaces PASSED
tests/test_canvas.py::TestCanvasRender::test_render_unicode_box PASSED
============================== 14 passed in 0.06s ==============================
```

**Existing Tests**: 22/22 still passing (20 model + 2 engine protocol)

**Issues**: None

**Lessons Learned**:
- Pydantic `PrivateAttr` with `model_validator(mode="after")` is the correct pattern for initializing internal state that depends on model fields
- Canvas coordinates: x = column (horizontal), y = row (vertical), origin at top-left
- Clipping is handled gracefully by checking bounds in place_box - content outside canvas is silently ignored
- `render()` strips trailing spaces per line AND trailing empty lines to produce clean output
- Unicode box-drawing characters work correctly since Canvas just stores characters without interpretation

**Result**: Canvas class implemented and tested. Ready for Step 4 (Test Fixtures with Real Box Content)

---

### Step 4: Test Fixtures with Real Box Content - COMPLETE
**Status**: Complete (2026-01-16T16:34:27-0800)
**Expected**: 7 test fixtures with realistic box content

**Implementation**:
- Created `tests/fixtures/boxes.py` with helper functions:
  - `make_simple_box(label, width)` - creates 3-line box with centered label
  - `make_detailed_box(title, subtitle, status, width)` - creates 5-line box like Mission Control tasks
  - Pre-made box constants: BOX_POC1 through BOX_POC8, BOX_STANDALONE_A, BOX_STANDALONE_B
- Created 7 fixture files:
  - `simple_chain.py` - A -> B -> C (3 nodes, 2 edges)
  - `diamond.py` - poc-1, poc-2 -> poc-3 -> poc-7 (4 nodes, 3 edges)
  - `wide_fanout.py` - poc-3 -> 5 children (6 nodes, 5 edges)
  - `merge_branch.py` - merge with independent branch (4 nodes, 3 edges)
  - `skip_level.py` - a -> b -> c1, a -> c2 with skip edge (4 nodes, 3 edges)
  - `standalone.py` - two disconnected nodes (2 nodes, 0 edges)
  - `complex_graph.py` - real-world mix of patterns (9 nodes, 8 edges)
- Updated `tests/fixtures/__init__.py` to export all `create_*` functions
- Created `tests/test_new_fixtures.py` with validation tests

**Test Results**: 17/17 tests passing
```bash
$ uv run pytest tests/test_new_fixtures.py -v
tests/test_new_fixtures.py::TestSimpleChainFixture::test_has_three_nodes PASSED
tests/test_new_fixtures.py::TestSimpleChainFixture::test_has_two_edges PASSED
tests/test_new_fixtures.py::TestSimpleChainFixture::test_nodes_have_content PASSED
tests/test_new_fixtures.py::TestDiamondFixture::test_has_four_nodes PASSED
tests/test_new_fixtures.py::TestDiamondFixture::test_has_three_edges PASSED
tests/test_new_fixtures.py::TestWideFanoutFixture::test_has_six_nodes PASSED
tests/test_new_fixtures.py::TestWideFanoutFixture::test_has_five_edges PASSED
tests/test_new_fixtures.py::TestMergeBranchFixture::test_has_four_nodes PASSED
tests/test_new_fixtures.py::TestMergeBranchFixture::test_has_three_edges PASSED
tests/test_new_fixtures.py::TestSkipLevelFixture::test_has_four_nodes PASSED
tests/test_new_fixtures.py::TestSkipLevelFixture::test_has_three_edges PASSED
tests/test_new_fixtures.py::TestSkipLevelFixture::test_has_skip_edge PASSED
tests/test_new_fixtures.py::TestStandaloneFixture::test_has_two_nodes PASSED
tests/test_new_fixtures.py::TestStandaloneFixture::test_has_no_edges PASSED
tests/test_new_fixtures.py::TestComplexGraphFixture::test_has_nine_nodes PASSED
tests/test_new_fixtures.py::TestComplexGraphFixture::test_has_eight_edges PASSED
tests/test_new_fixtures.py::TestComplexGraphFixture::test_nodes_have_varying_sizes PASSED
============================== 17 passed in 0.07s ==============================
```

**Existing Tests**: 36/36 still passing (20 model + 14 canvas + 2 engine protocol)

**Issues**: None

**Lessons Learned**:
- Fixtures use the new Pydantic DAG model from models.py - validates structure automatically
- Pre-made box constants (BOX_POC1, etc.) represent realistic Mission Control task content
- Helper functions `make_simple_box` and `make_detailed_box` enable consistent box creation
- Test coverage verifies node counts, edge counts, and structural properties (e.g., all edges from single parent in wide_fanout)
- Varying box widths in complex_graph tests that layout engines handle heterogeneous node sizes

**Result**: All 7 fixtures created and tested. Ready for Step 5 (GrandalfEngine Implementation)

---

### Step 5: GrandalfEngine Implementation - COMPLETE
**Status**: Complete (2026-01-16T16:38:46-0800)
**Expected**: GrandalfEngine implementing LayoutEngine protocol

**Implementation**:
- Created `src/visualflow/engines/grandalf.py` with GrandalfEngine class
- `_VertexView` plain class (not Pydantic) - Grandalf mutates xy attribute during layout
- `GrandalfEngine` with configurable `horizontal_spacing` and `vertical_spacing`
- `compute(dag: DAG) -> LayoutResult` implements the LayoutEngine protocol
- `_build_grandalf_graph()` - converts DAG to Grandalf Vertex/Edge format
- `_convert_positions()` - converts float center coordinates to integer top-left coordinates
- `_calculate_canvas_size()` - computes canvas dimensions with padding
- Updated `src/visualflow/engines/__init__.py` to export `GrandalfEngine`

**Test Results**: 20/20 tests passing
```bash
$ uv run pytest tests/test_engines.py -v
tests/test_engines.py::TestLayoutEngineProtocol::test_mock_engine_implements_protocol PASSED
tests/test_engines.py::TestLayoutEngineProtocol::test_protocol_requires_compute_method PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_engine_creation PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_engine_custom_spacing PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_empty_dag PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_single_node PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_level_ordering PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_canvas_size_positive PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_positions_are_integers PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_roots_above_children PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_siblings_same_level PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_children_below_parent PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_children_spread_horizontally PASSED
tests/test_engines.py::TestGrandalfEngineStandalone::test_disconnected_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_simple_chain_no_overlap PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_diamond_no_overlap PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_complex_graph_no_overlap PASSED
============================== 20 passed in 0.07s ==============================
```

**Existing Tests**: 51/51 still passing (20 model + 14 canvas + 17 fixture tests)

**Test Coverage**:
- TestGrandalfEngineBasic: 4 tests (creation, custom spacing, empty DAG, single node)
- TestGrandalfEngineSimpleChain: 4 tests (all nodes, level ordering, canvas size, integer positions)
- TestGrandalfEngineDiamond: 3 tests (all nodes, roots above children, siblings same level)
- TestGrandalfEngineWideFanout: 3 tests (all nodes, children below parent, horizontal spread)
- TestGrandalfEngineStandalone: 1 test (disconnected nodes positioned)
- TestGrandalfEngineNoOverlap: 3 tests (simple_chain, diamond, complex_graph)

**Issues**: None

**Lessons Learned**:
- `_VertexView` must be a plain class, not Pydantic - Grandalf mutates `xy` attribute directly during `sug.draw()`
- Grandalf provides center coordinates as floats; conversion to top-left integer coords requires: `int(cx - w/2 - min_x) + spacing`
- Grandalf automatically handles connected components via `graph.C` list - layout each separately
- Position normalization (subtracting min_x/min_y) ensures all coordinates are positive
- Explicit no-overlap tests verify Sugiyama algorithm respects box dimensions
- Level ordering tests verify topological sort places parents above children

**Result**: GrandalfEngine fully implemented and tested. Ready for Step 6 (GraphvizEngine Implementation)

---

### Step 6: GraphvizEngine Implementation - COMPLETE
**Status**: Complete (2026-01-16T16:42:17-0800)
**Expected**: GraphvizEngine implementing LayoutEngine protocol

**Implementation**:
- Created `src/visualflow/engines/graphviz.py` with GraphvizEngine class
- `_PlainNode` Pydantic model for parsed Graphviz plain output (name, x, y, width, height)
- `GraphvizEngine` with configurable `horizontal_spacing` and `vertical_spacing`
- `is_available()` static method - checks if `dot` command is in PATH using `shutil.which`
- `compute(dag: DAG) -> LayoutResult` implements the LayoutEngine protocol
- `_generate_dot()` - converts DAG to DOT format (hyphens in node IDs converted to underscores)
- `_run_graphviz()` - subprocess call to `dot -Tplain` with 30s timeout
- `_parse_plain_output()` - parses node lines from plain format
- `_convert_positions()` - converts inches to chars, flips y-axis (Graphviz origin is bottom-left)
- `_calculate_canvas_size()` - computes canvas dimensions with padding
- Updated `src/visualflow/engines/__init__.py` to export `GraphvizEngine`

**Test Results**: 30/30 tests passing
```bash
$ uv run pytest tests/test_engines.py -v
tests/test_engines.py::TestLayoutEngineProtocol::test_mock_engine_implements_protocol PASSED
tests/test_engines.py::TestLayoutEngineProtocol::test_protocol_requires_compute_method PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_engine_creation PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_engine_custom_spacing PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_empty_dag PASSED
tests/test_engines.py::TestGrandalfEngineBasic::test_single_node PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_level_ordering PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_canvas_size_positive PASSED
tests/test_engines.py::TestGrandalfEngineSimpleChain::test_positions_are_integers PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_roots_above_children PASSED
tests/test_engines.py::TestGrandalfEngineDiamond::test_siblings_same_level PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_children_below_parent PASSED
tests/test_engines.py::TestGrandalfEngineWideFanout::test_children_spread_horizontally PASSED
tests/test_engines.py::TestGrandalfEngineStandalone::test_disconnected_nodes_positioned PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_simple_chain_no_overlap PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_diamond_no_overlap PASSED
tests/test_engines.py::TestGrandalfEngineNoOverlap::test_complex_graph_no_overlap PASSED
tests/test_engines.py::TestGraphvizEngineAvailability::test_is_available_returns_bool PASSED
tests/test_engines.py::TestGraphvizEngineBasic::test_engine_creation PASSED
tests/test_engines.py::TestGraphvizEngineBasic::test_empty_dag PASSED
tests/test_engines.py::TestGraphvizEngineBasic::test_single_node PASSED
tests/test_engines.py::TestGraphvizEngineSimpleChain::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGraphvizEngineSimpleChain::test_level_ordering PASSED
tests/test_engines.py::TestGraphvizEngineDiamond::test_all_nodes_positioned PASSED
tests/test_engines.py::TestGraphvizEngineDiamond::test_roots_above_children PASSED
tests/test_engines.py::TestGraphvizEngineNoOverlap::test_simple_chain_no_overlap PASSED
tests/test_engines.py::TestGraphvizEngineNoOverlap::test_complex_graph_no_overlap PASSED
============================== 30 passed in 1.09s ==============================
```

**Existing Tests**: 51/51 still passing (20 model + 14 canvas + 17 fixture tests)

**Test Coverage (GraphvizEngine)**:
- TestGraphvizEngineAvailability: 1 test (is_available returns bool)
- TestGraphvizEngineBasic: 3 tests (creation, empty DAG, single node) - all with @skipif
- TestGraphvizEngineSimpleChain: 2 tests (all nodes positioned, level ordering) - with @skipif
- TestGraphvizEngineDiamond: 2 tests (all nodes positioned, roots above children) - with @skipif
- TestGraphvizEngineNoOverlap: 2 tests (simple_chain, complex_graph) - with @skipif

**Issues**: None

**Lessons Learned**:
- `shutil.which("dot")` is the clean way to check if Graphviz is installed - returns path or None
- Node ID sanitization (hyphens to underscores) is critical for DOT format compatibility
- Graphviz plain output format: `node <name> <x> <y> <width> <height> <label> ...` with coordinates in inches
- Y-axis flip required: Graphviz origin is bottom-left, terminal origin is top-left
- Conversion factors (CHARS_PER_INCH=10.0, LINES_PER_INCH=2.0) work well for readable layouts
- `@pytest.mark.skipif` with static method check allows tests to gracefully skip when Graphviz not installed
- Subprocess timeout (30s) prevents hanging on malformed input

**Result**: GraphvizEngine fully implemented and tested. Ready for Step 7 (Integration - Canvas with Layout Engine)

---

### Step 7: Integration - Canvas with Layout Engine - COMPLETE
**Status**: Complete (2026-01-16T16:46:11-0800)
**Expected**: render_dag function combining layout engine and canvas

**Implementation**:
- Updated `src/visualflow/__init__.py` with all public API exports:
  - Models: DAG, Node, Edge, LayoutResult, NodePosition, EdgePath
  - Engines: LayoutEngine, GrandalfEngine, GraphvizEngine
  - Rendering: Canvas, render_dag
- Created `render_dag(dag, engine=None)` helper function:
  - Accepts DAG and optional LayoutEngine
  - Defaults to GrandalfEngine if no engine provided
  - Computes layout, creates canvas, places boxes, returns rendered string
- Fixed GrandalfEngine to handle disconnected components:
  - Each component now offset horizontally to prevent overlap
  - Uses `component.sV` to access vertices in each connected component
- Created `tests/test_integration.py` with 20 tests:
  - TestRenderDagGrandalf: 8 tests (all 7 fixtures + empty DAG)
  - TestRenderDagGraphviz: 7 tests (all 7 fixtures with @skipif)
  - TestRenderDagDefaultEngine: 1 test (verifies default engine is Grandalf)
  - TestVisualInspection: 4 tests (print output for manual review)

**Test Results**: 20/20 tests passing
```bash
$ uv run pytest tests/test_integration.py -v
tests/test_integration.py::TestRenderDagGrandalf::test_render_simple_chain PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_diamond PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_wide_fanout PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_merge_branch PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_skip_level PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_standalone PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_complex_graph PASSED
tests/test_integration.py::TestRenderDagGrandalf::test_render_empty_dag PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_simple_chain PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_diamond PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_wide_fanout PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_merge_branch PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_skip_level PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_standalone PASSED
tests/test_integration.py::TestRenderDagGraphviz::test_render_complex_graph PASSED
tests/test_integration.py::TestRenderDagDefaultEngine::test_default_engine_is_grandalf PASSED
tests/test_integration.py::TestVisualInspection::test_print_simple_chain PASSED
tests/test_integration.py::TestVisualInspection::test_print_diamond PASSED
tests/test_integration.py::TestVisualInspection::test_print_wide_fanout PASSED
tests/test_integration.py::TestVisualInspection::test_print_complex PASSED
============================== 20 passed in 1.08s ==============================
```

**Issues**:
- Initially standalone fixture failed - disconnected nodes were placed at the same position
- Fixed by adding component offset logic in GrandalfEngine.compute()

**Lessons Learned**:
- Grandalf layouts disconnected components independently with overlapping origins - need manual offset
- `component.sV` contains the vertices for each connected component in `graph.C`
- Visual inspection tests are valuable for human verification of ASCII output quality
- End-to-end tests should cover all fixtures to catch edge cases early
- Default engine selection makes API simpler: `render_dag(dag)` just works

**Result**: Integration complete. All components work together to render positioned ASCII diagrams.

---

## Final Validation

**All Tests**:
```bash
$ uv run pytest tests/ -v
============================= test session starts ==============================
167 passed in 8.59s
==============================
```

**Total**: 167 tests passing
- test_models.py: 20 tests
- test_canvas.py: 14 tests
- test_engines.py: 30 tests
- test_new_fixtures.py: 17 tests
- test_integration.py: 20 tests
- test_fixtures.py: 10 tests (original)
- test_grandalf.py: 19 tests (original)
- test_graphviz.py: 18 tests (original)
- test_ascii_dag.py: 19 tests (original)

**Visual Verification**:
```
============================================================
Simple Chain (Grandalf):
============================================================

    +-------------+
    |    Task A   |
    +-------------+

    +-------------+
    |    Task B   |
    +-------------+

    +-------------+
    |    Task C   |
    +-------------+
============================================================
```

---

## Key Decisions Made
| Decision | Rationale |
|----------|-----------|
| Use Pydantic BaseModel | Built-in validation, type hints, serialization |
| Protocol class for engines | Type checking without inheritance coupling |
| Separate engines/render directories | Clean module separation |
| Default to GrandalfEngine | Pure Python, no external dependencies, fast |
| Offset disconnected components | Prevents overlapping boxes in standalone fixtures |
| `__all__` exports | Explicit public API surface |

---

## Production-Grade Checklist
- [x] OOP Design: Classes with single responsibility and clear interfaces
- [x] Pydantic Models: All data structures use Pydantic BaseModel with validation
- [x] Protocol Classes: LayoutEngine is a Protocol for type checking
- [x] Strong Typing: Type hints on all functions, methods, and class attributes
- [x] No mock data: Fixtures use realistic box content
- [x] Real integrations: Grandalf and Graphviz actually called
- [x] Error handling: Graphviz availability checked, errors raised
- [x] Scalable patterns: Engine abstraction allows easy addition of new engines
- [x] Tests in same step: Each step writes AND runs its tests
- [x] Config externalized: Spacing parameters configurable
- [x] Clean separation: Models, engines, rendering in separate modules
- [x] Self-contained: Works independently; positions boxes without edges (edge routing is PoC2)

---

## What This Unlocks
- visual-poc2: Edge Routing Implementation (needs positioned boxes)

---

## Next Steps
1. Proceed to visual-poc2: Edge Routing Implementation
2. Implement simple geometric edge router
3. Add edge rendering to canvas

---

## Lessons Learned

- **Grandalf VertexView must be plain class** - Grandalf mutates the `xy` attribute directly during `sug.draw()`, so using Pydantic causes frozen model errors. Use a plain Python class with mutable attributes.

- **Grandalf disconnected components overlap by default** - Each connected component in `graph.C` is laid out independently with its own origin at (0,0). Must manually offset components horizontally using `component.sV` to access vertices per component.

- **Grandalf returns center coordinates as floats** - Conversion to top-left integer character coordinates requires: `int(center_x - width/2 - min_x) + spacing`. Forgetting the center-to-corner adjustment causes boxes to overlap.

- **Graphviz Y-axis is inverted** - Graphviz origin is bottom-left while terminal origin is top-left. Must flip Y coordinates: `max_y - node_y` during position conversion.

- **DOT format requires sanitized node IDs** - Hyphens in node IDs break DOT parsing. Convert `poc-1` to `poc_1` when generating DOT, then map back when parsing results.

- **wcwidth returns -1 for non-printable chars** - `wcwidth.wcswidth()` returns -1 for strings containing control characters. Always fallback to `len()` when wcwidth returns negative values.
