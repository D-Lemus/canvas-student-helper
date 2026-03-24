# CanvasBot 🐛

A desktop app that connects to your Canvas LMS account, fetches your upcoming assignments, and uses an AI (via Groq) to generate a prioritized backlog for the week.

---

## What it does

- Fetches all your active courses for the current term (P2026)
- Filters assignments due within the next 30 days that haven't been submitted yet
- Displays them as cards in a clean dark-themed UI
- On demand, sends all assignments to an LLM (llama-3.3-70b via Groq) and streams back a prioritized action plan

---

## Project structure

```
canvasbot/
├── app.py              # Flet desktop UI — tabs, chat, load button
├── canvas_student.py   # Canvas API client — fetches and filters assignments
├── groq_bot.py         # Groq LLM client — builds and streams the AI response
├── analyze_json.py     # Standalone debug script for inspecting Canvas API responses
└── .env                # API credentials (not committed)
```

---

## Setup

### 1. Install dependencies

```bash
pip install flet groq requests pandas python-dotenv
```

### 2. Create a `.env` file

```env
CANVAS_URL=https://your-institution.instructure.com/
CANVAS_API_TOKEN=your_canvas_token_here
GROQ_API_TOKEN=your_groq_token_here
```

**Getting your Canvas token:** Canvas → Account → Settings → Approved Integrations → New Access Token

**Getting your Groq token:** [console.groq.com](https://console.groq.com) → API Keys

### 3. Run the app

```bash
python app.py
```

---

## How each file works

### `canvas_student.py`

| Function | Description |
|---|---|
| `obtainCourses()` | Fetches all courses where you're enrolled as a student for term `326` (P2026), returns a list of course IDs |
| `_getAssignmentsFromACourse(course_id)` | Raw Canvas API call — returns all assignments for a course ordered by due date |
| `_getDueAssignments(course_id)` | Filters to assignments that are unsubmitted and due within the next 30 days |
| `_getAssignmentInfo(course_id)` | Extracts just `{name: description}` from due assignments |
| `getAllWeekAssignments()` | Runs the full pipeline across all your courses, returns a list of dicts |

### `groq_bot.py`

| Function | Description |
|---|---|
| `startChatBot()` | Fetches all week assignments via `canvas_student`, sends them to `llama-3.3-70b-versatile`, returns a streaming response |
| `responseAnimation(response)` | CLI helper that prints streamed output letter by letter (used for terminal testing) |

### `app.py`

The Flet UI. Two tabs:

- **Tareas** — shows all upcoming assignments as cards after loading
- **Chat IA** — chat interface with a streaming AI response bubble; the ✨ button triggers the full assignment analysis

---

## Notes

- The term filter in `obtainCourses()` is hardcoded to `enrollment_term_id: 326` and course names containing `"P2026"` — update these to match your institution's term IDs
- `analyze_json.py` is a standalone debug script, not imported by the app
- The custom chat input (`_send_custom`) currently returns a placeholder response — full conversational AI is not yet wired up

---

## Future improvements

Ordered by priority:

### 1. Full conversational AI chat
The chat input is wired up but currently returns a hardcoded reply. The plan is to maintain a conversation history list and pass the full history on every Groq call, enabling real back-and-forth. Example questions the user could ask once this is live:
- "Which of these is worth the most points?"
- "Explain what this assignment is asking for"
- "How long do you think this will take me?"

This requires `groq_bot.py` to accept a `messages` list instead of building it internally, and `app.py` to accumulate that list as the conversation grows.

### 2. More Canvas data
Expand `canvas_student.py` to pull richer data so the AI has better context for prioritization:
- **Points possible** — lets the AI weigh assignments by grade impact, not just due date
- **Course name** — display which class each assignment belongs to on its card
- **Due date** — pass the actual deadline to the AI and show it on each card in the UI
- **Submission type** — file upload vs. online text vs. quiz, useful for estimating effort
- **Announcements** — surface urgent instructor messages alongside tasks so nothing is missed

### 3. Code refactor — split `app.py`
`app.py` is currently ~400 lines mixing UI layout, state management, threading, and business logic. The plan is to split it into:
- `ui/components.py` — reusable visual elements (cards, badges, palette constants)
- `ui/assignments.py` — the assignments tab and its load/fetch thread
- `ui/chat.py` — the chat tab, bubble rendering, and streaming logic
- `app.py` — thin entry point that assembles the above and calls `ft.app()`

This should be done before adding the conversational chat feature, since that will add significant complexity to the chat module.
