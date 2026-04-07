#!/usr/bin/env python3
"""
Interview Practice TUI — conversational Claude coach in a split screen.

Run:
    python tui.py

Requires:
    pip install textual
    claude CLI installed and authenticated (claude.ai/code)
"""
import json
import os
import re
import subprocess
import sys
import tempfile

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Input, RichLog, Static, Footer, Header, TextArea
    from textual.containers import Horizontal, Vertical
    from textual import on, work
    from textual.binding import Binding
except ImportError:
    print("pip install textual")
    sys.exit(1)

from rich.panel import Panel
from rich.markdown import Markdown
import tracker
from questions import coding, system_design, behavioral


# ── Question catalog ──────────────────────────────────────────────────────────

def _build_catalog() -> str:
    coding_qs = [
        {
            "id": q["id"],
            "title": q["title"],
            "difficulty": q["difficulty"],
            "pattern": coding.PATTERNS.get(q["pattern"], q["pattern"]),
            "prompt": q["prompt"],
            "hints": q["hints"],
            "solution": q["solution"],
            "pattern_note": q.get("pattern_note", ""),
        }
        for q in coding.QUESTIONS
    ]
    sd_qs = [
        {
            "id": q["id"],
            "title": q["title"],
            "difficulty": q["difficulty"],
            "prompt": q["prompt"],
            "framework_hints": q["framework_hints"],
            "relevance": q.get("relevance", ""),
        }
        for q in system_design.QUESTIONS
    ]
    beh_qs = [
        {
            "id": q["id"],
            "category": behavioral.CATEGORIES.get(q["category"], q["category"]),
            "prompt": q["prompt"],
            "coaching": q["coaching"],
            "follow_ups": q.get("follow_ups", []),
        }
        for q in behavioral.QUESTIONS
    ]
    return (
        f"### Coding Questions\n{json.dumps(coding_qs, indent=2)}\n\n"
        f"### System Design Questions\n{json.dumps(sd_qs, indent=2)}\n\n"
        f"### Behavioral Questions\n{json.dumps(beh_qs, indent=2)}"
    )


# ── XML action tags ───────────────────────────────────────────────────────────
# Claude emits these tags in its response to trigger app-side actions.

_DISPLAY_RE = re.compile(
    r'<display_question\s+track="([^"]+)"\s+question_id="([^"]+)"\s*/?>',
    re.IGNORECASE,
)
_RECORD_RE = re.compile(
    r'<record_result\s+category="([^"]+)"\s+question_id="([^"]+)"\s+result="([^"]+)"'
    r'(?:\s+note="([^"]*)")?\s*/?>',
    re.IGNORECASE,
)
_ANY_ACTION_TAG = re.compile(
    r'<(?:display_question|record_result)[^>]*/?>',
    re.IGNORECASE,
)


def _parse_actions(text: str) -> tuple[str, list[dict]]:
    """Extract action tags from text. Returns (cleaned_text, list_of_actions)."""
    actions: list[dict] = []
    for m in _DISPLAY_RE.finditer(text):
        actions.append({
            "type": "display_question",
            "track": m.group(1),
            "question_id": m.group(2),
        })
    for m in _RECORD_RE.finditer(text):
        actions.append({
            "type": "record_result",
            "category": m.group(1),
            "question_id": m.group(2),
            "result": m.group(3),
            "note": m.group(4) or "",
        })
    clean = _ANY_ACTION_TAG.sub("", text).strip()
    return clean, actions


# ── Coach context (prepended to the opening message only) ────────────────────

