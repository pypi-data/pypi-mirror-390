"""
CustomRadioButton - Radio button with custom styling and animations.

A fully customizable radio button widget with support for:
- Custom colors (background, border, check, hover, focus, disabled)
- Smooth animations on state changes
- Configurable size and border
- Label text support
- Radio button groups
"""

from PyQt6.QtWidgets import QRadioButton, QWidget, QButtonGroup
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QColor
from typing import Optional


class CustomRadioButton(QRadioButton):
    """
    Radio button widget with custom styling and animations.
    
    Signals:
        toggled_custom: Emitted when toggled (checked/unchecked)
    """
    
    toggled_custom = pyqtSignal(bool)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        label: str = "Option",
        checked: bool = False,
        size: int = 20,
        border_width: int = 2,
        animation_name: str = "smooth",
        bg_color: str = "#1a1a2e",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        check_color: str = "#a855f7",
        hover_color: str = "#a855f7",
        focus_color: str = "#a855f7",
        disabled_color: str = "rgba(168, 85, 247, 0.1)",
        text_color: str = "#ffffff",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomRadioButton.
        
        Args:
            parent: Parent widget
            label: Label text
            checked: Initial checked state
            size: Radio button size in pixels
            border_width: Border width in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            border_color: Border color (hex or rgba)
            check_color: Check mark color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            focus_color: Focus state color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
            text_color: Text color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.radio_size = size
        self.border_width = border_width
        self.animation_name = animation_name
        
        # Colors
        self.bg_color = bg_color
        self.border_color = border_color
        self.check_color = check_color
        self.hover_color = hover_color
        self.focus_color = focus_color
        self.disabled_color = disabled_color
        self.text_color = text_color
        self.current_border_color = border_color
        
        # State tracking
        self.is_hovered = False
        self.is_focused = False
        
        # Set text
        self.setText(label)
        self.setChecked(checked)
        
        # Set font
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Set size
        self.setMinimumHeight(size + 8)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Connect signals
        self.toggled.connect(self._on_toggled)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QRadioButton {{
                color: {self.text_color};
                font-family: {self.font().family()};
                font-size: {self.font().pointSize()}pt;
                spacing: 8px;
            }}
            QRadioButton::indicator {{
                width: {self.radio_size}px;
                height: {self.radio_size}px;
                border-radius: {self.radio_size // 2}px;
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {self.bg_color};
                border: {self.border_width}px solid {self.current_border_color};
            }}
            QRadioButton::indicator:checked {{
                background-color: {self.check_color};
                border: {self.border_width}px solid {self.check_color};
            }}
            QRadioButton::indicator:hover {{
                border: {self.border_width}px solid {self.hover_color};
            }}
            QRadioButton::indicator:focus {{
                border: {self.border_width}px solid {self.focus_color};
            }}
            QRadioButton::indicator:disabled {{
                background-color: {self.disabled_color};
                border: {self.border_width}px solid {self.disabled_color};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_toggled(self, checked: bool):
        """Handle toggle event."""
        self.toggled_custom.emit(checked)
    
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
            self._update_border_color()
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
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
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        border_color: Optional[str] = None,
        check_color: Optional[str] = None,
        hover_color: Optional[str] = None,
        focus_color: Optional[str] = None,
        disabled_color: Optional[str] = None,
        text_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        if check_color:
            self.check_color = check_color
        if hover_color:
            self.hover_color = hover_color
        if focus_color:
            self.focus_color = focus_color
        if disabled_color:
            self.disabled_color = disabled_color
        if text_color:
            self.text_color = text_color
        
        self._apply_stylesheet()
    
    def set_size(self, size: int):
        """Change radio button size."""
        self.radio_size = size
        self.setMinimumHeight(size + 8)
        self._apply_stylesheet()
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
    
    def set_label(self, label: str):
        """Update label text."""
        self.setText(label)
    
    def is_checked(self) -> bool:
        """Check if radio button is checked."""
        return self.isChecked()
    
    def set_checked(self, checked: bool):
        """Set checked state."""
        self.setChecked(checked)
