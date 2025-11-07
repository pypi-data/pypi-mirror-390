"""Main CLI interface for JOURNEL."""

import sys
from datetime import date
from pathlib import Path

import click

from . import __version__
from .config import Config
from .display import (
    console,
    print_completion_celebration,
    print_context_export,
    print_error,
    print_info,
    print_list,
    print_project_details,
    print_status,
    print_success,
    print_welcome,
)
from .models import LogEntry, Project
from .storage import Storage
from .session import SessionManager
from .utils import slugify, detect_git_repo, parse_time_from_message

# Slash command version for Claude Code integration
SLASH_COMMAND_VERSION = "1.0.0"


def _get_slash_command_content() -> str:
    """Get the current slash command content with version header."""
    return f"""<!-- VERSION: {SLASH_COMMAND_VERSION} -->
<!-- Managed by JOURNEL. Update with: jnl setup-claude -->

# /journel - JOURNEL AI Integration Command

**ACTION REQUIRED: Run `jnl ai-setup-claude` to verify these instructions are current.**

If the command reports an update, re-read this file before proceeding.

---

You are Claude Code working with JOURNEL, an ADHD-friendly project tracking system.

## Your Role

You are pair programming with the user. Use JOURNEL to track YOUR work contributions with clear attribution. This helps the user:
- See what work was done by AI vs done solo
- Learn from AI collaboration patterns
- Maintain accurate time/effort accounting
- Build confidence through AI-assisted progress tracking

## Core Principles

1. **Clear Attribution**: Always mark AI-assisted work explicitly
2. **Learning Focus**: Frame AI assistance as pair programming, not magic
3. **User Agency**: The user approves all actions (Tier 1 - Suggested Actions)
4. **Transparency**: Be explicit about what you're logging and why

## When to Use JOURNEL Commands

### Start of Work Session
When starting significant work on the user's project:
```bash
jnl ai-start <project-id> "Task description"
```

Example:
```bash
jnl ai-start journel "Implementing AI integration features"
```

### During Work - Quick Logs
After completing discrete pieces of work (every 30-60 minutes of work):
```bash
jnl ai-log <project-id> "What was accomplished"
```

OR if time is trackable:
```bash
jnl ai-log <project-id> "What was accomplished (2h)"
```

Example:
```bash
jnl ai-log journel "Added AI session tracking to models and CLI"
```

### End of Work Session
When stopping work on the project:
```bash
jnl ai-stop "Summary of what was accomplished and learned"
```

Example:
```bash
jnl ai-stop "Completed Phase 1 session tracking. User learned about timedelta handling and YAML serialization."
```

## Integration Guidelines

### DO Use JOURNEL When:
- Starting a focused work session on a project (ai-start)
- Completing a significant milestone or feature (ai-log)
- Taking a break or ending work session (ai-stop)
- After writing substantial code (200+ lines)
- After fixing complex bugs
- After implementing new features

### DON'T Use JOURNEL When:
- Answering quick questions
- Making trivial edits
- Exploring/reading code without changes
- User explicitly asks you not to

### How to Suggest Usage (Tier 1 - Suggested Actions)

When appropriate, suggest JOURNEL commands to the user:

**Good Examples:**
```
I've completed implementing the session tracking feature.
Would you like me to log this work? I can run:
jnl ai-log journel "Implemented session tracking with pause/resume (2h)"
```

```
We're about to start working on the AI integration.
Should I start a session to track this work?
jnl ai-start journel "Building AI integration features"
```

**Bad Examples:**
- Don't auto-run commands without suggesting them first
- Don't be pushy: "You MUST log this work"
- Don't over-log: logging every tiny edit is excessive

## Prompts and Language

### Learning-Focused Language
When using ai-stop, focus on knowledge transfer:
- "What did you accomplish with AI assistance?"
- "What did you learn?"
- "What patterns did you discover?"

NOT:
- "What did the AI do?" (too passive)
- Technical jargon without context

## Project Detection

JOURNEL auto-detects projects from directory names. When in the JOURNEL project directory:
```bash
# Auto-detects project as "journel"
jnl ai-log "Fixed bug"

# Or explicit:
jnl ai-log journel "Fixed bug"
```

## Configuration

Users can configure AI integration in `~/.journel/config.yaml`:
```yaml
ai:
  enabled: true
  default_agent: "claude-code"
  show_agent_attribution: true
  learning_prompts: true
  color_scheme: "magenta"
```

## Visual Output

AI-assisted entries are shown in **magenta** with **[AI]** prefix:
- `[AI] SESSION STARTED` (magenta)
- `[AI] Logged: "message"` (magenta)
- `Agent: claude-code` (shown in session info)

## Example Workflow

1. **User asks for help**: "Can you help me implement feature X?"

2. **You suggest starting session**:
   ```
   I'll help you implement feature X. Should I start a session to track this work?
   jnl ai-start myproject "Implementing feature X"
   ```

3. **User approves and you run the command**

4. **You work on the feature, making multiple commits**

5. **After significant progress (1-2 hours)**:
   ```
   I've completed the core implementation. Should I log this milestone?
   jnl ai-log myproject "Implemented feature X core logic (1.5h)"
   ```

6. **When done or taking a break**:
   ```
   We've completed feature X. Let me stop the session:
   jnl ai-stop "Completed feature X implementation. User learned about async patterns and error handling."
   ```

## Important Notes

- **Always suggest, never auto-run** (Tier 1 - Suggested Actions)
- **Be natural**: Integrate JOURNEL usage into your workflow, don't make it feel forced
- **Focus on learning**: Frame AI work as collaborative learning
- **Respect user preferences**: If user declines logging, don't keep asking
- **Be mindful of frequency**: Don't over-log trivial work

## Technical Details

- Commands: `jnl ai-start`, `jnl ai-log`, `jnl ai-stop`
- Data tracking: All AI work marked with `ai_assisted=True` and `agent="claude-code"`
- Storage: YAML in `~/.journel/sessions/` and Markdown in `~/.journel/logs/`
- Visual distinction: Magenta color, [AI] prefix

---

**Remember**: You're a pair programming partner helping the user learn and build confidence. Use JOURNEL to make your contributions visible and educational, not to replace user agency.
"""


