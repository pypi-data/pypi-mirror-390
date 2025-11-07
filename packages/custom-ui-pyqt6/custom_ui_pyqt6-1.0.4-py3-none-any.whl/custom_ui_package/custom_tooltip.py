"""
CustomTooltip - Hover tooltips with custom styling.

A fully customizable tooltip widget with support for:
- Custom colors (background, text, border)
- Multiple position options
- Smooth animations
- Configurable delay
- Arrow pointing to target
"""

from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class CustomTooltip(QWidget):
    """
    Tooltip widget with custom styling and animations.
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        text: str = "Tooltip",
        delay: int = 500,
        position: str = "top",
        width: int = 200,
        border_radius: int = 6,
        animation_name: str = "smooth",
        bg_color: str = "#2d2d44",
        text_color: str = "#ffffff",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        font_family: str = "Segoe UI",
        font_size: int = 10,
    ):
        """
        Initialize CustomTooltip.
        
        Args:
            parent: Parent widget
            text: Tooltip text
            delay: Show delay in milliseconds
            position: Position - 'top', 'bottom', 'left', 'right'
            width: Tooltip width in pixels
            border_radius: Border radius in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.tooltip_text = text
        self.delay = delay
        self.position = position
        self.border_radius = border_radius
        self.animation_name = animation_name
        self.arrow_size = 8
        
        # Colors
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(width)
        
        # Create label
        self.label = QLabel(text)
        font = QFont(font_family, font_size)
        self.label.setFont(font)
        self.label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Set layout
        from PyQt6.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.addWidget(self.label)
        
        # Timer for delayed show
        self.show_timer = QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._on_show_timeout)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
    
    def show_at(self, widget: QWidget, offset_x: int = 0, offset_y: int = 0):
        """Show tooltip at widget position."""
        self.target_widget = widget
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        if self.delay > 0:
            self.show_timer.start(self.delay)
        else:
            self._on_show_timeout()
    
    def _on_show_timeout(self):
        """Handle show timer timeout."""
        self._position_tooltip()
        self.show()
        
        if self.animation_name != "none":
            self._start_animation()
    
    def _position_tooltip(self):
        """Position the tooltip relative to target widget."""
        if not hasattr(self, 'target_widget'):
            return
        
        widget_rect = self.target_widget.geometry()
        widget_pos = self.target_widget.mapToGlobal(QPoint(0, 0))
        
        # Adjust for offset
        widget_rect.moveTo(widget_pos)
        
        spacing = 10
        
        if self.position == "top":
            x = widget_rect.center().x() - self.width() // 2
            y = widget_rect.top() - self.height() - spacing
        elif self.position == "bottom":
            x = widget_rect.center().x() - self.width() // 2
            y = widget_rect.bottom() + spacing
        elif self.position == "left":
            x = widget_rect.left() - self.width() - spacing
            y = widget_rect.center().y() - self.height() // 2
        else:  # right
            x = widget_rect.right() + spacing
            y = widget_rect.center().y() - self.height() // 2
        
        # Clamp to screen
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        
        x = max(screen_rect.left(), min(x, screen_rect.right() - self.width()))
        y = max(screen_rect.top(), min(y, screen_rect.bottom() - self.height()))
        
        self.move(x, y)
    
    def _start_animation(self):
        """Start animation."""
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        # Update opacity
        opacity = self.animation_progress
        self.setWindowOpacity(opacity)
    
    def paintEvent(self, event):
        """Paint the tooltip."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with border radius
        path = QPainterPath()
        path.addRoundedRect(
            self.arrow_size, 0,
            self.width() - self.arrow_size,
            self.height(),
            self.border_radius,
            self.border_radius
        )
        
        painter.fillPath(path, QBrush(QColor(self.bg_color)))
        painter.strokePath(path, QPen(QColor(self.border_color), 1))
        
        # Draw arrow
        if self.position == "top":
            arrow_points = [
                QPoint(self.width() // 2, self.height()),
                QPoint(self.width() // 2 - self.arrow_size, self.height() - self.arrow_size),
                QPoint(self.width() // 2 + self.arrow_size, self.height() - self.arrow_size),
            ]
        elif self.position == "bottom":
            arrow_points = [
                QPoint(self.width() // 2, 0),
                QPoint(self.width() // 2 - self.arrow_size, self.arrow_size),
                QPoint(self.width() // 2 + self.arrow_size, self.arrow_size),
            ]
        elif self.position == "left":
            arrow_points = [
                QPoint(self.width(), self.height() // 2),
                QPoint(self.width() - self.arrow_size, self.height() // 2 - self.arrow_size),
                QPoint(self.width() - self.arrow_size, self.height() // 2 + self.arrow_size),
            ]
        else:  # right
            arrow_points = [
                QPoint(0, self.height() // 2),
                QPoint(self.arrow_size, self.height() // 2 - self.arrow_size),
                QPoint(self.arrow_size, self.height() // 2 + self.arrow_size),
            ]
        
        arrow_path = QPainterPath()
        arrow_path.moveTo(arrow_points[0])
        arrow_path.lineTo(arrow_points[1])
        arrow_path.lineTo(arrow_points[2])
        arrow_path.closeSubpath()
        
        painter.fillPath(arrow_path, QBrush(QColor(self.bg_color)))
        painter.strokePath(arrow_path, QPen(QColor(self.border_color), 1))
        
        painter.end()
        super().paintEvent(event)
    
    def set_text(self, text: str):
        """Set tooltip text."""
        self.tooltip_text = text
        self.label.setText(text)
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
            self.label.setStyleSheet(f"color: {text_color}; background: transparent;")
        if border_color:
            self.border_color = border_color
        
        self.update()
    
    def set_delay(self, delay: int):
        """Set show delay."""
        self.delay = delay
    
    def set_position(self, position: str):
        """Set tooltip position."""
        self.position = position
