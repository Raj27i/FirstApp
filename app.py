"""
Couples Bucket List App — Main entry point.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from db import init_db, is_setup_complete
from auth import render_setup_wizard, render_login, get_current_partner, logout

st.set_page_config(
    page_title="Us 💕",
    page_icon="💕",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    :root {
        --bg: #0f0f14;
        --bg-card: #1a1a23;
        --bg-elev: #232330;
        --accent: #e91e63;
        --accent-soft: #f48fb1;
        --text: #f5f5f7;
        --text-muted: #a1a1aa;
        --border: #2a2a35;
    }
    .stApp {
        background: var(--bg);
        color: var(--text);
        font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    }
    /* Hide sidebar entirely - using top tabs instead */
    [data-testid="stSidebarNav"] { display: none !important; }
    section[data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Block container width */
    .block-container { padding-top: 2rem !important; max-width: 1100px; }

    /* Top tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background: var(--bg-card);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: var(--text-muted);
        font-weight: 500;
        padding: 10px 20px;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e91e63, #c2185b) !important;
        color: white !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none; }
    .stTabs [data-baseweb="tab-border"] { display: none; }

    /* Card containers */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--bg-card);
        border-radius: 14px;
    }
    [data-testid="stVerticalBlockBorderWrapper"] > div {
        border-color: var(--border) !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 10px;
        border: 1px solid var(--border);
        background: var(--bg-elev);
        color: var(--text);
        transition: all 0.15s;
        font-weight: 500;
    }
    .stButton > button:hover {
        border-color: var(--accent);
        color: var(--accent-soft);
        transform: translateY(-1px);
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent), #c2185b);
        border: none;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #f06292, var(--accent));
        color: white;
    }

    /* Metrics */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, var(--bg-card), var(--bg-elev));
        border: 1px solid var(--border);
        padding: 20px;
        border-radius: 14px;
    }
    [data-testid="stMetricValue"] {
        color: var(--text) !important;
        font-size: 2rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background: var(--bg-elev) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
        border-radius: 10px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent) !important;
    }
    [data-baseweb="select"] > div {
        background: var(--bg-elev) !important;
        border-color: var(--border) !important;
        border-radius: 10px !important;
    }

    /* Radio as chips */
    .stRadio > div {
        flex-wrap: wrap;
        gap: 8px;
    }
    .stRadio [role="radiogroup"] label {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 6px 14px;
        margin: 0 !important;
        cursor: pointer;
        transition: all 0.15s;
    }
    .stRadio [role="radiogroup"] label:hover {
        border-color: var(--accent);
    }
    .stRadio [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(135deg, var(--accent), #c2185b);
        border-color: var(--accent);
        color: white;
    }
    .stRadio [role="radiogroup"] label > div:first-child { display: none; }

    /* Header */
    .app-logo {
        font-size: 1.7rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f48fb1, #e91e63);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
    }
    .pill-badge {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 999px;
        padding: 8px 16px;
        font-size: 0.9rem;
        color: var(--text);
        display: inline-block;
    }

    /* Dividers */
    hr { border-color: var(--border) !important; }

    /* Expander */
    [data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 14px;
    }

    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-soft));
    }

    /* Captions */
    [data-testid="stCaptionContainer"] { color: var(--text-muted); }
</style>
""", unsafe_allow_html=True)

init_db()

if not is_setup_complete():
    render_setup_wizard()
    st.stop()

if not st.session_state.get("logged_in"):
    render_login()
    st.stop()

partner = get_current_partner()

# --- Header ---
hcol1, hcol2, hcol3 = st.columns([4, 2, 1])
with hcol1:
    st.markdown('<div class="app-logo">💕 Us</div>', unsafe_allow_html=True)
    st.caption("Dreams. Dates. Memories.")
with hcol2:
    st.markdown(
        f'<div style="text-align:right; padding-top:14px;">'
        f'<span class="pill-badge">{partner["avatar"]} {partner["name"]}</span></div>',
        unsafe_allow_html=True,
    )
with hcol3:
    st.markdown('<div style="padding-top:12px;"></div>', unsafe_allow_html=True)
    if st.button("Switch", use_container_width=True):
        logout()
        st.rerun()

st.markdown("")

# --- Top tabs ---
tab_home, tab_goals, tab_dash = st.tabs([
    "🏠  Home",
    "📝  Dreams",
    "📊  Dashboard",
])

with tab_home:
    from pages.home import render as render_home
    render_home()

with tab_goals:
    from pages.bucket_list import render as render_goals
    render_goals()

with tab_dash:
    from pages.dashboard import render as render_dash
    render_dash()