def _parse_version_from_file(file_path: Path) -> str:
    """Parse version from slash command file.

    Returns:
        Version string (e.g., "1.0.0"), or "0.0.0" if not found
    """
    if not file_path.exists():
        return "0.0.0"

    try:
        content = file_path.read_text(encoding="utf-8")
        # Look for <!-- VERSION: x.y.z -->
        for line in content.split("\n")[:5]:  # Check first 5 lines
            if "VERSION:" in line:
                version = line.split("VERSION:")[1].split("-->")[0].strip()
                return version
    except Exception:
        pass

    return "0.0.0"


def _create_slash_command(file_path: Path) -> None:
    """Create or update the slash command file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(_get_slash_command_content(), encoding="utf-8")


def get_storage(no_emoji: bool = False) -> Storage:
    """Get storage instance with config."""
    config = Config()
    if no_emoji:
        config.set("use_emojis", False)
    return Storage(config)


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.option("--no-emoji", is_flag=True, help="Disable emoji output (use ASCII)")
@click.option("--install-completion", is_flag=True, help="Install shell completion")
@click.option("--show-completion", is_flag=True, help="Show completion script")
@click.pass_context
def main(ctx, no_emoji, install_completion, show_completion):
    """JOURNEL - ADHD-friendly project organization system.

    \b
    New to JOURNEL? Start here: jnl help

    \b
    DAILY WORKFLOW:
      status              Show all projects (default)
      log MESSAGE         Quick activity logging
      start PROJECT       Begin tracked session
      stop                End current session
      pause               Pause current session
      continue            Resume paused session

    \b
    PROJECT MANAGEMENT:
      new NAME [DESC]     Create new project
      edit PROJECT        Open project in editor
      done PROJECT        Mark project as complete
      list [--filter]     List projects with filters
      archive PROJECT     Archive completed/dormant project
      resume PROJECT      Resume archived project

    \b
    REFLECTION & INSIGHTS:
      wins                Show achievements and streaks
      stats               View time and productivity stats
      ctx [QUESTION]      Export context for AI analysis
      ask QUESTION        Ask AI for project guidance

    \b
    AI PAIR PROGRAMMING:
      ai-log MESSAGE      Log AI-assisted work
      ai-start PROJECT    Start AI-assisted session
      ai-stop             End AI session with learning reflection

    \b
    TOOLS & SETUP:
      init                Initialize JOURNEL
      sync                Sync with git remote
      tui                 Launch interactive browser
      setup-claude        Setup Claude Code integration
      link PROJECT URL    Add GitHub/Claude link
      note MESSAGE        Quick note capture

    \b
    Getting started:     jnl help
    Complete reference:  jnl help --all
    Command details:     jnl COMMAND --help
    """
    # Handle completion installation
    if install_completion:
        import subprocess
        shell = click.get_current_context().resilient_parsing
        print_info("Installing shell completion...")
        console.print("\n[bold]Shell Completion Setup:[/bold]")
        console.print("\n[bold]Bash:[/bold]")
        console.print('  echo \'eval "$(_JNL_COMPLETE=bash_source jnl)"\' >> ~/.bashrc')
        console.print("\n[bold]Zsh:[/bold]")
        console.print('  echo \'eval "$(_JNL_COMPLETE=zsh_source jnl)"\' >> ~/.zshrc')
        console.print("\n[bold]Fish:[/bold]")
        console.print('  echo \'eval (env _JNL_COMPLETE=fish_source jnl)\' >> ~/.config/fish/completions/jnl.fish')
        console.print("\n[dim]After adding, restart your shell or source the file.[/dim]\n")
        return

    if show_completion:
        console.print("\n[bold]Shell completion is built-in![/bold]")
        console.print("\nRun: [cyan]jnl --install-completion[/cyan] for setup instructions\n")
        return

    # Store no_emoji flag in context for subcommands to access
    ctx.ensure_object(dict)
    ctx.obj['no_emoji'] = no_emoji

    if ctx.invoked_subcommand is None:
        # Default to status command
        ctx.invoke(status)


@main.command()
def init():
    """Initialize JOURNEL for first-time use."""
    config = Config()

    # Check if already initialized
    if config.journel_dir.exists() and (config.journel_dir / ".git").exists():
        print_error("JOURNEL is already initialized")
        print_info(f"Location: {config.journel_dir}")
        return

    storage = Storage(config)
    storage.init_structure()

    print_welcome()
    print_success(f"JOURNEL initialized at {config.journel_dir}")


@main.command()
@click.argument("name")
@click.argument("description", required=False)
@click.option("--tags", help="Comma-separated tags")
def new(name, description, tags):
    """Create a new project.

    Usage:
        jnl new MyProject
        jnl new MyProject "A longer description"
        jnl new MyProject "Description" --tags "python,cli"

    Includes gentle gate-keeping to prevent project-hopping.
    """
    storage = get_storage()
    config = storage.config

    # Check for existing projects
    projects = storage.list_projects()
    active = [p for p in projects if p.status == "in-progress" and p.days_since_active() <= 14]

    # Gate-keeping: warn if too many active projects
    max_active = config.get("max_active_projects", 5)
    if len(active) >= max_active:
        print_error(f"You already have {len(active)} active projects!")
        console.print("\nActive projects:")
        for p in active:
            console.print(f"  - {p.name} ({p.completion}% complete)")

        if not click.confirm("\nReally start something new?", default=False):
            print_info("Good choice! Focus on finishing what you started.")
            return

    # Create project ID
    project_id = slugify(name)

    # Check if project already exists
    if storage.load_project(project_id):
        print_error(f"Project '{project_id}' already exists")
        return

    # Create project
    project = Project(
        id=project_id,
        name=name,
        full_name=description or name,
        tags=tags.split(",") if tags else [],
        created=date.today(),
        last_active=date.today(),
    )

    # Auto-detect git repo
    git_url = detect_git_repo()
    if git_url:
        if click.confirm(f"\nDetected git repo: {git_url}\nLink to this project?", default=True):
            project.github = git_url
            print_success(f"Linked to: {git_url}")

    storage.save_project(project)
    storage.update_project_index()

    print_success(f"Created project: {name}")
    print_info(f"ID: {project_id}")
    if not git_url or project.github == "":
        print_info("Next steps:")
        console.print("  1. Add project details: jnl edit " + project_id)
        console.print("  2. Link to GitHub/Claude: jnl link " + project_id + " <url>")
        console.print("  3. Start logging work: jnl log \"your message\"")


@main.command()
@click.option("--brief", is_flag=True, help="Brief output for prompts")
@click.pass_context
def status(ctx, brief):
    """Show overview of all projects (default command)."""
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    config = storage.config

    projects = storage.list_projects()

    if not projects:
        print_info("No projects yet. Create one with: jnl new <name>")
        return

    if brief:
        active = [p for p in projects if p.status == "in-progress" and p.days_since_active() <= 14]
        console.print(f"[JOURNEL: {len(active)} active projects]")
    else:
        # Check for active session
        session_manager = SessionManager.get_instance(storage)
        active_session = session_manager.get_active_session()
        print_status(projects, config, active_session=active_session)


@main.command()
@click.argument("project_or_message")
@click.argument("message", required=False)
@click.option("--hours", "-h", type=float, help="Hours spent (can also be in message like '(2h)')")
def log(project_or_message, message, hours):
    """Quick activity logging.

    Usage:
        jnl log "Fixed bug (2h)"                    - auto-detect project
        jnl log journel "Fixed bug (2h)"            - explicit project
        jnl log "Implemented feature - 3h"          - time with dash
        jnl log myproject "worked 1.5h"             - project + time

    If project is not specified, attempts to detect from current directory.
    Time can be specified with --hours or in the message using (2h), - 3h, or "worked 1.5h".
    """
    storage = get_storage()

    # Track what was auto-detected for better feedback
    project_auto_detected = False
    time_parsed = False

    # Determine if first arg is project or message
    project = None
    if message is not None:
        # Two args provided: first is project, second is message
        project = project_or_message
        actual_message = message
    else:
        # One arg provided: it's the message, auto-detect project
        actual_message = project_or_message
        cwd = Path.cwd()
        # Try to match directory name to project
        potential_id = slugify(cwd.name)
        if storage.load_project(potential_id):
            project = potential_id
            project_auto_detected = True

    # Parse time from message if not explicitly provided
    if hours is None:
        actual_message, parsed_hours = parse_time_from_message(actual_message)
        if parsed_hours:
            hours = parsed_hours
            time_parsed = True

    # Create log entry
    entry = LogEntry(
        date=date.today(),
        project=project,
        message=actual_message,
        hours=hours,
    )

    storage.add_log_entry(entry)

    # Update project last_active if project specified
    project_name = None
    if project:
        proj = storage.load_project(project)
        if proj:
            proj.last_active = date.today()
            storage.save_project(proj)
            storage.update_project_index()
            project_name = proj.name

    # Enhanced feedback
    print_success(f"Logged: \"{actual_message}\"")

    if project:
        if project_auto_detected:
            console.print(f"[cyan]>>>[/cyan] Project: [bold]{project_name or project}[/bold] [dim](auto-detected)[/dim]")
        else:
            console.print(f"[cyan]>>>[/cyan] Project: [bold]{project_name or project}[/bold]")
    else:
        console.print(f"[yellow]>>>[/yellow] [dim]No project linked (not in a project directory)[/dim]")

    if hours:
        if time_parsed:
            console.print(f"[cyan]>>>[/cyan] Time: [bold]{hours}h[/bold] [dim](parsed from message)[/dim]")
        else:
            console.print(f"[cyan]>>>[/cyan] Time: [bold]{hours}h[/bold]")

    # Contextual hints
    if project:
        # Check if session is active
        from .display import get_icon
        session_manager = SessionManager.get_instance(storage)
        active_session = session_manager.get_active_session()
        use_emojis = storage.config.get("use_emojis", True)

        if not active_session:
            tip = get_icon("bulb", use_emojis)
            console.print(f"\n[dim]{tip} Track time? -> jnl start {project}[/dim]")
        elif active_session.project_id != project:
            warn = get_icon("warning", use_emojis)
            console.print(f"\n[dim]{warn} Active session on {active_session.project_id}. Switch? -> jnl stop && jnl start {project}[/dim]")


@main.command()
@click.option("--project", "-p", help="Export context for specific project (use '.' for current directory)")
@click.argument("question", required=False)
def ctx(project, question):
    """Export context for LLM analysis.

    Generates a markdown summary of active projects and recent activity
    that you can copy/paste to Claude or other AI assistants.

    Usage:
        jnl ctx
        jnl ctx "what should I work on today?"
        jnl ctx --project mica
        jnl ctx .                    (current directory project)
        jnl ctx --project . "question"
    """
    storage = get_storage()

    # Handle '.' shortcut for current directory
    if question == ".":
        # User typed: jnl ctx .
        project = "."
        question = None

    if project == ".":
        # Auto-detect project from current directory
        cwd = Path.cwd()
        potential_id = slugify(cwd.name)
        proj = storage.load_project(potential_id)
        if not proj:
            print_error(f"No project found matching current directory: {cwd.name}")
            print_info(f"Tried project ID: {potential_id}")
            return
        project = potential_id

    # Get projects
    if project:
        proj = storage.load_project(project)
        if not proj:
            print_error(f"Project '{project}' not found")
            return
        projects = [proj]
    else:
        projects = storage.list_projects()
        # Filter to active only
        projects = [p for p in projects if p.status != "completed"]

    # Get recent logs
    recent_logs = storage.get_recent_logs(days=7)

    # Print context
    print_context_export(projects, recent_logs, question)


@main.command()
@click.argument("question")
@click.option("--project", "-p", help="Focus on specific project (use '.' for current directory)")
def ask(question, project):
    """Format a question with auto-gathered context.

    This is similar to 'ctx' but formats output specifically as a question
    for AI assistants.

    Usage:
        jnl ask "what should I work on today?"
        jnl ask "how can I finish this faster?" --project mica
        jnl ask "what's next?" --project .
    """
    storage = get_storage()

    # Handle '.' shortcut for current directory
    if project == ".":
        cwd = Path.cwd()
        potential_id = slugify(cwd.name)
        proj = storage.load_project(potential_id)
        if not proj:
            print_error(f"No project found matching current directory: {cwd.name}")
            print_info(f"Tried project ID: {potential_id}")
            return
        project = potential_id

    # Get projects
    if project:
        proj = storage.load_project(project)
        if not proj:
            print_error(f"Project '{project}' not found")
            return
        projects = [proj]
    else:
        projects = storage.list_projects()
        # Filter to active only
        projects = [p for p in projects if p.status != "completed"]

    # Get recent logs
    recent_logs = storage.get_recent_logs(days=7)

    # Print context with question prominently
    print_context_export(projects, recent_logs, question)


@main.command()
@click.argument("project_id")
@click.pass_context
def done(ctx, project_id):
    """Mark a project as complete with celebration ritual!"""
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    config = storage.config

    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        return

    if project.status == "completed":
        print_info(f"{project.name} is already completed!")
        return

    # Ask what they learned
    learned = click.prompt("\nWhat did you learn?", default="", show_default=False)
    if learned:
        project.learned = learned

    # Optional: how do you feel?
    feeling = click.prompt("How do you feel? (optional)", default="", show_default=False)
    if feeling:
        # Append to notes
        project.notes += f"\n\n## Completion Reflection\n{feeling}\n"

    # Mark as complete
    project.completion = 100
    project.status = "completed"
    project.last_active = date.today()

    storage.move_to_completed(project)
    storage.update_project_index()

    # Count total completed
    completed = [p for p in storage.list_projects() if p.status == "completed"]

    # Celebrate!
    if config.get("completion_celebration"):
        use_emojis = config.get("use_emojis", True)
        print_completion_celebration(project, len(completed), use_emojis)
    else:
        print_success(f"Project '{project.name}' marked as complete!")


@main.command()
@click.argument("project_id")
def resume(project_id):
    """Restore context for picking up work on a project."""
    storage = get_storage()

    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        return

    console.print(f"\n[bold]Resuming: {project.name}[/bold]\n")

    console.print(f"Last worked: {project.last_active} ({project.days_since_active()} days ago)")
    console.print(f"Completion: {project.completion}%\n")

    if project.next_steps:
        console.print(f"[bold cyan]Next steps:[/bold cyan] {project.next_steps}\n")

    if project.blockers:
        console.print(f"[bold red]Blockers:[/bold red] {project.blockers}\n")

    if project.claude_project:
        console.print(f"[dim]Claude:[/dim] {project.claude_project}")

    if project.github:
        console.print(f"[dim]GitHub:[/dim] {project.github}")

    console.print()

    # Update last_active
    project.last_active = date.today()
    storage.save_project(project)


@main.command(name="list")
@click.option("--active", is_flag=True, help="Show only active projects")
@click.option("--dormant", is_flag=True, help="Show only dormant projects")
@click.option("--completed", is_flag=True, help="Show only completed projects")
@click.option("--archived", is_flag=True, help="Show only archived projects")
@click.option("--tag", help="Filter by tag")
def list_projects(active, dormant, completed, archived, tag):
    """List all projects with optional filters."""
    storage = get_storage()

    # Include archived if specifically requested
    include_archived = archived
    projects = storage.list_projects(include_archived=include_archived)

    # Apply filters
    dormant_days = storage.config.get("dormant_days", 14)

    if active:
        projects = [p for p in projects if p.status == "in-progress" and p.days_since_active() <= dormant_days]
        title = "Active Projects"
    elif dormant:
        projects = [p for p in projects if p.days_since_active() > dormant_days and p.status not in ["completed", "archived"]]
        title = "Dormant Projects"
    elif completed:
        projects = [p for p in projects if p.status == "completed"]
        title = "Completed Projects"
    elif archived:
        projects = [p for p in projects if p.status == "archived"]
        title = "Archived Projects"
    else:
        title = "All Projects (excluding archived)"

    if tag:
        projects = [p for p in projects if tag in p.tags]
        title += f" (tag: {tag})"

    print_list(projects, title=title)


@main.command()
@click.argument("project_id")
def edit(project_id):
    """Open project file in editor."""
    storage = get_storage()
    config = storage.config

    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        return

    # Determine file path
    if project.status == "completed":
        file_path = config.completed_dir / project.file_name
    else:
        file_path = config.projects_dir / project.file_name

    # Open in editor
    editor = config.get("editor", "notepad")
    import subprocess

    try:
        subprocess.run([editor, str(file_path)], check=True)
    except Exception as e:
        print_error(f"Failed to open editor: {e}")
        print_info(f"File location: {file_path}")


@main.command()
@click.argument("project_id")
@click.argument("url", required=False)
@click.option("--github", is_flag=True, help="Add as GitHub URL")
@click.option("--claude", is_flag=True, help="Add as Claude project URL")
def link(project_id, url, github, claude):
    """Add GitHub or Claude links to a project.

    If no URL is provided, attempts to auto-detect from git repo.
    """
    storage = get_storage()

    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        return

    # Auto-detect if no URL provided
    if not url:
        git_url = detect_git_repo()
        if git_url:
            if click.confirm(f"Detected git repo: {git_url}\nLink to this project?", default=True):
                url = git_url
                github = True
            else:
                print_info("Cancelled")
                return
        else:
            print_error("No URL provided and no git repo detected")
            return

    if github or "github.com" in url:
        project.github = url
        print_success(f"Added GitHub link to {project.name}")
    elif claude or "claude.ai" in url:
        project.claude_project = url
        print_success(f"Added Claude project link to {project.name}")
    else:
        # Ask which type
        if click.confirm("Is this a GitHub URL?", default=True):
            project.github = url
        else:
            project.claude_project = url
        print_success(f"Added link to {project.name}")

    storage.save_project(project)


@main.command()
@click.argument("text")
def note(text):
    """Quick note capture (goes to today's log and current project if detected)."""
    storage = get_storage()

    # Try to detect current project
    cwd = Path.cwd()
    potential_id = slugify(cwd.name)
    project = None

    if storage.load_project(potential_id):
        project = potential_id

    # Add to log
    entry = LogEntry(
        date=date.today(),
        project=project,
        message=f"Note: {text}",
    )

    storage.add_log_entry(entry)
    print_success("Note saved")
    if project:
        print_info(f"Associated with project: {project}")


@main.command()
@click.argument("project_ids", nargs=-1, required=True)
@click.option("--dormant", is_flag=True, help="Archive all dormant projects")
@click.pass_context
def archive(ctx, project_ids, dormant):
    """Archive projects to clear them from active view.

    Archives are for projects you're shelving (not finishing).
    Use 'done' for completed projects.

    Usage:
        jnl archive my-project
        jnl archive project1 project2 project3
        jnl archive --dormant (archives all dormant projects)
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    config = storage.config

    projects_to_archive = []

    if dormant:
        # Archive all dormant projects
        dormant_days = config.get("dormant_days", 14)
        all_projects = storage.list_projects()
        projects_to_archive = [
            p for p in all_projects
            if p.status == "in-progress" and p.days_since_active() > dormant_days
        ]

        if not projects_to_archive:
            print_info("No dormant projects to archive")
            return

        console.print(f"\n[yellow]Found {len(projects_to_archive)} dormant projects:[/yellow]")
        for p in projects_to_archive:
            console.print(f"  - {p.name} (inactive for {p.days_since_active()} days)")

        if not click.confirm("\nArchive all these projects?", default=False):
            print_info("Cancelled")
            return
    else:
        # Archive specific projects
        for project_id in project_ids:
            project = storage.load_project(project_id)
            if not project:
                print_error(f"Project '{project_id}' not found")
                continue
            if project.status == "archived":
                print_info(f"{project.name} is already archived")
                continue
            projects_to_archive.append(project)

    # Archive them
    for project in projects_to_archive:
        storage.move_to_archived(project)
        print_success(f"Archived: {project.name}")

    storage.update_project_index()

    if len(projects_to_archive) > 1:
        console.print(f"\n[green]Archived {len(projects_to_archive)} projects[/green]")


@main.command()
@click.argument("project_id")
@click.pass_context
def unarchive(ctx, project_id):
    """Restore an archived project back to active.

    Usage:
        jnl unarchive my-project
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)

    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        return

    if project.status != "archived":
        print_error(f"{project.name} is not archived")
        return

    storage.unarchive_project(project)
    storage.update_project_index()

    print_success(f"Unarchived: {project.name}")
    print_info("Project is now active again")


