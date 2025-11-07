"""
CustomSpinner - Loading indicator with animations.

A fully customizable spinner widget with support for:
- Custom colors (spinner, background)
- Multiple animation styles
- Configurable size
- Smooth continuous rotation
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect, QSize
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from typing import Optional


class CustomSpinner(QWidget):
    """
    Spinner widget with custom styling and animations.
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        size: int = 50,
        line_width: int = 4,
        animation_speed: int = 50,
        spinner_color: str = "#a855f7",
        bg_color: str = "rgba(168, 85, 247, 0.1)",
        animation_style: str = "rotating",
    ):
        """
        Initialize CustomSpinner.
        
        Args:
            parent: Parent widget
            size: Spinner size in pixels
            line_width: Line width in pixels
            animation_speed: Animation speed in milliseconds
            spinner_color: Spinner color (hex or rgba)
            bg_color: Background color (hex or rgba)
            animation_style: Animation style - 'rotating', 'pulsing', 'bouncing'
        """
        super().__init__(parent)
        
        # Store properties
        self.spinner_size = size
        self.line_width = line_width
        self.animation_speed = animation_speed
        self.spinner_color = spinner_color
        self.bg_color = bg_color
        self.animation_style = animation_style
        
        # Animation state
        self.rotation_angle = 0
        self.pulse_value = 1.0
        self.pulse_direction = 1
        
        # Set size
        self.setFixedSize(size, size)
        
        # Create timer for animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_timer.start(animation_speed)
    
    def _update_animation(self):
        """Update animation state."""
        if self.animation_style == "rotating":
            self.rotation_angle = (self.rotation_angle + 6) % 360
        elif self.animation_style == "pulsing":
            self.pulse_value += 0.05 * self.pulse_direction
            if self.pulse_value >= 1.0:
                self.pulse_direction = -1
            elif self.pulse_value <= 0.3:
                self.pulse_direction = 1
        elif self.animation_style == "bouncing":
            self.rotation_angle = (self.rotation_angle + 10) % 360
        
        self.update()
    
    def paintEvent(self, event):
        """Paint the spinner."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background circle
        bg_color = QColor(self.bg_color)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, self.spinner_size, self.spinner_size)
        
        # Draw spinner
        center_x = self.spinner_size // 2
        center_y = self.spinner_size // 2
        radius = (self.spinner_size - self.line_width) // 2
        
        if self.animation_style == "rotating":
            self._draw_rotating_spinner(painter, center_x, center_y, radius)
        elif self.animation_style == "pulsing":
            self._draw_pulsing_spinner(painter, center_x, center_y, radius)
        elif self.animation_style == "bouncing":
            self._draw_bouncing_spinner(painter, center_x, center_y, radius)
        
        painter.end()
    
    def _draw_rotating_spinner(self, painter, center_x, center_y, radius):
        """Draw rotating spinner."""
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)
        
        spinner_color = QColor(self.spinner_color)
        pen = QPen(spinner_color, self.line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw arc
        painter.drawArc(
            -radius, -radius, radius * 2, radius * 2,
            0, 270 * 16
        )
        
        painter.restore()
    
    def _draw_pulsing_spinner(self, painter, center_x, center_y, radius):
        """Draw pulsing spinner."""
        spinner_color = QColor(self.spinner_color)
        spinner_color.setAlpha(int(255 * self.pulse_value))
        
        pen = QPen(spinner_color, self.line_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        # Draw circle
        current_radius = int(radius * self.pulse_value)
        painter.drawEllipse(
            center_x - current_radius,
            center_y - current_radius,
            current_radius * 2,
            current_radius * 2
        )
    
    def _draw_bouncing_spinner(self, painter, center_x, center_y, radius):
        """Draw bouncing spinner."""
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation_angle)
        
        spinner_color = QColor(self.spinner_color)
        
        # Draw multiple dots
        dot_count = 8
        for i in range(dot_count):
            angle = (360 / dot_count) * i
            x = radius * (1 + 0.3 * (i % 2)) * (1 if angle < 180 else -1)
            y = radius * (1 + 0.3 * (i % 2)) * (1 if angle % 180 < 90 else -1)
            
            alpha = int(255 * (1 - (i / dot_count)))
            spinner_color.setAlpha(alpha)
            painter.setBrush(QBrush(spinner_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(x - 2), int(y - 2), 4, 4)
        
        painter.restore()
    
    def start(self):
        """Start the spinner animation."""
        self.animation_timer.start()
    
    def stop(self):
        """Stop the spinner animation."""
        self.animation_timer.stop()
    
    def set_colors(self, spinner_color: Optional[str] = None, bg_color: Optional[str] = None):
        """Update colors at runtime."""
        if spinner_color:
            self.spinner_color = spinner_color
        if bg_color:
            self.bg_color = bg_color
        
        self.update()
    
    def set_size(self, size: int):
        """Change spinner size."""
        self.spinner_size = size
        self.setFixedSize(size, size)
        self.update()
    
    def set_animation_style(self, style: str):
        """Change animation style."""
        self.animation_style = style
        self.rotation_angle = 0
        self.pulse_value = 1.0
        self.update()
    
    def set_animation_speed(self, speed: int):
        """Change animation speed."""
        self.animation_speed = speed
        self.animation_timer.setInterval(speed)
    
    def is_running(self) -> bool:
        """Check if spinner is running."""
        return self.animation_timer.isActive()
