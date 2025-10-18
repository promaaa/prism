"""
Modern notification system for Prism application.
Provides toast notifications, progress indicators, and user feedback.
"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    pyqtSignal,
)
from PyQt6.QtGui import QPainter, QColor, QPainterPath, QFont


class ToastNotification(QWidget):
    """
    Modern toast notification widget with smooth animations.
    """

    closed = pyqtSignal()

    def __init__(
        self,
        message: str,
        notification_type: str = "info",
        duration: int = 3000,
        parent=None,
    ):
        """
        Initialize toast notification.

        Args:
            message: Notification message to display
            notification_type: Type of notification ("success", "error", "warning", "info")
            duration: Duration in milliseconds before auto-hide
            parent: Parent widget
        """
        super().__init__(parent)
        self.message = message
        self.notification_type = notification_type
        self.duration = duration

        # Set window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._init_ui()
        self._setup_animations()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(12)

        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set icon based on type
        icons = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}
        icon_text = icons.get(self.notification_type, "ℹ")
        self.icon_label.setText(icon_text)
        self.icon_label.setStyleSheet(f"font-size: 18px; font-weight: bold;")

        layout.addWidget(self.icon_label)

        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("SF Pro Display", 13))
        layout.addWidget(self.message_label, 1)

        # Set minimum and maximum size
        self.setMinimumWidth(300)
        self.setMaximumWidth(500)
        self.adjustSize()

    def _setup_animations(self):
        """Setup fade in/out animations."""
        # Opacity effect
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        # Fade in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Fade out animation
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out.finished.connect(self._on_fade_out_finished)

        # Auto-hide timer
        if self.duration > 0:
            QTimer.singleShot(self.duration, self.hide_notification)

    def paintEvent(self, event):
        """Custom paint event for rounded background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define colors based on notification type
        colors = {
            "success": {
                "bg": QColor(16, 185, 129, 230),  # Green
                "text": QColor(255, 255, 255),
            },
            "error": {
                "bg": QColor(239, 68, 68, 230),  # Red
                "text": QColor(255, 255, 255),
            },
            "warning": {
                "bg": QColor(245, 158, 11, 230),  # Orange
                "text": QColor(255, 255, 255),
            },
            "info": {
                "bg": QColor(59, 130, 246, 230),  # Blue
                "text": QColor(255, 255, 255),
            },
        }

        color_scheme = colors.get(self.notification_type, colors["info"])

        # Draw rounded rectangle background
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path, color_scheme["bg"])

        # Set text color
        self.icon_label.setStyleSheet(
            f"color: {color_scheme['text'].name()}; font-size: 18px; font-weight: bold;"
        )
        self.message_label.setStyleSheet(
            f"color: {color_scheme['text'].name()}; background: transparent;"
        )

    def show_notification(self):
        """Show notification with fade-in animation."""
        self.show()
        self.fade_in.start()

    def hide_notification(self):
        """Hide notification with fade-out animation."""
        self.fade_out.start()

    def _on_fade_out_finished(self):
        """Handle fade-out animation completion."""
        self.hide()
        self.closed.emit()


