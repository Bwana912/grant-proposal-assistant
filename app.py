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

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MissionBridge AI",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
.stApp { background-color: #0F1117; }
.block-container { padding-top: 1.25rem; padding-bottom: 2rem; max-width: 100%; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1A1F2E !important;
    border-right: 1px solid #2E3347 !important;
    min-width: 215px !important;
    max-width: 215px !important;
}
[data-testid="stSidebar"] section { padding-top: 0 !important; }

/* Sidebar buttons (nav) */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #9BA3AF !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    width: 100% !important;
    text-align: left !important;
    padding: 0.5rem 0.65rem !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(45,212,191,0.09) !important;
    color: #F0F2F6 !important;
}

/* Primary buttons */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2DD4BF, #22b5a3) !important;
    color: #0F1117 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.02em !important;
    padding: 0.65rem 1.4rem !important;
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
}

/* Text areas */
[data-testid="stTextArea"] textarea {
    background: #1A1F2E !important;
    border: 1px solid #2E3347 !important;
    border-radius: 10px !important;
    color: #F0F2F6 !important;
    font-size: 0.87rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextArea"] textarea:focus {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.15) !important;
}
[data-testid="stTextArea"] textarea::placeholder { color: #4B5563 !important; }

/* Text inputs */
[data-testid="stTextInput"] input {
    background: #1A1F2E !important;
    border: 1px solid #2E3347 !important;
    border-radius: 8px !important;
    color: #F0F2F6 !important;
    font-size: 0.92rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #2DD4BF !important;
    box-shadow: 0 0 0 3px rgba(45,212,191,0.15) !important;
}

/* Selectbox */
[data-testid="stSelectbox"] > div > div {
    background: #1A1F2E !important;
    border-color: #2E3347 !important;
    border-radius: 8px !important;
    color: #F0F2F6 !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label span {
    color: #F0F2F6 !important;
    font-size: 0.83rem !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1A1F2E;
    border-radius: 10px 10px 0 0;
    padding: 6px 8px 0;
    gap: 4px;
    border-bottom: 2px solid #2E3347;
}
.stTabs [data-baseweb="tab"] {
    background: transparent;
    color: #9BA3AF;
    border-radius: 8px 8px 0 0;
    font-size: 0.73rem;
    font-weight: 700;
    padding: 7px 11px;
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
    background: #1A1F2E;
    border: 1px solid #2E3347;
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 18px 16px 14px;
}

/* Expander */
[data-testid="stExpander"] details {
    background: #161926 !important;
    border: 1px solid #2E3347 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary { color: #9BA3AF !important; font-size: 0.81rem !important; }

/* Progress bar */
.stProgress > div > div > div { background: #2DD4BF !important; border-radius: 4px !important; }
.stProgress > div > div { background: #2E3347 !important; border-radius: 4px !important; }

/* Dividers */
hr { border-color: #2E3347 !important; opacity: 1 !important; }

/* Alerts */
[data-testid="stAlert"] {
    background: #1A1F2E !important;
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
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(45,212,191,0.1) !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
_DEFAULTS = {
    "screen":       "login",
    "user_email":   "",
    "is_demo":      False,
    "nav_item":     "dashboard",
    "sections":     {},
    "full_draft":   "",
    "rfp_saved":    "",
    "prog_saved":   "",
    "pending_regen": None,
    "regen_log":    [],
    "settings_snap": {},
}
for _k, _v in _DEFAULTS.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

for _wk in ("rfp_area", "prog_area", "api_override"):
    if _wk not in st.session_state:
        st.session_state[_wk] = ""

# ── Seed data ──────────────────────────────────────────────────────────────────
SEED_PROPOSALS = [
    {"name": "TechForward Youth Initiative",  "funder": "Horizon Community Foundation", "amount": "$50,000",  "status": "Drafting",  "deadline": "Jun 15, 2026"},
    {"name": "Digital Literacy Expansion",    "funder": "Gates Foundation",             "amount": "$75,000",  "status": "In Review", "deadline": "May 30, 2026"},
    {"name": "Broadband Access Initiative",   "funder": "FCC E-Rate",                   "amount": "$120,000", "status": "Submitted", "deadline": "Apr 1, 2026"},
    {"name": "AI Literacy for Seniors",       "funder": "AARP Foundation",              "amount": "$35,000",  "status": "Awarded",   "deadline": "Mar 15, 2026"},
    {"name": "Career Pathways Program",       "funder": "JPMorgan Chase",               "amount": "$60,000",  "status": "Drafting",  "deadline": "Jul 10, 2026"},
]

STATUS_COLORS = {
    "Drafting":  ("#2DD4BF", "#0d3330"),
    "In Review": ("#F59E0B", "#3d2e0a"),
    "Submitted": ("#3B82F6", "#0d1f3d"),
    "Awarded":   ("#10B981", "#0a2e1e"),
    "Archived":  ("#6B7280", "#1e1e24"),
}

# ── Helpers ────────────────────────────────────────────────────────────────────
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
            result[num] = {"name": name, "content": f"## {num}. {name}\n\n{body}"}
    return result


def rebuild_draft(sections: dict) -> str:
    return "\n\n---\n\n".join(sections[n]["content"] for n in sorted(sections))


def _copy_btn(text: str, uid: str) -> str:
    safe = text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")
    return (
        f'<button id="cb_{uid}" '
        'style="background:#2DD4BF;color:#0F1117;border:none;padding:6px 15px;'
        'border-radius:6px;cursor:pointer;font-weight:700;font-size:12px;'
        'font-family:system-ui,-apple-system,sans-serif;letter-spacing:0.03em;" '
        'onmouseover="this.style.background=\'#22b5a3\'" '
        'onmouseout="this.style.background=\'#2DD4BF\'" '
        f'onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{'
        f'var b=document.getElementById(\'cb_{uid}\');'
        "b.textContent='✓ Copied!';b.style.background='#059669';b.style.color='#fff';"
        f"setTimeout(()=>{{b.textContent='📋 Copy';b.style.background='#2DD4BF';b.style.color='#0F1117';}},2000);"
        "}).catch(()=>alert('Copy manually.'));\">"
        "📋 Copy</button>"
    )


def compute_alignment(rfp: str, proposal: str) -> int:
    if not rfp or not proposal:
        return 0
    stop = {
        'about','above','after','again','their','there','these','which','while',
        'would','could','should','where','other','those','under','until','before',
        'include','program','nonprofit','community','organization','provide',
        'support','service','funding','grant','proposal','foundation','between',
        'through','during','having','within','without','across','further',
    }
    rfp_w  = set(re.findall(r'\b[a-z]{5,}\b', rfp.lower()))  - stop
    prop_w = set(re.findall(r'\b[a-z]{5,}\b', proposal.lower())) - stop
    if not rfp_w:
        return 85
    return max(62, min(97, int(len(rfp_w & prop_w) / len(rfp_w) * 160)))


def _resolved_api_key() -> str:
    return st.session_state.get("api_override", "").strip() or os.getenv("ANTHROPIC_API_KEY", "")


# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN 1 — LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <style>
    section[data-testid="stSidebar"]          { display: none !important; }
    button[data-testid="collapsedControl"]    { display: none !important; }
    .block-container                          { padding-top: 4rem !important; }
    </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        # Branding
        st.markdown("""
        <div style="text-align:center;margin-bottom:2.25rem;">
            <div style="font-size:3.2rem;margin-bottom:0.5rem;">🌉</div>
            <h1 style="color:#F0F2F6;font-size:2.1rem;font-weight:900;margin:0;letter-spacing:-0.03em;">
                MissionBridge AI
            </h1>
            <p style="color:#9BA3AF;font-size:0.97rem;margin-top:8px;margin-bottom:0;">
                AI-powered grant proposals for nonprofits
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Card
        st.markdown("""
        <div style="background:#1A1F2E;border:1px solid #2E3347;border-radius:16px;
                    padding:2rem 2.25rem 1.75rem;">
        """, unsafe_allow_html=True)

        st.markdown(
            "<p style='color:#F0F2F6;font-weight:700;font-size:1rem;margin:0 0 1.1rem;'>Sign in to your workspace</p>",
            unsafe_allow_html=True,
        )

        email    = st.text_input("Email address", placeholder="you@yourorg.org", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

        st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign In", type="primary", use_container_width=True, key="btn_signin"):
                if email.strip():
                    st.session_state.user_email = email.strip()
                    st.session_state.is_demo    = False
                    st.session_state.screen     = "dashboard"
                    st.session_state.nav_item   = "dashboard"
                    st.rerun()
                else:
                    st.error("Enter your email address.")
        with c2:
            if st.button("Continue as Demo", use_container_width=True, key="btn_demo"):
                st.session_state.user_email = "demo@missionbridge.ai"
                st.session_state.is_demo    = True
                st.session_state.screen     = "dashboard"
                st.session_state.nav_item   = "dashboard"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
        <p style="text-align:center;color:#4B5563;font-size:0.74rem;margin-top:1.25rem;">
            Demo mode: any email + any password &nbsp;·&nbsp; No data stored externally
        </p>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAV  (shared by Dashboard + Workspace)
# ══════════════════════════════════════════════════════════════════════════════
def show_sidebar_nav():
    with st.sidebar:
        st.markdown("""
        <div style="padding:1rem 0.6rem 0.85rem;border-bottom:1px solid #2E3347;margin-bottom:0.6rem;">
            <span style="font-size:1.45rem;">🌉</span>
            <span style="color:#F0F2F6;font-size:1rem;font-weight:800;margin-left:8px;letter-spacing:-0.01em;">
                MissionBridge AI
            </span>
        </div>
        """, unsafe_allow_html=True)

        NAV = [
            ("dashboard",  "📊", "Dashboard"),
            ("workspace",  "✍️", "New Proposal"),
            ("proposals",  "📋", "All Proposals"),
            ("rfp",        "🔍", "RFP Analyzer"),
            ("research",   "🔬", "Research Hub"),
            ("analytics",  "📈", "Analytics"),
            ("settings",   "⚙️",  "Settings"),
        ]

        active = st.session_state.nav_item
        for key, icon, label in NAV:
            if active == key:
                st.markdown(
                    f"<div style='background:rgba(45,212,191,0.12);border-left:3px solid #2DD4BF;"
                    f"border-radius:0 8px 8px 0;padding:0.5rem 0.65rem;margin-bottom:2px;"
                    f"color:#2DD4BF;font-size:0.88rem;font-weight:700;cursor:default;'>"
                    f"{icon}&nbsp; {label}</div>",
                    unsafe_allow_html=True,
                )
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                    st.session_state.nav_item = key
                    if key == "workspace":
                        st.session_state.screen = "workspace"
                    else:
                        st.session_state.screen = "dashboard"
                    st.rerun()

        # User footer
        st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
        st.divider()

        email    = st.session_state.user_email
        raw_name = email.split("@")[0]
        initials = "".join(p[0].upper() for p in raw_name.split(".")[:2]) if raw_name else "DM"
        role_tag = "Demo Mode" if st.session_state.is_demo else "Admin"

        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;padding:0.3rem 0.4rem;'>"
            f"<div style='background:#2DD4BF;color:#0F1117;width:32px;height:32px;"
            f"border-radius:50%;display:flex;align-items:center;justify-content:center;"
            f"font-weight:800;font-size:0.75rem;flex-shrink:0;'>{initials}</div>"
            f"<div style='overflow:hidden;'>"
            f"<div style='color:#F0F2F6;font-size:0.78rem;font-weight:600;"
            f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:130px;'>{email}</div>"
            f"<div style='color:#9BA3AF;font-size:0.68rem;'>{role_tag}</div>"
            f"</div></div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:4px;'></div>", unsafe_allow_html=True)
        if st.button("Sign Out", key="sign_out", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN 2 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    email = st.session_state.user_email
    first = email.split("@")[0].split(".")[0].capitalize()

    # Greeting
    st.markdown(
        f"<h1 style='color:#F0F2F6;font-size:1.75rem;font-weight:900;margin-bottom:2px;'>"
        f"Good morning, {first}! 👋</h1>"
        f"<p style='color:#9BA3AF;font-size:0.92rem;margin-top:0 0 0.25rem;'>"
        f"Here's your grant portfolio at a glance.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

    # Stats cards
    c1, c2, c3, c4 = st.columns(4)
    stats = [
        ("📋", "Active Proposals", "3",   "+1 this week"),
        ("📤", "Submitted",        "2",   "this month"),
        ("🏆", "Win Rate",         "67%", "+5% vs last Qtr"),
        ("⚡", "Avg. Draft Time",  "28s", "vs 20–40 hrs manual"),
    ]
    for col, (icon, label, value, delta) in zip([c1, c2, c3, c4], stats):
        with col:
            st.markdown(
                f"<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:12px;"
                f"padding:1.1rem 1.2rem;'>"
                f"<div style='font-size:1.35rem;margin-bottom:5px;'>{icon}</div>"
                f"<div style='color:#9BA3AF;font-size:0.72rem;font-weight:700;text-transform:uppercase;"
                f"letter-spacing:0.06em;margin-bottom:4px;'>{label}</div>"
                f"<div style='color:#F0F2F6;font-size:1.65rem;font-weight:900;line-height:1;'>{value}</div>"
                f"<div style='color:#2DD4BF;font-size:0.71rem;margin-top:5px;'>{delta}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:1.4rem;'></div>", unsafe_allow_html=True)

    # Proposals table header
    hdr_l, hdr_r = st.columns([5, 1])
    with hdr_l:
        st.markdown(
            "<h3 style='color:#F0F2F6;font-size:1.05rem;font-weight:700;margin:0;'>Recent Proposals</h3>",
            unsafe_allow_html=True,
        )
    with hdr_r:
        if st.button("＋ New Proposal", type="primary", use_container_width=True, key="dash_new"):
            st.session_state.screen    = "workspace"
            st.session_state.nav_item  = "workspace"
            st.session_state.sections  = {}
            st.session_state.full_draft = ""
            st.session_state.rfp_area  = ""
            st.session_state.prog_area = ""
            st.rerun()

    # Table HTML
    rows = ""
    for p in SEED_PROPOSALS:
        color, bg = STATUS_COLORS.get(p["status"], ("#9BA3AF", "#1e2130"))
        badge = (
            f"<span style='background:{bg};color:{color};border:1px solid {color};"
            f"border-radius:20px;padding:3px 10px;font-size:0.71rem;font-weight:700;'>"
            f"{p['status']}</span>"
        )
        rows += (
            f"<tr style='border-bottom:1px solid #2E3347;transition:background 0.15s;'>"
            f"<td style='padding:12px 16px;color:#F0F2F6;font-weight:600;font-size:0.87rem;'>{p['name']}</td>"
            f"<td style='padding:12px 16px;color:#9BA3AF;font-size:0.84rem;'>{p['funder']}</td>"
            f"<td style='padding:12px 16px;color:#2DD4BF;font-weight:700;font-size:0.87rem;'>{p['amount']}</td>"
            f"<td style='padding:12px 16px;'>{badge}</td>"
            f"<td style='padding:12px 16px;color:#9BA3AF;font-size:0.82rem;'>{p['deadline']}</td>"
            f"</tr>"
        )

    st.markdown(
        f"<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:12px;"
        f"overflow:hidden;margin-top:0.7rem;'>"
        f"<table style='width:100%;border-collapse:collapse;'>"
        f"<thead><tr style='border-bottom:1px solid #2E3347;background:#161926;'>"
        f"<th style='padding:10px 16px;color:#9BA3AF;font-size:0.72rem;font-weight:700;"
        f"text-align:left;text-transform:uppercase;letter-spacing:0.06em;'>Proposal</th>"
        f"<th style='padding:10px 16px;color:#9BA3AF;font-size:0.72rem;font-weight:700;"
        f"text-align:left;text-transform:uppercase;letter-spacing:0.06em;'>Funder</th>"
        f"<th style='padding:10px 16px;color:#9BA3AF;font-size:0.72rem;font-weight:700;"
        f"text-align:left;text-transform:uppercase;letter-spacing:0.06em;'>Amount</th>"
        f"<th style='padding:10px 16px;color:#9BA3AF;font-size:0.72rem;font-weight:700;"
        f"text-align:left;text-transform:uppercase;letter-spacing:0.06em;'>Status</th>"
        f"<th style='padding:10px 16px;color:#9BA3AF;font-size:0.72rem;font-weight:700;"
        f"text-align:left;text-transform:uppercase;letter-spacing:0.06em;'>Deadline</th>"
        f"</tr></thead><tbody>{rows}</tbody></table></div>",
        unsafe_allow_html=True,
    )

    # Coming-soon chips for non-workspace nav items
    nav = st.session_state.nav_item
    if nav not in ("dashboard", "workspace"):
        nav_labels = {
            "proposals": "All Proposals", "rfp": "RFP Analyzer",
            "research": "Research Hub", "analytics": "Analytics", "settings": "Settings",
        }
        label = nav_labels.get(nav, nav.capitalize())
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f"<div style='background:#1A1F2E;border:1px dashed #2E3347;border-radius:12px;"
            f"padding:2rem;text-align:center;'>"
            f"<div style='font-size:2rem;margin-bottom:0.5rem;'>🚧</div>"
            f"<div style='color:#F0F2F6;font-weight:700;font-size:1rem;'>{label}</div>"
            f"<div style='color:#9BA3AF;font-size:0.83rem;margin-top:6px;'>"
            f"This module is available in the full platform.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  SCREEN 3 — PROPOSAL WORKSPACE
# ══════════════════════════════════════════════════════════════════════════════
def show_workspace():
    # ── Handle pending section regen (runs before columns render) ─────────────
    if st.session_state.pending_regen is not None and st.session_state.sections:
        sec_num  = st.session_state.pending_regen
        st.session_state.pending_regen = None
        sec_name = dict(SECTION_DEFS).get(sec_num, f"Section {sec_num}")
        snap     = st.session_state.settings_snap

        with st.spinner(f"Rewriting: {sec_name}…"):
            api_key = _resolved_api_key()
            if not api_key:
                st.error("No API key found. Add it in the ⚙️ API Settings panel.")
            else:
                try:
                    client = anthropic.Anthropic(api_key=api_key)
                    msg = client.messages.create(
                        model="claude-sonnet-4-6",
                        max_tokens=1500,
                        messages=[{"role": "user", "content": build_section_regen_prompt(
                            sec_num, sec_name,
                            st.session_state.sections[sec_num]["content"],
                            st.session_state.rfp_saved,
                            st.session_state.prog_saved,
                            snap.get("tone",         "Persuasive"),
                            snap.get("length",        "Standard"),
                            snap.get("funder_type",   "Private Foundation"),
                            snap.get("focus_area",    "Digital Equity"),
                            snap.get("reading_level", "Professional"),
                        )}],
                    )
                    st.session_state.sections[sec_num]["content"] = msg.content[0].text.strip()
                    st.session_state.full_draft = rebuild_draft(st.session_state.sections)
                    st.session_state.regen_log.append(sec_name)
                except anthropic.AuthenticationError:
                    st.error("Invalid API key.")
                except Exception as exc:
                    st.error(f"Rewrite failed: {exc}")

    # Workspace header / breadcrumb
    st.markdown(
        "<div style='margin-bottom:0.85rem;'>"
        "<span style='color:#9BA3AF;font-size:0.78rem;'>📋 Proposals &nbsp;/&nbsp;</span>"
        "<span style='color:#F0F2F6;font-size:0.78rem;font-weight:600;'>New Proposal</span>"
        "</div>"
        "<h2 style='color:#F0F2F6;font-size:1.35rem;font-weight:900;margin:0 0 1rem;'>"
        "Proposal Workspace</h2>",
        unsafe_allow_html=True,
    )

    # ── 3-column layout ────────────────────────────────────────────────────────
    left_col, center_col, right_col = st.columns([2, 5, 2.3])

    # ── LEFT: Fine-tuning ──────────────────────────────────────────────────────
    with left_col:
        st.markdown(
            "<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:12px;padding:1rem 0.9rem;'>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color:#2DD4BF;font-size:0.82rem;font-weight:800;text-transform:uppercase;"
            "letter-spacing:0.06em;margin:0 0 0.75rem;'>🎨 Fine-Tuning</p>",
            unsafe_allow_html=True,
        )

        tone          = st.selectbox("Tone",          ["Persuasive", "Formal", "Urgent", "Conversational"],                    key="ws_tone")
        length        = st.selectbox("Length",        ["Standard", "Concise", "Comprehensive"],                                key="ws_length")
        funder_type   = st.selectbox("Funder Type",   ["Private Foundation", "Government", "Corporate", "Community Fund"],     key="ws_funder")
        focus_area    = st.selectbox("Focus Area",    ["Digital Equity", "Youth Development", "Education", "Health", "Workforce", "Other"], key="ws_focus")
        reading_level = st.selectbox("Reading Level", ["Professional", "Expert", "General Audience"],                          key="ws_reading")

        st.markdown(
            "<p style='color:#9BA3AF;font-size:0.75rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:0.05em;margin:0.85rem 0 0.4rem;'>Sections to Include</p>",
            unsafe_allow_html=True,
        )
        selected_sections = [
            num for num, name in SECTION_DEFS
            if st.checkbox(name[:24] + ("…" if len(name) > 24 else ""), value=True, key=f"sec_{num}")
        ]
        if not selected_sections:
            st.warning("Select at least 1 section.")

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

        with st.expander("⚙️ API Settings"):
            st.text_input(
                "API Key Override",
                type="password",
                placeholder="sk-ant-… (optional)",
                key="api_override",
            )
            st.markdown(
                "<small style='color:#6B7280;'>Reads from .env by default. Override here for testing.</small>",
                unsafe_allow_html=True,
            )

        if st.session_state.sections:
            st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
            if st.button("🔁 Start Over", use_container_width=True, key="start_over"):
                st.session_state.sections   = {}
                st.session_state.full_draft = ""
                st.session_state.rfp_area   = ""
                st.session_state.prog_area  = ""
                st.session_state.regen_log  = []
                st.session_state.settings_snap = {}
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # ── CENTER: Inputs / Output ────────────────────────────────────────────────
    with center_col:

        if not st.session_state.sections:
            # ── API key warning ──
            if not _resolved_api_key():
                st.warning(
                    "⚠️ No API key detected. Add `ANTHROPIC_API_KEY=sk-ant-…` to your `.env` file, "
                    "or enter it in ⚙️ API Settings (left panel)."
                )

            # ── RFP input ──
            rfp_hdr, rfp_btn = st.columns([5, 1])
            with rfp_hdr:
                st.markdown(
                    "<p style='color:#F0F2F6;font-size:0.95rem;font-weight:700;margin-bottom:4px;'>"
                    "📄 Funder RFP / Guidelines</p>",
                    unsafe_allow_html=True,
                )
            with rfp_btn:
                if st.button("Load eg.", key="load_rfp", help="Load built-in sample RFP"):
                    st.session_state.rfp_area = _read(
                        os.path.join(BASE, "examples", "rfp_sample.txt")
                    )
                    st.rerun()

            rfp_input = st.text_area(
                "rfp",
                key="rfp_area",
                height=215,
                placeholder="Paste the funder's full RFP, call for proposals, or grant guidelines here…",
                label_visibility="collapsed",
            )
            char1 = len(rfp_input)
            st.markdown(
                f"<small style='color:{'#2DD4BF' if char1 > 100 else '#4B5563'};'>"
                f"✏️ {char1:,} chars"
                + (" · ready" if char1 > 100 else " · paste RFP above")
                + "</small>",
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)

            # ── Program description ──
            prog_hdr, prog_btn = st.columns([5, 1])
            with prog_hdr:
                st.markdown(
                    "<p style='color:#F0F2F6;font-size:0.95rem;font-weight:700;margin-bottom:4px;'>"
                    "🏢 Program Description</p>",
                    unsafe_allow_html=True,
                )
            with prog_btn:
                if st.button("Load eg.", key="load_prog", help="Load built-in sample program description"):
                    st.session_state.prog_area = _read(
                        os.path.join(BASE, "examples", "program_desc.txt")
                    )
                    st.rerun()

            prog_input = st.text_area(
                "prog",
                key="prog_area",
                height=215,
                placeholder="Describe your nonprofit's mission, program, target population, activities, and outcomes…",
                label_visibility="collapsed",
            )
            char2 = len(prog_input)
            st.markdown(
                f"<small style='color:{'#2DD4BF' if char2 > 100 else '#4B5563'};'>"
                f"✏️ {char2:,} chars"
                + (" · ready" if char2 > 100 else " · describe your program above")
                + "</small>",
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)

            # Settings summary bar
            st.markdown(
                f"<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:8px;"
                f"padding:8px 14px;margin-bottom:10px;display:flex;gap:14px;flex-wrap:wrap;'>"
                f"<span style='color:#9BA3AF;font-size:0.76rem;'>Tone: <b style='color:#2DD4BF;'>{tone}</b></span>"
                f"<span style='color:#9BA3AF;font-size:0.76rem;'>Length: <b style='color:#2DD4BF;'>{length}</b></span>"
                f"<span style='color:#9BA3AF;font-size:0.76rem;'>Funder: <b style='color:#2DD4BF;'>{funder_type}</b></span>"
                f"<span style='color:#9BA3AF;font-size:0.76rem;'>Sections: <b style='color:#2DD4BF;'>{len(selected_sections)}/7</b></span>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Generate button
            if st.button(
                "🚀  Generate Grant Proposal",
                type="primary",
                use_container_width=True,
                disabled=not selected_sections,
                key="gen_btn",
            ):
                api_key = _resolved_api_key()
                if not api_key:
                    st.error("Add your API key in ⚙️ API Settings (left panel) or your `.env` file.")
                elif not rfp_input.strip():
                    st.warning("Paste the funder's RFP before generating.")
                elif not prog_input.strip():
                    st.warning("Describe your program before generating.")
                else:
                    with st.spinner("✍️ Drafting your grant proposal… (20–40 seconds)"):
                        try:
                            client = anthropic.Anthropic(api_key=api_key)
                            msg = client.messages.create(
                                model="claude-sonnet-4-6",
                                max_tokens=4096,
                                system=build_dynamic_system_prompt(
                                    tone, length, funder_type, focus_area,
                                    selected_sections, reading_level,
                                ),
                                messages=[{
                                    "role": "user",
                                    "content": build_user_prompt(rfp_input, prog_input),
                                }],
                            )
                            draft  = msg.content[0].text
                            parsed = parse_sections(draft)
                            if not parsed:
                                parsed = {1: {"name": "Full Proposal", "content": draft}}

                            st.session_state.sections      = parsed
                            st.session_state.full_draft    = rebuild_draft(parsed)
                            st.session_state.rfp_saved     = rfp_input
                            st.session_state.prog_saved    = prog_input
                            st.session_state.regen_log     = []
                            st.session_state.settings_snap = {
                                "tone": tone, "length": length,
                                "funder_type": funder_type, "focus_area": focus_area,
                                "reading_level": reading_level,
                            }
                            st.rerun()

                        except anthropic.AuthenticationError:
                            st.error("Invalid API key. Check ⚙️ API Settings.")
                        except anthropic.RateLimitError:
                            st.error("Rate limit reached. Wait a moment and try again.")
                        except Exception as exc:
                            st.error(f"Generation failed: {exc}")

        else:
            # ── Output view ───────────────────────────────────────────────────
            sections = st.session_state.sections
            snap     = st.session_state.settings_snap

            tags = "&nbsp;·&nbsp;".join([
                f"<b style='color:#2DD4BF;'>{snap.get('tone','')}</b>",
                f"<b style='color:#2DD4BF;'>{snap.get('length','')}</b>",
                f"<b style='color:#2DD4BF;'>{snap.get('funder_type','')}</b>",
            ])
            bar_l, bar_r1, bar_r2 = st.columns([4, 1, 1])
            with bar_l:
                st.markdown(
                    f"<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:8px;"
                    f"padding:8px 14px;'>"
                    f"<span style='color:#2DD4BF;font-weight:700;'>✅ Draft Ready</span>"
                    f"<span style='color:#9BA3AF;font-size:0.77rem;margin-left:8px;'>{tags}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with bar_r1:
                st.download_button(
                    "⬇️ Export",
                    data=st.session_state.full_draft,
                    file_name="grant_proposal_draft.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with bar_r2:
                if st.button("← Inputs", use_container_width=True, help="Return to input form"):
                    st.session_state.sections   = {}
                    st.session_state.full_draft = ""
                    st.rerun()

            st.markdown("<div style='height:0.4rem;'></div>", unsafe_allow_html=True)

            TAB_LABELS = {
                1: "Org Bg.", 2: "Need", 3: "Program",
                4: "Goals",   5: "Eval.", 6: "Capacity", 7: "Budget",
            }
            tab_nums = sorted(sections.keys())
            tabs     = st.tabs([TAB_LABELS.get(n, f"§{n}") for n in tab_nums])

            for tab, num in zip(tabs, tab_nums):
                sec = sections[num]
                with tab:
                    st.markdown(sec["content"])
                    st.markdown(
                        "<hr style='border-color:#2E3347;margin:10px 0 12px;'>",
                        unsafe_allow_html=True,
                    )
                    a1, a2, a3 = st.columns([1.5, 1.7, 5])
                    with a1:
                        components.html(_copy_btn(sec["content"], f"s{num}"), height=34)
                    with a2:
                        if st.button("↺ Rewrite", key=f"regen_{num}",
                                     help="AI-rewrite this section with current settings"):
                            st.session_state.pending_regen = num
                            st.rerun()
                    with a3:
                        wc = len(sec["content"].split())
                        st.markdown(
                            f"<small style='color:#4B5563;line-height:2.4;'>"
                            f"{wc:,} words &nbsp;·&nbsp; {len(sec['content']):,} chars</small>",
                            unsafe_allow_html=True,
                        )

            if st.session_state.regen_log:
                st.markdown(
                    f"<small style='color:#6B7280;'>"
                    f"Rewritten: {' · '.join(st.session_state.regen_log)}</small>",
                    unsafe_allow_html=True,
                )

    # ── RIGHT: Intelligence panel ──────────────────────────────────────────────
    with right_col:
        has_draft = bool(st.session_state.sections)

        st.markdown(
            "<div style='background:#1A1F2E;border:1px solid #2E3347;border-radius:12px;"
            "padding:1rem 0.9rem;'>",
            unsafe_allow_html=True,
        )

        # Compliance checklist
        st.markdown(
            "<p style='color:#2DD4BF;font-size:0.78rem;font-weight:800;text-transform:uppercase;"
            "letter-spacing:0.06em;margin:0 0 0.6rem;'>✅ Compliance</p>",
            unsafe_allow_html=True,
        )
        done_nums = set(st.session_state.sections.keys()) if has_draft else set()
        compliance = [
            (1 in done_nums, "Org background"),
            (2 in done_nums, "Need statement"),
            (3 in done_nums, "Program description"),
            (4 in done_nums, "Goals & objectives"),
            (5 in done_nums, "Evaluation plan"),
            (7 in done_nums, "Budget narrative"),
            (False,          "Signed cover letter"),
            (False,          "Letters of support"),
        ]
        comp_html = ""
        for done, item in compliance:
            icon  = "✅" if done else "○"
            color = "#2DD4BF" if done else "#6B7280"
            comp_html += f"<div style='color:{color};font-size:0.77rem;padding:2px 0;'>{icon} {item}</div>"
        st.markdown(comp_html, unsafe_allow_html=True)

        st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

        # Funder alignment score
        st.markdown(
            "<p style='color:#2DD4BF;font-size:0.78rem;font-weight:800;text-transform:uppercase;"
            "letter-spacing:0.06em;margin:0 0 0.45rem;'>🎯 Funder Alignment</p>",
            unsafe_allow_html=True,
        )
        if has_draft:
            score = compute_alignment(
                st.session_state.rfp_saved, st.session_state.full_draft
            )
            st.progress(score / 100)
            st.markdown(
                f"<div style='color:#2DD4BF;font-size:1.1rem;font-weight:900;margin-top:3px;'>{score}%</div>"
                f"<div style='color:#9BA3AF;font-size:0.71rem;'>keyword alignment with RFP</div>",
                unsafe_allow_html=True,
            )
        else:
            st.progress(0.0)
            st.markdown(
                "<div style='color:#6B7280;font-size:0.74rem;margin-top:3px;'>"
                "Score appears after generation.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

        # Review status stages
        st.markdown(
            "<p style='color:#2DD4BF;font-size:0.78rem;font-weight:800;text-transform:uppercase;"
            "letter-spacing:0.06em;margin:0 0 0.5rem;'>📍 Review Status</p>",
            unsafe_allow_html=True,
        )
        current_stage = 2 if has_draft else 1
        stages = [("✏️", "Draft"), ("👥", "Internal Review"), ("✔️", "Final Edits"), ("🚀", "Submit Ready")]
        stage_html = "<div style='display:flex;flex-direction:column;gap:7px;'>"
        for i, (icon, label) in enumerate(stages, 1):
            if i < current_stage:
                color, fw, prefix = "#2DD4BF", "600", "✓ "
            elif i == current_stage:
                color, fw, prefix = "#F0F2F6", "800", "▶ "
            else:
                color, fw, prefix = "#4B5563", "400", "○ "
            stage_html += (
                f"<div style='display:flex;align-items:center;gap:6px;'>"
                f"<span style='color:{color};font-size:0.77rem;font-weight:{fw};'>{prefix}{icon} {label}</span>"
                f"</div>"
            )
        stage_html += "</div>"
        st.markdown(stage_html, unsafe_allow_html=True)

        st.markdown("<div style='height:0.85rem;'></div>", unsafe_allow_html=True)

        # Export readiness checklist
        st.markdown(
            "<p style='color:#2DD4BF;font-size:0.78rem;font-weight:800;text-transform:uppercase;"
            "letter-spacing:0.06em;margin:0 0 0.45rem;'>📤 Export Readiness</p>",
            unsafe_allow_html=True,
        )
        export_items = [
            (has_draft, "All sections generated"),
            (False,     "Budget reviewed by finance"),
            (False,     "Executive sign-off"),
            (False,     "Attachments gathered"),
        ]
        exp_html = ""
        for done, item in export_items:
            icon  = "✅" if done else "○"
            color = "#2DD4BF" if done else "#6B7280"
            exp_html += f"<div style='color:{color};font-size:0.77rem;padding:2px 0;'>{icon} {item}</div>"
        st.markdown(exp_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN ROUTER
# ══════════════════════════════════════════════════════════════════════════════
screen = st.session_state.screen

if screen == "login":
    show_login()
else:
    show_sidebar_nav()
    if screen == "workspace" or st.session_state.nav_item == "workspace":
        show_workspace()
    else:
        show_dashboard()

# ── Footer ─────────────────────────────────────────────────────────────────────
if screen != "login":
    st.markdown(
        "<p style='text-align:center;color:#4B5563;font-size:0.71rem;margin-top:2.5rem;'>"
        "MissionBridge AI &nbsp;·&nbsp; JHU Generative AI Final Project &nbsp;·&nbsp; "
        "Powered by Anthropic Claude &nbsp;·&nbsp; "
        "Always reviewed by a human before submission.</p>",
        unsafe_allow_html=True,
    )
