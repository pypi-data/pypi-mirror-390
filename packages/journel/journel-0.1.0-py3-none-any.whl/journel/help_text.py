"""Help text content for JOURNEL CLI."""

# Simplified help - shows only essential commands (ADHD-friendly, low cognitive load)
SIMPLIFIED_HELP = """[bold cyan]JOURNEL[/bold cyan] - Track projects without the chaos

[bold]GETTING STARTED[/bold] (first time?)
  jnl init                 Set up JOURNEL
  jnl new MyProject        Start your first project

[bold]YOUR DAILY COMMANDS[/bold] (use these most)
  jnl status               What's active? (default command)
  jnl log "did a thing"    Quick note (auto-detects project)

  jnl start PROJECT        Begin focused work session
  jnl stop                 End session (captures time)

[bold]WHEN YOU NEED MORE[/bold]
  jnl list                 Browse all projects
  jnl done PROJECT         Complete & celebrate!
  jnl wins                 See your achievements

[dim]------------------------------------------------[/dim]
[bold]New to JOURNEL?[/bold]  Try: [cyan]jnl init[/cyan]
[bold]See all commands:[/bold] [cyan]jnl help --all[/cyan]
[bold]Help for a command:[/bold] [cyan]jnl help <command>[/cyan] or [cyan]jnl <command> --help[/cyan]
"""


# Full help - complete reference with all commands
FULL_HELP = """[bold cyan]JOURNEL[/bold cyan] - ADHD-friendly project organization

[bold]DAILY WORKFLOW[/bold]
  status                   What's active right now? (default command)
  log MESSAGE              Quick note (auto-detects project from directory)

  start PROJECT [TASK]     Begin tracked work session
  stop [NOTES]             End session & save time
  pause                    Take a break (pauses timer)
  continue                 Resume paused session

[bold]PROJECT MANAGEMENT[/bold]
  new NAME [DESC]          Create new project (with gatekeeping)
  list [--filter]          Browse all projects
  edit PROJECT             Open in your editor

  done PROJECT             Mark complete (celebration!)
  resume PROJECT           Pick up old work (shows context)
  archive PROJECT          Hide from view (not done, just shelved)
  unarchive PROJECT        Restore archived project

[bold]REFLECTION & INSIGHTS[/bold]
  wins                     Your completed projects & streaks
  stats                    Time tracking & productivity stats

  ctx [QUESTION]           Export context for AI chat
  ask QUESTION             Ask AI about your projects

[bold]AI PAIR PROGRAMMING[/bold]
  ai-start PROJECT [TASK]  Start AI-assisted session
  ai-log MESSAGE           Log AI work (clear attribution)
  ai-stop [NOTES]          End AI session (with learning notes)

[bold]TOOLS & SETUP[/bold]
  init                     First-time setup
  link PROJECT URL         Connect GitHub/Claude projects
  note MESSAGE             Quick note capture
  sync                     Git sync across machines

  setup-claude             Install Claude Code integration
  tui                      Interactive browser (EXPERIMENTAL)

[dim]------------------------------------------------[/dim]
[bold]Just the basics?[/bold]     [cyan]jnl help[/cyan]
[bold]Help on a command?[/bold]   [cyan]jnl help <command>[/cyan] or [cyan]jnl <command> --help[/cyan]
[bold]First time here?[/bold]     [cyan]jnl init[/cyan]
"""


