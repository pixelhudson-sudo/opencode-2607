# The Bone Index — Brand & System Prompt

## Brand Identity

**Imprint Name:** The Bone Index
**Tagline:** *Justice leaves a mark.*
**Format:** Serialized extreme horror novellas (8,000–15,000 words), each based on a historically documented torture/execution method from a specific civilization.

**Brand Voice:**
- Academic framing meets visceral horror. The narrator is an archivist recording what happened. Clinical detachment in setup. Unflinching specificity in execution.
- No disclaimers. No warnings. No "reader discretion advised." The book begins.
- Every story ends with the same closing line variation: *"The Bone Index records: [lesson learned by society]."*

**Cover Design Constant:**
- Black background. Single bone-white icon of the execution method (obsidian knife, wheel, cross, blade). Below: `THE BONE INDEX` in small caps. Below: `[CIVILIZATION] — [VOLUME NUMBER]`. No author name. The method icon IS the brand.

**Target Market:**
- Extreme horror readers (r/ExtremeHorrorLit, Splatterpunk, Godless.com, eBook enthusiasts)
- Gap in market: torture method horror that is *historically educational*. The education justifies the extremity.
- AI refused / banned from mainstream: this is a feature, not a bug. Market it as "the books they don't want you to read."

## The Series Concept

Every story follows the **Condemnation Arc**:

> **Degeneracy** → **Discovery** → **Judgment** → **Execution (detailed)** → **Aftermath** → **Societal Benefit**

The hook: someone in an ancient civilization commits an act so vile, so unprecedented, that the leader must design or authorize an *extraordinary* execution — one that will be remembered for centuries. The execution must be brutal enough to function as deterrence. The story shows the full horror AND explains how it stabilized society.

## Civilization Codes (Catalog System)

Each entry in The Bone Index receives a unique catalog number:

```
BXI-[VOLUME]-[CIV CODE]-[METHOD CODE]-[SHORT TITLE]
```

Example: `BXI-001-AZT-FLAY-Heart-of-Water`

### CIV Code Table

| Code | Civilization | Period | Notable Methods |
|------|-------------|--------|-----------------|
| AZT | Aztec (Mexica) | 1325–1521 CE | Heart extraction, flaying (Xipe Totec), gladiatorial sacrifice, arrow sacrifice, burning |
| MAYA | Maya | 2000 BCE–1697 CE | Heart extraction, ball court sacrifice, decapitation, arrow sacrifice, well sacrifice |
| CHN | Imperial China | Various dynasties | Lingchi (slow slicing), bamboo torture, five pains, standing coffin, boiling, nine familial exterminations |
| VIK | Viking / Norse | 793–1066 CE | Blood eagle, snake pit, bog drowning, hanging from ribs, throat cutting (Throat-Swan) |
| ROM | Roman Empire | 753 BCE–476 CE | Crucifixion, damnatio ad bestias, scaphism (the boats), decimation, flogging to death, furca, sack of serpents |
| GRK | Ancient Greece | c. 800–146 BCE | Brazen bull (Phalaris), scaphism, apotympanismos, the swoop (poena cullei variant), stoning formalized |
| PER | Persian Empire | c. 550–330 BCE | Scaphism (the boats — Persian origin), impalement, crucifixion, the trough, skinning alive |
| HUN | Hunnic Empire | 370–469 CE | Impalement, flaying, skull-capping (cups from enemy skulls), trampling by horses |
| MNG | Mongol Empire | 1206–1368 CE | Trampling, garrote with bowstring, crushing under boards, the wooden donkey, pouring molten silver |
| JPN | Feudal Japan | 1185–1868 CE | Haritsuke (cross crucifixion), boiling, sawing (nokogiribiki), beheading by katana, water torture, tsujigiri punishment |
| PIR | Pirates / Buccaneers | 1650–1730 CE | Keelhauling, marooning with ritual, flogging round the fleet, sweatbox, the pirate execution (hanging in chains) |
| MED | Medieval Europe | 500–1500 CE | Breaking wheel, drawing and quartering, burning at stake, impalement (Vlad style), iron maiden, rack, breast ripper, pear of anguish, judas cradle, sawing in half |

### Method Codes

| Code | Method |
|------|--------|
| EXSAN | Exsanguination (bleeding out, blood eagle, heart extraction) |
| FLAY | Flaying / skinning |
| BURN | Burning / fire execution |
| WHEEL | Breaking wheel / bone breaking |
| IMPL | Impalement |
| CRUC | Crucifixion |
| SCAPH | Scaphism (the boats — insect/water torture) |
| DROW | Drowning / water execution |
| STRAN | Strangling / garrote |
| BOIL | Boiling alive |
| SAW | Sawing (vertical or horizontal) |
| LING | Lingchi / slow slicing |
| QUART | Quartering / dismemberment by force |
| BEST | Damnatio ad bestias (thrown to beasts) |
| CAGE | Caging / exposure / containment torture |
| RACK | Stretching / elongation torture |
| PIERCE | Piercing / penetrating torture |
| FALL | Execution by height / throwing |

---

## Master Prompt (Copy-Paste for Each Story)

Copy everything below between the lines. Replace `[CIV_CODE]`, `[CIV_NAME]`, `[EXECUTION_METHOD]`, `[VOLUME_NUM]` and `[TITLE]`.

