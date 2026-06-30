"""
create_task_records.py

Commits approved tasks to the tasks table, decisions to the decisions table,
and creates a meeting record. Called after human approval step in process_meeting workflow.

Input:
  approved_tasks (list[dict]): Human-reviewed and approved task objects
  meeting_title (str): Title of the source meeting
  raw_notes (str): Original meeting notes/transcript
  decisions (list[str]): Decisions extracted from the meeting

Output:
  {
    "meeting_id": str,
    "task_ids": list[str],
    "task_count": int,
    "decision_count": int,
    "recurring_count": int,
  }

Note: actual DB writes handled by Lemma runtime via `db` context injected at
execution time. This module defines the transformation logic; the runtime
handles persistence. In mock mode, the frontend handles this locally.
"""

import uuid
from datetime import datetime, timezone


def _word_overlap(title_a: str, title_b: str) -> float:
    """
    Simple word-overlap similarity for recurring task detection.
    Returns ratio of common non-trivial words to max title word count.
    Threshold 0.45 → treat as recurring.
    """
    stop = {"the", "a", "an", "to", "for", "in", "on", "with", "and", "or",
            "of", "is", "are", "was", "were", "be", "been", "has", "have",
            "new", "this", "that", "from", "by", "at", "it"}
    wa = [w for w in title_a.lower().split() if len(w) > 2 and w not in stop]
    wb = [w for w in title_b.lower().split() if len(w) > 2 and w not in stop]
    if not wa or not wb:
        return 0.0
    set_a = set(wa)
    common = sum(1 for w in wb if w in set_a)
    return common / max(len(wa), len(wb))


def run(
    approved_tasks: list[dict],
    meeting_title: str,
    raw_notes: str = "",
    decisions: list[str] | None = None,
    existing_tasks: list[dict] | None = None,   # injected by runtime from tasks table
) -> dict:
    decisions = decisions or []
    existing_tasks = existing_tasks or []
    now = datetime.now(timezone.utc).isoformat()

    meeting_id = str(uuid.uuid4())

    # ── Meeting record ────────────────────────────────────────────────────────
    meeting_record = {
        "id": meeting_id,
        "title": meeting_title,
        "raw_notes": raw_notes,
        "task_count": len(approved_tasks),
        "decision_count": len(decisions),
        "processed_at": now,
    }

    # ── Recurring task detection ──────────────────────────────────────────────
    SIMILARITY_THRESHOLD = 0.45
    task_records = []
    recurring_updates = []   # existing task IDs to increment recurrence_count on

    for task in approved_tasks:
        matched_existing = None
        for et in existing_tasks:
            if et.get("status") == "done":
                continue
            if _word_overlap(task.get("title", ""), et.get("title", "")) >= SIMILARITY_THRESHOLD:
                matched_existing = et
                break

        if matched_existing:
            # Don't create duplicate — update the existing task
            new_count = (matched_existing.get("recurrence_count") or 1) + 1
            update = {
                "id": matched_existing["id"],
                "recurrence_count": new_count,
                "is_recurring": True,
                "priority": "high" if new_count >= 3 else matched_existing.get("priority", "medium"),
            }
            recurring_updates.append(update)
        else:
            task_id = str(uuid.uuid4())
            record = {
                "id": task_id,
                "title": task.get("title", ""),
                "description": task.get("description", ""),
                "owner": task.get("owner", "UNASSIGNED"),
                "deadline": task.get("deadline") if task.get("deadline") not in ("NO_DEADLINE", "", None) else None,
                "status": "todo",
                "priority": task.get("priority", "medium"),
                "meeting_id": meeting_id,
                "source_meeting_title": meeting_title,
                "created_at": now,
                "followup_sent": False,
                # New fields with defaults
                "blocked_reason": None,
                "blocked_at": None,
                "escalated": False,
                "recurrence_count": 1,
                "first_seen_meeting_id": meeting_id,
                "is_recurring": False,
            }
            task_records.append(record)

    # ── Decision records ──────────────────────────────────────────────────────
    decision_records = []
    for text in decisions:
        decision_records.append({
            "id": str(uuid.uuid4()),
            "text": text,
            "meeting_id": meeting_id,
            "meeting_title": meeting_title,
            "created_at": now,
        })

    return {
        "meeting_id": meeting_id,
        "meeting_record": meeting_record,
        "task_ids": [r["id"] for r in task_records],
        "task_records": task_records,
        "decision_records": decision_records,
        "recurring_updates": recurring_updates,
        "task_count": len(task_records),
        "decision_count": len(decision_records),
        "recurring_count": len(recurring_updates),
    }
