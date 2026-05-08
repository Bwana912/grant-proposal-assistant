import streamlit as st
import anthropic
import os
from dotenv import load_dotenv
from prompts.grant_prompt import (
    GRANT_SYSTEM_PROMPT,
    REFINEMENT_SYSTEM_PROMPT,
    build_user_prompt,
    build_refinement_prompt,
    get_refinement_options,
)

load_dotenv()

st.set_page_config(
    page_title="Grant Proposal Assistant",
    page_icon="📝",
    layout="wide"
)

# ── Session state defaults ────────────────────────────────────────────────────
for key, default in {
    "draft": None,
    "rfp_input": "",
    "program_input": "",
    "refinement_log": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        help="Your key is never stored. Provide it here or set ANTHROPIC_API_KEY in your .env file.",
    )

    st.markdown("---")

    if st.session_state.draft:
        st.markdown("### ✏️ Refine Your Draft")
        st.caption("Click any button to instantly improve a specific aspect of the proposal.")

        ICONS = {
            "make_persuasive":      "✨",
            "strengthen_need":      "📊",
            "improve_alignment":    "🎯",
            "add_theory_of_change": "🔄",
            "tighten_condense":     "✂️",
            "strengthen_budget":    "💰",
            "elevate_outcomes":     "📈",
        }

        for key, label in get_refinement_options().items():
            icon = ICONS.get(key, "•")
            if st.button(f"{icon} {label}", key=f"btn_{key}", use_container_width=True):
                st.session_state["pending_refinement"] = key

        st.markdown("---")

        if st.session_state.refinement_log:
            st.markdown("**Refinements applied:**")
            for entry in st.session_state.refinement_log:
                st.caption(f"• {entry}")

        st.markdown("---")
        if st.button("🔁 Start Over", use_container_width=True):
            st.session_state.draft = None
            st.session_state.rfp_input = ""
            st.session_state.program_input = ""
            st.session_state.refinement_log = []
            st.rerun()
    else:
        st.markdown("**About this tool**")
        st.markdown(
            "This app uses Claude to draft structured grant proposal narratives "
            "for nonprofit program officers."
        )
        st.markdown("---")
        st.markdown("**⚠️ Important**")
        st.markdown(
            "Always review AI-generated content. Verify all facts, figures, and "
            "organizational claims before submission."
        )

# ── Resolve API key ───────────────────────────────────────────────────────────
resolved_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("📝 Grant Proposal Draft Assistant")
st.markdown(
    "Helping nonprofit program officers produce compelling first-draft grant narratives — "
    "faster, and without a consultant."
)
st.divider()

# ── Apply pending refinement ──────────────────────────────────────────────────
if st.session_state.draft and st.session_state.get("pending_refinement"):
    refinement_key = st.session_state.pop("pending_refinement")
    label = get_refinement_options()[refinement_key]

    with st.spinner(f"Applying: {label}…"):
        try:
            client = anthropic.Anthropic(api_key=resolved_key)
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=REFINEMENT_SYSTEM_PROMPT,
                messages=[
                    {
                        "role": "user",
                        "content": build_refinement_prompt(
                            refinement_key,
                            st.session_state.draft,
                            st.session_state.rfp_input,
                        ),
                    }
                ],
            )
            st.session_state.draft = message.content[0].text
            st.session_state.refinement_log.append(label)
            st.success(f"✅ Applied: {label}")
        except anthropic.AuthenticationError:
            st.error("Invalid API key. Please check your Anthropic API key.")
        except anthropic.RateLimitError:
            st.error("Rate limit reached. Please wait a moment and try again.")
        except Exception as e:
            st.error(f"Refinement failed: {str(e)}")

# ── Input view ────────────────────────────────────────────────────────────────
if not st.session_state.draft:
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
                "theory of change, measurable outcomes, and organizational capacity…"
            ),
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
                "over 300 young people, with 78% completing the program…"
            ),
        )

    st.divider()
    if st.button("🚀 Generate Grant Proposal Draft", use_container_width=True, type="primary"):
        if not resolved_key:
            st.error("Please provide your Anthropic API key in the sidebar or in your .env file.")
        elif not rfp_input.strip():
            st.warning("Please paste the funder's RFP or guidelines before generating.")
        elif not program_input.strip():
            st.warning("Please describe your program before generating.")
        else:
            with st.spinner("Drafting your grant proposal… this may take 20–30 seconds."):
                try:
                    client = anthropic.Anthropic(api_key=resolved_key)
                    message = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=4096,
                        system=GRANT_SYSTEM_PROMPT,
                        messages=[
                            {
                                "role": "user",
                                "content": build_user_prompt(rfp_input, program_input),
                            }
                        ],
                    )
                    st.session_state.draft = message.content[0].text
                    st.session_state.rfp_input = rfp_input
                    st.session_state.program_input = program_input
                    st.session_state.refinement_log = []
                    st.rerun()
                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Please check your Anthropic API key and try again.")
                except anthropic.RateLimitError:
                    st.error("Rate limit reached. Please wait a moment and try again.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {str(e)}")

# ── Draft view ────────────────────────────────────────────────────────────────
else:
    st.info("✅ Draft ready — use the **sidebar buttons** to refine any aspect of the proposal, then download.")

    st.subheader("📋 Your Grant Proposal Draft")
    st.markdown(st.session_state.draft)

    st.divider()
    st.download_button(
        label="⬇️ Download Draft as .txt",
        data=st.session_state.draft,
        file_name="grant_proposal_draft.txt",
        mime="text/plain",
        use_container_width=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "Grant Proposal Assistant · Built for JHU Final Project · "
    "Powered by Anthropic Claude · Always reviewed by a human before submission."
)
