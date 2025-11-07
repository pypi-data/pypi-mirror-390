"""
CustomAccordion - Collapsible panels/sections.

A fully customizable accordion widget with support for:
- Custom colors (header, content, border)
- Smooth expand/collapse animations
- Multiple panels
- Icon support
- Configurable header size
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QFont, QColor, QIcon
from typing import Optional, List


class AccordionItem(QWidget):
    """Single accordion item with header and content."""
    
    expanded_changed = pyqtSignal(bool)
    
    def __init__(
        self,
        title: str = "Item",
        content_widget: Optional[QWidget] = None,
        header_height: int = 40,
        bg_color: str = "#1a1a2e",
        header_color: str = "rgba(168, 85, 247, 0.2)",
        content_color: str = "#0f0f1e",
        text_color: str = "#ffffff",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        hover_color: str = "rgba(168, 85, 247, 0.4)",
        animation_name: str = "smooth",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """Initialize accordion item."""
        super().__init__()
        
        # Store properties
        self.title = title
        self.header_height = header_height
        self.animation_name = animation_name
        self.is_expanded = False
        
        # Colors
        self.bg_color = bg_color
        self.header_color = header_color
        self.content_color = content_color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Create header button
        self.header_button = QPushButton(f"▶ {title}")
        self.header_button.setFixedHeight(header_height)
        self.header_button.setFont(QFont(font_family, font_size))
        self.header_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {header_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 0px;
                padding: 0px 12px;
                text-align: left;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """)
        self.header_button.clicked.connect(self._toggle)
        self.layout.addWidget(self.header_button)
        
        # Create content frame
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {content_color};
                border: 1px solid {border_color};
                border-top: none;
            }}
        """)
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(12, 12, 12, 12)
        
        if content_widget:
            self.content_layout.addWidget(content_widget)
        
        self.content_frame.setMaximumHeight(0)
        self.layout.addWidget(self.content_frame)
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
        self.target_height = 0
    
    def _toggle(self):
        """Toggle expanded state."""
        self.is_expanded = not self.is_expanded
        self._start_animation()
        self.expanded_changed.emit(self.is_expanded)
    
    def _start_animation(self):
        """Start expand/collapse animation."""
        if self.animation_name == "none":
            self._update_height()
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        self._update_height()
    
    def _update_height(self):
        """Update content frame height."""
        if self.is_expanded:
            self.target_height = self.content_frame.sizeHint().height()
            # Update arrow
            self.header_button.setText(f"▼ {self.title}")
        else:
            self.target_height = 0
            # Update arrow
            self.header_button.setText(f"▶ {self.title}")
        
        current_height = self.content_frame.maximumHeight()
        new_height = int(current_height + (self.target_height - current_height) * self.animation_progress)
        self.content_frame.setMaximumHeight(new_height)
    
    def set_content(self, widget: QWidget):
        """Set content widget."""
        # Clear existing
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget().deleteLater()
        
        # Add new
        self.content_layout.addWidget(widget)
    
    def expand(self):
        """Expand the item."""
        if not self.is_expanded:
            self._toggle()
    
    def collapse(self):
        """Collapse the item."""
        if self.is_expanded:
            self._toggle()


class CustomAccordion(QWidget):
    """
    Accordion widget with multiple collapsible items.
    
    Signals:
        item_expanded: Emitted when item is expanded
        item_collapsed: Emitted when item is collapsed
    """
    
    item_expanded = pyqtSignal(int)
    item_collapsed = pyqtSignal(int)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        header_height: int = 40,
        animation_name: str = "smooth",
        bg_color: str = "#1a1a2e",
        header_color: str = "rgba(168, 85, 247, 0.2)",
        content_color: str = "#0f0f1e",
        text_color: str = "#ffffff",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        hover_color: str = "rgba(168, 85, 247, 0.4)",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomAccordion.
        
        Args:
            parent: Parent widget
            header_height: Header height in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            header_color: Header color (hex or rgba)
            content_color: Content color (hex or rgba)
            text_color: Text color (hex or rgba)
            border_color: Border color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.header_height = header_height
        self.animation_name = animation_name
        
        # Colors
        self.bg_color = bg_color
        self.header_color = header_color
        self.content_color = content_color
        self.text_color = text_color
        self.border_color = border_color
        self.hover_color = hover_color
        self.font_family = font_family
        self.font_size = font_size
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Items list
        self.items: List[AccordionItem] = []
        
        # Apply stylesheet
        self._apply_stylesheet()
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QWidget {{
                background-color: {self.bg_color};
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def add_item(self, title: str, content_widget: Optional[QWidget] = None) -> AccordionItem:
        """Add accordion item."""
        item = AccordionItem(
            title=title,
            content_widget=content_widget,
            header_height=self.header_height,
            bg_color=self.bg_color,
            header_color=self.header_color,
            content_color=self.content_color,
            text_color=self.text_color,
            border_color=self.border_color,
            hover_color=self.hover_color,
            animation_name=self.animation_name,
            font_family=self.font_family,
            font_size=self.font_size,
        )
        
        index = len(self.items)
        item.expanded_changed.connect(
            lambda expanded: self._on_item_expanded(index, expanded)
        )
        
        self.items.append(item)
        self.layout.addWidget(item)
        
        return item
    
    def _on_item_expanded(self, index: int, expanded: bool):
        """Handle item expansion."""
        if expanded:
            self.item_expanded.emit(index)
        else:
            self.item_collapsed.emit(index)
    
    def expand_item(self, index: int):
        """Expand item at index."""
        if 0 <= index < len(self.items):
            self.items[index].expand()
    
    def collapse_item(self, index: int):
        """Collapse item at index."""
        if 0 <= index < len(self.items):
            self.items[index].collapse()
    
    def expand_all(self):
        """Expand all items."""
        for item in self.items:
            item.expand()
    
    def collapse_all(self):
        """Collapse all items."""
        for item in self.items:
            item.collapse()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        header_color: Optional[str] = None,
        content_color: Optional[str] = None,
        text_color: Optional[str] = None,
        border_color: Optional[str] = None,
        hover_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if header_color:
            self.header_color = header_color
        if content_color:
            self.content_color = content_color
        if text_color:
            self.text_color = text_color
        if border_color:
            self.border_color = border_color
        if hover_color:
            self.hover_color = hover_color
        
        self._apply_stylesheet()
    
    def get_item_count(self) -> int:
        """Get number of items."""
        return len(self.items)
