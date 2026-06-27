"""
validate_tasks.py

Validates extracted tasks for required fields (owner, deadline).
Splits into valid (ready to commit) and flagged (needs human attention).

Input:
  extracted_tasks (list[dict]): Raw task objects from extractor agent

Output:
  {
    "valid_tasks": list[dict],
    "flagged_tasks": list[dict],   # each has "_flags" key
    "total": int,
    "ready_count": int,
    "needs_attention": int,
  }
"""


def run(extracted_tasks: list[dict]) -> dict:
    valid_tasks = []
    flagged_tasks = []

    for task in extracted_tasks:
        flags = _validate(task)
        if flags:
            task_copy = dict(task)
            task_copy["_flags"] = flags
            flagged_tasks.append(task_copy)
        else:
            valid_tasks.append(task)

    return {
        "valid_tasks": valid_tasks,
        "flagged_tasks": flagged_tasks,
        "total": len(extracted_tasks),
        "ready_count": len(valid_tasks),
        "needs_attention": len(flagged_tasks),
    }


def _validate(task: dict) -> list[str]:
    flags = []

    owner = task.get("owner", "").strip()
    if not owner or owner.upper() == "UNASSIGNED":
        flags.append("NO_OWNER")

    deadline = task.get("deadline", "").strip()
    if not deadline or deadline.upper() == "NO_DEADLINE":
        flags.append("NO_DEADLINE")

    return flags