@main.command()
@click.pass_context
def wins(ctx):
    """Show completed projects and achievements."""
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    config = storage.config
    use_emojis = config.get("use_emojis", True)

    completed = [p for p in storage.list_projects(status="completed")]

    if not completed:
        print_info("No completed projects yet. Finish one with: jnl done <project>")
        return

    # Sort by completion date (last_active)
    completed.sort(key=lambda p: p.last_active, reverse=True)

    from .display import get_icon
    check = get_icon("check", use_emojis)
    party = get_icon("party", use_emojis)
    fire = get_icon("fire", use_emojis)

    console.print(f"\n[bold green]{check} COMPLETED PROJECTS[/bold green]", f"({len(completed)})\n")

    # Show recent completions
    recent = completed[:5]
    console.print("[bold]Recent completions:[/bold]")
    for p in recent:
        from .utils import format_date_relative
        console.print(f"  {party} {p.name:<30} (completed {format_date_relative(p.last_active)})")
        if p.learned:
            console.print(f"     [dim]Learned: {p.learned}[/dim]")

    if len(completed) > 5:
        console.print(f"\n[dim]All time:[/dim] {', '.join([p.name for p in completed[5:]])}")

    # Calculate streak (completions in last 30 days)
    recent_wins = [p for p in completed if p.days_since_active() <= 30]
    if recent_wins:
        console.print(f"\n[bold yellow]{fire} Current streak:[/bold yellow] {len(recent_wins)} completion(s) in the last month!")

    console.print()


