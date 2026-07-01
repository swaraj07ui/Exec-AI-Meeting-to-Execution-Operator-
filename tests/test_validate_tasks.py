import pytest
import os
import sys

# Add parent dir to path to import functions
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions.validate_tasks import run

def test_validate_tasks_all_valid():
    tasks = [
        {"title": "Fix bug", "owner": "Alice", "deadline": "2026-07-05"},
        {"title": "Write tests", "owner": "Bob", "deadline": "2026-07-06"}
    ]
    result = run(tasks)
    
    assert result["total"] == 2
    assert result["ready_count"] == 2
    assert result["needs_attention"] == 0
    assert len(result["valid_tasks"]) == 2
    assert len(result["flagged_tasks"]) == 0

def test_validate_tasks_no_owner():
    tasks = [
        {"title": "Fix bug", "owner": "", "deadline": "2026-07-05"},
        {"title": "Write tests", "owner": "UNASSIGNED", "deadline": "2026-07-06"}
    ]
    result = run(tasks)
    
    assert result["total"] == 2
    assert result["ready_count"] == 0
    assert result["needs_attention"] == 2
    assert len(result["valid_tasks"]) == 0
    
    flags1 = result["flagged_tasks"][0]["_flags"]
    flags2 = result["flagged_tasks"][1]["_flags"]
    assert "NO_OWNER" in flags1
    assert "NO_OWNER" in flags2
    assert "NO_DEADLINE" not in flags1

def test_validate_tasks_no_deadline():
    tasks = [
        {"title": "Fix bug", "owner": "Alice", "deadline": ""},
        {"title": "Write tests", "owner": "Bob", "deadline": "NO_DEADLINE"}
    ]
    result = run(tasks)
    
    assert result["needs_attention"] == 2
    assert "NO_DEADLINE" in result["flagged_tasks"][0]["_flags"]
    assert "NO_DEADLINE" in result["flagged_tasks"][1]["_flags"]
    assert "NO_OWNER" not in result["flagged_tasks"][0]["_flags"]

def test_validate_tasks_both_flags():
    tasks = [
        {"title": "Unknown task", "owner": "UNASSIGNED", "deadline": "NO_DEADLINE"}
    ]
    result = run(tasks)
    
    assert result["needs_attention"] == 1
    flags = result["flagged_tasks"][0]["_flags"]
    assert "NO_OWNER" in flags
    assert "NO_DEADLINE" in flags

def test_validate_tasks_empty_input():
    result = run([])
    assert result["total"] == 0
    assert result["ready_count"] == 0
    assert result["needs_attention"] == 0
    assert len(result["valid_tasks"]) == 0
    assert len(result["flagged_tasks"]) == 0
