"""Global settings for visualflow."""

import os

from dotenv import load_dotenv

from visualflow.models import (
    EdgeTheme,
    DEFAULT_THEME,
    LIGHT_THEME,
    ROUNDED_THEME,
    HEAVY_THEME,
)

# Map of theme names to theme instances
THEME_MAP: dict[str, EdgeTheme] = {
    "default": DEFAULT_THEME,
    "light": LIGHT_THEME,
    "rounded": ROUNDED_THEME,
    "heavy": HEAVY_THEME,
}


def _load_theme_from_env() -> EdgeTheme:
    """Load theme from VISUALFLOW_THEME environment variable.

    Loads .env file from current working directory or parent directories.

    Returns:
        Theme instance, or DEFAULT_THEME if not set or invalid.
    """
    load_dotenv()
    theme_name = os.environ.get("VISUALFLOW_THEME", "").lower().strip()
    if not theme_name:
        return DEFAULT_THEME
    return THEME_MAP.get(theme_name, DEFAULT_THEME)


class Settings:
    """Global configuration for visualflow.

    Theme is loaded from VISUALFLOW_THEME environment variable if set.
    Can also be set in .env file (with python-dotenv).

    Environment variable values: default, light, rounded, heavy

    Usage:
        # In .env file:
        VISUALFLOW_THEME=rounded

        # Or set programmatically:
        from visualflow import settings, ROUNDED_THEME
        settings.theme = ROUNDED_THEME

        # All render_dag calls will now use ROUNDED_THEME by default
        render_dag(dag)  # Uses global theme
        render_dag(dag, theme=HEAVY_THEME)  # Overrides with HEAVY_THEME
    """

    def __init__(self) -> None:
        self._theme: EdgeTheme = _load_theme_from_env()

    @property
    def theme(self) -> EdgeTheme:
        """Get the global theme."""
        return self._theme

    @theme.setter
    def theme(self, value: EdgeTheme) -> None:
        """Set the global theme."""
        self._theme = value

    def reset(self) -> None:
        """Reset all settings to defaults."""
        self._theme = DEFAULT_THEME


# Global settings instance
settings = Settings()
