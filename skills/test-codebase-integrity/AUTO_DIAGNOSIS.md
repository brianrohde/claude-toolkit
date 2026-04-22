# Auto-Diagnosis Feature

Enhanced `test-codebase-integrity` skill with automatic failure diagnosis.

## What It Does

When a test fails, the diagnosis engine automatically:
1. **Parses the error** — Extracts error type and key details
2. **Identifies likely files** — Suggests which source files are probably affected
3. **Suggests fixes** — Generates 2-3 hypotheses ranked by confidence
4. **Shows excerpts** — Displays relevant code snippets for context (optional)

## Quick Start

### Default Usage (Excerpt Depth, Text Output)

```bash
python scripts/test_runner.py --module all
```

Runs all tests with default diagnosis:
- **Depth**: excerpt (20-30 lines around problem)
- **Format**: text (human-readable Markdown to stdout)
- **Diagnosis**: enabled (fails are diagnosed automatically)

### Full Analysis with JSON Logging

```bash
python scripts/test_runner.py --module all --diagnosis full --output-format both
```

For complex issues:
- **Depth**: full (reads entire files)
- **Format**: both (Markdown to stdout + JSON to file)
- **Output file**: `diagnosis_output.json` (customizable with `--diagnosis-json`)

### No Diagnosis (Just Results)

```bash
python scripts/test_runner.py --module all --diagnosis off
```

Fastest mode:
- Skips diagnosis engine
- Returns only pass/fail summary
- Good when you already know the issue

## Command-Line Options

### `--diagnosis`
Control auto-diagnosis depth:
- `off` — No diagnosis
- `paths` — Suggest files only, don't read
- `excerpt` — Read ~30 lines (default)
- `full` — Read entire files + deep analysis

### `--output-format`
Choose output presentation:
- `text` — Markdown to stdout (default)
- `json` — Structured JSON to file
- `both` — Markdown to stdout + JSON to file

### `--diagnosis-json`
Specify JSON output path (default: `diagnosis_output.json`)

## How It Works

### Error Parsing

Diagnosis engine recognizes these error types:
- **ImportError** — Class/module not imported correctly
- **AttributeError** — Missing attribute or method
- **AssertionError** — Test assertion failed (logic/config issue)
- **TypeError** — Wrong argument types or count
- **ValueError** — Invalid value or edge case
- **ModuleNotFoundError** — Module path doesn't exist
- **Generic errors** — Fallback for other exception types

### Confidence Levels

Fix hypotheses are ranked:
- **HIGH** — Most likely cause, check this first
- **MEDIUM** — Plausible, but less probable
- **LOW** — Unlikely, but worth investigating

### Code Excerpts

In excerpt or full depth mode, diagnosis shows relevant code:
```
-- __init__.py ----------------------------------------
|   1  from .agents import DataAssessmentAgent
|   2  # <- Missing: from .agents import ForecastingAgent
|   3  from .synthesis import SynthesisAgent
--------------------------------------------------
```

## Example: Diagnosing ImportError

**Scenario:** ForecastingAgent not exported from agents module

**Command:**
```bash
python scripts/test_runner.py --module all
```

**Output (excerpt shown):**
```
Test 1: State & Coordinator Import     ... [FAIL]
cannot import name 'ForecastingAgent' from 'ai_research_framework.agents'

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
  ...

  Action: Add line to imports:
  from .forecasting_agent import ForecastingAgent
```

## JSON Output Format

When using `--output-format json` or `both`, results are saved as:

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
      "error_message": "cannot import name 'ForecastingAgent'...",
      "likely_files": [
        "ai_research_framework/agents/__init__.py",
        "ai_research_framework/agents/forecasting_agent.py"
      ],
      "suspected_problem": "ForecastingAgent class not exported...",
      "fix_hypotheses": [
        {
          "title": "Check __init__.py -- ForecastingAgent missing...",
          "confidence": "HIGH",
          "description": "...",
          "file_path": "ai_research_framework/agents/__init__.py",
          "line_range": [1, 30],
          "code_excerpt": "...",
          "action": "Add line to imports: ..."
        }
      ]
    }
  }
}
```

## Design Notes

### Why Auto-Diagnosis?

The diagnosis engine solves the iterate → test → read error → fix → test cycle:

**Before:** Error message → read REMEDIATION dict → manually check files → apply fix
**After:** Error message → auto-diagnosis shows likely files + code excerpts → apply fix

### Depth Levels Explained

| Level | Behavior | When To Use |
|-------|----------|-------------|
| **paths** | List file paths, user reads manually | Quick feedback, prefer reading code yourself |
| **excerpt** (default) | Read 20-30 lines context | Standard debugging workflow |
| **full** | Read entire files, all analysis | Complex issues, unfamiliar codebase |

### No Side Effects

The diagnosis engine:
- ✅ Only reads files (no modifications)
- ✅ Parses error messages (no test mutations)
- ✅ Runs standalone from test execution
- ✅ Can be disabled entirely (`--diagnosis off`)

## Extending the Diagnosis Engine

To add support for a new error type:

1. **diagnosis.py**: Add method `_diagnose_<error_type>()`
2. **test_runner.py**: Add routing in `diagnose()` method
3. **Test it**: Create a scenario that triggers the error, verify diagnosis output

Example for a hypothetical `CustomError`:

```python
# diagnosis.py
def _diagnose_custom_error(self, msg: str, test_name: str, module: str) -> Diagnosis:
    """Diagnose: CustomError from XYZ"""
    # Parse error message
    # Identify likely files
    # Create 2-3 fix hypotheses
    # Return Diagnosis object

# test_runner.py (in diagnose method)
elif error_type == "CustomError":
    return self._diagnose_custom_error(error_message, test_name, test_module)
```

## Future Enhancements

Potential improvements:
- [ ] Auto-fix suggestions (read-only, propose patches)
- [ ] Integration with git diff (show recent changes)
- [ ] Machine learning ranking (learn which fixes work best)
- [ ] Slack/email integration (send diagnosis reports)
- [ ] Historical tracking (learn from past failures)

## Troubleshooting

### "diagnosis module not found"

The diagnosis engine must be in the same `scripts/` directory as test_runner.py:
```bash
ls .claude/skills/test-codebase-integrity/scripts/
# Should show: diagnosis.py, test_runner.py
```

### "JSON output file not created"

Ensure you're using `--output-format json` or `both`:
```bash
python scripts/test_runner.py --diagnosis excerpt --output-format both
```

### "Code excerpts not showing"

Use `--diagnosis excerpt` (default) or `--diagnosis full`:
```bash
python scripts/test_runner.py --diagnosis excerpt
```

`--diagnosis paths` only lists files without reading them.

## See Also

- [SKILL.md](SKILL.md) — Full skill documentation
- [test_runner.py](scripts/test_runner.py) — Test execution logic
- [diagnosis.py](scripts/diagnosis.py) — Diagnosis engine implementation