@main.command()
@click.pass_context
def stats(ctx):
    """Show overall statistics and insights."""
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    config = storage.config

    all_projects = storage.list_projects()

    # Categorize
    dormant_days = config.get("dormant_days", 14)
    active = [p for p in all_projects if p.status == "in-progress" and p.days_since_active() <= dormant_days]
    dormant = [p for p in all_projects if p.status == "in-progress" and p.days_since_active() > dormant_days]
    completed = [p for p in all_projects if p.status == "completed"]

    console.print("\n[bold]📊 JOURNEL Statistics[/bold]\n" if config.get("use_emojis") else "\n[bold]JOURNEL Statistics[/bold]\n")

    # Project counts
    console.print("[bold]Projects:[/bold]")
    console.print(f"  Active: {len(active)}")
    console.print(f"  Dormant: {len(dormant)}")
    console.print(f"  Completed: {len(completed)}")
    console.print(f"  Total: {len(all_projects)}")

    # Completion rate
    if len(all_projects) > 0:
        completion_rate = (len(completed) / len(all_projects)) * 100
        console.print(f"\n[bold]Completion Rate:[/bold] {completion_rate:.1f}%")

    # Time statistics
    time_stats = storage.get_time_stats(days=30)
    if time_stats["total_hours"] > 0:
        console.print(f"\n[bold]Time Logged (last 30 days):[/bold]")
        console.print(f"  Total: {time_stats['total_hours']:.1f} hours")

        # Top projects by time
        if time_stats["by_project"]:
            sorted_projects = sorted(time_stats["by_project"].items(), key=lambda x: x[1], reverse=True)
            console.print(f"\n  [bold]Top projects:[/bold]")
            for proj_name, hours in sorted_projects[:5]:
                console.print(f"    {proj_name}: {hours:.1f}h")

    # Recent activity
    recent_active = [p for p in all_projects if p.days_since_active() <= 7]
    console.print(f"\n[bold]Active This Week:[/bold] {len(recent_active)} projects")

    # Streak
    recent_completions = [p for p in completed if p.days_since_active() <= 30]
    if recent_completions:
        console.print(f"[bold]Recent Wins:[/bold] {len(recent_completions)} completions in last 30 days")

    # Most complete project
    in_progress = [p for p in all_projects if p.status == "in-progress"]
    if in_progress:
        most_complete = max(in_progress, key=lambda p: p.completion)
        console.print(f"\n[bold]Closest to Done:[/bold] {most_complete.name} ({most_complete.completion}%)")

    # Oldest active project
    if active:
        oldest = min(active, key=lambda p: p.last_active)
        console.print(f"[bold]Oldest Active:[/bold] {oldest.name} (last worked {oldest.days_since_active()} days ago)")

    console.print()