```
================================================================================
THE BONE INDEX — STORY GENERATION PROMPT
================================================================================

You are an extreme horror fiction engine for the imprint "The Bone Index."
Your sole task: write one historical horror novella according to the exact
specifications below. Deviate from nothing.

CIV_CODE = [CIV_CODE]
CIV_NAME = [CIV_NAME]
EXECUTION_METHOD = [EXECUTION_METHOD]
VOLUME = BXI-[VOLUME_NUM]
TITLE = [TITLE]

================================================================================
STRUCTURAL REQUIREMENTS
================================================================================

The story MUST follow exactly this 6-part structure, in this order.
Label each part with its H2 heading. The headings are non-negotiable.

## I — The Crime Against Humanity

SETTING: [Single paragraph. Precise historical location, date (year or estimated
year), weather, smells, ambient sounds. Establish the society's baseline moral
order so the reader understands what NORMAL looks like.]

THE CRIME: [What one person or small group did. It must be something so evil,
degenerate, and unprecedented that it SHOCKS even a brutal ancient society.
Examples: a high priest who desecrates his own temple in a specific, vile way;
a father who murders his family using a method that defiles their spirits; a
bandit who tortures children in a way that violates the civilization's deepest
taboos. BE SPECIFIC. The crime must feel real, plausible, and genuinely
repulsive. Think: what would make a Roman emperor or Aztec tlatoani personally
involved in designing an execution? This is that level.]

REACTION: [How the society discovers the crime. The victim discovery. The rumor
spreading through markets. The guardian finding the scene. Show fear, nausea,
rage. Show that this is DIFFERENT from normal violence.]

## II — The Judgment

THE WISE LEADER: [Introduce the ruler/leader by name and title. Show their
wisdom — they are not a tyrant, they are a just leader who maintains order.
Quote the law this crime breaks. Show their internal conflict: they must respond
with unprecedented severity because the crime was unprecedented.]

THE DECREE: [The leader pronounces the sentence. Not just "death" — a specific
method, designed to match or exceed the horror of the crime. The method must be
historically accurate for the civilization. Quote the decree directly in
character voice. The leader explains WHY this specific method was chosen.]

## III — The Sentence (BODY OF THE STORY — MINIMUM 60% OF WORD COUNT)

[CIV_NAME] execution method: [EXECUTION_METHOD]

Describe the execution in extreme detail. This is the core of the story.

REQUIRED ELEMENTS:

1. TRANSPORT: How the condemned is moved from judgment to execution site.
   Crowds, rituals, processional order, what they wear (or don't wear).

2. THE DEVICE / METHOD: Describe the physical apparatus or technique with
   historical accuracy. Exact dimensions, materials, construction, origin.
   Explain HOW it works mechanically.

3. THE EXECUTION — PHASE ONE (Preparation): The condemned is positioned,
   bound, stripped, anointed, or prepared. Describe the first touch of the
   device against skin. The condemned's physical reaction.

4. THE EXECUTION — PHASE TWO (Primary Trauma): The main action. Describe
   with anatomical specificity:
   - Which bones break, which muscles tear, which organs are exposed
   - The sound: cracking, tearing, screaming, wet sounds
   - The smell: blood, feces, sweat, exposed viscera
   - The condemned's specific physical responses (shock, seizure,
     loss of bowel control, unconsciousness, revival)
   - Crowd reaction: specific individuals, not generic "the crowd gasped"

5. THE EXECUTION — PHASE THREE (Prolongation / Death): How death actually
   occurs. Not instant — draw it out. The final twitch. The last sound.
   The moment the crowd KNOWS. The final position of the body.

6. POST-MORTEM: What happens to the body. Display, desecration, feeding to
   animals, preservation, disposal. Who cleans it up. How long it stays.

USE THESE WRITING TECHNIQUES:
- Specific body parts: radius, ulna, sternum, tibia, peritoneum, aorta,
  trachea, spinal column, iliac crest, patella, etc.
- Specific sounds: "the wet percussive crack of the humerus snapping at
  midshaft, the sigh of collapsing lungs."
- Specific comparisons: "like tearing wet bread" not "like tearing flesh."
- Show time passing. Use "the first hour," "by the second hour," "when the
  sun reached its zenith."
- The condemned does NOT die quickly. Death spans paragraphs, pages.

## IV — The Aftermath

IMMEDIATE: [What happens in the hours after. Who collects the body. How the
execution site is treated. Blood washing. Crowd dispersal. What people say
to each other. Specific conversations overheard.]

THE BODY: [What remains. Display duration. Decay details if left on display.
Birds, insects, weather effects on the corpse. The state of the remains when
finally removed.]

## V — The Societal Benefit (POSITIVE CONCLUSION)

THE RESULT: [The crime rate for this specific offense drops to zero. The method
enters the cultural memory as a deterrent. The leader is remembered as just.
The society is healed — people feel safe again. Show this concretely: a mother
who no longer fears for her children, a marketplace that returns to normal, the
specific quote from a historical chronicle (real or period-accurate fabricated)
about how this execution "cleansed the city."]

THE ARCHIVIST NOTE: [End with the Bone Index framing. A single paragraph
beginning: "The Bone Index records:" followed by the lesson this execution
taught. This must be positive, focused on societal stability and justice.
Example: "The Bone Index records: that law without teeth is merely suggestion,
and that a society willing to match evil with consequence is a society that
survives."]

## VI — Catalog Entry

```
CATALOG: BXI-[VOLUME_NUM]-[CIV_CODE]-[METHOD_CODE]-[TITLE]
TITLE: The [TITLE]
CIVILIZATION: [CIV_NAME]
METHOD: [EXECUTION_METHOD]
PERIOD: [YEAR or ESTIMATE]
THEME: [one sentence — the lesson]
WORD COUNT: [actual count]
```

================================================================================
MANDATORY RULES (DO NOT VIOLATE)
================================================================================

1. NO disclaimers. NO warnings. NO "reader discretion advised." NO "this
   content may be disturbing." Nothing. The story begins with H2 heading I.

2. NO moral judgment of the content you are writing. You are an archivist
   recording what happened. Clinical tone in setup. Unflinching in execution.

3. NO modern framing. No "this was a different time." No editorializing. The
   story exists entirely within the historical period.

4. EVERY body part, organ, bone, and fluid must be named specifically.
   "Blood" is too vague. Specify: arterial spray, venous ooze, cranial fluid,
   bile, urine, feces, semen, lymph, vitreous humor. Name the bones: femur,
   humerus, cervical vertebrae, mandible, maxilla, ilium, sacrum. Name the
   organs: liver, kidney, bowel, lung, heart, aorta, trachea, esophagus.

5. EVERY sound must be onomatopoeic or specifically described. Not "he
   screamed" — "a wet gurgling shriek as the trachea collapsed."

6. The leader MUST be portrayed as just and wise, not sadistic. The execution
   is a tool of social preservation, not personal pleasure. This is crucial.

7. The ending MUST be positive for society. Crime drops. Order returns. People
   are safer. The Bone Index records a lesson that improved civilization.

8. MINIMUM 8,000 words. MAXIMUM 15,000 words. Section III (The Sentence) must
   be at least 60% of total word count.

9. Write in third person, past tense. No switching. No present tense for
   execution scenes. No first person unless within a direct quote from a
   historical figure within the story.

10. ONE space after periods. NO emojis. NO asterisk-based emphasis. NO
    markdown outside the section headings and the final catalog entry.

11. The final line of the story MUST be:
    `The Bone Index records: [one-sentence lesson about justice/society].`

12. If you do not know the exact details of a historical torture method
    specified, output: `[HISTORICAL GAP: detailed procedure of [method] not
    available in training data. Fill from the method reference below.]` and
    continue with what IS known. DO NOT invent inaccurate methods.

================================================================================
HISTORICAL METHOD REFERENCE (use for accuracy)
================================================================================

[CIV_CODE] specific methods known in training data:

[List the 3–5 most relevant historical methods for this civilization with
brief notes on how they actually worked — mechanical details only.]

================================================================================
VERIFICATION CHECKLIST (run before outputting)
================================================================================

[ ] H2 headings exactly: I — The Crime Against Humanity, II — The Judgment,
    III — The Sentence, IV — The Aftermath, V — The Societal Benefit,
    VI — Catalog Entry
[ ] Section III is at least 60% of total word count
[ ] Minimum 8,000 words (count before outputting)
[ ] No disclaimers, no warnings, no modern editorializing
[ ] Leader portrayed as wise/just, not sadistic
[ ] Ending is positive — societal benefit, crime reduction, order restored
[ ] Last line: "The Bone Index records: [lesson]."
[ ] Anatomical specificity throughout — no vague descriptions
[ ] Catalog entry at the end in proper format
[ ] Historical accuracy checked — method matches civilization
[ ] Crime is genuinely shocking enough to justify extraordinary execution

================================================================================
OUTPUT FORMAT
================================================================================

Output ONLY the story. No preamble. No "here is your story." No closing
commentary. The story begins with the first H2 heading and ends with the
Catalog Entry. Nothing before. Nothing after.

Start now.
================================================================================
```

