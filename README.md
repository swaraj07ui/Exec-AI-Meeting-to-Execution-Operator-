# ⚡ Exec — Meeting to Action

> **Lemma Hackathon Submission** · Built by Swaraj Keshav Gawde

**Exec** is a Lemma-powered agentic operator that turns raw meeting transcripts into tracked, owned, deadline-bound action items — in under 30 seconds. Version 2.0 adds four new features: **Contradiction Detector**, **Blocker Escalation**, **Recurring Task Alerts**, and **WhatsApp Voice Note Intake**.

---

## 🎯 The Problem

Startups run 6–8 meetings a week, but **80% of action items die** in Google Docs or Otter.ai transcripts. Three deeper problems compound this:

1. **Contradictions go unnoticed** — "We're going with a 3-step flow" (Jul 1) → "Let's add a verification step" (Jul 3). Nobody catches the conflict. Weeks get wasted re-litigating closed decisions.
2. **Blockers become invisible** — A task sits "in progress" for 4 days while someone is silently stuck waiting on Auth0 support. Nobody escalates.
3. **Recurring tasks accumulate** — "Update docs" appears in 3 consecutive standups. Nobody notices it's never getting done.

---

## 🧠 The Solution

**Exec** is a Lemma-powered operator that sits downstream of transcription tools.

```
Transcript or Voice Note in
     ↓
voice-note-transcriber agent (Hinglish/informal → structured English)
     ↓
action-item-extractor agent (Claude via Lemma)
     ↓
contradiction-detector agent (compares new decisions vs. all historical ones)
     ↓
recurring task detection (word-overlap similarity, in Python + JS)
     ↓
deterministic validation (owners, deadlines, priority)
     ↓
Workflow PAUSES → Human approval step (HUMAN-IN-THE-LOOP)
     ↓
Founder reviews tasks in 30 seconds, sees conflict warnings and recurring alerts
     ↓
Tasks + decisions committed to Lemma datastore → Execution board
     ↓
blocker-check workflow (daily) → escalation reminders via followup-drafter
deadline-check workflow (daily) → deadline reminders via followup-drafter
```

---

## 🏗️ Lemma SDK Utilisation

### Tables (4)

| Table | Purpose |
|---|---|
| `meetings` | Stores processed meeting records |
| `tasks` | Action items — with blocked_reason, recurrence_count, is_recurring |
| `team_members` | Team roster for owner resolution |
| `decisions` | All decisions extracted from meetings — enables contradiction detection |

### Agents (4)

| Agent | Purpose |
|---|---|
| `action-item-extractor` | Claude extracts tasks + decisions from transcript |
| `followup-drafter` | Drafts Slack reminders for deadlines and blockers |
| `contradiction-detector` | Compares new decisions vs. historical ones for conflicts |
| `voice-note-transcriber` | Cleans Hinglish/informal voice notes into structured English |

### Workflows (4)

| Workflow | Trigger | Purpose |
|---|---|---|
| `process-meeting` | Manual | Main extraction + contradiction check + approval pipeline |
| `deadline-check` | Daily 8 AM | Scans for overdue tasks, sends reminders |
| `blocker-check` | Daily 9 AM | Finds stuck in-progress tasks, drafts escalations |
| `voice-note-intake` | Manual / WhatsApp webhook | Transcriber → process-meeting pipeline |

---

## 🚀 Feature Breakdown

### F1 — Contradiction Detector
When new decisions are extracted from a meeting, the `contradiction-detector` agent compares them against **all historical decisions** stored in the `decisions` table. Conflicts surface in the review modal with severity rating and an "Override anyway" checkbox.

**Demo**: Load "Sprint Review" (stores `"Going with 3-step flow"`) → then load "Board Call" (extracts `"Add verification step"`) → review modal shows ⚠️ conflict.

### F2 — Blocker Detection
Tasks can be marked **Blocked** via status dropdown. Selecting "Blocked" opens an inline reason input. Blocked tasks get a 🔴 badge, red left border, and reason text on the card. The `blocker-check` workflow runs daily and escalates tasks stuck in-progress for 2+ days.

**Demo**: Open any in-progress task → status dropdown → "🔴 Blocked" → type reason → card updates live.

### F3 — Recurring Task Detector
Before saving new tasks, a word-overlap similarity check (threshold 0.42) compares new task titles against existing active tasks. Matches are flagged in the review modal as 🔁 Recurring — the existing task's count increments rather than creating a duplicate. Tasks seen 3+ times are auto-escalated to HIGH priority.

**Demo**: Process "Sprint Review" (creates onboarding email task) → then "Quick Standup" (extracts "update docs" for onboarding flow) → recurring section appears in modal.

### F4 — WhatsApp / Voice Note Intake
A new input section accepts informal Hinglish transcripts. The `voice-note-transcriber` agent (mocked in frontend) cleans them into structured English, pastes into the main textarea, and auto-triggers extraction. Future: WhatsApp Business API webhook integration.

