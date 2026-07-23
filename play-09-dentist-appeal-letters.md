# Play 9: AI Dental Insurance Appeal Letters

## What It Is

A service that takes a dental office's denied insurance claims and generates formatted, payer-specific appeal letters. The dental office uploads the denial EOB + patient records, AI generates a letter in 5 minutes that cites the payer's own policy language and clinical documentation.

## The Problem

- **15%** of dental claims are denied at first submission
- Average dental practice loses **$25,000-75,000/year** to denials that are never appealed
- **63% of denials are recoverable** — most are never reworked because manual appeals take 30-90 minutes each
- Top denial reasons: eligibility issues (25-30%), coding errors (15-20%), missing documentation, frequency limitations, missing tooth clauses

Your value proposition: "We appeal the denials your staff doesn't have time for. You only pay if we generate the letter. You keep 100% of what you recover."

## Real Example 1: Frequency Limitation Denial

**The Denial:**
> Procedure: D0274 (4 bitewings)
> Denial reason: Frequency limitation — patient had bitewings within last 12 months (CO-21)
> Patient: Maria K., last bitewings were 13 months ago but insurance counts from date of service, not date of processing

**AI-generated appeal letter:**

> **SMILES OF AUSTIN — DENTAL**
> 3401 Medical Pkwy, Austin, TX 78705
> (512) 555-0211
>
> July 17, 2026
>
> **Appeals Department**
> Delta Dental of Texas
> P.O. Box 200637
> Dallas, TX 75230
>
> **Re: Member Appeal — Claim #2026-07-44128**
> **Member:** Maria K. | **Member ID:** XKT4729J
> **Patient:** Maria K. | **Date of Service:** July 10, 2026
> **Procedure:** D0274 (Four Bitewing Radiographs)
> **Denial Code:** CO-21 (Frequency limitation)
> **Provider:** Smiles of Austin (NPI: 1845532917)
>
> Dear Appeals Review Board,
>
> This letter requests a review of the denial for procedure D0274 (four bitewing radiographs) performed on July 10, 2026 on behalf of Maria K. (Member ID: XKT4729J, Claim #2026-07-44128).
>
> **Reason for Denial Stated:**
> The claim was denied under code CO-21, indicating the procedure was not covered due to a frequency limitation. Specifically, the payer's system indicates that bitewing radiographs were performed within the last 12 months.
>
> **Basis for Appeal:**
> Upon review, the most recent prior bitewing radiographs (D0274) for this patient were performed on **June 2, 2025** — a gap of **13 months and 8 days** from the current service date of July 10, 2026.
>
> Per Delta Dental of Texas Policy #DDTX-RAD-001, Section 3.1, bitewing radiographs are covered once per 12-month period. At 13 months from the prior service date, this procedure falls **outside the frequency limitation** and meets the medical necessity criteria for diagnostic imaging:
>
>   • The patient presented with generalized gingival inflammation on examination
>   • Interproximal caries were suspected in teeth #3-4 and #14-15
>   • No prior radiographs demonstrated the current clinical condition
>   • New radiographs were clinically indicated to assess for interproximal decay and bone levels
>
> **Requested Action:**
> We respectfully request that this denial be overturned and the claim reprocessed for reimbursement. We have attached the following supporting documentation:
>
>   1. Copy of the original claim
>   2. Clinical chart notes from July 10, 2026
>   3. Radiographic images from July 10, 2026
>   4. Prior radiograph dates and documentation
>   5. Copy of payer's frequency policy reference
>
> Please contact us at (512) 555-0211 if additional information is needed.
>
> Sincerely,
>
> Dr. Sarah Chen, DDS
> Smiles of Austin

**Why this works:** It acknowledges the denial reason, shows the actual date gap (13 months vs the 12-month rule), cites the policy section by name, provides clinical justification, and attaches the right documentation. Most offices would just write this off — or try to appeal with one sentence that gets nowhere.

---

## Real Example 2: Missing Tooth Clause Denial

**The Denial:**
> Procedure: D6240 (Pontic — porcelain fused to high noble metal for tooth #19)
> Denial reason: Missing tooth clause — tooth was missing prior to coverage effective date (PR-1 + MA-96)
> Patient: James T., lost tooth #19 due to accident 2 years ago, but has had current policy for only 8 months

**AI-generated appeal letter (excerpt):**

> **Re: Appeal of Missing Tooth Clause Denial — Claim #2026-07-81934**
>
> ...
>
> **Basis for Appeal:**
> The denial cites the Missing Tooth Clause indicating that tooth #19 was extracted prior to the member's coverage effective date under this plan (December 1, 2025).
>
> However, the patient's prior dental coverage under Cigna (Policy #CIG-2291, active through November 30, 2025) covered this procedure under its Major Restorative benefit with a 12-month waiting period, which was satisfied on June 15, 2026.
>
> Under the Texas Department of Insurance guidelines for replacement coverage (28 TAC §3.3703), a Missing Tooth Clause does not apply when the member had prior continuous creditable coverage that would have covered the same procedure. We have attached the prior coverage verification letter from Cigna (dated June 16, 2026) confirming that the 12-month waiting period was met.
>
> **Requested Action:**
> Please overturn the denial and reprocess under continuity of coverage provisions.
>
> ...

**Why this works:** It cites the specific regulation (28 TAC §3.3703) that overrides the Missing Tooth Clause when prior creditable coverage exists. Most dental offices don't know this exception exists — they just write off the $800-1,200 bridge.

---

## The Opportunity

The appeal letter market for medical is crowded (MedAppeals, EZAppeal, AuthAppeals at $249-479/mo). The dental-specific market is **wide open** — most existing tools are medical-first with dental as an afterthought.

Dental-specific knowledge matters here: CDT codes (not CPT), frequency rules for D0274/D0120/D1110, missing tooth clauses, alternate benefit provisions, and the difference between CO, PR, and OA denial codes.

## How It Works (Delivery Model)

1. Dental office sends you the denial EOB (photo of the paper or ERA export)
2. You upload to the AI system (Claude + your prompt template)
3. AI generates a letter citing payer policy + clinical docs in ~3 minutes
4. You review and revise (10 minutes)
5. You send the formatted letter back as a Word doc or PDF
6. Dental office prints, signs, mails or faxes
7. You track the outcome

**Optional upsell:** Handle the entire submission process — fax/mail the letter, track the response, follow up at 30 days.

## Pricing

| Model | Price | Example Revenue |
|---|---|---|
| Per appeal letter | $50-75 | 10/month = $500-750 |
| Monthly retainer (unlimited) | $500-1,000/mo | 5 offices = $2,500-5,000/mo |
| Percentage of recovered amount | 10% of collected | On $10k recovered = $1k |

Reseller model: You train the dental office's existing billing staff to input denials into your system. They send you the output letters. You never touch their workflow — you're just the AI layer.

## First Sale

1. Walk into a local dental office. Ask: "How much in denied claims did you write off last month?"
2. If they say $2,000-5,000 (average for a 2-3 provider practice), ask: "What if I could appeal half of those for $50 each?"
3. Offer to do 3 appeal letters for free
4. Track results. If 2 of 3 overturn, the ROI math sells itself.

## Legal Boundary

- You are generating a letter based on facts provided by the provider
- The provider reviews and signs the letter — they own the submission
- The letter cites the payer's own published policy — you're not creating new policy positions
- The line you don't cross: claiming clinical facts that aren't in the patient's chart, recommending specific treatment plans, or representing the patient in the appeal
- This is document automation + factual synthesis, not medical practice or legal advice

**Risk: Low with verification step.**

Want me to build a single-script MVP that takes a denial EOB photo and spits out a formatted letter? I can make that in about 30 minutes.
