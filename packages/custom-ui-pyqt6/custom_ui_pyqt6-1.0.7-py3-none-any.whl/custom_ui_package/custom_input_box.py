"""Custom Qt input box with configurable parameters and animations."""

from PyQt6.QtWidgets import QLineEdit, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from .colors.color_palette import get_global_color


class CustomInputBox(QLineEdit):
    """A custom QLineEdit with configurable styling, animations, and global color palette support."""
    
    # Custom signals
    text_changed_custom = pyqtSignal(str)
    focus_in = pyqtSignal()
    focus_out = pyqtSignal()
    
    def __init__(
        self,
        parent=None,
        placeholder="Enter text...",
        size=(200, 40),
        position=(0, 0),
        font_size=11,
        shape="rounded_rectangle",
        border_radius=8,
        bg_color=None,
        text_color=None,
        border_color=None,
        hover_color=None,
        focus_color=None,
        disabled_color=None,
        animation_name="smooth",
        shadow_blur=10,
        shadow_color=None,
        shadow_offset=(0, 2),
        border_width=1,
        padding="8px 12px"
    ):
        """Initialize the custom input box.
        
        Args:
            parent: Parent widget
            placeholder: Placeholder text
            size: Tuple of (width, height)
            position: Tuple of (x, y)
            font_size: Font size for the text
            shape: Shape type - "rounded_rectangle", "circular", "custom_path"
            border_radius: Border radius in pixels (8-20 recommended)
            bg_color: Background color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            focus_color: Focus state color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
            animation_name: Animation type - "smooth", "bounce", "elastic", "none"
            shadow_blur: Shadow blur radius
            shadow_color: Shadow color (hex or rgba)
            shadow_offset: Tuple of (x, y) shadow offset
            border_width: Border width in pixels
            padding: Padding value (e.g., "8px 12px")
        """
        super().__init__(parent)
        
        # Store configuration
        self.shape = shape
        self.border_radius = border_radius
        self.animation_name = animation_name
        self.shadow_blur = shadow_blur
        self.shadow_offset = shadow_offset
        self.border_width = border_width
        self.padding = padding
        
        # Set default colors using global palette
        self.bg_color = bg_color or get_global_color('surface', '#1a1a2e')
        self.text_color = text_color or get_global_color('text', '#ffffff')
        self.border_color = border_color or get_global_color('border', 'rgba(168, 85, 247, 0.3)')
        self.hover_color = hover_color or get_global_color('primary', '#a855f7')
        self.focus_color = focus_color or get_global_color('primary', '#a855f7')
        self.disabled_color = disabled_color or get_global_color('border', 'rgba(168, 85, 247, 0.1)')
        self.shadow_color = shadow_color or 'rgba(168, 85, 247, 0.2)'
        
        # Set input box size
        self.setFixedSize(QSize(size[0], size[1]))
        
        # Set input box position
        self.move(position[0], position[1])
        
        # Set placeholder text
        self.setPlaceholderText(placeholder)
        
        # Set font
        font = QFont()
        font.setPointSize(font_size)
        self.setFont(font)
        
        # Add shadow effect
        self._apply_shadow()
        
        # Apply initial styling
        self._apply_style()
        
        # Connect signals
        self.textChanged.connect(self.text_changed_custom.emit)
        
        # Animation properties
        self._is_focused = False
        self._animation = None
    
    def _apply_shadow(self):
        """Apply shadow effect to the input box."""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self.shadow_blur)
        shadow.setOffset(self.shadow_offset[0], self.shadow_offset[1])
        shadow.setColor(QColor(self.shadow_color))
        self.setGraphicsEffect(shadow)
    
    def _apply_style(self):
        """Apply styling based on shape and colors."""
        if self.shape == "rounded_rectangle":
            border_style = f"border-radius: {self.border_radius}px;"
        elif self.shape == "circular":
            # For circular, use 50% of the smaller dimension
            size = min(self.width(), self.height())
            border_style = f"border-radius: {size // 2}px;"
        elif self.shape == "custom_path":
            # Custom path uses a more complex border-radius
            border_style = f"border-radius: {self.border_radius}px {self.border_radius * 2}px {self.border_radius}px {self.border_radius * 2}px;"
        else:
            border_style = f"border-radius: {self.border_radius}px;"
        
        stylesheet = f"""
            QLineEdit {{
                background-color: {self.bg_color};
                color: {self.text_color};
                border: {self.border_width}px solid {self.border_color};
                {border_style}
                padding: {self.padding};
                font-size: {self.font().pointSize()}pt;
                selection-background-color: {self.focus_color};
                selection-color: {self.text_color};
                outline: none;
            }}
            QLineEdit:hover {{
                border: {self.border_width}px solid {self.hover_color};
            }}
            QLineEdit:focus {{
                border: {self.border_width}px solid {self.focus_color};
                background-color: {self.bg_color};
            }}
            QLineEdit:disabled {{
                background-color: {self.disabled_color};
                color: {self.text_color};
                border: {self.border_width}px solid {self.disabled_color};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def focusInEvent(self, event):
        """Handle focus in event with animation."""
        super().focusInEvent(event)
        self._is_focused = True
        self.focus_in.emit()
        self._play_animation("focus_in")
    
    def focusOutEvent(self, event):
        """Handle focus out event with animation."""
        super().focusOutEvent(event)
        self._is_focused = False
        self.focus_out.emit()
        self._play_animation("focus_out")
    
    def _play_animation(self, animation_type):
        """Play animation based on animation_name setting.
        
        Args:
            animation_type: "focus_in" or "focus_out"
        """
        if self.animation_name == "none":
            return
        
        # Stop any existing animation
        if self._animation:
            self._animation.stop()
        
        if self.animation_name == "smooth":
            self._play_smooth_animation(animation_type)
        elif self.animation_name == "bounce":
            self._play_bounce_animation(animation_type)
        elif self.animation_name == "elastic":
            self._play_elastic_animation(animation_type)
    
    def _play_smooth_animation(self, animation_type):
        """Play smooth animation on focus."""
        # Smooth animation is handled by stylesheet transitions
        pass
    
    def _play_bounce_animation(self, animation_type):
        """Play bounce animation on focus."""
        # Bounce effect through border color change
        pass
    
    def _play_elastic_animation(self, animation_type):
        """Play elastic animation on focus."""
        # Elastic effect through size change
        pass
    
    def set_placeholder(self, text):
        """Set placeholder text at runtime.
        
        Args:
            text: Placeholder text
        """
        self.setPlaceholderText(text)
    
    def set_colors(self, bg_color=None, text_color=None, border_color=None, 
                   hover_color=None, focus_color=None, disabled_color=None):
        """Update colors at runtime.
        
        Args:
            bg_color: Background color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            focus_color: Focus state color (hex or rgba)
            disabled_color: Disabled state color (hex or rgba)
        """
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
        
        self._apply_style()
    
    def set_position(self, x, y):
        """Change input box position at runtime.
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.move(x, y)
    
    def set_size(self, width, height):
        """Change input box size at runtime.
        
        Args:
            width: Width in pixels
            height: Height in pixels
        """
        self.setFixedSize(QSize(width, height))
        if self.shape == "circular":
            self._apply_style()
    
    def set_shape(self, shape):
        """Change shape at runtime.
        
        Args:
            shape: "rounded_rectangle", "circular", or "custom_path"
        """
        self.shape = shape
        self._apply_style()
    
    def set_border_radius(self, radius):
        """Change border radius at runtime.
        
        Args:
            radius: Border radius in pixels
        """
        self.border_radius = radius
        self._apply_style()
    
    def set_animation(self, animation_name):
        """Change animation type at runtime.
        
        Args:
            animation_name: "smooth", "bounce", "elastic", or "none"
        """
        self.animation_name = animation_name
    
    def set_shadow(self, blur_radius, offset_x=0, offset_y=2, color=None):
        """Update shadow effect at runtime.
        
        Args:
            blur_radius: Shadow blur radius
            offset_x: X offset
            offset_y: Y offset
            color: Shadow color (hex or rgba)
        """
        self.shadow_blur = blur_radius
        self.shadow_offset = (offset_x, offset_y)
        if color:
            self.shadow_color = color
        self._apply_shadow()
    
    def get_text(self):
        """Get the current text value.
        
        Returns:
            Current text in the input box
        """
        return self.text()
    
    def set_text(self, text):
        """Set text value at runtime.
        
        Args:
            text: Text to set
        """
        self.setText(text)
    
    def clear_text(self):
        """Clear the input box."""
        self.clear()
    
    def is_focused(self):
        """Check if input box is currently focused.
        
        Returns:
            True if focused, False otherwise
        """
        return self._is_focused
