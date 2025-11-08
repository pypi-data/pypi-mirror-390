"""AI configuration management for AnyTask CLI."""

import json
import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class AIConfig(BaseModel):
    """AI provider configuration."""

    provider: str = "anthropic"
    model: str = "claude-haiku-4-5-20251001"
    max_tokens: int = 4096
    temperature: float = 0.0
    cache_enabled: bool = True
    api_key: Optional[str] = None  # Optional override for API key

    @classmethod
    def get_config_path(cls) -> Path:
        """Get the path to the AI config file."""
        # Use ANYT_CONFIG_DIR if set, otherwise use XDG_CONFIG_HOME or ~/.config
        config_dir_override = os.getenv("ANYT_CONFIG_DIR")
        if config_dir_override:
            config_dir = Path(config_dir_override)
        else:
            config_home = os.getenv("XDG_CONFIG_HOME")
            if config_home:
                config_dir = Path(config_home) / "anyt"
            else:
                config_dir = Path.home() / ".config" / "anyt"

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "ai.json"

    @classmethod
    def load(cls) -> "AIConfig":
        """Load AI configuration from file.

        Returns:
            AIConfig instance with loaded or default configuration.
        """
        config_path = cls.get_config_path()

        if not config_path.exists():
            # Create default config
            config = cls()
            config.save()
            return config

        try:
            with open(config_path, "r") as f:
                data = json.load(f)
                return cls(**data)
        except Exception as e:
            raise RuntimeError(f"Failed to load AI config from {config_path}: {e}")

    def save(self) -> None:
        """Save AI configuration to file."""
        config_path = self.get_config_path()

        try:
            with open(config_path, "w") as f:
                json.dump(self.model_dump(), f, indent=2)
        except Exception as e:
            raise RuntimeError(f"Failed to save AI config to {config_path}: {e}")

    def update(
        self,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        cache_enabled: Optional[bool] = None,
        provider: Optional[str] = None,
    ) -> None:
        """Update AI configuration and save.

        Args:
            model: Model name to use
            max_tokens: Maximum tokens for AI responses
            temperature: Temperature for AI generation (0.0-1.0)
            cache_enabled: Whether to enable prompt caching
            provider: AI provider (anthropic, openai)
        """
        if model is not None:
            self.model = model
        if max_tokens is not None:
            self.max_tokens = max_tokens
        if temperature is not None:
            self.temperature = temperature
        if cache_enabled is not None:
            self.cache_enabled = cache_enabled
        if provider is not None:
            self.provider = provider
        self.save()

    def get_api_key(self) -> Optional[str]:
        """Get the API key for the current provider.

        Returns API key from config or environment variable.
        Returns None if not found.
        """
        # Check config override first
        if self.api_key:
            return self.api_key

        # Check environment variables
        if self.provider == "anthropic":
            return os.getenv("ANTHROPIC_API_KEY")
        elif self.provider == "openai":
            return os.getenv("OPENAI_API_KEY")

        return None