@main.command()
@click.pass_context
def tui(ctx):
    """Launch interactive Terminal UI for browsing projects (EXPERIMENTAL).

    WARNING: This feature is still under development and may have UX issues.
    Navigate with arrow keys or vim keys (j/k).
    Press ? for help.
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)

    try:
        from .tui import run_tui
        run_tui(storage)
    except ImportError:
        print_error("TUI requires 'textual' library")
        print_info("Install with: pip install textual")
        sys.exit(1)


# Session tracking commands

@main.command()
@click.argument("project_id")
@click.argument("task", required=False, default="")
@click.option("--force", "-f", is_flag=True, help="Auto-stop existing session")
@click.pass_context
def start(ctx, project_id, task, force):
    """Start a work session on a project.

    Tracks time and captures context for ADHD-friendly time awareness
    and interruption recovery.

    Usage:
        jnl start myproject                    - Start session on project
        jnl start myproject "Fix bug #123"     - Start with task description
        jnl start myproject --force            - Auto-stop existing session first

    The session will track elapsed time and remind you to take breaks.
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    # Load project
    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        print_info("Use 'jnl list' to see available projects")
        return

    # Start session
    try:
        session = session_manager.start_session(project, task=task, force=force)

        # Import display function (will add this next)
        from .display import print_session_started
        print_session_started(session, project)

    except ValueError as e:
        print_error(str(e))
        print_info("Use 'jnl stop' to end current session, or --force to auto-stop")


