---
name: run
description: Orchestrate the full intake → classify → execute → report cycle in sequence, optionally on a recurring /loop schedule
---

Chains the full cycle in order. Equivalent to setting up both the Finn Loop's build loop and review loop together.

## Behavior
1. Run `intake` once (skip if `inbox/` already has unclassified items and user says "skip intake").
2. Run `classify` once on everything currently in `inbox/`.
3. Run `execute` repeatedly (default: until `tasks/queued/` is empty, or up to a max_tasks limit passed by the user).
4. Run `report` once at the end of the batch.
5. Print the final report content to the user directly — do not make them open the file manually.

## Recurring mode
To mimic the Finn Loop's `/loop 5min /him build`, the user can run:
`/loop 30min /run` — this repeats the full intake→classify→execute→report cycle every 30 minutes throughout the day.
Recommended cadence for a personal loop: less frequent than code (30-60 min), since human input during intake matters more.

## Guardrails (apply to all skills)
- Never delete files — archive/move instead, and mark with a status field.
- Never bulk-modify more than 5 files without explicit user confirmation first.
- If confidence in an outcome is below ~70%, downgrade to `needs_review` rather than guessing.
- Always cite which context files were used to resolve a task.
