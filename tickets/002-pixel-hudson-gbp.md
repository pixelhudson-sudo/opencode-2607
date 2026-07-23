---
id: 002
title: Create Google Business Profile for Pixel Hudson AI Consulting
status: building
branch: ""
pr: ""
---
## Goal
Create a new Google Business Profile for "Pixel Hudson" (AI consulting) at 185 Grange Rd Ste 2, Otisville, NY 10963, request mail verification, and get the listing live on Google Maps.

## Acceptance criteria
- AC-1: Google Business Profile is created under pixelhudson@gmail.com with business name "Pixel Hudson"
- AC-2: Profile is set to category "AI Consulting" or closest available category for local business AI consulting
- AC-3: Address is set to 185 Grange Rd Ste 2, Otisville, NY 10963
- AC-4: Service area is configured as 40 miles around Middletown, NY (customers travel to office + service-area coverage)
- AC-5: Business hours set to 8:00 AM – 6:00 PM daily
- AC-6: No phone number or website listed on profile
- AC-7: Verification postcard is requested to the Grange St address
- AC-8: Verification code from the postcard is entered once received, making the listing public

## Non-goals
- NG-1: No profile description or photos will be added (left blank / default)
- NG-2: No paid features (Google Ads, Local Services Ads, etc.)
- NG-3: No phone or website will be added to the profile
- NG-4: Do not create a new Google account — use existing pixelhudson@gmail.com
- NG-5: No posts, reviews management, or ongoing maintenance

## Scope / files
- `guides/pixel-hudson-gbp-setup.md` — step-by-step setup guide documenting every click, field, and decision
- Verification postcard tracking note (log expected delivery date)

## Test notes
1. Log into Google Business Profile dashboard (pixelhudson@gmail.com)
2. Confirm "Pixel Hudson" profile exists with status "awaiting verification" or "live"
3. Confirm address matches 185 Grange Rd Ste 2, Otisville, NY 10963
4. Confirm service area set to 40 mi around Middletown, NY
5. Confirm hours: 8 AM – 6 PM, every day
6. If awaiting verification: confirm postcard was requested to Grange St address
7. After postcard arrives: enter code, confirm listing is public on Google Maps