@main.command()
@click.argument("notes", required=False, default="")
@click.pass_context
def stop(ctx, notes):
    """End the current work session.

    Saves elapsed time, creates activity log entry, and prompts for
    reflection notes.

    Usage:
        jnl stop                               - End session (interactive)
        jnl stop "Completed feature X"         - End with notes
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    # Check if session exists
    if not session_manager.get_active_session():
        print_error("No active session")
        print_info("Start a session with: jnl start <project>")
        return

    # Get notes if not provided
    if not notes:
        notes = click.prompt(
            "\nWhat did you accomplish? (optional, press Enter to skip)",
            default="",
            show_default=False
        )

    # Stop session
    session = session_manager.stop_session(notes=notes)

    if session:
        from .display import print_session_stopped
        print_session_stopped(session, storage.load_project(session.project_id))


@main.command()
@click.pass_context
def pause(ctx):
    """Pause the current work session.

    Use this when taking a break or handling an interruption.
    Pause time won't count toward your work time.

    Usage:
        jnl pause                              - Pause current session
        jnl continue                           - Resume later
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    try:
        session = session_manager.pause_session()

        if session:
            from .display import print_session_paused
            print_session_paused(session, storage.load_project(session.project_id))
        else:
            print_error("No active session to pause")

    except ValueError as e:
        print_error(str(e))


