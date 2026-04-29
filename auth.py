"""
Authentication module for Couples Bucket List App.
Handles PIN hashing, login, session state, and first-run setup.
"""

import hashlib
import streamlit as st
from db import get_connection, is_setup_complete, get_partners

AVATAR_OPTIONS = ["😊", "😎", "🥰", "🤗", "🦋", "🌟", "🔥", "🌈", "🎯", "💎", "🦊", "🐱", "🐶", "🌸", "🍀", "⭐"]


def hash_pin(pin: str) -> str:
    """Hash a PIN using SHA-256. Lightweight for MVP."""
    return hashlib.sha256(pin.encode()).hexdigest()


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Verify a PIN against its hash."""
    return hash_pin(pin) == pin_hash


def register_partner(name: str, avatar: str, pin: str):
    """Register a new partner in the database."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO partners (name, avatar, pin_hash) VALUES (?, ?, ?)",
        (name, avatar, hash_pin(pin)),
    )
    conn.commit()
    conn.close()


def login_partner(name: str, pin: str):
    """Attempt to log in a partner. Returns partner row or None."""
    conn = get_connection()
    partner = conn.execute(
        "SELECT * FROM partners WHERE name = ?", (name,)
    ).fetchone()
    conn.close()

    if partner and verify_pin(pin, partner["pin_hash"]):
        return partner
    return None


def render_setup_wizard():
    """First-run wizard to register both partners."""
    st.markdown("## 💑 Welcome! Let's set up your couple profile")
    st.markdown("Both partners need to create a profile to get started.")

    partners = get_partners()
    registered = len(partners)

    if registered == 0:
        st.info("**Partner 1** — create your profile first!")
        _render_registration_form("partner_1")
    elif registered == 1:
        st.success(f"✅ **{partners[0]['name']}** {partners[0]['avatar']} is registered!")
        st.info("**Partner 2** — your turn!")
        _render_registration_form("partner_2")
    else:
        st.success("Both partners are registered! Please log in.")
        st.rerun()


def _render_registration_form(key_prefix: str):
    """Render a registration form for one partner."""
    with st.form(f"{key_prefix}_form"):
        name = st.text_input("Your name", key=f"{key_prefix}_name")
        avatar = st.selectbox(
            "Pick your avatar",
            AVATAR_OPTIONS,
            key=f"{key_prefix}_avatar",
        )
        col1, col2 = st.columns(2)
        with col1:
            pin = st.text_input(
                "Set a 4-digit PIN",
                type="password",
                max_chars=4,
                key=f"{key_prefix}_pin",
            )
        with col2:
            pin_confirm = st.text_input(
                "Confirm PIN",
                type="password",
                max_chars=4,
                key=f"{key_prefix}_pin_confirm",
            )

        submitted = st.form_submit_button("Create Profile", use_container_width=True)

        if submitted:
            if not name.strip():
                st.error("Please enter your name.")
            elif len(pin) != 4 or not pin.isdigit():
                st.error("PIN must be exactly 4 digits.")
            elif pin != pin_confirm:
                st.error("PINs don't match. Try again.")
            else:
                # Check name isn't already taken
                existing = get_partners()
                if any(p["name"].lower() == name.strip().lower() for p in existing):
                    st.error("That name is already taken. Pick a different one!")
                else:
                    register_partner(name.strip(), avatar, pin)
                    st.success(f"Welcome aboard, {name}! {avatar}")
                    st.rerun()


def render_login():
    """Render the login screen."""
    st.markdown("## 💑 Couples Bucket List")
    st.markdown("Log in to continue your adventure together.")

    partners = get_partners()
    partner_names = [p["name"] for p in partners]
    partner_display = [f"{p['avatar']} {p['name']}" for p in partners]

    with st.form("login_form"):
        selected = st.selectbox("Who are you?", partner_display, key="login_select")
        pin = st.text_input("Enter your PIN", type="password", max_chars=4, key="login_pin")
        submitted = st.form_submit_button("Log In", use_container_width=True)

        if submitted:
            idx = partner_display.index(selected)
            name = partner_names[idx]
            partner = login_partner(name, pin)
            if partner:
                st.session_state["logged_in"] = True
                st.session_state["partner_id"] = partner["id"]
                st.session_state["partner_name"] = partner["name"]
                st.session_state["partner_avatar"] = partner["avatar"]
                st.rerun()
            else:
                st.error("Wrong PIN. Try again!")


def get_current_partner():
    """Return the currently logged-in partner info from session state."""
    if st.session_state.get("logged_in"):
        return {
            "id": st.session_state["partner_id"],
            "name": st.session_state["partner_name"],
            "avatar": st.session_state["partner_avatar"],
        }
    return None


def get_other_partner():
    """Return the partner who is NOT currently logged in."""
    current = get_current_partner()
    if not current:
        return None
    partners = get_partners()
    for p in partners:
        if p["id"] != current["id"]:
            return dict(p)
    return None


def logout():
    """Clear session state to log out."""
    for key in ["logged_in", "partner_id", "partner_name", "partner_avatar"]:
        st.session_state.pop(key, None)
