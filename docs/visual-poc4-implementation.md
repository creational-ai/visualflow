# Visual-PoC4 Implementation Plan

> **Track Progress**: See `docs/visual-poc4-results.md` for implementation status, test results, and issues.

## Overview

| Attribute | Value |
|-----------|-------|
| **Created** | 2026-01-17T01:12:57-0800 |
| **Name** | GitHub Release |
| **Type** | Feature |
| **Proves** | visualflow is properly packaged and installable from GitHub |
| **Production-Grade Because** | Proper license, metadata, documentation, and tagged release |

---

## Deliverables

- MIT LICENSE file in repository root
- Complete pyproject.toml metadata (authors, license, keywords)
- Updated README with GitHub install instructions, themes, .env config
- Git tag for version (v0.1.0)

---

## Prerequisites

### 1. Verify All Tests Pass

```bash
cd /Users/docchang/Development/visualflow && uv run pytest tests/ --tb=no -q
# Expected: 293 passed
```

---

## Success Criteria

- [ ] LICENSE file exists with MIT license text
- [ ] pyproject.toml has authors and license fields
- [ ] README has GitHub install instructions
- [ ] README documents themes and .env configuration
- [ ] Git tag v0.1.0 created
- [ ] `uv add git+https://github.com/creational-ai/visualflow.git` works

---

## Implementation Steps

### Step 0: Create LICENSE File

**Goal**: Add MIT license to repository root

Create `/Users/docchang/Development/visualflow/LICENSE`:
```
MIT License

Copyright (c) 2026 Dominic Chang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

### Step 1: Update pyproject.toml

**Goal**: Add author and license metadata

Add to `[project]` section:
```toml
license = { file = "LICENSE" }
authors = [
    { name = "Dominic Chang" },
]
keywords = ["ascii", "dag", "diagram", "graph", "visualization", "terminal"]
```

---

### Step 2: Update README.md

**Goal**: Add GitHub install instructions, themes, and .env docs

Key sections to add/update:
- Installation via `uv add git+...` and `pip install git+...`
- Themes section (DEFAULT, LIGHT, ROUNDED, HEAVY)
- Configuration section (VISUALFLOW_THEME env var)
- Correct output example with box connectors

---

### Step 3: Create Git Tag

**Goal**: Tag release for versioned installs

```bash
git tag -a v0.1.0 -m "Initial release: ASCII DAG visualization with themes"
git push origin v0.1.0
```

This enables:
```bash
uv add git+https://github.com/creational-ai/visualflow.git@v0.1.0
```

---

## What "Done" Looks Like

```bash
# 1. All tests pass
uv run pytest tests/ --tb=no -q
# Expected: 293 passed

# 2. Install from GitHub works
uv add git+https://github.com/creational-ai/visualflow.git

# 3. Package works
python -c "from visualflow import DAG, render_dag; print('visualflow installed!')"
```

---

## Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `LICENSE` | Create | MIT license text |
| `pyproject.toml` | Modify | Add authors, license |
| `README.md` | Modify | GitHub install, themes, .env config |

---

## Future: PyPI Publish

If we find a good name later, publishing to PyPI is simple:
1. Update `name` in pyproject.toml
2. Run `uv build && uv publish`

Available names (verified 2026-01-17):
- `textdag`, `boxdag`, `dagbox`, `dagdraw`, `dagrender`
- `renderdag`, `dagcanvas`, `dagascii`, `asciiflow`
