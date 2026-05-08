import re
import os
import streamlit as st
import streamlit.components.v1 as components
import anthropic
from dotenv import load_dotenv
from prompts.grant_prompt import (
    SECTION_DEFS,
    build_dynamic_system_prompt,
    build_user_prompt,
    build_section_regen_prompt,
)

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Grant Proposal Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
.stApp { background-color: #0F1117; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1E2130;
    border-right: 1px solid #2E3347;
}
[data-testid="stSidebar"] section { padding-top: 1rem; }

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2DD4BF, #22b5a3) !important;
    color: #0F1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(45,212,191,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 20px rgba(45,212,191,0.45) !important;
    transform: translateY(-2px) !important;
}

/* Secondary buttons */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #2DD4BF !important;
    border: 1px solid #2DD4BF !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    background: rgba(45,212,191,0.12) !important;
    transform: translateY(-1px) !important;
}

/* Tertiary / small buttons in sidebar */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #2DD4BF !important;
    border: 1px solid #2E3347 !important;
    border-radius: 6px !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: #2DD4BF !important;
    background: rgba(45,212,191,0.08) !important;
}

/* Text areas */
[data-testid="stTextArea"] textarea {
    background: #1E2130 !important;
    border: 1px solid #2E3347 !important;
    border-radius: 10px !important;
    color: #F0F2F6 !important;
    font-size: 0.88rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.15) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #4B5563 !important; }

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1E2130 !important;
    border-color: #2E3347 !important;
    border-radius: 8px !important;
    color: #F0F2F6 !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label span { color: #F0F2F6 !important; font-size: 0.85rem !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1E2130;
    border-radius: 10px 10px 0 0;
    padding: 6px 8px 0;
    gap: 4px;
    border-bottom: 2px solid #2E3347;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #9BA3AF;
    border-radius: 8px 8px 0 0;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 8px 14px;
    border: none;
    letter-spacing: 0.03em;
    transition: color 0.15s;
}
.stTabs [data-baseweb="tab"]:hover { color: #F0F2F6; }
.stTabs [aria-selected="true"] {
    background: #2DD4BF !important;
    color: #0F1117 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: #1E2130;
    border: 1px solid #2E3347;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 28px 24px 20px;
}

/* Expander */
[data-testid="stExpander"] details {
    background: #161926 !important;
    border: 1px solid #2E3347 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: #9BA3AF !important; font-size: 0.82rem !important; }

/* Dividers */
hr { border-color: #2E3347 !important; opacity: 1 !important; }

/* Caption / small text */
.stCaption p, small, .element-container small { color: #9BA3AF !important; }

/* Alerts / banners */
[data-testid="stAlert"] {
    background: #1E2130 !important;
    border: 1px solid #2E3347 !important;
    border-radius: 10px !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #2DD4BF !important;
    border: 1px solid #2DD4BF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(45,212,191,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
_DEFAULTS: dict = {
    "sections":      {},     # {num: {"name": str, "content": str}}
    "full_draft":    "",
    "rfp_saved":     "",     # saved at generation time for section regen
    "prog_saved":    "",
    "pending_regen": None,
    "regen_log":     [],
    "settings_snap": {},     # tone/length/etc saved at generation time
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

# initialize text area keys so Load Sample can set them before the widget renders
if "rfp_area" not in st.session_state:
    st.session_state.rfp_area = ""
if "prog_area" not in st.session_state:
    st.session_state.prog_area = ""

# ── Helpers ───────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def parse_sections(draft: str) -> dict:
    result = {}
    for num, name in SECTION_DEFS:
        pat = re.compile(
            rf"##\s*{num}\.\s*{re.escape(name)}(.*?)(?=\n##\s*\d+\.|\Z)",
            re.DOTALL | re.IGNORECASE,
        )
        m = pat.search(draft)
        if m:
            body = m.group(1).strip()
            result[num] = {
                "name": name,
                "content": f"## {num}. {name}\n\n{body}",
            }
    return result

def rebuild_draft(sections: dict) -> str:
    return "\n\n---\n\n".join(sections[n]["content"] for n in sorted(sections))

def _copy_btn(text: str, uid: str) -> str:
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return f"""
    <button id="cb_{uid}"
        style="background:#2DD4BF;color:#0F1117;border:none;padding:7px 18px;
               border-radius:6px;cursor:pointer;font-weight:700;font-size:12.5px;
               font-family:system-ui,-apple-system,sans-serif;
               letter-spacing:0.03em;transition:all 0.2s;"
        onmouseover="this.style.background='#22b5a3';this.style.boxShadow='0 4px 12px rgba(45,212,191,0.4)'"
        onmouseout="this.style.background='#2DD4BF';this.style.boxShadow='none'"
        onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{
            var b=document.getElementById('cb_{uid}');
            b.textContent='✓ Copied!';
            b.style.background='#059669';
            b.style.color='#fff';
            setTimeout(()=>{{
                b.textContent='📋 Copy';
                b.style.background='#2DD4BF';
                b.style.color='#0F1117';
            }},2200);
        }}).catch(()=>alert('Select the text and copy manually.'));">
        📋 Copy
    </button>"""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='color:#F0F2F6;font-size:1.15rem;margin-bottom:4px;'>"
        "🎨 Customize Your Draft</h2>"
        "<p style='color:#9BA3AF;font-size:0.78rem;margin-top:0;'>Set these before generating.</p>",
        unsafe_allow_html=True,
    )

    tone = st.selectbox(
        "📣 Tone",
        ["Persuasive", "Formal", "Urgent", "Conversational"],
        help="Controls the writing style throughout the entire proposal.",
    )
    length = st.selectbox(
        "📏 Length",
        ["Standard", "Concise", "Comprehensive"],
        help="Concise = 1–2 paragraphs/section · Standard = 2–3 · Comprehensive = 3–4",
    )
    funder_type = st.selectbox(
        "🏦 Funder Type",
        ["Private Foundation", "Government", "Corporate", "Community Fund"],
        help="Adjusts framing and emphasis to match funder expectations.",
    )
    focus_area = st.selectbox(
        "🎯 Focus Area",
        ["Digital Equity", "Youth Development", "Education", "Health", "Workforce", "Other"],
        help="Tells the model which domain vocabulary to emphasize.",
    )

    st.divider()
    st.markdown(
        "<p style='color:#F0F2F6;font-size:0.82rem;font-weight:700;margin-bottom:6px;'>"
        "📋 Sections to Include</p>",
        unsafe_allow_html=True,
    )
    selected_sections = [
        num for num, name in SECTION_DEFS
        if st.checkbox(name, value=True, key=f"sec_{num}")
    ]
    if not selected_sections:
        st.warning("Select at least one section.")

    st.divider()
    with st.expander("⚙️ Settings", expanded=False):
        api_key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-…",
            help="Never stored. Or set ANTHROPIC_API_KEY in your .env file.",
        )
        st.markdown(
            "<small style='color:#9BA3AF;'>Get a key at "
            "<a href='https://console.anthropic.com' style='color:#2DD4BF;'>console.anthropic.com</a></small>",
            unsafe_allow_html=True,
        )

    if st.session_state.sections:
        st.divider()
        if st.button("🔁 Start Over", use_container_width=True):
            for _k, _v in _DEFAULTS.items():
                st.session_state[_k] = _v
            st.session_state.rfp_area = ""
            st.session_state.prog_area = ""
            st.rerun()

# ── Resolved API key (available to all code below) ────────────────────────────
resolved_key = api_key_input or os.getenv("ANTHROPIC_API_KEY", "")

# ── Main header ───────────────────────────────────────────────────────────────
st.markdown(
    "<div style='margin-bottom:4px'>"
    "<span style='font-size:2.1rem;font-weight:800;color:#F0F2F6;'>📝 Grant Proposal Assistant</span>"
    "</div>"
    "<p style='color:#9BA3AF;font-size:0.97rem;margin-top:2px;margin-bottom:0;'>"
    "AI-powered first drafts for nonprofit grant proposals — structured, aligned, and ready to edit."
    "</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Handle pending section regeneration ──────────────────────────────────────
if st.session_state.pending_regen is not None and st.session_state.sections:
    sec_num  = st.session_state.pending_regen
    st.session_state.pending_regen = None
    sec_name = dict(SECTION_DEFS).get(sec_num, f"Section {sec_num}")
    snap     = st.session_state.settings_snap

    with st.spinner(f"Rewriting: {sec_name}…"):
        if not resolved_key:
            st.error("No API key found. Add it in Settings.")
        else:
            try:
                client = anthropic.Anthropic(api_key=resolved_key)
                msg = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1500,
                    messages=[{
                        "role": "user",
                        "content": build_section_regen_prompt(
                            sec_num, sec_name,
                            st.session_state.sections[sec_num]["content"],
                            st.session_state.rfp_saved,
                            st.session_state.prog_saved,
                            snap.get("tone", tone),
                            snap.get("length", length),
                            snap.get("funder_type", funder_type),
                            snap.get("focus_area", focus_area),
                        ),
                    }],
                )
                st.session_state.sections[sec_num]["content"] = msg.content[0].text.strip()
                st.session_state.full_draft = rebuild_draft(st.session_state.sections)
                st.session_state.regen_log.append(sec_name)
                st.success(f"✅ {sec_name} rewritten.")
            except anthropic.AuthenticationError:
                st.error("Invalid API key.")
            except Exception as exc:
                st.error(f"Regeneration failed: {exc}")

# ── INPUT VIEW ────────────────────────────────────────────────────────────────
if not st.session_state.sections:

    col1, col2 = st.columns(2, gap="large")

    with col1:
        hdr_c, btn_c = st.columns([4, 1])
        with hdr_c:
            st.markdown(
                "<p style='font-size:1.05rem;font-weight:700;color:#F0F2F6;margin-bottom:6px;'>"
                "📄 Funder RFP / Guidelines</p>",
                unsafe_allow_html=True,
            )
        with btn_c:
            if st.button("Load eg.", key="load_rfp", help="Load the built-in sample RFP"):
                st.session_state.rfp_area = _read(
                    os.path.join(BASE, "examples", "rfp_sample.txt")
                )

        rfp_input = st.text_area(
            "rfp",
            key="rfp_area",
            height=340,
            placeholder="Paste the funder's full RFP, call for proposals, or grant guidelines here…",
            label_visibility="collapsed",
        )
        char1 = len(rfp_input)
        colour1 = "#2DD4BF" if char1 > 100 else "#4B5563"
        st.markdown(
            f"<small style='color:{colour1};'>✏️ {char1:,} characters"
            + (" · ready" if char1 > 100 else " · paste your RFP above")
            + "</small>",
            unsafe_allow_html=True,
        )

    with col2:
        hdr_c2, btn_c2 = st.columns([4, 1])
        with hdr_c2:
            st.markdown(
                "<p style='font-size:1.05rem;font-weight:700;color:#F0F2F6;margin-bottom:6px;'>"
                "🏢 Program Description</p>",
                unsafe_allow_html=True,
            )
        with btn_c2:
            if st.button("Load eg.", key="load_prog", help="Load the built-in sample program description"):
                st.session_state.prog_area = _read(
                    os.path.join(BASE, "examples", "program_desc.txt")
                )

        prog_input = st.text_area(
            "prog",
            key="prog_area",
            height=340,
            placeholder="Describe your nonprofit's mission, program, target population, activities, and outcomes…",
            label_visibility="collapsed",
        )
        char2 = len(prog_input)
        colour2 = "#2DD4BF" if char2 > 100 else "#4B5563"
        st.markdown(
            f"<small style='color:{colour2};'>✏️ {char2:,} characters"
            + (" · ready" if char2 > 100 else " · describe your program above")
            + "</small>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Settings summary bar
    st.markdown(
        f"<div style='background:#1E2130;border:1px solid #2E3347;border-radius:8px;"
        f"padding:10px 18px;margin-bottom:14px;display:flex;gap:24px;flex-wrap:wrap;'>"
        f"<span style='color:#9BA3AF;font-size:0.8rem;'>Tone: <b style='color:#2DD4BF;'>{tone}</b></span>"
        f"<span style='color:#9BA3AF;font-size:0.8rem;'>Length: <b style='color:#2DD4BF;'>{length}</b></span>"
        f"<span style='color:#9BA3AF;font-size:0.8rem;'>Funder: <b style='color:#2DD4BF;'>{funder_type}</b></span>"
        f"<span style='color:#9BA3AF;font-size:0.8rem;'>Focus: <b style='color:#2DD4BF;'>{focus_area}</b></span>"
        f"<span style='color:#9BA3AF;font-size:0.8rem;'>Sections: <b style='color:#2DD4BF;'>{len(selected_sections)}/7</b></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "🚀 Generate Grant Proposal Draft",
        use_container_width=True,
        type="primary",
        disabled=not selected_sections,
    ):
        if not resolved_key:
            st.error("Add your Anthropic API key in the ⚙️ Settings panel (bottom of sidebar).")
        elif not rfp_input.strip():
            st.warning("Paste the funder's RFP before generating.")
        elif not prog_input.strip():
            st.warning("Describe your program before generating.")
        else:
            with st.spinner("✍️ Drafting your grant proposal… 20–30 seconds."):
                try:
                    client = anthropic.Anthropic(api_key=resolved_key)
                    msg = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=4096,
                        system=build_dynamic_system_prompt(
                            tone, length, funder_type, focus_area, selected_sections
                        ),
                        messages=[{
                            "role": "user",
                            "content": build_user_prompt(rfp_input, prog_input),
                        }],
                    )
                    draft = msg.content[0].text
                    parsed = parse_sections(draft)

                    if not parsed:
                        # Fallback: show raw output in a single tab
                        parsed = {1: {"name": "Full Proposal", "content": draft}}

                    st.session_state.sections      = parsed
                    st.session_state.full_draft    = rebuild_draft(parsed)
                    st.session_state.rfp_saved     = rfp_input
                    st.session_state.prog_saved    = prog_input
                    st.session_state.regen_log     = []
                    st.session_state.settings_snap = {
                        "tone": tone, "length": length,
                        "funder_type": funder_type, "focus_area": focus_area,
                    }
                    st.rerun()

                except anthropic.AuthenticationError:
                    st.error("Invalid API key. Check your key in ⚙️ Settings.")
                except anthropic.RateLimitError:
                    st.error("Rate limit reached. Wait a moment and try again.")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

# ── OUTPUT VIEW ───────────────────────────────────────────────────────────────
else:
    sections = st.session_state.sections
    snap     = st.session_state.settings_snap

    # Status + action bar
    bar_l, bar_r1, bar_r2 = st.columns([5, 1, 1])
    with bar_l:
        tags = " &nbsp;·&nbsp; ".join([
            f"<b style='color:#2DD4BF;'>{snap.get('tone','')}</b>",
            f"<b style='color:#2DD4BF;'>{snap.get('length','')}</b>",
            f"<b style='color:#2DD4BF;'>{snap.get('funder_type','')}</b>",
            f"<b style='color:#2DD4BF;'>{snap.get('focus_area','')}</b>",
        ])
        st.markdown(
            f"<div style='background:#1E2130;border:1px solid #2E3347;border-radius:8px;"
            f"padding:10px 16px;'>"
            f"<span style='color:#2DD4BF;font-weight:700;'>✅ Draft ready</span> &nbsp;"
            f"<span style='color:#9BA3AF;font-size:0.82rem;'>{tags}</span></div>",
            unsafe_allow_html=True,
        )
    with bar_r1:
        st.download_button(
            "⬇️ Download",
            data=st.session_state.full_draft,
            file_name="grant_proposal_draft.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with bar_r2:
        if st.button("← Edit", use_container_width=True, help="Go back and edit inputs"):
            st.session_state.sections   = {}
            st.session_state.full_draft = ""
            st.rerun()

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # Section tabs
    TAB_LABELS = {
        1: "Org Background", 2: "Need Statement",  3: "Project Desc.",
        4: "Goals & Obj.",   5: "Evaluation",       6: "Org Capacity",
        7: "Budget",
    }
    tab_nums   = sorted(sections.keys())
    tab_labels = [TAB_LABELS.get(n, f"§{n}") for n in tab_nums]
    tabs       = st.tabs(tab_labels)

    for tab, num in zip(tabs, tab_nums):
        sec = sections[num]
        with tab:
            st.markdown(sec["content"])
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            st.markdown(
                "<hr style='border-color:#2E3347;margin:4px 0 14px;'>",
                unsafe_allow_html=True,
            )
            act1, act2, act3 = st.columns([1.6, 1.8, 6])
            with act1:
                components.html(_copy_btn(sec["content"], f"s{num}"), height=42)
            with act2:
                if st.button(
                    "↺ Rewrite",
                    key=f"regen_{num}",
                    help=f"Rewrite {sec['name']} with current sidebar settings",
                ):
                    st.session_state.pending_regen = num
                    st.rerun()
            with act3:
                wc = len(sec["content"].split())
                st.markdown(
                    f"<small style='color:#4B5563;line-height:3;'>{wc:,} words &nbsp;·&nbsp; "
                    f"{len(sec['content']):,} chars</small>",
                    unsafe_allow_html=True,
                )

    if st.session_state.regen_log:
        st.markdown(
            "<small style='color:#6B7280;'>Rewritten: "
            + " · ".join(st.session_state.regen_log)
            + "</small>",
            unsafe_allow_html=True,
        )

# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center;color:#4B5563;font-size:0.73rem;'>"
    "Grant Proposal Assistant &nbsp;·&nbsp; JHU Final Project &nbsp;·&nbsp; "
    "Powered by Anthropic Claude &nbsp;·&nbsp; "
    "Always reviewed by a human before submission.</p>",
    unsafe_allow_html=True,
)
