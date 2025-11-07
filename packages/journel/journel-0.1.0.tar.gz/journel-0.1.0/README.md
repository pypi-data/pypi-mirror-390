# JOURNEL

![Status](https://img.shields.io/badge/status-active%20development-orange)
![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)

**JOURNEL** is an ADHD-friendly project organization and tracking system designed to help maintain focus, restore context, and celebrate completion.

> ⚠️ **Active Development Notice**: JOURNEL is in active development. Features and commands may change. The TUI interface is experimental. If you're trying it out, please report any issues!

## Why JOURNEL?

Homage to André Journel (geostatistics pioneer, GSLIB) + Journal (project logging)

## Features

- **Zero friction** - CLI commands are 2-3 words max (`jnl status`, `jnl log`)
- **Plain text storage** - Markdown + YAML, git-versioned, human-readable
- **Context restoration** - Pick up where you left off with `jnl resume`
- **Gentle gate-keeping** - Warns when you have too many active projects
- **Completion rituals** - Celebrate finishing with `jnl done`
- **LLM-friendly** - Export context for Claude or other AI assistants
- **Statistics & insights** - Track your progress with `jnl stats` and `jnl wins`
- **Flexible output** - Use `--no-emoji` flag for ASCII-only terminals

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/endarthur/journel.git
cd journel

# Install in development mode
pip install -e .
```

### Requirements

- Python 3.8+
- Dependencies: click, rich, pyyaml, gitpython (installed automatically)

## Quick Start

```bash
# Initialize JOURNEL (creates ~/.journel/)
journel init

# Create your first project (natural syntax!)
journel new my-project "My Awesome Project" --tags "python,web"

# Check status (also the default command)
journel
jnl status

# Log your work (even more natural!)
jnl log my-project "Fixed the authentication bug (2h)"

# Get context for AI assistance
jnl ctx
jnl ask "What should I work on today?"

# Complete a project (triggers celebration!)
jnl done my-project

# View your achievements
jnl wins
jnl stats
```

## All Commands

### Setup & Info
- `journel init` - Set up JOURNEL for first use
- `journel status` - Show all projects (default command)
- `journel stats` - Show overall statistics and insights
- `journel wins` - Show completed projects and achievements

### Project Management
- `journel new <name> [description]` - Create a new project (with gate-keeping)
- `journel list [--active|--dormant|--completed] [--tag <tag>]` - List projects with filters
- `journel edit <project>` - Open project file in $EDITOR
- `journel link <project> <url>` - Add GitHub or Claude project URL
- `journel done <project>` - Mark project as complete with celebration ritual

### Daily Workflow
- `journel log [project] "<message>"` - Quick activity logging (auto-detects project if omitted)
- `journel note "<text>"` - Quick note capture
- `journel resume <project>` - Restore context for picking up work

### AI Integration
- `journel ctx [question]` - Export context for LLM analysis
- `journel ask "<question>"` - Format a question with auto-gathered context

### Sync
- `journel sync` - Sync JOURNEL data with git remote

### Options
- `--no-emoji` - Use ASCII-only output (useful for compatibility)
- `--version` - Show version
- `--help` - Show help for any command

## Examples

### Starting Your Day

```bash
# See what's active
jnl

# Resume work on a project
jnl resume my-project
# Shows: last commit, next steps, blockers, links
```

### Logging Progress

```bash
# Quick log (auto-detects project from current directory)
jnl log "Implemented user authentication (2h)"

# Explicit project with time tracking
jnl log backend "Fixed database migration (3h)"

# Just a message, time parsed automatically
jnl log myproject "Refactored API - 1.5h"

# Add a note
jnl note "Remember to test with PostgreSQL"
```

### Getting Help from AI

```bash
# Export context to copy/paste to Claude
jnl ctx

# Ask a specific question
jnl ask "Which project should I prioritize?"

# Focus on one project
jnl ctx --project my-project "How can I optimize this?"
```

### Completing Projects

```bash
jnl done my-project
# Prompts: "What did you learn?"
# Prompts: "How do you feel?"
# Shows celebration message!
```

### Tracking Progress

```bash
# See all your wins
jnl wins

# View statistics
jnl stats
# Shows: completion rate, active projects, streaks, etc.

# List specific projects
jnl list --active
jnl list --tag python
```

## Data Storage

All data lives in `~/.journel/`:

```
~/.journel/
├── README.md              # System documentation
├── config.yaml            # Your preferences
├── projects/              # Active project files (*.md)
├── completed/             # Completed project files
├── logs/                  # Monthly activity logs
├── .meta/                 # Machine-readable indexes
└── .git/                  # Version control
```

Files are plain Markdown with YAML frontmatter - you can edit them directly or use the CLI.

## Configuration

Edit `~/.journel/config.yaml`:

```yaml
editor: code                    # Or vim, nano, etc.
max_active_projects: 5          # Warn when exceeded
completion_celebration: true    # Show celebration on completion
auto_git_commit: true           # Auto-commit changes
gentle_nudges: true             # Show tips and suggestions
dormant_days: 14                # Days until project is dormant
use_emojis: true                # Use emojis in output
```

Or use `--no-emoji` flag per-command.

## Philosophy

JOURNEL is an **accountability buddy**, not just an organization tool.

### ADHD-Friendly Design Principles

1. **Zero Friction** - Commands are fast and simple
2. **Instant Feedback** - No waiting, immediate results
3. **Forgiving** - No perfect tracking required, easy to catch up
4. **Visual** - Colors, emojis (optional), clear status
5. **Non-judgmental** - "Dormant" not "abandoned"
6. **Context-Rich** - Links to conversations, commits, notes
7. **Wins-Focused** - Track and celebrate completions

### What JOURNEL Helps With

- ✅ Finish more projects (gentle gate-keeping)
- ✅ Reduce "what was I doing?" moments (context restoration)
- ✅ Less guilt about project-hopping (forgiving tracking)
- ✅ Celebrate wins (completion rituals)
- ✅ Work with AI assistants (LLM-friendly exports)

### What JOURNEL is NOT

- ❌ Not a full project management system (no Gantt charts)
- ❌ Not a time tracker (just rough logging)
- ❌ Not an IDE integration (stays simple)
- ❌ Not multi-user (personal tool only)

## Development

JOURNEL was developed with the assistance of Claude Code (Sonnet 4.5) through collaborative pair programming. The AI integration features (`jnl ctx`, `jnl ask`, AI session tracking) were built alongside the tool itself - practicing the same AI-assisted workflow that JOURNEL helps users track.

This transparency is intentional: JOURNEL is designed to work *with* AI assistants, not hide them. The project serves as both a practical tool and a demonstration of effective AI-human collaboration in software development.

## Contributing

Contributions are welcome! JOURNEL is in active development and feedback is highly valued.

- **Bug reports**: Please open an issue with details about your environment and steps to reproduce
- **Feature requests**: Open an issue to discuss the idea first
- **Pull requests**: For major changes, please open an issue first to discuss what you'd like to change
- **Documentation**: Improvements to docs, examples, and guides are always appreciated

## Roadmap

Current focus areas:

- **Core stability** - Refining the CLI commands and data model
- **TUI refinement** - The interactive interface is experimental and needs polish
- **AI integration** - Expanding Claude Code integration and LLM context features
- **Testing** - Adding comprehensive test coverage
- **Documentation** - More examples, guides, and use cases

See the [issues](https://github.com/endarthur/journel/issues) for specific planned features and known bugs.

## Authors

**Arthur Endlein** (endarthur@gmail.com) - Creator and maintainer

**Claude Code (Sonnet 4.5)** - AI pair programming partner

## License

MIT
