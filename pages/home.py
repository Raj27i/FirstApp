"""Home — landing dashboard with greeting, stats, and next-up adventure."""

import streamlit as st
from datetime import datetime
from goals import get_stats, get_goals, get_random_approved_goal
from auth import get_current_partner, get_other_partner


def render():
    partner = get_current_partner()
    other = get_other_partner()
    stats = get_stats()

    hour = datetime.now().hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"

    st.markdown(f"## {greeting}, {partner['avatar']} {partner['name']}")
    if other:
        st.caption(
            f"You & {other['avatar']} {other['name']} have **{stats['total']}** dreams "
            f"and **{stats['completed']}** memories together."
        )
    st.markdown("")

    # Stat cards
    c1, c2, c3 = st.columns(3)
    c1.metric("✨ Dreams", stats["total"])
    c2.metric("🚀 In Motion", stats["approved"])
    c3.metric("🏆 Conquered", stats["completed"])

    if stats["total"] > 0:
        st.progress(stats["completed"] / stats["total"])

    st.markdown("")

    # Hero + recent activity
    left, right = st.columns([3, 2])

    with left:
        st.markdown("#### 🌟 Your Next Adventure")
        next_goal = get_random_approved_goal()
        with st.container(border=True):
            if next_goal:
                st.markdown(
                    f"<div style='font-size:3.5rem; line-height:1;'>{next_goal['category_emoji']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(f"### {next_goal['title']}")
                if next_goal["description"]:
                    st.markdown(f"_{next_goal['description']}_")
                type_label = "🤝 Together" if next_goal["goal_type"] == "together" else "🏃 Solo"
                st.caption(
                    f"{type_label} · {next_goal['category_emoji']} {next_goal['category_name']} · "
                    f"by {next_goal['partner_avatar']} {next_goal['partner_name']}"
                )
            else:
                st.markdown("### 💭 Nothing approved yet")
                st.caption("Add some dreams and approve them together — they'll show up here.")

    with right:
        st.markdown("#### 🔥 Recent")
        recent_goals = get_goals()[:5]
        with st.container(border=True):
            if not recent_goals:
                st.caption("No activity yet.")
            else:
                for i, g in enumerate(recent_goals):
                    icon = (
                        "🎉" if g["status"] == "completed"
                        else "✅" if g["status"] == "approved"
                        else "⏳"
                    )
                    title = g["title"][:32] + ("…" if len(g["title"]) > 32 else "")
                    st.markdown(f"{icon} **{title}**")
                    st.caption(
                        f"{g['partner_avatar']} {g['partner_name']} · "
                        f"{g['category_emoji']} {g['category_name']}"
                    )
                    if i < len(recent_goals) - 1:
                        st.markdown(
                            "<hr style='margin:6px 0; opacity:0.3;'/>",
                            unsafe_allow_html=True,
                        )
