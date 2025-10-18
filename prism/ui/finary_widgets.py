"""
Finary-style UI components for Prism application.
Precisely matched to Finary's dark mode design (Oct 2025).
Reusable widgets with exact color palette and styling from Finary screenshots.
"""

from typing import Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor


class FinaryAssetCard(QFrame):
    """
    Finary-style asset card (like "Trade Republic" card in screenshots).

    Layout (from Finary images):
    ┌─────────────────────────────┐
    │ [icon] Trade Republic       │
    │ €62,230                     │
    │ +9.55% [mini line chart]    │
    └─────────────────────────────┘

    Background: #2D2D2D
    Border: #404040
    Rounded: 12px
    Hover: border -> #10B981
    """

    clicked = pyqtSignal()

    def __init__(
        self,
        name: str,
        value: str,
        performance: Optional[str] = None,
        icon: str = "💼",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize Finary asset card.

        Args:
            name: Asset name (e.g., "Trade Republic", "Bitcoin")
            value: Current value (e.g., "€62,230")
            performance: Performance string (e.g., "+9.55%")
            icon: Emoji icon for the asset
            parent: Parent widget
        """
        super().__init__(parent)
        self.setProperty("class", "asset-card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._init_ui(name, value, performance, icon)

    def _init_ui(self, name: str, value: str, performance: Optional[str], icon: str):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header: Icon + Name
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(24)
        icon_label.setFont(icon_font)
        header.addWidget(icon_label)

        name_label = QLabel(name)
        name_label.setProperty("class", "card-asset-name")
        header.addWidget(name_label)
        header.addStretch()

        layout.addLayout(header)

        # Value (large, bold, white)
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "card-value")
        layout.addWidget(self.value_label)

        # Performance (green if positive, red if negative)
        if performance:
            self.performance_label = QLabel(performance)
            is_positive = performance.startswith("+") or not performance.startswith("-")
            self.performance_label.setProperty(
                "class", "positive" if is_positive else "negative"
            )
            layout.addWidget(self.performance_label)

        layout.addStretch()

    def update_value(self, value: str, performance: Optional[str] = None):
        """Update the card's value and performance."""
        self.value_label.setText(value)
        if performance and hasattr(self, "performance_label"):
            self.performance_label.setText(performance)
            is_positive = performance.startswith("+")
            self.performance_label.setProperty(
                "class", "positive" if is_positive else "negative"
            )
            self.performance_label.style().unpolish(self.performance_label)
            self.performance_label.style().polish(self.performance_label)

    def mousePressEvent(self, event):
        """Handle click events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class FinarySummaryCard(QFrame):
    """
    Finary-style summary card for key metrics.

    Layout:
    ┌─────────────────┐
    │ TOTAL BALANCE   │  <- uppercase gray text
    │ €423,817        │  <- large bold white
    │ +9.55%          │  <- green/red indicator
    └─────────────────┘

    Matches Finary's "Synthèse" section cards
    """

    def __init__(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        positive: Optional[bool] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize summary card.

        Args:
            title: Card title (e.g., "TOTAL BALANCE")
            value: Main value (e.g., "€423,817")
            subtitle: Optional subtitle (e.g., "+9.55%")
            positive: Color indicator (True=green, False=red, None=white)
            parent: Parent widget
        """
        super().__init__(parent)
        self.setProperty("class", "summary-card")
        self._init_ui(title, value, subtitle, positive)

    def _init_ui(
        self, title: str, value: str, subtitle: Optional[str], positive: Optional[bool]
    ):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Title (uppercase, small, gray)
        title_label = QLabel(title.upper())
        title_label.setProperty("class", "card-title")
        layout.addWidget(title_label)

        # Value (large, bold)
        self.value_label = QLabel(value)
        if positive is True:
            self.value_label.setProperty("class", "card-value positive")
        elif positive is False:
            self.value_label.setProperty("class", "card-value negative")
        else:
            self.value_label.setProperty("class", "card-value")
        layout.addWidget(self.value_label)

        # Subtitle/performance
        if subtitle:
            self.subtitle_label = QLabel(subtitle)
            if positive is True:
                self.subtitle_label.setProperty("class", "positive")
            elif positive is False:
                self.subtitle_label.setProperty("class", "negative")
            else:
                self.subtitle_label.setProperty("class", "card-subtitle")
            layout.addWidget(self.subtitle_label)

        layout.addStretch()

    def update_value(
        self,
        value: str,
        subtitle: Optional[str] = None,
        positive: Optional[bool] = None,
    ):
        """Update card value."""
        self.value_label.setText(value)
        if positive is True:
            self.value_label.setProperty("class", "card-value positive")
        elif positive is False:
            self.value_label.setProperty("class", "card-value negative")
        else:
            self.value_label.setProperty("class", "card-value")

        self.value_label.style().unpolish(self.value_label)
        self.value_label.style().polish(self.value_label)

        if subtitle and hasattr(self, "subtitle_label"):
            self.subtitle_label.setText(subtitle)


class FinaryContentCard(QFrame):
    """
    Finary-style content card for tables and lists.

    Background: #2D2D2D
    Rounded corners: 12px
    Contains table or list data
    """

    def __init__(
        self,
        title: Optional[str] = None,
        action_text: Optional[str] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize content card.

        Args:
            title: Card title
            action_text: Action button text (e.g., "View All")
            parent: Parent widget
        """
        super().__init__(parent)
        self.setProperty("class", "card")
        self._init_ui(title, action_text)

    def _init_ui(self, title: Optional[str], action_text: Optional[str]):
        """Initialize UI."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header with title and action button
        if title or action_text:
            header = QWidget()
            header.setStyleSheet("background-color: transparent;")
            header_layout = QHBoxLayout(header)
            header_layout.setContentsMargins(24, 20, 24, 16)
            header_layout.setSpacing(16)

            if title:
                title_label = QLabel(title)
                title_label.setProperty("class", "section-title")
                header_layout.addWidget(title_label)

            header_layout.addStretch()

            if action_text:
                self.action_button = QPushButton(action_text)
                self.action_button.setProperty("class", "secondary-button")
                header_layout.addWidget(self.action_button)
            else:
                self.action_button = None

            self.main_layout.addWidget(header)

        self.content_widget = None

    def set_content(self, widget: QWidget):
        """Set the main content widget."""
        if self.content_widget:
            self.main_layout.removeWidget(self.content_widget)
            self.content_widget.deleteLater()

        self.content_widget = widget
        self.main_layout.addWidget(widget)

    def get_action_button(self) -> Optional[QPushButton]:
        """Get the action button."""
        return self.action_button


class FinaryMetricRow(QWidget):
    """
    Horizontal row of summary cards (Finary's top metrics row).

    Example from Finary:
    [VALEUR TOTALE] [PERFORMANCE] [RÉPARTITION]
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize metric row."""
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(16)
        self.cards = []

    def add_card(
        self,
        title: str,
        value: str,
        subtitle: Optional[str] = None,
        positive: Optional[bool] = None,
    ) -> FinarySummaryCard:
        """Add a summary card to the row."""
        card = FinarySummaryCard(title, value, subtitle, positive)
        self.layout.addWidget(card)
        self.cards.append(card)
        return card

    def clear_cards(self):
        """Remove all cards."""
        for card in self.cards:
            self.layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()


class FinaryEmptyState(QWidget):
    """
    Empty state widget for when there's no data.

    Finary style: centered icon, message, and CTA button
    """

    action_clicked = pyqtSignal()

    def __init__(
        self,
        title: str,
        subtitle: Optional[str] = None,
        action_text: Optional[str] = None,
        icon: str = "📊",
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize empty state.

        Args:
            title: Main message
            subtitle: Secondary message
            action_text: Action button text
            icon: Emoji icon
            parent: Parent widget
        """
        super().__init__(parent)
        self._init_ui(title, subtitle, action_text, icon)

    def _init_ui(
        self, title: str, subtitle: Optional[str], action_text: Optional[str], icon: str
    ):
        """Initialize UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 80, 60, 80)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_font = QFont()
        icon_font.setPointSize(56)
        icon_label.setFont(icon_font)
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(title)
        title_label.setProperty("class", "section-title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        # Subtitle
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setProperty("class", "section-subtitle")
            subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            subtitle_label.setWordWrap(True)
            layout.addWidget(subtitle_label)

        # Action button
        if action_text:
            self.action_button = QPushButton(action_text)
            self.action_button.clicked.connect(self.action_clicked.emit)
            layout.addWidget(self.action_button, alignment=Qt.AlignmentFlag.AlignCenter)


class FinaryAddButton(QPushButton):
    """
    Finary's signature green "+" button.

    Circular, green (#10B981), with "+" sign
    Appears in bottom-right corner of screens
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """Initialize add button."""
        super().__init__("+", parent)
        self.setProperty("class", "add-button")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class FinarySearchBar(QWidget):
    """
    Finary-style search bar for header.

    Background: #2D2D2D
    Placeholder: "Rechercher comptes"
    Icon: magnifying glass
    """

    textChanged = pyqtSignal(str)

    def __init__(
        self, placeholder: str = "Rechercher...", parent: Optional[QWidget] = None
    ):
        """Initialize search bar."""
        super().__init__(parent)
        self._init_ui(placeholder)

    def _init_ui(self, placeholder: str):
        """Initialize UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        # Search icon
        icon = QLabel("🔍")
        icon_font = QFont()
        icon_font.setPointSize(14)
        icon.setFont(icon_font)
        layout.addWidget(icon)

        # Search input
        from PyQt6.QtWidgets import QLineEdit

        self.search_input = QLineEdit()
        self.search_input.setProperty("class", "search-bar")
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.textChanged.emit)
        layout.addWidget(self.search_input)


# ============================================================
# HELPER FUNCTIONS - Finary-style formatting
# ============================================================


def format_currency(amount: float, currency: str = "€", compact: bool = False) -> str:
    """
    Format currency like Finary.

    Examples:
        format_currency(423817) -> "€423,817"
        format_currency(62230.50) -> "€62,230.50"
        format_currency(1500000, compact=True) -> "€1.5M"
    """
    if compact:
        return format_compact_currency(amount, currency)

    # Standard formatting
    formatted = f"{abs(amount):,.2f}".rstrip("0").rstrip(".")
    sign = "-" if amount < 0 else ""
    return f"{sign}{currency}{formatted}"


def format_compact_currency(amount: float, currency: str = "€") -> str:
    """
    Format large numbers compactly (Finary style).

    Examples:
        1500000 -> "€1.5M"
        12500 -> "€12.5K"
        950000000 -> "€950M"
    """
    abs_amount = abs(amount)
    sign = "-" if amount < 0 else ""

    if abs_amount >= 1_000_000_000:
        value = abs_amount / 1_000_000_000
        return f"{sign}{currency}{value:.1f}B"
    elif abs_amount >= 1_000_000:
        value = abs_amount / 1_000_000
        return f"{sign}{currency}{value:.1f}M"
    elif abs_amount >= 1_000:
        value = abs_amount / 1_000
        return f"{sign}{currency}{value:.1f}K"
    else:
        return f"{sign}{currency}{abs_amount:.0f}"


def format_percentage(value: float, include_sign: bool = True) -> str:
    """
    Format percentage like Finary.

    Examples:
        format_percentage(0.0955) -> "+9.55%"
        format_percentage(-0.0234) -> "-2.34%"
        format_percentage(0.15, include_sign=False) -> "15.0%"
    """
    percentage = value * 100
    if include_sign and percentage > 0:
        return f"+{percentage:.2f}%"
    return f"{percentage:.2f}%"


def get_performance_class(value: float) -> str:
    """
    Get CSS class for performance indicator.

    Returns "positive" for positive values, "negative" for negative
    """
    return "positive" if value >= 0 else "negative"


def create_finary_card_grid(cards: list, columns: int = 3) -> QWidget:
    """
    Create a grid layout of cards (Finary's asset grid).

    Args:
        cards: List of QWidget cards
        columns: Number of columns

    Returns:
        QWidget with grid layout
    """
    from PyQt6.QtWidgets import QGridLayout

    container = QWidget()
    grid = QGridLayout(container)
    grid.setSpacing(16)
    grid.setContentsMargins(0, 0, 0, 0)

    for i, card in enumerate(cards):
        row = i // columns
        col = i % columns
        grid.addWidget(card, row, col)

    return container


# ============================================================
# FINARY COLOR CONSTANTS (from screenshots)
# ============================================================

FINARY_COLORS = {
    "background": "#0A0A0A",
    "background_secondary": "#121212",
    "sidebar": "#1A1A1A",
    "card": "#2D2D2D",
    "border": "#404040",
    "text_primary": "#FFFFFF",
    "text_secondary": "#A0A0A0",
    "accent_green": "#10B981",
    "accent_blue": "#3B82F6",
    "negative_red": "#EF4444",
    "chart_pink": "#EC4899",
    "chart_purple": "#A78BFA",
    "chart_blue": "#60A5FA",
    "chart_orange": "#F59E0B",
}


def get_finary_color(name: str) -> str:
    """Get a Finary color by name."""
    return FINARY_COLORS.get(name, FINARY_COLORS["accent_green"])
