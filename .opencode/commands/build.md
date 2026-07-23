---
description: "Build the oldest agent-ready ticket"
model: openrouter/deepseek/deepseek-v4-flash
---
Find the oldest ticket with status: agent-ready. If none, print "no agent-ready tickets" and exit 0. Otherwise: set its status to building; create git branch ticket/NNN-slug; implement ONLY the acceptance criteria, respecting every non-goal; run the project's build/tests; commit. Fill the ticket's branch: field, open a GitHub PR with `gh pr create` (body must link the ticket and list AC-N), put the PR URL in the pr: field, set status: ready_for_review. If build/tests fail 3 times, set status: blocked with a note explaining why, and exit. One ticket per run. Wrap model calls so a rate-limit/timeout retries with backoff — never drop a ticket.
