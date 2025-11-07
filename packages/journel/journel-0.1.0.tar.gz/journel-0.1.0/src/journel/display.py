"""Display and formatting utilities using Rich."""

import sys
from datetime import date
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn

from .models import Project, Session
from .utils import format_date_relative


# Configure console for cross-platform compatibility
console = Console()


def _can_render_emoji() -> bool:
    """Check if terminal can render emoji.

    Returns False on Windows if the terminal encoding can't handle Unicode.
    """
    try:
        # Check if stdout has proper encoding
        encoding = getattr(sys.stdout, 'encoding', 'utf-8')
        if encoding is None:
            return False

        # Try to encode an emoji
        test_emoji = "🔥"
        test_emoji.encode(encoding)
        return True
    except (UnicodeEncodeError, AttributeError, LookupError):
        return False


# Auto-detect emoji support
_EMOJI_SUPPORT = _can_render_emoji()

# Emoji mappings (can be disabled via config)
EMOJIS = {
    "fire": "🔥",
    "sleep": "💤",
    "check": "✅",
    "bulb": "💡",
    "warning": "⚠️",
    "party": "🎉",
    "star": "🌟",
}

ASCII_FALLBACKS = {
    "fire": ">>",
    "sleep": "--",
    "check": "[DONE]",
    "bulb": "[TIP]",
    "warning": "[!]",
    "party": "***",
    "star": "*",
}


def get_icon(name: str, use_emojis: bool = True) -> str:
    """Get an icon (emoji or ASCII fallback).

    Automatically uses ASCII if terminal doesn't support emoji,
    even if use_emojis is True.
    """
    # Auto-fallback to ASCII if terminal can't render emoji
    if use_emojis and _EMOJI_SUPPORT:
        return EMOJIS.get(name, "")
    return ASCII_FALLBACKS.get(name, "")


def format_completion(completion: int, show_bar: bool = False, width: int = 10) -> str:
    """Format completion percentage with color coding.

    Args:
        completion: Completion percentage (0-100)
        show_bar: If True, include a progress bar
        width: Width of the progress bar in characters

    Returns:
        Formatted string with color markup
    """
    # Color coding based on completion
    if completion >= 80:
        color = "green"
    elif completion >= 40:
        color = "yellow"
    else:
        color = "red"

    if show_bar:
        # Create simple text-based progress bar using ASCII-safe characters
        filled = int(completion / 10)  # 0-10 blocks
        bar = "#" * filled + "-" * (10 - filled)
        return f"[{color}]{completion:>3}%[/{color}] [{color}][{bar}][/{color}]"
    else:
        return f"[{color}]{completion:>3}%[/{color}]"


def print_welcome() -> None:
    """Print welcome message after init."""
    welcome = """
[bold green]Welcome to JOURNEL![/bold green]

Your ADHD-friendly project tracking system is ready.

[bold]Quick start:[/bold]
  jnl new <project>    Create your first project
  jnl                  Check status
  jnl log "message"    Log what you're working on
  jnl ctx              Get context for AI assistance

[dim]JOURNEL data is stored in ~/.journel/
All files are plain markdown - edit them anytime![/dim]
"""
    console.print(Panel(welcome, border_style="green"))


