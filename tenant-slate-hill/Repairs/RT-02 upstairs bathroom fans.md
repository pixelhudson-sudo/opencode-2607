---
type: repair-ticket
ticket: RT-02
status: open
priority: medium
opened: 2026-06-21
location: Both upstairs bathrooms
habitability: yes — ventilation (mold mitigation)
---

# RT-02 — Both upstairs bathroom fans not working

## Symptom
In both upstairs bathrooms the **light works but the exhaust fan does not run**. Fans used to work. Suspected bad connection (noted 2026-06-18: "I want to fix the fans. It was a bad connection").

## Likely cause
Combo light/fan units. Light circuit is live, fan circuit is dead → most likely a **failed fan motor**, a **broken/loose fan wire**, or (if the fan was on its own switch) a **dead switch leg**. Two units failing the same way also points to age/motor wear or a shared switch issue.

## Plan — proposed approach (splice fan onto the lighting feed)
The idea: since the light's hot is confirmed live, **tap the fan's hot from the light's hot** so the fan runs whenever the light is on.

**⚠ Do this only after diagnosing — read first:**
1. **Kill power at the breaker.** Confirm dead with a non-contact tester before touching wires.
2. **Test the fan motor itself** — apply line voltage directly to the fan motor leads (or jump it from the known-live light hot) for a few seconds. If the fan doesn't spin, the **motor is dead → splicing won't help, replace the unit/motor**. Splice only makes sense if the motor is good but its feed is broken.
3. If motor is good: **pigtail the fan hot to the light hot** (and fan neutral to the shared neutral) with a wire nut. Result = fan + light run together off the one switch.
4. **Tradeoff to accept:** fan will no longer be independently switchable — it runs with the light, and stays off when the light is off. For a bathroom that's usually fine (and actually good for the mold problem), but you lose run-on-after-shower control unless you add a timer/humidistat switch later.

## Better option to weigh
Given the **active mold/moisture problem downstairs and upstairs**, replacing the units with a **humidity-sensing fan** (auto-runs when humidity rises) directly attacks the mold and removes the human-forgot-to-switch-it failure. ~$30–60/unit vs ~free splice. Strongly consider for at least the unit nearest the moisture.

## Parts / cost
- Splice route: wire nuts only (~$0–5)
- Replace fan motor: ~$20–40/unit
- Humidity-sensing exhaust fan: ~$30–60/unit

## Notes
- Ventilation ties directly to the §235-b mold exposure — documenting this fix helps the habitability record. Scheduled to check fans 2026-06-22 ~9am.

## Log
- 2026-06-21 — ticket opened
