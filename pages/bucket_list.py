"""Dreams page — card grid, chip filters, search."""

import random
import streamlit as st
from db import get_categories
from auth import get_current_partner
from goals import (
    add_goal, get_goals, vote_on_goal, complete_goal,
    delete_goal, has_partner_voted,
)
from presets import PRESET_IDEAS


def render():
    partner = get_current_partner()
    if not partner:
        return

    st.markdown("### 📝 Our Dreams")
    st.caption("Big, small, wild, cozy — they all live here.")

    with st.expander("➕ Add a new dream", expanded=False):
        _render_add_form(partner)

    with st.expander("💡 Get inspired — one-click add", expanded=False):
        _render_idea_gallery(partner)

    st.markdown("")

    # Search bar
    search = st.text_input(
        "search",
        placeholder="🔍 Search dreams...",
        label_visibility="collapsed",
        key="dream_search",
    )

    # Category chips
    categories = get_categories()
    cat_chips = ["All"] + [f"{c['emoji']} {c['name']}" for c in categories]
    cat_chip = st.radio(
        "Category", cat_chips,
        horizontal=True, label_visibility="collapsed", key="cat_chip",
    )

    # Status chips
    status_chips = ["All", "⏳ Pending", "✅ Approved", "🎉 Done"]
    status_chip = st.radio(
        "Status", status_chips,
        horizontal=True, label_visibility="collapsed", key="status_chip",
    )

    # Resolve filters
    cat_id = None
    if cat_chip != "All":
        cat_name = cat_chip.split(" ", 1)[1]
        cat_id = next((c["id"] for c in categories if c["name"] == cat_name), None)

    status_map = {"⏳ Pending": "pending", "✅ Approved": "approved", "🎉 Done": "completed"}
    status = status_map.get(status_chip)

    goals = get_goals(status=status, category_id=cat_id)
    if search:
        s = search.lower()
        goals = [
            g for g in goals
            if s in g["title"].lower() or s in (g["description"] or "").lower()
        ]

    st.markdown("")

    if not goals:
        st.info("No dreams match. Add one above! 🗺️")
        return

    st.caption(f"**{len(goals)}** dream{'s' if len(goals) != 1 else ''}")

    # Card grid (2 cols)
    cols = st.columns(2)
    for idx, goal in enumerate(goals):
        with cols[idx % 2]:
            _render_goal_card(goal, partner)


def _render_add_form(partner):
    categories = get_categories()
    cat_options = {f"{c['emoji']} {c['name']}": c["id"] for c in categories}

    with st.form("add_goal_form", clear_on_submit=True):
        title = st.text_input("Dream title", placeholder="Watch sunrise from a mountain ⛰️")
        description = st.text_area(
            "Why this matters",
            placeholder="What makes this special?",
            height=70,
        )
        col1, col2 = st.columns(2)
        with col1:
            cat_display = st.selectbox("Category", list(cat_options.keys()))
        with col2:
            goal_type = st.selectbox(
                "Type", ["together", "solo"],
                format_func=lambda x: "🤝 Together" if x == "together" else "🏃 Solo",
            )
        if st.form_submit_button("Add Dream ✨", use_container_width=True, type="primary"):
            if not title.strip():
                st.error("Give your dream a title!")
            else:
                add_goal(
                    title.strip(), description.strip(),
                    cat_options[cat_display], partner["id"], goal_type,
                )
                st.success("Dream added! ✨")
                st.rerun()