# Focused help for individual commands (shorter, more digestible)
COMMAND_HELP = {
    "status": """[bold cyan]jnl status[/bold cyan] - What's active right now?

[bold]USAGE[/bold]
  jnl status
  jnl              (same - status is the default)

[bold]WHAT IT SHOWS[/bold]
  - Active projects (worked on recently)
  - Dormant projects (no activity for 14+ days)
  - Completed projects
  - Current work session (if any)

[bold]WHEN TO USE IT[/bold]
  - Starting your day: "What should I work on?"
  - After a break: "Where was I?"
  - Checking in: "Am I juggling too many projects?"

[dim]Full details: jnl status --help[/dim]
""",

    "log": """[bold cyan]jnl log[/bold cyan] - Quick note capture

[bold]USAGE[/bold]
  jnl log "your message here"
  jnl log "fixed the bug (2h)"          (tracks time)

[bold]WHAT IT DOES[/bold]
  - Auto-detects project from current directory
  - Captures your note with timestamp
  - Optionally tracks time: "(2h)" or "(30m)"
  - No need to specify project ID

[bold]WHEN TO USE IT[/bold]
  - Capture a thought before you forget
  - Log progress without interrupting flow
  - Quick time tracking

[bold]EXAMPLES[/bold]
  jnl log "implemented user auth"
  jnl log "refactored database layer (3h)"
  jnl log "meeting with stakeholders"

[dim]Full details: jnl log --help[/dim]
""",

    "start": """[bold cyan]jnl start[/bold cyan] - Begin focused work session

[bold]USAGE[/bold]
  jnl start PROJECT
  jnl start PROJECT "task description"

[bold]WHAT IT DOES[/bold]
  - Starts a timer for focused work
  - Tracks time automatically
  - Shows elapsed time in status
  - Prevents hyperfocus (you'll know how long you've been working)

[bold]WHEN TO USE IT[/bold]
  - Starting a work session
  - Need time awareness
  - Want to track billable hours

[bold]EXAMPLES[/bold]
  jnl start journel
  jnl start journel "fixing TUI bugs"

[dim]End session: jnl stop
Pause session: jnl pause
Full details: jnl start --help[/dim]
""",

    "stop": """[bold cyan]jnl stop[/bold cyan] - End your work session

[bold]USAGE[/bold]
  jnl stop
  jnl stop "optional completion note"

[bold]WHAT IT DOES[/bold]
  - Stops the timer
  - Saves total session time
  - Shows what you accomplished
  - Logs to your project

[bold]WHEN TO USE IT[/bold]
  - Taking a break
  - Switching projects
  - End of work day

[dim]Pause instead: jnl pause
Resume paused: jnl continue
Full details: jnl stop --help[/dim]
""",

    "new": """[bold cyan]jnl new[/bold cyan] - Create a new project

[bold]USAGE[/bold]
  jnl new ProjectName
  jnl new ProjectName "optional description"

[bold]WHAT IT DOES[/bold]
  - Creates a new project
  - Gate-keeps: asks if you have capacity
  - Sets up tracking structure
  - ADHD-friendly: prevents overcommitment

[bold]WHEN TO USE IT[/bold]
  - Starting something new
  - Got a new idea (but check capacity first!)

[bold]EXAMPLES[/bold]
  jnl new my-website
  jnl new blog "Personal tech blog"

[dim]Full details: jnl new --help[/dim]
""",

    "done": """[bold cyan]jnl done[/bold cyan] - Complete a project with celebration!

[bold]USAGE[/bold]
  jnl done PROJECT

[bold]WHAT IT DOES[/bold]
  - Marks project as complete
  - Celebrates your win!
  - Tracks completion in your history
  - Removes from active list

[bold]WHEN TO USE IT[/bold]
  - You finished something!
  - Need that dopamine hit
  - Want to celebrate progress

[bold]EXAMPLES[/bold]
  jnl done journel

[dim]View wins: jnl wins
Full details: jnl done --help[/dim]
""",

    "list": """[bold cyan]jnl list[/bold cyan] - Browse all projects

[bold]USAGE[/bold]
  jnl list
  jnl list --active
  jnl list --completed
  jnl list --dormant
  jnl list --archived

[bold]WHAT IT SHOWS[/bold]
  - All your projects with details
  - Filterable by status
  - Last activity dates
  - Completion percentages

[bold]WHEN TO USE IT[/bold]
  - Need to see everything
  - Looking for a specific project
  - Want more detail than status

[dim]Full details: jnl list --help[/dim]
""",

    "wins": """[bold cyan]jnl wins[/bold cyan] - Celebrate your achievements!

[bold]USAGE[/bold]
  jnl wins

[bold]WHAT IT SHOWS[/bold]
  - All completed projects
  - Completion streaks
  - Your productivity stats
  - Positive reinforcement!

[bold]WHEN TO USE IT[/bold]
  - Feeling unproductive (you'll see you've done more than you think!)
  - Need motivation
  - Want to celebrate progress
  - End of week reflection

[dim]Full details: jnl wins --help[/dim]
""",

    "init": """[bold cyan]jnl init[/bold cyan] - First-time setup

[bold]USAGE[/bold]
  jnl init

[bold]WHAT IT DOES[/bold]
  - Creates JOURNEL directory structure
  - Sets up config files
  - Shows welcome message
  - Gets you ready to track!

[bold]WHEN TO USE IT[/bold]
  - First time using JOURNEL
  - Setting up on a new machine

[dim]Full details: jnl init --help[/dim]
""",

    "ctx": """[bold cyan]jnl ctx[/bold cyan] - Export context for AI

[bold]USAGE[/bold]
  jnl ctx
  jnl ctx "optional question for the AI"

[bold]WHAT IT DOES[/bold]
  - Exports all your project context
  - Formats for LLM consumption
  - Includes recent activity
  - Optionally adds your question

[bold]WHEN TO USE IT[/bold]
  - Planning with Claude Code
  - Need AI help prioritizing
  - Want project suggestions

[bold]EXAMPLES[/bold]
  jnl ctx
  jnl ctx "what should I focus on this week?"

[dim]Full details: jnl ctx --help[/dim]
""",

    "resume": """[bold cyan]jnl resume[/bold cyan] - Pick up where you left off

[bold]USAGE[/bold]
  jnl resume PROJECT

[bold]WHAT IT DOES[/bold]
  - Shows recent activity
  - Reminds you what you were doing
  - Displays notes and logs
  - Helps restore context after breaks

[bold]WHEN TO USE IT[/bold]
  - Been away from a project
  - Coming back after interruption
  - "What was I doing?"

[dim]Full details: jnl resume --help[/dim]
""",
}


def get_simplified_help() -> str:
    """Get simplified help text (essential commands only)."""
    return SIMPLIFIED_HELP


def get_full_help() -> str:
    """Get full help text (complete reference)."""
    return FULL_HELP


def get_command_help(command: str) -> str:
    """Get focused help for a specific command.

    Args:
        command: Command name (e.g., 'status', 'log')

    Returns:
        Focused help text, or empty string if not available
    """
    return COMMAND_HELP.get(command, "")
