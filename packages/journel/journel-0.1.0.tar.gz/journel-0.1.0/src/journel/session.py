"""Session management for JOURNEL.

Handles active work sessions, tracking time, pauses, and context.
"""

import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import Project, Session
from .storage import Storage


class SessionManager:
    """Manages work sessions (singleton pattern).

    Tracks active sessions, handles pauses/resumes, and captures context
    for ADHD-friendly time awareness and interruption recovery.
    """

    _instance: Optional["SessionManager"] = None

    def __init__(self, storage: Storage):
        """Initialize SessionManager (use get_instance() instead)."""
        self.storage = storage
        self.active_session: Optional[Session] = None
        self._load_active_session()

    @classmethod
    def get_instance(cls, storage: Storage) -> "SessionManager":
        """Get or create the SessionManager singleton."""
        if cls._instance is None:
            cls._instance = cls(storage)
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (useful for testing)."""
        cls._instance = None

    def _load_active_session(self) -> None:
        """Load active session from storage on init."""
        self.active_session = self.storage.load_active_session()

    def _capture_context(self, project: Project) -> dict:
        """Capture current context for session restoration.

        Captures: git branch, last commit, current directory, etc.
        """
        context = {}

        # Try to get git context
        try:
            import git
            # Check if we're in a git repo
            repo_path = Path.cwd()
            if (repo_path / ".git").exists() or any((p / ".git").exists() for p in repo_path.parents):
                repo = git.Repo(repo_path, search_parent_directories=True)
                context["git_branch"] = repo.active_branch.name
                context["git_commit"] = repo.head.commit.hexsha[:7]
                context["git_message"] = repo.head.commit.message.strip().split("\n")[0][:50]
        except Exception:
            # Git context capture is optional
            pass

        # Capture directory context
        context["working_directory"] = str(Path.cwd())

        # Add project links if available
        if project.github:
            context["github_url"] = project.github
        if project.claude_project:
            context["claude_url"] = project.claude_project

        return context

    def start_session(self, project: Project, task: str = "", force: bool = False) -> Session:
        """Start a new work session.

        Args:
            project: The project to work on
            task: Optional task description
            force: If True, auto-stop existing session before starting new one

        Returns:
            The newly created session

        Raises:
            ValueError: If a session is already active and force=False
        """
        if self.active_session and (self.active_session.is_active() or self.active_session.is_paused()):
            if not force:
                raise ValueError(
                    f"Session already active for '{self.active_session.project_id}'. "
                    f"Use force=True to auto-stop it, or run stop_session() first."
                )
            else:
                # Auto-stop existing session with note
                self.stop_session(notes=f"Auto-stopped to start new session on {project.id}")

        # Create new session
        session = Session(
            id=str(uuid.uuid4())[:8],
            project_id=project.id,
            task=task,
            start_time=datetime.now(),
            context_snapshot=self._capture_context(project),
        )

        self.active_session = session
        self.storage.save_active_session(session)

        return session

    def stop_session(self, notes: str = "", create_log_entry: bool = True) -> Optional[Session]:
        """Stop the active session.

        Args:
            notes: Optional notes about what was accomplished
            create_log_entry: If True, also create an entry in activity log (default)

        Returns:
            The stopped session, or None if no active session
        """
        if not self.active_session:
            return None

        # Resume if paused (to calculate final time)
        if self.active_session.is_paused():
            self._resume_from_pause()

        # End the session
        self.active_session.end_time = datetime.now()
        if notes:
            self.active_session.notes = notes

        # Calculate hours for activity log
        elapsed = self.active_session.elapsed_time()
        hours = elapsed.total_seconds() / 3600

        # Save to session log and clear active
        completed_session = self.active_session
        self.storage.append_session_to_log(completed_session)

        # Auto-create activity log entry (links session to existing activity tracking)
        if create_log_entry:
            from .models import LogEntry
            log_message = notes or self.active_session.task or "Work session"
            entry = LogEntry(
                date=self.active_session.start_time.date(),
                project=self.active_session.project_id,
                message=log_message,
                hours=hours,
                ai_assisted=self.active_session.ai_assisted,  # Preserve AI attribution
                agent=self.active_session.agent,  # Preserve agent info
            )
            self.storage.add_log_entry(entry)

        self.storage.clear_active_session()
        self.active_session = None

        return completed_session

    def pause_session(self) -> Optional[Session]:
        """Pause the active session.

        Returns:
            The paused session, or None if no active session
        """
        if not self.active_session:
            return None

        if self.active_session.is_paused():
            raise ValueError("Session is already paused")

        if self.active_session.is_ended():
            raise ValueError("Session has already ended")

        # Mark as paused
        self.active_session.paused_at = datetime.now()
        self.storage.save_active_session(self.active_session)

        return self.active_session

    def resume_session(self) -> Optional[Session]:
        """Resume a paused session.

        Returns:
            The resumed session, or None if no session or not paused
        """
        if not self.active_session:
            return None

        if not self.active_session.is_paused():
            raise ValueError("Session is not paused")

        self._resume_from_pause()
        self.storage.save_active_session(self.active_session)

        return self.active_session

    def _resume_from_pause(self) -> None:
        """Internal method to resume from pause (updates pause duration)."""
        if self.active_session and self.active_session.paused_at:
            pause_elapsed = datetime.now() - self.active_session.paused_at
            self.active_session.pause_duration += pause_elapsed
            self.active_session.paused_at = None

    def get_active_session(self) -> Optional[Session]:
        """Get the current active session.

        Returns:
            The active session, or None if no session active
        """
        return self.active_session

    def get_elapsed_time(self) -> Optional[timedelta]:
        """Get elapsed time of active session (excluding pauses).

        Returns:
            Elapsed time as timedelta, or None if no active session
        """
        if not self.active_session:
            return None

        return self.active_session.elapsed_time()

    def add_interruption(self, description: str) -> None:
        """Record an interruption during the current session.

        Args:
            description: Description of the interruption
        """
        if self.active_session:
            self.active_session.interruptions.append(
                f"{datetime.now().strftime('%H:%M')}: {description}"
            )
            self.storage.save_active_session(self.active_session)

    def should_take_break(self) -> tuple[bool, str]:
        """Check if user should take a break (hyperfocus protection).

        Returns tiered urgency levels based on continuous work time:
        - 60 min: gentle reminder
        - 90 min: firm reminder
        - 120 min: urgent (health concern)

        Returns:
            Tuple of (should_break, severity)
            severity: 'none', 'gentle', 'firm', 'urgent'
        """
        if not self.active_session or not self.active_session.is_active():
            return (False, 'none')

        elapsed = self.get_elapsed_time()
        if not elapsed:
            return (False, 'none')

        # Tiered break reminders (ADHD hyperfocus protection)
        if elapsed >= timedelta(minutes=120):
            return (True, 'urgent')  # 2+ hours - health risk
        elif elapsed >= timedelta(minutes=90):
            return (True, 'firm')    # 1.5+ hours - strong suggestion
        elif elapsed >= timedelta(minutes=60):
            return (True, 'gentle')  # 1+ hour - gentle nudge

        return (False, 'none')
