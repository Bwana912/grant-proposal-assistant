import re, os, datetime
import streamlit as st
import streamlit.components.v1 as components
import anthropic
from dotenv import load_dotenv
from prompts.grant_prompt import (
    SECTION_DEFS, build_dynamic_system_prompt,
    build_user_prompt, build_section_regen_prompt,
)

load_dotenv()

st.set_page_config(page_title="MissionBridge AI", page_icon="🌱",
                   layout="wide", initial_sidebar_state="expanded")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""<style>
/* ── Base ── */
.stApp{background:#F8FAFC}
.block-container{padding-top:1.1rem;padding-bottom:2rem;max-width:100%}
/* ── Sidebar ── */
[data-testid="stSidebar"]{
  background:#FFFFFF!important;
  border-right:1.5px solid #E2E8F0!important;
  min-width:252px!important;max-width:252px!important}
[data-testid="stSidebar"] section{padding-top:0!important}
/* Flat borderless nav buttons — all states */
[data-testid="stSidebar"] .stButton>button,
[data-testid="stSidebar"] .stButton>button:hover,
[data-testid="stSidebar"] .stButton>button:focus,
[data-testid="stSidebar"] .stButton>button:active,
[data-testid="stSidebar"] .stButton>button:focus:not(:active){
  background:transparent!important;border:none!important;
  outline:none!important;box-shadow:none!important;
  color:#64748B!important;border-radius:7px!important;
  font-size:.82rem!important;font-weight:500!important;
  width:100%!important;text-align:left!important;
  padding:.43rem .75rem!important;
  transition:background .12s,color .12s!important;margin-bottom:0!important}
[data-testid="stSidebar"] .stButton>button:hover{
  background:#F1F5F9!important;color:#1E293B!important;
  border:none!important;box-shadow:none!important}
[data-testid="stSidebar"] .stButton>button:active{
  background:#EEF2FF!important;border:none!important;box-shadow:none!important}
[data-testid="stSidebar"] [data-testid="stButton"]{
  border:none!important;background:transparent!important;box-shadow:none!important}
[data-testid="stSidebar"] .stButton>button:focus-visible{
  outline:none!important;box-shadow:none!important;border:none!important}
/* ── Primary buttons ── */
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#6366F1,#8B5CF6)!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-weight:700!important;font-size:.92rem!important;
  padding:.58rem 1.3rem!important;transition:all .2s ease!important;
  box-shadow:0 4px 14px rgba(99,102,241,.28)!important}
.stButton>button[kind="primary"]:hover{
  box-shadow:0 6px 22px rgba(99,102,241,.45)!important;transform:translateY(-1px)!important}
/* ── Secondary buttons ── */
.stButton>button[kind="secondary"]{
  background:#fff!important;color:#6366F1!important;
  border:1.5px solid #6366F1!important;border-radius:8px!important;font-weight:600!important}
.stButton>button[kind="secondary"]:hover{background:#EEF2FF!important}
/* ── Default buttons ── */
.stButton>button{
  border-radius:8px!important;font-size:.87rem!important;transition:all .15s!important}
/* ── Form fields ── */
[data-testid="stTextArea"] textarea{
  background:#FFFFFF!important;border:1.5px solid #E2E8F0!important;
  border-radius:10px!important;color:#1E293B!important;
  font-size:.87rem!important;line-height:1.65!important}
[data-testid="stTextArea"] textarea:focus{
  border-color:#6366F1!important;box-shadow:0 0 0 3px rgba(99,102,241,.12)!important}
[data-testid="stTextInput"] input{
  background:#FFFFFF!important;border:1.5px solid #E2E8F0!important;
  border-radius:8px!important;color:#1E293B!important;font-size:.92rem!important}
[data-testid="stTextInput"] input:focus{
  border-color:#6366F1!important;box-shadow:0 0 0 3px rgba(99,102,241,.12)!important}
[data-testid="stSelectbox"]>div>div{
  background:#FFFFFF!important;border-color:#E2E8F0!important;
  border-radius:8px!important;color:#1E293B!important}
[data-testid="stCheckbox"] label span{color:#1E293B!important;font-size:.83rem!important}
[data-testid="stCheckbox"] label p{color:#1E293B!important;font-size:.83rem!important}
[data-testid="stRadio"] label span{color:#1E293B!important;font-size:.86rem!important}
[data-testid="stWidgetLabel"] p{color:#1E293B!important;font-size:.85rem!important;font-weight:500!important}
[data-testid="stWidgetLabel"] label{color:#1E293B!important;font-size:.85rem!important}
[data-testid="stSelectbox"] label{color:#1E293B!important;font-size:.85rem!important}
.stSelectbox label, .stTextInput label, .stTextArea label{color:#1E293B!important;font-size:.85rem!important}
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
  background:#F1F5F9;border-radius:10px 10px 0 0;
  padding:6px 8px 0;gap:3px;border-bottom:2px solid #E2E8F0}
.stTabs [data-baseweb="tab"]{
  background:transparent;color:#94A3B8;border-radius:8px 8px 0 0;
  font-size:.72rem;font-weight:700;padding:7px 10px;border:none;letter-spacing:.03em}
.stTabs [data-baseweb="tab"]:hover{color:#1E293B}
.stTabs [aria-selected="true"]{background:#6366F1!important;color:#fff!important}
.stTabs [data-baseweb="tab-panel"]{
  background:#FFFFFF;border:1.5px solid #E2E8F0;border-top:none;
  border-radius:0 0 10px 10px;padding:20px 18px 16px}
/* ── Expanders ── */
[data-testid="stExpander"] details{
  background:#FFFFFF!important;border:1.5px solid #E2E8F0!important;border-radius:12px!important;
  overflow:hidden!important;margin-bottom:2px!important}
[data-testid="stExpander"] summary{color:#1E293B!important;font-size:.84rem!important;
  font-weight:600!important;padding:.65rem 1rem!important}
[data-testid="stExpander"] details[open] summary{color:#4F46E5!important;background:#F8FAFF!important}
[data-testid="stExpander"] details summary:focus{outline:none!important}
/* ── Progress / dividers ── */
.stProgress>div>div>div{border-radius:6px!important;
  background:linear-gradient(90deg,#6366F1,#8B5CF6)!important}
.stProgress>div>div{background:#E2E8F0!important;border-radius:6px!important;height:10px!important}
hr{border-color:#E2E8F0!important;opacity:1!important}
/* ── Alerts ── */
[data-testid="stAlert"]{
  background:#FFFFFF!important;border:1.5px solid #E2E8F0!important;border-radius:10px!important}
/* ── Download buttons ── */
[data-testid="stDownloadButton"]>button{
  background:#EEF2FF!important;color:#6366F1!important;
  border:1.5px solid #6366F1!important;border-radius:8px!important;
  font-weight:600!important;font-size:.83rem!important;
  transition:all .2s!important;padding:.45rem .9rem!important}
[data-testid="stDownloadButton"]>button:hover{
  background:#6366F1!important;color:#fff!important}
/* ── Card hover effect ── */
.mb-card{transition:box-shadow .2s,transform .2s;}
.mb-card:hover{box-shadow:0 6px 24px rgba(99,102,241,.14)!important;transform:translateY(-1px);}
/* ── File uploader — full light theme ── */
[data-testid="stFileUploadDropzone"]{
  background:#F8FAFC!important;border:2px dashed #6366F1!important;
  border-radius:14px!important;padding:1.2rem!important}
[data-testid="stFileUploadDropzone"] p,
[data-testid="stFileUploadDropzone"] small,
[data-testid="stFileUploadDropzone"] span{color:#64748B!important;font-size:.84rem!important}
[data-testid="stFileUploadDropzone"] button{
  background:#6366F1!important;color:#fff!important;border:none!important;
  border-radius:8px!important;font-weight:600!important;font-size:.83rem!important;
  padding:6px 18px!important;transition:all .2s!important}
[data-testid="stFileUploadDropzone"] button:hover{background:#4F46E5!important}
[data-testid="stFileUploaderFile"]{
  background:#EEF2FF!important;border:1px solid #C7D2FE!important;
  border-radius:8px!important;padding:4px 10px!important;margin-top:6px!important}
[data-testid="stFileUploaderFile"] *{color:#4F46E5!important;font-size:.82rem!important}
/* ── Markdown — dark readable text everywhere ── */
.stMarkdown p{color:#1E293B!important;line-height:1.78!important;margin:.35rem 0!important}
.stMarkdown li{color:#1E293B!important;line-height:1.75!important;margin:.12rem 0!important}
.stMarkdown h1{color:#1E293B!important;font-size:1.5rem!important;font-weight:800!important;margin:.5rem 0 .4rem!important}
.stMarkdown h2{color:#1E293B!important;font-size:1.05rem!important;font-weight:700!important;
  margin:1.1rem 0 .4rem!important;padding-left:10px!important;border-left:3px solid #6366F1!important}
.stMarkdown h3{color:#1E293B!important;font-size:.95rem!important;font-weight:700!important;margin:.75rem 0 .3rem!important}
.stMarkdown strong{color:#1E293B!important;font-weight:700!important}
.stMarkdown em{color:#64748B!important}
.stMarkdown code{background:#EEF2FF!important;color:#6366F1!important;border-radius:4px!important;padding:1px 6px!important;font-size:.85em!important}
.stMarkdown blockquote{border-left:3px solid #6366F1!important;padding-left:.9rem!important;color:#64748B!important;margin:.5rem 0!important}
.stMarkdown ul,.stMarkdown ol{padding-left:1.4rem!important;margin:.3rem 0!important}
.stMarkdown a{color:#6366F1!important;text-decoration:none!important}
.stMarkdown a:hover{text-decoration:underline!important}
.stMarkdown hr{border-color:#E2E8F0!important;margin:1rem 0!important}
/* ── Number input ── */
[data-testid="stNumberInput"] input{
  background:#FFFFFF!important;border:1.5px solid #E2E8F0!important;
  border-radius:8px!important;color:#1E293B!important;font-size:.9rem!important}
[data-testid="stNumberInput"] button{color:#64748B!important;background:#F8FAFC!important;border-color:#E2E8F0!important}
/* ── Form container ── */
[data-testid="stForm"]{
  border:1.5px solid #E2E8F0!important;border-radius:14px!important;
  background:#FFFFFF!important;padding:1.4rem 1.5rem!important;
  box-shadow:0 1px 6px rgba(0,0,0,.04)!important}
/* ── Multiselect ── */
[data-testid="stMultiSelect"] div[data-baseweb="select"]{background:#FFFFFF!important;border-color:#E2E8F0!important}
[data-testid="stMultiSelect"] span[data-baseweb="tag"]{background:#EEF2FF!important;color:#4F46E5!important}
/* ── Alerts ── */
[data-testid="stAlert"]{border-radius:10px!important;padding:.75rem 1rem!important}
[data-testid="stAlert"] p{color:#1E293B!important;font-size:.86rem!important;margin:0!important}
/* ── Spinner ── */
[data-testid="stSpinner"] p{color:#6366F1!important;font-weight:600!important;font-size:.9rem!important}
/* ── Success / toast ── */
div[data-baseweb="notification"]{background:#ECFDF5!important;border:1px solid #6EE7B7!important;border-radius:10px!important}
/* ── Radio buttons ── */
[data-testid="stRadio"] div[role="radiogroup"] label{color:#1E293B!important}
/* ── Sidebar polish ── */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:1px!important}
/* ── Column gap tightening ── */
[data-testid="column"]{min-width:0!important}
/* ── Color picker ── */
[data-testid="stColorPicker"] input{border-radius:8px!important;border:1.5px solid #E2E8F0!important;background:#fff!important}
/* ── Tooltip ── */
[data-testid="stTooltipContent"]{background:#1E293B!important;color:#fff!important;border-radius:8px!important;font-size:.8rem!important}
/* ── Selectbox dropdown list ── */
[data-baseweb="popover"] [role="option"]{color:#1E293B!important;font-size:.85rem!important}
[data-baseweb="popover"] [role="option"]:hover{background:#EEF2FF!important}
[data-baseweb="popover"] [aria-selected="true"]{background:#EEF2FF!important;color:#6366F1!important}
/* ── Caption / small text ── */
.stMarkdown small,small{color:#64748B!important}
[data-testid="stCaptionContainer"]{color:#64748B!important;font-size:.78rem!important}
/* ── Table ── */
table{border-collapse:collapse!important}
/* ── Image ── */
[data-testid="stImage"]{border-radius:10px!important;overflow:hidden!important}
/* ── Scrollbar ── */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-thumb{background:#CBD5E1;border-radius:4px}
::-webkit-scrollbar-track{background:#F8FAFC}
/* ── Focus ring removal for non-keyboard ── */
button:focus:not(:focus-visible){outline:none!important;box-shadow:none!important}
</style>""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "Drafting":  ("#63B3ED","#0d2035"),
    "In Review": ("#F6AD55","#2d1e09"),
    "Submitted": ("#9F7AEA","#1e0d35"),
    "Awarded":   ("#68D391","#0a2018"),
    "Archived":  ("#718096","#1a1c22"),
}
SECTION_COLORS = {1:"#A78BFA",2:"#FB923C",3:"#60A5FA",4:"#34D399",5:"#F472B6",6:"#FBBF24",7:"#2DD4BF"}
SHORT_LABELS   = {1:"Who We Are",2:"The Problem",3:"Our Solution",
                  4:"What We'll Achieve",5:"Measuring It",6:"Why Trust Us",7:"The Budget"}

# ── Seed data ──────────────────────────────────────────────────────────────────
_SEED_PROPOSALS = [
    {"name":"TechForward Youth Initiative","funder":"Horizon Community Foundation","amount":"$50,000",
     "status":"Drafting", "deadline":"Jun 15, 2026","compliance":84,
     "notes":"Complete budget narrative section before Jun 10."},
    {"name":"Digital Literacy Expansion",  "funder":"Gates Foundation",           "amount":"$75,000",
     "status":"In Review","deadline":"May 30, 2026","compliance":91,
     "notes":"Awaiting reviewer feedback from Priya — follow up May 20."},
    {"name":"Broadband Access Initiative", "funder":"FCC E-Rate",                 "amount":"$120,000",
     "status":"Submitted","deadline":"Apr 1, 2026", "compliance":98,
     "notes":"Submitted Apr 1. Decision expected by Jul 1."},
    {"name":"AI Literacy for Seniors",     "funder":"AARP Foundation",            "amount":"$35,000",
     "status":"Awarded",  "deadline":"Mar 15, 2026","compliance":96,
     "notes":"Award confirmed. Send thank-you letter and set up reporting schedule."},
    {"name":"Career Pathways Program",     "funder":"JPMorgan Chase",             "amount":"$60,000",
     "status":"Drafting", "deadline":"Jul 10, 2026","compliance":72,
     "notes":"Add 3 data citations and partner letters of support."},
]
_SEED_PROGRAMS = [
    {"id":1,"name":"TechForward Youth Coding Academy","target":"Youth ages 13–18",
     "location":"Washington, DC — Wards 7 & 8","budget":"$180,000/year",
     "outcomes":"200 students/yr · 78% complete · 45% continue STEM",
     "description":"A 16-week after-school coding bootcamp for students ages 13–18 in underserved DC neighborhoods. Participants learn Python, web development, and data literacy. We partner with Anacostia High School and DCPS. 85% of graduates report increased confidence in STEM fields."},
    {"id":2,"name":"Digital Skills for Seniors","target":"Adults 60+",
     "location":"Metro DC & Maryland suburbs","budget":"$95,000/year",
     "outcomes":"350 seniors/yr · 91% improved confidence · 67% now use telehealth",
     "description":"A free 8-week digital literacy program for adults 60+ covering smartphones, video calling, online banking, and scam awareness. Delivered at 12 senior centers. Curriculum is bilingual (English/Spanish)."},
    {"id":3,"name":"Workforce Ready: Tech Careers","target":"Adults 25–45 seeking employment",
     "location":"Greater Baltimore–DC corridor","budget":"$240,000/year",
     "outcomes":"120 participants/yr · 72% job placement · avg salary $38,500",
     "description":"An intensive 12-week workforce training placing adults into entry-level tech roles. Includes job placement support and 90-day post-placement coaching. Partners include Booz Allen, SAIC, and Accenture."},
]
_SEED_CITATIONS = [
    {"id":1,"source":"Pew Research Center","year":2023,"stat":"15% of U.S. adults do not use the internet","tags":["digital equity","access"]},
    {"id":2,"source":"NTIA","year":2022,"stat":"Rural households are 3x less likely to have broadband","tags":["broadband","rural"]},
    {"id":3,"source":"McKinsey Global Institute","year":2023,"stat":"Digital skills gap costs the U.S. economy $1.2T annually","tags":["workforce","economy"]},
    {"id":4,"source":"Common Sense Media","year":2022,"stat":"58% of low-income students lack reliable home internet","tags":["youth","education"]},
    {"id":5,"source":"Urban Institute","year":2023,"stat":"Low-broadband neighborhoods have 2x unemployment rates","tags":["broadband","equity"]},
]
_SEED_FACTS = [
    {"id":1,"claim":"15% of DC residents lack home internet access","status":"Verified","source":"Pew Research 2023","note":""},
    {"id":2,"claim":"Our program serves 200 students annually","status":"Verified","source":"Internal program data","note":""},
    {"id":3,"claim":"78% of participants complete all 16 weeks","status":"Verified","source":"2023 Annual Report","note":""},
    {"id":4,"claim":"Broadband costs decreased 40% since 2018","status":"Needs Review","source":"Unverified","note":"Check FCC broadband pricing report"},
    {"id":5,"claim":"Digital literacy increases income by $8,000/year","status":"Flagged","source":"Could not verify","note":"Remove or find a verified source"},
]
_SEED_TEAM = [
    {"name":"Maya Johnson",  "role":"Executive Director",  "email":"m.johnson@org.org","access":"Admin",   "status":"Active"},
    {"name":"Carlos Rivera", "role":"Development Director","email":"c.rivera@org.org", "access":"Editor",  "status":"Active"},
    {"name":"Priya Nair",    "role":"Program Officer",     "email":"p.nair@org.org",   "access":"Reviewer","status":"Active"},
    {"name":"James Wilson",  "role":"Finance Manager",     "email":"j.wilson@org.org", "access":"Viewer",  "status":"Active"},
]
_SEED_AUDIT = [
    {"time":"Today 2:14pm",      "user":"Carlos Rivera","action":"Exported proposal as .txt",         "item":"TechForward Youth Initiative"},
    {"time":"Today 10:31am",     "user":"Maya Johnson", "action":"Updated organization profile",      "item":"DiTi Foundation"},
    {"time":"Yesterday 4:07pm",  "user":"Priya Nair",   "action":"Left review comment",               "item":"Digital Literacy Expansion"},
    {"time":"Yesterday 11:22am", "user":"Carlos Rivera","action":"Generated new proposal draft",      "item":"Career Pathways Program"},
    {"time":"May 6 3:45pm",      "user":"James Wilson", "action":"Viewed budget narrative",           "item":"Broadband Access Initiative"},
    {"time":"May 5 9:00am",      "user":"Maya Johnson", "action":"Submitted proposal to funder",      "item":"Broadband Access Initiative"},
]

# ── Session state ─────────────────────────────────────────────────────────────
_DEFAULTS = {
    "screen":"login","user_email":"","is_demo":False,"nav_item":"dashboard",
    "sections":{},"full_draft":"","rfp_saved":"","prog_saved":"",
    "pending_regen":None,"regen_log":[],"settings_snap":{},
    "rfp_analysis":"","rfp_analysis_input":"",
    "org_settings":{},
    "wizard_step":1,"wizard_data":{},
    "brand_kit":{"primary":"#6366F1","accent":"#8B5CF6","font":"Georgia","template":"Professional"},
}
for _k,_v in _DEFAULTS.items():
    if _k not in st.session_state: st.session_state[_k]=_v

for _wk in ("rfp_area","prog_area","api_override","rfp_analyzer_text","wiz_rfp_text"):
    if _wk not in st.session_state: st.session_state[_wk]=""

if "proposals" not in st.session_state: st.session_state.proposals = [dict(p) for p in _SEED_PROPOSALS]
if "programs"  not in st.session_state: st.session_state.programs  = list(_SEED_PROGRAMS)
if "citations" not in st.session_state: st.session_state.citations = list(_SEED_CITATIONS)
if "facts"     not in st.session_state: st.session_state.facts     = list(_SEED_FACTS)
if "team"      not in st.session_state: st.session_state.team      = list(_SEED_TEAM)
if "audit_log" not in st.session_state: st.session_state.audit_log = list(_SEED_AUDIT)

# ── Helpers ───────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))

def _read(path):
    try:
        with open(path,encoding="utf-8") as f: return f.read()
    except Exception: return ""

def parse_sections(draft):
    result={}
    for num,name in SECTION_DEFS:
        m=re.compile(rf"##\s*{num}\.\s*{re.escape(name)}(.*?)(?=\n##\s*\d+\.|\Z)",re.DOTALL|re.IGNORECASE).search(draft)
        if m: result[num]={"name":name,"content":f"## {num}. {name}\n\n{m.group(1).strip()}"}
    return result

def rebuild_draft(sections):
    return "\n\n---\n\n".join(sections[n]["content"] for n in sorted(sections))

def _copy_btn(text,uid,label="📋 Copy",color="#6366F1"):
    safe=text.replace("\\","\\\\").replace("`","\\`").replace("${","\\${")
    return (f'<button id="cb_{uid}" style="background:{color};color:#fff;border:none;'
            'padding:7px 16px;border-radius:8px;cursor:pointer;font-weight:700;font-size:12.5px;'
            'font-family:system-ui,-apple-system,sans-serif;"'
            f' onclick="navigator.clipboard.writeText(`{safe}`).then(()=>{{'
            f'var b=document.getElementById(\'cb_{uid}\');b.textContent=\'✓ Copied!\';'
            f"b.style.background='#059669';setTimeout(()=>{{b.textContent='{label}';"
            f"b.style.background='{color}';}},2000)}}).catch(()=>alert('Copy manually.'));"
            f'">{label}</button>')

def compute_alignment(rfp,proposal):
    if not rfp or not proposal: return 0
    stop={'about','above','after','again','their','there','these','which','while','would',
          'could','should','where','other','those','under','until','before','include',
          'program','nonprofit','community','organization','provide','support','service',
          'funding','grant','proposal','foundation','between','through','during'}
    rw=set(re.findall(r'\b[a-z]{5,}\b',rfp.lower()))-stop
    pw=set(re.findall(r'\b[a-z]{5,}\b',proposal.lower()))-stop
    if not rw: return 85
    return max(62,min(97,int(len(rw&pw)/len(rw)*160)))

def _resolved_api_key():
    return st.session_state.get("api_override","").strip() or os.getenv("ANTHROPIC_API_KEY","")

def _section_badge(num,label):
    c=SECTION_COLORS.get(num,"#6366F1")
    return (f"<div style='display:inline-flex;align-items:center;gap:8px;background:{c}22;"
            f"border:1px solid {c}55;border-radius:20px;padding:4px 14px;margin-bottom:12px;'>"
            f"<span style='width:8px;height:8px;border-radius:50%;background:{c};display:inline-block;'></span>"
            f"<span style='color:{c};font-size:.78rem;font-weight:800;text-transform:uppercase;"
            f"letter-spacing:.06em;'>{label}</span></div>")

def _h2(title,sub=""):
    if st.session_state.get("is_demo"):
        st.markdown("<div style='background:#FFFBEB;border:1px solid #FCD34D;border-radius:8px;"
                    "padding:.4rem .9rem;margin-bottom:.6rem;display:inline-flex;align-items:center;gap:6px;'>"
                    "<span style='font-size:.85rem;'>🎬</span>"
                    "<span style='color:#92400E;font-size:.74rem;font-weight:600;'>"
                    "Demo Mode — sample data only</span></div>",unsafe_allow_html=True)
    sub_html=(f"<p style='color:#64748B;font-size:.9rem;margin:0 0 1.2rem;'>{sub}</p>"
              if sub else "<div style='height:.6rem;'></div>")
    st.markdown(f"<h2 style='color:#1E293B;font-size:1.45rem;font-weight:900;margin-bottom:4px;'>"
                f"{title}</h2>{sub_html}",unsafe_allow_html=True)

def _extract_file_text(f):
    if f is None: return ""
    if f.name.lower().endswith(".pdf"):
        try:
            import pdfplumber
            with pdfplumber.open(f) as pdf: return "\n".join(p.extract_text() or "" for p in pdf.pages)
        except ImportError: pass
        try:
            from pypdf import PdfReader
            return "\n".join(p.extract_text() or "" for p in PdfReader(f).pages)
        except ImportError: pass
        return ""
    return f.read().decode("utf-8",errors="ignore")

def _make_html(content):
    lines=content.split("\n"); out=[]
    for line in lines:
        if line.startswith("## "): out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "): out.append(f"<h1>{line[2:]}</h1>")
        elif line.strip()=="---": out.append("<hr>")
        elif line.strip(): out.append(f"<p>{line}</p>")
    today=datetime.date.today().strftime("%B %d, %Y")
    return (f'<!DOCTYPE html><html><head><meta charset="utf-8"><title>Grant Proposal</title>'
            f'<style>body{{font-family:Georgia,serif;max-width:820px;margin:50px auto;'
            f'line-height:1.8;color:#1a1a2e;padding:0 24px}}'
            f'h1{{color:#1a1a2e;font-size:1.8rem;border-bottom:3px solid #6366F1;padding-bottom:10px}}'
            f'h2{{color:#312e81;font-size:1.25rem;margin-top:2rem;border-left:4px solid #6366F1;padding-left:12px}}'
            f'p{{color:#374151;margin:.8rem 0}}hr{{border:1px solid #e5e7eb;margin:2rem 0}}'
            f'</style></head><body><h1>Grant Proposal</h1>{"".join(out)}'
            f'<hr><p style="color:#9ca3af;font-size:.8rem;text-align:center;">'
            f'Generated with MissionBridge AI · {today}</p></body></html>')

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""<style>
    section[data-testid="stSidebar"]{display:none!important}
    button[data-testid="collapsedControl"]{display:none!important}
    .block-container{padding-top:4rem!important}
    </style>""",unsafe_allow_html=True)
    _,center,_=st.columns([1,1.55,1])
    with center:
        st.markdown("""<div style="text-align:center;margin-bottom:2rem;">
        <div style="display:inline-flex;align-items:center;justify-content:center;
                    width:72px;height:72px;background:linear-gradient(135deg,#6366F1,#8B5CF6);
                    border-radius:20px;font-size:2.4rem;margin-bottom:1rem;
                    box-shadow:0 10px 28px rgba(99,102,241,.35);">🌱</div>
        <h1 style="color:#1E293B;font-size:2.1rem;font-weight:900;margin:0 0 8px;letter-spacing:-.04em;">
          MissionBridge AI</h1>
        <p style="color:#64748B;font-size:.95rem;margin:0 0 .5rem;">
          Write better grant proposals, faster.</p>
        <div style="display:inline-flex;gap:6px;flex-wrap:wrap;justify-content:center;">
          <span style="background:#EEF2FF;color:#6366F1;border-radius:20px;padding:2px 10px;font-size:.72rem;font-weight:700;">AI-Powered ⚡</span>
          <span style="background:#ECFDF5;color:#059669;border-radius:20px;padding:2px 10px;font-size:.72rem;font-weight:700;">Compliance Ready ✅</span>
          <span style="background:#FFFBEB;color:#D97706;border-radius:20px;padding:2px 10px;font-size:.72rem;font-weight:700;">Export-Ready 📤</span>
        </div>
        </div>""",unsafe_allow_html=True)
        st.markdown("<div style='background:#FFFFFF;border:1.5px solid #E2E8F0;border-radius:16px;"
                    "padding:2rem 2.25rem 1.75rem;box-shadow:0 4px 24px rgba(0,0,0,.07);'>",unsafe_allow_html=True)
        st.markdown("<p style='color:#1E293B;font-weight:700;font-size:.97rem;margin:0 0 1.1rem;'>"
                    "Welcome back — let's get to work.</p>",unsafe_allow_html=True)
        email   =st.text_input("Your email address",placeholder="you@yourorg.org",key="login_email")
        password=st.text_input("Your password",type="password",placeholder="••••••••",key="login_password")
        st.markdown("<div style='height:.55rem;'></div>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("Sign In",type="primary",use_container_width=True,key="btn_signin"):
                if email.strip():
                    st.session_state.update(user_email=email.strip(),is_demo=False,screen="app",nav_item="dashboard")
                    st.rerun()
                else: st.error("Please enter your email address.")
        with c2:
            if st.button("🎬  Try the Demo",type="primary",use_container_width=True,key="btn_demo"):
                st.session_state.update(user_email="demo@missionbridge.ai",is_demo=True,screen="app",nav_item="dashboard")
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;color:#94A3B8;font-size:.74rem;margin-top:1rem;'>"
                    "🎬 Demo: click <b>Try the Demo</b> — no account needed · Nothing stored externally</p>",unsafe_allow_html=True)
        st.markdown("<div style='height:1.5rem;'></div>",unsafe_allow_html=True)
        st.markdown("""<div style="text-align:center;">
          <div style="color:#94A3B8;font-size:.68rem;font-weight:800;text-transform:uppercase;
                      letter-spacing:.1em;margin-bottom:1.2rem;">How it works in 3 steps</div>
          <div style="display:flex;justify-content:center;gap:1.4rem;flex-wrap:wrap;align-items:flex-start;">
            <div style="text-align:center;max-width:130px;">
              <div style="width:40px;height:40px;border-radius:50%;background:#EEF2FF;
                          display:inline-flex;align-items:center;justify-content:center;
                          font-size:1.25rem;margin-bottom:.5rem;">📋</div>
              <div style="color:#1E293B;font-size:.76rem;font-weight:700;">Paste your RFP</div>
              <div style="color:#94A3B8;font-size:.7rem;margin-top:2px;line-height:1.4;">
                Drop in any funder's grant guidelines</div>
            </div>
            <div style="color:#CBD5E1;font-size:1.2rem;padding-top:.6rem;">→</div>
            <div style="text-align:center;max-width:130px;">
              <div style="width:40px;height:40px;border-radius:50%;background:#ECFDF5;
                          display:inline-flex;align-items:center;justify-content:center;
                          font-size:1.25rem;margin-bottom:.5rem;">🏢</div>
              <div style="color:#1E293B;font-size:.76rem;font-weight:700;">Add your program</div>
              <div style="color:#94A3B8;font-size:.7rem;margin-top:2px;line-height:1.4;">
                Tell us who you serve and what you do</div>
            </div>
            <div style="color:#CBD5E1;font-size:1.2rem;padding-top:.6rem;">→</div>
            <div style="text-align:center;max-width:130px;">
              <div style="width:40px;height:40px;border-radius:50%;background:#F5F3FF;
                          display:inline-flex;align-items:center;justify-content:center;
                          font-size:1.25rem;margin-bottom:.5rem;">✍️</div>
              <div style="color:#1E293B;font-size:.76rem;font-weight:700;">Get your draft</div>
              <div style="color:#94A3B8;font-size:.7rem;margin-top:2px;line-height:1.4;">
                Full 7-section proposal in ~30 seconds</div>
            </div>
          </div>
        </div>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR NAV
# ══════════════════════════════════════════════════════════════════════════════
def show_sidebar_nav():
    with st.sidebar:
        st.markdown("<div style='padding:1rem .85rem .9rem;border-bottom:1.5px solid #F1F5F9;margin-bottom:.25rem;'>"
                    "<div style='display:flex;align-items:center;gap:10px;'>"
                    "<div style='background:linear-gradient(135deg,#6366F1,#8B5CF6);border-radius:10px;"
                    "width:34px;height:34px;display:flex;align-items:center;justify-content:center;"
                    "font-size:1.2rem;flex-shrink:0;"
                    "box-shadow:0 3px 10px rgba(99,102,241,.35);'>🌱</div>"
                    "<div>"
                    "<div style='color:#1E293B;font-size:.93rem;font-weight:800;letter-spacing:-.02em;"
                    "line-height:1.2;'>MissionBridge AI</div>"
                    "<div style='color:#94A3B8;font-size:.64rem;margin-top:1px;letter-spacing:.01em;'>"
                    "Grant Intelligence Platform</div>"
                    "</div></div>"
                    "</div>",unsafe_allow_html=True)
        active=st.session_state.nav_item

        def _btn(key,icon,label):
            if active==key:
                st.markdown(f"<div style='background:#EEF2FF;border-left:3px solid #6366F1;"
                            f"border-radius:0 8px 8px 0;padding:.44rem .7rem;margin-bottom:1px;"
                            f"color:#4F46E5;font-size:.82rem;font-weight:700;display:flex;"
                            f"align-items:center;gap:6px;'>{icon}&nbsp;{label}</div>",
                            unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {label}",key=f"nav_{key}",use_container_width=True):
                    st.session_state.nav_item=key; st.rerun()

        def _grp(label):
            st.markdown(f"<div style='color:#94A3B8;font-size:.63rem;font-weight:800;text-transform:uppercase;"
                        f"letter-spacing:.1em;padding:.7rem .7rem .18rem;'>{label}</div>",unsafe_allow_html=True)

        _grp("WORKSPACE")
        _btn("dashboard","📊","Dashboard")
        _btn("wizard","🪄","New Proposal")
        _btn("workspace","✍️","Proposal Workspace")

        _grp("GRANT TOOLS")
        _btn("rfp","🔍","RFP Analyzer")
        _btn("facts","✅","Fact Verification")
        _btn("citations","📚","Citation Library")

        _grp("ORGANIZATION")
        _btn("settings","🏢","Organization Profile")
        _btn("programs","🎯","Program Library")
        _btn("brand","🎨","Brand Kit")

        _grp("PRODUCTION")
        _btn("export","📤","Export Center")
        _btn("team","👥","Team & Sharing")
        _btn("admin","⚙️","Security & Admin")

        _grp("INSIGHTS")
        _btn("analytics","📈","Analytics")
        _btn("research","💡","Writing Tips")
        _btn("proposals","📋","All Proposals")

        st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#F1F5F9;margin:.3rem 0;'>",unsafe_allow_html=True)
        email=st.session_state.user_email
        raw=email.split("@")[0]
        initials="".join(p[0].upper() for p in raw.split(".")[:2]) if raw else "DM"
        role="Demo Mode" if st.session_state.is_demo else "Admin"
        st.markdown(f"<div style='display:flex;align-items:center;gap:9px;padding:.3rem .5rem;'>"
                    f"<div style='background:linear-gradient(135deg,#6366F1,#8B5CF6);color:#fff;"
                    f"width:30px;height:30px;border-radius:50%;display:flex;align-items:center;"
                    f"justify-content:center;font-weight:800;font-size:.72rem;flex-shrink:0;'>{initials}</div>"
                    f"<div style='overflow:hidden;'>"
                    f"<div style='color:#1E293B;font-size:.76rem;font-weight:600;white-space:nowrap;"
                    f"overflow:hidden;text-overflow:ellipsis;max-width:145px;'>{email}</div>"
                    f"<div style='color:#94A3B8;font-size:.66rem;'>{role}</div></div></div>",
                    unsafe_allow_html=True)
        st.markdown("<div style='height:4px;'></div>",unsafe_allow_html=True)
        if st.button("Sign Out",key="sign_out",use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
def show_dashboard():
    email=st.session_state.user_email
    first=email.split("@")[0].split(".")[0].capitalize()

    # ── Demo mode banner ───────────────────────────────────────────────────────
    if st.session_state.is_demo:
        st.markdown("""<div style="background:#FFFBEB;border:1.5px solid #FCD34D;border-radius:10px;
        padding:.6rem 1.1rem;margin-bottom:.7rem;display:flex;align-items:center;gap:10px;">
          <span style="font-size:1.1rem;">🎬</span>
          <span style="color:#92400E;font-size:.83rem;font-weight:600;">
            <b>Demo Mode</b> — Explore all features. Data is sample-only and resets on sign-out.</span>
        </div>""",unsafe_allow_html=True)

    # ── Time-aware header banner ───────────────────────────────────────────────
    _hour=datetime.datetime.now().hour
    _greet="Good morning" if _hour<12 else "Good afternoon" if _hour<17 else "Good evening"
    st.markdown(f"""<div style="background:linear-gradient(135deg,#6366F1 0%,#8B5CF6 100%);
    border-radius:16px;padding:1.5rem 2rem 1.4rem;margin-bottom:.9rem;
    box-shadow:0 4px 20px rgba(99,102,241,.2);">
      <h1 style="color:#fff;font-size:1.65rem;font-weight:900;margin:0 0 5px;letter-spacing:-.02em;">
        {_greet}, {first}! 👋</h1>
      <p style="color:rgba(255,255,255,.85);font-size:.91rem;margin:0;">
        Grant proposal command center for <strong>BrightPath Community Learning Initiative</strong></p>
    </div>""",unsafe_allow_html=True)

    # ── Quick action buttons ───────────────────────────────────────────────────
    qa1,qa2,qa3,_=st.columns([1.3,1.3,1.8,3.6])
    with qa1:
        if st.button("🪄  New Proposal",type="primary",use_container_width=True,key="dash_new_prop"):
            st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={}); st.rerun()
    with qa2:
        if st.button("📄  Upload RFP",use_container_width=True,key="dash_upload_rfp"):
            st.session_state.nav_item="rfp"; st.rerun()
    with qa3:
        if st.button("✅  Run Compliance Check",use_container_width=True,key="dash_compliance"):
            st.session_state.nav_item="facts"; st.rerun()

    st.markdown("<div style='height:.55rem;'></div>",unsafe_allow_html=True)

    # ── Search + global new ────────────────────────────────────────────────────
    sc,nc=st.columns([5,1])
    with sc:
        _sv=st.text_input("",placeholder="🔍  Search proposals, funders, citations, RFPs...",
                           key="dash_search",label_visibility="collapsed")
        if _sv:
            st.markdown(f"<div style='background:#EEF2FF;border-radius:8px;padding:.4rem .9rem;"
                        f"margin-top:3px;'><span style='color:#4F46E5;font-size:.81rem;'>"
                        f"🔍 Searching for <b>\"{_sv}\"</b> — full-text search across all proposals, "
                        f"citations, and funders launching soon.</span></div>",unsafe_allow_html=True)
    with nc:
        if st.button("＋  New",type="primary",use_container_width=True,key="dash_plus_new"):
            st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={}); st.rerun()

    # ── Recommended Next Actions ───────────────────────────────────────────────
    st.markdown("""<div style="background:#fff;border:1.5px solid #C7D2FE;border-left:4px solid #6366F1;
    border-radius:12px;padding:.8rem 1.4rem .5rem;margin:.6rem 0 .4rem;
    box-shadow:0 2px 8px rgba(99,102,241,.07);">
      <div style="color:#1E293B;font-size:.87rem;font-weight:800;margin-bottom:.5rem;">
        🎯 &nbsp;Recommended Next Actions</div>
    </div>""",unsafe_allow_html=True)
    _na1,_na2=st.columns(2)
    with _na1:
        if st.button("⚠️  Review 5 fact-check warnings",use_container_width=True,key="na_facts"):
            st.session_state.nav_item="facts"; st.rerun()
        if st.button("👤  Send draft to Finance Reviewer",use_container_width=True,key="na_team"):
            st.session_state.nav_item="team"; st.rerun()
    with _na2:
        if st.button("📝  Complete Budget Narrative section",use_container_width=True,key="na_workspace"):
            st.session_state.nav_item="workspace"; st.rerun()
        if st.button("📅  Export package before June 14",use_container_width=True,key="na_export"):
            st.session_state.nav_item="export"; st.rerun()
    st.markdown("<div style='height:.4rem;'></div>",unsafe_allow_html=True)

    # ── Metric cards ──────────────────────────────────────────────────────────
    _active=sum(1 for p in _SEED_PROPOSALS if p["status"] in ("Drafting","In Review"))
    _submitted=sum(1 for p in _SEED_PROPOSALS if p["status"]=="Submitted")
    _METRICS=[
        ("#6366F1","#EEF2FF","📋",str(_active),"Active Proposals","2 due within 30 days","proposals","View proposals →"),
        ("#10B981","#ECFDF5","📤",str(_submitted),"Submitted","this month","proposals_sub","View submitted →"),
        ("#F59E0B","#FFFBEB","🏆","67%","Win Rate","+5% vs last quarter","analytics","View analytics →"),
        ("#8B5CF6","#F5F3FF","⚡","28s","Time to Draft","vs 20–40 hrs manually","wizard_new","Start writing →"),
    ]
    for col,(accent,bg,icon,val,label,sub,nav,link) in zip(st.columns(4),_METRICS):
        with col:
            st.markdown(f"""<div class="mb-card" style="background:{bg};border:1.5px solid {accent}22;
            border-top:3px solid {accent};border-radius:12px;padding:1rem 1.1rem .45rem;
            box-shadow:0 2px 8px rgba(0,0,0,.04);">
              <div style="font-size:1.25rem;margin-bottom:4px;">{icon}</div>
              <div style="color:#64748B;font-size:.67rem;font-weight:700;text-transform:uppercase;
                          letter-spacing:.07em;margin-bottom:2px;">{label}</div>
              <div style="color:#1E293B;font-size:1.65rem;font-weight:900;line-height:1.1;margin-bottom:2px;">{val}</div>
              <div style="color:#64748B;font-size:.73rem;margin-bottom:7px;">{sub}</div>
            </div>""",unsafe_allow_html=True)
            if st.button(link,key=f"mcard_{nav}",use_container_width=True):
                if nav=="proposals_sub":
                    st.session_state.proposals_filter="Submitted"
                    st.session_state.nav_item="proposals"
                elif nav=="wizard_new":
                    st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={})
                else:
                    st.session_state.nav_item=nav
                st.rerun()

    st.markdown("<div style='height:.55rem;'></div>",unsafe_allow_html=True)

    # ── Pipeline status (computed from seed data) ──────────────────────────────
    _pc={p["status"]:0 for p in _SEED_PROPOSALS}
    for _p in _SEED_PROPOSALS: _pc[_p["status"]]=_pc.get(_p["status"],0)+1
    _nreview=sum(1 for f in st.session_state.facts if f["status"]!="Verified")
    _PIPELINE=[
        ("Drafting",  str(_pc.get("Drafting",0)),  "#6366F1","#EEF2FF"),
        ("In Review", str(_pc.get("In Review",0)), "#F59E0B","#FFFBEB"),
        ("Compliance",str(_nreview)+" flags",       "#EF4444","#FEF2F2"),
        ("Export Ready","1",                        "#10B981","#ECFDF5"),
        ("Submitted", str(_pc.get("Submitted",0)), "#94A3B8","#F8FAFC"),
    ]
    ph=("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
        "padding:.85rem 1.2rem;margin-bottom:.9rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
        "<div style='color:#1E293B;font-size:.83rem;font-weight:700;margin-bottom:.55rem;'>"
        "📊 &nbsp;Proposal Pipeline</div><div style='display:flex;gap:.6rem;flex-wrap:wrap;'>")
    for stage,count,color,bg in _PIPELINE:
        ph+=(f"<div style='flex:1;min-width:88px;background:{bg};border:1.5px solid {color}30;"
             f"border-radius:10px;padding:.55rem .7rem;text-align:center;'>"
             f"<div style='color:{color};font-size:1.45rem;font-weight:900;'>{count}</div>"
             f"<div style='color:#64748B;font-size:.64rem;font-weight:700;text-transform:uppercase;"
             f"letter-spacing:.04em;'>{stage}</div></div>")
    ph+="</div></div>"
    st.markdown(ph,unsafe_allow_html=True)

    # ── Two-column layout ──────────────────────────────────────────────────────
    left,right=st.columns([3,2])

    with left:
        # Active Proposals table
        _SL={
            "Drafting":     ("#6366F1","#EEF2FF"),
            "In Review":    ("#F59E0B","#FFFBEB"),
            "Submitted":    ("#8B5CF6","#F5F3FF"),
            "Awarded":      ("#10B981","#ECFDF5"),
            "Export Ready": ("#10B981","#ECFDF5"),
        }
        _AP=[
            {"name":"TechForward Youth Initiative", "funder":"Horizon Foundation","dl":"Jun 15","cs":84,"status":"Drafting",  "next":"Complete budget"},
            {"name":"Digital Literacy Expansion",   "funder":"Gates Foundation",  "dl":"May 30","cs":91,"status":"In Review","next":"Await reviewer"},
            {"name":"Career Pathways Program",      "funder":"JPMorgan Chase",    "dl":"Jul 10","cs":72,"status":"Drafting",  "next":"Add citations"},
            {"name":"Broadband Access Initiative",  "funder":"FCC E-Rate",        "dl":"Apr 1", "cs":98,"status":"Submitted","next":"Awaiting decision"},
        ]
        th="padding:9px 14px;color:#94A3B8;font-size:.65rem;font-weight:700;text-align:left;text-transform:uppercase;letter-spacing:.07em;background:#F8FAFC;border-bottom:1px solid #E2E8F0;"
        rows=""
        for p in _AP:
            fc,fbg=_SL.get(p["status"],("#94A3B8","#F8FAFC"))
            cc_color="#10B981" if p["cs"]>=85 else "#F59E0B" if p["cs"]>=70 else "#EF4444"
            badge=(f"<span style='background:{fbg};color:{fc};border:1px solid {fc}44;"
                   f"border-radius:20px;padding:2px 10px;font-size:.66rem;font-weight:700;'>{p['status']}</span>")
            rows+=(f"<tr style='border-bottom:1px solid #F1F5F9;'>"
                   f"<td style='padding:10px 14px;color:#1E293B;font-weight:600;font-size:.82rem;'>{p['name']}</td>"
                   f"<td style='padding:10px 14px;color:#64748B;font-size:.8rem;'>{p['funder']}</td>"
                   f"<td style='padding:10px 14px;color:#64748B;font-size:.8rem;'>{p['dl']}</td>"
                   f"<td style='padding:10px 14px;color:{cc_color};font-weight:700;font-size:.82rem;'>{p['cs']}%</td>"
                   f"<td style='padding:10px 14px;'>{badge}</td>"
                   f"<td style='padding:10px 14px;color:#6366F1;font-size:.78rem;font-weight:500;'>{p['next']}</td>"
                   "</tr>")
        heads="".join(f"<th style='{th}'>{h}</th>"
                      for h in ["Proposal","Funder","Deadline","Compliance","Status","Next Action"])
        st.markdown(f"""<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;
        overflow:hidden;margin-bottom:.9rem;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="padding:.8rem 1.1rem .5rem;border-bottom:1px solid #F1F5F9;
                      color:#1E293B;font-size:.87rem;font-weight:700;">Active Proposals</div>
          <table style="width:100%;border-collapse:collapse;">
            <thead><tr>{heads}</tr></thead><tbody>{rows}</tbody>
          </table>
        </div>""",unsafe_allow_html=True)

        # RFPs Awaiting Analysis
        st.markdown("""<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;
        padding:1.1rem 1.3rem .8rem;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="color:#1E293B;font-size:.87rem;font-weight:700;margin-bottom:.7rem;">
            📄 &nbsp;RFPs Awaiting Analysis</div>
          <div style="text-align:center;padding:.8rem 0 .5rem;">
            <div style="font-size:2rem;margin-bottom:.45rem;">📭</div>
            <div style="color:#64748B;font-size:.83rem;line-height:1.65;max-width:380px;margin:0 auto;">
              No RFPs awaiting analysis. Upload a funder guideline, paste an RFP, or add an
              application URL to begin a compliance review.
            </div>
          </div>
        </div>""",unsafe_allow_html=True)
        r1,r2,r3=st.columns(3)
        with r1:
            if st.button("📤 Upload RFP",use_container_width=True,key="dash_rfp_up"):
                st.session_state.nav_item="rfp"; st.rerun()
        with r2:
            if st.button("📋 Paste Guidelines",use_container_width=True,key="dash_rfp_paste"):
                st.session_state.nav_item="rfp"; st.rerun()
        with r3:
            if st.button("🔗 Add URL",use_container_width=True,key="dash_rfp_url"):
                st.session_state.nav_item="rfp"; st.rerun()

    with right:
        # Alerts
        st.markdown("""<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;
        padding:.95rem 1.15rem;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="color:#1E293B;font-size:.85rem;font-weight:700;margin-bottom:.6rem;">🔔 &nbsp;Alerts</div>
          <div style="border-left:3px solid #F59E0B;padding:.42rem .75rem;background:#FFFBEB;
                      border-radius:0 8px 8px 0;margin-bottom:.4rem;">
            <span style="color:#92400E;font-size:.78rem;font-weight:600;">
              ⚠️ 5 claims need verification before final export.</span>
          </div>
          <div style="border-left:3px solid #EF4444;padding:.42rem .75rem;background:#FEF2F2;
                      border-radius:0 8px 8px 0;margin-bottom:.4rem;">
            <span style="color:#991B1B;font-size:.78rem;font-weight:600;">
              📅 Digital Literacy Expansion due May 30</span>
          </div>
          <div style="border-left:3px solid #6366F1;padding:.42rem .75rem;background:#EEF2FF;
                      border-radius:0 8px 8px 0;">
            <span style="color:#3730A3;font-size:.78rem;font-weight:600;">
              💬 Priya left a review comment on your draft</span>
          </div>
        </div>""",unsafe_allow_html=True)
        if st.button("Review Claims",type="primary",use_container_width=True,key="dash_review_claims"):
            st.session_state.nav_item="facts"; st.rerun()

        st.markdown("<div style='height:.45rem;'></div>",unsafe_allow_html=True)

        # AI Usage
        st.markdown("""<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;
        padding:.95rem 1.15rem;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="color:#1E293B;font-size:.85rem;font-weight:700;margin-bottom:.6rem;">
            ⚡ &nbsp;AI Usage — May 2026</div>
          <div style="display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid #F1F5F9;">
            <span style="color:#64748B;font-size:.78rem;">Proposals generated</span>
            <span style="color:#1E293B;font-weight:700;font-size:.78rem;">8</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:.3rem 0;border-bottom:1px solid #F1F5F9;">
            <span style="color:#64748B;font-size:.78rem;">Sections regenerated</span>
            <span style="color:#1E293B;font-weight:700;font-size:.78rem;">14</span>
          </div>
          <div style="display:flex;justify-content:space-between;padding:.3rem 0;">
            <span style="color:#64748B;font-size:.78rem;">API calls this month</span>
            <span style="color:#1E293B;font-weight:700;font-size:.78rem;">22</span>
          </div>
        </div>""",unsafe_allow_html=True)

        # Compliance Trend
        st.markdown("""<div style="background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;
        padding:.95rem 1.15rem .65rem;margin-bottom:.4rem;box-shadow:0 1px 4px rgba(0,0,0,.04);">
          <div style="color:#1E293B;font-size:.85rem;font-weight:700;margin-bottom:.45rem;">
            📊 &nbsp;Compliance Trend</div>
          <div style="display:flex;justify-content:space-between;margin-bottom:5px;">
            <span style="color:#64748B;font-size:.75rem;">Portfolio avg score</span>
            <span style="color:#10B981;font-weight:800;font-size:.9rem;">84%</span>
          </div>
        </div>""",unsafe_allow_html=True)
        st.progress(0.84)

        st.markdown("<div style='height:.4rem;'></div>",unsafe_allow_html=True)

        # Recent Activity (4 max, no scroll)
        act_html=("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                  "padding:.95rem 1.15rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                  "<div style='color:#1E293B;font-size:.85rem;font-weight:700;margin-bottom:.6rem;'>"
                  "🕐 &nbsp;Recent Activity</div>")
        for entry in st.session_state.audit_log[:4]:
            act_html+=(f"<div style='border-bottom:1px solid #F1F5F9;padding:.4rem 0;'>"
                       f"<div style='color:#1E293B;font-size:.78rem;font-weight:600;'>{entry['action']}</div>"
                       f"<div style='color:#94A3B8;font-size:.69rem;margin-top:1px;'>"
                       f"{entry['user']} · {entry['time']}</div></div>")
        act_html+="</div>"
        st.markdown(act_html,unsafe_allow_html=True)
        if st.button("View full activity log →",use_container_width=True,key="dash_full_log"):
            st.session_state.nav_item="admin"; st.rerun()

    st.markdown("<div style='text-align:center;margin-top:2rem;padding-top:1rem;"
                "border-top:1px solid #F1F5F9;'>"
                "<span style='color:#CBD5E1;font-size:.7rem;'>"
                "MissionBridge AI &nbsp;·&nbsp; JHU Generative AI Capstone Project &nbsp;·&nbsp; "
                "Powered by Anthropic Claude Sonnet &nbsp;·&nbsp; "
                "Always reviewed by a human before submission."
                "</span></div>",unsafe_allow_html=True)

_STATUS_LIGHT={
    "Drafting":  ("#6366F1","#EEF2FF"),
    "In Review": ("#F59E0B","#FFFBEB"),
    "Submitted": ("#8B5CF6","#F5F3FF"),
    "Awarded":   ("#10B981","#ECFDF5"),
    "Archived":  ("#94A3B8","#F8FAFC"),
}

def _proposals_table(proposals):
    rows=""
    for p in proposals:
        color,bg=_STATUS_LIGHT.get(p["status"],("#94A3B8","#F8FAFC"))
        badge=(f"<span style='background:{bg};color:{color};border:1px solid {color}44;"
               f"border-radius:20px;padding:2px 10px;font-size:.68rem;font-weight:700;'>{p['status']}</span>")
        rows+=(f"<tr style='border-bottom:1px solid #F1F5F9;'>"
               f"<td style='padding:10px 14px;color:#1E293B;font-weight:600;font-size:.83rem;'>{p['name']}</td>"
               f"<td style='padding:10px 14px;color:#64748B;font-size:.8rem;'>{p['funder']}</td>"
               f"<td style='padding:10px 14px;color:#10B981;font-weight:700;font-size:.83rem;'>{p['amount']}</td>"
               f"<td style='padding:10px 14px;'>{badge}</td>"
               f"<td style='padding:10px 14px;color:#64748B;font-size:.8rem;'>{p['deadline']}</td></tr>")
    th="padding:9px 14px;color:#94A3B8;font-size:.67rem;font-weight:700;text-align:left;text-transform:uppercase;letter-spacing:.07em;background:#F8FAFC;border-bottom:1px solid #E2E8F0;"
    st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                f"overflow:hidden;margin-top:.5rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                f"<table style='width:100%;border-collapse:collapse;'><thead><tr>"
                +"".join(f"<th style='{th}'>{h}</th>"
                         for h in ["Proposal","Funder","Amount","Status","Deadline"])
                +f"</tr></thead><tbody>{rows}</tbody></table></div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  NEW PROPOSAL WIZARD
# ══════════════════════════════════════════════════════════════════════════════
def show_wizard():
    _h2("🪄 New Proposal Wizard","Six quick steps and we'll generate a polished first draft.")
    if st.session_state.is_demo and not st.session_state.wizard_data:
        st.session_state.wizard_data={
            "funder_name":"Horizon Community Foundation",
            "funder_type":"Private Foundation",
            "grant_amount":"$50,000",
            "deadline":"June 15, 2026",
        }
    step=st.session_state.wizard_step
    wd  =st.session_state.wizard_data

    STEPS=["Funder","RFP","Your Org","Program","Settings","Generate"]
    bar="<div style='display:flex;align-items:center;gap:4px;margin-bottom:1.6rem;flex-wrap:wrap;'>"
    for i,s in enumerate(STEPS,1):
        done=i<step; curr=i==step
        c="#10B981" if done else ("#6366F1" if curr else "#E2E8F0")
        tc="#fff" if (done or curr) else "#94A3B8"
        fc="#1E293B" if curr else ("#10B981" if done else "#94A3B8")
        fw="700" if curr else "500"
        bar+=(f"<div style='display:flex;align-items:center;gap:5px;'>"
              f"<div style='width:26px;height:26px;border-radius:50%;background:{c};"
              f"display:flex;align-items:center;justify-content:center;"
              f"font-size:.72rem;font-weight:800;color:{tc};flex-shrink:0;'>{'✓' if done else str(i)}</div>"
              f"<span style='color:{fc};font-size:.77rem;font-weight:{fw};'>{s}</span>"
              +(f"<div style='width:22px;height:1px;background:#E2E8F0;margin:0 2px;'></div>" if i<6 else "")
              +"</div>")
    bar+="</div>"
    st.markdown(bar,unsafe_allow_html=True)

    _,center,_=st.columns([.5,5,.5])
    with center:
        card="background:#fff;border:1.5px solid #E2E8F0;border-radius:14px;padding:1.8rem 2rem;box-shadow:0 2px 10px rgba(0,0,0,.05);"

        if step==1:
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 1 — Who is the funder?</p>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                st.text_input("Funder name",value=wd.get("funder_name",""),
                              placeholder="e.g. Horizon Community Foundation",key="wiz_funder_name")
                st.selectbox("Funder type",["Private Foundation","Government","Corporate","Community Fund"],
                             index=["Private Foundation","Government","Corporate","Community Fund"].index(
                                 wd.get("funder_type","Private Foundation")),key="wiz_funder_type")
            with c2:
                st.text_input("Grant amount / range",value=wd.get("grant_amount",""),
                              placeholder="e.g. $25,000–$75,000",key="wiz_grant_amount")
                st.text_input("Application deadline",value=wd.get("deadline",""),
                              placeholder="e.g. June 15, 2026",key="wiz_deadline")
            st.markdown("</div>",unsafe_allow_html=True)
            _,nc=st.columns([4,1])
            with nc:
                if st.button("Next →",type="primary",use_container_width=True,key="wiz_n1"):
                    st.session_state.wizard_data.update({
                        "funder_name":st.session_state.get("wiz_funder_name",""),
                        "funder_type":st.session_state.get("wiz_funder_type","Private Foundation"),
                        "grant_amount":st.session_state.get("wiz_grant_amount",""),
                        "deadline":st.session_state.get("wiz_deadline",""),
                    })
                    st.session_state.wizard_step=2; st.rerun()

        elif step==2:
            if "wiz_rfp_text" not in st.session_state:
                st.session_state["wiz_rfp_text"]=wd.get("rfp_text","")
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 2 — Paste or upload the funder's RFP</p>",unsafe_allow_html=True)
            uploaded=st.file_uploader("Upload RFP (.txt or .pdf)",type=["txt","pdf"],key="wiz_rfp_upload")
            if uploaded:
                txt=_extract_file_text(uploaded)
                if txt.strip(): st.session_state["wiz_rfp_text"]=txt
            st.text_area("RFP text",height=260,
                         placeholder="Paste the funder's request for proposals, grant guidelines…",
                         key="wiz_rfp_text",label_visibility="collapsed")
            st.markdown("</div>",unsafe_allow_html=True)
            bc,_,nc=st.columns([1,3,1])
            with bc:
                if st.button("← Back",use_container_width=True,key="wiz_b2"):
                    st.session_state.wizard_step=1; st.rerun()
            with nc:
                if st.button("Next →",type="primary",use_container_width=True,key="wiz_n2"):
                    st.session_state.wizard_data["rfp_text"]=st.session_state.get("wiz_rfp_text","")
                    st.session_state.wizard_step=3; st.rerun()

        elif step==3:
            saved=st.session_state.get("org_settings",{})
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 3 — Your organization</p>",unsafe_allow_html=True)
            st.text_input("Organization name",value=wd.get("org_name",saved.get("org_name","")),
                          placeholder="e.g. DiTi Foundation",key="wiz_org_name")
            st.text_area("Mission statement",value=wd.get("org_mission",saved.get("mission","")),height=100,
                         placeholder="One or two sentences describing your mission…",key="wiz_org_mission")
            st.markdown("</div>",unsafe_allow_html=True)
            bc,_,nc=st.columns([1,3,1])
            with bc:
                if st.button("← Back",use_container_width=True,key="wiz_b3"):
                    st.session_state.wizard_step=2; st.rerun()
            with nc:
                if st.button("Next →",type="primary",use_container_width=True,key="wiz_n3"):
                    st.session_state.wizard_data.update({
                        "org_name":st.session_state.get("wiz_org_name",""),
                        "org_mission":st.session_state.get("wiz_org_mission",""),
                    })
                    st.session_state.wizard_step=4; st.rerun()

        elif step==4:
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 4 — Choose your program</p>",unsafe_allow_html=True)
            options=["Write from scratch"]+[p["name"] for p in st.session_state.programs]
            current=wd.get("program_choice","Write from scratch")
            idx=options.index(current) if current in options else 0
            choice=st.radio("Select a program from your library:",options,index=idx,key="wiz_program_choice")
            if choice!="Write from scratch":
                prog=next((p for p in st.session_state.programs if p["name"]==choice),None)
                if prog:
                    st.markdown(f"<div style='background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;"
                                f"padding:.9rem 1rem;margin-top:.8rem;'>"
                                f"<div style='color:#6366F1;font-size:.75rem;font-weight:700;'>{prog['target']} · {prog['location']}</div>"
                                f"<div style='color:#64748B;font-size:.83rem;margin-top:4px;'>{prog['description'][:200]}…</div>"
                                f"</div>",unsafe_allow_html=True)
            else:
                st.text_area("Describe your program",value=wd.get("program_custom",""),height=160,
                             placeholder="Describe your program, who you serve, what you do, and results you've seen…",
                             key="wiz_program_custom")
            st.markdown("</div>",unsafe_allow_html=True)
            bc,_,nc=st.columns([1,3,1])
            with bc:
                if st.button("← Back",use_container_width=True,key="wiz_b4"):
                    st.session_state.wizard_step=3; st.rerun()
            with nc:
                if st.button("Next →",type="primary",use_container_width=True,key="wiz_n4"):
                    c=st.session_state.get("wiz_program_choice","Write from scratch")
                    if c=="Write from scratch":
                        desc=st.session_state.get("wiz_program_custom","")
                    else:
                        prog=next((p for p in st.session_state.programs if p["name"]==c),None)
                        desc=prog["description"] if prog else ""
                    st.session_state.wizard_data.update({"program_choice":c,"program_desc":desc})
                    st.session_state.wizard_step=5; st.rerun()

        elif step==5:
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 5 — Writing settings</p>",unsafe_allow_html=True)
            c1,c2=st.columns(2)
            with c1:
                st.selectbox("Tone",["Persuasive","Formal","Urgent","Conversational"],
                             index=["Persuasive","Formal","Urgent","Conversational"].index(wd.get("tone","Persuasive")),
                             key="wiz_tone")
                st.selectbox("Length",["Standard","Concise","Comprehensive"],
                             index=["Standard","Concise","Comprehensive"].index(wd.get("length","Standard")),
                             key="wiz_length")
            with c2:
                fa=["Digital Equity","Youth Development","Education","Health","Workforce","Other"]
                st.selectbox("Focus area",fa,index=fa.index(wd.get("focus_area","Digital Equity")),key="wiz_focus")
                st.selectbox("Reading level",["Professional","Expert","General Audience"],
                             index=["Professional","Expert","General Audience"].index(wd.get("reading_level","Professional")),
                             key="wiz_reading")
            st.markdown("<p style='color:#64748B;font-size:.78rem;font-weight:700;text-transform:uppercase;"
                        "letter-spacing:.05em;margin:.9rem 0 .4rem;'>Sections to include</p>",unsafe_allow_html=True)
            label_map={1:"Who We Are",2:"The Problem",3:"Our Solution",
                       4:"What We'll Achieve",5:"How We'll Measure It",6:"Why Trust Us",7:"The Budget"}
            prev=wd.get("selected_sections",list(range(1,8)))
            cc1,cc2=st.columns(2)
            sel=[]
            for i,(num,_) in enumerate(SECTION_DEFS):
                with (cc1 if i%2==0 else cc2):
                    if st.checkbox(label_map[num],value=(num in prev),key=f"wiz_sec_{num}"):
                        sel.append(num)
            st.markdown("</div>",unsafe_allow_html=True)
            bc,_,nc=st.columns([1,3,1])
            with bc:
                if st.button("← Back",use_container_width=True,key="wiz_b5"):
                    st.session_state.wizard_step=4; st.rerun()
            with nc:
                if st.button("Next →",type="primary",use_container_width=True,key="wiz_n5"):
                    st.session_state.wizard_data.update({
                        "tone":st.session_state.get("wiz_tone","Persuasive"),
                        "length":st.session_state.get("wiz_length","Standard"),
                        "focus_area":st.session_state.get("wiz_focus","Digital Equity"),
                        "reading_level":st.session_state.get("wiz_reading","Professional"),
                        "selected_sections":sel if sel else list(range(1,8)),
                    })
                    st.session_state.wizard_step=6; st.rerun()

        elif step==6:
            st.markdown(f"<div style='{card}'>",unsafe_allow_html=True)
            st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        "letter-spacing:.06em;margin:0 0 1rem;'>Step 6 — Review & Generate</p>",unsafe_allow_html=True)
            items=[("Funder",wd.get("funder_name","—")),("Type",wd.get("funder_type","—")),
                   ("Amount",wd.get("grant_amount","—")),("Deadline",wd.get("deadline","—")),
                   ("Program",wd.get("program_choice","—")),("Tone",wd.get("tone","Persuasive")),
                   ("Length",wd.get("length","Standard")),("Sections",f"{len(wd.get('selected_sections',[]))} of 7")]
            c1,c2=st.columns(2)
            for i,(k,v) in enumerate(items):
                with (c1 if i%2==0 else c2):
                    st.markdown(f"<div style='background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:8px;"
                                f"padding:.65rem .9rem;margin-bottom:.5rem;'>"
                                f"<div style='color:#94A3B8;font-size:.69rem;font-weight:700;text-transform:uppercase;"
                                f"letter-spacing:.06em;'>{k}</div>"
                                f"<div style='color:#1E293B;font-size:.88rem;font-weight:600;margin-top:2px;'>{v}</div>"
                                f"</div>",unsafe_allow_html=True)
            rfp=wd.get("rfp_text",""); prog=wd.get("program_desc","")
            if not rfp.strip(): st.warning("⚠️ No RFP text — go back to Step 2.")
            if not prog.strip(): st.warning("⚠️ No program description — go back to Step 4.")
            st.markdown("</div>",unsafe_allow_html=True)
            bc,_,gc=st.columns([1,2,2])
            with bc:
                if st.button("← Back",use_container_width=True,key="wiz_b6"):
                    st.session_state.wizard_step=5; st.rerun()
            with gc:
                if st.button("🚀 Generate My Proposal",type="primary",use_container_width=True,key="wiz_gen"):
                    if not rfp.strip(): st.error("Add the RFP first (Step 2).")
                    elif not prog.strip(): st.error("Add your program description (Step 4).")
                    else:
                        api_key=_resolved_api_key()
                        if not api_key: st.error("No API key. Add it in Org Profile.")
                        else:
                            with st.spinner("✍️ Writing your proposal… 20–40 seconds…"):
                                try:
                                    client=anthropic.Anthropic(api_key=api_key)
                                    tone=wd.get("tone","Persuasive"); length=wd.get("length","Standard")
                                    ftype=wd.get("funder_type","Private Foundation")
                                    focus=wd.get("focus_area","Digital Equity")
                                    rlevel=wd.get("reading_level","Professional")
                                    secs=wd.get("selected_sections",list(range(1,8)))
                                    msg=client.messages.create(
                                        model="claude-sonnet-4-6",max_tokens=4096,
                                        system=build_dynamic_system_prompt(tone,length,ftype,focus,secs,rlevel),
                                        messages=[{"role":"user","content":build_user_prompt(rfp,prog)}])
                                    draft=msg.content[0].text
                                    parsed=parse_sections(draft)
                                    if not parsed: parsed={1:{"name":"Full Proposal","content":draft}}
                                    st.session_state.update(
                                        sections=parsed,full_draft=rebuild_draft(parsed),
                                        rfp_saved=rfp,prog_saved=prog,regen_log=[],
                                        settings_snap={"tone":tone,"length":length,
                                                       "funder_type":ftype,"focus_area":focus,
                                                       "reading_level":rlevel},
                                        nav_item="workspace",wizard_step=1)
                                    st.rerun()
                                except anthropic.AuthenticationError: st.error("Invalid API key.")
                                except anthropic.APIStatusError as exc:
                                    if exc.status_code==529: st.warning("🟡 Anthropic is busy — try again in a moment.")
                                    else: st.error(f"API error ({exc.status_code}): {exc.message}")
                                except Exception as exc: st.error(f"Something went wrong: {exc}")

# ══════════════════════════════════════════════════════════════════════════════
#  RFP ANALYZER
# ══════════════════════════════════════════════════════════════════════════════
def show_rfp_analyzer():
    _h2("🔍 Analyze an RFP","Paste or upload any funder's RFP — we'll break it into a plain-English checklist.")
    if st.session_state.is_demo and not st.session_state.rfp_analyzer_text:
        st.markdown("<div style='background:#FFFBEB;border:1.5px solid #FCD34D;border-left:4px solid #F59E0B;"
                    "border-radius:10px;padding:.65rem 1rem;margin-bottom:.6rem;display:flex;"
                    "align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;'>"
                    "<span style='color:#92400E;font-size:.83rem;font-weight:600;'>"
                    "🎬 <b>Demo</b> — Click <b>Load sample RFP</b> below to analyze a real foundation RFP instantly.</span>"
                    "</div>",unsafe_allow_html=True)
    uploaded=st.file_uploader("Upload RFP (.txt or .pdf)",type=["txt","pdf"],
                               key="rfp_upload",label_visibility="collapsed")
    if uploaded:
        txt=_extract_file_text(uploaded)
        if txt.strip(): st.session_state["rfp_analyzer_text"]=txt

    bc,_=st.columns([1,5])
    with bc:
        if st.button("📄 Load sample RFP",key="load_rfp_sample"):
            st.session_state["rfp_analyzer_text"]=_read(os.path.join(BASE,"examples","rfp_sample.txt"))
            st.rerun()

    rfp_text=st.text_area("rfp_analyzer_area",height=230,
                           placeholder="Paste the funder's RFP here…",
                           key="rfp_analyzer_text",label_visibility="collapsed")
    cc=len(rfp_text)
    st.markdown(f"<small style='color:{'#6366F1' if cc>100 else '#94A3B8'};'>✏️ {cc:,} characters"
                +(" · ready to analyze!" if cc>100 else "")+"</small>",unsafe_allow_html=True)
    st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)

    if st.button("🔍 Analyze This RFP",type="primary",use_container_width=True,key="btn_analyze_rfp"):
        if not rfp_text.strip(): st.warning("Paste or upload an RFP first.")
        else:
            api_key=_resolved_api_key()
            if not api_key: st.error("No API key. Add it in Org Profile.")
            else:
                with st.spinner("Reading the RFP carefully… about 10 seconds."):
                    try:
                        client=anthropic.Anthropic(api_key=api_key)
                        msg=client.messages.create(
                            model="claude-sonnet-4-6",max_tokens=1500,
                            messages=[{"role":"user","content":
                                f"""Analyze this grant RFP and give a clear breakdown under these exact headings:

**Who Can Apply**
- Bullet points listing eligibility requirements

**What They Want to Fund**
- Bullet points on funding priorities

**What You Must Include**
- Every required section or attachment

**Key Numbers**
- Grant amount, deadlines, application limits

**Watch Out For**
- Tricky requirements or things applicants commonly miss

RFP:
{rfp_text}

Be concise and practical. Write like you're briefing a busy grant writer."""}])
                        st.session_state.rfp_analysis=msg.content[0].text.strip()
                        st.session_state.rfp_analysis_input=rfp_text
                    except anthropic.AuthenticationError:
                        st.error("That API key doesn't work.")
                    except anthropic.APIStatusError as exc:
                        if exc.status_code==529: st.warning("🟡 Anthropic is busy. Try again in a moment.")
                        else: st.error(f"API error ({exc.status_code}): {exc.message}")
                    except Exception as exc: st.error(f"Something went wrong: {exc}")

    if st.session_state.rfp_analysis:
        st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)
        st.markdown("<div style='background:#ECFDF5;border:1.5px solid #6EE7B7;border-left:4px solid #10B981;"
                    "border-radius:10px;padding:.65rem 1.1rem;margin-bottom:.7rem;display:flex;"
                    "align-items:center;gap:10px;'>"
                    "<span style='font-size:1rem;'>✅</span>"
                    "<span style='color:#065F46;font-weight:700;font-size:.86rem;'>"
                    "Analysis complete — review the plain-English breakdown below.</span>"
                    "</div>",unsafe_allow_html=True)
        act1,act2=st.columns([1,4])
        with act1:
            components.html(_copy_btn(st.session_state.rfp_analysis,"rfp_analysis","📋 Copy Breakdown"),height=38)
        with act2:
            if st.button("✍️  Use This RFP to Write a Proposal →",type="primary",key="rfp_to_workspace",use_container_width=True):
                st.session_state.rfp_area=st.session_state.rfp_analysis_input
                st.session_state.nav_item="workspace"
                st.session_state.sections={}; st.session_state.full_draft=""
                st.rerun()
        st.markdown("<div style='background:#FFFFFF;border:1.5px solid #E2E8F0;border-left:4px solid #6366F1;"
                    "border-radius:12px;padding:1.4rem 1.6rem;margin-top:.3rem;"
                    "box-shadow:0 2px 12px rgba(99,102,241,.06);'>",unsafe_allow_html=True)
        st.markdown(st.session_state.rfp_analysis)
        st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  FACT VERIFICATION
# ══════════════════════════════════════════════════════════════════════════════
def show_fact_verification():
    _h2("✅ Fact Check","Review every claim in your proposal before it goes to the funder.")
    FACT_COLORS={"Verified":("#10B981","#ECFDF5"),"Needs Review":("#F59E0B","#FFFBEB"),"Flagged":("#EF4444","#FEF2F2")}

    if st.session_state.full_draft:
        st.markdown("<div style='background:#EEF2FF;border:1.5px solid #C7D2FE;border-left:4px solid #6366F1;"
                    "border-radius:10px;padding:.75rem 1rem;margin-bottom:1rem;'>"
                    "<span style='color:#4F46E5;font-weight:600;font-size:.85rem;'>"
                    "✍️ Proposal loaded — reviewing claims below.</span></div>",unsafe_allow_html=True)
    else:
        st.info("No draft yet. Generate one in **New Proposal** or **Draft Editor**, then come back here.")

    st.markdown("<h3 style='color:#1E293B;font-size:.95rem;font-weight:700;margin:.5rem 0 .7rem;'>"
                "Claims Under Review</h3>",unsafe_allow_html=True)
    for fact in st.session_state.facts:
        fc,bg=FACT_COLORS.get(fact["status"],("#94A3B8","#F8FAFC"))
        badge=f"<span style='background:{bg};color:{fc};border:1px solid {fc}55;border-radius:20px;padding:3px 12px;font-size:.71rem;font-weight:700;'>{fact['status']}</span>"
        note_html=(f"<div style='color:#F59E0B;font-size:.76rem;margin-top:4px;'>⚠️ {fact['note']}</div>"
                   if fact["note"] else "")
        st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-left:4px solid {fc};"
                    f"border-radius:10px;padding:.85rem 1rem;margin-bottom:.6rem;"
                    f"box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                    f"<div style='display:flex;align-items:flex-start;justify-content:space-between;gap:12px;'>"
                    f"<div style='flex:1;'><div style='color:#1E293B;font-size:.88rem;font-weight:600;'>"
                    f"\"{fact['claim']}\"</div>"
                    f"<div style='color:#64748B;font-size:.76rem;margin-top:3px;'>Source: {fact['source']}</div>"
                    f"{note_html}</div><div style='flex-shrink:0;'>{badge}</div></div></div>",unsafe_allow_html=True)

    with st.expander("➕ Add a claim to check"):
        with st.form("add_fact_form"):
            new_claim =st.text_input("Claim / statistic",placeholder="e.g. 1 in 4 residents lacks internet access")
            new_source=st.text_input("Source",placeholder="e.g. Pew Research 2023")
            new_status=st.selectbox("Status",["Verified","Needs Review","Flagged"])
            new_note  =st.text_input("Note (optional)",placeholder="Any caveats or follow-up needed")
            if st.form_submit_button("Add Claim",type="primary"):
                if new_claim.strip():
                    st.session_state.facts.append({"id":len(st.session_state.facts)+1,
                        "claim":new_claim,"status":new_status,"source":new_source,"note":new_note})
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CITATION LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
def show_citation_library():
    _h2("📚 Citation Library","A curated bank of statistics and data points for your proposals.")
    TAG_COLORS={"digital equity":"#A78BFA","access":"#60A5FA","broadband":"#34D399",
                "rural":"#68D391","workforce":"#FBBF24","economy":"#FB923C",
                "youth":"#F472B6","education":"#2DD4BF","equity":"#A78BFA"}
    for cit in st.session_state.citations:
        tags="".join(f"<span style='background:{TAG_COLORS.get(t,'#374151')}22;color:{TAG_COLORS.get(t,'#8892A4')};"
                     f"border:1px solid {TAG_COLORS.get(t,'#374151')}44;border-radius:20px;"
                     f"padding:2px 9px;font-size:.68rem;font-weight:700;margin-right:4px;'>{t}</span>"
                     for t in cit["tags"])
        st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:10px;"
                    f"padding:.9rem 1.1rem;margin-bottom:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                    f"<div style='color:#1E293B;font-size:.9rem;font-weight:600;margin-bottom:4px;'>"
                    f"\"{cit['stat']}\"</div>"
                    f"<div style='color:#64748B;font-size:.78rem;margin-bottom:6px;'>— {cit['source']}, {cit['year']}</div>"
                    f"<div>{tags}</div></div>",unsafe_allow_html=True)
        col1,_=st.columns([1,8])
        with col1:
            tc=TAG_COLORS.get(cit["tags"][0] if cit["tags"] else "","#6366F1")
            components.html(_copy_btn(f'"{cit["stat"]}" — {cit["source"]}, {cit["year"]}',
                                      f"cit_{cit['id']}","📋 Copy",tc),height=36)
    with st.expander("➕ Add a citation"):
        with st.form("add_citation_form"):
            new_stat  =st.text_input("Statistic / data point",placeholder="e.g. 1 in 5 seniors lacks internet at home")
            new_source=st.text_input("Source",placeholder="e.g. AARP Foundation")
            new_year  =st.number_input("Year",min_value=2000,max_value=2030,value=2023,step=1)
            new_tags  =st.text_input("Tags (comma-separated)",placeholder="e.g. digital equity, seniors")
            if st.form_submit_button("Add Citation",type="primary"):
                if new_stat.strip():
                    tags_list=[t.strip() for t in new_tags.split(",") if t.strip()]
                    st.session_state.citations.append({"id":len(st.session_state.citations)+1,
                        "source":new_source,"year":int(new_year),"stat":new_stat,"tags":tags_list})
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  ALL PROPOSALS
# ══════════════════════════════════════════════════════════════════════════════
def show_all_proposals():
    _h2("📋 All Proposals","View, edit, and act on every proposal in your pipeline.")
    proposals=st.session_state.proposals
    _STATUS_OPTS=["Drafting","In Review","Submitted","Awarded","Archived"]

    # ── Summary stat chips ────────────────────────────────────────────────────
    _sc={}
    for p in proposals: _sc[p["status"]]=_sc.get(p["status"],0)+1
    chip_html="<div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:1rem;'>"
    for status,(color,bg) in _STATUS_LIGHT.items():
        n=_sc.get(status,0)
        chip_html+=(f"<div style='background:{bg};border:1px solid {color}33;border-radius:20px;"
                    f"padding:3px 12px;font-size:.74rem;font-weight:700;color:{color};'>"
                    f"{n} {status}</div>")
    chip_html+="</div>"
    st.markdown(chip_html,unsafe_allow_html=True)

    # ── Filter row ────────────────────────────────────────────────────────────
    fc,_,nc=st.columns([2,3,1])
    with fc:
        sf=st.selectbox("Filter",["All"]+_STATUS_OPTS,key="proposals_filter",label_visibility="collapsed")
    with nc:
        if st.button("＋ New Proposal",type="primary",use_container_width=True,key="all_new"):
            st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={}); st.rerun()

    filtered=[p for p in proposals if sf=="All" or p["status"]==sf]

    if not filtered:
        st.markdown("<div style='background:#fff;border:1.5px dashed #CBD5E1;border-radius:12px;"
                    "padding:2.5rem;text-align:center;'>"
                    "<div style='font-size:2rem;margin-bottom:.5rem;'>🔍</div>"
                    "<div style='color:#1E293B;font-weight:700;'>No proposals match that filter.</div>"
                    "<div style='color:#64748B;font-size:.85rem;margin-top:4px;'>Try a different status above.</div>"
                    "</div>",unsafe_allow_html=True)
        return

    st.markdown(f"<div style='color:#94A3B8;font-size:.75rem;margin-bottom:.4rem;'>"
                f"Showing {len(filtered)} of {len(proposals)}</div>",unsafe_allow_html=True)

    # ── Proposal cards ────────────────────────────────────────────────────────
    for p in filtered:
        idx=proposals.index(p)
        color,bg=_STATUS_LIGHT.get(p["status"],("#94A3B8","#F8FAFC"))
        cc=p.get("compliance",0)
        cc_color="#10B981" if cc>=85 else "#F59E0B" if cc>=70 else "#EF4444"

        with st.expander(
            f"**{p['name']}**  ·  {p['funder']}  ·  {p['amount']}  ·  Due {p['deadline']}",
            expanded=False):

            # ── Status + compliance row ───────────────────────────────────────
            st.markdown(
                f"<div style='display:flex;gap:10px;align-items:center;margin-bottom:.8rem;'>"
                f"<span style='background:{bg};color:{color};border:1px solid {color}44;"
                f"border-radius:20px;padding:3px 12px;font-size:.72rem;font-weight:700;'>{p['status']}</span>"
                f"<span style='color:{cc_color};font-size:.8rem;font-weight:700;'>●  {cc}% compliant</span>"
                f"<span style='color:#94A3B8;font-size:.75rem;'>{p.get('notes','')}</span>"
                f"</div>",unsafe_allow_html=True)

            # ── Editable fields ───────────────────────────────────────────────
            e1,e2,e3,e4=st.columns([3,2,2,2])
            with e1:
                new_name=st.text_input("Proposal title",value=p["name"],key=f"pname_{idx}")
            with e2:
                new_funder=st.text_input("Funder",value=p["funder"],key=f"pfunder_{idx}")
            with e3:
                new_amount=st.text_input("Amount",value=p["amount"],key=f"pamount_{idx}")
            with e4:
                new_status=st.selectbox("Status",_STATUS_OPTS,
                                        index=_STATUS_OPTS.index(p["status"]) if p["status"] in _STATUS_OPTS else 0,
                                        key=f"pstatus_{idx}")
            e5,e6=st.columns([1,3])
            with e5:
                new_deadline=st.text_input("Deadline",value=p["deadline"],key=f"pdeadline_{idx}")
            with e6:
                new_notes=st.text_input("Notes / next step",value=p.get("notes",""),
                                        placeholder="e.g. Follow up with program officer by May 20",
                                        key=f"pnotes_{idx}")

            # ── Action buttons ────────────────────────────────────────────────
            st.markdown("<div style='height:.3rem;'></div>",unsafe_allow_html=True)
            a1,a2,a3,a4,a5=st.columns(5)
            with a1:
                if st.button("💾 Save Changes",type="primary",use_container_width=True,key=f"psave_{idx}"):
                    proposals[idx].update(
                        name=new_name,funder=new_funder,amount=new_amount,
                        status=new_status,deadline=new_deadline,notes=new_notes)
                    st.session_state.audit_log.insert(0,{
                        "time":"Just now","user":st.session_state.user_email.split("@")[0].capitalize(),
                        "action":"Updated proposal details","item":new_name})
                    st.rerun()
            with a2:
                if st.button("✍️ Open Draft",use_container_width=True,key=f"popen_{idx}"):
                    st.session_state.nav_item="workspace"; st.rerun()
            with a3:
                if st.button("✅ Fact Check",use_container_width=True,key=f"pfact_{idx}"):
                    st.session_state.nav_item="facts"; st.rerun()
            with a4:
                if st.button("📤 Export",use_container_width=True,key=f"pexport_{idx}"):
                    st.session_state.nav_item="export"; st.rerun()
            with a5:
                if st.button("🔍 Analyze RFP",use_container_width=True,key=f"prfp_{idx}"):
                    st.session_state.nav_item="rfp"; st.rerun()

    # ── Add new proposal shortcut ─────────────────────────────────────────────
    st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
    if st.button("＋  Add Another Proposal",use_container_width=True,key="all_new2"):
        st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={}); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PROGRAM LIBRARY
# ══════════════════════════════════════════════════════════════════════════════
def show_program_library():
    _h2("🎯 Program Library","Your programs, ready to pull into any proposal in one click.")
    if st.button("＋ Add Program",type="primary",key="add_program_btn"):
        st.session_state["show_add_program"]=not st.session_state.get("show_add_program",False)
    for prog in st.session_state.programs:
        c=["#A78BFA","#60A5FA","#34D399"][(prog["id"]-1)%3]
        st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-left:4px solid {c};"
                    f"border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:.9rem;"
                    f"box-shadow:0 1px 4px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
        col1,col2=st.columns([5,1])
        with col1:
            st.markdown(f"<div style='color:{c};font-size:.75rem;font-weight:800;text-transform:uppercase;"
                        f"letter-spacing:.05em;'>{prog['target']} · {prog['location']}</div>"
                        f"<div style='color:#1E293B;font-size:1rem;font-weight:700;margin:.25rem 0 .4rem;'>{prog['name']}</div>"
                        f"<div style='color:#64748B;font-size:.84rem;line-height:1.55;'>{prog['description'][:180]}…</div>"
                        f"<div style='color:#64748B;font-size:.76rem;margin-top:.5rem;'>"
                        f"Budget: <b style='color:#1E293B;'>{prog['budget']}</b> &nbsp;·&nbsp; {prog['outcomes']}</div>",
                        unsafe_allow_html=True)
        with col2:
            if st.button("Use in\nDraft Editor",key=f"use_prog_{prog['id']}",use_container_width=True):
                st.session_state.prog_area=prog["description"]
                st.session_state.nav_item="workspace"
                st.session_state.sections={}; st.session_state.full_draft=""
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    if st.session_state.get("show_add_program"):
        with st.form("add_prog_form"):
            st.markdown("<p style='color:#6366F1;font-weight:700;'>New Program</p>",unsafe_allow_html=True)
            n1,n2=st.columns(2)
            with n1:
                pname  =st.text_input("Program name")
                ptarget=st.text_input("Target population")
            with n2:
                ploc   =st.text_input("Location")
                pbudget=st.text_input("Annual budget")
            pdesc=st.text_area("Program description",height=100)
            pout =st.text_input("Key outcomes")
            c1,c2=st.columns(2)
            with c1:
                if st.form_submit_button("Save Program",type="primary"):
                    if pname.strip():
                        st.session_state.programs.append({
                            "id":len(st.session_state.programs)+1,
                            "name":pname,"target":ptarget,"location":ploc,
                            "budget":pbudget,"outcomes":pout,"description":pdesc})
                        st.session_state["show_add_program"]=False; st.rerun()
            with c2:
                if st.form_submit_button("Cancel"):
                    st.session_state["show_add_program"]=False; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  ORG PROFILE
# ══════════════════════════════════════════════════════════════════════════════
def show_settings():
    _h2("🏢 Org Profile","Save your details here so they pre-fill into every new proposal.")
    if st.session_state.is_demo and not st.session_state.get("org_settings"):
        st.session_state.org_settings={
            "org_name":"BrightPath Community Learning Initiative",
            "org_type":"501(c)(3) Nonprofit",
            "org_location":"Washington, DC",
            "ein":"47-2891034",
            "mission":"BrightPath connects underserved DC residents with digital skills and technology access they need to participate fully in today's economy, civic life, and educational opportunities.",
            "api_key_display":"",
        }
    saved=st.session_state.get("org_settings",{})
    with st.form("org_form"):
        st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.05em;margin-bottom:.6rem;'>Organization Details</p>",unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            org_name=st.text_input("Organization name",value=saved.get("org_name",""),placeholder="e.g. DiTi Foundation")
            org_type_opts=["501(c)(3) Nonprofit","501(c)(4)","Fiscal Sponsor","Government","Other"]
            org_type=st.selectbox("Type",org_type_opts,
                                  index=org_type_opts.index(saved.get("org_type","501(c)(3) Nonprofit")))
        with c2:
            org_loc=st.text_input("City / State",value=saved.get("org_location",""),placeholder="e.g. Washington, DC")
            ein=st.text_input("EIN (optional)",value=saved.get("ein",""),placeholder="e.g. 12-3456789")
        mission=st.text_area("Mission statement",value=saved.get("mission",""),height=90,
                              placeholder="One or two sentences describing your mission…")
        st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.05em;margin:.8rem 0 .5rem;'>API Connection</p>",unsafe_allow_html=True)
        api_key_field=st.text_input("Anthropic API key",type="password",
                                     placeholder="sk-ant-… (or set in your .env file)",
                                     value=saved.get("api_key_display",""))
        st.markdown("<small style='color:#64748B;'>Your key stays on your machine and is never shared.</small>",
                    unsafe_allow_html=True)
        if st.form_submit_button("💾 Save Details",type="primary"):
            st.session_state.org_settings={"org_name":org_name,"org_type":org_type,
                                            "org_location":org_loc,"ein":ein,"mission":mission,
                                            "api_key_display":api_key_field}
            if api_key_field.strip(): st.session_state.api_override=api_key_field.strip()
            st.success("✅ Details saved.")

# ══════════════════════════════════════════════════════════════════════════════
#  BRAND KIT
# ══════════════════════════════════════════════════════════════════════════════
def show_brand_kit():
    _h2("🎨 Brand Kit","Set your colors, fonts, and template style for exported proposals.")
    bk=st.session_state.brand_kit
    c1,c2=st.columns(2)
    with c1:
        st.markdown("<p style='color:#1E293B;font-size:.88rem;font-weight:600;margin-bottom:.4rem;'>Colors</p>",unsafe_allow_html=True)
        primary=st.color_picker("Primary color",value=bk.get("primary","#6366F1"),key="bk_primary")
        accent =st.color_picker("Accent color", value=bk.get("accent","#8B5CF6"), key="bk_accent")
        font   =st.selectbox("Body font",["Georgia","Inter","Arial","Times New Roman","Merriweather"],
                             index=["Georgia","Inter","Arial","Times New Roman","Merriweather"].index(
                                 bk.get("font","Georgia")),key="bk_font")
    with c2:
        tmpl=st.radio("Template",["Professional","Modern","Classic","Minimal"],
                      index=["Professional","Modern","Classic","Minimal"].index(
                          bk.get("template","Professional")),key="bk_template")
        st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)
        st.markdown(f"<div style='background:#F8FAFC;border:1.5px solid #E2E8F0;border-radius:10px;"
                    f"padding:1rem 1.2rem;'>"
                    f"<p style='color:#94A3B8;font-size:.72rem;font-weight:700;text-transform:uppercase;"
                    f"letter-spacing:.06em;margin:0 0 .6rem;'>Preview</p>"
                    f"<div style='border-left:4px solid {primary};padding-left:10px;margin-bottom:.5rem;'>"
                    f"<div style='color:{primary};font-size:1rem;font-weight:800;font-family:{font},serif;'>"
                    f"Grant Proposal — TechForward Youth Initiative</div></div>"
                    f"<div style='color:#64748B;font-size:.82rem;font-family:{font},serif;line-height:1.6;'>"
                    f"BrightPath respectfully submits this proposal to support young people in our community…</div>"
                    f"<div style='margin-top:.6rem;'><span style='background:{accent};color:#fff;"
                    f"border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:700;'>{tmpl}</span></div>"
                    f"</div>",unsafe_allow_html=True)
    if st.button("💾 Save Brand Settings",type="primary",key="save_brand"):
        st.session_state.brand_kit={"primary":primary,"accent":accent,"font":font,"template":tmpl}
        st.success("✅ Brand settings saved.")

# ══════════════════════════════════════════════════════════════════════════════
#  EXPORT CENTER
# ══════════════════════════════════════════════════════════════════════════════
def show_export_center():
    _h2("📤 Export Center","Download your proposal in any format.")
    draft=st.session_state.full_draft
    if not draft:
        st.markdown("<div style='background:#fff;border:1.5px dashed #CBD5E1;border-radius:12px;"
                    "padding:3rem;text-align:center;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                    "<div style='font-size:2.5rem;'>📝</div>"
                    "<div style='color:#1E293B;font-weight:700;font-size:1.05rem;margin-top:.8rem;'>"
                    "No proposal draft yet.</div>"
                    "<div style='color:#64748B;font-size:.87rem;margin-top:.4rem;'>"
                    "Generate one in <b>New Proposal</b> or <b>Draft Editor</b> first.</div></div>",
                    unsafe_allow_html=True)
        if st.button("🪄 Start New Proposal",type="primary",key="export_to_wizard"):
            st.session_state.nav_item="wizard"; st.rerun()
        return

    snap=st.session_state.settings_snap; wc=len(draft.split())
    st.markdown(f"<div style='background:#ECFDF5;border:1.5px solid #6EE7B7;border-left:4px solid #10B981;"
                f"border-radius:10px;padding:.85rem 1.1rem;margin-bottom:1.2rem;'>"
                f"<span style='color:#065F46;font-weight:700;'>✅ Proposal ready to export</span>"
                f"<span style='color:#64748B;font-size:.78rem;margin-left:12px;'>"
                f"{wc:,} words · {snap.get('tone','')} · {snap.get('length','')} · {snap.get('funder_type','')}</span>"
                f"</div>",unsafe_allow_html=True)

    c1,c2,c3,c4=st.columns(4)
    with c1:
        st.download_button("⬇️ Download .txt",data=draft,
                           file_name="grant_proposal.txt",mime="text/plain",use_container_width=True)
    with c2:
        st.download_button("📝 Download .md",data=draft,
                           file_name="grant_proposal.md",mime="text/markdown",use_container_width=True)
    with c3:
        st.download_button("🌐 Download .html",data=_make_html(draft),
                           file_name="grant_proposal.html",mime="text/html",use_container_width=True)
    with c4:
        components.html(_copy_btn(draft,"export_full","📋 Copy All","#6366F1"),height=42)

    st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
    st.markdown("<h3 style='color:#1E293B;font-size:.95rem;font-weight:700;margin-bottom:.6rem;'>Full Proposal Preview</h3>",unsafe_allow_html=True)
    st.markdown("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:10px;"
                "padding:1.5rem 1.75rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
    st.markdown(draft)
    st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TEAM & SHARING
# ══════════════════════════════════════════════════════════════════════════════
def show_team():
    _h2("👥 Team & Sharing","Manage who can view and edit your proposals.")
    ACCESS_COLORS={"Admin":"#7C3AED","Editor":"#2563EB","Reviewer":"#059669","Viewer":"#D97706"}
    hdr1,hdr2=st.columns([4,1])
    with hdr1:
        st.markdown("<h3 style='color:#1E293B;font-size:.95rem;font-weight:700;margin:0;'>Team Members</h3>",unsafe_allow_html=True)
    with hdr2:
        if st.button("＋ Invite",type="primary",use_container_width=True,key="invite_btn"):
            st.session_state["show_invite"]=not st.session_state.get("show_invite",False)

    rows=""
    for m in st.session_state.team:
        ac=ACCESS_COLORS.get(m["access"],"#94A3B8")
        badge=f"<span style='background:{ac}18;color:{ac};border:1px solid {ac}44;border-radius:20px;padding:2px 10px;font-size:.69rem;font-weight:700;'>{m['access']}</span>"
        sc="#10B981" if m["status"]=="Active" else "#F59E0B"
        rows+=(f"<tr style='border-bottom:1px solid #F1F5F9;'>"
               f"<td style='padding:11px 14px;color:#1E293B;font-weight:600;font-size:.84rem;'>{m['name']}</td>"
               f"<td style='padding:11px 14px;color:#64748B;font-size:.82rem;'>{m['role']}</td>"
               f"<td style='padding:11px 14px;color:#64748B;font-size:.82rem;'>{m['email']}</td>"
               f"<td style='padding:11px 14px;'>{badge}</td>"
               f"<td style='padding:11px 14px;color:{sc};font-size:.78rem;font-weight:600;'>{m['status']}</td></tr>")
    th="padding:9px 14px;color:#94A3B8;font-size:.67rem;font-weight:700;text-align:left;text-transform:uppercase;letter-spacing:.07em;background:#F8FAFC;border-bottom:1px solid #E2E8F0;"
    st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                f"overflow:hidden;margin-top:.6rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                f"<table style='width:100%;border-collapse:collapse;'><thead><tr>"
                +"".join(f"<th style='{th}'>{h}</th>" for h in ["Name","Role","Email","Access","Status"])
                +f"</tr></thead><tbody>{rows}</tbody></table></div>",unsafe_allow_html=True)

    if st.session_state.get("show_invite"):
        st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
        with st.form("invite_form"):
            st.markdown("<p style='color:#6366F1;font-weight:700;margin-bottom:.6rem;'>Invite a Team Member</p>",unsafe_allow_html=True)
            ic1,ic2=st.columns(2)
            with ic1:
                inv_name =st.text_input("Full name",placeholder="e.g. Jordan Lee")
                inv_role =st.text_input("Role",placeholder="e.g. Program Manager")
            with ic2:
                inv_email =st.text_input("Email",placeholder="jordan@yourorg.org")
                inv_access=st.selectbox("Access level",["Viewer","Reviewer","Editor","Admin"])
            c1,c2=st.columns(2)
            with c1:
                if st.form_submit_button("Send Invite",type="primary"):
                    if inv_name.strip() and inv_email.strip():
                        st.session_state.team.append({"name":inv_name,"role":inv_role,
                                                        "email":inv_email,"access":inv_access,"status":"Pending"})
                        st.session_state["show_invite"]=False; st.rerun()
            with c2:
                if st.form_submit_button("Cancel"):
                    st.session_state["show_invite"]=False; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  SECURITY & ADMIN
# ══════════════════════════════════════════════════════════════════════════════
def show_admin():
    _h2("⚙️ Security & Admin","Audit log, API status, and account settings.")
    api_key=_resolved_api_key()
    for col,(accent,bg,label,value) in zip(st.columns(3),[
        ("#10B981","#ECFDF5","API Status","✅ Connected" if api_key else "❌ Not set"),
        ("#6366F1","#EEF2FF","Team Members",str(len(st.session_state.team))),
        ("#8B5CF6","#F5F3FF","Total Proposals",str(len(_SEED_PROPOSALS))),
    ]):
        with col:
            st.markdown(f"<div style='background:{bg};border:1.5px solid {accent}22;border-top:3px solid {accent};"
                        f"border-radius:10px;padding:1rem 1.1rem;text-align:center;"
                        f"box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                        f"<div style='color:#64748B;font-size:.72rem;font-weight:700;text-transform:uppercase;"
                        f"letter-spacing:.05em;margin-bottom:5px;'>{label}</div>"
                        f"<div style='color:#1E293B;font-size:1.1rem;font-weight:700;'>{value}</div></div>",
                        unsafe_allow_html=True)

    st.markdown("<h3 style='color:#1E293B;font-size:.95rem;font-weight:700;margin:1.3rem 0 .6rem;'>Audit Log</h3>",unsafe_allow_html=True)
    rows=""
    for entry in st.session_state.audit_log:
        rows+=(f"<tr style='border-bottom:1px solid #F1F5F9;'>"
               f"<td style='padding:10px 14px;color:#94A3B8;font-size:.78rem;'>{entry['time']}</td>"
               f"<td style='padding:10px 14px;color:#6366F1;font-size:.82rem;font-weight:600;'>{entry['user']}</td>"
               f"<td style='padding:10px 14px;color:#1E293B;font-size:.82rem;'>{entry['action']}</td>"
               f"<td style='padding:10px 14px;color:#64748B;font-size:.78rem;'>{entry['item']}</td></tr>")
    th="padding:9px 14px;color:#94A3B8;font-size:.67rem;font-weight:700;text-align:left;text-transform:uppercase;letter-spacing:.07em;background:#F8FAFC;border-bottom:1px solid #E2E8F0;"
    st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;overflow:hidden;"
                f"box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                f"<table style='width:100%;border-collapse:collapse;'><thead><tr>"
                +"".join(f"<th style='{th}'>{h}</th>" for h in ["Time","User","Action","Proposal"])
                +f"</tr></thead><tbody>{rows}</tbody></table></div>",unsafe_allow_html=True)

    st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
    with st.expander("🔑 Update API Key"):
        with st.form("api_key_form"):
            new_key=st.text_input("New Anthropic API key",type="password",placeholder="sk-ant-…")
            if st.form_submit_button("Save Key",type="primary"):
                if new_key.strip():
                    st.session_state.api_override=new_key.strip(); st.success("✅ API key updated.")

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS
# ══════════════════════════════════════════════════════════════════════════════
def show_analytics():
    _h2("📈 Analytics","How your grant portfolio is performing.")
    total =sum(int(p["amount"].replace("$","").replace(",","")) for p in _SEED_PROPOSALS)
    awarded=sum(int(p["amount"].replace("$","").replace(",","")) for p in _SEED_PROPOSALS if p["status"]=="Awarded")
    status_counts={}
    for p in _SEED_PROPOSALS: status_counts[p["status"]]=status_counts.get(p["status"],0)+1

    _AN_COLORS=[("#6366F1","#EEF2FF"),("#10B981","#ECFDF5"),("#F59E0B","#FFFBEB"),("#8B5CF6","#F5F3FF")]
    for col,(accent,bg),label,value in zip(st.columns(4),_AN_COLORS,[
        "Total Proposals","Funding Requested","Funding Won","Success Rate"],[
        str(len(_SEED_PROPOSALS)),f"${total:,}",f"${awarded:,}",f"{awarded/total*100:.0f}%"]):
        with col:
            st.markdown(f"<div style='background:{bg};border:1.5px solid {accent}22;border-top:3px solid {accent};"
                        f"border-radius:10px;padding:1rem 1.1rem;text-align:center;"
                        f"box-shadow:0 1px 4px rgba(0,0,0,.04);'>"
                        f"<div style='color:#64748B;font-size:.72rem;font-weight:700;text-transform:uppercase;"
                        f"letter-spacing:.05em;margin-bottom:5px;'>{label}</div>"
                        f"<div style='color:#1E293B;font-size:1.45rem;font-weight:900;'>{value}</div></div>",
                        unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem;'></div>",unsafe_allow_html=True)
    _STATUS_BAR_COLORS={"Drafting":"#6366F1","In Review":"#F59E0B","Submitted":"#8B5CF6","Awarded":"#10B981"}
    funding_by_status={p["status"]:int(p["amount"].replace("$","").replace(",","")) for p in _SEED_PROPOSALS}
    for title,data_dict in [("Proposal Pipeline",status_counts),("Funding by Stage",funding_by_status)]:
        st.markdown(f"<h3 style='color:#1E293B;font-size:.95rem;font-weight:700;margin-bottom:.7rem;'>{title}</h3>",unsafe_allow_html=True)
        total_v=sum(data_dict.values()) or 1
        html="<div style='display:flex;flex-direction:column;gap:8px;'>"
        for status in ["Drafting","In Review","Submitted","Awarded"]:
            v=data_dict.get(status,0); pct=v/total_v*100
            accent=_STATUS_BAR_COLORS.get(status,"#94A3B8")
            lbl=f"${v:,}" if "Funding" in title else str(v)
            html+=(f"<div style='display:flex;align-items:center;gap:12px;'>"
                   f"<div style='color:#64748B;font-size:.8rem;width:90px;flex-shrink:0;'>{status}</div>"
                   f"<div style='flex:1;background:#F1F5F9;border-radius:4px;height:22px;overflow:hidden;'>"
                   f"<div style='width:{pct}%;background:{accent}33;border-right:3px solid {accent};"
                   f"height:100%;border-radius:4px;'></div></div>"
                   f"<div style='color:{accent};font-weight:700;font-size:.82rem;width:80px;'>{lbl}</div></div>")
        html+="</div>"
        st.markdown(f"<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                    f"padding:1.25rem 1.5rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>{html}</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  WRITING TIPS
# ══════════════════════════════════════════════════════════════════════════════
def show_research_hub():
    _h2("💡 Writing Tips","Practical guidance to help your proposal stand out.")
    tips=[
        ("#3B82F6","📌","Lead with the community, not your org",
         "Funders fund change in communities — not organizations. Open every section by describing the people you serve and the real problem they face."),
        ("#059669","📊","Numbers build trust",
         "Replace 'many young people' with '247 young people ages 14–24 in Ward 7.' Every quantified claim makes reviewers more confident."),
        ("#F472B6","🔁","Mirror the funder's own words",
         "If the RFP uses 'digital equity' and 'career pathways,' so should your proposal. Reviewers score for alignment."),
        ("#FBBF24","🎯","One goal, one number, one deadline",
         "The best objectives are specific: 'At least 80% of participants will complete all 12 sessions by December 15, 2026.'"),
        ("#A78BFA","✅","Answer every single requirement",
         "Before submitting, go back to the RFP and check off every required section, attachment, and question. Missing one is the top disqualifier."),
        ("#FB923C","🤝","Name your partners",
         "'We will partner with local schools' is weak. 'We have an MOU with Anacostia High School' is strong. Named partners prove you can execute."),
    ]
    c1,c2=st.columns(2)
    for i,(accent,icon,title,body) in enumerate(tips):
        with (c1 if i%2==0 else c2):
            st.markdown(f"<div class='mb-card' style='background:#fff;border:1.5px solid {accent}22;border-top:3px solid {accent};"
                        f"border-radius:12px;padding:1.1rem 1.2rem;margin-bottom:1rem;"
                        f"box-shadow:0 2px 8px rgba(0,0,0,.05);'>"
                        f"<div style='font-size:1.3rem;margin-bottom:5px;'>{icon}</div>"
                        f"<div style='color:{accent};font-size:.78rem;font-weight:800;text-transform:uppercase;"
                        f"letter-spacing:.05em;margin-bottom:5px;'>{title}</div>"
                        f"<div style='color:#64748B;font-size:.86rem;line-height:1.6;'>{body}</div></div>",
                        unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem;'></div>",unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'>",unsafe_allow_html=True)
    if st.button("✍️  Start Writing a Proposal →",type="primary",key="tips_cta_wizard"):
        st.session_state.update(nav_item="wizard",wizard_step=1,wizard_data={})
        st.rerun()
    st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DRAFT EDITOR (Workspace)
# ══════════════════════════════════════════════════════════════════════════════
def show_workspace():
    if st.session_state.pending_regen is not None and st.session_state.sections:
        sec_num=st.session_state.pending_regen
        st.session_state.pending_regen=None
        sec_name=dict(SECTION_DEFS).get(sec_num,f"Section {sec_num}")
        with st.spinner(f"Rewriting '{sec_name}'…"):
            api_key=_resolved_api_key()
            if not api_key: st.error("No API key found.")
            else:
                try:
                    client=anthropic.Anthropic(api_key=api_key)
                    msg=client.messages.create(
                        model="claude-sonnet-4-6",max_tokens=1500,
                        messages=[{"role":"user","content":build_section_regen_prompt(
                            sec_num,sec_name,
                            st.session_state.sections[sec_num]["content"],
                            st.session_state.rfp_saved,st.session_state.prog_saved,
                            st.session_state.get("ws_tone","Persuasive"),
                            st.session_state.get("ws_length","Standard"),
                            st.session_state.get("ws_funder","Private Foundation"),
                            st.session_state.get("ws_focus","Digital Equity"),
                            st.session_state.get("ws_reading","Professional"),
                        )}])
                    st.session_state.sections[sec_num]["content"]=msg.content[0].text.strip()
                    st.session_state.full_draft=rebuild_draft(st.session_state.sections)
                    st.session_state.regen_log.append(sec_name)
                except anthropic.AuthenticationError: st.error("Invalid API key.")
                except Exception as exc: st.error(f"Rewrite failed: {exc}")

    st.markdown("<div style='margin-bottom:.8rem;display:flex;align-items:center;gap:6px;'>"
                "<span style='color:#94A3B8;font-size:.78rem;'>My Proposals</span>"
                "<span style='color:#CBD5E1;font-size:.78rem;'>/</span>"
                "<span style='color:#1E293B;font-size:.78rem;font-weight:600;'>Draft Editor</span></div>",
                unsafe_allow_html=True)

    left_col,center_col,right_col=st.columns([2,5,2.3])

    with left_col:
        st.markdown("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                    "padding:1rem .9rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
        st.markdown("<p style='color:#6366F1;font-size:.78rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.06em;margin:0 0 .8rem;'>✏️ Shape Your Draft</p>",unsafe_allow_html=True)
        tone        =st.selectbox("How should it sound?",["Persuasive","Formal","Urgent","Conversational"],key="ws_tone")
        length      =st.selectbox("How long?",["Standard","Concise","Comprehensive"],key="ws_length")
        funder_type =st.selectbox("Who's giving the grant?",["Private Foundation","Government","Corporate","Community Fund"],key="ws_funder")
        focus_area  =st.selectbox("What's the cause?",["Digital Equity","Youth Development","Education","Health","Workforce","Other"],key="ws_focus")
        reading_level=st.selectbox("Who will read this?",["Professional","Expert","General Audience"],key="ws_reading")
        st.markdown("<p style='color:#475569;font-size:.74rem;font-weight:700;text-transform:uppercase;"
                    "letter-spacing:.05em;margin:.85rem 0 .4rem;'>Sections needed</p>",unsafe_allow_html=True)
        label_map={1:"Who We Are",2:"The Problem",3:"Our Solution",
                   4:"What We'll Achieve",5:"Measuring It",6:"Why Trust Us",7:"The Budget"}
        selected_sections=[num for num,_ in SECTION_DEFS
                           if st.checkbox(label_map.get(num,""),value=True,key=f"sec_{num}")]
        if not selected_sections: st.warning("Pick at least one section.")
        with st.expander("⚙️ API Key"):
            st.text_input("Paste your key",type="password",
                          placeholder="sk-ant-… (leave blank if in .env)",key="api_override")
        if st.session_state.sections:
            st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)
            if st.button("🗑️ Start Fresh",use_container_width=True,key="start_over"):
                st.session_state.update(sections={},full_draft="",rfp_area="",prog_area="",
                                        regen_log=[],settings_snap={})
                st.rerun()
        st.markdown("</div>",unsafe_allow_html=True)

    with center_col:
        if not st.session_state.sections:
            if st.session_state.is_demo and not st.session_state.rfp_area and not st.session_state.prog_area:
                st.markdown("<div style='background:#FFFBEB;border:1.5px solid #FCD34D;border-left:4px solid #F59E0B;"
                            "border-radius:10px;padding:.7rem 1rem;margin-bottom:.7rem;display:flex;"
                            "align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;'>"
                            "<span style='color:#92400E;font-size:.83rem;font-weight:600;'>"
                            "🎬 <b>Demo Mode</b> — Load sample RFP and program data to generate a real proposal instantly.</span>"
                            "</div>",unsafe_allow_html=True)
                if st.button("⚡  Load Demo Content & Generate",type="primary",use_container_width=True,key="demo_load_all"):
                    st.session_state.rfp_area=_read(os.path.join(BASE,"examples","rfp_sample.txt"))
                    st.session_state.prog_area=_read(os.path.join(BASE,"examples","program_desc.txt"))
                    st.rerun()
                st.markdown("<div style='height:.4rem;'></div>",unsafe_allow_html=True)
            if not _resolved_api_key():
                st.warning("⚠️ No API key found. Add `ANTHROPIC_API_KEY=sk-ant-…` to your `.env` file, "
                           "or paste it in ⚙️ API Key on the left.")
            st.markdown("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                        "padding:1rem 1.2rem 1.1rem;margin-bottom:.7rem;"
                        "box-shadow:0 1px 6px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
            r1,r2=st.columns([5,1])
            with r1:
                st.markdown("<p style='color:#1E293B;font-size:.93rem;font-weight:700;margin-bottom:4px;'>"
                            "<span style='color:#6366F1;'>①</span>  📄 Paste the funder's RFP</p>",unsafe_allow_html=True)
            with r2:
                if st.button("Load sample",key="load_rfp"):
                    st.session_state.rfp_area=_read(os.path.join(BASE,"examples","rfp_sample.txt")); st.rerun()
            rfp_input=st.text_area("rfp",key="rfp_area",height=200,
                                    placeholder="Drop in the funder's full RFP or grant guidelines…",
                                    label_visibility="collapsed")
            c1=len(rfp_input)
            st.markdown(f"<small style='color:{'#6366F1' if c1>100 else '#94A3B8'};'>✏️ {c1:,} chars"
                        +(" · ready!" if c1>100 else " · paste the funder's RFP above")+"</small>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

            st.markdown("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                        "padding:1rem 1.2rem 1.1rem;margin-bottom:.7rem;"
                        "box-shadow:0 1px 6px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
            p1,p2=st.columns([5,1])
            with p1:
                st.markdown("<p style='color:#1E293B;font-size:.93rem;font-weight:700;margin-bottom:4px;'>"
                            "<span style='color:#10B981;'>②</span>  🏢 Tell us about your program</p>",unsafe_allow_html=True)
            with p2:
                if st.button("Load sample",key="load_prog"):
                    st.session_state.prog_area=_read(os.path.join(BASE,"examples","program_desc.txt")); st.rerun()
            prog_input=st.text_area("prog",key="prog_area",height=200,
                                     placeholder="Describe your nonprofit's mission, who you serve, and what your program does…",
                                     label_visibility="collapsed")
            c2=len(prog_input)
            st.markdown(f"<small style='color:{'#10B981' if c2>100 else '#94A3B8'};'>✏️ {c2:,} chars"
                        +(" · ready!" if c2>100 else " · describe your program above")+"</small>",unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)
            st.markdown("<div style='height:.75rem;'></div>",unsafe_allow_html=True)
            st.markdown(f"<div style='background:linear-gradient(135deg,#EEF2FF,#F5F3FF);"
                        f"border:1.5px solid #C7D2FE;border-radius:10px;"
                        f"padding:10px 14px;margin-bottom:12px;display:flex;gap:14px;flex-wrap:wrap;"
                        f"align-items:center;'>"
                        f"<span style='color:#64748B;font-size:.76rem;'>③ &nbsp;Settings:</span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>Sound: <b style='color:#6366F1;'>{tone}</b></span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>·</span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>Length: <b style='color:#6366F1;'>{length}</b></span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>·</span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>Funder: <b style='color:#6366F1;'>{funder_type}</b></span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>·</span>"
                        f"<span style='color:#64748B;font-size:.76rem;'>Sections: <b style='color:#6366F1;'>{len(selected_sections)}/7</b></span>"
                        f"</div>",unsafe_allow_html=True)
            if st.button("✍️  Write My Proposal Draft",type="primary",use_container_width=True,
                         disabled=not selected_sections,key="gen_btn"):
                api_key=_resolved_api_key()
                if not api_key: st.error("Add your API key in ⚙️ API Key (left panel) or your `.env` file.")
                elif not rfp_input.strip(): st.warning("Paste the funder's RFP first.")
                elif not prog_input.strip(): st.warning("Describe your program first.")
                else:
                    with st.spinner("✍️ Writing your proposal… 20–40 seconds."):
                        try:
                            client=anthropic.Anthropic(api_key=api_key)
                            msg=client.messages.create(
                                model="claude-sonnet-4-6",max_tokens=4096,
                                system=build_dynamic_system_prompt(tone,length,funder_type,focus_area,
                                                                    selected_sections,reading_level),
                                messages=[{"role":"user","content":build_user_prompt(rfp_input,prog_input)}])
                            draft=msg.content[0].text
                            parsed=parse_sections(draft)
                            if not parsed: parsed={1:{"name":"Full Proposal","content":draft}}
                            st.session_state.update(
                                sections=parsed,full_draft=rebuild_draft(parsed),
                                rfp_saved=rfp_input,prog_saved=prog_input,regen_log=[],
                                settings_snap={"tone":tone,"length":length,"funder_type":funder_type,
                                               "focus_area":focus_area,"reading_level":reading_level})
                            st.rerun()
                        except anthropic.AuthenticationError: st.error("That API key doesn't work.")
                        except anthropic.RateLimitError: st.error("Too many requests — wait a moment.")
                        except anthropic.APIStatusError as exc:
                            if exc.status_code==529: st.warning("🟡 Anthropic is busy — try again in a moment.")
                            else: st.error(f"API error ({exc.status_code}): {exc.message}")
                        except Exception as exc: st.error(f"Something went wrong: {exc}")
        else:
            sections=st.session_state.sections; snap=st.session_state.settings_snap
            st.markdown(f"<div style='background:#ECFDF5;border:1.5px solid #6EE7B7;border-left:4px solid #10B981;"
                        f"border-radius:10px;padding:10px 16px;margin-bottom:10px;display:flex;"
                        f"align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;'>"
                        f"<span style='color:#065F46;font-weight:700;'>✅ Draft ready to review!</span>"
                        f"<span style='color:#64748B;font-size:.78rem;'>"
                        f"{snap.get('tone','')} · {snap.get('length','')} · {snap.get('funder_type','')}"
                        f"</span></div>",unsafe_allow_html=True)

            ex1,ex2,ex3,ex4=st.columns([1.5,1,1,.9])
            with ex1: components.html(_copy_btn(st.session_state.full_draft,"full_draft","📋 Copy All","#6366F1"),height=36)
            with ex2:
                st.download_button("⬇️ .txt",data=st.session_state.full_draft,
                                   file_name="grant_proposal.txt",mime="text/plain",use_container_width=True)
            with ex3:
                st.download_button("📝 .md",data=st.session_state.full_draft,
                                   file_name="grant_proposal.md",mime="text/markdown",use_container_width=True)
            with ex4:
                if st.button("← Edit",use_container_width=True,key="back_btn"):
                    st.session_state.sections={}; st.session_state.full_draft=""; st.rerun()

            st.markdown("<div style='height:.5rem;'></div>",unsafe_allow_html=True)
            tab_nums=sorted(sections.keys())
            tabs=st.tabs([SHORT_LABELS.get(n,f"§{n}") for n in tab_nums])
            for tab,num in zip(tabs,tab_nums):
                sec=sections[num]; color=SECTION_COLORS.get(num,"#6366F1")
                with tab:
                    st.markdown(_section_badge(num,SHORT_LABELS.get(num,sec["name"])),unsafe_allow_html=True)
                    st.markdown(sec["content"])
                    st.markdown(f"<hr style='border-color:#E2E8F0;margin:12px 0;'>",unsafe_allow_html=True)
                    a1,a2,a3=st.columns([1.5,2,5])
                    with a1: components.html(_copy_btn(sec["content"],f"s{num}","📋 Copy",color),height=34)
                    with a2:
                        if st.button("↺ Rewrite",key=f"regen_{num}"):
                            st.session_state.pending_regen=num; st.rerun()
                    with a3:
                        wc=len(sec["content"].split())
                        st.markdown(f"<small style='color:#94A3B8;line-height:2.4;'>"
                                    f"{wc:,} words · {len(sec['content']):,} chars</small>",unsafe_allow_html=True)
            if st.session_state.regen_log:
                st.markdown(f"<small style='color:#94A3B8;'>Rewritten: {' · '.join(st.session_state.regen_log)}</small>",unsafe_allow_html=True)

    with right_col:
        has_draft=bool(st.session_state.sections)
        st.markdown("<div style='background:#fff;border:1.5px solid #E2E8F0;border-radius:12px;"
                    "padding:1rem .9rem;box-shadow:0 1px 4px rgba(0,0,0,.04);'>",unsafe_allow_html=True)
        st.markdown("<p style='color:#10B981;font-size:.77rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.06em;margin:0 0 .5rem;'>✅ What's Done</p>",unsafe_allow_html=True)
        done_nums=set(st.session_state.sections.keys()) if has_draft else set()
        for done,item in [(1 in done_nums,"Who you are"),(2 in done_nums,"The problem you solve"),
                          (3 in done_nums,"Your program description"),(4 in done_nums,"Goals & outcomes"),
                          (5 in done_nums,"Evaluation plan"),(7 in done_nums,"Budget narrative"),
                          (False,"Signed cover letter"),(False,"Letters of support")]:
            c="#10B981" if done else "#94A3B8"
            st.markdown(f"<div style='color:{c};font-size:.77rem;padding:2px 0;'>{'✅' if done else '○'} {item}</div>",unsafe_allow_html=True)

        st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
        st.markdown("<p style='color:#6366F1;font-size:.77rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.06em;margin:0 0 .4rem;'>🎯 RFP Alignment</p>",unsafe_allow_html=True)
        if has_draft:
            score=compute_alignment(st.session_state.rfp_saved,st.session_state.full_draft)
            st.progress(score/100)
            st.markdown(f"<div style='color:#6366F1;font-size:1.1rem;font-weight:900;'>{score}%</div>"
                        f"<div style='color:#94A3B8;font-size:.7rem;'>of funder's key terms matched</div>",unsafe_allow_html=True)
        else:
            st.progress(0.0)
            st.markdown("<div style='color:#94A3B8;font-size:.73rem;'>Generate a draft to see score.</div>",unsafe_allow_html=True)

        st.markdown("<div style='height:.8rem;'></div>",unsafe_allow_html=True)
        st.markdown("<p style='color:#F59E0B;font-size:.77rem;font-weight:800;text-transform:uppercase;"
                    "letter-spacing:.06em;margin:0 0 .4rem;'>📤 Before You Submit</p>",unsafe_allow_html=True)
        for done,item in [(has_draft,"Draft written"),(False,"Finance reviewed budget"),
                          (False,"ED signed off"),(False,"Attachments gathered")]:
            c="#F59E0B" if done else "#94A3B8"
            st.markdown(f"<div style='color:{c};font-size:.77rem;padding:2px 0;'>{'✅' if done else '○'} {item}</div>",unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen=="login":
    show_login()
else:
    show_sidebar_nav()
    {
        "dashboard": show_dashboard,
        "wizard":    show_wizard,
        "workspace": show_workspace,
        "rfp":       show_rfp_analyzer,
        "facts":     show_fact_verification,
        "citations": show_citation_library,
        "proposals": show_all_proposals,
        "programs":  show_program_library,
        "settings":  show_settings,
        "brand":     show_brand_kit,
        "export":    show_export_center,
        "team":      show_team,
        "admin":     show_admin,
        "analytics": show_analytics,
        "research":  show_research_hub,
    }.get(st.session_state.nav_item, show_dashboard)()