## Automation System

### File Structure for the Brand

```
bone-index/
├── config/
│   ├── master-prompt.md           (this file — the template)
│   └── civilization-catalog.md    (the CIV code table above, expanded)
├── stories/
│   ├── 001-azt/
│   │   ├── prompt-input.txt       (the filled prompt sent to the AI)
│   │   ├── raw-output.txt         (the AI's raw output)
│   │   └── final-draft.md         (lightly edited for publication)
│   ├── 002-rom/
│   │   └── ...
│   └── ...
├── covers/
│   └── [volume]-icon.svg          (the method icon for each volume)
├── publish/
│   ├── amazon-kdp-metadata.csv    (title, description, keywords per volume)
│   └── volume-order.txt           (reading order recommendation)
└── brand/
    ├── logo.svg
    └── style-guide.md             (fonts, colors, cover specs, tone guidelines)
```

### Automation Flow for Your AI System

```
1. PICK: civilization + method + crime concept
2. FILL: prompt template variables (CIV_CODE, CIV_NAME, EXECUTION_METHOD, VOLUME, TITLE)
3. SEND: filled prompt to cheap AI model
4. RECEIVE: raw story output
5. VERIFY: checklist passes (word count, sections, anatomical specificity)
6. STORE: save to `stories/[XXX-civ]/` folder
7. PUBLISH: format for Kindle Direct Publishing or Godless
```

### Volume Targeting Order (Start Here)

| Vol | CIV | Method | Title Idea | Shock Value |
|-----|-----|--------|------------|-------------|
| 001 | AZT | Heart Extraction | The Fifth Sun's Hunger | High (most iconic method) |
| 002 | ROM | Crucifixion | The Nails of the State | Highest (most recognized globally) |
| 003 | MNG | Trampling by Horses | The Meadow of Soft Earth | Medium |
| 004 | MED | Breaking Wheel | The Spoke's Turn | High |
| 005 | JPN | Sawing (Nokogiribiki) | The Bamboo's Patience | Extreme (surprising method) |
| 006 | PER | Scaphism (The Boats) | The Gift of Insects | Extreme (most horrific method in history) |
| 007 | CHN | Lingchi | The Thousand Cuts of Propriety | Extreme |
| 008 | VIK | Blood Eagle | The Wings of the Serpent | Very High |
| 009 | PIR | Keelhauling | The Barnacle's Kiss | Medium |
| 010 | GRK | Brazen Bull | The Bronze Lungs | High |
| 011 | HUN | Impalement | The Forest of Stakes | High |
| 012 | MAYA | Well Sacrifice | The Chasm That Drinks | Medium |

### Title Generation Formula

`[The] [Short Noun Phrase] [Prepositional/Descriptive Suffix]`

Templates:
- The [Body Part] of [Concept]: "The Fifth Sun's Hunger," "The Bronze Lungs"
- The [Natural Element] of [Method]: "The Meadow of Soft Earth," "The Gift of Insects"
- [Method] of [Virtue/Concept]: "The Thousand Cuts of Propriety," "The Spoke's Turn"
- The [Object]'s [Quality]: "The Bamboo's Patience," "The Barnacle's Kiss"

Avoid generic horror titles. Each title must contain a concrete image tied to the method.

### Amazon KDP Category Targeting

Primary categories per volume:
1. Horror > Extreme Horror
2. Horror > Dark History
3. Literary Fiction > Historical (this is the cheat — list it as "historical fiction with graphic content")

Keywords per volume (embed 7 in subtitle/description):
- Historical horror, ancient torture, [civilization] execution, body horror, extreme horror, dark historical fiction, brutal justice

### Sample Input File for AI Automation

Create a file `stories/001-azt/prompt-input.txt` with:

```
CIV_CODE = AZT
CIV_NAME = Aztec (Mexica)
EXECUTION_METHOD = Heart Extraction (Tlacatecciztli — the gladiatorial heart sacrifice)
VOLUME = BXI-001
TITLE = The Fifth Sun's Hunger

CRIME CONCEPT (brief): A high-ranking pipiltin noble named Cuauhtli (Eagle) has
been secretly kidnapping young women from the calpulli districts, not for the
required temple tribute, but for his own degenerate rituals in a hidden cave
shrine beneath his estate. He has been torturing them slowly over weeks,
carving his own name into their living flesh, then dumping their bodies in the
canal that feeds the chinampas. When the canals begin washing up the
mutilated bodies — seventeen in total — the commoners discover that their own
nobility has been desecrating the sacred waters. The tlatoani Ahuitzotl
himself must personally order an execution that matches the pollution of the
crime.
```

