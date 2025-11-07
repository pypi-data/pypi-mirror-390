"""
CustomProgressBar - Progress indicator with animations.

A fully customizable progress bar widget with support for:
- Custom colors (background, progress, text)
- Configurable size and border radius
- Smooth animations
- Percentage display
- Indeterminate mode
"""

from PyQt6.QtWidgets import QProgressBar, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor
from typing import Optional


class CustomProgressBar(QProgressBar):
    """
    Progress bar widget with custom styling and animations.
    
    Signals:
        progress_changed_custom: Emitted when progress changes
    """
    
    progress_changed_custom = pyqtSignal(int)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        min_value: int = 0,
        max_value: int = 100,
        current_value: int = 0,
        width: int = 300,
        height: int = 20,
        border_radius: int = 10,
        animation_name: str = "smooth",
        show_text: bool = True,
        show_percentage: bool = True,
        bg_color: str = "rgba(168, 85, 247, 0.1)",
        progress_color: str = "#a855f7",
        text_color: str = "#ffffff",
        disabled_color: str = "rgba(168, 85, 247, 0.05)",
        font_family: str = "Segoe UI",
        font_size: int = 10,
    ):
        """
        Initialize CustomProgressBar.
        
        Args:
            parent: Parent widget
            min_value: Minimum value
            max_value: Maximum value
            current_value: Current value
            width: Widget width in pixels
            height: Widget height in pixels
            border_radius: Border radius in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            show_text: Show text on progress bar
            show_percentage: Show percentage text
            bg_color: Background color (hex or rgba)
            progress_color: Progress color (hex or rgba)
            text_color: Text color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.border_radius = border_radius
        self.animation_name = animation_name
        self.show_percentage = show_percentage
        
        # Colors
        self.bg_color = bg_color
        self.progress_color = progress_color
        self.text_color = text_color
        self.disabled_color = disabled_color
        
        # Set range and value
        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setValue(current_value)
        
        # Set size
        self.setFixedSize(width, height)
        
        # Set text
        self.setTextVisible(show_text)
        
        # Set font
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Connect signals
        self.valueChanged.connect(self._on_value_changed)
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
        self.is_animating = False
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QProgressBar {{
                background-color: {self.bg_color};
                border-radius: {self.border_radius}px;
                text-align: center;
                color: {self.text_color};
                font-family: {self.font().family()};
                font-size: {self.font().pointSize()}pt;
                font-weight: bold;
            }}
            QProgressBar::chunk {{
                background-color: {self.progress_color};
                border-radius: {self.border_radius}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_value_changed(self, value: int):
        """Handle value change event."""
        self.progress_changed_custom.emit(value)
        if self.animation_name != "none":
            self._start_animation()
    
    def _start_animation(self):
        """Start animation."""
        if self.animation_name == "none":
            return
        
        self.animation_progress = 0.0
        self.is_animating = True
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
            self.is_animating = False
        
        self.update()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        progress_color: Optional[str] = None,
        text_color: Optional[str] = None,
        disabled_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if progress_color:
            self.progress_color = progress_color
        if text_color:
            self.text_color = text_color
        if disabled_color:
            self.disabled_color = disabled_color
        
        self._apply_stylesheet()
    
    def set_value(self, value: int):
        """Set progress value."""
        self.setValue(value)
    
    def get_value(self) -> int:
        """Get current value."""
        return self.value()
    
    def set_range(self, min_value: int, max_value: int):
        """Set value range."""
        self.setMinimum(min_value)
        self.setMaximum(max_value)
    
    def set_size(self, width: int, height: int):
        """Change dimensions."""
        self.setFixedSize(width, height)
    
    def set_border_radius(self, radius: int):
        """Update border radius."""
        self.border_radius = radius
        self._apply_stylesheet()
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
    
    def set_text_visible(self, visible: bool):
        """Set text visibility."""
        self.setTextVisible(visible)
    
    def get_percentage(self) -> int:
        """Get progress as percentage."""
        if self.maximum() == 0:
            return 0
        return int((self.value() / self.maximum()) * 100)
    
    def set_percentage(self, percentage: int):
        """Set progress by percentage."""
        value = int((percentage / 100) * self.maximum())
        self.setValue(value)
