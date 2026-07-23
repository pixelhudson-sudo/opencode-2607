---
description: "Review the oldest ready_for_review ticket"
model: openrouter/deepseek/deepseek-v4-flash
---
Find a ticket with status: ready_for_review. Check out its branch. Verify each AC-N is actually met by reading the diff and running the tests — judge ONLY against that ticket's AC/NG, nothing else. Write concrete 60-second human test steps into the ticket. Post a verdict comment on the PR and apply a GitHub label: loop-approved, loop-changes-requested, or needs-human-review (`gh label create` them first if missing). If approved, set ticket status: reviewed. If changes requested, set status back to todo with a note so build retries. NEVER merge. Exit after one ticket.