class NotificationManager(QWidget):
    """
    Manages multiple toast notifications in a stack.
    """

    def __init__(self, parent=None):
        """
        Initialize notification manager.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.notifications = []
        self.spacing = 10
        self.margin = 20

    def show_success(self, message: str, duration: int = 3000):
        """
        Show success notification.

        Args:
            message: Success message
            duration: Duration in milliseconds
        """
        self._show_notification(message, "success", duration)

    def show_error(self, message: str, duration: int = 4000):
        """
        Show error notification.

        Args:
            message: Error message
            duration: Duration in milliseconds
        """
        self._show_notification(message, "error", duration)

    def show_warning(self, message: str, duration: int = 3500):
        """
        Show warning notification.

        Args:
            message: Warning message
            duration: Duration in milliseconds
        """
        self._show_notification(message, "warning", duration)

    def show_info(self, message: str, duration: int = 3000):
        """
        Show info notification.

        Args:
            message: Info message
            duration: Duration in milliseconds
        """
        self._show_notification(message, "info", duration)

    def _show_notification(self, message: str, notification_type: str, duration: int):
        """
        Internal method to show notification.

        Args:
            message: Notification message
            notification_type: Type of notification
            duration: Duration in milliseconds
        """
        # Create notification
        notification = ToastNotification(
            message=message,
            notification_type=notification_type,
            duration=duration,
            parent=self.parent(),
        )

        # Connect closed signal
        notification.closed.connect(lambda: self._remove_notification(notification))

        # Add to list
        self.notifications.append(notification)

        # Position notification
        self._position_notifications()

        # Show notification
        notification.show_notification()

    def _remove_notification(self, notification: ToastNotification):
        """
        Remove notification from list.

        Args:
            notification: Notification to remove
        """
        if notification in self.notifications:
            self.notifications.remove(notification)
            notification.deleteLater()
            self._position_notifications()

    def _position_notifications(self):
        """Position all notifications in a stack."""
        if not self.parent():
            return

        parent_rect = self.parent().rect()
        y_offset = self.margin

        for notification in self.notifications:
            # Position at top-right corner
            x = parent_rect.width() - notification.width() - self.margin
            y = y_offset

            notification.move(x, y)
            y_offset += notification.height() + self.spacing


class LoadingOverlay(QWidget):
    """
    Semi-transparent loading overlay with spinner.
    """

    def __init__(self, message: str = "Loading...", parent=None):
        """
        Initialize loading overlay.

        Args:
            message: Loading message to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.message = message

        # Set window flags
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self._init_ui()

        # Hide by default
        self.hide()

    def _init_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container widget for centered content
        container = QWidget()
        container.setObjectName("loading-container")
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)
        container_layout.setContentsMargins(30, 30, 30, 30)

        # Spinner label (using Unicode spinner character)
        self.spinner_label = QLabel("⟳")
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spinner_label.setStyleSheet("""
            font-size: 48px;
            color: #10B981;
            background: transparent;
        """)
        container_layout.addWidget(self.spinner_label)

        # Message label
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("""
            font-size: 14px;
            color: #F5F5F5;
            background: transparent;
            font-weight: 500;
        """)
        container_layout.addWidget(self.message_label)

        # Style container
        container.setStyleSheet("""
            QWidget#loading-container {
                background-color: rgba(26, 26, 26, 200);
                border-radius: 16px;
                border: 1px solid rgba(64, 64, 64, 150);
            }
        """)

        layout.addWidget(container)

        # Setup rotation animation
        self._setup_animation()

    def _setup_animation(self):
        """Setup spinner rotation animation."""
        self.rotation = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._rotate_spinner)

    def _rotate_spinner(self):
        """Rotate spinner character."""
        self.rotation = (self.rotation + 30) % 360
        # Cycle through spinner characters for animation effect
        spinners = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        index = (self.rotation // 30) % len(spinners)
        self.spinner_label.setText(spinners[index])

    def paintEvent(self, event):
        """Paint semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 100))

    def show_overlay(self):
        """Show overlay with animation."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()
        self.timer.start(100)

    def hide_overlay(self):
        """Hide overlay."""
        self.timer.stop()
        self.hide()

    def update_message(self, message: str):
        """
        Update loading message.

        Args:
            message: New message to display
        """
        self.message = message
        self.message_label.setText(message)


class ConfirmDialog(QWidget):
    """
    Modern confirmation dialog with custom styling.
    """

    confirmed = pyqtSignal()
    cancelled = pyqtSignal()

    def __init__(
        self,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        dialog_type: str = "warning",
        parent=None,
    ):
        """
        Initialize confirmation dialog.

        Args:
            title: Dialog title
            message: Dialog message
            confirm_text: Text for confirm button
            cancel_text: Text for cancel button
            dialog_type: Type of dialog ("warning", "danger", "info")
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.dialog_type = dialog_type

        # Set window flags
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._init_ui()
        self.hide()

    def _init_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dialog container
        container = QWidget()
        container.setObjectName("confirm-dialog")
        container.setFixedWidth(400)

        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)

        # Icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icons = {"warning": "⚠️", "danger": "🗑️", "info": "ℹ️"}
        icon_label.setText(icons.get(self.dialog_type, "⚠️"))
        icon_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(icon_label)

        # Title
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #F5F5F5;
            background: transparent;
        """)
        layout.addWidget(title_label)

        # Message
        message_label = QLabel(self.message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            font-size: 14px;
            color: #A0A0A0;
            background: transparent;
        """)
        layout.addWidget(message_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        # Cancel button
        cancel_btn = QPushButton(self.cancel_text)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                color: #F5F5F5;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: #4A4A4A;
            }
        """)
        cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_btn)

        # Confirm button
        confirm_btn = QPushButton(self.confirm_text)
        confirm_btn.setFixedHeight(40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        # Color based on type
        colors = {"warning": "#F59E0B", "danger": "#EF4444", "info": "#10B981"}
        color = colors.get(self.dialog_type, "#10B981")

        confirm_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
        """)
        confirm_btn.clicked.connect(self._on_confirm)
        button_layout.addWidget(confirm_btn)

        layout.addLayout(button_layout)

        # Style container
        container.setStyleSheet("""
            QWidget#confirm-dialog {
                background-color: #2A2A2A;
                border-radius: 16px;
                border: 1px solid #404040;
            }
        """)

        main_layout.addWidget(container)

    def paintEvent(self, event):
        """Paint semi-transparent background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))

    def show_dialog(self):
        """Show dialog."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()

    def _on_confirm(self):
        """Handle confirm button click."""
        self.confirmed.emit()
        self.hide()

    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled.emit()
        self.hide()
