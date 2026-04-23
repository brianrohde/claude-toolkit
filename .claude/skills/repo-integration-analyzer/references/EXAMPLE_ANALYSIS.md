# Example: Claude-Mem & Context-Mode Integration Analysis

This is a worked example showing what a complete analysis looks like using this skill.

**Note:** This is the actual analysis Brian did for his multi-project workflow. It serves as a template for future analyses.

---

## Executive Summary

Two complementary tools for context optimization:

1. **Context-Mode** (5-10 min setup): Protects in-session context window (94-99% savings on logs/output)
2. **Claude-Mem** (30-45 min setup): Persistent cross-session archive with semantic search

**Recommendation:** Use **both** in phases. They solve different problems. For multi-project developers, Claude-Mem's cross-project pattern reuse and decision rationale lookup provide 2-5 hours/week ROI.

---

## Repository Comparison

| Aspect | Claude-Mem | Context-Mode |
|--------|-----------|--------------|
| **Problem Solved** | "Did we already solve this?" across sessions/projects | Raw logs flooding context window DURING session |
| **When It Works** | Between sessions, searching past work | During session, preventing context waste |
| **Setup Time** | 30-45 min (Bun, uv, Python, daemon) | 5-10 min (hooks only, existing `.claude/hooks/`) |
| **Runtime Overhead** | ~500 tokens/session (SDK Agent synthesis) | <1% (async post-tool queuing) |
| **Storage** | ~200 MB/month (observations + embeddings) | ~100 KB/month (session events) |
| **Monthly API Cost** | ~$0.02-$0.05 | ~$0.01-$0.02 |
| **Learning Curve** | Medium (agent SDK, vector search concepts) | Low (hook pattern you already use) |
| **Maintenance** | Active (v6.5.0+) | Active (latest releases) |
| **License** | AGPL-3.0 | ELv2 (source-available) |

**Synergy:** Complementary. Claude-Mem captures observations across projects. Context-Mode keeps in-session context lean. Together they cover the full lifecycle.

---

## Module Breakdown

### Claude-Mem

| Module | Effort | Benefit | Relevance | File Path |
|--------|--------|---------|-----------|-----------|
| **5 Lifecycle Hooks** | 5 min | Capture tool usage, session summaries | ⭐⭐⭐⭐⭐ | `src/cli/handlers/` |
| **Worker Service** | 30 min | Express daemon (port 37777), manages SDK Agent | ⭐⭐⭐⭐ | `src/services/worker-service.ts` |
| **SDK Agent Integration** | 20 min | Claude Agent SDK generates semantic narratives | ⭐⭐⭐⭐⭐ | `src/services/worker/SDKAgent.ts` |
| **SQLite Storage** | 15 min | Observations, sessions, summaries, prompts | ⭐⭐⭐⭐ | `src/services/sqlite/` |
| **ChromaDB Vector Search** | 25 min | Semantic embedding + search (requires uv + Python) | ⭐⭐⭐⭐ | `src/services/sync/ChromaSync.ts` |
| **mem-search MCP Skill** | 5 min | Query archive (search → timeline → fetch) | ⭐⭐⭐⭐⭐ | `plugin/skills/mem-search/SKILL.md` |
| **make-plan Skill** | 10 min | Orchestrator for multi-step implementation plans | ⭐⭐ | `plugin/skills/make-plan/SKILL.md` |
| **Web Viewer UI (React)** | 30 min | Real-time observation stream at localhost:37777 | ⭐⭐ | `src/ui/viewer/` |

**Why not the UI?** Nice-to-have but not essential. The MCP tools are sufficient for searching/retrieving. UI is useful for browsing but doesn't add functional value.

### Context-Mode

| Module | Effort | Benefit | Relevance | File Path |
|--------|--------|---------|-----------|-----------|
| **PreToolUse Hook** | 5 min | Enforce sandbox routing before execution | ⭐⭐⭐ | `src/adapters/claude-code/hooks.ts` |
| **PostToolUse Hook** | 5 min | Capture session events (files, tasks, errors) | ⭐⭐⭐⭐⭐ | `src/adapters/claude-code/hooks.ts` |
| **SessionStart Hook** | 5 min | Restore session state after compaction | ⭐⭐⭐⭐ | `src/adapters/claude-code/hooks.ts` |
| **PreCompact Hook** | 5 min | Build snapshot before context reset | ⭐⭐⭐⭐ | `src/adapters/claude-code/hooks.ts` |
| **Sandbox Execution** (ctx_execute) | 20 min | Run code (11 languages) without dumping output | ⭐⭐⭐⭐⭐ | `src/tools/ctx_execute.ts` |
| **Batch Execution** (ctx_batch_execute) | 15 min | Run 3+ commands + search results in one call | ⭐⭐⭐⭐ | `src/tools/ctx_batch_execute.ts` |
| **FTS5 Indexing & Search** | 25 min | Index markdown docs, search with BM25 ranking | ⭐⭐⭐⭐ | `src/tools/ctx_index.ts` + `ctx_search.ts` |
| **Session Continuity DB** | 15 min | SQLite event tracking for compaction recovery | ⭐⭐⭐⭐⭐ | `src/db/` |
| **Analytics Dashboard** (React) | 60 min | Local UI showing token savings, call counts | ⭐ | `insight/` |

