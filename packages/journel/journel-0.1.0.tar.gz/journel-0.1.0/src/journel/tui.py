"""Terminal UI for JOURNEL using Textual."""

from datetime import date
from typing import List, Optional

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Label, ListItem, ListView, Static
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.events import Key

from .config import Config
from .storage import Storage
from .models import Project
from .utils import format_date_relative


class ProjectDetail(Static):
    """Widget to display project details."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project: Optional[Project] = None

    def set_project(self, project: Optional[Project]) -> None:
        """Update the displayed project."""
        self.project = project
        if project is None:
            self.update("[dim]No project selected[/dim]")
            return

        # Build rich markup for project details
        details = f"""[bold]{project.full_name or project.name}[/bold]

[cyan]Status:[/cyan] {project.status}
[cyan]Completion:[/cyan] {project.completion}%
[cyan]Last Active:[/cyan] {format_date_relative(project.last_active)}
[cyan]Created:[/cyan] {project.created}
"""

        if project.tags:
            details += f"\n[cyan]Tags:[/cyan] {', '.join(project.tags)}"

        if project.priority != "medium":
            details += f"\n[cyan]Priority:[/cyan] {project.priority}"

        if project.next_steps:
            details += f"\n\n[bold yellow]Next Steps:[/bold yellow]\n{project.next_steps}"

        if project.blockers:
            details += f"\n\n[bold red]Blockers:[/bold red]\n{project.blockers}"

        if project.github:
            details += f"\n\n[cyan]GitHub:[/cyan] {project.github}"

        if project.claude_project:
            details += f"\n[cyan]Claude:[/cyan] {project.claude_project}"

        if project.learned:
            details += f"\n\n[bold green]Learned:[/bold green]\n{project.learned}"

        self.update(details)


class ProjectListItem(ListItem):
    """Custom list item for projects."""

    def __init__(self, project: Project, *args, **kwargs):
        self.project = project

        # Build the label
        status_icon = {
            "in-progress": "▶",
            "completed": "✓",
            "dormant": "⏸",
            "archived": "📦",
        }.get(project.status, "•")

        self.label_text = f"{status_icon} {project.name} ({project.completion}%)"
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        """Compose the list item with a label."""
        yield Static(self.label_text)


class HelpScreen(ModalScreen):
    """Modal screen to display help information."""

    CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 70;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: thick $primary;
        padding: 2 3;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
        ("question_mark", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help dialog."""
        help_text = """[bold cyan]JOURNEL TUI - Keyboard Shortcuts[/bold cyan]

[bold]Navigation:[/bold]
  ↑/↓ or j/k    - Move selection up/down
  [dim]Arrow keys and vim keys both work to navigate the project list[/dim]

[bold]Filters:[/bold]
  A             - Active projects
  D             - Dormant projects
  C             - Completed projects
  X             - Archived projects
  *             - All projects

[bold]Actions:[/bold]
  Shift+W       - Mark selected project as completed (Win!)
  Backspace     - Archive selected project
  U             - Unarchive selected project
  E             - Edit project (opens in external editor)

[bold]Other:[/bold]
  R             - Refresh project list
  Ctrl+\\        - Command palette
  ?             - Toggle this help
  Q or Esc      - Quit / Close help

[dim]Press any key to close this help...[/dim]"""

        with Container(id="help-dialog"):
            yield Static(help_text)

    def on_key(self, event: Key) -> None:
        """Close on any keypress except the ones that would break things."""
        # Don't dismiss on modifier keys
        if event.key not in ("ctrl", "shift", "alt"):
            self.dismiss()

    def action_dismiss(self) -> None:
        """Dismiss the help screen."""
        self.dismiss()


