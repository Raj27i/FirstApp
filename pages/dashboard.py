"""
Dashboard Page — Couples stats, progress, and charts.
"""

import streamlit as st
import pandas as pd
from goals import get_stats
from db import get_partners


def render():
    partner_rows = get_partners()
    names = " & ".join([f"{p['avatar']} {p['name']}" for p in partner_rows])
    st.markdown(f"## 📊 {names}'s Dashboard")

    stats = get_stats()

    if stats["total"] == 0:
        st.info("No goals yet! Head to the Bucket List page to add your first adventure.")
        return

    # --- Top Metrics ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Goals", stats["total"])
    col2.metric("⏳ Pending", stats["pending"])
    col3.metric("✅ Approved", stats["approved"])
    col4.metric("🎉 Completed", stats["completed"])

    # --- Progress Bar ---
    if stats["total"] > 0:
        progress = stats["completed"] / stats["total"]
        st.markdown(f"**Overall Progress** — {stats['completed']}/{stats['total']} completed")
        st.progress(progress)

    st.divider()

    # --- Charts side by side ---
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Goals by Category")
        if stats["by_category"]:
            df_cat = pd.DataFrame(stats["by_category"])
            st.bar_chart(df_cat.set_index("category")["count"])
        else:
            st.caption("No data yet")

    with col_right:
        st.markdown("### Who's Adding More?")
        if stats["by_partner"]:
            df_partner = pd.DataFrame(stats["by_partner"])
            st.bar_chart(df_partner.set_index("partner")["count"])
        else:
            st.caption("No data yet")

    # --- Recently Completed ---
    st.divider()
    st.markdown("### 🏆 Recently Completed")
    if stats["recent_completed"]:
        for item in stats["recent_completed"]:
            date_str = item["completed_at"][:10] if item.get("completed_at") else "Unknown"
            st.markdown(f"- {item['category_emoji']} **{item['title']}** — _{date_str}_")
    else:
        st.caption("No completed goals yet. Get out there! 🚀")

    # --- Compatibility hint ---
    st.divider()
    if stats["total"] >= 5:
        if stats["completed"] > 0:
            ratio = stats["completed"] / stats["total"]
            if ratio >= 0.5:
                st.success("🔥 You two are crushing it! Over half your goals are done!")
            elif ratio >= 0.2:
                st.info("💪 Great progress! Keep the adventures coming!")
            else:
                st.info("🌱 Just getting started — the best is yet to come!")
