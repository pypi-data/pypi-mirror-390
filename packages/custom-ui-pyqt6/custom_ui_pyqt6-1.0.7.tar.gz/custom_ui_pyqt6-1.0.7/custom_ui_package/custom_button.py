"""Custom Qt button with configurable parameters."""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from .colors.color_palette import get_global_color


class CustomButton(QPushButton):
    """A custom QPushButton with configurable parameters, colors, and styling options."""
    
    def __init__(self, parent=None, title="Button", size=(100, 30), position=(0, 0), font_size=10, color=None, bg_color=None, bold=False):
        """Initialize the custom button.
        
        Args:
            parent: Parent widget
            title: Button text
            size: Tuple of (width, height)
            position: Tuple of (x, y)
            font_size: Font size for the button text
            color: Text color (hex or rgba). Uses global palette 'text' color if None
            bg_color: Background color (hex or rgba). Uses global palette 'primary' color if None
            bold: Whether text should be bold
        """
        super().__init__(title, parent)
        
        # Store custom colors
        self.color = color or get_global_color('text', '#ffffff')
        self.bg_color = bg_color or get_global_color('primary', '#6366f1')
        
        # Set button size
        self.setFixedSize(QSize(size[0], size[1]))
        
        # Set button position
        self.move(position[0], position[1])
        
        # Set font size and weight
        font = QFont()
        font.setPointSize(font_size)
        if bold:
            font.setBold(True)
        self.setFont(font)
        
        # Apply styling
        self._apply_style()
    
    def _apply_style(self):
        """Apply styling using custom or global color palette"""
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: {self.bg_color};
                color: {self.color};
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: 600;
                outline: none;
                margin: 0px;
            }}
            QPushButton:hover {{
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                opacity: 0.6;
            }}
            QPushButton:focus {{
                outline: none;
            }}
        """)
    
    def set_position(self, x, y):
        """Change button position at runtime
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.move(x, y)
