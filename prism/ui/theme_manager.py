"""
Theme manager for Prism application.
Handles light and dark themes for Plotly charts, inspired by Finary.
"""

import plotly.graph_objects as go
import plotly.io as pio
from typing import Dict, Any

# --- Finary-inspired Color Palettes ---

FINARY_DARK_COLORS: Dict[str, Any] = {
    "background": "#1A1A1A",
    "paper_background": "#242424",
    "text": "#FFFFFF",
    "grid": "#3A3A3A",
    "primary": "#007AFF",  # Bright Blue
    "accent": "#34C759",  # Bright Green
    "danger": "#FF3B30",  # Bright Red
    "palette": [
        "#007AFF",
        "#34C759",
        "#FF9500",
        "#AF52DE",
        "#5AC8FA",
        "#FF2D55",
        "#FFCC00",
        "#8E8E93",
    ],
}

FINARY_LIGHT_COLORS: Dict[str, Any] = {
    "background": "#FFFFFF",
    "paper_background": "#F2F2F7",
    "text": "#000000",
    "grid": "#E5E5EA",
    "primary": "#007AFF",
    "accent": "#34C759",
    "danger": "#FF3B30",
    "palette": [
        "#007AFF",
        "#34C759",
        "#FF9500",
        "#AF52DE",
        "#5AC8FA",
        "#FF2D55",
        "#FFCC00",
        "#8E8E93",
    ],
}

FINARY_DARK_STYLESHEET = """
/* Dark Theme */
QWidget {
    background-color: #1A1A1A;
    color: #FFFFFF;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

QMainWindow {
    background-color: #1A1A1A;
}

/* Other widgets */

"""

FINARY_LIGHT_STYLESHEET = """
/* Light Theme */
QWidget {
    background-color: #FFFFFF;
    color: #000000;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

QMainWindow {
    background-color: #FFFFFF;
}

/* Other widgets */
"""


class ThemeManager:
    """Manages and applies Plotly themes for the application."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._register_themes()
        self.current_theme = "finary_dark"  # Default theme

    def _create_template(self, colors: Dict[str, Any]) -> go.layout.Template:
        """Creates a Plotly template from a color dictionary."""
        template = go.layout.Template()
        template.layout = go.Layout(
            font=dict(
                color=colors["text"],
                family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif',
            ),
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["paper_background"],
            title_font=dict(size=20, color=colors["text"]),
            xaxis=dict(
                gridcolor=colors["grid"],
                linecolor=colors["grid"],
                zerolinecolor=colors["grid"],
                tickfont=dict(color=colors["text"]),
                title_font=dict(color=colors["text"]),
            ),
            yaxis=dict(
                gridcolor=colors["grid"],
                linecolor=colors["grid"],
                zerolinecolor=colors["grid"],
                tickfont=dict(color=colors["text"]),
                title_font=dict(color=colors["text"]),
            ),
            legend=dict(font=dict(color=colors["text"])),
            colorway=colors["palette"],
        )
        return template

    def _register_themes(self):
        """Registers the Finary-inspired light and dark themes."""
        pio.templates["finary_dark"] = self._create_template(FINARY_DARK_COLORS)
        pio.templates["finary_light"] = self._create_template(FINARY_LIGHT_COLORS)
        print("Finary light and dark themes registered with Plotly.")

    def set_theme(self, theme_name: str):
        """Sets the default Plotly template for all new charts."""
        if theme_name in ["finary_dark", "finary_light"]:
            pio.templates.default = theme_name
            self.current_theme = theme_name
            print(f"Prism theme set to: {theme_name}")
        else:
            print(f"Warning: Theme '{theme_name}' not recognized. Using default.")

    def get_stylesheet(self) -> str:
        """Returns the stylesheet for the current theme."""
        if self.current_theme == "finary_dark":
            return FINARY_DARK_STYLESHEET
        else:
            return FINARY_LIGHT_STYLESHEET


# --- Global Instance ---

theme_manager = ThemeManager()