def print_status(projects: List[Project], config, active_session: Optional['Session'] = None) -> None:
    """Print project status overview.

    Args:
        projects: List of projects to display
        config: Configuration dict
        active_session: Optional active session to display at top
    """
    # Get config values early
    use_emojis = config.get("use_emojis", True)
    dormant_days = config.get("dormant_days", 14)

    # Show active session first if present
    if active_session:
        elapsed = active_session.elapsed_time()
        hours = elapsed.total_seconds() / 3600
        # Use simple [TIME] prefix if emojis not supported
        time_icon = "⏱ " if _EMOJI_SUPPORT and use_emojis else "[TIME] "
        console.print(f"\n[yellow]{time_icon} Active Session:[/yellow] [bold]{active_session.project_id}[/bold] ({_format_time_duration(elapsed)})")
        if active_session.task:
            console.print(f"    Task: {active_session.task}")
        console.print(f"    [dim]Stop: jnl stop | Pause: jnl pause[/dim]\n")

    # Categorize projects
    active = []
    dormant = []
    completed = []

    for p in projects:
        if p.status == "completed":
            completed.append(p)
        elif p.days_since_active() > dormant_days:
            dormant.append(p)
        else:
            active.append(p)

    # Sort by last_active
    active.sort(key=lambda p: p.last_active, reverse=True)
    dormant.sort(key=lambda p: p.last_active, reverse=True)
    completed.sort(key=lambda p: p.last_active, reverse=True)

    # Print active projects
    if active:
        fire = get_icon("fire", use_emojis)
        console.print(f"\n[bold yellow]{fire} ACTIVE[/bold yellow]", f"({len(active)})")
        for p in active:
            completion_str = format_completion(p.completion, show_bar=True)
            status_line = f"  [bold]{p.name:<20}[/bold] {completion_str}   {format_date_relative(p.last_active):<15}"
            if p.next_steps:
                status_line += f"  [dim][{p.next_steps[:30]}][/dim]"
            console.print(status_line)
    else:
        console.print("\n[dim]No active projects[/dim]")

    # Print dormant projects
    if dormant:
        sleep = get_icon("sleep", use_emojis)
        console.print(f"\n[bold blue]{sleep} DORMANT[/bold blue] ({len(dormant)})")
        for p in dormant[:5]:  # Show max 5
            completion_str = format_completion(p.completion, show_bar=False)
            console.print(f"  [dim]{p.name:<20}[/dim] {completion_str}   {format_date_relative(p.last_active):<15}")
        if len(dormant) > 5:
            console.print(f"  [dim]... and {len(dormant) - 5} more[/dim]")

    # Print completed summary
    if completed:
        check = get_icon("check", use_emojis)
        console.print(f"\n[bold green]{check} COMPLETED[/bold green] ({len(completed)})")
        recent = completed[:3]
        if recent:
            names = ", ".join([p.name for p in recent])
            console.print(f"  [dim]Recently: {names}[/dim]")

    # Print tips/nudges
    if config.get("gentle_nudges"):
        if active:
            # Find nearly done projects
            nearly_done = [p for p in active if p.completion >= 80]
            if nearly_done:
                p = nearly_done[0]
                bulb = get_icon("bulb", use_emojis)
                console.print(f"\n[bold cyan]{bulb} Tip:[/bold cyan] {p.name} is {p.completion}% done - finish it first?")

        # Warn about too many active projects
        max_active = config.get("max_active_projects", 5)
        if len(active) > max_active:
            warn = get_icon("warning", use_emojis)
            console.print(f"\n[yellow]{warn} You have {len(active)} active projects. Consider completing some before starting new ones.[/yellow]")

    # Project health warnings
    if dormant:
        warn = get_icon("warning", use_emojis)
        console.print(f"\n[yellow]{warn} Health Check:[/yellow] {len(dormant)} dormant project(s)")

        # Find stalled projects (30+ days)
        stalled = [p for p in dormant if p.days_since_active() >= 30]
        if stalled:
            console.print(f"  [dim]{len(stalled)} project(s) inactive for 30+ days[/dim]")
            console.print(f"  [dim]Consider: jnl archive --dormant[/dim]")

    # Command hints (if enabled)
    if config.get("show_command_hints", True):
        _print_command_hints(active, dormant, completed, use_emojis)

    console.print()  # Blank line


def _print_command_hints(active: List[Project], dormant: List[Project], completed: List[Project], use_emojis: bool) -> None:
    """Print helpful command suggestions based on current project state."""
    bulb = get_icon("bulb", use_emojis)

    hints = []

    # Context-specific hints
    if active:
        # Find projects close to completion
        nearly_done = [p for p in active if p.completion >= 80]
        if nearly_done:
            hints.append(f"jnl done {nearly_done[0].id} - Complete {nearly_done[0].name}")

        # Suggest logging work
        most_recent = max(active, key=lambda p: p.last_active)
        hints.append(f"jnl log \"your update\" - Log work on {most_recent.name}")

        # Suggest getting context
        hints.append("jnl ctx - Get AI context for planning")

    if dormant:
        oldest_dormant = max(dormant, key=lambda p: p.days_since_active())
        hints.append(f"jnl resume {oldest_dormant.id} - Pick up {oldest_dormant.name}")

        if len(dormant) > 2:
            hints.append("jnl archive --dormant - Clean up dormant projects")

    if not active and not dormant:
        hints.append("jnl new <name> - Start a new project")

    # General hints (always show 1-2)
    hints.append("jnl tui - Browse projects interactively")

    # Print hints
    if hints:
        console.print(f"\n[bold cyan]{bulb} Quick commands:[/bold cyan]")
        # Show max 4 hints to avoid overwhelming
        for hint in hints[:4]:
            console.print(f"  [dim]>[/dim] {hint}")


