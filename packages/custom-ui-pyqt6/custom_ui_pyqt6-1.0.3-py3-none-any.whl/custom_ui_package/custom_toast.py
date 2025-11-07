"""
CustomToast - Notification/toast messages.

A fully customizable toast widget with support for:
- Custom colors (background, text, border)
- Multiple toast types (info, success, warning, error)
- Auto-dismiss with configurable duration
- Smooth animations
- Position control
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class CustomToast(QWidget):
    """
    Toast notification widget with custom styling and animations.
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        message: str = "Notification",
        toast_type: str = "info",
        duration: int = 3000,
        position: str = "bottom-right",
        width: int = 300,
        border_radius: int = 8,
        animation_name: str = "smooth",
        bg_color: Optional[str] = None,
        text_color: str = "#ffffff",
        border_color: Optional[str] = None,
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomToast.
        
        Args:
            parent: Parent widget
            message: Toast message
            toast_type: Type - 'info', 'success', 'warning', 'error'
            duration: Display duration in milliseconds
            position: Position - 'top-left', 'top-right', 'bottom-left', 'bottom-right'
            width: Toast width in pixels
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
        self.toast_type = toast_type
        self.duration = duration
        self.position = position
        self.border_radius = border_radius
        self.animation_name = animation_name
        self.text_color = text_color
        
        # Set colors based on type if not provided
        type_colors = {
            "info": ("#0ea5e9", "#0c4a6e"),
            "success": ("#10b981", "#064e3b"),
            "warning": ("#f59e0b", "#78350f"),
            "error": ("#ef4444", "#7f1d1d"),
        }
        
        if bg_color is None:
            self.bg_color = type_colors.get(toast_type, ("#1a1a2e", "#0f0f1e"))[0]
        else:
            self.bg_color = bg_color
        
        if border_color is None:
            self.border_color = type_colors.get(toast_type, ("#1a1a2e", "#0f0f1e"))[1]
        else:
            self.border_color = border_color
        
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedWidth(width)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(0)
        
        # Create message label
        self.message_label = QLabel(message)
        font = QFont(font_family, font_size)
        self.message_label.setFont(font)
        self.message_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.message_label.setWordWrap(True)
        layout.addWidget(self.message_label)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Timer for auto-dismiss
        self.dismiss_timer = QTimer()
        self.dismiss_timer.setSingleShot(True)
        self.dismiss_timer.timeout.connect(self._on_dismiss)
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
        self.is_showing = False
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QWidget {{
                background-color: {self.bg_color};
                border: 1px solid {self.border_color};
                border-radius: {self.border_radius}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def show_toast(self):
        """Show the toast notification."""
        self.is_showing = True
        self._position_toast()
        self.show()
        
        if self.animation_name != "none":
            self._start_animation()
        
        # Start dismiss timer
        if self.duration > 0:
            self.dismiss_timer.start(self.duration)
    
    def _position_toast(self):
        """Position the toast on screen."""
        if self.parent() is None:
            screen = QApplication.primaryScreen()
            screen_rect = screen.geometry()
        else:
            screen_rect = self.parent().geometry()
        
        margin = 20
        
        if self.position == "top-left":
            x = screen_rect.left() + margin
            y = screen_rect.top() + margin
        elif self.position == "top-right":
            x = screen_rect.right() - self.width() - margin
            y = screen_rect.top() + margin
        elif self.position == "bottom-left":
            x = screen_rect.left() + margin
            y = screen_rect.bottom() - self.height() - margin
        else:  # bottom-right
            x = screen_rect.right() - self.width() - margin
            y = screen_rect.bottom() - self.height() - margin
        
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
    
    def _on_dismiss(self):
        """Handle auto-dismiss."""
        self.is_showing = False
        self.close()
        self.deleteLater()
    
    def paintEvent(self, event):
        """Paint the toast."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with border radius
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.border_radius, self.border_radius)
        
        painter.fillPath(path, QBrush(QColor(self.bg_color)))
        painter.strokePath(path, QPen(QColor(self.border_color), 1))
        
        painter.end()
        super().paintEvent(event)
    
    def set_message(self, message: str):
        """Set toast message."""
        self.message_label.setText(message)
    
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
            self.message_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        if border_color:
            self.border_color = border_color
        
        self._apply_stylesheet()
    
    def set_duration(self, duration: int):
        """Set display duration."""
        self.duration = duration
    
    def set_position(self, position: str):
        """Set toast position."""
        self.position = position
        if self.is_showing:
            self._position_toast()
