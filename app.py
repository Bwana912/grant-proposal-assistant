import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from prompts.grant_prompt import GRANT_SYSTEM_PROMPT, build_user_prompt

# Load environment variables
load_dotenv()

# ── Page Configuration ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grant Proposal Assistant",
    page_icon="📝",
    layout="wide"
)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("📝 Grant Proposal Draft Assistant")
st.markdown(
    "Helping nonprofit program officers produce compelling first-draft grant narratives — "
    "faster, and without a consultant."
)
st.divider()

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Your key is never stored. Provide it here or set ANTHROPIC_API_KEY in your .env file."
    )
    st.markdown("---")
    st.markdown("**About this tool**")
    st.markdown(
        "This app uses Claude to draft structured grant proposal narratives. "
        "It is designed for nonprofit program officers who need a strong first draft quickly."
    )
    st.markdown("---")
    st.markdown("**⚠️ Important**")
    st.markdown(
        "Always review AI-generated content. Verify all facts, figures, and organizational "
        "claims before submission. A human grant writer should review the final draft."
    )

# ── Resolve API Key ───────────────────────────────────────────────────────────
resolved_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")

# ── Input Section ─────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Funder RFP / Guidelines")
    rfp_input = st.text_area(
        label="Paste the funder's RFP, call for proposals, or grant guidelines here.",
        height=350,
        placeholder=(
            "Example:\n"
            "The XYZ Foundation invites proposals from 501(c)(3) organizations working to "
            "improve digital literacy among underserved youth in urban communities. "
            "Grants of up to $50,000 are available. Proposals should demonstrate a clear "
            "theory of change, measurable outcomes, and organizational capacity..."
        )
    )

with col2:
    st.subheader("🏢 Your Program Description")
    program_input = st.text_area(
        label="Describe your nonprofit's program, mission, target population, and activities.",
        height=350,
        placeholder=(
            "Example:\n"
            "Our organization, the DiTi Foundation, provides digital skills training to "
            "youth ages 14–24 in Washington DC. Our 12-week program teaches coding, "
            "AI literacy, and professional technology skills. Since 2022 we have served "
            "over 300 young people, with 78% completing the program and 65% going on to "
            "tech-related employment or further education..."
        )
    )

st.divider()

# ── Generate Button ───────────────────────────────────────────────────────────
generate = st.button("🚀 Generate Grant Proposal Draft", use_container_width=True, type="primary")

# ── Generation Logic ──────────────────────────────────────────────────────────
if generate:
    if not resolved_key:
        st.error("Please provide your Anthropic API key in the sidebar or in your .env file.")
    elif not rfp_input.strip():
        st.warning("Please paste the funder's RFP or guidelines before generating.")
    elif not program_input.strip():
        st.warning("Please describe your program before generating.")
    else:
        with st.spinner("Drafting your grant proposal... this may take 20–30 seconds."):
            try:
                client = anthropic.Anthropic(api_key=resolved_key)

                message = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=2000,
                    system=GRANT_SYSTEM_PROMPT,
                    messages=[
                        {
                            "role": "user",
                            "content": build_user_prompt(rfp_input, program_input)
                        }
                    ]
                )

                draft = message.content[0].text

                st.success("✅ Draft generated successfully!")
                st.divider()
                st.subheader("📋 Your Grant Proposal Draft")
                st.markdown(draft)

                st.divider()
                st.download_button(
                    label="⬇️ Download Draft as .txt",
                    data=draft,
                    file_name="grant_proposal_draft.txt",
                    mime="text/plain",
                    use_container_width=True
                )

            except anthropic.AuthenticationError:
                st.error("Invalid API key. Please check your Anthropic API key and try again.")
            except anthropic.RateLimitError:
                st.error("Rate limit reached. Please wait a moment and try again.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Grant Proposal Assistant · Built for JHU Final Project · "
    "Powered by Anthropic Claude · Always reviewed by a human before submission."
)
