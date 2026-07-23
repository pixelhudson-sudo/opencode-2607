---
description: "Interview and file a ticket from a one-line idea"
model: openrouter/deepseek/deepseek-v4-flash
---
Take my one-line idea from $ARGUMENTS. Interview me with clarifying questions, in batches, and KEEP ASKING until the idea is unambiguous — spec quality is the bottleneck, so ask as many questions as you need. Then write one or more small tickets into ./tickets/ using the shape:

---
id: NNN
title: <short title>
status: todo
branch: ""
pr: ""
---
## Goal
## Acceptance criteria   (list as AC-1, AC-2, … — observable outcomes)
## Non-goals             (list as NG-1, NG-2, … — binding)
## Scope / files
## Test notes

Split big ideas into several day-sized tickets. Do not write code. Stop after filing tickets and show me the filenames.
