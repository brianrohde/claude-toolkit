---
name: test-codebase-integrity
description: |
  Comprehensive integration testing for the entire CBS Master Thesis CMT codebase (System A + B agents, LangGraph state transitions, forecasting models, data models, metrics, and feature engineering). Automatically validates code health, import chains, state machine routing, data type integrity, and numerical stability. Use this skill whenever you need to ensure codebase integrity before merging commits, syncing branches, or deploying—or when testing a specific module (agents, forecasting models, coordination layer, data structures). Triggers on: "test codebase integrity", "validate system integrity", "run full integration tests", "check codebase health", "ensure system stability", "test agents", "validate forecasting", "check state transitions", "test data models".
compatibility: Python 3.10+, LangChain/LangGraph, pandas, scikit-learn
---

# Test Codebase Integrity Skill

## Overview

This skill runs a comprehensive test suite against your CMT thesis codebase to catch breaking changes, import errors, and integration issues **before** you merge, push, or sync. It validates:

1. **Import & Initialization** — agents, state, coordinator, config all load correctly
2. **Data Models & Feature Engineering** — dataclasses instantiate, lag/price features compute correctly
3. **Integration & State Transitions** — LangGraph routing logic, end-to-end state machine execution
4. **Metrics & Numerical Stability** — MAPE/RMSE/MAE calculations, Ridge log clipping prevents overflow

## When to Use

- **Before merging a branch:** `"test codebase integrity"` → validates System A/B agents still work
- **After refactoring agents:** `"test agents"` → checks import chains and instantiation
- **After changing forecasting models:** `"validate forecasting"` → checks feature engineering and metrics
- **After state machine edits:** `"check state transitions"` → validates routing and end-to-end execution
- **Before pushing commits:** `"ensure system stability"` → full suite, detailed report with remediation steps
- **Debugging a flaky test:** `"test data models"` → isolate to one module, skip unrelated tests

## How It Works

### Step 1: Module Selection (Prompted)

You'll be asked which module to test:
- **agents** — State, Coordinator, all 4 agents (ForecastingAgent, etc.)
- **forecasting** — Feature engineering (lag_12, price_per_unit), model instantiation
- **coordination** — LangGraph graph building, routing logic, state transitions
- **data_models** — Output dataclasses (ModelForecast, SynthesisOutput, ValidationReport)
- **all** — Run all 10 tests (default, recommended for pre-sync validation)

### Step 2: Test Execution

Runs 10 integration tests in sequence:

| # | Test | Module | What It Checks |
|---|------|--------|-----------------|
| 1 | State & Coordinator Import | agents | LangGraph imports, 4 nodes load |
| 2 | Config Loading | coordination | RAM budget, LLM setup, Nielsen/Indeks configs |
| 3 | Agent Imports | agents | All 4 agents instantiate without error |
| 4 | Routing Logic | coordination | State transition rules work correctly |
| 5 | Data Models | data_models | Output dataclasses instantiate and validate |
| 6 | Feature Engineering | forecasting | lag_12, price_per_unit compute correctly |
| 7 | Metric Functions | forecasting | MAPE, RMSE, MAE handle edge cases |
| 8 | Ridge Log Clipping | forecasting | Log predictions clipped, inverse expm1 stable |
| 9 | State Transitions | coordination | Coordinator state machine end-to-end |
| 10 | Full Integration | agents | All components together, no import/init errors |

### Step 3: Output

**For each failed test:**
- ❌ Test name
- 📋 What failed (assertion, import error, type mismatch, etc.)
- 🔍 Root cause (likely reason)
- 🛠️ Remediation steps (how to fix)
- 📝 Next action (run in isolation, check file X, etc.)

**Summary:**
- Pass/fail count (e.g., 10/10 PASS, 7/10 FAIL)
- Time to run
- Go/no-go decision (safe to sync? yes/no)

## Usage Examples

### Example 1: Pre-sync Validation (Full Suite)

**User:** `"Before I push these commits, test codebase integrity"`

**Skill:**
1. Prompts: "Which module? (agents / forecasting / coordination / data_models / all)"
2. User: `"all"`
3. Runs 10 tests → shows detailed results

**Output:**
```
COMPREHENSIVE CODEBASE INTEGRITY VALIDATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Test 1: State & Coordinator Import ... [PASS]
Test 2: Config Loading ... [PASS]
...
Test 10: Full Integration ... [PASS]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY: 10/10 PASS (45.2s)

✅ GO FOR SYNC
All tests pass. Ready to merge and notify colleague.
```

