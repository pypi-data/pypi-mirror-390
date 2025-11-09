# Style Tune-up — Executable Loop Playbook

**Category:** Refinement **Abbreviation:** ST **Schema:**
<https://questfoundry.liesdonk.nl/schemas/style_addendum.schema.json>

## Purpose

Detect and correct style drift across prose, captions, and PN surfaces without re-architecting the
story. Tighten voice, register, motifs, and visual guardrails so the book reads like one mind made
it. Outcome: A consolidated style addendum with specific edit notes to owners, plus a green
Presentation/Style pre-gate—ready for merge after downstream fixes.

## Activation Criteria (Showrunner)

- Readers/PN report tonal wobble or inconsistent diction
- New chapter/act introduces a variant tone that needs harmonizing
- Art/Audio plans landed and nudge aesthetics
- Localization uncovered phrasing that fights register

Showrunner opens/attaches a Trace Unit (TU): `tu-style-tune-<scope>`.

## RACI Matrix

| Role            | Assignment | Responsibilities                                                 |
| --------------- | ---------- | ---------------------------------------------------------------- |
| Style Lead      | R          | Diagnose drift; author style addendum; write targeted edit notes |
| Showrunner      | A          | Scope pass; sequence fixes                                       |
| Scene Smith     | C          | Receive edits; propose rewrites that preserve intent             |
| Plotwright      | C          | Confirm revisions don't alter topology/gateways                  |
| Art Director    | C          | If active: align captions/cue language with register             |
| Audio Director  | C          | If active: align audio cue descriptions with register            |
| Translator      | C          | If active: flag untranslatable idioms; suggest equivalents       |
| Gatekeeper      | C          | Pre-check Style and Presentation Safety                          |
| Player-Narrator | I          | Receives updated PN phrasing patterns if relevant                |

## Inputs

- Current Cold style guide (plus motifs and exemplars)
- Recent prose drafts (Hot), captions, PN lines
- Canon changes that might affect tone (grim vs caper)
- PN and Binder UX notes; localization notes (if any)

## Procedure (Message Sequences)

### Step 1: Drift Diagnosis (Style Lead)

Sample sections (early/middle/late), PN lines, and recent captions. Tag issues: `voice-shift`,
`register-mismatch`, `motif-missing`, `over-exposition`, `jargon-spike`.

### Step 2: Exemplar Pass

Provide short before/after exemplars for each issue (human prose). Reaffirm motif kit (e.g.,
"shadow-side neon", "low-G dust", "relay hum").

**Example:**

- **Before:** "In low gravity, you are floating, which is disorienting, and the alarms are very
  loud."
- **After:** "Low-G lifts you an inch; the floor forgets you. Alarms chew the corridor."
- **Motifs:** `low-G`, `industrial noise`. Rhythm: shorter under pressure.

### Step 3: Style Addendum

Add rules or clarifications: sentence rhythm under pressure, idiom boundaries, POV distance, caption
tone. Localization notes: avoid puns / provide alternatives.

### Step 4: Edit Notes to Owners

Annotated list: `file/section → issue → fix suggestion (1-2 lines)`. PN phrase bank updates if
needed (diegetic checks phrasing).

### Step 5: Owner Revisions (Scene/PN/Art/Audio)

Make minimal changes to hit style; escalate if structure might change.

### Step 6: Pre-Gate (Gatekeeper)

Style and Presentation Safety check; ensure no spoilers snuck into captions/PN.

### Step 7: Package

Bundle style addendum + edit notes + pre-gate note into the TU.

## Deliverables

- **Style Addendum** (human text): rules, motif kit, exemplar snippets
- **Edit Notes:** targeted fix list by section/caption/PN line
- **Phrase Bank** (optional): PN diegetic gate phrasing patterns
- **Pre-gate note:** Style/Presentation status and any residual risks

## Success Criteria

- Prose and PN read in a consistent register; motifs reappear intentionally
- Captions and cue sheets align with voice; no technique-talk on surfaces
- Localization pitfalls are noted with alternatives
- Gatekeeper reports Style/Presentation green

## Failure Modes & Remedies

- **Overcorrection flattens character voice** → Keep character idiolect; harmonize narration only
- **Style change implies story change** → Route to Story Spark; don't smuggle structure via style
- **Caption spoilers** → Move detail to canon notes; rewrite caption atmospheric
- **Untranslatable idioms** → Provide neutral phrasing or region-appropriate equivalents

## Quality Bars Pressed

**Primary:** Style, Presentation (readability), Accessibility (readability)

**Secondary:** Integrity (voice consistency across sections)

## Handoffs

- **To Scene Smith:** Targeted edits for prose sections that need register adjustment
- **To Art/Audio Directors:** Caption/cue description rewrites for voice consistency
- **To Translator:** Idiom alternatives and localization-safe phrasing patterns
- **To Gatecheck:** After owners apply edits, full gatecheck before merge to Cold
