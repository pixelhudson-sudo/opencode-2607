# Play 3: AI Review Response Automation

## What It Is

An AI system that monitors Google Business Profile and Yelp for new reviews, automatically drafts a thoughtful response, puts it in an approval queue for the business owner to review and hit "publish." The business owner never writes from scratch — just edits if needed, then clicks approve.

## Real Examples

### Example 1: Positive Review for a Dentist

**Review (5★):**
> *"Dr. Chen was so gentle with my cleaning. I have really sensitive gums and she took her time. The front desk was friendly and the office is beautiful."* — Maria K.

**AI-generated response:**
> Hi Maria, thank you so much for the kind words! We're especially glad Dr. Chen made your cleaning comfortable — sensitive gums deserve a gentle touch, and she genuinely cares about that. We'll pass your compliment to the front desk team too. See you at your next visit!
>
> — The Austin Smiles Team

**Why this works:** It references the specific compliment (gentle, sensitive gums), names the provider, it's warm but not robotic, and it ends with a forward-looking invite.

---

### Example 2: Negative Review for a Plumber

**Review (2★):**
> *"They came out to fix a leak under my sink. The guy was nice but the leak came back 3 days later. I had to call someone else to redo it."* — James T.

**AI-generated response:**
> James, I'm really sorry to hear that. That's not the standard we hold ourselves to, and I appreciate you giving us the chance to make it right. I'd like to send one of our senior techs out this week to inspect the repair at no charge. If you're open to it, please call me directly at (512) 555-0142 — I'll make sure it's handled personally.
>
> — Mark, Owner, ATX Plumbing

**Why this works:** It acknowledges the failure without being defensive, offers a specific remedy (free re-inspection by senior tech), gives a direct line to the owner, and takes ownership. The key is *not* to make excuses.

---

### Example 3: Mixed Review for a Restaurant

**Review (3★):**
> *"Food was good but we waited 40 minutes for our table even with a reservation. The hostess seemed overwhelmed. Once we sat down the service was great."* — David L.

**AI-generated response:**
> David, thank you for the honest feedback — and I'm sorry about the wait, especially with a reservation. You're right, we were short-staffed on host stand that night and it showed. We've added an extra person to the Friday night rotation starting this week. Glad the table service made up for it, and we'd love to have you back to show you the difference. Next round of drinks is on us — just mention this when you book.
>
> — Elena, GM

**Why this works:** Doesn't argue with the perception, takes concrete action (extra host on Fridays), offers a specific incentive (drinks on them), and signs with a real person.

---

## The Workflow

```
Google review  →  Webhook / API poll  →  AI drafts response  →  Dashboard queue  →  Owner reviews  →  Posts
```

- New review detected within 2 hours
- AI generates 2 tone options (professional / warm)
- Owner gets email: "New review from Maria K. — response ready for your review"
- Owner edits or approves from phone in <30 seconds
- Posted automatically after approval

## What Makes This Different From the FTC Trap

The FTC's Consumer Review Rule (16 CFR Part 465, eff. Oct 2024) bans:
- Creating fake reviews
- Buying fake social proof
- Incentivizing specific sentiment

It does **not** prohibit:
- Automatically generating responses to *existing* reviews
- Making the business owner approve before posting
- Managing the review request/response workflow

The line is: the review must be real. The response is just customer service.

## Tech Stack

| Component | Tool | Cost |
|---|---|---|
| Monitor new reviews | Google Business Profile API | $0 |
| AI response generation | Claude API / GPT-4o | ~$0.05/review |
| Approval dashboard | Simple web app (Next.js) | $0 |
| Email notifications | Resend | $0-10/mo |
| Hosting | Vercel free tier | $0 |

**Total infra cost: ~$10-20/mo for 20+ clients**

## Pricing

| Tier | Reviews/mo | Price |
|---|---|---|
| Solo | Up to 20 reviews/mo, email approval | $150/mo |
| Growth | Up to 50 reviews/mo, dashboard + analytics | $300/mo |
| Multi-location | Per location, consolidated dashboard | $200/location/mo |

Benchmark: local SEO agencies charge $1,000-3,000/mo for "reputation management" that includes this plus 15 other services. You're offering *just* this for a fraction.

## First Sale

1. Pick a local business with 50+ Google reviews and inconsistent responses (responds to some, not all)
2. Manually respond to their last 20 unanswered reviews by hand
3. Show them the difference: "Your 20 unanswered reviews were sending a signal you don't respond to feedback — now they all have thoughtful replies"
4. Offer the automated system at $150/mo
5. Ask: "What would it be worth to never write a review response from scratch again?"

## Legal Boundary

- The response is approved by the business owner before posting — you are not representing yourself as the business
- No fake reviews are generated — only responses to real reviews
- The AI does not post anything without human approval
- The line you don't cross: automating the posting step without review, generating fake reviews, or writing responses that misrepresent the business (e.g., promising refunds without authorization)

**Risk: Near-zero.**