def _render_idea_gallery(partner):
    categories = get_categories()
    cat_lookup = {c["name"]: c for c in categories}

    st.caption("Tap any idea to add it instantly to your dreams.")

    # Category picker
    cat_names = [c["name"] for c in categories if c["name"] in PRESET_IDEAS]
    chip_labels = ["🎲 Surprise me"] + [
        f"{cat_lookup[n]['emoji']} {n}" for n in cat_names
    ]
    pick = st.radio(
        "Inspiration category",
        chip_labels,
        horizontal=True,
        label_visibility="collapsed",
        key="idea_cat",
    )

    # Build the list of ideas to show
    if pick == "🎲 Surprise me":
        pool = []
        for cname in cat_names:
            for title, emoji in PRESET_IDEAS[cname]:
                pool.append((title, emoji, cname))
        random.seed(st.session_state.get("idea_seed", 0))
        sample = random.sample(pool, min(8, len(pool)))
        if st.button("🔀 Shuffle", key="idea_shuffle"):
            st.session_state["idea_seed"] = random.randint(0, 10_000)
            st.rerun()
        ideas = sample
    else:
        cname = pick.split(" ", 1)[1]
        ideas = [(t, e, cname) for t, e in PRESET_IDEAS.get(cname, [])]

    if not ideas:
        st.caption("No ideas in this category yet.")
        return

    # Render as a grid of clickable buttons
    cols = st.columns(2)
    for idx, (title, emoji, cname) in enumerate(ideas):
        with cols[idx % 2]:
            if st.button(
                f"{emoji}  {title}",
                key=f"idea_{cname}_{idx}_{title}",
                use_container_width=True,
            ):
                cat = cat_lookup.get(cname)
                if cat:
                    add_goal(
                        title=title,
                        description="",
                        category_id=cat["id"],
                        added_by=partner["id"],
                        goal_type="together",
                    )
                    st.toast(f"Added: {title} ✨")
                    st.rerun()


def _render_goal_card(goal, partner):
    status_pill = {
        "pending": "⏳ Pending",
        "approved": "✅ Approved",
        "completed": "🎉 Done",
    }.get(goal["status"], goal["status"])
    type_icon = "🤝" if goal["goal_type"] == "together" else "🏃"

    with st.container(border=True):
        st.markdown(
            f"<div style='font-size:2.5rem; line-height:1; margin-bottom:4px;'>"
            f"{goal['category_emoji']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(f"#### {goal['title']}")
        st.caption(
            f"{status_pill} · {type_icon} {goal['goal_type'].title()} · "
            f"by {goal['partner_avatar']} {goal['partner_name']}"
        )

        if goal["description"]:
            preview = goal["description"][:120] + ("…" if len(goal["description"]) > 120 else "")
            st.markdown(
                f"<div style='color:#a1a1aa; font-size:0.9rem; margin: 4px 0 8px;'>"
                f"<em>{preview}</em></div>",
                unsafe_allow_html=True,
            )

        _render_actions(goal, partner)


def _render_actions(goal, partner):
    if goal["status"] == "completed":
        if goal.get("completed_at"):
            st.caption(f"🏆 Completed {goal['completed_at'][:10]}")
        return

    if goal["status"] == "pending":
        already_voted = has_partner_voted(goal["id"], partner["id"])
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            if already_voted:
                st.button("✓ Voted", key=f"v_{goal['id']}", disabled=True, use_container_width=True)
            else:
                if st.button("👍 Approve", key=f"a_{goal['id']}", use_container_width=True, type="primary"):
                    vote_on_goal(goal["id"], partner["id"], "approve")
                    st.rerun()
        with c2:
            if not already_voted:
                if st.button("👎 Skip", key=f"s_{goal['id']}", use_container_width=True):
                    vote_on_goal(goal["id"], partner["id"], "skip")
                    st.rerun()
        with c3:
            if goal["added_by"] == partner["id"]:
                if st.button("🗑", key=f"d_{goal['id']}", use_container_width=True):
                    delete_goal(goal["id"])
                    st.rerun()

    elif goal["status"] == "approved":
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button("🎉 We did it!", key=f"c_{goal['id']}", use_container_width=True, type="primary"):
                complete_goal(goal["id"])
                st.balloons()
                st.rerun()
        with c2:
            if goal["added_by"] == partner["id"]:
                if st.button("🗑", key=f"d_{goal['id']}", use_container_width=True):
                    delete_goal(goal["id"])
                    st.rerun()
