#!/usr/bin/env python3
"""
Interview Practice CLI
Run: python practice.py
"""
import argparse
import random
import sys

# Parse args early so --help works before heavy imports
def _build_parser():
    parser = argparse.ArgumentParser(
        prog="practice.py",
        description="Interview practice CLI — DS&A, system design, and behavioral.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
tracks:
  coding         DS&A algorithm problems (hash map, two pointers, sliding window, ...)
  system_design  Architecture and scale problems
  behavioral     STAR-format interview questions + your resume stories

examples:
  python practice.py                   # open main menu
  python practice.py --track coding    # jump straight to DS&A
  python practice.py --track behavioral

profile setup (first-time):
  cp questions/profile.example.py questions/profile.py
  # edit profile.py with your projects and story mappings
""",
    )
    parser.add_argument(
        "--track",
        choices=["coding", "system_design", "behavioral"],
        metavar="TRACK",
        help="jump directly to a track: coding | system_design | behavioral",
    )
    return parser

if __name__ == "__main__":
    _args = _build_parser().parse_args()

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.prompt import Prompt
    from rich.text import Text
    from rich.rule import Rule
except ImportError:
    print("Install rich first: pip install rich")
    sys.exit(1)

import tracker
from questions import coding, system_design, behavioral

console = Console()


# ─── HELPERS ────────────────────────────────────────────────────────────────

def clear():
    console.clear()


def pause():
    console.print()
    Prompt.ask("[dim]Press Enter to continue[/dim]", default="")


def ask_result() -> tuple[str, str]:
    console.print()
    console.print("[bold]How did it go?[/bold]")
    console.print("  [green]1[/green] Got it")
    console.print("  [yellow]2[/yellow] Struggled / need review")
    console.print("  [dim]3[/dim] Skip / don't record")
    choice = Prompt.ask("", choices=["1", "2", "3"], default="3")
    result_map = {"1": "got_it", "2": "struggled", "3": "skipped"}
    note = ""
    if choice != "3":
        note = Prompt.ask("[dim]Optional note (Enter to skip)[/dim]", default="")
    return result_map[choice], note


# ─── PROGRESS SUMMARY ────────────────────────────────────────────────────────

def show_progress():
    clear()
    console.print(Panel("[bold]Progress Summary[/bold]", style="bold blue"))
    summary = tracker.get_summary()

    table = Table(box=box.ROUNDED)
    table.add_column("Track", style="bold")
    table.add_column("Attempted", justify="right")
    table.add_column("Got It", justify="right", style="green")
    table.add_column("Needs Review", justify="right", style="yellow")

    labels = {
        "coding": "DS&A / Coding",
        "system_design": "System Design",
        "behavioral": "Behavioral",
    }
    for key, label in labels.items():
        s = summary.get(key, {})
        table.add_row(
            label,
            str(s.get("total_attempted", 0)),
            str(s.get("got_it", 0)),
            str(s.get("struggled", 0)),
        )

    console.print(table)
    console.print()

    # Show review list
    for key, label in labels.items():
        review = tracker.get_review_list(key)
        if review:
            console.print(f"[yellow]⚑ {label} — needs review:[/yellow] {', '.join(review)}")

    pause()


# ─── CODING TRACK ────────────────────────────────────────────────────────────

def show_coding_question(q: dict):
    clear()
    difficulty_color = {"easy": "green", "medium": "yellow", "hard": "red"}
    color = difficulty_color.get(q["difficulty"], "white")
    pattern_label = coding.PATTERNS.get(q["pattern"], q["pattern"])

    console.print(Panel(
        f"[bold]{q['title']}[/bold]\n"
        f"[{color}]{q['difficulty'].upper()}[/{color}]  •  Pattern: [cyan]{pattern_label}[/cyan]",
        title="[bold blue]Coding Problem[/bold blue]",
        border_style="blue",
    ))
    console.print()
    console.print(q["prompt"])
    console.print()
    console.print(Rule("[dim]Think it through before peeking[/dim]", style="dim"))

    while True:
        console.print()
        console.print("  [cyan]h[/cyan] Hint    [cyan]s[/cyan] Solution    [cyan]n[/cyan] Pattern note    [cyan]d[/cyan] Done")
        action = Prompt.ask("", choices=["h", "s", "n", "d"], default="d")

        if action == "h":
            for i, hint in enumerate(q["hints"], 1):
                console.print(Panel(f"[italic]{hint}[/italic]", title=f"Hint {i}", border_style="dim"))
                if i < len(q["hints"]):
                    more = Prompt.ask("Next hint?", choices=["y", "n"], default="y")
                    if more == "n":
                        break
        elif action == "s":
            console.print(Panel(q["solution"], title="[green]Solution[/green]", border_style="green"))
        elif action == "n":
            console.print(Panel(
                f"[bold]Pattern:[/bold] {pattern_label}\n\n{q['pattern_note']}",
                title="Pattern Note",
                border_style="cyan",
            ))
        elif action == "d":
            break

    result, note = ask_result()
    tracker.record("coding", q["id"], result, note)
    console.print(f"[dim]Recorded: {result}[/dim]")
    pause()


def coding_menu():
    while True:
        clear()
        console.print(Panel("[bold]DS&A / Coding Practice[/bold]", style="bold cyan"))

        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column(width=4)
        table.add_column()

        table.add_row("[cyan]1[/cyan]", "Random problem")
        table.add_row("[cyan]2[/cyan]", "Random easy")
        table.add_row("[cyan]3[/cyan]", "Random medium")
        table.add_row("[cyan]4[/cyan]", "Browse by pattern")
        table.add_row("[cyan]5[/cyan]", "Review problems I struggled with")
        table.add_row("[dim]b[/dim]", "[dim]Back[/dim]")

        console.print(table)
        choice = Prompt.ask("", choices=["1", "2", "3", "4", "5", "b"], default="b")

        if choice == "b":
            break
        elif choice == "1":
            q = random.choice(coding.QUESTIONS)
            show_coding_question(q)
        elif choice == "2":
            pool = [q for q in coding.QUESTIONS if q["difficulty"] == "easy"]
            show_coding_question(random.choice(pool))
        elif choice == "3":
            pool = [q for q in coding.QUESTIONS if q["difficulty"] == "medium"]
            show_coding_question(random.choice(pool))
        elif choice == "4":
            pattern_menu()
        elif choice == "5":
            review_ids = tracker.get_review_list("coding")
            if not review_ids:
                console.print("[green]Nothing marked for review![/green]")
                pause()
                continue
            pool = [q for q in coding.QUESTIONS if q["id"] in review_ids]
            if pool:
                show_coding_question(random.choice(pool))


def pattern_menu():
    clear()
    console.print(Panel("[bold]Browse by Pattern[/bold]", style="cyan"))

    patterns = list(coding.PATTERNS.items())
    for i, (key, label) in enumerate(patterns, 1):
        count = len(coding.PATTERN_GROUPS.get(key, []))
        console.print(f"  [cyan]{i}[/cyan]  {label}  [dim]({count} problems)[/dim]")
    console.print()

    choices = [str(i) for i in range(1, len(patterns) + 1)] + ["b"]
    choice = Prompt.ask("Pick a pattern (b to go back)", choices=choices, default="b")

    if choice == "b":
        return

    pattern_key = patterns[int(choice) - 1][0]
    pool = coding.get_by_pattern(pattern_key)
    if pool:
        show_coding_question(random.choice(pool))


# ─── SYSTEM DESIGN TRACK ─────────────────────────────────────────────────────

def show_sd_question(q: dict):
    clear()
    difficulty_color = {"medium": "yellow", "hard": "red"}
    color = difficulty_color.get(q["difficulty"], "white")

    console.print(Panel(
        f"[bold]{q['title']}[/bold]\n"
        f"[{color}]{q['difficulty'].upper()}[/{color}]\n\n"
        f"[dim]{q['relevance']}[/dim]",
        title="[bold magenta]System Design[/bold magenta]",
        border_style="magenta",
    ))
    console.print()
    console.print(q["prompt"])
    console.print()
    console.print(Rule(
        "[dim]Take 2-3 min to think. Use the framework. Then check hints.[/dim]",
        style="dim"
    ))

    while True:
        console.print()
        console.print("  [cyan]f[/cyan] Framework    [cyan]h[/cyan] Hints / key points    [cyan]d[/cyan] Done")
        action = Prompt.ask("", choices=["f", "h", "d"], default="d")

        if action == "f":
            console.print(Panel(
                system_design.FRAMEWORK,
                title="System Design Framework",
                border_style="blue",
            ))
        elif action == "h":
            console.print(Panel(
                q["framework_hints"],
                title="[yellow]Key Points & Hints[/yellow]",
                border_style="yellow",
            ))
        elif action == "d":
            break

    result, note = ask_result()
    tracker.record("system_design", q["id"], result, note)
    console.print(f"[dim]Recorded: {result}[/dim]")
    pause()


def system_design_menu():
    while True:
        clear()
        console.print(Panel("[bold]System Design Practice[/bold]", style="bold magenta"))

        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column(width=4)
        table.add_column()

        table.add_row("[cyan]1[/cyan]", "Random problem")
        table.add_row("[cyan]2[/cyan]", "Browse all problems")
        table.add_row("[cyan]3[/cyan]", "Show framework / cheat sheet")
        table.add_row("[cyan]4[/cyan]", "Review problems I struggled with")
        table.add_row("[dim]b[/dim]", "[dim]Back[/dim]")

        console.print(table)
        choice = Prompt.ask("", choices=["1", "2", "3", "4", "b"], default="b")

        if choice == "b":
            break
        elif choice == "1":
            q = random.choice(system_design.QUESTIONS)
            show_sd_question(q)
        elif choice == "2":
            sd_browse_menu()
        elif choice == "3":
            clear()
            console.print(Panel(system_design.FRAMEWORK, title="System Design Framework", border_style="blue"))
            pause()
        elif choice == "4":
            review_ids = tracker.get_review_list("system_design")
            if not review_ids:
                console.print("[green]Nothing marked for review![/green]")
                pause()
                continue
            pool = [q for q in system_design.QUESTIONS if q["id"] in review_ids]
            if pool:
                show_sd_question(random.choice(pool))


def sd_browse_menu():
    clear()
    console.print(Panel("[bold]System Design Problems[/bold]", style="magenta"))

    for i, q in enumerate(system_design.QUESTIONS, 1):
        diff_color = {"medium": "yellow", "hard": "red"}.get(q["difficulty"], "white")
        console.print(
            f"  [cyan]{i}[/cyan]  {q['title']}  "
            f"[{diff_color}]{q['difficulty']}[/{diff_color}]"
        )
    console.print()

    choices = [str(i) for i in range(1, len(system_design.QUESTIONS) + 1)] + ["b"]
    choice = Prompt.ask("Pick a problem (b to go back)", choices=choices, default="b")

    if choice != "b":
        q = system_design.QUESTIONS[int(choice) - 1]
        show_sd_question(q)


# ─── BEHAVIORAL TRACK ────────────────────────────────────────────────────────

def show_behavioral_question(q: dict):
    clear()
    cat_label = behavioral.CATEGORIES.get(q["category"], q["category"])

    console.print(Panel(
        f"[bold]{q['prompt']}[/bold]\n\n[dim]Category: {cat_label}[/dim]",
        title="[bold yellow]Behavioral[/bold yellow]",
        border_style="yellow",
    ))

    if q.get("follow_ups"):
        console.print()
        console.print("[dim]Common follow-ups:[/dim]")
        for fu in q["follow_ups"]:
            console.print(f"  [dim]• {fu}[/dim]")

    console.print()
    console.print(Rule("[dim]Take a moment to think in STAR format before peeking[/dim]", style="dim"))

    while True:
        console.print()
        console.print("  [cyan]c[/cyan] Coaching    [cyan]s[/cyan] Resume stories    [cyan]r[/cyan] STAR reminder    [cyan]d[/cyan] Done")
        action = Prompt.ask("", choices=["c", "s", "r", "d"], default="d")

        if action == "c":
            console.print(Panel(
                q["coaching"],
                title="[yellow]Coaching Notes[/yellow]",
                border_style="yellow",
            ))
        elif action == "s":
            story_ids = q.get("stories", [])
            if not story_ids:
                console.print("[dim]No specific stories mapped — use your judgment.[/dim]")
            else:
                for sid in story_ids:
                    story = behavioral.RESUME_STORIES.get(sid)
                    if story:
                        bullets = "\n".join(f"  • {b}" for b in story["bullets"])
                        console.print(Panel(
                            bullets,
                            title=f"[cyan]{story['label']}[/cyan]",
                            border_style="cyan",
                        ))
        elif action == "r":
            console.print(Panel(
                behavioral.STAR_REMINDER,
                title="STAR Format",
                border_style="dim",
            ))
        elif action == "d":
            break

    result, note = ask_result()
    tracker.record("behavioral", q["id"], result, note)
    console.print(f"[dim]Recorded: {result}[/dim]")
    pause()


def show_projects_directory():
    clear()
    console.print(Panel("[bold]My Projects[/bold]", style="bold cyan"))
    console.print("[dim]Press Enter after each to continue.[/dim]")
    console.print()

    for story in behavioral.RESUME_STORIES.values():
        bullets = "\n".join(f"  {b}" for b in story["bullets"])
        console.print(Panel(bullets, title=f"[bold]{story['label']}[/bold]", border_style="cyan"))
        console.print()

    pause()


def behavioral_menu():
    while True:
        clear()
        console.print(Panel("[bold]Behavioral Practice[/bold]", style="bold yellow"))

        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column(width=4)
        table.add_column()

        table.add_row("[cyan]1[/cyan]", "Random question")
        table.add_row("[cyan]2[/cyan]", "Browse by category")
        table.add_row("[cyan]3[/cyan]", "STAR format reminder")
        table.add_row("[cyan]4[/cyan]", "Review questions I struggled with")
        table.add_row("[cyan]5[/cyan]", "View my projects")
        table.add_row("[dim]b[/dim]", "[dim]Back[/dim]")

        console.print(table)
        choice = Prompt.ask("", choices=["1", "2", "3", "4", "5", "b"], default="b")

        if choice == "b":
            break
        elif choice == "1":
            q = random.choice(behavioral.QUESTIONS)
            show_behavioral_question(q)
        elif choice == "2":
            behavioral_category_menu()
        elif choice == "3":
            clear()
            console.print(Panel(behavioral.STAR_REMINDER, title="STAR Format", border_style="dim"))
            pause()
        elif choice == "4":
            review_ids = tracker.get_review_list("behavioral")
            if not review_ids:
                console.print("[green]Nothing marked for review![/green]")
                pause()
                continue
            pool = [q for q in behavioral.QUESTIONS if q["id"] in review_ids]
            if pool:
                show_behavioral_question(random.choice(pool))
        elif choice == "5":
            show_projects_directory()


def behavioral_category_menu():
    clear()
    console.print(Panel("[bold]Browse by Category[/bold]", style="yellow"))

    categories = list(behavioral.CATEGORIES.items())
    for i, (key, label) in enumerate(categories, 1):
        count = len(behavioral.get_by_category(key))
        console.print(f"  [cyan]{i}[/cyan]  {label}  [dim]({count} questions)[/dim]")
    console.print()

    choices = [str(i) for i in range(1, len(categories) + 1)] + ["b"]
    choice = Prompt.ask("Pick a category (b to go back)", choices=choices, default="b")

    if choice == "b":
        return

    cat_key = categories[int(choice) - 1][0]
    pool = behavioral.get_by_category(cat_key)
    if pool:
        show_behavioral_question(random.choice(pool))


# ─── MAIN MENU ───────────────────────────────────────────────────────────────

def main_menu():
    while True:
        clear()
        console.print(Panel(
            "[bold]Interview Practice[/bold]\n[dim]Python  •  DS&A  •  System Design  •  Behavioral[/dim]",
            border_style="bold white",
        ))
        console.print()

        table = Table(box=box.SIMPLE, show_header=False)
        table.add_column(width=4)
        table.add_column()

        table.add_row("[cyan]1[/cyan]", "[bold]DS&A / Coding[/bold]  — algorithm patterns, LeetCode-style")
        table.add_row("[cyan]2[/cyan]", "[bold]System Design[/bold]  — architecture, scale, trade-offs")
        table.add_row("[cyan]3[/cyan]", "[bold]Behavioral[/bold]     — STAR stories, your resume")
        table.add_row("[cyan]4[/cyan]", "[bold]Progress[/bold]       — what you've done, what to review")
        table.add_row("[dim]q[/dim]",  "[dim]Quit[/dim]")

        console.print(table)
        choice = Prompt.ask("\nWhat do you want to practice?", choices=["1", "2", "3", "4", "q"])

        if choice == "1":
            coding_menu()
        elif choice == "2":
            system_design_menu()
        elif choice == "3":
            behavioral_menu()
        elif choice == "4":
            show_progress()
        elif choice == "q":
            console.print("\n[dim]Good luck out there.[/dim]\n")
            break


if __name__ == "__main__":
    if _args.track == "coding":
        coding_menu()
    elif _args.track == "system_design":
        system_design_menu()
    elif _args.track == "behavioral":
        behavioral_menu()
    else:
        main_menu()
