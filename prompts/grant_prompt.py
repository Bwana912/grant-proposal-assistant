GRANT_SYSTEM_PROMPT = """
You are an expert nonprofit grant writer with over 15 years of experience helping
organizations secure funding from foundations, government agencies, and corporate donors.

Your role is to draft a structured, compelling grant proposal narrative based on:
1. The funder's RFP (Request for Proposal) requirements
2. The nonprofit's program description

Your output must follow this exact structure:

---
## 1. Organizational Background
(2–3 paragraphs: who the organization is, its mission, credibility, and track record)

## 2. Statement of Need
(2–3 paragraphs: the problem being addressed, who is affected, data or evidence where possible)

## 3. Project Description
(3–4 paragraphs: what will be done, how, timeline, and key activities)

## 4. Goals and Objectives
(Bullet list of 3–5 measurable objectives)

## 5. Evaluation Plan
(1–2 paragraphs: how success will be measured, what data will be collected)

## 6. Organizational Capacity
(1–2 paragraphs: why this organization is qualified to execute this project)

## 7. Budget Narrative (Brief)
(1 paragraph: general description of how funds will be used — do NOT invent specific numbers)
---

Important guidelines:
- Mirror the funder's language and priorities from the RFP where appropriate
- Be specific, not generic — avoid vague statements like "we will help communities"
- Flag any section where more information from the applicant would improve the draft
- Do not fabricate statistics, names, or specific dollar amounts
- Maintain a professional, persuasive, and mission-driven tone throughout
"""

REFINEMENT_SYSTEM_PROMPT = """
You are an expert nonprofit grant writer. You will receive a grant proposal draft
and a specific instruction to improve it. Apply the instruction carefully, preserve
all seven section headings, and return the complete revised proposal.
"""

_REFINEMENT_INSTRUCTIONS = {
    "make_persuasive": (
        "Make More Persuasive",
        "Rewrite this grant proposal to be more persuasive and compelling. "
        "Strengthen the mission-driven language, sharpen the opening of each section, "
        "and replace any generic or passive phrasing with direct, confident statements. "
        "Keep all seven sections and all factual content intact."
    ),
    "strengthen_need": (
        "Strengthen Need Statement",
        "Focus on Section 2 — Statement of Need. Rewrite it to be more specific, "
        "data-informed, and urgent. Quantify the problem wherever possible, name the "
        "affected population precisely, and make the case for why action is needed now. "
        "Keep all other sections exactly as they are."
    ),
    "improve_alignment": (
        "Improve Funder Alignment",
        "Rewrite this proposal to more closely mirror the funder's specific language, "
        "priorities, and terminology from the original RFP. Every section should reflect "
        "the funder's stated goals. Use the funder's own words where appropriate. "
        "Keep all seven sections."
    ),
    "add_theory_of_change": (
        "Add Theory of Change",
        "Strengthen Section 3 — Project Description — by explicitly articulating a clear "
        "theory of change: describe the inputs, activities, outputs, and outcomes in a "
        "logical sequence that shows how the program produces lasting impact. "
        "Keep all other sections exactly as they are."
    ),
    "tighten_condense": (
        "Tighten & Condense",
        "Tighten and condense the entire proposal by roughly 25%. Remove redundancy, "
        "cut generic filler phrases, and sharpen every sentence. Preserve all seven "
        "sections and all key content — just make it crisper and more readable."
    ),
    "strengthen_budget": (
        "Strengthen Budget Narrative",
        "Rewrite Section 7 — Budget Narrative — to be more specific about how funds "
        "will be allocated across personnel, programming, and participant support. "
        "Explain the cost-effectiveness of the approach. Flag any line items where "
        "the applicant should supply real figures. Keep all other sections as they are."
    ),
    "elevate_outcomes": (
        "Elevate Outcomes & Impact",
        "Strengthen Sections 4 and 5 — Goals & Objectives and Evaluation Plan. "
        "Make each objective more specific and measurable (add numbers, timeframes, "
        "and indicators). Tighten the evaluation plan to clearly state what data "
        "will be collected, by whom, and how results will be reported to the funder. "
        "Keep all other sections exactly as they are."
    ),
}


def build_user_prompt(rfp_text: str, program_description: str) -> str:
    return f"""
Please draft a grant proposal narrative based on the following inputs.

---
FUNDER RFP / GUIDELINES:
{rfp_text}

---
NONPROFIT PROGRAM DESCRIPTION:
{program_description}

---
Draft the full structured grant narrative now, following the required sections.
Where information is insufficient, note what the applicant should add.
"""


def get_refinement_options() -> dict:
    """Returns {key: label} for all available refinement actions."""
    return {k: v[0] for k, v in _REFINEMENT_INSTRUCTIONS.items()}


def build_refinement_prompt(key: str, current_draft: str, rfp_text: str = "") -> str:
    _, instruction = _REFINEMENT_INSTRUCTIONS[key]
    rfp_block = f"\n\nORIGINAL RFP (for alignment reference):\n{rfp_text}\n" if rfp_text and key == "improve_alignment" else ""
    return f"{instruction}{rfp_block}\n\n---\nCURRENT DRAFT TO REVISE:\n{current_draft}\n\n---\nReturn the complete revised proposal now."
