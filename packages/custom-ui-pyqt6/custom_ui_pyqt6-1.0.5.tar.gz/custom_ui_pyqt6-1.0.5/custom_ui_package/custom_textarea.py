"""
CustomTextArea - Multi-line text input with scrollbars and custom styling.

A fully customizable multi-line text input widget with support for:
- Custom colors (background, text, border, hover, focus, disabled)
- Multiple shape options (rounded_rectangle, circular, custom_path)
- Smooth animations on hover and focus
- Drop shadow effects
- Configurable border and padding
- Placeholder text support
"""

from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional, Tuple


class CustomTextArea(QTextEdit):
    """
    Multi-line text input widget with custom styling and animations.
    
    Signals:
        text_changed_custom: Emitted when text changes
        focus_in: Emitted when widget gains focus
        focus_out: Emitted when widget loses focus
    """
    
    text_changed_custom = pyqtSignal(str)
    focus_in = pyqtSignal()
    focus_out = pyqtSignal()
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        placeholder: str = "Enter text...",
        width: int = 300,
        height: int = 150,
        shape: str = "rounded_rectangle",
        border_radius: int = 12,
        border_width: int = 2,
        padding: int = 12,
        animation_name: str = "smooth",
        bg_color: str = "#1a1a2e",
        text_color: str = "#ffffff",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        hover_color: str = "#a855f7",
        focus_color: str = "#a855f7",
        disabled_color: str = "rgba(168, 85, 247, 0.1)",
        shadow_color: str = "rgba(168, 85, 247, 0.2)",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomTextArea.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            width: Widget width in pixels
            height: Widget height in pixels
            shape: Shape type - 'rounded_rectangle', 'circular', 'custom_path'
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            padding: Padding in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            focus_color: Focus state color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
            shadow_color: Shadow color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.shape = shape
        self.border_radius = border_radius
        self.border_width = border_width
        self.padding = padding
        self.animation_name = animation_name
        self.shadow_blur = 8
        self.shadow_offset_x = 0
        self.shadow_offset_y = 2
        
        # Colors
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.focus_color = focus_color
        self.disabled_color = disabled_color
        self.shadow_color = shadow_color
        self.current_border_color = border_color
        
        # State tracking
        self.is_hovered = False
        self.is_focused = False
        
        # Set size
        self.setFixedSize(width, height)
        
        # Set placeholder
        self.setPlaceholderText(placeholder)
        
        # Set font
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Connect signals
        self.textChanged.connect(self._on_text_changed)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet to the text area."""
        stylesheet = f"""
            QTextEdit {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: {self.border_width}px solid {self.current_border_color};
                border-radius: {self.border_radius}px;
                padding: {self.padding}px;
                font-family: {self.font().family()};
                font-size: {self.font().pointSize()}pt;
                selection-background-color: {self.focus_color};
                selection-color: {self.bg_color};
            }}
            QTextEdit:focus {{
                border: {self.border_width}px solid {self.focus_color};
                outline: none;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_text_changed(self):
        """Handle text change event."""
        self.text_changed_custom.emit(self.toPlainText())
    
    def focusInEvent(self, event):
        """Handle focus in event."""
        super().focusInEvent(event)
        self.is_focused = True
        self.focus_in.emit()
        self._start_animation()
    
    def focusOutEvent(self, event):
        """Handle focus out event."""
        super().focusOutEvent(event)
        self.is_focused = False
        self.focus_out.emit()
        self._start_animation()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        if not self.is_focused:
            self.is_hovered = True
            self._start_animation()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.is_hovered = False
        if not self.is_focused:
            self._start_animation()
    
    def _start_animation(self):
        """Start animation based on animation_name."""
        if self.animation_name == "none":
            self._update_border_color()
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)  # ~60 FPS
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        self._update_border_color()
    
    def _update_border_color(self):
        """Update border color based on state."""
        if self.is_focused:
            target_color = self.focus_color
        elif self.is_hovered:
            target_color = self.hover_color
        else:
            target_color = self.border_color
        
        # Interpolate color
        if self.animation_name != "none":
            self.current_border_color = self._interpolate_color(
                self.current_border_color, target_color, self.animation_progress
            )
        else:
            self.current_border_color = target_color
        
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
    
    def get_text(self) -> str:
        """Get the current text."""
        return self.toPlainText()
    
    def set_text(self, text: str):
        """Set the text."""
        self.setPlainText(text)
    
    def clear_text(self):
        """Clear the text."""
        self.clear()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_color: Optional[str] = None,
        hover_color: Optional[str] = None,
        focus_color: Optional[str] = None,
        disabled_color: Optional[str] = None,
        shadow_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
        if border_color:
            self.border_color = border_color
        if hover_color:
            self.hover_color = hover_color
        if focus_color:
            self.focus_color = focus_color
        if disabled_color:
            self.disabled_color = disabled_color
        if shadow_color:
            self.shadow_color = shadow_color
        
        self._apply_stylesheet()
    
    def set_shape(self, shape: str):
        """Change the shape type."""
        self.shape = shape
        self.update()
    
    def set_border_radius(self, radius: int):
        """Update border radius."""
        self.border_radius = radius
        self._apply_stylesheet()
    
    def set_size(self, width: int, height: int):
        """Change dimensions."""
        self.setFixedSize(width, height)
    
    def set_position(self, x: int, y: int):
        """Change position."""
        self.move(x, y)
    
    def set_shadow(
        self, blur_radius: int, offset_x: int, offset_y: int, color: str
    ):
        """Update shadow properties."""
        self.shadow_blur = blur_radius
        self.shadow_offset_x = offset_x
        self.shadow_offset_y = offset_y
        self.shadow_color = color
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
    
    def set_placeholder(self, text: str):
        """Update placeholder text."""
        self.setPlaceholderText(text)
    
    def is_focused_state(self) -> bool:
        """Check if widget is focused."""
        return self.is_focused
