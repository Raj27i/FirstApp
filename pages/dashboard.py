"""Dashboard — clean overview & tracker for all dreams."""

import streamlit as st
import pandas as pd
from datetime import datetime
from goals import get_stats, get_goals
from db import get_partners


def render():
    partner_rows = get_partners()
    names = " & ".join([f"{p['avatar']} {p['name']}" for p in partner_rows])
    st.markdown(f"### 📊 {names} — Dashboard")
    st.caption("Everything you've dreamed up, at a glance.")

    stats = get_stats()

    if stats["total"] == 0:
        st.info("No dreams yet. Head to the Dreams tab to add your first.")
        return

    # --- Top metrics ---
    progress = stats["completed"] / stats["total"] if stats["total"] else 0
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Dreams", stats["total"])
    c2.metric("⏳ Pending", stats["pending"])
    c3.metric("🚀 Approved", stats["approved"])
    c4.metric("🎉 Done", stats["completed"])

    st.markdown(
        f"**Progress** — {stats['completed']} of {stats['total']} complete "
        f"({progress * 100:.0f}%)"
    )
    st.progress(progress)

    st.markdown("")

    # --- Tracking table ---
    st.markdown("#### 📋 Tracker")
    all_goals = get_goals()

    rows = []
    for g in all_goals:
        status_label = {
            "pending": "⏳ Pending",
            "approved": "🚀 Approved",
            "completed": "🎉 Done",
        }.get(g["status"], g["status"])
        rows.append({
            "Status": status_label,
            "Dream": f"{g['category_emoji']} {g['title']}",
            "Category": g["category_name"],
            "Type": "🤝 Together" if g["goal_type"] == "together" else "🏃 Solo",
            "Added by": f"{g['partner_avatar']} {g['partner_name']}",
            "Completed": (g.get("completed_at") or "")[:10] or "—",
        })

    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(420, 60 + 36 * len(rows)),
    )

    st.markdown("")

    # --- Charts ---
    cl, cr = st.columns(2)
    with cl:
        st.markdown("#### By Category")
        if stats["by_category"]:
            df_cat = pd.DataFrame(stats["by_category"])
            st.bar_chart(df_cat.set_index("category")["count"], color="#e91e63")
        else:
            st.caption("No data yet")
    with cr:
        st.markdown("#### Who's Dreaming More?")
        if stats["by_partner"]:
            df_p = pd.DataFrame(stats["by_partner"])
            st.bar_chart(df_p.set_index("partner")["count"], color="#f48fb1")
        else:
            st.caption("No data yet")

    # --- Vibe footer ---
    if stats["total"] >= 5:
        ratio = stats["completed"] / stats["total"]
        st.markdown("")
        if ratio >= 0.5:
            st.success("🔥 You two are crushing it! Over half your dreams are real.")
        elif ratio >= 0.2:
            st.info("💪 Great progress — keep the adventures coming.")
        else:
            st.info("🌱 Just getting started — the best is yet to come.")
