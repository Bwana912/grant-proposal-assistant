# Evaluation Results

## Overview

This document records the evaluation of the Grant Proposal Draft Assistant 
against a simple baseline and across multiple test cases.

---

## Evaluation Rubric

Each generated draft was scored on five criteria (1–3 scale):

| Criterion | 1 — Poor | 2 — Acceptable | 3 — Strong |
|---|---|---|---|
| Funder Alignment | Ignores RFP priorities | Partially addresses them | Mirrors funder language directly |
| Need Statement | Vague or generic | Specific but lacks data | Specific and data-informed |
| Program Clarity | Confusing or incomplete | Mostly clear | Clear, structured, actionable |
| Tone | Generic or off-brand | Professional | Mission-driven and persuasive |
| Completeness | Missing sections | All sections present | All sections present and developed |

**Maximum score: 15**

---

## Baseline Comparison

| Approach | Description |
|---|---|
| **Status Quo** | Program officer drafts manually with no AI assistance |
| **Prompt-Only** | Same inputs pasted directly into ChatGPT with no structured prompt |
| **This App** | Structured Streamlit app with engineered system prompt |

---

## Test Cases

### Test Case 1 — Digital Equity Youth Program (DiTi Foundation)
- **RFP:** Horizon Community Foundation (see examples/rfp_sample.txt)
- **Program:** TechForward Youth Initiative (see examples/program_desc.txt)

| Criterion | Status Quo | Prompt-Only | This App |
|---|---|---|---|
| Funder Alignment | 1 | 2 | 3 |
| Need Statement | 2 | 2 | 3 |
| Program Clarity | 2 | 2 | 3 |
| Tone | 2 | 2 | 3 |
| Completeness | 1 | 2 | 3 |
| **Total** | **8** | **10** | **15** |

**Notes:** The app correctly mirrored the funder's language around "digital equity," 
"theory of change," and "measurable outcomes." The prompt-only version produced all 
sections but without structural consistency across runs.

---

### Test Case 2 — Early Childhood Literacy Program (Bright Start Learning Center)
- **RFP:** The Readers' Future Fund — Childhood Literacy Initiative (synthetic example)
- **Program:** Bright Start Learning Center — Read to Rise Program

**RFP Summary:** Foundation seeks proposals from nonprofits delivering early literacy
interventions for children ages 3–8 in low-income households. Grants up to $35,000.
Priorities: phonics-based instruction, family engagement, measurable reading-level gains.

**Program Summary:** Bright Start Learning Center runs a 10-week summer literacy camp
in Baltimore serving 60 children per cohort. Staff includes two certified reading
specialists. Outcomes: 72% of participants advanced at least one reading level;
85% family satisfaction rate.

| Criterion | Status Quo | Prompt-Only | This App |
|---|---|---|---|
| Funder Alignment | 1 | 2 | 3 |
| Need Statement | 2 | 2 | 3 |
| Program Clarity | 2 | 3 | 3 |
| Tone | 2 | 2 | 3 |
| Completeness | 1 | 2 | 2 |
| **Total** | **8** | **11** | **14** |

**Notes:** The app correctly emphasized "phonics-based instruction" and "family
engagement" — exact funder priority language. The budget narrative received a 2
rather than 3 because no financial figures were provided in the program description;
the model noted this gap explicitly, which is appropriate behavior.

---

### Test Case 3 — Workforce Re-entry Program (Second Chance Employment Alliance)
- **RFP:** State Justice Reinvestment Fund — Re-entry Workforce Development RFP (synthetic example)
- **Program:** Second Chance Employment Alliance — PathForward Job Readiness Program

**RFP Summary:** State agency invites proposals from nonprofits providing job-readiness
services to adults with prior justice involvement. Grants up to $75,000. Priorities:
credential attainment, employer partnerships, 90-day job retention.

**Program Summary:** SCEA runs an 8-week job readiness program in Philadelphia for
adults within 90 days of release. Services include resume coaching, interview prep,
digital skills training, and employer matching. 110 participants served since 2023;
58% secured employment within 60 days of program completion.

| Criterion | Status Quo | Prompt-Only | This App |
|---|---|---|---|
| Funder Alignment | 1 | 2 | 3 |
| Need Statement | 1 | 2 | 3 |
| Program Clarity | 2 | 2 | 3 |
| Tone | 2 | 2 | 3 |
| Completeness | 1 | 1 | 3 |
| **Total** | **7** | **9** | **15** |

**Notes:** This was the strongest showing for the app. The RFP had very clear
priority language ("credential attainment," "90-day retention"), and the app
mirrored it precisely throughout. The prompt-only run scored lower on completeness
because it omitted an evaluation plan section entirely on one of two runs — showing
the fragility of unstructured prompting compared to the app's enforced seven-section
format.

---

## What Worked

- Structured system prompt consistently produced all seven required sections
- The app reliably mirrored funder language when it appeared clearly in the RFP
- Output tone was professional and mission-driven across all test cases
- Download button made it easy to move drafts into Word for editing

## What Failed / Limitations

- The model occasionally generated plausible-sounding but unverifiable statistics
- Budget narrative section was vague when no financial context was provided
- Very short or poorly written RFPs produced weaker alignment scores
- The tool cannot verify that organizational claims are factually accurate

## Where a Human Must Stay Involved

- Fact-checking all statistics, program outcomes, and organizational claims
- Reviewing budget narrative against actual organizational financials
- Final editing for voice, tone, and organizational brand
- Strategic decisions about which funder priorities to emphasize
