---
name: One-off execution default
description: Trigger phrases like "update docs" or "git commit message" are one-off (non-recurring) unless explicitly specified
type: feedback
---

# One-Off Execution Default

**Rule:** When Brian triggers a workflow command without specifying an interval (e.g., `"update all docs"`, `"git commit message"`, `"finalize standup"`), execute it **once immediately** — do not schedule it as a recurring task via `/loop`.

**Why:** Recurring tasks require explicit intent. The default assumption should be "do this now, once" to avoid unwanted background automation.

**How to apply:**
- If Brian says `"update all docs"` → execute the docs workflow immediately, one time only
- If Brian says `"update all docs every 10m"` → then use `/loop` to schedule it recurring
- If Brian says `"git commit message"` → generate and display the message, one time
- Do not invoke `/loop` skill unless Brian explicitly specifies an interval or uses the word "every"

**Exception:** Auto-triggers at session end (like auto-standup logging) are separate and should continue to follow existing standup-workflow.md rules.