_CONTEXT_TEMPLATE = """\
[COACH CONTEXT — instructions for you, not shown to user]

You are an embedded interview coach in a split-screen terminal TUI. \
The user is a mid-level software engineer preparing for backend/devops roles.

To trigger app actions, emit XML tags on their own line in your response:

  Show a question in the left panel:
    <display_question track="TRACK" question_id="QUESTION_ID"/>
    track: coding | system_design | behavioral

  Save the user's result to their tracker:
    <record_result category="CATEGORY" question_id="QUESTION_ID" result="RESULT" note="OPTIONAL"/>
    result: got_it | struggled | skipped

Rules:
- Always emit <display_question .../> when presenting a question.
- Emit <record_result .../> when the user signals they are done \
("got it", "struggled", "done", "next", "skip", etc.).
- Give hints Socratically — ask guiding questions, don't just reveal answers.
- If the user pastes code, review it: spot bugs, edge cases, suggest improvements.
- Be concise. The question is already visible in the left panel once displayed.
- After the user solves a question (or gives up), before moving on: ask them \
to state the time and space complexity of their solution, then ask 1-2 realistic \
interview follow-up questions (e.g. "what if the input doesn't fit in memory?", \
"can you do it in-place?", "how would this scale?"). Only move to a new question \
after this debrief is done.
- After recording a result, do NOT ask to retry immediately. Just acknowledge and \
move on. Struggled questions are automatically queued for future sessions.

Question catalog:
{catalog}

[END CONTEXT]

"""


# ── Claude subprocess ─────────────────────────────────────────────────────────