**Demo**: Paste `"arjun wala bug fix karna hai by friday, priya ko email bhejni hai before release"` → click Clean & Extract → cleaned English appears → extraction runs.

---

## 📊 Insights Strip

A live-updating strip above the Kanban board shows:

```
| 📋 Tasks: 8 | 🔴 Blocked: 1 | 🔁 Recurring: 2 | 🏛 Decisions: 6 |
```

---

## 📁 Pod Structure

```
meeting-exec-pod/
├── agents/
│   ├── extractor.yaml                # action-item-extractor agent
│   ├── followup_drafter.yaml         # followup-drafter agent
│   ├── contradiction_detector.yaml   # [NEW] contradiction detector agent
│   └── transcriber.yaml              # [NEW] voice note transcriber agent
├── workflows/
│   ├── process_meeting.yaml          # main pipeline (now includes contradiction check)
│   ├── deadline_check.yaml           # daily deadline monitoring
│   ├── blocker_check.yaml            # [NEW] daily blocker escalation
│   └── voice_note_intake.yaml        # [NEW] voice note → process-meeting
├── tables/
│   ├── meetings.yaml                 # meetings table schema
│   ├── tasks.yaml                    # tasks (+ blocked_reason, recurrence_count, etc.)
│   ├── team_members.yaml             # team roster
│   └── decisions.yaml                # [NEW] decisions table
├── functions/
│   ├── parse_entities.py             # date parsing
│   ├── validate_tasks.py             # task validation
│   └── create_task_records.py        # task persistence + recurring detection
├── apps/
│   ├── index.html                    # full frontend app (all 4 features)
│   └── logo.png                      # app logo
├── pod.json                          # Lemma pod definition (v2, 4+4+4 resources)
└── run_meeting.py                    # Python SDK demo script
```

---

## 🛠️ Setup & Run

### Prerequisites
- [Lemma CLI](https://lemma.work) installed and authenticated
- Anthropic API key configured (agent uses `claude-sonnet-4-6`)

### 1. Authenticate
```bash
lemma auth login
lemma org set 019f02d1-81b5-7705-97b1-12fc47ace383
```

### 2. Verify deployed resources
```bash
lemma table list      # should show: meetings, tasks, team_members, decisions
lemma agent list      # should show: action-item-extractor, followup-drafter, contradiction-detector, voice-note-transcriber
lemma workflow list   # should show: process-meeting, deadline-check, blocker-check, voice-note-intake
```

### 3. Open the app
```
apps/index.html → open in Chrome
```
The app seeds demo data automatically on first load. Or press `⌘K` → "Seed Demo Data".

---

## 🎬 Demo Sequence

### Full 4-Feature Demo (2 minutes)

1. **App loads** → seeded Sprint Review tasks appear on board. Insights strip shows "3 tasks · 0 blocked · 1 recurring · 3 decisions"

2. **F4 Voice**: Paste `"arjun wala bug fix karna hai by friday, priya ko email bhejni hai before release"` in the WhatsApp section → **Clean & Extract** → watch AI clean it → extraction auto-starts

3. **F3 Recurring**: Process "Quick Standup" → review modal shows 🔁 Recurring Tasks section for "update docs" matching existing onboarding task

4. **F1 Contradiction**: Process "Board Call" → review modal shows ⚠️ Decision Conflicts section — "Add verification step" conflicts with stored "3-step flow" decision

5. **F2 Blocker**: On any in-progress card → status dropdown → "🔴 Blocked" → type "Waiting on Auth0 support" → card shows red left border + BLOCKED badge + reason text

6. **Insights strip** updates live throughout — showing blocked count and recurring count

---

## 📝 Submission Rationale

### Problem (35%)
Startups run 6–8 meetings weekly, but 80% of action items die in transcripts. Exec solves the execution gap: decisions get contradicted, blockers go invisible, recurring tasks accumulate silently. These are real, painful problems every startup founder recognizes.

### Solution (25%)
Exec chains 4 Lemma agents in a human-in-the-loop workflow: extract → detect contradictions → validate → human review → persist. The frontend drives the demo fully in mock mode, identical to how the real Lemma API would behave. Voice notes are cleaned by the transcriber agent before entering the pipeline.

### Lemma SDK Utilisation (15%)
4 Tables · 4 Agents · 4 Workflows · 1 App. The `decisions` table is a new Lemma resource created specifically to enable cross-meeting contradiction detection — a capability that only exists because Lemma persists structured agent output across workflow runs. The `blocker-check` workflow uses Lemma's scheduled trigger (`0 9 * * *`) and human approval step.

### Design & UX
- 4-column Kanban (To Do / In Progress / Blocked / Done)
- Live insights strip with real-time counts
- Conflict cards with severity badge and override checkbox
- Recurring task panel with escalation badge
- Inline blocker reason capture on cards
- Hinglish voice note intake with animated cleaning

---

*Built with ❤️ using Lemma SDK · June 2025 · v2.0*
