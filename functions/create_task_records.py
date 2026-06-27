"""
create_task_records.py

Commits approved tasks to the tasks table and creates a meeting record.
Called after human approval step in process_meeting workflow.

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
  }

Note: actual DB writes handled by Lemma runtime via `db` context injected at
execution time. This module defines the transformation logic; the runtime
handles persistence. In mock mode, the frontend handles this locally.
"""

import uuid
from datetime import datetime, timezone


def run(
    approved_tasks: list[dict],
    meeting_title: str,
    raw_notes: str = "",
    decisions: list[str] | None = None,
) -> dict:
    decisions = decisions or []
    now = datetime.now(timezone.utc).isoformat()

    meeting_id = str(uuid.uuid4())

    # Build meeting record
    meeting_record = {
        "id": meeting_id,
        "title": meeting_title,
        "raw_notes": raw_notes,
        "task_count": len(approved_tasks),
        "decision_count": len(decisions),
        "processed_at": now,
    }

    # Build task records
    task_records = []
    for task in approved_tasks:
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
        }
        task_records.append(record)

    # Return payload — runtime persists via db context
    return {
        "meeting_id": meeting_id,
        "meeting_record": meeting_record,
        "task_ids": [r["id"] for r in task_records],
        "task_records": task_records,
        "task_count": len(task_records),
        "decision_count": len(decisions),
    }