def print_project_details(project: Project) -> None:
    """Print detailed project information."""
    console.print(f"\n[bold]{project.full_name or project.name}[/bold]")
    console.print(f"Status: {project.status} | Completion: {project.completion}%")
    console.print(f"Last active: {format_date_relative(project.last_active)}")

    if project.tags:
        console.print(f"Tags: {', '.join(project.tags)}")

    if project.next_steps:
        console.print(f"\n[bold cyan]Next steps:[/bold cyan] {project.next_steps}")

    if project.blockers:
        console.print(f"[bold red]Blockers:[/bold red] {project.blockers}")

    if project.github:
        console.print(f"\nGitHub: {project.github}")

    if project.claude_project:
        console.print(f"Claude: {project.claude_project}")

    console.print()


def print_completion_celebration(project: Project, total_completed: int, use_emojis: bool = True) -> None:
    """Print celebration message when completing a project."""
    party = get_icon("party", use_emojis)
    star = get_icon("star", use_emojis)

    celebration = f"""
[bold green]{party} CONGRATULATIONS! {party}[/bold green]

[bold]{project.name}[/bold] is COMPLETE!

"""
    if total_completed > 1:
        celebration += f"That's your {_ordinal(total_completed)} completion!"
    else:
        celebration += f"That's your first completion! {star}"

    console.print(Panel(celebration, border_style="green", expand=False))


def print_list(projects: List[Project], title: str = "Projects") -> None:
    """Print a list of projects in table format."""
    if not projects:
        console.print("[dim]No projects found[/dim]")
        return

    table = Table(title=title, show_header=True, header_style="bold")
    table.add_column("Name", style="cyan", no_wrap=True)
    table.add_column("Status", style="yellow")
    table.add_column("Progress", justify="right")
    table.add_column("Last Active", style="dim")
    table.add_column("Tags", style="dim")

    for p in projects:
        # Use color-coded completion with progress bar
        completion_display = format_completion(p.completion, show_bar=True)
        table.add_row(
            p.name,
            p.status,
            completion_display,
            format_date_relative(p.last_active),
            ", ".join(p.tags[:2]) if p.tags else "",
        )

    console.print(table)


def print_context_export(projects: List[Project], recent_logs: str, question: str = None) -> None:
    """Print context export for LLM."""
    output = ["# JOURNEL Context Export", ""]

    # Active projects
    active = [p for p in projects if p.status != "completed" and p.days_since_active() <= 14]
    if active:
        output.append("## Active Projects")
        output.append("")
        for p in active:
            output.append(f"### {p.name} ({p.completion}% complete)")
            output.append(f"- Last active: {format_date_relative(p.last_active)}")
            if p.next_steps:
                output.append(f"- Next steps: {p.next_steps}")
            if p.blockers:
                output.append(f"- Blockers: {p.blockers}")
            output.append("")

    # Recent activity
    output.append("## Recent Activity")
    output.append("")
    output.append(recent_logs)
    output.append("")

    # Question if provided
    if question:
        output.append("## Question")
        output.append("")
        output.append(question)
        output.append("")

    output.append("---")
    output.append("[Copy this to Claude for analysis]")

    console.print("\n".join(output))


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[green][OK][/green] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"[cyan]>>>[/cyan] {message}")


def _ordinal(n: int) -> str:
    """Convert number to ordinal string (1st, 2nd, 3rd, etc.)."""
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


# Session display functions

