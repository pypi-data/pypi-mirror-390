"""Data models for JOURNEL."""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class Project:
    """Represents a project in JOURNEL."""

    id: str
    name: str
    full_name: str = ""
    status: str = "in-progress"  # in-progress, completed, dormant
    tags: List[str] = field(default_factory=list)
    created: date = field(default_factory=date.today)
    last_active: date = field(default_factory=date.today)
    completion: int = 0  # 0-100
    priority: str = "medium"  # low, medium, high
    github: str = ""
    claude_project: str = ""
    next_steps: str = ""
    blockers: str = ""
    notes: str = ""
    learned: str = ""

    @property
    def file_name(self) -> str:
        """Get the filename for this project."""
        return f"{self.id}.md"

    def to_frontmatter(self) -> dict:
        """Convert project to YAML frontmatter dict."""
        return {
            "id": self.id,
            "name": self.name,
            "full_name": self.full_name,
            "status": self.status,
            "tags": self.tags,
            "created": self.created.isoformat() if isinstance(self.created, date) else self.created,
            "last_active": self.last_active.isoformat() if isinstance(self.last_active, date) else self.last_active,
            "completion": self.completion,
            "priority": self.priority,
            "github": self.github,
            "claude_project": self.claude_project,
            "next_steps": self.next_steps,
            "blockers": self.blockers,
        }

    @classmethod
    def from_frontmatter(cls, data: dict, notes: str = "") -> "Project":
        """Create project from YAML frontmatter dict."""
        # Convert date strings to date objects
        if isinstance(data.get("created"), str):
            data["created"] = datetime.fromisoformat(data["created"]).date()
        if isinstance(data.get("last_active"), str):
            data["last_active"] = datetime.fromisoformat(data["last_active"]).date()

        project = cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
        project.notes = notes
        return project

    def days_since_active(self) -> int:
        """Get number of days since last activity."""
        if isinstance(self.last_active, str):
            last_active = datetime.fromisoformat(self.last_active).date()
        else:
            last_active = self.last_active
        return (date.today() - last_active).days


@dataclass
class LogEntry:
    """Represents a log entry."""

    date: date
    project: Optional[str]
    message: str
    hours: Optional[float] = None
    ai_assisted: bool = False
    agent: Optional[str] = None  # e.g., "claude-code", "user"

    def to_markdown(self) -> str:
        """Convert log entry to markdown."""
        # Add AI marker if applicable
        prefix = "[AI] " if self.ai_assisted else ""

        if self.project:
            base = f"- {prefix}**{self.project}**"
            if self.hours:
                base += f" ({self.hours}h)"
            base += f": {self.message}"
            if self.agent and self.ai_assisted:
                base += f" [via {self.agent}]"
            return base
        return f"- {prefix}{self.message}"


@dataclass
class Session:
    """Represents a work session on a project.

    Tracks active work time, pauses, and context for interruption handling.
    Enables time awareness and prevents time blindness.
    Supports AI-assisted work tracking with clear attribution.
    """

    id: str
    project_id: str
    task: str
    start_time: datetime
    end_time: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    pause_duration: timedelta = field(default_factory=lambda: timedelta(0))
    interruptions: List[str] = field(default_factory=list)
    context_snapshot: Dict[str, str] = field(default_factory=dict)
    notes: str = ""
    ai_assisted: bool = False
    agent: Optional[str] = None  # e.g., "claude-code", "user"

    def elapsed_time(self, current_time: Optional[datetime] = None) -> timedelta:
        """Calculate elapsed time excluding pauses.

        Args:
            current_time: Current time (defaults to now)

        Returns:
            Elapsed time as timedelta
        """
        if current_time is None:
            current_time = datetime.now()

        if self.end_time:
            # Completed session
            total_time = self.end_time - self.start_time
        elif self.paused_at:
            # Currently paused
            total_time = self.paused_at - self.start_time
        else:
            # Currently active
            total_time = current_time - self.start_time

        # Subtract pause duration
        return total_time - self.pause_duration

    def is_active(self) -> bool:
        """Check if session is currently active (not paused, not ended)."""
        return self.end_time is None and self.paused_at is None

    def is_paused(self) -> bool:
        """Check if session is currently paused."""
        return self.paused_at is not None and self.end_time is None

    def is_ended(self) -> bool:
        """Check if session has ended."""
        return self.end_time is not None

    def to_dict(self) -> Dict:
        """Convert session to dictionary for YAML serialization."""
        return {
            "id": self.id,
            "project_id": self.project_id,
            "task": self.task,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "pause_duration": self.pause_duration.total_seconds(),
            "interruptions": self.interruptions,
            "context_snapshot": self.context_snapshot,
            "notes": self.notes,
            "ai_assisted": self.ai_assisted,
            "agent": self.agent,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Session":
        """Create session from dictionary (YAML deserialization)."""
        # Convert ISO strings back to datetime
        data = data.copy()
        data["start_time"] = datetime.fromisoformat(data["start_time"])
        if data.get("end_time"):
            data["end_time"] = datetime.fromisoformat(data["end_time"])
        if data.get("paused_at"):
            data["paused_at"] = datetime.fromisoformat(data["paused_at"])
        data["pause_duration"] = timedelta(seconds=data.get("pause_duration", 0))

        # Backward compatibility: add defaults for AI fields if missing
        data.setdefault("ai_assisted", False)
        data.setdefault("agent", None)

        return cls(**data)

    def to_markdown(self) -> str:
        """Convert session to markdown for logging."""
        elapsed = self.elapsed_time()
        hours = elapsed.total_seconds() / 3600

        # Format: ## 2025-11-06 10:15-12:30 (2.3h) - project-name
        start_str = self.start_time.strftime("%H:%M")
        if self.end_time:
            end_str = self.end_time.strftime("%H:%M")
            time_range = f"{start_str}-{end_str}"
        else:
            time_range = f"{start_str}-ongoing"

        # Add AI marker to header if AI-assisted
        ai_prefix = "[AI] " if self.ai_assisted else ""
        header = f"## {ai_prefix}{self.start_time.date()} {time_range} ({hours:.1f}h) - {self.project_id}"

        lines = [header, ""]

        if self.task:
            lines.append(f"**Task:** {self.task}")
            lines.append("")

        # Add agent attribution if AI-assisted
        if self.ai_assisted and self.agent:
            lines.append(f"**Agent:** {self.agent}")
            lines.append("")

        if self.notes:
            lines.append(f"**Notes:**")
            lines.append(self.notes)
            lines.append("")

        if self.interruptions:
            lines.append(f"**Interruptions:** {len(self.interruptions)}")
            for interruption in self.interruptions:
                lines.append(f"  - {interruption}")
            lines.append("")

        if self.pause_duration.total_seconds() > 0:
            pause_min = self.pause_duration.total_seconds() / 60
            lines.append(f"**Breaks:** {pause_min:.0f} minutes")
            lines.append("")

        return "\n".join(lines)
