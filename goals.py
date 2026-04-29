"""
Goal CRUD and voting logic for Couples Bucket List App.
"""

from datetime import datetime
from db import get_connection


def add_goal(title: str, description: str, category_id: int, added_by: int, goal_type: str = "together"):
    """Add a new goal to the bucket list."""
    conn = get_connection()
    conn.execute(
        """INSERT INTO goals (title, description, category_id, added_by, goal_type)
           VALUES (?, ?, ?, ?, ?)""",
        (title, description, category_id, added_by, goal_type),
    )
    conn.commit()
    conn.close()


def get_goals(status=None, category_id=None, added_by=None):
    """Fetch goals with optional filters. Returns list of dicts with category and partner info."""
    conn = get_connection()
    query = """
        SELECT g.*, c.name as category_name, c.emoji as category_emoji,
               p.name as partner_name, p.avatar as partner_avatar
        FROM goals g
        JOIN categories c ON g.category_id = c.id
        JOIN partners p ON g.added_by = p.id
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND g.status = ?"
        params.append(status)
    if category_id:
        query += " AND g.category_id = ?"
        params.append(category_id)
    if added_by:
        query += " AND g.added_by = ?"
        params.append(added_by)

    query += " ORDER BY g.created_at DESC"
    goals = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(g) for g in goals]


def get_goal_by_id(goal_id: int):
    """Fetch a single goal by ID."""
    conn = get_connection()
    goal = conn.execute(
        """SELECT g.*, c.name as category_name, c.emoji as category_emoji,
                  p.name as partner_name, p.avatar as partner_avatar
           FROM goals g
           JOIN categories c ON g.category_id = c.id
           JOIN partners p ON g.added_by = p.id
           WHERE g.id = ?""",
        (goal_id,),
    ).fetchone()
    conn.close()
    return dict(goal) if goal else None


def vote_on_goal(goal_id: int, partner_id: int, vote: str = "approve"):
    """Cast a vote on a goal. Auto-approves if both partners have voted 'approve'."""
    conn = get_connection()

    # Upsert the vote
    conn.execute(
        """INSERT INTO votes (goal_id, partner_id, vote) VALUES (?, ?, ?)
           ON CONFLICT(goal_id, partner_id) DO UPDATE SET vote = ?, created_at = CURRENT_TIMESTAMP""",
        (goal_id, partner_id, vote, vote),
    )

    # Check if both partners approved
    approvals = conn.execute(
        "SELECT COUNT(*) FROM votes WHERE goal_id = ? AND vote = 'approve'",
        (goal_id,),
    ).fetchone()[0]

    if approvals >= 2:
        conn.execute("UPDATE goals SET status = 'approved' WHERE id = ?", (goal_id,))

    conn.commit()
    conn.close()


def get_votes_for_goal(goal_id: int):
    """Get all votes for a specific goal."""
    conn = get_connection()
    votes = conn.execute(
        """SELECT v.*, p.name as partner_name, p.avatar as partner_avatar
           FROM votes v
           JOIN partners p ON v.partner_id = p.id
           WHERE v.goal_id = ?""",
        (goal_id,),
    ).fetchall()
    conn.close()
    return [dict(v) for v in votes]


def has_partner_voted(goal_id: int, partner_id: int) -> bool:
    """Check if a partner has already voted on a goal."""
    conn = get_connection()
    vote = conn.execute(
        "SELECT id FROM votes WHERE goal_id = ? AND partner_id = ?",
        (goal_id, partner_id),
    ).fetchone()
    conn.close()
    return vote is not None


def complete_goal(goal_id: int):
    """Mark a goal as completed."""
    conn = get_connection()
    conn.execute(
        "UPDATE goals SET status = 'completed', completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), goal_id),
    )
    conn.commit()
    conn.close()


def delete_goal(goal_id: int):
    """Delete a goal and its votes."""
    conn = get_connection()
    conn.execute("DELETE FROM votes WHERE goal_id = ?", (goal_id,))
    conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
    conn.commit()
    conn.close()


def get_random_approved_goal():
    """Pick a random approved (but not completed) goal for date night."""
    conn = get_connection()
    goal = conn.execute(
        """SELECT g.*, c.name as category_name, c.emoji as category_emoji,
                  p.name as partner_name, p.avatar as partner_avatar
           FROM goals g
           JOIN categories c ON g.category_id = c.id
           JOIN partners p ON g.added_by = p.id
           WHERE g.status = 'approved'
           ORDER BY RANDOM() LIMIT 1""",
    ).fetchone()
    conn.close()
    return dict(goal) if goal else None


def get_stats():
    """Get dashboard statistics."""
    conn = get_connection()

    total = conn.execute("SELECT COUNT(*) FROM goals").fetchone()[0]
    pending = conn.execute("SELECT COUNT(*) FROM goals WHERE status = 'pending'").fetchone()[0]
    approved = conn.execute("SELECT COUNT(*) FROM goals WHERE status = 'approved'").fetchone()[0]
    completed = conn.execute("SELECT COUNT(*) FROM goals WHERE status = 'completed'").fetchone()[0]

    # Goals by category
    by_category = conn.execute(
        """SELECT c.emoji || ' ' || c.name as category, COUNT(*) as count
           FROM goals g JOIN categories c ON g.category_id = c.id
           GROUP BY c.id ORDER BY count DESC"""
    ).fetchall()

    # Goals by partner
    by_partner = conn.execute(
        """SELECT p.avatar || ' ' || p.name as partner, COUNT(*) as count
           FROM goals g JOIN partners p ON g.added_by = p.id
           GROUP BY p.id"""
    ).fetchall()

    # Recently completed
    recent = conn.execute(
        """SELECT g.title, g.completed_at, c.emoji as category_emoji
           FROM goals g JOIN categories c ON g.category_id = c.id
           WHERE g.status = 'completed'
           ORDER BY g.completed_at DESC LIMIT 5"""
    ).fetchall()

    conn.close()

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "completed": completed,
        "by_category": [dict(r) for r in by_category],
        "by_partner": [dict(r) for r in by_partner],
        "recent_completed": [dict(r) for r in recent],
    }