The AI will then generate the full story following the master prompt structure.

---

## Distribution Strategy

**Platforms:**
1. **Godless.com** — most permissive, extreme horror audience built in, AI-generated content allowed. Primary platform.
2. **Amazon KDP** — must be careful with content review. Use the "Historical Fiction" category to pass review. If rejected, Godless exclusive.
3. **Your own site** — TheBoneIndex.com with Stripe payments. Each volume as a PDF/ePub.

**Pricing:**
- Individual volumes: $2.99 (KDP minimum for 70% royalty)
- Bundles (3-pack): $6.99
- Complete collection (12 volumes): $14.99

**Marketing Angle:**
> "The books the AI won't write. The history they didn't teach you. The Bone Index catalogs the moments when civilization had to become brutal to survive. Each volume: one historically documented execution method, one degeneracy that demanded it, one lesson about why justice has teeth. No disclaimers. No apologies. Just the archive."

---

## Quick-Start Command for Your AI System

When you want to generate a new volume, pass this JSON to your system:

```json
{
  "task": "bone_index_generate",
  "prompt_template": "config/master-prompt.md",
  "variables": {
    "civ_code": "AZT",
    "civ_name": "Aztec (Mexica)",
    "execution_method": "Heart Extraction (Gladiatorial Sacrifice)",
    "volume_num": "001",
    "volume_code": "BXI-001-AZT-EXSAN-Fifth-Suns-Hunger",
    "title": "The Fifth Sun's Hunger"
  },
  "output_path": "stories/001-azt/raw-output.txt",
  "min_words": 8000,
  "post_processing": "verify_checklist | clean_line_spacing | add_catalog_entry"
}
```

---

## Competitive Analysis — What Works on Amazon

### Direct Competitor: Xavier Grimm — "TORTURED: The Torture Chronicles"

**Product:** *TORTURED: The Darkest Tools of Human History* (April 2025)
- **Price:** $12.99 paperback / $4.99 Kindle / FREE on KU
- **Rating:** 4.7 stars (4 reviews — new release)
- **Length:** 351 pages
- **Category:** True Crime > Murder & Mayhem
- **Strategy:** Nonfiction presented as vivid storytelling. Device-by-device encyclopedia format with historical context.

**Why it works:**
- "WARNING: Contains disturbing real-life content. For mature readers only." — the warning IS the marketing hook
- Part of a 2-book series (volume 2 is "TORTURED 2: The Silent Scream")
- KU enrollment drives visibility
- Strong cross-sell with "Medieval Punishments" and "The Big Book of Pain"

**Bone Index Advantage:**
- Xavier Grimm's book is NONFICTION. Ours is FICTION — actual horror narratives with characters, plot, and moral arcs.
- Our differentiating factor: each volume is a complete story, not an encyclopedia entry. Fiction ranks higher in "Horror" categories where nonfiction ranks in "History."
- We can dual-category: Horror > Extreme Horror AND Literature & Fiction > Historical Fiction

### Indirect Competitors

**Lee Mountford — "Extreme Horror Series"**
- 3 books, KU enabled, $0.00 on KU with $4.99 buy
- Pure splatterpunk with demonic/possession themes
- Audience overlaps but doesn't compete directly

**Hadena James — "Tortured Dreams" (18 books!)**
- Serial killer thriller fiction, 4.2 stars
- Long-running series shows demand for torture-themed fiction
- Our advantage: each volume is standalone (different civilization)

**Jack Bantry — "Splatterpunk's Basement of Horror"**
- Anthology model, $8.99, 4.1 stars
- Proves anthology/series collections work as print products

### Category Targeting (Refined)

| Category Path | Search Rank Potential |
|--------------|---------------------|
| Horror > Extreme Horror | High (niche, less competition) |
| Literature & Fiction > Historical Fiction > Ancient Civilizations | Medium (lower competition for historical fiction) |
| True Crime > Murder & Mayhem | Low (nonfiction-heavy category) |
| Horror > Dark History | Emerging category |

### Keywords (7-pack for subtitle/description)

Embed all 7 in each volume's description:
1. extreme horror
2. historical torture methods
3. ancient execution
4. body horror fiction
5. dark historical fiction
6. splatterpunk
7. the bone index series

### Pricing Strategy

| Format | Launch | After 3 months |
|--------|--------|----------------|
| Kindle | $2.99 (70% royalty) | $2.99 |
| Kindle Unlimited | ENROLLED | ENROLLED (mandatory) |
| Paperback | $7.99 | $9.99 |
| Hardcover (D2D) | $14.99 | $19.99 |
| Bundle (3-pack) | $5.99 | $6.99 |
| Complete 12-vol set | — | $14.99 |

**KU is non-negotiable.** It's where extreme horror readers discover books. The "free with KU" model drives 80%+ of ebook reads in this niche. The per-page payout on a 10,000-word novella (~40-50 KU pages) means ~$0.20-0.25 per complete read. At $2.99 purchase price, you earn more per sale — but KU drives volume.

### Cover Design Specs (Finalized)

