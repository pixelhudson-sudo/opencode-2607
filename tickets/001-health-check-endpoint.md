---
id: 001
title: Add a health-check endpoint
status: ready_for_review
branch: ticket/001-health-check-endpoint
pr: "https://github.com/pixelhudson-sudo/opencode-2607/pull/1"
---
## Goal
Expose a HTTP GET /health endpoint so infrastructure can ping the service.

## Acceptance criteria
- AC-1: GET /health returns 200 with JSON body `{"status":"ok"}`
- AC-2: Response headers include `Content-Type: application/json`
- AC-3: The endpoint responds within 100ms
- AC-4: No authentication or API key required

## Non-goals
- NG-1: No health-check logic beyond basic aliveness (no DB checks, no dependency pings)
- NG-2: No changes to existing auth middleware
- NG-3: No new npm dependencies

## Scope / files
- `src/health.ts` — new file, handler + route registration

## Test notes
```bash
curl -s http://localhost:3000/health
# → {"status":"ok"}

## Build log
- Created `src/health.ts` — standalone Node.js HTTP server using built-in `http` module (zero new deps)
- Verified: HTTP 200, `Content-Type: application/json`, response time 3.9ms
- PR: https://github.com/pixelhudson-sudo/opencode-2607/pull/1
```