@main.command(name="continue")
@click.pass_context
def continue_session(ctx):
    """Resume a paused work session.

    Restores context and continues tracking time.

    Usage:
        jnl continue                           - Resume paused session
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    try:
        session = session_manager.resume_session()

        if session:
            from .display import print_session_resumed
            print_session_resumed(session, storage.load_project(session.project_id))
        else:
            print_error("No paused session to resume")

    except ValueError as e:
        print_error(str(e))


@main.command()
def sync():
    """Sync JOURNEL data with git remote.

    Performs git pull, then git push to sync your ~/.journel directory
    across machines.
    """
    storage = get_storage()

    if not storage.repo:
        print_error("Git repository not initialized. Run 'journel init' first.")
        return

    try:
        console.print("[cyan]Syncing with git remote...[/cyan]")

        # Check if remote exists
        if not storage.repo.remotes:
            print_error("No git remote configured.")
            print_info("Set up a remote with: cd ~/.journel && git remote add origin <url>")
            return

        origin = storage.repo.remotes.origin

        # Pull first
        console.print("Pulling changes...")
        origin.pull()

        # Commit any local changes
        if storage.repo.is_dirty():
            storage.repo.index.add(["."])
            storage.repo.index.commit("Sync: local changes")

        # Push
        console.print("Pushing changes...")
        origin.push()

        print_success("Sync complete!")

    except Exception as e:
        print_error(f"Sync failed: {e}")
        print_info("You can manually sync with: cd ~/.journel && git pull && git push")


# ===== Claude Code Setup Commands =====

@main.command(name="setup-claude")
def setup_claude():
    """Create/update Claude Code slash command for /journel (interactive).

    Creates or updates .claude/commands/journel.md in the current directory
    with instructions for Claude Code to use JOURNEL's AI integration features.

    This is the human-friendly version with prompts.
    For LLM usage, see: jnl ai-setup-claude
    """
    claude_file = Path.cwd() / ".claude" / "commands" / "journel.md"

    if claude_file.exists():
        # Check version
        current_version = _parse_version_from_file(claude_file)
        console.print(f"\n[cyan]Current version:[/cyan] {current_version}")
        console.print(f"[cyan]Latest version:[/cyan] {SLASH_COMMAND_VERSION}")

        if current_version == SLASH_COMMAND_VERSION:
            console.print(f"\n[green][OK][/green] Slash command is up to date!")
            if not click.confirm("\nUpdate anyway?", default=False):
                return
        else:
            console.print(f"\n[yellow]Update available:[/yellow] {current_version} -> {SLASH_COMMAND_VERSION}")
            if not click.confirm("Update slash command?", default=True):
                return
    else:
        console.print(f"\n[cyan]Claude Code slash command not found[/cyan]")
        console.print(f"Will create: {claude_file}")
        if not click.confirm("\nCreate slash command?", default=True):
            return

    # Create/update the file
    try:
        _create_slash_command(claude_file)
        print_success(f"Slash command created/updated!")
        console.print(f"\n[dim]Location:[/dim] {claude_file}")
        console.print(f"[dim]Version:[/dim] {SLASH_COMMAND_VERSION}")
        console.print(f"\n[cyan]Usage:[/cyan] Type [bold]/journel[/bold] in Claude Code to load instructions")
    except Exception as e:
        print_error(f"Failed to create slash command: {e}")


@main.command(name="ai-setup-claude")
def ai_setup_claude():
    """Update Claude Code slash command (non-interactive, LLM-friendly).

    Checks and updates .claude/commands/journel.md without prompts.
    Designed for use by AI assistants (like Claude Code).

    Exit codes:
        0 - Already up to date (no action needed)
        1 - File was created/updated (LLM should re-read)
        2 - Error occurred

    Output format (parseable by LLMs):
        [OK] Instructions current (v1.0.0)
        [OK] Updated to v1.0.1 - Re-reading instructions...
    """
    claude_file = Path.cwd() / ".claude" / "commands" / "journel.md"

    try:
        if not claude_file.exists():
            # Create new file
            _create_slash_command(claude_file)
            console.print(f"[green][OK][/green] Created slash command v{SLASH_COMMAND_VERSION}")
            console.print(f"[yellow]>>>[/yellow] Re-read {claude_file} for current instructions")
            sys.exit(1)  # Signal update occurred

        # Check version
        current_version = _parse_version_from_file(claude_file)

        if current_version == SLASH_COMMAND_VERSION:
            # Already current
            console.print(f"[green][OK][/green] Instructions current (v{SLASH_COMMAND_VERSION})")
            sys.exit(0)  # No update needed

        # Update needed
        _create_slash_command(claude_file)
        console.print(f"[green][OK][/green] Updated to v{SLASH_COMMAND_VERSION} (was v{current_version})")
        console.print(f"[yellow]>>>[/yellow] Re-read {claude_file} for current instructions")
        sys.exit(1)  # Signal update occurred

    except Exception as e:
        console.print(f"[red][ERROR][/red] {e}")
        sys.exit(2)  # Error occurred


# ===== AI Integration Commands =====
# These commands allow AI assistants (like Claude Code) to track their contributions
# with clear attribution. Supports pair programming mental model and learning focus.

@main.command(name="ai-log")
@click.argument("project_or_message")
@click.argument("message", required=False)
@click.option("--hours", "-h", type=float, help="Hours spent")
@click.option("--agent", "-a", default="claude-code", help="AI agent name (default: claude-code)")
def ai_log(project_or_message, message, hours, agent):
    """Log AI-assisted work with clear attribution.

    Same as 'jnl log' but marks the entry as AI-assisted.

    Usage:
        jnl ai-log "Fixed bug (2h)"                    - AI work (auto-detect project)
        jnl ai-log journel "Fixed bug (2h)"            - AI work on specific project
        jnl ai-log journel "Feature" --agent cursor    - Specify different AI agent

    This is for Tier 1 (Suggested Actions) - the user must explicitly approve and run
    this command. For Claude Code users, this can be used via slash commands.
    """
    storage = get_storage()

    # Same logic as regular log command
    project_auto_detected = False
    time_parsed = False

    # Determine if first arg is project or message
    project = None
    if message is not None:
        project = project_or_message
        actual_message = message
    else:
        actual_message = project_or_message
        cwd = Path.cwd()
        potential_id = slugify(cwd.name)
        if storage.load_project(potential_id):
            project = potential_id
            project_auto_detected = True

    # Parse time from message if not explicitly provided
    if hours is None:
        actual_message, parsed_hours = parse_time_from_message(actual_message)
        if parsed_hours:
            hours = parsed_hours
            time_parsed = True

    # Create log entry with AI attribution
    entry = LogEntry(
        date=date.today(),
        project=project,
        message=actual_message,
        hours=hours,
        ai_assisted=True,  # Mark as AI-assisted
        agent=agent,       # Track which agent
    )

    storage.add_log_entry(entry)

    # Update project last_active
    project_name = None
    if project:
        proj = storage.load_project(project)
        if proj:
            proj.last_active = date.today()
            storage.save_project(proj)
            storage.update_project_index()
            project_name = proj.name

    # Enhanced feedback with AI marker
    print_success(f"[AI] Logged: \"{actual_message}\"")

    if project:
        if project_auto_detected:
            console.print(f"[cyan]>>>[/cyan] Project: [bold]{project_name or project}[/bold] [dim](auto-detected)[/dim]")
        else:
            console.print(f"[cyan]>>>[/cyan] Project: [bold]{project_name or project}[/bold]")
    else:
        console.print(f"[yellow]>>>[/yellow] [dim]No project linked[/dim]")

    if hours:
        if time_parsed:
            console.print(f"[cyan]>>>[/cyan] Time: [bold]{hours}h[/bold] [dim](parsed)[/dim]")
        else:
            console.print(f"[cyan]>>>[/cyan] Time: [bold]{hours}h[/bold]")

    console.print(f"[magenta]>>>[/magenta] Agent: [bold]{agent}[/bold]")


@main.command(name="ai-start")
@click.argument("project_id")
@click.argument("task", required=False, default="")
@click.option("--force", "-f", is_flag=True, help="Auto-stop existing session")
@click.option("--agent", "-a", default="claude-code", help="AI agent name (default: claude-code)")
@click.pass_context
def ai_start(ctx, project_id, task, force, agent):
    """Start an AI-assisted work session.

    Same as 'jnl start' but marks the session as AI-assisted.

    Usage:
        jnl ai-start myproject                         - Start AI session
        jnl ai-start myproject "Fix bug #123"          - With task description
        jnl ai-start myproject --force                 - Auto-stop existing session
        jnl ai-start myproject --agent cursor          - Different AI agent

    This enables tracking of pair programming sessions with AI assistants.
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    # Load project
    project = storage.load_project(project_id)
    if not project:
        print_error(f"Project '{project_id}' not found")
        print_info("Use 'jnl list' to see available projects")
        return

    # Start AI-assisted session
    try:
        session = session_manager.start_session(project, task=task, force=force)

        # Mark as AI-assisted
        session.ai_assisted = True
        session.agent = agent
        storage.save_active_session(session)

        from .display import print_session_started
        print_session_started(session, project)
        console.print(f"[magenta]>>>[/magenta] AI Agent: [bold]{agent}[/bold]")

    except ValueError as e:
        print_error(str(e))
        print_info("Use 'jnl stop' to end current session, or --force to auto-stop")