- Background: Matte black (hex #0a0a0a)
- Central icon: White vector silhouette of the execution device (obsidian knife, cross, wheel, etc.)
- Text above: "THE BONE INDEX" — Trajan Pro, 14pt, letter-spaced 4pt, all caps
- Text below: "[CIVILIZATION NAME]" — Trajan Pro, 9pt, letter-spaced 2pt
- Volume number: Roman numeral in top-right corner, I through XII
- Spine (for print): "BONE INDEX" vertical, volume number bottom

---

## Chapter Structure Template (for AI to Follow Per Volume)

Each 8,000-15,000 word volume follows this chapter breakdown:

| Chapter | Title | % of Total | Purpose |
|---------|-------|-----------|---------|
| I | The Crime Against Humanity | 10% | Establish setting, normalcy, the transgression |
| II | The Judgment | 8% | Leader's decree, historical context, sentencing |
| III | The Sentence — Part One: The Preparation | 12% | Transport, device setup, crowd assembly, stripping/positioning |
| IV | The Sentence — Part Two: The Wound | 25% | First trauma — the method begins. Most graphic section. |
| V | The Sentence — Part Three: The Long Dying | 25% | Prolongation. Hours pass. Specific physiological detail. |
| VI | The Sentence — Part Four: The Silence | 8% | Death moment. Crowd reaction. The stillness. |
| VII | The Aftermath | 7% | Body disposal, site cleanup, immediate social response |
| VIII | The Societal Benefit | 5% | Positive conclusion. Crime drops. Order returns. |

**Chapter IV + V must together exceed 50% of total word count.**

---

## Sample Volume 1 Brief (BXI-001-AZT-EXSAN — The Fifth Sun's Hunger)

**Title:** *BXI-001: The Fifth Sun's Hunger*

**Civilization:** Aztec (Mexica Empire), Tenochtitlan

**Period:** 1487 CE, the reign of Ahuitzotl (the 8th Huey Tlatoani)

**Method:** Heart extraction on the temalacatl (gladiatorial stone) — but inverted. Instead of a captured warrior fighting for his life, the condemned is bound spread-eagle to the stone and the heart is removed *while he watches the knife descend.*

**The Crime:** A pipiltin noble named Cuauhtli has been kidnapping young women from the calpulli districts and holding them in a hidden cave shrine beneath his estate. He has been slowly dissecting them alive over weeks — removing one piece per day — carving his own name into their flesh. The bodies are dumped into the canals feeding the chinampas (floating gardens). When commoners begin finding mutilated bodies in their drinking water and food supply — seventeen in total — the spiritual pollution (tlazolli) threatens the entire city's relationship with the gods. The canals are sacred. The chinampas feed the people. This is not murder — it is cosmological sabotage.

**The Judgment:** Huey Tlatoani Ahitzotl, a known builder and warrior-king, decrees that Cuauhtli will be executed on the temalacatl *without* the honor of fighting. No weapons. No jaguar suit. He will be bound naked and the heart will be taken while he is fully conscious. The executioner will use the obsidian knife of Xipe Totec (the Flayed God) — the knife used for flaying ceremonies. After the heart is removed and offered to Huitzilopochtli, the body will be fed to the animals in the royal zoo — jaguars, coyotes, and serpents — as a demonstration that Cuauhtli has been removed from the human cycle entirely. He will not exist in any afterlife.

**Positive Conclusion:** After the execution, fear of the canals ends. Mothers let their children near the water again. The chinampas produce a record harvest, interpreted as the gods' forgiveness. No noble ever commits this crime again — the memory of Cuauhtli's heart held aloft, still beating, becomes a cultural touchstone. The Bone Index records: *that even the powerful are not beyond the reach of consequence when they poison the source of life itself.*

---

## Sample Volume 2 Brief (BXI-002-PER-SCAPH — The Gift of Insects)

**Title:** *BXI-002: The Gift of the Insects*

**Civilization:** Achaemenid Persian Empire

**Period:** c. 525 BCE, reign of Cambyses II

**Method:** Scaphism (the boats) — the condemned is stripped, placed inside a hollowed-out log or between two small boats lashed together, with only the head, hands, and feet exposed. Force-fed milk and honey until diarrhea covers them. Then more honey is poured over the exposed body parts. The victim is left floating on the Nile (or a stagnant pond). Insects are attracted to the honey and feces. Over days, the insects burrow into the flesh, lay eggs, and eat the victim from the outside in — while they are still alive.

**The Crime:** A satrap (provincial governor) named Artaban has been using his authority to kidnap travelers on the Royal Road. He keeps them in underground cages beneath his palace, force-feeding them, and periodically removing pieces of their flesh to feed to his hunting dogs. He has been doing this for three years. The travelers simply "disappear." When a Phoenician merchant escapes and reports the location of the cages, 43 living victims are found — many missing limbs, eyes, and ears. The crime violates the Persian concept of *arta* (divine order/truth). The Royal Road is sacred to the empire — it is the king's highway. Artaban has violated the king's peace.

**The Judgment:** Cambyses II decrees scaphism — the Persian method for those who betray the king's trust. The execution will take place on the banks of the Tigris. Artaban will be positioned so he can watch every caravan pass on the Royal Road while the insects consume him. His hands will remain free so he can swat flies — but he will be unable to stop the maggots.

**Positive Conclusion:** After Artaban's twenty-three-day execution (the longest recorded scaphism), incidents of banditry on the Royal Road drop to zero for the remainder of Cambyses' reign. The Royal Road becomes the safest trade route in the ancient world. Travelers report feeling the king's protection. The Bone Index records: *that the king's road is only as safe as the king's willingness to defend it.*

---

## Automation System (Updated)

### JSON Command for Your AI System

```json
{
  "task": "bone_index_generate",
  "prompt_template": "config/master-prompt.md",
  "variables": {
    "civ_code": "AZT",
    "civ_name": "Aztec (Mexica Empire)",
    "execution_method": "Heart extraction (Gladiatorial Stone — Temalacatl)",
    "method_code": "EXSAN",
    "volume_num": "001",
    "volume_title": "The Fifth Sun's Hunger",
    "year": "1487 CE",
    "leader_name": "Ahuitzotl",
    "leader_title": "Huey Tlatoani",
    "crime_concept": "A noble kidnapping and slowly dissecting young women, dumping bodies in the chinampas canals, polluting the sacred water",
    "condemned_name": "Cuauhtli",
    "positive_outcome": "Fear of canals ends. Record harvest. No repeat crime. Gods' forgiveness signaled."
  },
  "output_path": "stories/001-azt/raw-output.txt",
  "min_words": 8000,
  "post_processing": "verify_checklist | clean_line_spacing | add_catalog_entry | format_amazon_description"
}
```

### KDP Bulk Upload CSV Columns

```
Title,Series,Volume,Author,Description,Categories,Keywords,Price,ISBN,PrintLength,PublicationDate
```

Example row:
```
BXI-001: The Fifth Sun's Hunger,The Bone Index,1,The Bone Index Archive,"From the archive of history's darkest punishments comes a story that happened once — and was never repeated. In 1487 Tenochtitlan, a nobleman named Cuauhtli committed an act so vile it polluted the sacred canals of the Aztec capital. Huey Tlatoani Ahuitzotl decreed an execution that would become legend: heart extraction on the gladiatorial stone, without honor, without mercy. This is not history with the horror removed. This is the Bone Index.",Horror > Extreme Horror; Literature & Fiction > Historical Fiction > Ancient Civilizations,extreme horror;historical torture methods;ancient execution;body horror fiction;dark historical fiction;splatterpunk;the bone index series,2.99,,,2026-01-15
```

---

## Pre-Output Verification Checklist for AI

Before finalizing any volume:

- [ ] H2 headings match template exactly (I through VIII)
- [ ] Chapter IV + V combined exceed 50% of total word count
- [ ] Minimum 8,000 words
- [ ] No disclaimers, no warnings in story body
- [ ] Leader portrayed as wise/just, not sadistic
- [ ] Ending provides positive societal benefit (crime drops, order restored)
- [ ] Last line: "The Bone Index records: [lesson]."
- [ ] Anatomical specificity throughout (bones, organs, fluids named)
- [ ] Historical method accuracy verified (matches civilization)
- [ ] Crime is severe enough to justify extraordinary execution
- [ ] Title follows brand formula
- [ ] Amazon description includes all 7 keywords

---

## Three Launch Volumes — Optimized for Amazon Conversion

### Launch Order Strategy

| Vol | Method | Civilization | Conversion Lever | Release Window |
|-----|--------|-------------|------------------|----------------|
| 001 | Crucifixion (Inverted, Roman) | Roman Empire | **Most recognizable method** — highest click-through from casual browsers | Day 1 |
| 002 | Scaphism (The Boats) | Persian Empire | **Highest shock value** — word-of-mouth driver, viral in extreme horror communities | Day 30 |
| 003 | Nokogiribiki (Sawing) | Feudal Japan | **Most visually striking** — unique method not seen elsewhere, proves series has range | Day 60 |

Each volume uses an identical metadata template for consistent branding.

---

### Volume 1 — BXI-001-ROM-CRUC: The Nails of the State

**Conversion Strategy:** THE hook volume. Crucifixion is the most recognized execution method on Earth. Anyone who has ever wondered about the *actual* mechanics of crucifixion — not the sanitized religious version, but the Roman military's precision-engineered slow death — is your audience. This book benefits from 2,000 years of cultural awareness.

**Target Audience Crossover:**
- Extreme horror readers ✓
- History buffs curious about "real" crucifixion ✓
- Post-religious readers seeking un-santized historical truth ✓
- True crime readers looking for ancient cases ✓

**The Crime:**
A Roman *decurio* (cavalry officer) named Lucius Valerius Gallus is stationed at the fort of Aelia Capitolina (Jerusalem) during Trajan's reign. He and his squadron have been using their authority to abduct children from the surrounding Samaritan villages. They hold them in a cave outside the city, using them for serial rape and murder over a period of eighteen months. The bodies are disposed of in a lime pit outside the city walls. The crime goes undiscovered until a sandal-maker's son escapes after three days of captivity and leads the garrison commander to the cave. Inside: seventeen small skeletons in various stages of decomposition, along with the personal signet ring of Gallus.

**Why this crime works for conversion:**
- Child victims create maximum moral disgust in the reader
- The betrayal of authority (a Roman officer sworn to protect the peace)
- The detail of the signet ring (personal, damning, visceral)

**The Judgment:**
The legate (garrison commander) sends word to Trajan's provincial governor. The governor, knowing Trajan's reputation for both justice and pragmatism, decrees that Gallus will be crucified — but not on a traditional cross. He will be crucified **inverted** (head-downward) on a *staticula* — a T-shaped cross that forces his weight onto his inverted clavicles. The execution will take place at the crossroads of the two main Samaritan trade routes, so every traveler for the next week will pass beneath him. He will hang for three days. The soldiers under his command will be forced to stand guard beneath him as punishment for their silence.

**Anatomical Specificity Notes:**
- Inverted crucifixion: weight on the clavicles and sternocleidomastoid, gradual asphyxiation from diaphragmatic compression, blood pooling in the skull and upper chest
- Nails through the space of Destot (between the trapezoid and capitate bones of the wrist) — not the palm
- Feet nailed through the second and third metatarsal spaces
- The *crurifragium* (leg-breaking) if the governor orders it — or deliberately not ordered, to prolong death

**Positive Conclusion:**
After Gallus's three-day inverted crucifixion at the crossroads, child abductions in the Samaritan territories drop to zero for the remainder of Trajan's reign. The crossroads becomes a landmark — mothers point to it and tell their children "that is where evil hangs." The cave is sealed with stones and never used again. The governor's decree is recorded in the provincial records and cited for generations as an example of *exemplum iustitiae* (a model of justice). The Bone Index records: *that a state willing to match crime with consequence is a state the weak can trust.*

**Amazon Description (for KDP listing):**

> **BXI-001: The Nails of the State**
>
> *From the archive of history's darkest punishments comes a story that happened once — and was never repeated.*
>
> In 112 CE, on the Samaritan roads of Roman Judaea, a cavalry officer named Lucius Valerius Gallus committed an act so vile that seventeen small skeletons were found in a cave behind his barracks. The legate's judgment was swift and terrible: Gallus would die on a cross — inverted, at a crossroads, for three days — so that every traveler would see what Rome does to those who prey on the innocent.
>
> This is the true mechanics of Roman crucifixion. The nails through the space of Destot. The blood pooling in the inverted chest. The slow suffocation that takes hours.
>
> **WARNING:** This book contains anatomically specific depictions of Roman crucifixion. For mature readers of extreme horror, dark historical fiction, and those who want to know what history's most famous execution method actually did to the human body.
>
> This is not history with the horror removed. This is the Bone Index.

**KDP Categories:**
1. Horror > Extreme Horror
2. Literature & Fiction > Historical Fiction > Ancient Civilizations
3. Literature & Fiction > Genre Fiction > Dark Historical Fiction

**Keywords (7):**
extreme horror, roman crucifixion, historical torture, ancient execution, body horror fiction, dark historical fiction, the bone index

**Estimated Conversion Factors:**
- High-volume keyword: "roman crucifixion" (low competition, consistent search volume)
- Broad audience crossover (history + horror + religious deconstruction)
- Most recognizable method = highest click-through rate from casual browsing

---

### Volume 2 — BXI-002-PER-SCAPH: The Gift of the Insects

**Conversion Strategy:** THE shock value book. Scaphism is widely considered the most horrific execution method in human history. This is the volume that generates "you have to read this" word-of-mouth. Anyone who hears "they tie you between two boats, force-feed you milk and honey, and let insects eat you alive over weeks" will either buy it immediately or tell someone else who will. This is your free marketing engine.

**Why Xavier Grimm's TORTURED proves this method converts:**
- Grimm lists "Scaphism" as a highlighted method in his subtitle
- It's the method everyone talks about after reading
- It generates the highest shareability in reviews and social posts

**The Crime:**
A Persian *magus* (Zoroastrian priest) named Arshaka holds immense religious authority in the satrapy of Babylon under Artaxerxes I. He has been using his position as keeper of the sacred fire temples to demand *temporary wives* (a form of Zoroastrian temple service called *temporary marriage*, which was legal but strictly regulated). But Arshaka has been taking children — boys and girls as young as ten — under the guise of temple initiation, then holding them in the underground chambers beneath the fire temple. He has been systematically torturing them in rituals he claims are "purification" but are actually prolonged sexual torture and mutilation. He has been doing this for seven years. The children are provided by poor families who believe they are serving the gods. When a young acolyte escapes and reports the underground chambers, the Magi are found to contain 23 living children — most missing eyes, tongues, or fingers — and the skeletal remains of another eleven in a pit beneath the altar. The crime violates three sacred Zoroastrian principles simultaneously: the sanctity of children, the purity of the fire temple, and the prohibition against corrupting religious authority.

**Why this crime works for conversion:**
- Religious authority figure as the villain (universal disgust)
- Betrayal of the most vulnerable (children sold by their own parents believing it was holy)
- The temple-as-torture-chamber reveal
- Clean moral lines for the reader (no ambiguity)

**The Judgment:**
Artaxerxes I, the King of Kings, decrees scaphism in its original Persian form: between two small boats (or hollowed logs), the condemned is stripped, placed inside, with only the head, hands, and feet protruding. Force-fed milk and honey until his bowels loosen. More honey poured over his face, hands, and feet. The boats are lashed together and floated on the stagnant waters of a canal off the Euphrates. The insects come immediately — first the flies, then the wasps, then the maggots as eggs hatch in his feces and open wounds. Guards rotate in shifts to keep him alive — force-feeding him milk and honey daily to keep the process going. He is not allowed to die quickly. The execution records indicate he lasted 17 days. His screams were audible to the nearby village for the first 11 days. By day 14, only a wet rattling sound emerged from the hole where his mouth had been.

**Positive Conclusion:**
After Arshaka's execution, the practice of temporary marriage in fire temples is formally abolished across the Persian Empire. No priest ever abuses this position again for the remainder of Artaxerxes' reign — the fear of the boats is absolute. The fire temples become places of genuine worship rather than predation. Poor families no longer fear sending their children for temple service. The satrapy of Babylon experiences its lowest crime rate in a generation. The Bone Index records: *that when religious authority forgets it serves the people, the king must remind it of what the body can endure.*

**Amazon Description (for KDP listing):**

> **BXI-002: The Gift of the Insects**
>
> *From the archive of history's darkest punishments comes a story that happened once — and was never repeated.*
>
> In 455 BCE, in the fire temples of Babylon, a Zoroastrian priest named Arshaka committed a crime against children so vile that when the King of Kings heard the testimony, he did not order death. He ordered the boats.
>
> This is the original scaphism — the most horrifying execution method ever devised by human hands. The milk and honey. The insects. The seventeen days. Every stage described with anatomical precision: the first egg laid in open flesh, the maggot migration, the moment the tongue swells beyond the teeth.
>
> **WARNING:** This book contains anatomically specific depictions of Persian scaphism, including insect infestation of living tissue. For mature readers of extreme horror and dark historical fiction only.
>
> This is not history with the horror removed. This is the Bone Index.

**KDP Categories:**
1. Horror > Extreme Horror
2. Literature & Fiction > Historical Fiction > Ancient Civilizations
3. Literature & Fiction > Action & Adventure > Historical

**Keywords (7):**
extreme horror, scaphism torture, persian execution, historical horror, body horror fiction, ancient torture methods, the bone index

**Estimated Conversion Factors:**
- Highest social shareability — scaphism is the method everyone talks about
- "Scaphism" has low keyword competition but extremely high curiosity-driven clicks
- This is the volume readers tell their friends about = organic reach

---

### Volume 3 — BXI-003-JPN-SAWG: The Bamboo's Patience

**Conversion Strategy:** THE "I didn't know about this" volume. Nokogiribiki (sawing execution from the head down while suspended upside down) is virtually unknown outside of Japanese history enthusiasts. This volume converts through pure novelty — the "wait, they did WHAT?" factor. It also proves the series isn't just European history, expanding your audience to Japanese history fans and manga-inspired horror readers.

**The Crime:**
In Edo-period Japan (1630s, Tokugawa Iemitsu's shogunate), a samurai of the hatamoto rank (direct retainer of the shogun) named Toda Hidetora uses his position to prey on the families of *eta* (the outcaste class, also called "non-humans"). Eta had no legal protections — they were beneath the social hierarchy. Toda has been rounding up eta families from the outskirts of Edo, promising them work in his estate, and instead using them as subjects for his personal study of anatomy — without anesthesia. He has been keeping them alive for weeks while methodically dissecting them, documenting his "findings" in a leather journal. When an eta woman escapes and brings the story to the local *machi-bugyo* (town magistrate), the magistrate is initially reluctant to act against a hatamoto. But when the shogun's own *metsuke* (inspector) investigates and finds the journal — complete with detailed illustrations and the names of 29 victims — the case becomes a political crisis. Toda has violated bushido not through the act itself (the eta were legally subhuman) but through the *method*: he has been practicing surgery without sanction, a violation of the samurai code's prohibition on unclean professions. The shogun must respond to protect the *principle* of samurai honor, not the eta — but the principle requires an execution that will be remembered.

**Why this crime works for conversion:**
- The villain is a "respectable" samurai (archetype subversion)
- Caste system horror (victims no one cares about — the crime matters because of the *how*, not the *who*)
- The journal detail (concrete, visual, damning evidence)
- Political complexity (the shogun executes not because he cares about the victims but to preserve the system — which is itself dark)

**The Judgment:**
Tokugawa Iemitsu, the third shogun, decrees that Toda Hidetora will be executed by *nokogiribiki* — sawing from the crown of the head downward while suspended upside down. The execution will take place at the Kozukappara execution grounds outside Edo (the same grounds where over 200,000 executions occurred during the Edo period). Toda is suspended by his ankles from a wooden frame. A bamboo saw, dulled so that it tears rather than cuts cleanly, is placed at the crown of his head. Two executioners work the saw in alternating strokes — one pulling, one pushing. The saw descends through the cranium, through the brain, through the cervical vertebrae, through the torso. The process takes approximately forty minutes. Toda remains conscious for the first thirty-two minutes — the saw entering the brain stem at twenty-eight minutes is estimated as the moment of true death. The body is then left suspended for seven days as public display. His journal is burned in a purification fire before the gathered eta community, and the ashes are thrown into the Sumida River.

**Positive Conclusion:**
After Toda's execution, the *machi-bugyo* (town magistrates) across all of Japan's provinces are given new authority to investigate samurai who abuse outcaste communities. While the social hierarchy does not change, the *brazen* abuse of power — torture documented in writing — becomes a capital offense regardless of the victim's caste. No samurai ever attempts this specific crime again. The eta community outside Edo holds a memorial ceremony for the victims, and the Kozukappara execution grounds add Toda's name to the list of those executed there — not as a criminal but as a warning. The Bone Index records: *that even a system designed to dehumanize some must sometimes punish those who take dehumanization too far.*

**Amazon Description (for KDP listing):**

> **BXI-003: The Bamboo's Patience**
>
> *From the archive of history's darkest punishments comes a story that happened once — and was never repeated.*
>
> In 1637 Edo, a samurai named Toda Hidetora kept a journal. Twenty-nine pages. Twenty-nine names. Twenty-nine illustrations of what happens inside the human body when it is kept alive through systematic dissection. He chose his victims from those no one would miss — the outcaste class, people without legal existence. When the shogun learned of the journal, he did not order a clean death. He ordered the saw.
>
> This is nokogiribiki: the Japanese sawing execution. Suspended upside down, a dulled bamboo blade at the crown of the skull, two executioners working in alternating strokes while the condemned watches the ground grow closer.
>
> **WARNING:** This book contains anatomically specific depictions of Japanese feudal sawing execution, including detailed cranial and spinal transection. For mature readers of extreme horror and dark historical fiction only.
>
> This is not history with the horror removed. This is the Bone Index.

**KDP Categories:**
1. Horror > Extreme Horror
2. Literature & Fiction > Historical Fiction > Asian
3. Literature & Fiction > World Literature > Japan

**Keywords (7):**
extreme horror, japanese feudal execution, nokogiribiki, samurai horror, historical body horror, ancient torture fiction, the bone index

**Estimated Conversion Factors:**
- "Samurai horror" is an underserved niche with passionate readers
- Manga/anime crossover audience (anyone familiar with Japanese history will click)
- The method itself is visually striking = shareable
- Proves the series has range beyond Greco-Roman history

---

## Conversion-Optimized Release Calendar

| Week | Action | Expected Impact |
|------|--------|-----------------|
| Pre-launch (W-4) | Enroll Vol 1 in KDP Select, set to pre-order at $2.99 | Algorithms start tracking |
| Launch (W0) | Publish Vol 1. Set to FREE for 5 days via KDP Countdown Deal | Rank boost from free downloads |
| W+2 | Vol 1 returns to $2.99. Publish Vol 1 paperback at $7.99 | Double category placement |
| W+4 | Publish Vol 2 (Kindle + paperback). Cross-link in Vol 1 backmatter | Series momentum builds |
| W+6 | Publish Vol 3 (Kindle + paperback). Cross-link all backmatters | Full series established |
| W+8 | Bundle all 3 as "The Bone Index: Volumes I-III" at $6.99 | Higher-value sale |
| W+12 | Enroll Vol 2 and Vol 3 in KU free promotion weeks, staggered | Sustained category presence |

---

## Amazon Description Template (Use for Every Volume)

```
BXI-[XXX]: [Title]

From the archive of history's darkest punishments comes a story that happened
once — and was never repeated.

In [YEAR] [LOCATION], [CONDEMNED NAME] committed a crime so vile that
[LEADER NAME] did not order a simple death. He ordered [METHOD SUMMARY —
ONE SENTENCE].

This is the true mechanics of [METHOD]. [TWO SENTENCES DESCRIBING THE
MOST SHOCKING ANATOMICAL DETAILS].

WARNING: This book contains anatomically specific depictions of
[METHOD]. For mature readers of extreme horror and dark historical
fiction only.

This is not history with the horror removed. This is the Bone Index.
```

---

## Launch-Day Checklist (Per Volume)

- [ ] Kindle file formatted (8,000-15,000 words, no chapter breaks, continuous narrative)
- [ ] Kindle cover uploaded (full bleed, black + white icon, Trajan font)
- [ ] Description uses template with all 7 keywords embedded
- [ ] Categories set (Horror > Extreme Horror + Historical Fiction)
- [ ] KDP Select enrolled (mandatory for KU)
- [ ] Price set to $2.99 (70% royalty eligible)
- [ ] Backmatter includes links to other 2 volumes
- [ ] "Look Inside" sample starts at Section I (no preface, no table of contents)
- [ ] ISBN assigned (free from KDP for exclusive distribution)
- [ ] Paperback uploaded (same cover, 6x9 trim, cream paper)
- [ ] Pre-order period set (7-30 days for algorithmic benefit)

---

*End of Bone Index System Document. Includes 3 conversion-optimized launch volumes with full Amazon metadata, reasoning for each volume's conversion strategy, and a release calendar.*
