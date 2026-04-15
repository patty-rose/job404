# job404 — Interview Practice CLI

A terminal-based interview practice tool for software engineers. Two interfaces: a menu-driven CLI and a conversational Claude-powered TUI.

Three tracks: DS&A / coding problems, system design, and behavioral (STAR format). Your personal projects and resume stories live in a gitignored profile file — the question banks are generic and work for anyone.

---

## Setup

**Run the CLI in Docker (no local dependencies needed)**

```bash
make build   # build the image
make         # run
```

**Personal profile (required for behavioral track)**

```bash
cp questions/profile.example.py questions/profile.py
```

Edit `profile.py` with your own projects and resume stories. This file is gitignored — it never leaves your machine.

**Claude TUI only — authenticate the CLI**

```bash
# Install the Claude CLI, then:
claude login
```

---

## Usage

### CLI (`practice.py`)

```bash
python practice.py                   # main menu
python practice.py --track coding    # jump straight to DS&A
python practice.py --track system_design
python practice.py --track behavioral
python practice.py --help
```

Menu navigation uses number keys. Within a question:

| Key | Action |
|-----|--------|
| `h` | Hint (coding) / Framework (system design) |
| `s` | Solution (coding) / Key points (system design) / Your stories (behavioral) |
| `c` | Coaching notes (behavioral) |
| `r` | STAR format reminder (behavioral) |
| `d` | Done — record result |

After each question: rate yourself (`got it` / `struggled` / `skip`). Struggled questions are queued for review.

### Claude TUI (`tui.py`)

```bash
./tui.sh        # recommended (manages venv automatically)
python tui.py   # or run directly if deps are installed
python tui.py --help
```

Split-screen layout: question panel | code editor | Claude chat.

| Keybinding | Action |
|------------|--------|
| `Enter` | Send message to Claude |
| `Ctrl+Return` | Run code in editor |
| `Ctrl+K` | Send editor code to Claude for review |
| `Ctrl+_` | Toggle line comment |
| `Escape` | Clear input |
| `Ctrl+C` | Quit |

Claude acts as an interview coach — ask it for a question, get hints Socratically, paste your code for review. It tracks your results automatically.

---

## Tracks

### DS&A / Coding
Algorithm problems organized by pattern (hash map, two pointers, sliding window, stack, binary search, BFS/DFS, SQL, REST APIs). Each problem includes hints, a full solution with complexity analysis, and a pattern note.

Browse randomly, by difficulty, or by pattern. Struggling questions get queued for review sessions.

### System Design
Architecture problems with a shared design framework (requirements → scale → components → trade-offs). Each problem includes framework hints tied to the approach.

### Behavioral
STAR-format interview questions across six categories: intro, motivation, technical skills, project deep dives, teamwork, and situational. Each question has coaching notes and links to your resume stories from `profile.py`.

Press `s` during practice to pull up your mapped project stories as reference material.

---

## Personalizing for your own use

**Projects / resume stories** — edit `questions/profile.py`:

```python
RESUME_STORIES = {
    "my_project": {
        "label": "Project Name — Company",
        "bullets": [
            "Situation: ...",
            "Action: ...",
            "Result: ...",
        ],
    },
}

QUESTION_STORIES = {
    "project_proud_of": ["my_project"],
    # map question IDs to story IDs
}
```

**Adding questions** — edit the relevant file in `questions/`:
- `coding.py` — add to `QUESTIONS`, pick a `pattern` from `PATTERNS`
- `system_design.py` — add to `QUESTIONS`
- `behavioral.py` — add to `QUESTIONS` with `id`, `prompt`, `category`, `coaching`, `follow_ups`, `stories`

**Progress tracking** — stored in `data/progress.json` (gitignored). View it from the main menu → Progress, or reset by deleting the file.

---

## Project structure

```
practice.py               menu-driven CLI
tui.py                    Claude TUI (split-screen)
tracker.py                progress tracking (JSON)
questions/
  coding.py               DS&A question bank
  system_design.py        system design question bank
  behavioral.py           behavioral question bank (generic)
  profile.example.py      personal profile template
  profile.py              your profile (gitignored)
data/
  progress.json           your practice history (gitignored)
practice.sh               Docker runner for CLI
tui.sh                    venv runner for TUI
```
