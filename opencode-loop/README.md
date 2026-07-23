# OpenCode Personal Loop (Chelsea's "Finn Loop" adaptation)

Adapted from Alex Finn's "Finn Loop" (spec → build → review) for a personal capture-and-resolve workflow
run in OpenCode with DeepSeek v4 (free) as the model.

## Cycle
1. **Intake** (`prompts/intake.md`) — asks "What's on your mind?", captures raw thoughts into `inbox/`.
2. **Classify** (`prompts/classify.md`) — files each thought into a context folder, creates a task or memory item.
3. **Execute** (`prompts/execute.md`) — works the top queued task, logs evidence, marks completed/blocked/needs_review.
4. **Report** (`prompts/report.md`) — summarizes work, blockers, 5 suggestions, and one recommended next step.
5. **Run** (`prompts/run.md`) — orchestrates 1-4 in sequence, optionally on a recurring `/loop` schedule.

## Folder structure
```
opencode-loop/
├── inbox/                 raw captured thoughts, pre-classification
├── contexts/
│   ├── business/index.md
│   ├── personal/index.md
│   ├── travel/index.md
│   ├── learning/index.md
│   ├── admin/index.md
│   ├── ideas/index.md
│   └── blocked/index.md   ambiguous items awaiting clarification
├── tasks/
│   ├── queued/            actionable tasks not yet started
│   ├── active/            currently being worked, or needs_review
│   └── done/               completed tasks with work logs
├── reports/
│   └── daily/             one report file per run, e.g. 2026-07-23.md
├── memory/                 reference material, no task tracking needed
└── prompts/                the 5 skill prompt files above
```

## Quick start in OpenCode
1. Copy this whole `opencode-loop/` folder into your project or home directory.
2. In OpenCode, register each file in `prompts/` as a custom skill (`/intake`, `/classify`, `/execute`, `/report`, `/run`).
3. Point OpenCode at DeepSeek v4 free as the model for all five skills.
4. Run `/run` once manually to test the full cycle end-to-end.
5. Once reliable, set a recurring loop: `/loop 30min /run`.

## Guardrails (baked into every skill)
- Never delete files — archive/move with a status field instead.
- Never bulk-modify more than 5 files without explicit confirmation.
- Low-confidence outcomes get downgraded to `needs_review`, never guessed as done.
- Every completed task must have a work log with result + evidence + next consequence.

## MVP scope
No Slack/Discord/Linear integration yet — everything runs on local markdown files so the system stays simple and
debuggable. Add notifications only after the core loop is proven reliable for a few days.