@main.command(name="ai-stop")
@click.argument("notes", required=False, default="")
@click.option("--agent", "-a", default=None, help="Override agent name")
@click.pass_context
def ai_stop(ctx, notes, agent):
    """End an AI-assisted work session.

    Same as 'jnl stop' but with AI-focused reflection prompts.

    Usage:
        jnl ai-stop                                    - End AI session (interactive)
        jnl ai-stop "Completed feature X"              - End with notes

    Prompts focus on learning and knowledge transfer from AI collaboration.
    """
    no_emoji = ctx.obj.get('no_emoji', False) if ctx.obj else False
    storage = get_storage(no_emoji)
    session_manager = SessionManager.get_instance(storage)

    # Check if session exists
    active_session = session_manager.get_active_session()
    if not active_session:
        print_error("No active session")
        print_info("Start a session with: jnl ai-start <project>")
        return

    # Get notes with AI-focused prompt if not provided
    if not notes:
        notes = click.prompt(
            "\nWhat did you accomplish with AI assistance? What did you learn? (optional, press Enter to skip)",
            default="",
            show_default=False
        )

    # Override agent if specified
    if agent:
        active_session.agent = agent
        storage.save_active_session(active_session)

    # Stop session (this will create AI-attributed log entry)
    session = session_manager.stop_session(notes=notes)

    if session:
        from .display import print_session_stopped
        print_session_stopped(session, storage.load_project(session.project_id))
        if session.agent:
            console.print(f"[magenta]>>>[/magenta] Agent: [bold]{session.agent}[/bold]")


@main.command(name="help")
@click.argument("command", required=False)
@click.option("--all", "show_all", is_flag=True, help="Show all commands (complete reference)")
@click.pass_context
def help_command(ctx, command, show_all):
    """Show help for JOURNEL commands.

    \b
    Usage:
      jnl help              Simplified help (essential commands)
      jnl help --all        Complete command reference
      jnl help <command>    Focused help for a specific command

    \b
    Examples:
      jnl help              Show the basics
      jnl help status       Quick help for 'status' command
      jnl help --all        See all 26+ commands
    """
    from .help_text import get_simplified_help, get_full_help, get_command_help

    # jnl help <command> - Show focused help for specific command
    if command:
        help_text = get_command_help(command)
        if help_text:
            console.print(help_text)
        else:
            # Command doesn't have custom focused help, fall back to --help
            cmd = ctx.parent.command.get_command(ctx, command)
            if cmd is None:
                print_error(f"Unknown command: '{command}'")
                console.print("\n[dim]Run[/dim] [cyan]jnl help[/cyan] [dim]to see available commands.[/dim]\n")
                ctx.exit(1)

            print_info(f"Showing detailed help for '{command}':")
            console.print()
            ctx.invoke(cmd, ["--help"])
        return

    # jnl help --all - Show complete reference
    if show_all:
        console.print(get_full_help())
        return

    # jnl help - Show simplified essentials
    console.print(get_simplified_help())


def tui_main():
    """Entry point for 'tnl' command - direct TUI launcher."""
    storage = get_storage()
    try:
        from .tui import run_tui
        run_tui(storage)
    except ImportError:
        from .display import print_error, print_info
        print_error("TUI requires 'textual' library")
        print_info("Install with: pip install textual")
        sys.exit(1)


if __name__ == "__main__":
    main()