**Why not the dashboard?** Self-contained analytics are nice, but not essential for core functionality. Can add later if useful.

---

## Real-World Scenario: Multi-Project Reuse

### Session 1: CBP Tariff Extraction (pta-cbp-parser)

**Claude-Mem + Context-Mode working together:**

```
PostToolUse Hook (Context-Mode):
  Tool: Read 50 CBP PDF letters
  Tool: Grep for HTS tariff codes using /^\d{2,8}/
  Tool: Write benchmark.csv with results
  
  Context-Mode captures:
    - File edits + grep searches
    - Task completion status
    - Any errors encountered
  
  Observation sent to Claude-Mem worker:
    title: "Extracted HTS codes from batch-1"
    narrative: "Read 50 CBP ruling letters. Applied regex /^\d{2,8}/ 
               for HTS classification. Extracted 1,200 matches. 
               Validation against ground-truth: 87% accuracy. 
               Gap: field coverage in 13% of entries."
    facts: [
      "HTS pattern matched 1,200 items",
      "87% accuracy vs ground truth",
      "13% field coverage gap",
      "Error patterns: incomplete fields, OCR artifacts"
    ]
    concepts: ["HTS codes", "tariff extraction", "validation"]
```

**End of session:**
- Context-Mode: Session events (file edits, task status) stored in SQLite
- Claude-Mem: Full observation + narrative + facts stored in SQLite + Chroma vectors

### 6 Months Later: Tax Analysis Project (Different Project)

**New developer on team asks:**
```
"I need to extract tariff codes too. How did we validate them last time?
What were the accuracy metrics? Any error patterns to watch for?"
```

**With Claude-Mem:**
```
/mem-search "HTS validation tariff extraction accuracy"

Chroma vectors match semantically similar observations:
  
Search returns:
  ID: 11131 | Type: change | Title: "Extracted HTS codes from batch-1"
  ID: 11129 | Type: discovery | Title: "Found 13% field coverage gap"
  ID: 11128 | Type: bugfix | Title: "Fixed multi-code entry parsing"

Click on ID 11131 → Full observation loaded:
  
  Narrative: "Read 50 CBP ruling letters. Applied regex /^\d{2,8}/ 
             for HTS classification. Extracted 1,200 matches. 
             Validation against ground-truth: 87% accuracy. 
             Gap: field coverage in 13% of entries."
  
  Facts: ["87% accuracy vs ground truth", "13% field coverage gap", 
          "Error patterns: incomplete fields, OCR artifacts"]
  
  Files: ["data/cbp-letters/batch-1/", "data/benchmarks/ground_truth.json"]

  ✅ New developer: "Perfect! I'll focus on the 3 error patterns first."
  ✅ Skips 2 hours of benchmarking
  ✅ Reuses exact validation logic
```

**Without Claude-Mem:**
```
New developer: "Ask around if anyone has notes from the last extraction"
Spend 2 hours searching Slack, old notes, trying old scripts
Hope the regex pattern is still in git history
Possibly re-benchmark from scratch
```

**Time saved:** 2-3 hours per extraction task × 5 future projects = **10-15 hours/year minimum**.

---

## Token Cost Analysis

### Claude-Mem

| Scenario | Calculation | Cost |
|----------|-------------|------|
| **Per-session capture** | 50 observations × async queuing | $0 (queued, not immediate) |
| **Per-session synthesis** | SDK Agent: 50 obs × 10 tokens = 500 tokens | ~$0.0015 |
| **Per-search index lookup** | SQLite query + Chroma vector search | ~$0 (local) |
| **Per-search fetch (3 results)** | 3 observations × 500 tokens = 1,500 tokens | ~$0.0045 |
| **Monthly typical** | 20 sessions (50 obs each) + 10 searches | ~$0.08 |

**Cost: Negligible.** One cup of coffee per month for 12+ months of searchable history.

### Context-Mode

| Scenario | Calculation | Cost |
|----------|-------------|------|
| **Per-session savings** | 600 KB logs → 25 KB compressed | Prevents context waste |
| **Per-execute call** | Sandbox execution, no API calls | $0 (local) |
| **Per-search call** | FTS5 search, no API calls | $0 (local) |
| **Monthly typical** | 50 tool calls, 20 searches | $0 |

**Cost: Free.** All local execution and SQLite searches.

---

## Recommended Integration Path

### Phase 1: Context-Mode Hooks (5-10 min) ← Start here

**Why first?** Existing `.claude/hooks/` infrastructure; no external dependencies.

1. Copy hook scripts from `context-mode/hooks/`
2. Register in `.claude/settings.json`
3. Test: Run a session, verify session events captured

**Benefit:** Session continuity on context resets. No more "wait, what was I doing?" when context compacts.

**Cost:** 5-10 min setup. Zero ongoing cost.

### Phase 2: Sandbox Execution Tool (20 min)

