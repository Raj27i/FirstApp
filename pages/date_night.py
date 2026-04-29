"""Date Night — spin the wheel for tonight's adventure."""

import streamlit as st
from goals import get_random_approved_goal, complete_goal, get_goals


def render():
    st.markdown("### 🎲 Date Night")
    st.caption("Can't decide what to do? Let fate choose your next adventure.")

    approved = get_goals(status="approved")

    st.markdown("")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        spin = st.button(
            "🎰  Spin the Wheel",
            use_container_width=True,
            type="primary",
            disabled=len(approved) == 0,
        )

    if len(approved) == 0:
        st.warning(
            "No approved dreams yet! Head to the **Dreams** tab — "
            "add some and approve them together first."
        )
        return

    st.caption(
        f"<div style='text-align:center; opacity:0.7;'>🎯 "
        f"{len(approved)} approved dream{'s' if len(approved) != 1 else ''} in the pool</div>",
        unsafe_allow_html=True,
    )

    if spin:
        st.session_state["date_night_pick"] = get_random_approved_goal()

    pick = st.session_state.get("date_night_pick")
    if not pick:
        return

    st.markdown("")
    st.markdown("#### 🌟 Tonight's Adventure")

    with st.container(border=True):
        st.markdown(
            f"<div style='font-size:5rem; text-align:center; line-height:1; margin: 12px 0;'>"
            f"{pick['category_emoji']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<h2 style='text-align:center; margin: 8px 0;'>{pick['title']}</h2>",
            unsafe_allow_html=True,
        )

        type_label = "🤝 Together" if pick["goal_type"] == "together" else "🏃 Solo"
        st.markdown(
            f"<div style='text-align:center; color:#a1a1aa;'>"
            f"{pick['category_name']} · {type_label} · "
            f"by {pick['partner_avatar']} {pick['partner_name']}</div>",
            unsafe_allow_html=True,
        )

        if pick["description"]:
            st.markdown(
                f"<div style='text-align:center; margin: 16px 0; font-style:italic; color:#d4d4d8;'>"
                f"{pick['description']}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🎉 We did it!", use_container_width=True, type="primary", key="dn_done"):
                complete_goal(pick["id"])
                st.balloons()
                st.session_state.pop("date_night_pick", None)
                st.rerun()
        with col_b:
            if st.button("🔄 Pick another", use_container_width=True, key="dn_again"):
                new_goal = get_random_approved_goal()
                if new_goal:
                    st.session_state["date_night_pick"] = new_goal
                    st.rerun()