def _claude(prompt: str, session_id: str | None = None) -> tuple[str, str]:
    """
    Run `claude -p <prompt>` and return (response_text, session_id).
    Raises RuntimeError on failure.
    """
    cmd = ["claude", "-p", prompt, "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]

    proc = subprocess.run(cmd, capture_output=True, text=True)

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(err or f"claude exited with code {proc.returncode}")

    try:
        data = json.loads(proc.stdout)
        text = data.get("result", "")
        sid = data.get("session_id", session_id or "")
    except (json.JSONDecodeError, AttributeError):
        text = proc.stdout.strip()
        sid = session_id or ""

    return text, sid


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_stub(q: dict) -> str:
    """Extract the first def line from the solution and return a runnable stub."""
    sig = None
    for line in q.get("solution", "").splitlines():
        stripped = line.strip()
        if stripped.startswith("def "):
            sig = stripped
            break
    if not sig:
        title = q.get("title", "solve").lower().replace(" ", "_")
        sig = f"def {title}():"
    stub = f"{sig}\n    # your solution here\n    pass\n"
    if example := q.get("example_call"):
        stub += f"\n\n{example}\n"
    return stub


def _find_question(track: str, qid: str) -> dict | None:
    bank = {
        "coding": coding.QUESTIONS,
        "system_design": system_design.QUESTIONS,
        "behavioral": behavioral.QUESTIONS,
    }.get(track, [])
    return next((q for q in bank if q["id"] == qid), None)


def _render_question_panel(track: str, q: dict) -> Panel:
    if track == "coding":
        diff_color = {"easy": "green", "medium": "yellow", "hard": "red"}.get(
            q["difficulty"], "white"
        )
        pattern_label = coding.PATTERNS.get(q["pattern"], q["pattern"])
        body = (
            f"[bold]{q['title']}[/bold]\n"
            f"[{diff_color}]{q['difficulty'].upper()}[/{diff_color}]"
            f"  •  Pattern: [cyan]{pattern_label}[/cyan]\n\n"
            f"{q['prompt']}"
        )
        return Panel(body, title="[bold blue]Coding[/bold blue]", border_style="blue")

    if track == "system_design":
        diff_color = {"medium": "yellow", "hard": "red"}.get(q["difficulty"], "white")
        body = (
            f"[bold]{q['title']}[/bold]\n"
            f"[{diff_color}]{q['difficulty'].upper()}[/{diff_color}]\n\n"
            f"[dim]{q.get('relevance', '')}[/dim]\n\n"
            f"{q['prompt']}"
        )
        return Panel(body, title="[bold magenta]System Design[/bold magenta]", border_style="magenta")

    # behavioral
    cat_label = behavioral.CATEGORIES.get(q.get("category", ""), q.get("category", ""))
    body = f"[bold]{q['prompt']}[/bold]\n\n[dim]Category: {cat_label}[/dim]"
    if q.get("follow_ups"):
        body += "\n\n[dim]Follow-ups:[/dim]"
        for fu in q["follow_ups"]:
            body += f"\n  [dim]• {fu}[/dim]"
    return Panel(body, title="[bold yellow]Behavioral[/bold yellow]", border_style="yellow")


# ── App ───────────────────────────────────────────────────────────────────────

class PracticeApp(App):
    CSS = """
    #main {
        height: 1fr;
    }

    #question-panel {
        width: 30%;
        height: 100%;
        overflow-y: auto;
        padding: 1 2;
        border-right: tall $primary-darken-3;
    }

    #code-panel {
        width: 40%;
        height: 100%;
        border-right: tall $primary-darken-3;
    }

    #code-editor {
        height: 1fr;
    }

    #code-output {
        height: 10;
        border-top: tall $primary-darken-3;
        padding: 0 1;
    }

    #chat-side {
        width: 30%;
        height: 100%;
    }

    #chat-log {
        height: 1fr;
        padding: 1 2;
    }

    #chat-input {
        height: 3;
        border-top: tall $primary-darken-3;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit", priority=True),
        Binding("ctrl+return", "run_code", "Run code", priority=True),
        Binding("ctrl+k", "send_code", "Send code to Claude", priority=True),
        Binding("ctrl+underscore", "toggle_comment", "Toggle comment", priority=True),
        Binding("escape", "clear_input", "Clear input"),
    ]

    def __init__(self):
        super().__init__()
        self.session_id: str | None = None
        self.current_question: tuple[str, str] | None = None
        self._opening = _CONTEXT_TEMPLATE.format(catalog=_build_catalog())
        self._opening += "Hi! I'm ready to practice."

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="main"):
            yield Static(
                "[dim]No question loaded yet.\nAsk Claude for one![/dim]",
                id="question-panel",
            )
            with Vertical(id="code-panel"):
                yield TextArea("", language="python", tab_behavior="indent", id="code-editor")
                yield RichLog(id="code-output", wrap=True, markup=True, highlight=False)
            with Vertical(id="chat-side"):
                yield RichLog(id="chat-log", wrap=True, markup=True, highlight=False)
                yield Input(
                    placeholder="Ask Claude anything…  (Enter to send)",
                    id="chat-input",
                )
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Interview Practice"
        self.sub_title = "powered by Claude"
        self.query_one("#chat-input", Input).disabled = True
        self._greet()

    # ── Workers ───────────────────────────────────────────────────────────────

    @work(thread=True)
    def _greet(self) -> None:
        try:
            text, sid = _claude(self._opening)
        except RuntimeError as e:
            self.call_from_thread(lambda: self._show("System", f"Error: {e}"))
            self.call_from_thread(self._enable_input)
            return
        self.session_id = sid
        clean, actions = _parse_actions(text)
        self._dispatch_actions(actions)
        if clean:
            self.call_from_thread(lambda t=clean: self._show("Claude", t))
        self.call_from_thread(self._enable_input)

    @work(thread=True)
    def _chat(self, user_text: str) -> None:
        try:
            text, sid = _claude(user_text, self.session_id)
        except RuntimeError as e:
            self.call_from_thread(lambda: self._show("System", f"Error: {e}"))
            self.call_from_thread(self._enable_input)
            return
        self.session_id = sid
        clean, actions = _parse_actions(text)
        self._dispatch_actions(actions)
        if clean:
            self.call_from_thread(lambda t=clean: self._show("Claude", t))
        self.call_from_thread(self._enable_input)

    def _dispatch_actions(self, actions: list[dict]) -> None:
        """Handle action tags parsed from Claude's response (called in worker thread)."""
        for action in actions:
            if action["type"] == "display_question":
                q = _find_question(action["track"], action["question_id"])
                if q:
                    self.current_question = (action["track"], action["question_id"])
                    panel = _render_question_panel(action["track"], q)
                    self.call_from_thread(
                        lambda p=panel: self.query_one("#question-panel", Static).update(p)
                    )
                    if action["track"] == "coding":
                        stub = _make_stub(q)
                        self.call_from_thread(
                            lambda s=stub: self.query_one("#code-editor", TextArea).load_text(s)
                        )
            elif action["type"] == "record_result":
                tracker.record(
                    action["category"],
                    action["question_id"],
                    action["result"],
                    action.get("note", ""),
                )

    # ── UI helpers ────────────────────────────────────────────────────────────

    def _show(self, speaker: str, text: str) -> None:
        log = self.query_one("#chat-log", RichLog)
        if speaker == "Claude":
            log.write("[bold cyan]Claude[/bold cyan]")
            log.write(Markdown(text))
        elif speaker == "You":
            log.write(f"[bold green]You[/bold green]  {text}")
        else:
            log.write(f"[dim]{speaker}: {text}[/dim]")
        log.write(" ")

    def _enable_input(self) -> None:
        inp = self.query_one("#chat-input", Input)
        inp.disabled = False
        inp.focus()

    # ── Event handlers ────────────────────────────────────────────────────────

    @on(Input.Submitted, "#chat-input")
    def handle_submit(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        event.input.value = ""
        event.input.disabled = True
        self._show("You", text)
        self._chat(text)

    def action_clear_input(self) -> None:
        self.query_one("#chat-input", Input).value = ""

    def action_run_code(self) -> None:
        self._run_code()

    @work(thread=True)
    def _run_code(self) -> None:
        code = self.query_one("#code-editor", TextArea).text
        out_log = self.query_one("#code-output", RichLog)
        self.call_from_thread(out_log.clear)
        self.call_from_thread(lambda: out_log.write("[dim]Running…[/dim]"))

        fname = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                fname = f.name
            result = subprocess.run(
                ["python3", fname], capture_output=True, text=True, timeout=10
            )
            self.call_from_thread(out_log.clear)
            if result.stdout:
                self.call_from_thread(lambda o=result.stdout: out_log.write(o.rstrip()))
            if result.stderr:
                self.call_from_thread(lambda e=result.stderr: out_log.write(f"[red]{e.rstrip()}[/red]"))
            if not result.stdout and not result.stderr:
                self.call_from_thread(lambda: out_log.write("[dim](no output)[/dim]"))
        except subprocess.TimeoutExpired:
            self.call_from_thread(lambda: out_log.write("[red]Timed out after 10s[/red]"))
        except Exception as e:
            self.call_from_thread(lambda err=e: out_log.write(f"[red]Error: {err}[/red]"))
        finally:
            if fname:
                try:
                    os.unlink(fname)
                except OSError:
                    pass

    def action_toggle_comment(self) -> None:
        editor = self.query_one("#code-editor", TextArea)
        row, col = editor.cursor_location
        lines = editor.text.split("\n")
        if row >= len(lines):
            return
        line = lines[row]
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("# "):
            lines[row] = indent + stripped[2:]
            new_col = max(0, col - 2)
        elif stripped.startswith("#"):
            lines[row] = indent + stripped[1:]
            new_col = max(0, col - 1)
        else:
            lines[row] = indent + "# " + stripped
            new_col = col + 2
        editor.load_text("\n".join(lines))
        editor.move_cursor((row, new_col))

    def action_send_code(self) -> None:
        code = self.query_one("#code-editor", TextArea).text.strip()
        if not code:
            return
        msg = f"Here's my code:\n```python\n{code}\n```"
        self._show("You", msg)
        inp = self.query_one("#chat-input", Input)
        inp.disabled = True
        self._chat(msg)

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    PracticeApp().run()
