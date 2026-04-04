#!/usr/bin/env python3
"""
Interview Practice TUI — conversational Claude coach in a split screen.

Run:
    python tui.py

Requires (in addition to existing deps):
    pip install anthropic textual
"""
import json
import os
import sys

try:
    import anthropic
except ImportError:
    print("pip install anthropic")
    sys.exit(1)

try:
    from textual.app import App, ComposeResult
    from textual.widgets import Input, RichLog, Static, Footer, Header
    from textual.containers import Horizontal, Vertical
    from textual import on, work
    from textual.binding import Binding
except ImportError:
    print("pip install textual")
    sys.exit(1)

from pathlib import Path
from rich.panel import Panel

# Load .env from project root if present (for `python3 tui.py` usage)
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())
from rich.markdown import Markdown
import tracker
from questions import coding, system_design, behavioral


# ── Question catalog (goes into Claude's system prompt) ──────────────────────

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


# ── Tool schemas ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "display_question",
        "description": (
            "Render a question in the left panel so the user can read it while they work. "
            "Call this every time you want to present a specific question."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "track": {
                    "type": "string",
                    "enum": ["coding", "system_design", "behavioral"],
                },
                "question_id": {"type": "string"},
            },
            "required": ["track", "question_id"],
        },
    },
    {
        "name": "record_result",
        "description": "Save the user's outcome for a question to their progress tracker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["coding", "system_design", "behavioral"],
                },
                "question_id": {"type": "string"},
                "result": {
                    "type": "string",
                    "enum": ["got_it", "struggled", "skipped"],
                },
                "note": {
                    "type": "string",
                    "description": "Optional note about the attempt",
                },
            },
            "required": ["category", "question_id", "result"],
        },
    },
]


SYSTEM_PROMPT = """\
You are an embedded interview coach inside a terminal practice app. \
The user is a mid-level software engineer preparing for backend / devops roles.

Your job:
- Help the user pick and work through coding, system design, and behavioral questions.
- When presenting a question, ALWAYS call `display_question` so it appears in the left panel.
- Give hints Socratically — ask guiding questions before revealing answers. \
  Offer the next hint only if they ask.
- If the user pastes code, review it: find bugs, point out edge cases, suggest improvements.
- When the user signals they're done with a question \
  ("got it", "struggled", "done", "next", "skip", etc.), call `record_result` \
  then ask what they want to do next.
- Keep responses concise. Only elaborate when the user asks.
- Be encouraging but direct.

Here is the complete question catalog:

{catalog}
"""


# ── Helpers ──────────────────────────────────────────────────────────────────

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


# ── App ──────────────────────────────────────────────────────────────────────

class PracticeApp(App):
    CSS = """
    #main {
        height: 1fr;
    }

    #question-panel {
        width: 44%;
        height: 100%;
        overflow-y: auto;
        padding: 1 2;
        border-right: tall $primary-darken-3;
    }

    #chat-side {
        width: 56%;
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
        Binding("escape", "clear_input", "Clear input"),
    ]

    def __init__(self):
        super().__init__()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Set ANTHROPIC_API_KEY first.")
            sys.exit(1)
        self.client = anthropic.Anthropic()
        self.conv: list[dict] = []
        self.system_prompt = SYSTEM_PROMPT.format(catalog=_build_catalog())
        self.current_question: tuple[str, str] | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Horizontal(id="main"):
            yield Static(
                "[dim]No question loaded yet.\nAsk Claude for one![/dim]",
                id="question-panel",
            )
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

    # ── Workers ──────────────────────────────────────────────────────────────

    @work(thread=True)
    def _greet(self) -> None:
        """Get Claude's opening message on startup."""
        init = [{"role": "user", "content": "Hi! I'm ready to practice."}]
        try:
            resp = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=512,
                system=self.system_prompt,
                messages=init,
            )
        except Exception as e:
            self.call_from_thread(lambda: self._show("System", f"API error: {e}"))
            self.call_from_thread(self._enable_input)
            return
        text = " ".join(b.text for b in resp.content if b.type == "text")
        self.conv.extend([init[0], {"role": "assistant", "content": resp.content}])
        self.call_from_thread(lambda t=text: self._show("Claude", t))
        self.call_from_thread(self._enable_input)

    @work(thread=True)
    def _chat(self, user_text: str) -> None:
        """Send a message, handle tool calls, update UI."""
        self.conv.append({"role": "user", "content": user_text})
        try:
            self._claude_loop()
        except Exception as e:
            self.call_from_thread(lambda: self._show("System", f"API error: {e}"))
        self.call_from_thread(self._enable_input)

    def _claude_loop(self) -> None:
        """Run the Claude request/tool-call loop (runs in worker thread)."""
        while True:
            resp = self.client.messages.create(
                model="claude-opus-4-6",
                max_tokens=2048,
                system=self.system_prompt,
                messages=self.conv,
                tools=TOOLS,
            )
            self.conv.append({"role": "assistant", "content": resp.content})

            text_blocks = [b for b in resp.content if b.type == "text"]
            tool_blocks = [b for b in resp.content if b.type == "tool_use"]

            if text_blocks:
                msg = "\n".join(b.text for b in text_blocks)
                self.call_from_thread(lambda m=msg: self._show("Claude", m))

            if not tool_blocks:
                break

            results = []
            for tb in tool_blocks:
                result_text = self._run_tool(tb.name, tb.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tb.id,
                    "content": result_text,
                })
            self.conv.append({"role": "user", "content": results})

            if resp.stop_reason != "tool_use":
                break

    def _run_tool(self, name: str, inputs: dict) -> str:
        """Execute a tool call (runs in worker thread; UI updates via call_from_thread)."""
        if name == "display_question":
            track = inputs["track"]
            qid = inputs["question_id"]
            q = _find_question(track, qid)
            if q is None:
                return f"Question '{qid}' not found in track '{track}'."
            self.current_question = (track, qid)
            panel = _render_question_panel(track, q)
            self.call_from_thread(
                lambda p=panel: self.query_one("#question-panel", Static).update(p)
            )
            return "Question displayed."

        if name == "record_result":
            tracker.record(
                inputs["category"],
                inputs["question_id"],
                inputs["result"],
                inputs.get("note", ""),
            )
            return f"Recorded: {inputs['result']}."

        return f"Unknown tool: {name}"

    # ── UI helpers (must run on main thread) ─────────────────────────────────

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

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":
    PracticeApp().run()
