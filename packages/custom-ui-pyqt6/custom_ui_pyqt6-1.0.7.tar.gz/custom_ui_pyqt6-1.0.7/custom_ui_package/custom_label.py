"""Custom Qt label with configurable parameters."""

from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from .colors.color_palette import get_global_color


class CustomLabel(QLabel):
    """A custom QLabel with configurable parameters and global color palette support."""
    
    def __init__(self, parent=None, text="Label", size=(100, 30), position=(0, 0), font_size=10, bold=False, color=None):
        """Initialize the custom label.
        
        Args:
            parent: Parent widget
            text: Label text
            size: Tuple of (width, height)
            position: Tuple of (x, y)
            font_size: Font size for the label text
            bold: Whether text should be bold
            color: Text color (hex or rgba). Uses global palette 'text' color if None
        """
        super().__init__(text, parent)
        
        # Set label size
        self.setFixedSize(QSize(size[0], size[1]))
        
        # Set label position
        self.move(position[0], position[1])
        
        # Set font size and weight
        font = QFont()
        font.setPointSize(font_size)
        if bold:
            font.setBold(True)
        self.setFont(font)
        
        # Store color
        self.color = color or get_global_color('text', '#e8f0ff')
        
        # Disable focus and text selection
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        
        # Disable text selection highlighting
        self.setAutoFillBackground(False)
        
        # Apply styling
        self._apply_style()
        
        # Show the label
        self.show()
    
    def _apply_style(self):
        """Apply styling to label"""
        self.setStyleSheet(f"""
            QLabel {{
                color: {self.color};
                background: transparent;
                margin: 0px;
                padding: 0px;
                selection-background-color: transparent;
                selection-color: {self.color};
            }}
        """)
    
    def set_position(self, x, y):
        """Change label position at runtime
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.move(x, y)