class JournelTUI(App):
    """A Textual TUI for JOURNEL."""

    CSS = """
    Screen {
        layout: vertical;
    }

    #main-container {
        layout: horizontal;
        height: 100%;
    }

    #left-panel {
        width: 35%;
        border: solid $primary;
    }

    #right-panel {
        width: 65%;
        border: solid $secondary;
        padding: 1 2;
    }

    ListView {
        height: 100%;
    }

    ListView:focus {
        border: solid $accent;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: $boost;
    }

    ListItem.-selected {
        background: $primary;
        text-style: bold;
    }

    #status-bar {
        dock: bottom;
        height: 1;
        background: $boost;
        color: $text;
        padding: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", key_display="Q"),
        Binding("a", "filter_active", "Active", key_display="A"),
        Binding("d", "filter_dormant", "Dormant", key_display="D"),
        Binding("c", "filter_completed", "Completed", key_display="C"),
        Binding("x", "filter_archived", "Archived", key_display="X"),
        Binding("asterisk", "filter_all", "All", key_display="*"),
        Binding("r", "refresh", "Refresh", key_display="R"),
        Binding("question_mark", "show_help", "Help", key_display="?"),
        Binding("W", "complete_project", "Win!", key_display="Shift+W"),
        Binding("backspace", "archive_project", "Archive"),
        Binding("u", "unarchive_project", "Unarchive"),
        Binding("e", "edit_project", "Edit"),
    ]

    def __init__(self, storage: Storage):
        super().__init__()
        self.storage = storage
        self.config = storage.config
        self.current_filter = "active"
        self.projects: List[Project] = []
        self.selected_project: Optional[Project] = None

    def compose(self) -> ComposeResult:
        """Create child widgets."""
        yield Header()

        with Horizontal(id="main-container"):
            with Vertical(id="left-panel"):
                yield ListView(id="project-list")

            with Vertical(id="right-panel"):
                yield ProjectDetail(id="project-detail")

        yield Static("A:Active | D:Dormant | C:Completed | X:Archived | *:All | R:Refresh | ?:Help | Q:Quit", id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """Set up the app when mounted."""
        self.title = "JOURNEL - Project Browser"
        self.sub_title = f"Filter: {self.current_filter.title()}"
        self.load_projects()

    def load_projects(self) -> None:
        """Load projects based on current filter."""
        dormant_days = self.config.get("dormant_days", 14)

        if self.current_filter == "all":
            self.projects = self.storage.list_projects(include_archived=True)
        elif self.current_filter == "archived":
            self.projects = self.storage.list_projects(status="archived")
        elif self.current_filter == "completed":
            self.projects = self.storage.list_projects(status="completed")
        elif self.current_filter == "dormant":
            all_projects = self.storage.list_projects()
            self.projects = [
                p for p in all_projects
                if p.status == "in-progress" and p.days_since_active() > dormant_days
            ]
        else:  # active
            all_projects = self.storage.list_projects()
            self.projects = [
                p for p in all_projects
                if p.status == "in-progress" and p.days_since_active() <= dormant_days
            ]

        # Sort by last_active
        self.projects.sort(key=lambda p: p.last_active, reverse=True)

        # Update the list
        list_view = self.query_one("#project-list", ListView)
        list_view.clear()

        if not self.projects:
            # Provide helpful empty state based on filter
            if self.current_filter == "all":
                msg = "[dim]No projects yet.\n\nCreate one with:[/dim]\n[cyan]jnl new my-project[/cyan]"
            else:
                msg = f"[dim]No {self.current_filter} projects.\n\nPress [cyan]*[/cyan] to see all projects.[/dim]"

            # Wrap Label in ListItem to satisfy ListView's assertion that all children are ListItems
            empty_item = ListItem(Label(msg))
            list_view.append(empty_item)
        else:
            for project in self.projects:
                list_view.append(ProjectListItem(project))

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        """Handle project selection (Enter key or click)."""
        # Get detail widget
        detail = self.query_one("#project-detail", ProjectDetail)

        # Only handle ProjectListItem selections
        if not isinstance(event.item, ProjectListItem):
            # Clear selection for invalid items (like empty state)
            self.selected_project = None
            detail.set_project(None)
            return

        # Set selected project
        self.selected_project = event.item.project
        detail.set_project(self.selected_project)

    @on(ListView.Highlighted)
    def on_list_highlighted(self, event: ListView.Highlighted) -> None:
        """Handle project navigation (arrow keys / j/k)."""
        # Get detail widget
        detail = self.query_one("#project-detail", ProjectDetail)

        # Only handle ProjectListItem highlights
        if event.item is None or not isinstance(event.item, ProjectListItem):
            # Clear for invalid items (like empty state)
            self.selected_project = None
            detail.set_project(None)
            return

        # Update selected project as user navigates
        self.selected_project = event.item.project
        detail.set_project(self.selected_project)

    def action_filter_active(self) -> None:
        """Filter to show only active projects."""
        self.current_filter = "active"
        self.sub_title = "Filter: Active"
        self.load_projects()

    def action_filter_dormant(self) -> None:
        """Filter to show only dormant projects."""
        self.current_filter = "dormant"
        self.sub_title = "Filter: Dormant"
        self.load_projects()

    def action_filter_completed(self) -> None:
        """Filter to show only completed projects."""
        self.current_filter = "completed"
        self.sub_title = "Filter: Completed"
        self.load_projects()

    def action_filter_archived(self) -> None:
        """Filter to show only archived projects."""
        self.current_filter = "archived"
        self.sub_title = "Filter: Archived"
        self.load_projects()

    def action_filter_all(self) -> None:
        """Show all projects."""
        self.current_filter = "all"
        self.sub_title = "Filter: All"
        self.load_projects()

    def action_refresh(self) -> None:
        """Refresh the project list."""
        self.load_projects()
        self.notify("Projects refreshed")

    def action_show_help(self) -> None:
        """Show help modal."""
        self.push_screen(HelpScreen())

    def action_complete_project(self) -> None:
        """Mark selected project as completed."""
        if not self.selected_project:
            self.notify("No project selected", severity="warning")
            return

        if self.selected_project.status == "completed":
            self.notify("Project is already completed", severity="warning")
            return

        # Mark as complete
        self.selected_project.status = "completed"
        self.selected_project.completion = 100
        self.selected_project.last_active = date.today()
        self.storage.move_to_completed(self.selected_project)
        self.storage.update_project_index()

        self.notify(f"✓ Completed: {self.selected_project.name}", severity="information")
        self.action_refresh()

    def action_archive_project(self) -> None:
        """Archive the selected project."""
        if not self.selected_project:
            self.notify("No project selected", severity="warning")
            return

        if self.selected_project.status == "archived":
            self.notify("Project is already archived", severity="warning")
            return

        self.storage.move_to_archived(self.selected_project)
        self.storage.update_project_index()

        self.notify(f"📦 Archived: {self.selected_project.name}", severity="information")
        self.action_refresh()

    def action_unarchive_project(self) -> None:
        """Unarchive the selected project."""
        if not self.selected_project:
            self.notify("No project selected", severity="warning")
            return

        if self.selected_project.status != "archived":
            self.notify("Project is not archived", severity="warning")
            return

        self.storage.unarchive_project(self.selected_project)
        self.storage.update_project_index()

        self.notify(f"▶ Unarchived: {self.selected_project.name}", severity="information")
        self.action_refresh()

    def action_edit_project(self) -> None:
        """Edit the selected project."""
        if self.selected_project:
            self.notify(f"Use 'jnl edit {self.selected_project.id}' to edit in your editor", severity="information")
        else:
            self.notify("No project selected", severity="warning")


def run_tui(storage: Storage) -> None:
    """Run the TUI application with error handling and terminal recovery."""
    import sys
    import traceback

    app = JournelTUI(storage)

    try:
        app.run()
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        pass
    except Exception as e:
        # Ensure terminal is restored on crash
        try:
            # Force terminal reset sequences
            sys.stdout.write('\033[?1049l')  # Exit alternate screen
            sys.stdout.write('\033[?25h')     # Show cursor
            sys.stdout.write('\033[0m')       # Reset colors
            sys.stdout.flush()
        except Exception:
            pass  # If stdout is broken, nothing we can do

        # Print error information
        print(f"\n❌ TUI Error: {e}", file=sys.stderr)
        print("\n📋 Full traceback:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        print("\n💡 If your terminal is broken, try running: reset", file=sys.stderr)
        print("💡 Please report this issue at: https://github.com/yourusername/JOURNEL/issues\n", file=sys.stderr)
        sys.exit(1)
