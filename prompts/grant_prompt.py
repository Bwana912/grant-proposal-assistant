SECTION_DEFS = [
    (1, "Organizational Background"),
    (2, "Statement of Need"),
    (3, "Project Description"),
    (4, "Goals and Objectives"),
    (5, "Evaluation Plan"),
    (6, "Organizational Capacity"),
    (7, "Budget Narrative"),
]

_TONE = {
    "Formal":          "Write in a formal, precise, institutional tone. Avoid contractions. Use professional vocabulary throughout.",
    "Persuasive":      "Write in a compelling, persuasive tone. Make a strong case for funding. Use vivid, mission-driven language.",
    "Urgent":          "Write in an urgent, action-oriented tone. Convey the critical nature of the need and the time-sensitivity of this opportunity.",
    "Conversational":  "Write in a warm, accessible, conversational tone. Avoid jargon. Connect emotionally with the reader.",
}

_LENGTH = {
    "Concise":         "Keep each section brief — 1–2 short paragraphs maximum per narrative section. Prioritize clarity over comprehensiveness.",
    "Standard":        "Write standard-length sections — 2–3 paragraphs per narrative section. Balance depth with readability.",
    "Comprehensive":   "Write detailed, thorough sections — 3–4 paragraphs per narrative section. Include context, evidence, and nuance.",
}

_FUNDER = {
    "Private Foundation": "This is a private foundation grant. Emphasize mission alignment, community impact, and organizational credibility.",
    "Government":         "This is a government grant. Emphasize compliance, measurable outcomes, accountability structures, and public policy alignment.",
    "Corporate":          "This is a corporate funder proposal. Emphasize partnership value, visibility, and business-relevant impact metrics.",
    "Community Fund":     "This is a community fund proposal. Emphasize local roots, community voice, and neighborhood-level impact.",
}

_FOCUS = {
    "Digital Equity":    "digital equity, technology access, and digital inclusion",
    "Youth Development": "youth development and positive youth outcomes",
    "Education":         "education, learning outcomes, and academic achievement",
    "Health":            "health equity and community wellness",
    "Workforce":         "workforce development and economic mobility",
    "Other":             "the domain described in the program description",
}


def build_dynamic_system_prompt(
    tone: str,
    length: str,
    funder_type: str,
    focus_area: str,
    selected_sections: list,
) -> str:
    section_block = "\n".join(
        f"## {n}. {name}"
        for n, name in SECTION_DEFS
        if n in selected_sections
    )
    return f"""You are an expert nonprofit grant writer with 15+ years of experience.

TONE: {_TONE[tone]}

LENGTH: {_LENGTH[length]}

FUNDER TYPE: {_FUNDER[funder_type]}

FOCUS AREA: This proposal concerns {_FOCUS[focus_area]}.

Generate ONLY the following sections, in this exact order, using these exact headings:
{section_block}

GUIDELINES:
- Mirror the funder's language and priorities from the RFP
- Be specific — avoid vague statements like "we will help communities"
- Do not fabricate statistics, names, or specific dollar amounts
- Flag where more applicant detail would strengthen the draft
- Apply the specified tone consistently throughout all sections
"""


def build_user_prompt(rfp_text: str, program_description: str) -> str:
    return f"""Draft a grant proposal narrative based on the following inputs.

---
FUNDER RFP / GUIDELINES:
{rfp_text}

---
NONPROFIT PROGRAM DESCRIPTION:
{program_description}

---
Draft the full structured grant narrative now, following the required sections exactly.
Where information is insufficient, note what the applicant should add.
"""


def build_section_regen_prompt(
    section_num: int,
    section_name: str,
    current_content: str,
    rfp: str,
    program: str,
    tone: str,
    length: str,
    funder_type: str,
    focus_area: str,
) -> str:
    return f"""You are an expert grant writer. Rewrite ONLY Section {section_num}: {section_name}.

Settings for this rewrite:
- Tone: {tone} — {_TONE[tone]}
- Length: {length} — {_LENGTH[length]}
- Funder type: {_FUNDER[funder_type]}
- Focus area: {_FOCUS[focus_area]}

ORIGINAL RFP:
{rfp}

PROGRAM DESCRIPTION:
{program}

CURRENT SECTION (rewrite this):
{current_content}

Return ONLY the rewritten section. Start with the exact heading:
## {section_num}. {section_name}

Do not include other sections, commentary, or preamble.
"""
