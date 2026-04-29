"""
Date Night Generator — Pick a random approved goal for tonight's adventure.
"""

import streamlit as st
from goals import get_random_approved_goal, complete_goal, get_goals


def render():
    st.markdown("## 🎲 Date Night Generator")
    st.markdown("Can't decide what to do? Let fate choose your next adventure!")

    st.markdown("")

    # Big spin button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        spin = st.button(
            "🎰 Spin the Wheel!",
            use_container_width=True,
            type="primary",
        )

    if spin:
        goal = get_random_approved_goal()
        if goal:
            st.session_state["date_night_pick"] = goal
        else:
            st.session_state["date_night_pick"] = None
            st.warning("No approved goals yet! Add some goals and get your partner to approve them first.")

    # Show the pick
    pick = st.session_state.get("date_night_pick")
    if pick:
        st.markdown("---")
        st.markdown("### 🌟 Tonight's Adventure")

        with st.container(border=True):
            st.markdown(f"## {pick['category_emoji']} {pick['title']}")

            type_label = "🤝 Together" if pick["goal_type"] == "together" else "🏃 Solo"
            st.markdown(
                f"**{pick['category_name']}** · {type_label} · "
                f"Suggested by {pick['partner_avatar']} {pick['partner_name']}"
            )

            if pick["description"]:
                st.markdown(f"_{pick['description']}_")

            st.markdown("")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("🎉 We did it!", use_container_width=True, type="primary"):
                    complete_goal(pick["id"])
                    st.balloons()
                    st.session_state.pop("date_night_pick", None)
                    st.rerun()
            with col_b:
                if st.button("🔄 Pick another", use_container_width=True):
                    new_goal = get_random_approved_goal()
                    if new_goal:
                        st.session_state["date_night_pick"] = new_goal
                        st.rerun()
                    else:
                        st.warning("That was the only approved goal!")

    # Show how many options are in the pool
    approved = get_goals(status="approved")
    st.markdown("")
    st.caption(f"🎯 {len(approved)} approved goal{'s' if len(approved) != 1 else ''} in the pool")