### Example 2: Debugging a Failing Agent Import

**User:** `"Test agents—I think I broke something in the import chain"`

**Skill:**
1. Runs tests 1, 3, 10 (agent-specific tests)
2. Test 1 fails: `ImportError: cannot import name 'ForecastingAgent'`

**Output:**
```
Test 1: State & Coordinator Import ... [FAIL]
  Error: ImportError: cannot import name 'ForecastingAgent' 
         from 'ai_research_framework.agents'

  Root cause: 
    ForecastingAgent class not exported in agents/__init__.py
    OR missing class definition in forecasting_agent.py

  Remediation:
    1. Check agents/__init__.py line 15+
       - Is ForecastingAgent in the import list?
       - Is it in __all__?
    2. Check ai_research_framework/agents/forecasting_agent.py
       - Does the file define class ForecastingAgent?
       - Or is it a standalone script?
    3. If standalone script, add a minimal wrapper class:
       class ForecastingAgent:
           def __init__(self): pass

  Next action:
    → Read agents/__init__.py and forecasting_agent.py
    → Apply fix from remediation step 3
    → Re-run "test agents" to confirm
```

### Example 3: Validating Feature Engineering After Refactor

**User:** `"I changed how we compute lag features. Validate forecasting."`

**Skill:**
1. Runs tests 6, 7, 8 (forecasting-specific)
2. Test 6: Feature engineering works ✅
3. Test 7: Metrics work ✅
4. Test 8: Ridge clipping works ✅

**Output:**
```
Test 6: Feature Engineering ... [PASS]
Test 7: Metric Functions ... [PASS]
Test 8: Ridge Log Clipping ... [PASS]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUMMARY: 3/3 PASS (12.1s)

✅ FORECASTING MODULE VALIDATED
Feature engineering, metrics, and numerical stability all pass.
```

## Implementation Notes

### The Test Runner Script

The skill bundles a Python test runner (`scripts/test_runner.py`) that:
- Imports the 10 test functions from your existing `tests/test_agent_system_comprehensive.py`
- Accepts a module filter (`--module all|agents|forecasting|coordination|data_models`)
- Runs only the relevant tests
- Captures stdout, stderr, and timing data
- Formats output with color coding and remediation suggestions

### Reusable Across Branches

The skill can run on **any branch** in your repo—it doesn't modify files, only validates. You can:
- Run before merging a feature branch: `git checkout my-branch && test codebase integrity`
- Run after rebasing: `test agents` (just to be safe)
- Run before pushing: `test codebase integrity` (full validation)

### Idempotent

The skill can be run multiple times with no side effects. Useful for:
- Iterating on a fix: change code → test → change code → test
- CI/CD pipelines (if integrated)
- Supervisor validation (run the exact same test suite they would)

## Troubleshooting

### "Test runner script not found"

The script should be in `.claude/skills/test-codebase-integrity/scripts/test_runner.py`. If not:
1. Verify skill installation: `ls .claude/skills/test-codebase-integrity/`
2. Check git status: `git status .claude/skills/`
3. Reinstall the skill if corrupted

### "Tests pass locally but fail in CI"

Common causes:
- Python version mismatch (tests run on 3.10+, CI uses 3.8?)
- Virtual environment not activated
- Dependencies not installed (`pip install -r requirements.txt`)
- Different PYTHONPATH (relative imports breaking)

Run with verbose flag: `python tests/test_agent_system_comprehensive.py --verbose`

### "ImportError on tests, but imports work in REPL"

The test suite imports modules fresh each time. Your REPL may have cached an old import. Try:
```python
import importlib
import ai_research_framework.agents
importlib.reload(ai_research_framework.agents)
```

## Auto-Diagnosis (NEW!)

When a test fails, the skill now automatically diagnoses the issue and suggests fixes:

### How It Works

1. **Parse the error** — Extract error type and relevant details
2. **Identify likely files** — Suggest which source files are probably affected
3. **Suggest 2-3 fix hypotheses** — Ranked by confidence (HIGH, MEDIUM, LOW)
4. **Show code excerpts** — Display relevant snippets for context

### Depth Levels

Control how deeply the diagnosis reads source code:

| Level | Behavior | Use When |
|-------|----------|----------|
| **off** | No diagnosis, just test results | You already know the issue |
| **paths** | Suggest files only, don't read | Quick feedback, read files yourself |
| **excerpt** (default) | Read 20-30 lines around problem | Standard debugging workflow |
| **full** | Read entire files + deep analysis | Complex issues, unfamiliar code |

### Output Formats

Choose how diagnosis results are presented:

| Format | Output | Use When |
|--------|--------|----------|
| **text** (default) | Markdown to stdout, human-friendly | Reading during test execution |
| **json** | Structured JSON to file | Piping to other tools, logging |
| **both** | Markdown to stdout + JSON to file | Full documentation + programmatic use |

### Example Usage

**Basic:** Full diagnosis with default excerpt depth
```bash
python test_runner.py --module all
```

**Advanced:** Full analysis with JSON output
```bash
python test_runner.py --module all --diagnosis full --output-format both --diagnosis-json failures.json
```

**No Diagnosis:** Just test results
```bash
python test_runner.py --module all --diagnosis off
```

### Example Diagnosis Output

```
======================================================
DIAGNOSIS: ImportError in State & Coordinator Import
======================================================

Likely Files:
  * ai_research_framework/agents/__init__.py
  * ai_research_framework/agents/forecasting_agent.py

Suspected Problem:
  ForecastingAgent class not exported from ai_research_framework.agents

Fix Hypothesis 1 (HIGH confidence):
  Check __init__.py -- ForecastingAgent missing from imports or __all__
  Location: ai_research_framework/agents/__init__.py:1-30

  Code excerpt:
  -- __init__.py ----------------------------------------
  |   1  from .data_assessment_agent import DataAssessmentAgent
  |   2  # <- Missing: from .forecasting_agent import ForecastingAgent
  |   3  from .synthesis_agent import SynthesisAgent
  |   4  from .validation_agent import ValidationAgent
  |   5
  |   6  __all__ = [
  |   7      "DataAssessmentAgent",
  |   8      # <- Missing: "ForecastingAgent",
  |   9      "SynthesisAgent",
  |  10      "ValidationAgent",
  |  11  ]
  --------------------------------------------------

  Action: Add line to imports:
  from .forecasting_agent import ForecastingAgent

  Add to __all__:
  'ForecastingAgent'

Fix Hypothesis 2 (MEDIUM confidence):
  Check forecasting_agent.py -- class definition may not exist
  Location: ai_research_framework/agents/forecasting_agent.py

  Action: Verify file contains:
  class ForecastingAgent:
      def __init__(self): ...
      def run(self, state: dict) -> dict: ...

Fix Hypothesis 3 (LOW confidence):
  Python path issue or circular import
  Location: ai_research_framework/__init__.py

  Action: Run: python -c "import ai_research_framework.agents; print(dir())"
          Check if ForecastingAgent appears in output
```

### JSON Diagnosis Output

When using `--output-format json` or `both`, results are saved to a structured JSON file:

```json
{
  "test_results": {
    "total": 10,
    "passed": 7,
    "failed": 3,
    "elapsed_seconds": 45.2
  },
  "diagnoses": {
    "1": {
      "test_name": "State & Coordinator Import",
      "error_type": "ImportError",
      "error_message": "cannot import name 'ForecastingAgent' from 'ai_research_framework.agents'",
      "likely_files": [
        "ai_research_framework/agents/__init__.py",
        "ai_research_framework/agents/forecasting_agent.py"
      ],
      "suspected_problem": "ForecastingAgent class not exported from ai_research_framework.agents",
      "fix_hypotheses": [
        {
          "title": "Check __init__.py -- ForecastingAgent missing from imports or __all__",
          "confidence": "HIGH",
          "description": "The class ForecastingAgent may not be exported from ai_research_framework.agents",
          "file_path": "ai_research_framework/agents/__init__.py",
          "line_range": [1, 30],
          "code_excerpt": "...",
          "action": "Add line to imports: ..."
        },
        ...
      ]
    }
  }
}
```

This JSON can be piped to tools, logged, or archived for later analysis.

## Related Workflows

- **After running this skill:** Use `/git-draft-commit` to document findings
- **Before supervisor meeting:** Run `test codebase integrity` and include results in standup
- **Before major refactor:** Save results with `/plan-update-all-all` as a baseline
