# ⚡ Exec — Meeting to Action

> **Lemma Hackathon Submission** · Built by Swaraj Keshav Gawde  
> 🔗 **Live Demo:** [swaraj07ui.github.io/Exec-AI-Meeting-to-Execution-Operator-/apps](https://swaraj07ui.github.io/Exec-AI-Meeting-to-Execution-Operator-/apps/index.html)

**Exec** is a Lemma-powered agentic operator that turns raw meeting transcripts into tracked, owned, deadline-bound action items — in under 30 seconds.

It solves a real problem every startup founder faces: **80% of action items die in meeting notes.** Exec bridges the gap between "we discussed it" and "it actually got done."

---

## 🎯 The Problem

Startups run 6–8 meetings a week. Three compounding problems kill execution:

1. **Contradictions go unnoticed** — "Going with 3-step flow" (Jul 1) → "Add a verification step" (Jul 3). Nobody catches it. Weeks get re-litigated.
2. **Blockers become invisible** — A task sits "in progress" for 4 days while someone is silently stuck on Auth0 support. Nobody escalates.
3. **Recurring tasks accumulate** — "Update docs" appears in 3 consecutive standups. Nobody notices it's never getting done.

---

## 🧠 How It Works

```
Meeting Notes / Voice Note (Hinglish OK)
          ↓
  voice-note-transcriber agent   ← cleans Hinglish into structured English
          ↓
  action-item-extractor agent    ← Claude extracts tasks + decisions
          ↓
  contradiction-detector agent   ← compares new decisions vs historical ones
          ↓
  recurring task detection       ← word-overlap similarity check (Python + JS)
          ↓
  validate_tasks function        ← flags missing owners / deadlines
          ↓
  ⏸ HUMAN-IN-THE-LOOP PAUSE     ← founder reviews in the web app
          ↓
  create_task_records function   ← commits tasks + decisions to Lemma datastore
          ↓
  Kanban Board                   ← 4-column execution board (To Do / In Progress / Blocked / Done)
          ↓
  blocker-check workflow (9 AM daily)   → escalation reminders
  deadline-check workflow (8 AM daily)  → deadline reminders
```

---

## 🏗️ Lemma SDK Resources

### Tables (4)

| Table | Purpose |
|---|---|
| `meetings` | Stores processed meeting records with raw notes |
| `tasks` | Action items with full audit trail — blocked_reason, recurrence_count, completion_verified, history |
| `team_members` | Team roster for AI owner resolution |
| `decisions` | All decisions across meetings — enables cross-meeting contradiction detection |

### Agents (5)

| Agent | Model | Purpose |
|---|---|---|
| `action-item-extractor` | claude-sonnet-4-6 | Extracts tasks, decisions, and follow-up meetings from transcript |
| `followup-drafter` | claude-sonnet-4-6 | Drafts Slack/email reminders for deadlines and blockers |
| `contradiction-detector` | claude-sonnet-4-6 | Compares new decisions vs. all historical ones for conflicts |
| `voice-note-transcriber` | claude-sonnet-4-6 | Cleans Hinglish/informal voice notes into structured English |
| `completion-verifier` | claude-sonnet-4-6 | Reviews task completion notes — prevents false "Done" signals |

### Workflows (4)

| Workflow | Trigger | Purpose |
|---|---|---|
| `process-meeting` | Manual | Main pipeline: extract → detect → validate → approve → persist |
| `deadline-check` | `0 8 * * *` Daily 8 AM | Scans overdue tasks, drafts reminders |
| `blocker-check` | `0 9 * * *` Daily 9 AM | Finds stuck in-progress tasks, drafts escalations |
| `voice-note-intake` | Manual / Webhook | Transcriber → process-meeting pipeline |

### Functions (3)

| Function | Purpose |
|---|---|
| `parse_entities` | Resolves relative dates ("next Tuesday" → ISO date) + identifies team members |
| `validate_tasks` | Splits tasks into valid vs. flagged — catches missing owner/deadline |
| `create_task_records` | Commits approved tasks + decisions to DB; handles recurring task merging |

### App (1)

| App | Purpose |
|---|---|
| `apps/index.html` | Full-featured Kanban execution board — zero dependencies, single HTML file |

---

## 🚀 Feature Breakdown

### F1 — Contradiction Detector
When new decisions are extracted from a meeting, the `contradiction-detector` agent compares them against **all historical decisions** in the `decisions` table. Conflicts surface in the human review modal with:
- Severity badge (HIGH / MEDIUM)
- What the new decision says vs. what was previously decided
- Which meeting the original decision came from
- "Override anyway" checkbox to consciously accept the conflict

**Demo:** Load "Sprint Review" → then "Board Call" → review modal shows ⚠️ conflict between "3-step flow" and "Add verification step."

---

### F2 — Blocker Detection
Tasks can be marked **Blocked** via the status dropdown on any card. Selecting "Blocked" captures a free-text reason inline. Blocked tasks get:
- 🔴 badge on the card
- Red left border
- Reason text displayed on the card
- Auto-escalation via the daily `blocker-check` workflow (tasks stuck in-progress 2+ days)

**Demo:** Any in-progress card → dropdown → "🔴 Blocked" → type reason → card updates live.

---

### F3 — Recurring Task Detector
Before saving, new tasks are checked for word-overlap similarity (threshold 0.45) against all existing active tasks. Matches are flagged in the review modal as 🔁 Recurring:
- Existing task's `recurrence_count` increments (no duplicate created)
- Tasks seen 3+ times are auto-escalated to HIGH priority
- Cards show "×3 across meetings" badge

**Demo:** Process "Sprint Review" → then "Quick Standup" → recurring section appears in review modal.

---

### F4 — WhatsApp / Hinglish Voice Note Intake
A dedicated input accepts informal Hinglish transcripts. The `voice-note-transcriber` agent cleans them into structured English, pastes into the main textarea, and triggers extraction.

- Translates "arjun wala bug fix karna hai by friday" → "Arjun: Fix the bug by Friday."
- Future: WhatsApp Business API webhook integration (endpoint defined in `voice_note_intake.yaml`)

**Demo:** Paste Hinglish text → Clean & Extract → watch AI clean it → extraction auto-runs.

---

### F5 — Task Completion Guard
When an employee marks a task Done, they must write a completion note (and optionally provide a link). The `completion-verifier` agent reviews the note:
- **approved** — credibly demonstrates the task is done
- **needs_more** — too vague ("done", "fixed it") — prompts for detail
- **rejected** — describes a completely different task

Tasks that are rejected 2+ times get escalated to the founder with 🚨 badge.

---

## 📊 Live Insights Strip

A live-updating strip above the board shows real-time counts:

```
| 📋 Tasks: 8 | 🔴 Blocked: 1 | 🔁 Recurring: 2 | 🏛 Decisions: 6 | ✅ Verified: 3/8 |
```

---

## 📁 Project Structure

```
meeting-exec-pod/
├── agents/
│   ├── extractor.yaml               # action-item-extractor
│   ├── followup_drafter.yaml        # followup-drafter
│   ├── contradiction_detector.yaml  # contradiction-detector
│   ├── transcriber.yaml             # voice-note-transcriber
│   └── completion_verifier.yaml     # completion-verifier [NEW]
├── workflows/
│   ├── process_meeting.yaml         # main human-in-the-loop pipeline
│   ├── deadline_check.yaml          # daily 8 AM deadline reminders
│   ├── blocker_check.yaml           # daily 9 AM blocker escalation
│   └── voice_note_intake.yaml       # voice note → process-meeting
├── tables/
│   ├── meetings.yaml                # meeting records
│   ├── tasks.yaml                   # tasks (all feature columns)
│   ├── team_members.yaml            # team roster
│   └── decisions.yaml               # decisions for contradiction detection
├── functions/
│   ├── parse_entities.py            # date + entity resolution
│   ├── validate_tasks.py            # task validation
│   └── create_task_records.py       # persistence + recurring detection
├── apps/
│   ├── index.html                   # full Kanban app (single file, no deps)
│   └── logo.png
├── pod.json                         # Lemma pod definition (v2)
├── deploy2.py                       # bundle + deploy script
└── run_meeting.py                   # Python SDK demo script
```

---

## 🛠️ Setup & Deploy

### Prerequisites
- [Lemma CLI](https://lemma.work) installed and authenticated
- Python 3.9+ with `pyyaml` (`pip install pyyaml`)

### 1. Authenticate
```bash
lemma auth login
lemma org set 019f02d1-81b5-7705-97b1-12fc47ace383
```

### 2. Deploy Everything (One Command)
```bash
python deploy2.py
```

This bundles all tables, agents, workflows, functions, and the app into a single pod and runs:
```bash
lemma pod import my_bundle/meeting-exec-pod
```

### 3. Verify Deployed Resources
```bash
lemma table list
# meetings, tasks, team_members, decisions

lemma agent list
# action-item-extractor, followup-drafter, contradiction-detector, voice-note-transcriber, completion-verifier

lemma workflow list
# process-meeting, deadline-check, blocker-check, voice-note-intake
```

### 4. Open the App
Open `apps/index.html` in Chrome, or visit the deployed Lemma app URL.  
The app seeds demo data automatically on first load. Or press `⌘K` → "Seed Demo Data."

---

## 🎬 Demo Sequence (2 Minutes)

| Step | Action | Feature Shown |
|------|--------|---------------|
| 1 | App loads → Sprint Review tasks appear on board | Kanban board, insights strip |
| 2 | Paste Hinglish in WhatsApp box → Clean & Extract | F4: Voice Note Intake |
| 3 | Process "Quick Standup" → see 🔁 in review modal | F3: Recurring Detection |
| 4 | Process "Board Call" → see ⚠️ in review modal | F1: Contradiction Detector |
| 5 | Mark a task Blocked → type reason | F2: Blocker Detection |
| 6 | Mark a task Done → write completion note | F5: Completion Guard |

**Keyboard shortcuts:**
- `1` `2` `3` — load transcripts
- `Space` — extract tasks
- `⌘K` / `Ctrl+K` — command palette

---

## 📝 Submission Rationale

### Problem (35%)
Startups run 6–8 meetings weekly. 80% of action items die in transcripts. Exec solves three compounding execution failures: contradicted decisions, invisible blockers, and recurring tasks nobody notices. These are real, painful problems every founder recognizes immediately.

### Solution (25%)
Exec chains 5 Lemma agents in a human-in-the-loop workflow: transcribe → extract → detect contradictions → validate → human review → persist. The frontend is fully functional in mock mode (identical UX to the live Lemma API), so the demo works offline. The `completion-verifier` agent adds a new accountability layer that doesn't exist in any competing tool.

### Lemma SDK Utilisation (15%)
**4 Tables · 5 Agents · 4 Workflows · 3 Functions · 1 App.**  
The `decisions` table is a Lemma-native resource — it only exists because Lemma persists structured agent output across workflow runs. Cross-meeting contradiction detection is impossible without this. The `blocker-check` and `deadline-check` workflows use Lemma's scheduled triggers. The `process-meeting` workflow uses Lemma's human approval step to pause execution and surface data to the frontend.

### Design & UX
- 4-column Kanban (To Do / In Progress / Blocked / Done) with horizontal scroll
- Live insights strip updating across all 5 features
- Inline blocker capture on cards
- Task completion guard with AI verdict
- Conflict cards with severity + override
- Recurring panel with escalation badge
- Hinglish voice note intake with animated AI cleaning
- Command palette (`⌘K`) with keyboard shortcuts
- Dark mode toggle
- Notification system

---

*Built with ❤️ using Lemma SDK · July 2025 · v2.0*
