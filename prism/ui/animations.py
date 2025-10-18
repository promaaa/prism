"""
Animation and visual effects system for Prism application.
Provides smooth transitions, hover effects, and interactive animations.
"""

from PyQt6.QtWidgets import QWidget, QGraphicsOpacityEffect, QGraphicsDropShadowEffect
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QSequentialAnimationGroup,
    QAbstractAnimation,
    QPoint,
    QRect,
    pyqtProperty,
)
from PyQt6.QtGui import QColor


class AnimationHelper:
    """
    Helper class for creating smooth animations throughout the application.
    """

    @staticmethod
    def fade_in(widget: QWidget, duration: int = 300, start_value: float = 0.0):
        """
        Create fade-in animation for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_value: Starting opacity value (0.0 to 1.0)

        Returns:
            QPropertyAnimation: The fade-in animation
        """
        if not hasattr(widget, "_opacity_effect"):
            widget._opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(widget._opacity_effect)

        animation = QPropertyAnimation(widget._opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(start_value)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        return animation

    @staticmethod
    def fade_out(widget: QWidget, duration: int = 300, end_value: float = 0.0):
        """
        Create fade-out animation for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            end_value: Ending opacity value (0.0 to 1.0)

        Returns:
            QPropertyAnimation: The fade-out animation
        """
        if not hasattr(widget, "_opacity_effect"):
            widget._opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(widget._opacity_effect)

        animation = QPropertyAnimation(widget._opacity_effect, b"opacity")
        animation.setDuration(duration)
        animation.setStartValue(1.0)
        animation.setEndValue(end_value)
        animation.setEasingCurve(QEasingCurve.Type.InCubic)
        return animation

    @staticmethod
    def slide_in(
        widget: QWidget,
        direction: str = "bottom",
        duration: int = 400,
        distance: int = 50,
    ):
        """
        Create slide-in animation for widget.

        Args:
            widget: Widget to animate
            direction: Direction to slide from ("top", "bottom", "left", "right")
            duration: Animation duration in milliseconds
            distance: Distance to slide in pixels

        Returns:
            QPropertyAnimation: The slide-in animation
        """
        current_pos = widget.pos()

        if direction == "bottom":
            start_pos = QPoint(current_pos.x(), current_pos.y() + distance)
        elif direction == "top":
            start_pos = QPoint(current_pos.x(), current_pos.y() - distance)
        elif direction == "left":
            start_pos = QPoint(current_pos.x() - distance, current_pos.y())
        elif direction == "right":
            start_pos = QPoint(current_pos.x() + distance, current_pos.y())
        else:
            start_pos = current_pos

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        return animation

    @staticmethod
    def scale_in(widget: QWidget, duration: int = 300, start_scale: float = 0.8):
        """
        Create scale-in animation for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            start_scale: Starting scale value (0.0 to 1.0)

        Returns:
            QParallelAnimationGroup: Combined scale and fade animation
        """
        current_geometry = widget.geometry()
        scaled_width = int(current_geometry.width() * start_scale)
        scaled_height = int(current_geometry.height() * start_scale)
        x_offset = (current_geometry.width() - scaled_width) // 2
        y_offset = (current_geometry.height() - scaled_height) // 2

        start_geometry = QRect(
            current_geometry.x() + x_offset,
            current_geometry.y() + y_offset,
            scaled_width,
            scaled_height,
        )

        # Geometry animation
        geometry_anim = QPropertyAnimation(widget, b"geometry")
        geometry_anim.setDuration(duration)
        geometry_anim.setStartValue(start_geometry)
        geometry_anim.setEndValue(current_geometry)
        geometry_anim.setEasingCurve(QEasingCurve.Type.OutBack)

        # Opacity animation
        opacity_anim = AnimationHelper.fade_in(widget, duration, 0.0)

        # Combine animations
        group = QParallelAnimationGroup()
        group.addAnimation(geometry_anim)
        group.addAnimation(opacity_anim)
        return group

    @staticmethod
    def bounce_in(widget: QWidget, duration: int = 600):
        """
        Create bounce-in animation for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds

        Returns:
            QPropertyAnimation: The bounce animation
        """
        current_pos = widget.pos()
        start_pos = QPoint(current_pos.x(), current_pos.y() - 100)

        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(duration)
        animation.setStartValue(start_pos)
        animation.setEndValue(current_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        return animation

    @staticmethod
    def shake(widget: QWidget, duration: int = 500, intensity: int = 10):
        """
        Create shake animation for widget (useful for errors).

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            intensity: Shake intensity in pixels

        Returns:
            QSequentialAnimationGroup: Shake animation sequence
        """
        original_pos = widget.pos()

        # Create shake sequence
        group = QSequentialAnimationGroup()

        for i in range(4):
            # Shake left
            anim_left = QPropertyAnimation(widget, b"pos")
            anim_left.setDuration(duration // 8)
            anim_left.setEndValue(
                QPoint(original_pos.x() - intensity, original_pos.y())
            )
            group.addAnimation(anim_left)

            # Shake right
            anim_right = QPropertyAnimation(widget, b"pos")
            anim_right.setDuration(duration // 8)
            anim_right.setEndValue(
                QPoint(original_pos.x() + intensity, original_pos.y())
            )
            group.addAnimation(anim_right)

        # Return to original position
        anim_center = QPropertyAnimation(widget, b"pos")
        anim_center.setDuration(duration // 8)
        anim_center.setEndValue(original_pos)
        group.addAnimation(anim_center)

        return group

    @staticmethod
    def pulse(widget: QWidget, duration: int = 1000, scale_factor: float = 1.05):
        """
        Create pulsing animation for widget.

        Args:
            widget: Widget to animate
            duration: Animation duration in milliseconds
            scale_factor: Scale multiplier for pulse effect

        Returns:
            QSequentialAnimationGroup: Pulse animation sequence
        """
        current_geometry = widget.geometry()
        scaled_width = int(current_geometry.width() * scale_factor)
        scaled_height = int(current_geometry.height() * scale_factor)
        x_offset = (scaled_width - current_geometry.width()) // 2
        y_offset = (scaled_height - current_geometry.height()) // 2

        scaled_geometry = QRect(
            current_geometry.x() - x_offset,
            current_geometry.y() - y_offset,
            scaled_width,
            scaled_height,
        )

        # Scale up
        scale_up = QPropertyAnimation(widget, b"geometry")
        scale_up.setDuration(duration // 2)
        scale_up.setStartValue(current_geometry)
        scale_up.setEndValue(scaled_geometry)
        scale_up.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Scale down
        scale_down = QPropertyAnimation(widget, b"geometry")
        scale_down.setDuration(duration // 2)
        scale_down.setStartValue(scaled_geometry)
        scale_down.setEndValue(current_geometry)
        scale_down.setEasingCurve(QEasingCurve.Type.InOutCubic)

        group = QSequentialAnimationGroup()
        group.addAnimation(scale_up)
        group.addAnimation(scale_down)
        group.setLoopCount(-1)  # Infinite loop
        return group


class HoverEffect:
    """
    Helper class for adding hover effects to widgets.
    """

    @staticmethod
    def add_scale_hover(
        widget: QWidget, scale_factor: float = 1.05, duration: int = 150
    ):
        """
        Add scale effect on hover.

        Args:
            widget: Widget to add effect to
            scale_factor: Scale multiplier on hover
            duration: Animation duration in milliseconds
        """
        original_geometry = widget.geometry()

        def on_enter(event):
            scaled_width = int(original_geometry.width() * scale_factor)
            scaled_height = int(original_geometry.height() * scale_factor)
            x_offset = (scaled_width - original_geometry.width()) // 2
            y_offset = (scaled_height - original_geometry.height()) // 2

            target_geometry = QRect(
                original_geometry.x() - x_offset,
                original_geometry.y() - y_offset,
                scaled_width,
                scaled_height,
            )

            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(duration)
            animation.setEndValue(target_geometry)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._hover_animation = animation

        def on_leave(event):
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(duration)
            animation.setEndValue(original_geometry)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._hover_animation = animation

        widget.enterEvent = on_enter
        widget.leaveEvent = on_leave

    @staticmethod
    def add_shadow_hover(
        widget: QWidget,
        normal_blur: int = 10,
        hover_blur: int = 20,
        color: QColor = QColor(0, 0, 0, 100),
        duration: int = 200,
    ):
        """
        Add shadow effect on hover.

        Args:
            widget: Widget to add effect to
            normal_blur: Normal shadow blur radius
            hover_blur: Hover shadow blur radius
            color: Shadow color
            duration: Animation duration in milliseconds
        """
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(normal_blur)
        shadow.setColor(color)
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)

        def on_enter(event):
            animation = QPropertyAnimation(shadow, b"blurRadius")
            animation.setDuration(duration)
            animation.setStartValue(normal_blur)
            animation.setEndValue(hover_blur)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._shadow_animation = animation

        def on_leave(event):
            animation = QPropertyAnimation(shadow, b"blurRadius")
            animation.setDuration(duration)
            animation.setStartValue(hover_blur)
            animation.setEndValue(normal_blur)
            animation.setEasingCurve(QEasingCurve.Type.InCubic)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._shadow_animation = animation

        widget.enterEvent = on_enter
        widget.leaveEvent = on_leave

    @staticmethod
    def add_opacity_hover(
        widget: QWidget, normal_opacity: float = 0.7, hover_opacity: float = 1.0
    ):
        """
        Add opacity effect on hover.

        Args:
            widget: Widget to add effect to
            normal_opacity: Normal opacity value
            hover_opacity: Hover opacity value
        """
        opacity_effect = QGraphicsOpacityEffect(widget)
        opacity_effect.setOpacity(normal_opacity)
        widget.setGraphicsEffect(opacity_effect)

        def on_enter(event):
            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(150)
            animation.setEndValue(hover_opacity)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._opacity_animation = animation

        def on_leave(event):
            animation = QPropertyAnimation(opacity_effect, b"opacity")
            animation.setDuration(150)
            animation.setEndValue(normal_opacity)
            animation.start(QAbstractAnimation.DeletionPolicy.DeleteWhenStopped)
            widget._opacity_animation = animation

        widget.enterEvent = on_enter
        widget.leaveEvent = on_leave


class LoadingSpinner(QWidget):
    """
    Animated loading spinner widget.
    """

    def __init__(
        self, size: int = 40, color: QColor = QColor(16, 185, 129), parent=None
    ):
        """
        Initialize loading spinner.

        Args:
            size: Spinner size in pixels
            color: Spinner color
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._rotation = 0
        self._color = color

        self._animation = QPropertyAnimation(self, b"rotation")
        self._animation.setDuration(1000)
        self._animation.setStartValue(0)
        self._animation.setEndValue(360)
        self._animation.setLoopCount(-1)
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)

    def start(self):
        """Start spinner animation."""
        self._animation.start()

    def stop(self):
        """Stop spinner animation."""
        self._animation.stop()

    @pyqtProperty(int)
    def rotation(self):
        """Get current rotation angle."""
        return self._rotation

    @rotation.setter
    def rotation(self, angle):
        """Set rotation angle."""
        self._rotation = angle
        self.update()

    def paintEvent(self, event):
        """Paint spinner."""
        from PyQt6.QtGui import QPainter, QPen
        import math

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center_x = self.width() / 2
        center_y = self.height() / 2
        radius = min(self.width(), self.height()) / 2 - 5

        # Draw spinning arcs
        for i in range(8):
            angle = (self._rotation + i * 45) % 360
            opacity = 255 - (i * 30)
            color = QColor(self._color)
            color.setAlpha(opacity)

            pen = QPen(color)
            pen.setWidth(3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            x = center_x + radius * math.cos(math.radians(angle))
            y = center_y + radius * math.sin(math.radians(angle))
            painter.drawPoint(int(x), int(y))


class ProgressIndicator(QWidget):
    """
    Smooth progress indicator with animation.
    """

    def __init__(self, parent=None):
        """Initialize progress indicator."""
        super().__init__(parent)
        self._progress = 0
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(300)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    @pyqtProperty(int)
    def progress(self):
        """Get current progress value."""
        return self._progress

    @progress.setter
    def progress(self, value):
        """Set progress value with animation."""
        self._progress = value
        self.update()

    def set_progress(self, value: int):
        """
        Set progress value with smooth animation.

        Args:
            value: Progress value (0-100)
        """
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(value)
        self._animation.start()

    def paintEvent(self, event):
        """Paint progress bar."""
        from PyQt6.QtGui import QPainter, QPainterPath

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(0, 0, self.width(), self.height(), 4, 4)
        painter.fillPath(bg_path, QColor(60, 60, 60))

        # Progress
        if self._progress > 0:
            progress_width = int(self.width() * (self._progress / 100))
            progress_path = QPainterPath()
            progress_path.addRoundedRect(0, 0, progress_width, self.height(), 4, 4)
            painter.fillPath(progress_path, QColor(16, 185, 129))