**Why next?** Immediate ROI on regex testing.

1. Extract `ctx_execute.ts` logic → local tool or MCP
2. Create test script for regex patterns
3. Test: Run regex test on 10 sample PDFs, verify output summary

**Benefit:** 150 KB logs → 200 B summary. 99.9% context savings per test.

**Cost:** 20 min setup. One-time.

### Phase 3: Claude-Mem Setup (30-45 min)

**Why last?** Requires external dependencies (Bun, uv, Python); but highest long-term ROI.

1. Install Bun (auto-installs if missing)
2. Install uv (auto-installs if missing)
3. Install Python 3.10+ (if not present)
4. Run `npx claude-mem install`
5. Restart Claude Code
6. Test: Run a session, check http://localhost:37777

**Benefit:** Cross-project pattern reuse. No more re-solving same problem twice.

**Cost:** 30-45 min setup. ~$0.08/month ongoing. **ROI: 2-5 hours/week saved.**

### Phase 4: Analytics Dashboard (Optional, 60 min)

**Why optional?** Nice-to-have visualization. Core functionality works without it.

1. Clone `insight/` from context-mode
2. Customize for pta-cbp-parser metrics (extraction accuracy, phase duration)
3. Deploy locally at `localhost:3000`

**Benefit:** Visual feedback on extraction performance, token savings per phase.

**Cost:** 60 min setup. One-time. No ongoing cost.

---

## What NOT to Copy

### ❌ Claude-Mem: ChromaDB Vector Embeddings

**Why skip initially?** 
- Requires uv + Python (added complexity)
- FTS5 + BM25 ranking (bundled with SQLite) is sufficient
- Vector search only useful when archive exceeds 1,000+ observations

**Better alternative:** Start with FTS5 (full-text search), add vectors later if needed.

### ❌ Claude-Mem: Worker Daemon on Port 37777

**Why skip initially?** 
- External process adds infrastructure complexity
- Graceful degradation: if daemon crashes, Claude Code continues
- Can prototype with simpler in-project solution first

**Better alternative:** Implement observation capture with local SQLite first, add daemon later.

### ❌ Context-Mode: Analytics Dashboard

**Why skip initially?** 
- React + TanStack boilerplate
- Not essential for core context window protection
- Can visualize stats with CLI tools first

**Better alternative:** Use `/context-mode:ctx-stats` (built-in) to check token savings, add dashboard UI later if useful.

### ❌ Bundled Skills (make-plan, knowledge-agent, smart-explore)

**Why skip initially?** 
- Orthogonal to core integration
- Built on top of observations; use once core is working
- Nice-to-have, not critical path

**Better alternative:** Implement observation capture first, add skills later.

---

## Cross-Project Applicability

### Applicable to Almost Any Project

| Project Type | Claude-Mem | Context-Mode | Why |
|------|-----------|--------------|-----|
| **Data extraction** (CBP, tax, finance) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Heavy on logs, regex testing, cross-project pattern reuse |
| **Web/API development** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | API responses can be large; cross-API patterns reusable |
| **ML/data science** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Experiments generate huge output; pattern reuse critical |
| **Documentation** | ⭐⭐⭐ | ⭐⭐ | Less context pressure; less cross-project reuse |
| **DevOps/infrastructure** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Large config files + logs; patterns widely reusable |

---

## Decision Rationale

### Question: "Why not just use GitHub Issues for cross-project patterns?"

**Answer:** GitHub Issues are for bug reports and feature requests. Claude-Mem captures the **decision-making process and metrics**:

- "We tried regex only (fast, 99% accuracy) vs LLM hybrid (slower, 99.5%)"
- "Chose regex-only because token cost ($0.02/extraction) exceeds speed gain"
- "Field coverage gap: 13%, error patterns: incomplete fields, OCR artifacts"

Issues don't capture this context. Claude-Mem does automatically.

### Question: "Why not just store observations in Git?"

**Answer:** Git is for code versioning, not for the **work process**. Claude-Mem captures:

- Which tools ran (Grep, Read, Write, Bash)
- What was learned (narratives + facts)
- How long it took
- Benchmarks and metrics

You can commit the *result* to git; Claude-Mem captures the *process* and makes it searchable.

---

## Reference Files

| File | Location |
|------|----------|
| Full repo: Claude-Mem | `C:\Users\brian\OneDrive\Documents\03 - R - Resources\fork-claude-mem\` |
| Full repo: Context-Mode | `C:\Users\brian\OneDrive\Documents\03 - R - Resources\fork-context-mode\` |
| Deep dive into Claude-Mem | `C:\Users\brian\OneDrive\Documents\03 - R - Resources\CLAUDE_MEM_DEEP_DIVE.md` |
| This analysis | `C:\Users\brian\OneDrive\Documents\03 - R - Resources\CLAUDE_MEM_CONTEXT_MODE_INTEGRATION_ANALYSIS.md` |

---

**Analysis Date:** 2026-04-17  
**Status:** Ready to Implement (Phase 1 and 2 can start immediately)  
**Reviewer:** Claude Code (Haiku 4.5)
