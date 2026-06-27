"""
parse_entities.py

Resolves relative date phrases in meeting notes to ISO dates,
identifies mentioned team members, and detects transcript format.

Input:
  notes_text (str): Raw meeting notes or transcript
  team_names (list[str]): Known team member names

Output:
  {
    "resolved_dates": dict[str, str],   # phrase -> ISO date
    "mentioned_team_members": list[str],
    "has_timestamps": bool
  }
"""

import re
from datetime import date, timedelta


def run(notes_text: str, team_names: list[str]) -> dict:
    today = date.today()

    resolved_dates = _resolve_dates(notes_text, today)
    mentioned = _find_members(notes_text, team_names)
    has_timestamps = bool(re.search(r'\[\d{2}:\d{2}:\d{2}\]', notes_text))

    return {
        "resolved_dates": resolved_dates,
        "mentioned_team_members": mentioned,
        "has_timestamps": has_timestamps,
    }


def _resolve_dates(text: str, today: date) -> dict[str, str]:
    resolved = {}

    # today / tomorrow
    resolved["today"] = today.isoformat()
    resolved["tomorrow"] = (today + timedelta(days=1)).isoformat()
    resolved["day after tomorrow"] = (today + timedelta(days=2)).isoformat()

    # weekday names → next occurrence (including today)
    weekday_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, wd in enumerate(weekday_names):
        days_ahead = (i - today.weekday()) % 7
        # if today IS that weekday, return today (not +7)
        resolved[wd] = (today + timedelta(days=days_ahead)).isoformat()
        resolved[f"by {wd}"] = resolved[wd]
        resolved[f"next {wd}"] = (today + timedelta(days=(days_ahead or 7))).isoformat()
        if days_ahead == 0:
            resolved[f"next {wd}"] = (today + timedelta(days=7)).isoformat()

    # "this week" → coming Friday
    days_to_friday = (4 - today.weekday()) % 7
    resolved["this week"] = (today + timedelta(days=days_to_friday or 7)).isoformat()
    resolved["end of week"] = resolved["this week"]

    # "next week" → Monday of next week
    days_to_next_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_to_next_monday)
    resolved["next week"] = next_monday.isoformat()

    # "end of month"
    if today.month == 12:
        eom = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        eom = date(today.year, today.month + 1, 1) - timedelta(days=1)
    resolved["end of month"] = eom.isoformat()

    # "before July 10" → July 9 (current or next year)
    before_matches = re.findall(
        r'before\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})',
        text, re.IGNORECASE
    )
    month_map = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    for mon_str, day_str in before_matches:
        m = month_map[mon_str.lower()]
        d = int(day_str)
        target = date(today.year, m, d) - timedelta(days=1)
        if target < today:
            target = date(today.year + 1, m, d) - timedelta(days=1)
        key = f"before {mon_str.capitalize()} {day_str}"
        resolved[key] = target.isoformat()
        resolved[key.lower()] = target.isoformat()

    # explicit "July 10" style → parse inline dates too
    month_day_matches = re.findall(
        r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})(?:st|nd|rd|th)?',
        text, re.IGNORECASE
    )
    for mon_str, day_str in month_day_matches:
        m = month_map[mon_str.lower()]
        d = int(day_str)
        target = date(today.year, m, d)
        if target < today:
            target = date(today.year + 1, m, d)
        key = f"{mon_str.capitalize()} {day_str}"
        resolved[key] = target.isoformat()

    # "end of August" style
    end_of_month_matches = re.findall(
        r'end\s+of\s+(january|february|march|april|may|june|july|august|september|october|november|december)',
        text, re.IGNORECASE
    )
    for mon_str in end_of_month_matches:
        m = month_map[mon_str.lower()]
        year = today.year if m >= today.month else today.year + 1
        if m == 12:
            eom_target = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            eom_target = date(year, m + 1, 1) - timedelta(days=1)
        key = f"end of {mon_str.capitalize()}"
        resolved[key] = eom_target.isoformat()
        resolved[key.lower()] = eom_target.isoformat()

    return resolved


def _find_members(text: str, team_names: list[str]) -> list[str]:
    mentioned = []
    for name in team_names:
        if re.search(r'\b' + re.escape(name) + r'\b', text, re.IGNORECASE):
            mentioned.append(name)
    return mentioned
