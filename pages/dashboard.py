"""Memories — stats, charts, and a chronological memory timeline."""

import streamlit as st
import pandas as pd
from datetime import datetime
from goals import get_stats, get_goals
from db import get_partners


def render():
    partner_rows = get_partners()
    names = " & ".join([f"{p['avatar']} {p['name']}" for p in partner_rows])
    st.markdown(f"### 📖 {names}")
    st.caption("The story of you two, written in dreams come true.")

    stats = get_stats()

    if stats["total"] == 0:
        st.info("No dreams yet! Head to the Dreams tab to add your first.")
        return

    # Top metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total", stats["total"])
    c2.metric("⏳ Pending", stats["pending"])
    c3.metric("✅ Approved", stats["approved"])
    c4.metric("🎉 Done", stats["completed"])

    progress = stats["completed"] / stats["total"] if stats["total"] else 0
    st.markdown(
        f"**Journey progress** — {stats['completed']} of {stats['total']} complete "
        f"({progress * 100:.0f}%)"
    )
    st.progress(progress)

    st.markdown("")

    # Charts
    cl, cr = st.columns(2)
    with cl:
        st.markdown("#### By Category")
        if stats["by_category"]:
            df = pd.DataFrame(stats["by_category"])
            st.bar_chart(df.set_index("category")["count"], color="#e91e63")
        else:
            st.caption("No data yet")
    with cr:
        st.markdown("#### Who's Dreaming More?")
        if stats["by_partner"]:
            df = pd.DataFrame(stats["by_partner"])
            st.bar_chart(df.set_index("partner")["count"], color="#f48fb1")
        else:
            st.caption("No data yet")

    st.divider()

    # Memory timeline
    st.markdown("### 🌸 Memory Timeline")
    completed = get_goals(status="completed")

    if not completed:
        st.caption("No memories yet. Complete your first dream! 🚀")
    else:
        completed_sorted = sorted(
            completed,
            key=lambda g: g.get("completed_at") or "",
            reverse=True,
        )

        last_month = None
        for goal in completed_sorted:
            date_str = (goal.get("completed_at") or "")[:10]
            month = date_str[:7] if date_str else "Unknown"

            if month != last_month:
                try:
                    month_label = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
                except (ValueError, TypeError):
                    month_label = "Earlier"
                st.markdown(f"##### 📅 {month_label}")
                last_month = month

            with st.container(border=True):
                col_emoji, col_body = st.columns([1, 9])
                with col_emoji:
                    st.markdown(
                        f"<div style='font-size:2.2rem; line-height:1;'>"
                        f"{goal['category_emoji']}</div>",
                        unsafe_allow_html=True,
                    )
                with col_body:
                    st.markdown(f"**{goal['title']}**")
                    st.caption(
                        f"🗓 {date_str or '—'} · "
                        f"{goal['partner_avatar']} {goal['partner_name']} · "
                        f"{goal['category_name']}"
                    )
                    if goal.get("description"):
                        st.markdown(
                            f"<div style='color:#a1a1aa; font-size:0.9rem;'>"
                            f"<em>{goal['description']}</em></div>",
                            unsafe_allow_html=True,
                        )

    # Vibe footer
    if stats["total"] >= 5:
        ratio = stats["completed"] / stats["total"]
        st.markdown("")
        if ratio >= 0.5:
            st.success("🔥 You two are crushing it! Over half your dreams are real.")
        elif ratio >= 0.2:
            st.info("💪 Great progress! Keep the adventures coming.")
        else:
            st.info("🌱 Just getting started — the best is yet to come.")
