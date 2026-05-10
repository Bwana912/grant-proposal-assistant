# MissionBridge AI — Grant Intelligence Platform

> **JHU Generative AI Capstone Final Project**  
> A full-stack AI-powered grant proposal platform for nonprofit organizations.  
> Built with Streamlit + Anthropic Claude Sonnet · Spring 2026

---

## What It Is

MissionBridge AI is a grant writing and management platform designed for nonprofit program officers and executive directors. It transforms the 20–40 hour manual process of writing a grant proposal into a guided, AI-assisted workflow that produces a polished 7-section draft in under 30 seconds.

The app is a demonstration of how Generative AI can lower the barrier to grant funding access for small nonprofits who lack the capacity to hire professional grant writers.

---

## Try the Demo

**No API key required to explore the interface.**

```bash
# 1. Clone and install
git clone https://github.com/Bwana912/grant-proposal-assistant.git
cd grant-proposal-assistant
pip install -r requirements.txt

# 2. Run
streamlit run app.py
```

Open `http://localhost:8501` → click **"🎬 Try the Demo"** — sample data is pre-loaded across all pages. To actually generate proposals, add your Anthropic API key (see Setup below).

---

## Features (15 Modules)

| Module | What It Does |
|---|---|
| 📊 **Dashboard** | Command center — pipeline status, alerts, upcoming deadlines, activity log |
| 🪄 **New Proposal Wizard** | 6-step guided flow: funder → RFP → org → program → settings → generate |
| ✍️ **Proposal Workspace** | Side-by-side editor with per-section AI rewrite, compliance score, export |
| 🔍 **RFP Analyzer** | Paste any RFP → get a plain-English breakdown of requirements in seconds |
| ✅ **Fact Verification** | Flag and track every claim in your proposal before submission |
| 📚 **Citation Library** | Curated data bank — copy statistics directly into your draft |
| 📋 **All Proposals** | Full pipeline view — filter, edit, export, or fact-check any proposal |
| 🎯 **Program Library** | Save your programs once, pull them into any proposal with one click |
| 🏢 **Org Profile** | Organization details + API key — pre-fills every new proposal |
| 🎨 **Brand Kit** | Set colors, fonts, and template style for exported proposals |
| 📤 **Export Center** | Download as `.txt`, `.md`, or `.html` — export-ready formatting |
| 👥 **Team & Sharing** | Manage reviewer access and team permissions |
| ⚙️ **Security & Admin** | Audit log, API status, account settings |
| 📈 **Analytics** | Portfolio metrics — win rate, funding requested vs. awarded |
| 💡 **Writing Tips** | Practical grant-writing guidance with CTA to start writing |

---

## How the AI Works

**Core AI Feature — Proposal Generation:**

1. User pastes a funder's RFP + a description of their nonprofit program
2. App calls Claude Sonnet (`claude-sonnet-4-6`) with a structured system prompt that specifies:
   - Tone (Persuasive / Formal / Urgent / Conversational)
   - Length (Standard / Concise / Comprehensive)
   - Funder type (Foundation / Government / Corporate)
   - Focus area and reading level
   - Which of 7 sections to include
3. Claude produces a full structured draft aligned to the RFP's own language
4. Draft is parsed into sections, displayed in a tabbed editor, and ready for export

**Why GenAI is the right tool:**  
Grant writing is language-intensive, context-dependent, and unique to each funder — exactly the task where LLMs outperform templates or keyword tools. Claude can read a 2,000-word RFP and produce a 1,500-word aligned proposal narrative in 25 seconds.

**RFP Analyzer:**  
Separate feature — paste any RFP and Claude returns a structured 5-section breakdown ("Who Can Apply", "What They Fund", "What to Include", "Key Numbers", "Watch Out For").

---

## Setup

### Prerequisites
- Python 3.10+
- An Anthropic API key ([console.anthropic.com](https://console.anthropic.com))

### Installation

```bash
git clone https://github.com/Bwana912/grant-proposal-assistant.git
cd grant-proposal-assistant
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set your ANTHROPIC_API_KEY
streamlit run app.py
```

### API Key Options
- **`.env` file** (recommended): `ANTHROPIC_API_KEY=sk-ant-...`
- **In-app**: Org Profile page → API Connection field
- **Per-session**: Workspace left panel → ⚙️ API Key expander

---

## Project Structure

```
grant-proposal-assistant/
├── app.py                        # Main Streamlit app (~2,000 lines, 15 pages)
├── prompts/
│   ├── __init__.py
│   └── grant_prompt.py           # System prompt + user prompt builder
├── examples/
│   ├── rfp_sample.txt            # Horizon Community Foundation RFP (synthetic)
│   ├── program_desc.txt          # BrightPath TechForward program description
│   └── sample_output.txt         # Representative 7-section proposal output
├── evaluation/
│   └── results.md                # Test cases, rubric, and scoring results
├── .streamlit/
│   └── config.toml               # Light theme configuration
├── requirements.txt
├── .env.example
└── README.md
```

---

## Evaluation Summary

Three approaches tested against real grant-writing criteria (scored 1–3 per dimension, max 15):

| Approach | Avg Score |
|---|---|
| Status Quo (manual, no AI) | 8 / 15 |
| Prompt-only (pasting to ChatGPT) | 10 / 15 |
| **MissionBridge AI** | **14–15 / 15** |

Criteria: Funder Alignment · Specificity · Program Clarity · Tone · Completeness.  
Full results in `evaluation/results.md`.

**Limitations acknowledged:**
- Occasionally generates plausible but unverifiable statistics → Fact Verification module addresses this
- Budget narrative is vague without financial data from the applicant → flagged in output
- Weak or generic RFPs produce weaker alignment

---

## Design Decisions

| Choice | Rationale |
|---|---|
| Single-file architecture (`app.py`) | Simplicity for academic submission; all state in `st.session_state` |
| Structured 7-section prompt | Consistent output across all funder types and program descriptions |
| Demo mode with seed data | Enables full platform exploration without an API key |
| No RAG / no agents | Single-turn generation is sufficient; avoids retrieval complexity |
| Light-theme custom CSS | Professional SaaS aesthetic; all labels readable on white background |
| Per-section AI rewrite | Targeted regeneration without re-generating the entire proposal |

---

## Tech Stack

- **Frontend:** Streamlit 1.32+
- **AI:** Anthropic Claude Sonnet (`claude-sonnet-4-6`)
- **PDF parsing:** pdfplumber (with pypdf fallback)
- **Config:** python-dotenv
- **Deployment target:** Local / Streamlit Cloud

---

## License

MIT License. Built for JHU Generative AI Capstone · Spring 2026.

*MissionBridge AI · Powered by Anthropic Claude · Always reviewed by a human before submission.*
