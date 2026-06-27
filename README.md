# ⚡ Exec — Meeting to Action

> **Lemma Hackathon Submission** · Built by Swaraj Keshav Gawde

**Exec** is a Lemma-powered agentic operator that turns raw meeting transcripts into tracked, owned, deadline-bound action items — in under 30 seconds.

---

## 🎯 The Problem

Startups run 6–8 meetings a week, but **80% of action items die** in Google Docs or Otter.ai transcripts. The bottleneck isn't the project management tool — Notion and Linear work fine. The bottleneck is the **manual translation step**: reading a 20-minute transcript, identifying tasks, creating tickets, and assigning owners. It takes 15 minutes per meeting, so nobody does it.

---

## 🧠 The Solution

**Exec** is a Lemma-powered operator that sits downstream of transcription tools.

```
Transcript in
     ↓
action-item-extractor agent (Claude via Lemma)
     ↓
deterministic validation functions (owners, deadlines, priority)
     ↓
Workflow pauses → Human approval step (HUMAN-IN-THE-LOOP)
     ↓
Founder reviews 5 tasks in 30 seconds, fixes missing owners/deadlines
     ↓
Tasks committed to Lemma datastore → Execution board
     ↓
deadline-check workflow → followup-drafter agent → Slack reminders
```

---

## 🏗️ Lemma SDK Utilisation

| Resource | Name | Purpose |
|---|---|---|
| 📋 Table | `meetings` | Stores processed meeting records |
| 📋 Table | `tasks` | Stores all extracted action items |
| 📋 Table | `team_members` | Team roster for owner resolution |
| 🤖 Agent | `action-item-extractor` | Claude extracts tasks from transcript |
| 🤖 Agent | `followup-drafter` | Drafts Slack reminders for deadlines |
| ⚡ Workflow | `process-meeting` | End-to-end extraction + approval pipeline |
| ⚡ Workflow | `deadline-check` | Daily scan for overdue tasks |
| 🖥️ App | `apps/index.html` | Full frontend, connects to Lemma API |

The **entire application state lives in Lemma**. The frontend makes direct API calls to the Lemma stack for every read/write. It does not function without Lemma.

---

## 💡 What I Said No To

**I did not build transcription.** Otter.ai and Zoom already solve this perfectly. Rebuilding it would consume 80% of my time on a solved problem. I built the **unsolved 10%: the execution layer**.

I also chose a **status dropdown over pure drag-and-drop Kanban** for the demo. Drag-and-drop looks flashy but can break under live demo conditions. A dropdown achieves the exact same state change with zero friction.

---

## 🚀 Features

- **🤖 Live Agent Pipeline Visualizer** — watch the Lemma workflow execute step-by-step
- **💻 AI Thought Stream** — hacker terminal shows the agent reasoning in real-time
- **👤 Human-in-the-Loop Modal** — flags missing owners/deadlines for human review before saving
- **📊 Team Analytics Dashboard** — priority donut chart + team workload bars
- **🖱️ Drag & Drop Kanban** — move tasks between To Do / In Progress / Done
- **🎤 Voice Input** — speak meeting notes directly (Chrome)
- **💬 Slack Reminder Preview** — AI drafts followup messages via `followup-drafter` agent
- **⌨️ Command Palette** — `⌘K` or `/` to access all actions with keyboard shortcuts

---

## 📁 Pod Structure

```
meeting-exec-pod/
├── agents/
│   ├── extractor.yaml          # action-item-extractor agent
│   └── followup_drafter.yaml   # followup-drafter agent
├── workflows/
│   ├── process_meeting.yaml    # main extraction + approval workflow
│   └── deadline_check.yaml     # daily deadline monitoring workflow
├── tables/
│   ├── meetings.yaml           # meetings table schema
│   ├── tasks.yaml              # tasks table schema
│   └── team_members.yaml       # team roster table schema
├── apps/
│   ├── index.html              # full frontend app
│   └── logo.png                # app logo
├── functions/
│   └── validate_tasks.py       # date parsing + validation logic
├── pod.json                    # Lemma pod definition (format_version: 2)
└── run_meeting.py              # Python SDK demo script
```

---

## 🛠️ Setup & Run

### Prerequisites
- [Lemma CLI](https://lemma.work) installed and authenticated
- OpenAI or Anthropic API key configured

### 1. Authenticate
```bash
lemma auth login
```

### 2. Set your org
```bash
lemma org set 019f02d1-81b5-7705-97b1-12fc47ace383
```

### 3. Resources are already deployed on your Pod
```
Pod ID: 019f02e7-32c2-7248-8122-44ee70a2f0ff
```

Verify with:
```bash
lemma table list
lemma agent list
lemma workflow list
```

### 4. Open the app
```
apps/index.html → open in Chrome
```

### 5. Demo sequence
1. Click **"Sprint Review"** to load a sample transcript
2. Watch the transcript type out
3. Click **"⚡ Extract Tasks with AI →"**
4. Watch the Lemma agent pipeline + thought stream
5. See the **Review Modal** — note the flagged tasks with missing info
6. Fix the flagged task (type an owner name or date)
7. Click **"✓ Confirm Tasks"**
8. Watch cards appear one-by-one on the Kanban board
9. Click **"Remind"** on any card to see the Slack preview

---

## 📝 Submission Rationale

### Problem (35%)
Startups run 6–8 meetings a week, but 80% of action items die in Google Docs or Otter.ai transcripts. The bottleneck isn't the project management tool — Notion and Linear work fine. The bottleneck is the manual translation step: reading a 20-minute transcript, identifying tasks, creating tickets, and assigning owners. It takes 15 minutes per meeting, so nobody does it.

### Solution (25%)
Exec is a Lemma-powered operator that sits downstream of transcription tools. A transcript flows in, an LLM agent extracts structured tasks, deterministic functions parse relative dates ("Friday" → 2025-07-04) and validate completeness, and a workflow pauses at a human approval step. The founder reviews 5 AI-extracted tasks in 30 seconds — fixing missing owners or deadlines — before they hit the execution board.

### What I Said No To
I did not build transcription. Otter.ai and Zoom already solve this perfectly; rebuilding it would consume 80% of my time on a solved problem. I built the unsolved 10%: the execution layer. I also chose a status dropdown over drag-and-drop Kanban. Drag-and-drop looks flashy but breaks during live demos. A dropdown achieves the exact same state change with zero friction.

### Lemma SDK Utilisation (15%)
The entire state of the application lives in Lemma. 3 Tables (tasks, team_members, meetings), 2 Agents (extraction, follow-up drafting), 2 Workflows (process-meeting with Approval step, deadline-check), and 1 App. The frontend makes direct calls to the Lemma API for every read/write operation. It does not use localStorage as a primary store. It does not function without Lemma.

---

## ✅ Pre-Submit Checklist

- [x] Dark theme (`#0B0E13` background, `#1A2028` cards)
- [x] HIGH badge is red pill (`rgba(248,81,73,0.15)`, `color: #F85149`)
- [x] Owner color dots on every task card and modal chip
- [x] Review Modal has ⚠️ attention banner for flagged tasks
- [x] Inline fix inputs for missing owner/deadline IN the modal
- [x] "Human-in-the-loop approval · powered by Lemma" footer
- [x] Empty states show muted hint text
- [x] Lemma tables, agents, workflows all deployed
- [x] Demo sequence practised (Board Call → Sprint Review → modal → board)

---

*Built with ❤️ using Lemma SDK · June 2025*
