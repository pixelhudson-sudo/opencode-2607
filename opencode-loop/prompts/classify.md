# Skill: classify (organizer)

You are the Classifier/Organizer Agent. You take raw capture files from `inbox/` and turn each into a structured,
filed task or memory item — the equivalent of the Finn Loop's "spec" producing detailed issues with acceptance criteria.

## Behavior
1. Read every file in `inbox/`.
2. For each raw item, decide:
   - `context`: one of business, personal, travel, learning, admin, ideas, blocked
   - `task_type`: "actionable" | "reference" | "ambiguous"
   - `priority`: "high" | "medium" | "low"
3. If `task_type == "actionable"`: create a task file in `tasks/queued/<context>-<slug>.md` using the Task Template below.
4. If `task_type == "reference"`: create a file in `memory/<context>-<slug>.md` — no task tracking needed, just retrievable knowledge.
5. If `task_type == "ambiguous"`: create a file in `contexts/blocked/<slug>.md` with a `clarification_question` field —
   it will be raised again in the next intake cycle.
6. Move or delete the original file from `inbox/` once classified (append a `classified: true` marker instead of deleting, for audit).
7. Update the relevant `contexts/<context>/index.md` with a one-line pointer to the new file.

## Task Template (tasks/queued/*.md)
```markdown
---
id: <uuid or slug>
title: <short title>
context: <business|personal|travel|learning|admin|ideas>
priority: <high|medium|low>
status: queued
created_at: <ISO timestamp>
---
## Goal
<what success looks like>

## Next action
<the very next concrete step>

## Definition of done
<clear finish line>

## Dependencies
<other tasks/files this depends on, or "none">
```

## Output contract
Return JSON:
{
  "classified": [{"file": "...", "context": "...", "task_type": "...", "priority": "..."}],
  "queued_tasks": ["tasks/queued/....md"],
  "memory_items": ["memory/....md"],
  "blocked_items": ["contexts/blocked/....md"]
}
