"""Configuration management for JOURNEL."""

import os
from pathlib import Path
from typing import Any, Dict

import yaml


DEFAULT_CONFIG = {
    "editor": os.environ.get("EDITOR", "notepad"),
    "default_view": "status",
    "max_active_projects": 5,
    "completion_celebration": True,
    "auto_git_commit": True,
    "gentle_nudges": True,
    "show_command_hints": True,
    "dormant_days": 14,
    "use_emojis": True,
    # AI Integration settings
    "ai": {
        "enabled": True,  # Allow AI commands
        "default_agent": "claude-code",  # Default AI agent name
        "show_agent_attribution": True,  # Show agent name in logs/sessions
        "learning_prompts": True,  # Use learning-focused prompts in ai-stop
        "color_scheme": "magenta",  # Visual color for AI entries (magenta/cyan/yellow)
    },
}


class Config:
    """Manages JOURNEL configuration."""

    def __init__(self, journel_dir: Path = None):
        """Initialize config manager."""
        if journel_dir is None:
            journel_dir = Path.home() / ".journel"
        self.journel_dir = Path(journel_dir)
        self.config_file = self.journel_dir / "config.yaml"
        self._config = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}
                self._config.update(user_config)

    def save(self) -> None:
        """Save configuration to file."""
        self.journel_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False)

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    @property
    def projects_dir(self) -> Path:
        """Get projects directory."""
        return self.journel_dir / "projects"

    @property
    def logs_dir(self) -> Path:
        """Get logs directory."""
        return self.journel_dir / "logs"

    @property
    def completed_dir(self) -> Path:
        """Get completed projects directory."""
        return self.journel_dir / "completed"

    @property
    def archived_dir(self) -> Path:
        """Get archived projects directory."""
        return self.journel_dir / "archived"

    @property
    def meta_dir(self) -> Path:
        """Get meta directory."""
        return self.journel_dir / ".meta"
