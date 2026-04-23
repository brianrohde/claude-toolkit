---
name: parallel-orchestration
description: Run multiple agents in parallel and synthesize results. Use this skill when you need to execute 2+ agents simultaneously (e.g., code review + refactor + test, or skill creation across multiple domains). Saves ~50% execution time vs sequential. Triggers on "run X and Y in parallel", "orchestrate [agents]", "parallel setup", or similar multi-agent phrases.
---

# Parallel Agent Orchestration

Execute multiple agents simultaneously and synthesize their results. This skill orchestrates the `.agents/skills/` marketplace skills across your project.

## When to Use

- **Multi-agent setup**: Running 2-5 agents on related tasks
- **Time-sensitive workflows**: Parallel execution saves ~50% vs sequential
- **Independent analyses**: Code review + performance audit, security + refactor, multiple skill creation tasks
- **Project initialization**: Spinning up multiple analysis/creation agents at once

**NOT for**: Single-agent tasks (just invoke the skill directly) or agents with strict interdependencies (where one depends on another's output).

---

## Workflow

### Static Orchestration (Predefined Chains)

Define specific multi-agent combinations ahead of time. Best for workflows you repeat often.

**Example chain: Code Review + Refactor Setup**
```
User: run code-review and refactor-analyzer in parallel
↓
Session spawns 2 agents simultaneously
↓
Agent A: repo-integration-analyzer (analyzes codebase)
Agent B: skill-creator (prepares refactor skill)
↓
[both run independently, ~5 min total]
↓
Session synthesizes results → combined report
```

**Example chain: Multi-Domain Skill Creation**
```
User: create security-audit and perf-analyzer skills in parallel
↓
Session spawns 2 skill-creator agents
↓
Agent A: skill-creator (security domain)
Agent B: skill-creator (performance domain)
↓
[both iterate independently, evals run in parallel]
↓
Session collects both finished skills + test results
```

### Dynamic Orchestration (Any Agents)

For one-off combinations, pass agent names and optional configuration.

---

## Implementation Guide

### Option 1: Static Command (Quick Start)

**File**: `.claude/commands/parallel-skill-setup.md`

```markdown
---
description: Run repo analysis + 2 skill creation in parallel
allowed-tools: Agent
---

Execute in parallel:

1. **repo-integration-analyzer**: Analyze codebase structure
2. **skill-creator (security)**: Create security-audit skill
3. **skill-creator (perf)**: Create performance-analyzer skill

Wait for all three to complete, then synthesize results:
- Key findings from repo analysis
- Completion status of both skills
- Test results from each skill
- Recommendations for next steps
```

### Option 2: Reusable Skill (Recommended)

**File**: `.claude/skills/parallel-orchestration/SKILL.md` (this file)

This skill provides two modes:

#### Static Chains
Use these predefined multi-agent combinations:

**Available chains**:
- `code-review`: repo-analyzer + skill-creator (security audit)
- `skill-setup`: repo-analyzer + 2x skill-creator (security + perf)
- `full-audit`: repo-analyzer + skill-creator (security) + skill-creator (perf) + command-developer
- `custom`: Specify your own agents

#### Dynamic Execution
Parameterized orchestration for one-off chains:

```
/parallel-orchestration agents:skill-creator,skill-creator,command-developer \
  params:"{\"1\": \"security-review\", \"2\": \"performance-audit\", \"3\": \"hooks-framework\"}"
```

---

## Time Impact Analysis

### Sequential Execution
```
Agent A (repo-analyzer):     5 minutes
Agent B (skill-creator):     3 minutes
Agent C (skill-creator):     3 minutes
                             ─────────
Total:                       11 minutes
```

### Parallel Execution
```
Agent A: repo-analyzer       5 min  ─┐
Agent B: skill-creator       3 min  ─┼─ All run simultaneously
Agent C: skill-creator       3 min  ─┘
                             ─────────
Total:                       5 minutes (longest agent)

**Time saved**: ~55% reduction (11 min → 5 min)
```

---

## Synthesis Pattern

After all agents complete, synthesize results:

1. **Collect outputs** from each agent
2. **Identify dependencies** — what relies on what?
3. **Merge insights** — cross-reference findings
4. **Highlight conflicts** — if two agents disagree
5. **Prioritize actions** — what's most critical?
6. **Report status** — what's done, what's next

**Report template**:
```markdown
# Parallel Orchestration Results

## Summary
- Agents run: [list]
- Total time: [duration]
- Status: ✅ (all completed) or ⚠️ (partial)

## Agent A: [name]
- Output: [key findings]
- Time: [duration]

## Agent B: [name]
- Output: [key findings]
- Time: [duration]

## Cross-Agent Insights
- Dependencies resolved: [list]
- Conflicts: [if any]
- Synergies: [where outputs complement]

## Next Steps
1. [priority 1]
2. [priority 2]
```

---

## Key Patterns

### Pattern 1: Analysis → Creation

Run analysis agents first, feed results into creation agents.

```
Phase 1: Parallel Analysis
- repo-integration-analyzer
- find-skills (marketplace search)
[both run simultaneously, ~5 min]

Phase 2: Skill Creation
- skill-creator (security, informed by Phase 1)
- skill-creator (perf, informed by Phase 1)
[both run simultaneously, informed by Phase 1 results]
```

**Why**: Analysis agents gather context; creation agents use it. Two parallel phases, not three sequential.

### Pattern 2: Domain-Specific Skill Creation

Create multiple domain-specific skills in one go.

```
Spawn 3 skill-creator agents:
- Domain 1: Security audit
- Domain 2: Performance analysis
- Domain 3: Testing framework

All iterate independently. Merge results at end.
```

### Pattern 3: Workflow Validation

Run code review + security audit + perf check in parallel.

```
Agents:
- code-reviewer (structural, maintainability)
- security-auditor (vulnerabilities, auth, data)
- perf-analyzer (bottlenecks, optimization)

All run on same codebase simultaneously.
Synthesize: Cross-validate findings, prioritize fixes.
```

---

## Limitations & Gotchas

### Subagent Isolation

Each agent is **completely isolated**. They cannot:
- Access each other's working context
- Build on each other's files
- See each other's progress

**Workaround**: Synthesize at the end. If Agent B truly needs Agent A's output, run A→B sequentially instead.

### Agent Independence

Agents can't parallelize each other. If you spawn Agent X from within an agent, it runs sequentially with the parent.

**Workaround**: Spawn all agents from your main session, not from within agents.

### Tool Constraints

Each agent runs with its own tool access. If Agent A needs a tool Agent B doesn't have, failures are isolated (A fails, B still runs).

**Workaround**: Ensure all agents have required tools; test independently first.

---

## Testing & Validation

Before running a parallel chain in production:

1. **Test each agent independently**
   ```
   Run: /skill-name [args]
   Verify: Output, logs, side effects
   ```

2. **Estimate duration**
   ```
   Agent A: ~5 min
   Agent B: ~3 min
   Agent C: ~4 min
   Max (parallel): ~5 min
   Sequential would be: ~12 min
   Savings: ~7 min
   ```

3. **Run a small parallel test**
   ```
   Execute 2 agents on small input
   Verify: Both complete independently
   Check synthesis works
   ```

4. **Full production run**
   ```
   Run full chain with real data
   Monitor outputs, time, resource usage
   Update documentation with actual timings
   ```

---

## Next Steps

1. **Choose a static chain** from the available options above, or **define your own custom chain**
2. **Test each agent independently** to establish baseline timings
3. **Run your first parallel orchestration** and measure time savings
4. **Refine based on results** — adjust synthesis, handle edge cases
5. **Document your chain** in this skill for future reuse

---

## References

- **Architecture guide**: `resources/claude-code-architecture-guide.md` (full context)
- **Skill creator**: `.agents/skills/skill-creator/SKILL.md`
- **Repo analyzer**: `.agents/skills/repo-integration-analyzer/SKILL.md` or `.claude/skills/repo-integration-analyzer/README.md`
- **Command development**: `.agents/skills/command-development/SKILL.md`
- **Claude Code docs**: https://code.claude.com/docs/en/sub-agents
