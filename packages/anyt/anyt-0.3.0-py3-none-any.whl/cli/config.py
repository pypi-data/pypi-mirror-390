"""Configuration management for AnyTask CLI."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class WorkspaceConfig(BaseModel):
    """Local workspace configuration stored in anyt.json.

    Note: Authentication is handled via ANYT_API_KEY environment variable only.
    No credentials are stored in workspace config.
    """

    workspace_id: int
    name: str
    api_url: str
    last_sync: Optional[str] = None
    current_project_id: Optional[int] = None
    workspace_identifier: Optional[str] = None

    @classmethod
    def get_config_path(cls, directory: Optional[Path] = None) -> Path:
        """Get the path to the workspace config file."""
        if directory is None:
            directory = Path.cwd()

        return directory / ".anyt" / "anyt.json"

    @classmethod
    def load(cls, directory: Optional[Path] = None) -> Optional["WorkspaceConfig"]:
        """Load workspace configuration from file."""
        config_path = cls.get_config_path(directory)

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except json.JSONDecodeError as e:
            # Invalid JSON - log and return None
            import sys

            print(f"Warning: Invalid JSON in {config_path}: {e}", file=sys.stderr)
            return None
        except Exception as e:
            # Validation error or other issue - log for debugging
            import sys

            print(
                f"Warning: Failed to load workspace config from {config_path}: {e}",
                file=sys.stderr,
            )
            return None

    def save(self, directory: Optional[Path] = None) -> None:
        """Save workspace configuration to file."""
        config_path = self.get_config_path(directory)

        # Ensure .anyt directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save workspace config: {e}")


def get_workspace_config_or_none(
    directory: Optional[Path] = None,
) -> Optional[WorkspaceConfig]:
    """Safely load workspace config without raising exceptions.

    Args:
        directory: Directory to search for .anyt/anyt.json. Defaults to current directory.

    Returns:
        WorkspaceConfig if found and valid, None otherwise.
    """
    return WorkspaceConfig.load(directory)


def get_effective_api_config() -> dict[str, str]:
    """Get effective API configuration from environment variables and workspace config.

    Priority order for API URL:
    1. ANYT_API_URL environment variable
    2. .anyt/anyt.json (workspace config)
    3. Default: "https://api.anyt.dev"

    Priority order for API key:
    1. ANYT_API_KEY environment variable (REQUIRED)

    Returns:
        Dictionary with 'api_url' and 'api_key' keys.

    Raises:
        RuntimeError: If ANYT_API_KEY environment variable is not set.
    """
    # API URL priority: env var > workspace config > default
    api_url = os.getenv("ANYT_API_URL")

    if not api_url:
        # Try to load from workspace config
        workspace_config = get_workspace_config_or_none()
        if workspace_config:
            api_url = workspace_config.api_url
        else:
            # Fall back to default
            api_url = "https://api.anyt.dev"

    # API Key: MUST come from environment variable
    api_key = os.getenv("ANYT_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANYT_API_KEY environment variable is required. "
            "Please set it to your agent API key."
        )

    return {
        "api_url": api_url,
        "api_key": api_key,
    }


class ActiveTaskConfig(BaseModel):
    """Active task configuration stored in .anyt/active_task.json."""

    identifier: str
    title: str
    picked_at: str
    workspace_id: int
    project_id: int

    @classmethod
    def get_config_path(cls, directory: Optional[Path] = None) -> Path:
        """Get the path to the active task config file."""
        if directory is None:
            directory = Path.cwd()

        anyt_dir = directory / ".anyt"
        anyt_dir.mkdir(exist_ok=True)
        return anyt_dir / "active_task.json"

    @classmethod
    def load(cls, directory: Optional[Path] = None) -> Optional["ActiveTaskConfig"]:
        """Load active task configuration from file."""
        config_path = cls.get_config_path(directory)

        if not config_path.exists():
            return None

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception:
            return None

    def save(self, directory: Optional[Path] = None) -> None:
        """Save active task configuration to file."""
        config_path = self.get_config_path(directory)

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save active task config: {e}")

    @classmethod
    def clear(cls, directory: Optional[Path] = None) -> None:
        """Clear the active task by removing the config file."""
        config_path = cls.get_config_path(directory)
        if config_path.exists():
            config_path.unlink()
