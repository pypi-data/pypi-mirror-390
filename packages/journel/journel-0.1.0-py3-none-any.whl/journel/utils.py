"""Utility functions for JOURNEL."""

import re
from datetime import date
from pathlib import Path
from typing import Optional


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content.

    Returns:
        Tuple of (frontmatter_dict, body_content)
    """
    import yaml

    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1]) or {}
        body = parts[2].strip()
        return frontmatter, body
    except yaml.YAMLError:
        return {}, content


def format_frontmatter(data: dict, body: str) -> str:
    """Format frontmatter and body into markdown content."""
    import yaml

    frontmatter = yaml.dump(data, default_flow_style=False, sort_keys=False)
    return f"---\n{frontmatter}---\n\n{body}"


def get_month_file(target_date: Optional[date] = None) -> str:
    """Get the log filename for a given date."""
    if target_date is None:
        target_date = date.today()
    return f"{target_date.year}-{target_date.month:02d}.md"


def format_date_relative(target_date: date) -> str:
    """Format a date as a relative string."""
    delta = (date.today() - target_date).days

    if delta == 0:
        return "today"
    elif delta == 1:
        return "yesterday"
    elif delta < 7:
        return f"{delta} days ago"
    elif delta < 14:
        return "1 week ago"
    elif delta < 30:
        weeks = delta // 7
        return f"{weeks} weeks ago"
    elif delta < 60:
        return "1 month ago"
    else:
        months = delta // 30
        return f"{months} months ago"


def ensure_dir(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def detect_git_repo() -> Optional[str]:
    """Detect if current directory is a git repo and return remote URL."""
    try:
        import git
        repo = git.Repo(Path.cwd(), search_parent_directories=True)
        if repo.remotes:
            # Try to get origin URL
            origin = repo.remotes.origin if 'origin' in [r.name for r in repo.remotes] else repo.remotes[0]
            url = origin.url
            # Convert git@github.com:user/repo.git to https://github.com/user/repo
            if url.startswith('git@'):
                url = url.replace(':', '/').replace('git@', 'https://')
            if url.endswith('.git'):
                url = url[:-4]
            return url
    except:
        pass
    return None


def parse_time_from_message(message: str) -> tuple[str, Optional[float]]:
    """Parse time duration from message.

    Supports formats like:
    - "Fixed bug (2h)" -> ("Fixed bug", 2.0)
    - "worked 3h" -> ("worked", 3.0)
    - "Implemented feature (1.5h)" -> ("Implemented feature", 1.5)
    - "Did stuff - 2h" -> ("Did stuff", 2.0)

    Returns:
        Tuple of (cleaned_message, hours)
    """
    import re

    # Pattern for time in parentheses: (2h), (1.5h), etc.
    pattern_parens = r'\s*\((\d+\.?\d*)\s*h(?:ours?)?\)\s*'
    match = re.search(pattern_parens, message, re.IGNORECASE)
    if match:
        hours = float(match.group(1))
        cleaned = re.sub(pattern_parens, '', message, flags=re.IGNORECASE).strip()
        return cleaned, hours

    # Pattern for time with dash: - 2h, - 1.5h
    pattern_dash = r'\s*[-–]\s*(\d+\.?\d*)\s*h(?:ours?)?\s*$'
    match = re.search(pattern_dash, message, re.IGNORECASE)
    if match:
        hours = float(match.group(1))
        cleaned = re.sub(pattern_dash, '', message, flags=re.IGNORECASE).strip()
        return cleaned, hours

    # Pattern for "worked Xh" at end
    pattern_worked = r'\s*worked\s+(\d+\.?\d*)\s*h(?:ours?)?\s*$'
    match = re.search(pattern_worked, message, re.IGNORECASE)
    if match:
        hours = float(match.group(1))
        cleaned = re.sub(pattern_worked, '', message, flags=re.IGNORECASE).strip()
        # If message is now empty, use "worked"
        if not cleaned:
            cleaned = "worked"
        return cleaned, hours

    return message, None
