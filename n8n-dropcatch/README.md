# Domain Drop-Catching Pipeline (n8n)

Monitors expiring domains with backlink profiles, auto-registers valuable ones, and flips on Sedo/Afternic.

## Files

| File | Purpose |
|---|---|
| `n8n-dropcatch-workflow.json` | Import into n8n |
| `n8n-dropcatch-config.json` | API keys + settings (edit before running) |
| `drop_list.txt` | One domain per line (optional — uses seed list if absent) |

## Setup

1. **Import** — In n8n, **Workflows → Import from File** → select `n8n-dropcatch-workflow.json`
2. **Configure** — Edit `n8n-dropcatch-config.json` with your API keys
3. **Drop list** — Create `drop_list.txt` in the same directory with domains to check
4. **Test** — Click **Execute Workflow** to run once
5. **Schedule** — Activate the workflow (runs daily by default)

## Required APIs

| Service | Why | Cost |
|---|---|---|
| **MOZ** (moz_access_id + moz_secret_key) | Backlink metrics (DA, PA, RD) | Free tier: 1 query/10s |
| **Registrar** (Namecheap/GoDaddy) | Auto-register domains | Registration fee (~$10/domain) |
| **Sedo** (sedo_api_key) | List domains for sale | Free to list (15% commission) |

Optional: **OpenAI / cheap AI API** for enhanced evaluation (set `enable_ai_evaluation: true`).

## Decision Rules

Domains are evaluated in this order:

- **Rule A** — REGISTER: DA ≥ 25 AND referring domains ≥ 50 AND backlinks ≥ 500
- **Rule B** — REGISTER: DA ≥ 15 AND referring domains ≥ 100 AND domain ≤ 12 chars
- **Rule C** — REGISTER: Trust Flow ≥ 20 AND Citation Flow ≥ 20 AND referring domains ≥ 30
- **Rule D** — SKIP: DA < 10 AND referring domains < 10 (low quality)
- **Rule E** — SKIP: CF − TF > 20 AND referring domains < 20 (spam signal)

## Output

A report file `dropcatch_report_YYYY-MM-DD.json` is saved after each run with full breakdown including ROI projection.

## Integration with AI Agent

To wire this into your AI system:

1. Expose the workflow via n8n **Webhook** node (add before Initialize Pipeline)
2. Your AI agent POSTs to the webhook with a `drop_list` array in the body
3. The pipeline processes and returns results through the webhook response
