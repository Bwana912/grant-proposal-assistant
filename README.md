# Grant Proposal Draft Assistant

> A GenAI-powered tool that helps nonprofit program officers produce structured, 
> compelling grant proposal narratives — faster, and without a consultant.

---

## 1. Context, User, and Problem

**Who is the user?**  
Nonprofit program officers and executive directors at small-to-mid-size NGOs. 
These are professionals who are deeply expert in *delivering* programs — but not 
necessarily in *writing about* them for funders.

**What workflow are we improving?**  
Drafting a grant proposal narrative in response to a funder's RFP (Request for Proposals). 
A full grant narrative typically takes 20–40 hours to produce manually and often 
requires hiring an external grant writer at $50–150/hour.

**Why does this problem matter?**  
Small nonprofits are disproportionately disadvantaged in the grant funding landscape. 
They do strong work but lack the writing capacity to compete with larger organizations 
that employ full-time development staff. A tool that lowers the barrier to producing 
a credible first draft directly advances funding equity.

---

## 2. Solution and Design

**What was built:**  
A Streamlit web application where a user provides:
1. The funder's RFP or grant guidelines (pasted as text)
2. A description of their nonprofit program

The app then generates a structured, seven-section grant proposal narrative using 
the Anthropic Claude API.

**Output sections:**
1. Organizational Background
2. Statement of Need
3. Project Description
4. Goals and Objectives
5. Evaluation Plan
6. Organizational Capacity
7. Budget Narrative (Brief)

**Why GenAI is the right tool for this task:**

Grant writing is language-intensive, context-dependent, and highly variable across
funders — exactly the kind of task where large language models outperform simpler
automation. A template or mail-merge approach cannot read an RFP and mirror its
specific priorities; keyword search cannot synthesize a coherent narrative; a
spreadsheet workflow cannot produce persuasive prose. Claude can do all three: it
reads the funder's language, aligns it to the applicant's program, and produces a
structured, professional draft in under 30 seconds. The business value is concrete —
20–40 hours of professional writing time reduced to a reviewable first draft that
a program officer can refine in an afternoon.

**Key design choices:**

| Choice | Rationale |
|---|---|
| Structured system prompt | Ensures consistent section-by-section output across all inputs |
| Mirrors funder language | Prompt instructs the model to use the RFP's own terminology |
| Flags missing information | Model notes where more applicant input would strengthen the draft |
| No RAG or agents | Single-turn generation is sufficient for this workflow |
| Download button | Outputs a .txt file the user can immediately open in Word |

---

## 3. Evaluation and Results

**Baseline comparisons:**
- **Status Quo:** Manual drafting by the program officer, no AI assistance
- **Prompt-Only:** Same inputs pasted directly into ChatGPT with no structured prompt

**Rubric (each criterion scored 1–3):**
- Funder Alignment
- Specificity of Need Statement
- Program Clarity
- Professional Tone
- Completeness of Sections

**Summary of findings:**

| Approach | Avg. Score (out of 15) |
|---|---|
| Status Quo | 8 |
| Prompt-Only | 10 |
| This App | 14–15 |

Full test case results are documented in `evaluation/results.md`.

**What worked:**
- Consistently produced all seven sections with relevant content
- Reliably mirrored funder language when clearly stated in the RFP
- Professional, mission-driven tone across all test cases

**What failed / limitations:**
- Occasionally generates plausible-sounding but unverifiable statistics
- Budget narrative is vague without financial context from the applicant
- Weak or poorly written RFPs produce weaker alignment

**Where a human must stay involved:**
- Fact-checking all statistics and organizational claims
- Final editing for organizational voice and brand
- Strategic decisions about funder priority emphasis

---

## 4. Artifact Snapshot

**App Interface:**  
Two-column input layout — funder RFP on the left, program description on the right —
with a single "Generate Grant Proposal Draft" button. Output renders as structured
markdown in the app and can be downloaded as a `.txt` file.

**Sample inputs** are provided in the `examples/` folder:
- `examples/rfp_sample.txt` — A realistic digital equity grant RFP
- `examples/program_desc.txt` — A sample nonprofit program description

**Sample output** — a full seven-section grant proposal draft generated from the
above inputs — is available at:
- `examples/sample_output.txt`

This output was produced by the app using the sample files and represents the
quality and structure of a typical generation. Note the final section includes
an explicit flag from the model noting where the applicant should supply financial
figures — an example of the app's "flag missing information" behavior.

---

## Setup and Usage

### Prerequisites
- Python 3.10 or higher
- An Anthropic API key ([get one here](https://console.anthropic.com))

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Bwana912/grant-proposal-assistant.git
cd grant-proposal-assistant

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up your API key
cp .env.example .env
# Open .env and replace your_api_key_here with your actual Anthropic API key
```

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

### Using the App

1. Paste a funder's RFP or grant guidelines into the left input box
2. Paste your nonprofit's program description into the right input box
3. Click **Generate Grant Proposal Draft**
4. Review the structured output and download as a .txt file

> **Note:** You can also enter your API key directly in the sidebar instead of using a .env file.

### Running with the Sample Files

Copy the contents of `examples/rfp_sample.txt` into the RFP box and 
`examples/program_desc.txt` into the program description box to test the app 
on a pre-built example.

---

## Project Structure

```
grant-proposal-assistant/
├── app.py                        # Main Streamlit application
├── prompts/
│   ├── __init__.py
│   └── grant_prompt.py           # System prompt and user prompt builder
├── examples/
│   ├── rfp_sample.txt            # Sample funder RFP for testing
│   ├── program_desc.txt          # Sample program description for testing
│   └── sample_output.txt         # Representative app output for Test Case 1
├── evaluation/
│   └── results.md                # Test cases, rubric, and evaluation results
├── requirements.txt
├── .env.example                  # API key template (never commit .env)
└── README.md
```

---

## License

MIT License. Built for JHU Final Project.