def _format_time_duration(elapsed) -> str:
    """Format timedelta as human-readable duration."""
    total_seconds = int(elapsed.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"


def print_session_started(session: Session, project: Project) -> None:
    """Print message when session starts."""
    # Use magenta color for AI-assisted sessions
    if session.ai_assisted:
        console.print(f"\n[bold magenta]>> [AI] SESSION STARTED[/bold magenta]\n")
        console.print(f"[bold magenta]{project.name}[/bold magenta]")
        if session.agent:
            console.print(f"[dim]Agent: {session.agent}[/dim]")
    else:
        console.print(f"\n[bold green]>> SESSION STARTED[/bold green]\n")
        console.print(f"[bold]{project.name}[/bold]")

    if session.task:
        console.print(f"Task: {session.task}")

    start_time = session.start_time.strftime("%H:%M")
    console.print(f"Started: {start_time}")

    # Show context if available
    if session.context_snapshot:
        if session.context_snapshot.get("git_branch"):
            console.print(f"[dim]Branch: {session.context_snapshot['git_branch']}[/dim]")
        if session.context_snapshot.get("git_commit"):
            console.print(f"[dim]Commit: {session.context_snapshot['git_commit']} - {session.context_snapshot.get('git_message', '')}[/dim]")

    # Show next steps if available
    if project.next_steps:
        console.print(f"\n[cyan]Next:[/cyan] {project.next_steps}")

    console.print(f"\n[dim]Use 'jnl stop' when done, 'jnl pause' for breaks[/dim]\n")


def print_session_stopped(session: Session, project: Optional[Project]) -> None:
    """Print message when session stops."""
    elapsed = session.elapsed_time()
    hours = elapsed.total_seconds() / 3600

    # Use magenta color for AI-assisted sessions
    if session.ai_assisted:
        console.print(f"\n[bold magenta][DONE] [AI] SESSION COMPLETE[/bold magenta]\n")
        if project:
            console.print(f"[bold magenta]{project.name}[/bold magenta]")
        if session.agent:
            console.print(f"[dim]Agent: {session.agent}[/dim]")
    else:
        console.print(f"\n[bold green][DONE] SESSION COMPLETE[/bold green]\n")
        if project:
            console.print(f"[bold]{project.name}[/bold]")

    console.print(f"Duration: {_format_time_duration(elapsed)} ({hours:.1f}h)")

    if session.task:
        console.print(f"Task: {session.task}")

    if session.notes:
        console.print(f"\n[cyan]Notes:[/cyan] {session.notes}")

    if session.interruptions:
        console.print(f"\n[yellow]Interruptions:[/yellow] {len(session.interruptions)}")

    if session.pause_duration.total_seconds() > 0:
        console.print(f"[dim]Breaks: {_format_time_duration(session.pause_duration)}[/dim]")

    console.print(f"\n[dim]Logged to activity and session history[/dim]")
    console.print(f"[bold cyan]Take a break![/bold cyan]\n")


def print_session_paused(session: Session, project: Optional[Project]) -> None:
    """Print message when session is paused."""
    elapsed = session.elapsed_time()

    # Use magenta color for AI-assisted sessions
    if session.ai_assisted:
        console.print(f"\n[bold magenta][PAUSE] [AI] SESSION PAUSED[/bold magenta]\n")
        if project:
            console.print(f"[bold magenta]{project.name}[/bold magenta]")
        if session.agent:
            console.print(f"[dim]Agent: {session.agent}[/dim]")
    else:
        console.print(f"\n[bold yellow][PAUSE] SESSION PAUSED[/bold yellow]\n")
        if project:
            console.print(f"[bold]{project.name}[/bold]")

    console.print(f"Active time: {_format_time_duration(elapsed)}")

    if session.task:
        console.print(f"Task: {session.task}")

    console.print(f"\n[dim]Use 'jnl continue' to resume[/dim]\n")


def print_session_resumed(session: Session, project: Optional[Project]) -> None:
    """Print message when session resumes."""
    elapsed = session.elapsed_time()

    # Use magenta color for AI-assisted sessions
    if session.ai_assisted:
        console.print(f"\n[bold magenta]>> [AI] SESSION RESUMED[/bold magenta]\n")
        if project:
            console.print(f"[bold magenta]{project.name}[/bold magenta]")
        if session.agent:
            console.print(f"[dim]Agent: {session.agent}[/dim]")
    else:
        console.print(f"\n[bold green]>> SESSION RESUMED[/bold green]\n")
        if project:
            console.print(f"[bold]{project.name}[/bold]")

    console.print(f"Previous time: {_format_time_duration(elapsed)}")

    if session.task:
        console.print(f"Task: {session.task}")

    # Show context
    if session.context_snapshot:
        if session.context_snapshot.get("git_branch"):
            console.print(f"[dim]Branch: {session.context_snapshot['git_branch']}[/dim]")
        if session.context_snapshot.get("git_commit"):
            console.print(f"[dim]Last commit: {session.context_snapshot['git_commit']}[/dim]")

    console.print(f"\n[dim]Back to work! Use 'jnl stop' when done.[/dim]\n")
