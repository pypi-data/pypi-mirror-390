"""
CustomBadge - Status badges/chips/tags widget.

A fully customizable badge widget with support for:
- Custom colors (background, text, border)
- Multiple shape options (rounded, pill, square)
- Configurable size and border
- Close button support
- Icon support
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class CustomBadge(QWidget):
    """
    Badge widget with custom styling.
    
    Signals:
        closed_custom: Emitted when badge is closed
        clicked_custom: Emitted when badge is clicked
    """
    
    closed_custom = pyqtSignal()
    clicked_custom = pyqtSignal()
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        text: str = "Badge",
        shape: str = "pill",
        size: str = "medium",
        closable: bool = False,
        animation_name: str = "smooth",
        bg_color: str = "#a855f7",
        text_color: str = "#ffffff",
        border_color: str = "rgba(168, 85, 247, 0.5)",
        hover_color: str = "#c084fc",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomBadge.
        
        Args:
            parent: Parent widget
            text: Badge text
            shape: Shape type - 'rounded', 'pill', 'square'
            size: Size type - 'small', 'medium', 'large'
            closable: Show close button
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.shape = shape
        self.size = size
        self.closable = closable
        self.animation_name = animation_name
        
        # Colors
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.current_bg_color = bg_color
        
        # State tracking
        self.is_hovered = False
        
        # Determine size
        size_map = {"small": 24, "medium": 32, "large": 40}
        self.height = size_map.get(size, 32)
        
        # Create layout
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 4, 12 if not closable else 4, 4)
        self.layout.setSpacing(4)
        
        # Create text label
        self.text_label = QLabel(text)
        font = QFont(font_family, font_size)
        self.text_label.setFont(font)
        self.text_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        self.layout.addWidget(self.text_label)
        
        # Create close button if needed
        if closable:
            self.close_button = QPushButton("×")
            self.close_button.setFixedSize(20, 20)
            self.close_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: none;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    color: {hover_color};
                }}
            """)
            self.close_button.clicked.connect(self._on_close)
            self.layout.addWidget(self.close_button)
        
        # Set size
        self.setFixedHeight(self.height)
        self.adjustSize()
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        border_radius = self.height // 2 if self.shape == "pill" else (
            self.height // 4 if self.shape == "rounded" else 0
        )
        
        stylesheet = f"""
            QWidget {{
                background-color: {self.current_bg_color};
                border: 1px solid {self.border_color};
                border-radius: {border_radius}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_close(self):
        """Handle close button click."""
        self.closed_custom.emit()
        self.deleteLater()
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        super().mousePressEvent(event)
        self.clicked_custom.emit()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.is_hovered = True
        self._update_color()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.is_hovered = False
        self._update_color()
    
    def _update_color(self):
        """Update color based on state."""
        if self.is_hovered:
            self.current_bg_color = self.hover_color
        else:
            self.current_bg_color = self.bg_color
        
        self._apply_stylesheet()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_color: Optional[str] = None,
        hover_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
            self.current_bg_color = bg_color
        if text_color:
            self.text_color = text_color
            self.text_label.setStyleSheet(f"color: {text_color}; background: transparent;")
        if border_color:
            self.border_color = border_color
        if hover_color:
            self.hover_color = hover_color
        
        self._apply_stylesheet()
    
    def set_text(self, text: str):
        """Set badge text."""
        self.text_label.setText(text)
        self.adjustSize()
    
    def get_text(self) -> str:
        """Get badge text."""
        return self.text_label.text()
    
    def set_shape(self, shape: str):
        """Change shape type."""
        self.shape = shape
        self._apply_stylesheet()
    
    def set_size(self, size: str):
        """Change size type."""
        self.size = size
        size_map = {"small": 24, "medium": 32, "large": 40}
        self.height = size_map.get(size, 32)
        self.setFixedHeight(self.height)
        self._apply_stylesheet()
    
    def set_closable(self, closable: bool):
        """Set closable state."""
        self.closable = closable
        if closable and not hasattr(self, 'close_button'):
            self.close_button = QPushButton("×")
            self.close_button.setFixedSize(20, 20)
            self.close_button.clicked.connect(self._on_close)
            self.layout.addWidget(self.close_button)
