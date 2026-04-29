"""
Couples Bucket List App — Main entry point.
A shared bucket list where two partners add, vote on, and complete goals together.
"""

import sys
import os

# Ensure project root is on the path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from db import init_db, is_setup_complete
from auth import render_setup_wizard, render_login, get_current_partner, logout

# --- Page Config ---
st.set_page_config(
    page_title="Couples Bucket List 💑",
    page_icon="💑",
    layout="centered",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Romantic color accents */
    .stApp {
        font-family: 'Segoe UI', system-ui, sans-serif;
    }
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #fff0f5 0%, #fce4ec 100%);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid #f8bbd0;
    }
    div[data-testid="stMetric"] label {
        font-size: 0.85rem;
    }
    .stProgress > div > div {
        background: linear-gradient(90deg, #ec407a, #f48fb1);
    }
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fce4ec 0%, #fff0f5 50%, #ffffff 100%);
    }
    /* Force readable dark text in the pink sidebar regardless of theme */
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] * {
        color: #2c1810 !important;
    }
    section[data-testid="stSidebar"] .stButton > button {
        color: #2c1810 !important;
        background: #ffffff !important;
        border: 1px solid #f8bbd0 !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #fce4ec !important;
        border-color: #ec407a !important;
    }
    /* Nicer buttons */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #ec407a, #e91e63);
        border: none;
        color: white;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #e91e63, #c2185b);
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize DB ---
init_db()

# --- Auth Flow ---
if not is_setup_complete():
    render_setup_wizard()
    st.stop()

if not st.session_state.get("logged_in"):
    render_login()
    st.stop()

# --- Logged In: Sidebar Nav ---
partner = get_current_partner()

with st.sidebar:
    st.markdown(f"### {partner['avatar']} {partner['name']}")
    st.caption("Logged in")

    st.divider()

    page = st.radio(
        "Navigate",
        ["📝 Bucket List", "🎲 Date Night", "📊 Dashboard"],
        label_visibility="collapsed",
    )

    st.divider()

    if st.button("🚪 Switch Partner", use_container_width=True):
        logout()
        st.rerun()

# --- Page Router ---
if page == "📝 Bucket List":
    from pages.bucket_list import render
    render()
elif page == "🎲 Date Night":
    from pages.date_night import render
    render()
elif page == "📊 Dashboard":
    from pages.dashboard import render
    render()
