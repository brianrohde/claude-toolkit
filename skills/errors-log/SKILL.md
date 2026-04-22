---
name: errors-log
description: This skill should be used when the user asks to "log errors", "log tooling issues", or "/errors-log". Scans session conversation history for tool failures, Windows/OneDrive issues, CRLF problems, and encoding errors, then logs them to .claude/logs/tooling-issues.jsonl (source of truth), triggering automatic markdown rebuild.
version: 0.2.0
---

# Log Errors Skill

## Purpose

Extract and document errors that occur during a session by appending to `.claude/logs/tooling-issues.jsonl` (the authoritative source), which automatically triggers a rebuild of `docs/tooling-issues.md`. This prevents knowledge loss, avoids markdown corruption, and ensures all errors can be deduplicated by `symptom_short` field.

## When to Use

- **Manual invocation**: Call `/errors-log` after a session where tooling issues occurred
- **Pre-commit hook**: Automatically triggered before `/git-draft-commit` to ensure all session errors are logged before creating a commit

## How It Works

### Step 1: Scan Conversation for Errors

The skill scans the current conversation history for error signals:

- **Tool failures**: "failed", "error", "ERROR", "blocked", "EEXIST", "unexpected EOF"
- **Windows/OneDrive issues**: "OneDrive", "CRLF", "backspace", "\x08", "encoding"
- **File operation failures**: "Write tool", "Edit tool", "mkdir", "permission denied"
- **Pattern/regex problems**: "\b", "word boundary", "regex", "not matching"
- **Python execution errors**: "python -c", "escape sequence", "corrupted"

### Step 2: Extract Error Context

For each error signal found, capture:
1. **Symptom**: What went wrong (from error message or description)
2. **Cause**: Why it happened (root cause from logs or analysis)
3. **Solution**: What fixed it (the workaround or proper pattern used)
4. **Key lesson**: One-line rule to prevent recurrence (optional but recommended)

### Step 3: Format and Append to JSONL

Append new error to `.claude/logs/tooling-issues.jsonl` as a JSON line entry:

```json
{
  "timestamp": "ISO 8601 UTC timestamp",
  "issue_num": "next available number",
  "category": "Category/Subcategory",
  "symptom_short": "abbreviated key, 3-5 words, dashes",
  "symptom": "What went wrong",
  "cause": "Why it happened",
  "solution": "How to fix or avoid"
}
```

### Step 4: Automatic Markdown Rebuild

After appending to JSONL, the skill automatically triggers a rebuild of `docs/tooling-issues.md` from JSONL. No manual markdown editing required.

### Step 5: Avoid Duplicates

Before logging, check if the error already exists by comparing `symptom_short` against all entries in `.claude/logs/tooling-issues.jsonl`. If exact match exists, skip (already logged). If similar issue exists with better wording, update the existing JSONL entry with a new timestamp rather than creating a duplicate.

## Usage Examples

**Manual invocation:**
```
/errors-log
```
Scans conversation, extracts errors, prompts you to confirm/edit, then appends to `docs/tooling-issues.md`.

**Before drafting a commit:**
```
/errors-log
/git-draft-commit
```
Or if auto-trigger is enabled, `/git-draft-commit` will automatically run `/errors-log` first.

## Output

The skill returns a summary of errors logged:

```
Logged 2 new issues to tooling-issues.jsonl:
  - Issue 33: OneDrive mkdir conflicts when editing Python files
  - Issue 34: CRLF normalization breaks multi-line string replacements

Rebuilt markdown from JSONL (20 total issues).
To review: docs/tooling-issues.md
```

If no errors found, returns:
```
No new errors detected in conversation history.
```

## Integration with Git Workflow

When auto-trigger is enabled in `.claude/settings.json`, the `/git-draft-commit` skill will automatically invoke `/errors-log` before generating the commit message. This ensures:

1. All session errors are appended to JSONL
2. Markdown is rebuilt (no manual edits)
3. Deduplication prevents duplicates
4. Future sessions can reference `docs/tooling-issues.md` to avoid known issues

See `.claude/rules/trigger-git-commit-workflow.md` for git workflow details.

## Source of Truth

**JSONL is authoritative.** Always append to `.claude/logs/tooling-issues.jsonl`, never edit `docs/tooling-issues.md` directly. The markdown is auto-generated and will be overwritten.
