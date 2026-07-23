# Play 13: AI Insurance Verification for Dental/Medical Offices

## What It Is

A service that automates the tedious process of verifying patient insurance eligibility before appointments. The AI calls or checks payer portals to confirm: coverage status, deductible remaining, annual maximum remaining, and frequency limitations for specific procedures.

## The Problem

The average dental office front desk spends **3-6 hours per day** on insurance verification:
- Calling insurance companies (8-15 min per call, hold time included)
- Checking web portals (5-10 min per patient)
- Documenting results in the PMS
- Re-verifying on day of service (because coverage can change)

**The cost:** A front desk person at $18-22/hr spends ~$400-700/mo in labor per day just on verification. For a 3-provider office, that's easily $10,000+ in annual labor cost.

**The error cost:** 25-30% of all dental claim denials originate from eligibility issues. Each denied claim costs ~$30-50 in administrative rework — plus the delay in payment.

## What the AI System Does

### Input (patient info for tomorrow's schedule):

```
Patient: Maria K.
DOB: 04/12/1984
Insurance: Delta Dental PPO Plus Premier
Member ID: XKT4729J
Group: 12904
Procedure planned: D1110 (prophy) + D0274 (BWX)
Date of service: 2026-07-21
```

### AI Output (15-second verification):

```
═══ INSURANCE VERIFICATION REPORT ═══
Patient: Maria K.
Date: 2026-07-20 | Time: 14:03
Verified by: AI Verifier v1.2

COVERAGE STATUS: ✅ ACTIVE
  Plan: Delta Dental PPO Plus Premier
  Effective: 2024-01-01
  Member since: 2 years, 7 months
  Group: 12904 — Employer: Austin ISD

DEDUCTIBLE:
  Annual deductible: $50
  Applied this year: $50 (met on 2026-02-15)
  Remaining: $0 ✅

ANNUAL MAXIMUM:
  Maximum: $1,500
  Used this year: $325
  Remaining: $1,175

FREQUENCY LIMITATIONS:
  D1110 (Prophylaxis): Last done 2025-12-10 → ✅ Eligible (13-month gap, 6-month min)
  D0274 (4 BWX): Last done 2025-06-02 → ✅ Eligible (13-month gap, 12-month min)
  D0120 (Periodic exam): Last done 2025-12-10 → ✅ Eligible (7-month gap, 6-month min)

PATIENT RESPONSIBILITY ESTIMATE:
  D1110 - Prophylaxis: $93 (plan pays $72)
  D0274 - Four BWX: $49 (plan pays $41)
  D0120 - Periodic exam: $45 (plan pays $40)
  Total est. patient portion: $187

NOTES:
  - Annual deductible already met for 2026
  - Patient is within all frequency limits
  - Maximum not at risk for this visit
  - No waiting periods apply (patient has been on plan >24 months)

ALERTS: None
```

## Why This Is Valuable

**Before:** Front desk spends 8-15 min on phone, writing numbers on a scrap of paper.

**After:** Front desk pastes patient info into your system, gets a formatted report in 15 seconds.

**The key insight:** Most payers have publicly accessible provider portals (Delta Dental's Provider Toolkit, MetLife's DentalConnect, etc.). You can build an automation layer on top of these portals using browser automation — no API access required.

## How It Works (Architecture)

```
PMS export (tomorrow's schedule) → CSV file
    ↓
Your system logs into each payer portal automatically
    ↓
Extracts eligibility, benefits, frequency limits
    ↓
Formats into the report above
    ↓
Emails report to office manager before close of business
```

The tricky part: each payer portal is different. You need a "connector" for each major payer in your area:
- Delta Dental
- MetLife
- Cigna
- Aetna
- Guardian
- Blue Cross Blue Shield (dental)
- UnitedHealthcare Dental
- Humana
- Principal
- Regional payers

Start with the top 3 in your market. Add more as you grow.

## Pricing

| Tier | Volume | Price |
|---|---|---|
| Per-patient | Per verification | $2-4 |
| Small practice (1-2 providers) | ~15-30 patients/day | $300-500/mo |
| Medium practice (3-5 providers) | ~40-80 patients/day | $600-1,000/mo |

The dental office currently spends ~$400-700/mo in front desk labor on this. You're replacing it at roughly the same cost — but with zero errors, zero hold time, and zero missed verifications.

**Upsell:** Add a re-verification check on the morning of service. Medicare and Medicaid patients often have last-minute coverage changes.

## First Sale

1. Go to a dental office at 3pm. Ask the front desk person: "How many verifications did you do today?"
2. Count the sticky notes on their monitor (there will be 10-20)
3. Ask: "How much time did that take?" (Answer: 2-3 hours)
4. Offer: "What if this was automatically done at 2pm every day and emailed to you before close of business?"
5. Offer a 2-week free trial: "Give me tomorrow's schedule every morning. I'll send you the verification reports by 3pm. If it saves you time, we'll talk about making it permanent."

## Legal Boundary

- You are logging into payer *provider portals* with the provider's credentials — not bypassing authentication, not accessing patient accounts, not scraping hidden data
- You are acting as the provider's authorized agent for eligibility verification — a standard healthcare operations activity under HIPAA
- The data you access is the same data the front desk would access manually — you're just doing it faster
- The line you don't cross: storing PHI beyond the immediate verification session, sharing verification data with third parties, or making coverage determinations — you present the facts, the provider decides
- HIPAA applies: you need a BAA with the practice if you touch PHI. But you can structure as "we provide the automation tool, the practice runs it" to shift compliance responsibility

**Risk: Low with BAA. Moderate without.**

---

**Final note:** If you want to skip the portal automation complexity, there's a lighter version: **AI-powered verification call listening**. The front desk records verification calls, AI transcribes and extracts the key numbers into the formatted report. Same result, simpler tech, no login automation.

## Quick Comparison Table: All 5 Plays

| Play | Setup Effort | Monthly Revenue (20 clients) | Legal Risk | First Dollar |
|---|---|---|---|---|
| 1. Competitive Intel Newsletter | Medium | $4,000-8,000 | Minimal | Week 2 |
| 3. Review Response Automation | Low | $3,000-6,000 | Near-zero | Day 3 |
| 8. Dispute Letters | Low | $3,000-5,000 | Low | Day 1 |
| 9. Dental Appeal Letters | Medium | $10,000-20,000 | Low | Week 3 |
| 13. Insurance Verification | High | $6,000-20,000 | Low (with BAA) | Month 2 |

**Play 3 (Review Response)** is the fastest to revenue. **Play 9 (Dental Appeals)** has the highest ceiling per client. **Play 1 (Newsletter)** is the best moat (client won't leave if they depend on the data).
