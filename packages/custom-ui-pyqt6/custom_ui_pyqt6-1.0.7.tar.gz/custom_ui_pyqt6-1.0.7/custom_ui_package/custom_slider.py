"""
CustomSlider - Range slider with custom track and handle styling.

A fully customizable slider widget with support for:
- Custom colors (track, handle, groove, hover, focus)
- Configurable size and border
- Smooth animations on interaction
- Value range configuration
- Tick marks and labels
"""

from PyQt6.QtWidgets import QSlider, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class CustomSlider(QSlider):
    """
    Slider widget with custom styling and animations.
    
    Signals:
        value_changed_custom: Emitted when value changes
        slider_moved_custom: Emitted when slider is moved
    """
    
    value_changed_custom = pyqtSignal(int)
    slider_moved_custom = pyqtSignal(int)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        orientation: Qt.Orientation = Qt.Orientation.Horizontal,
        min_value: int = 0,
        max_value: int = 100,
        current_value: int = 50,
        width: int = 300,
        height: int = 30,
        handle_size: int = 20,
        track_height: int = 6,
        animation_name: str = "smooth",
        track_color: str = "rgba(168, 85, 247, 0.2)",
        groove_color: str = "#a855f7",
        handle_color: str = "#a855f7",
        hover_color: str = "#c084fc",
        focus_color: str = "#a855f7",
        disabled_color: str = "rgba(168, 85, 247, 0.1)",
    ):
        """
        Initialize CustomSlider.
        
        Args:
            parent: Parent widget
            orientation: Slider orientation (Horizontal or Vertical)
            min_value: Minimum value
            max_value: Maximum value
            current_value: Current value
            width: Widget width in pixels
            height: Widget height in pixels
            handle_size: Handle size in pixels
            track_height: Track height in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            track_color: Track background color (hex or rgba)
            groove_color: Groove (filled part) color (hex or rgba)
            handle_color: Handle color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            focus_color: Focus state color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
        """
        super().__init__(orientation, parent)
        
        # Store properties
        self.handle_size = handle_size
        self.track_height = track_height
        self.animation_name = animation_name
        
        # Colors
        self.track_color = track_color
        self.groove_color = groove_color
        self.handle_color = handle_color
        self.hover_color = hover_color
        self.focus_color = focus_color
        self.disabled_color = disabled_color
        self.current_handle_color = handle_color
        
        # State tracking
        self.is_hovered = False
        self.is_focused = False
        self.is_pressed = False
        
        # Set range and value
        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setValue(current_value)
        
        # Set size
        if orientation == Qt.Orientation.Horizontal:
            self.setFixedSize(width, height)
        else:
            self.setFixedSize(height, width)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Connect signals
        self.valueChanged.connect(self._on_value_changed)
        self.sliderMoved.connect(self._on_slider_moved)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QSlider::groove:horizontal {{
                background-color: {self.track_color};
                height: {self.track_height}px;
                border-radius: {self.track_height // 2}px;
                margin: {(self.handle_size - self.track_height) // 2}px 0px;
            }}
            QSlider::groove:vertical {{
                background-color: {self.track_color};
                width: {self.track_height}px;
                border-radius: {self.track_height // 2}px;
                margin: 0px {(self.handle_size - self.track_height) // 2}px;
            }}
            QSlider::handle:horizontal {{
                background-color: {self.current_handle_color};
                width: {self.handle_size}px;
                height: {self.handle_size}px;
                margin: -{(self.handle_size - self.track_height) // 2}px 0px;
                border-radius: {self.handle_size // 2}px;
            }}
            QSlider::handle:vertical {{
                background-color: {self.current_handle_color};
                width: {self.handle_size}px;
                height: {self.handle_size}px;
                margin: 0px -{(self.handle_size - self.track_height) // 2}px;
                border-radius: {self.handle_size // 2}px;
            }}
            QSlider::handle:hover {{
                background-color: {self.hover_color};
            }}
            QSlider::handle:focus {{
                background-color: {self.focus_color};
            }}
            QSlider::handle:disabled {{
                background-color: {self.disabled_color};
            }}
            QSlider::sub-page:horizontal {{
                background-color: {self.groove_color};
                border-radius: {self.track_height // 2}px;
            }}
            QSlider::sub-page:vertical {{
                background-color: {self.groove_color};
                border-radius: {self.track_height // 2}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_value_changed(self, value: int):
        """Handle value change event."""
        self.value_changed_custom.emit(value)
    
    def _on_slider_moved(self, value: int):
        """Handle slider move event."""
        self.slider_moved_custom.emit(value)
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        super().mousePressEvent(event)
        self.is_pressed = True
        self._start_animation()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        super().mouseReleaseEvent(event)
        self.is_pressed = False
        self._start_animation()
    
    def focusInEvent(self, event):
        """Handle focus in event."""
        super().focusInEvent(event)
        self.is_focused = True
        self._start_animation()
    
    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)
        self.is_focused = False
        self._start_animation()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.is_hovered = True
        self._start_animation()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.is_hovered = False
        if not self.is_focused:
            self._start_animation()
    
    def _start_animation(self):
        """Start animation."""
        if self.animation_name == "none":
            self._update_handle_color()
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        self._update_handle_color()
    
    def _update_handle_color(self):
        """Update handle color based on state."""
        if self.is_pressed:
            target_color = self.focus_color
        elif self.is_focused:
            target_color = self.focus_color
        elif self.is_hovered:
            target_color = self.hover_color
        else:
            target_color = self.handle_color
        
        if self.animation_name != "none":
            self.current_handle_color = self._interpolate_color(
                self.current_handle_color, target_color, self.animation_progress
            )
        else:
            self.current_handle_color = target_color
        
        self._apply_stylesheet()
    
    def _interpolate_color(self, color1: str, color2: str, progress: float) -> str:
        """Interpolate between two colors."""
        c1 = QColor(color1)
        c2 = QColor(color2)
        
        r = int(c1.red() + (c2.red() - c1.red()) * progress)
        g = int(c1.green() + (c2.green() - c1.green()) * progress)
        b = int(c1.blue() + (c2.blue() - c1.blue()) * progress)
        a = int(c1.alpha() + (c2.alpha() - c1.alpha()) * progress)
        
        return f"rgba({r}, {g}, {b}, {a / 255.0})"
    
    def set_colors(
        self,
        track_color: Optional[str] = None,
        groove_color: Optional[str] = None,
        handle_color: Optional[str] = None,
        hover_color: Optional[str] = None,
        focus_color: Optional[str] = None,
        disabled_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if track_color:
            self.track_color = track_color
        if groove_color:
            self.groove_color = groove_color
        if handle_color:
            self.handle_color = handle_color
        if hover_color:
            self.hover_color = hover_color
        if focus_color:
            self.focus_color = focus_color
        if disabled_color:
            self.disabled_color = disabled_color
        
        self._apply_stylesheet()
    
    def set_range(self, min_value: int, max_value: int):
        """Set value range."""
        self.setMinimum(min_value)
        self.setMaximum(max_value)
    
    def set_value(self, value: int):
        """Set current value."""
        self.setValue(value)
    
    def get_value(self) -> int:
        """Get current value."""
        return self.value()
    
    def set_size(self, width: int, height: int):
        """Change dimensions."""
        self.setFixedSize(width, height)
    
    def set_handle_size(self, size: int):
        """Change handle size."""
        self.handle_size = size
        self._apply_stylesheet()
    
    def set_track_height(self, height: int):
        """Change track height."""
        self.track_height = height
        self._apply_stylesheet()
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
