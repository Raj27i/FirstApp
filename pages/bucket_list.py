"""
Bucket List Page — Add, browse, vote on, and complete goals.
"""

import streamlit as st
from db import get_categories
from auth import get_current_partner, get_other_partner
from goals import add_goal, get_goals, vote_on_goal, complete_goal, delete_goal, has_partner_voted, get_votes_for_goal


def render():
    partner = get_current_partner()
    if not partner:
        return

    st.markdown("## 📝 Our Bucket List")

    # --- Add Goal Form ---
    with st.expander("➕ Add a new goal", expanded=False):
        _render_add_form(partner)

    st.divider()

    # --- Filters ---
    _render_goal_feed(partner)


def _render_add_form(partner):
    categories = get_categories()
    cat_options = {f"{c['emoji']} {c['name']}": c["id"] for c in categories}

    with st.form("add_goal_form", clear_on_submit=True):
        title = st.text_input("Goal title", placeholder="e.g., Visit Tokyo together")
        description = st.text_area("Description (optional)", placeholder="Why this matters to us...", height=80)

        col1, col2 = st.columns(2)
        with col1:
            cat_display = st.selectbox("Category", list(cat_options.keys()))
        with col2:
            goal_type = st.selectbox("Type", ["together", "solo"], format_func=lambda x: "🤝 Together" if x == "together" else "🏃 Solo")

        submitted = st.form_submit_button("Add Goal", use_container_width=True)

        if submitted:
            if not title.strip():
                st.error("Give your goal a title!")
            else:
                add_goal(
                    title=title.strip(),
                    description=description.strip(),
                    category_id=cat_options[cat_display],
                    added_by=partner["id"],
                    goal_type=goal_type,
                )
                st.success(f"Goal added! ✨")
                st.rerun()


def _render_goal_feed(partner):
    # Filter bar
    col1, col2, col3 = st.columns(3)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "pending", "approved", "completed"],
            format_func=lambda x: {
                "All": "📋 All Goals",
                "pending": "⏳ Pending",
                "approved": "✅ Approved",
                "completed": "🎉 Completed",
            }.get(x, x),
        )

    categories = get_categories()
    cat_map = {"All": None}
    cat_map.update({f"{c['emoji']} {c['name']}": c["id"] for c in categories})

    with col2:
        cat_filter = st.selectbox("Category", list(cat_map.keys()))

    with col3:
        partner_filter = st.selectbox(
            "Added by",
            ["Anyone", "Me", "My partner"],
        )

    # Build filters
    status = None if status_filter == "All" else status_filter
    category_id = cat_map[cat_filter]
    added_by = None
    if partner_filter == "Me":
        added_by = partner["id"]
    elif partner_filter == "My partner":
        other = get_other_partner()
        added_by = other["id"] if other else None

    goals = get_goals(status=status, category_id=category_id, added_by=added_by)

    if not goals:
        st.info("No goals found. Add your first adventure! 🗺️")
        return

    st.markdown(f"**{len(goals)} goal{'s' if len(goals) != 1 else ''}**")

    for goal in goals:
        _render_goal_card(goal, partner)


def _render_goal_card(goal, partner):
    status_badges = {
        "pending": "⏳ Pending",
        "approved": "✅ Approved",
        "completed": "🎉 Completed",
    }
    type_badge = "🤝" if goal["goal_type"] == "together" else "🏃"

    with st.container(border=True):
        # Header row
        col_main, col_status = st.columns([4, 1])
        with col_main:
            st.markdown(
                f"### {goal['category_emoji']} {goal['title']}"
            )
        with col_status:
            st.caption(status_badges.get(goal["status"], goal["status"]))

        # Meta info
        st.caption(
            f"{type_badge} {goal['goal_type'].title()} · "
            f"Added by {goal['partner_avatar']} {goal['partner_name']} · "
            f"{goal['category_emoji']} {goal['category_name']}"
        )

        if goal["description"]:
            st.markdown(f"_{goal['description']}_")

        # Action buttons
        _render_goal_actions(goal, partner)


def _render_goal_actions(goal, partner):
    if goal["status"] == "completed":
        if goal.get("completed_at"):
            st.caption(f"Completed on {goal['completed_at'][:10]}")
        return

    col1, col2, col3 = st.columns([2, 2, 1])

    if goal["status"] == "pending":
        already_voted = has_partner_voted(goal["id"], partner["id"])
        votes = get_votes_for_goal(goal["id"])
        vote_names = [f"{v['partner_avatar']} {v['partner_name']}" for v in votes if v["vote"] == "approve"]

        if vote_names:
            st.caption(f"Approved by: {', '.join(vote_names)}")

        with col1:
            if already_voted:
                st.button("✅ You voted", key=f"voted_{goal['id']}", disabled=True)
            else:
                if st.button("👍 Approve", key=f"approve_{goal['id']}"):
                    vote_on_goal(goal["id"], partner["id"], "approve")
                    st.rerun()
        with col2:
            if not already_voted:
                if st.button("👎 Skip", key=f"skip_{goal['id']}"):
                    vote_on_goal(goal["id"], partner["id"], "skip")
                    st.rerun()

    elif goal["status"] == "approved":
        with col1:
            if st.button("🎉 Mark Complete!", key=f"complete_{goal['id']}"):
                complete_goal(goal["id"])
                st.balloons()
                st.rerun()

    with col3:
        if goal["added_by"] == partner["id"]:
            if st.button("🗑️", key=f"delete_{goal['id']}", help="Delete this goal"):
                delete_goal(goal["id"])
                st.rerun()
