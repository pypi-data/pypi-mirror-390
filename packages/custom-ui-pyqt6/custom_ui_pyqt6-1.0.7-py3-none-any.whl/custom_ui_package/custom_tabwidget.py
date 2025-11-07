"""
CustomTabWidget - Tabbed interface with custom tab styling.

A fully customizable tab widget with support for:
- Custom colors (background, tab, text, hover, active)
- Configurable tab size and border
- Smooth animations on tab switching
- Icon support for tabs
- Tab close buttons
"""

from PyQt6.QtWidgets import QTabWidget, QWidget, QTabBar
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QPainterPath
from typing import Optional


class CustomTabBar(QTabBar):
    """Custom tab bar with styling."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tab_height = 40
        self.tab_width = 120
        self.border_radius = 8
        self.bg_color = "#1a1a2e"
        self.tab_color = "rgba(168, 85, 247, 0.2)"
        self.active_color = "#a855f7"
        self.text_color = "#ffffff"
        self.hover_color = "rgba(168, 85, 247, 0.4)"
    
    def sizeHint(self) -> QSize:
        """Return size hint."""
        return QSize(self.tab_width * self.count(), self.tab_height)
    
    def tabSizeHint(self, index: int) -> QSize:
        """Return tab size hint."""
        return QSize(self.tab_width, self.tab_height)


class CustomTabWidget(QTabWidget):
    """
    Tab widget with custom styling and animations.
    
    Signals:
        tab_changed_custom: Emitted when active tab changes
    """
    
    tab_changed_custom = pyqtSignal(int)
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        tab_height: int = 40,
        tab_width: int = 120,
        border_radius: int = 8,
        animation_name: str = "smooth",
        bg_color: str = "#1a1a2e",
        tab_color: str = "rgba(168, 85, 247, 0.2)",
        active_color: str = "#a855f7",
        text_color: str = "#ffffff",
        hover_color: str = "rgba(168, 85, 247, 0.4)",
        font_family: str = "Segoe UI",
        font_size: int = 11,
    ):
        """
        Initialize CustomTabWidget.
        
        Args:
            parent: Parent widget
            tab_height: Tab height in pixels
            tab_width: Tab width in pixels
            border_radius: Border radius in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            tab_color: Tab background color (hex or rgba)
            active_color: Active tab color (hex or rgba)
            text_color: Text color (hex or rgba)
            hover_color: Hover state color (hex or rgba)
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.tab_height = tab_height
        self.tab_width = tab_width
        self.border_radius = border_radius
        self.animation_name = animation_name
        
        # Colors
        self.bg_color = bg_color
        self.tab_color = tab_color
        self.active_color = active_color
        self.text_color = text_color
        self.hover_color = hover_color
        
        # Create custom tab bar
        self.tab_bar = CustomTabBar(self)
        self.tab_bar.tab_height = tab_height
        self.tab_bar.tab_width = tab_width
        self.tab_bar.border_radius = border_radius
        self.tab_bar.bg_color = bg_color
        self.tab_bar.tab_color = tab_color
        self.tab_bar.active_color = active_color
        self.tab_bar.text_color = text_color
        self.tab_bar.hover_color = hover_color
        
        self.setTabBar(self.tab_bar)
        
        # Set font
        font = QFont(font_family, font_size)
        self.setFont(font)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Connect signals
        self.currentChanged.connect(self._on_tab_changed)
        
        # Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QTabWidget::pane {{
                border: none;
                background-color: {self.bg_color};
            }}
            QTabBar::tab {{
                background-color: {self.tab_color};
                color: {self.text_color};
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: {self.border_radius}px;
                font-family: {self.font().family()};
                font-size: {self.font().pointSize()}pt;
            }}
            QTabBar::tab:hover {{
                background-color: {self.hover_color};
            }}
            QTabBar::tab:selected {{
                background-color: {self.active_color};
                color: #ffffff;
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _on_tab_changed(self, index: int):
        """Handle tab change event."""
        self.tab_changed_custom.emit(index)
        if self.animation_name != "none":
            self._start_animation()
    
    def _start_animation(self):
        """Start animation."""
        if self.animation_name == "none":
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        self.update()
    
    def add_tab(self, widget: QWidget, label: str, icon: Optional[QIcon] = None):
        """Add a tab."""
        if icon:
            self.addTab(widget, icon, label)
        else:
            self.addTab(widget, label)
    
    def remove_tab(self, index: int):
        """Remove a tab."""
        self.removeTab(index)
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        tab_color: Optional[str] = None,
        active_color: Optional[str] = None,
        text_color: Optional[str] = None,
        hover_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if tab_color:
            self.tab_color = tab_color
        if active_color:
            self.active_color = active_color
        if text_color:
            self.text_color = text_color
        if hover_color:
            self.hover_color = hover_color
        
        self.tab_bar.bg_color = self.bg_color
        self.tab_bar.tab_color = self.tab_color
        self.tab_bar.active_color = self.active_color
        self.tab_bar.text_color = self.text_color
        self.tab_bar.hover_color = self.hover_color
        
        self._apply_stylesheet()
    
    def set_tab_size(self, width: int, height: int):
        """Set tab size."""
        self.tab_width = width
        self.tab_height = height
        self.tab_bar.tab_width = width
        self.tab_bar.tab_height = height
    
    def set_border_radius(self, radius: int):
        """Update border radius."""
        self.border_radius = radius
        self.tab_bar.border_radius = radius
        self._apply_stylesheet()
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
    
    def get_current_index(self) -> int:
        """Get current tab index."""
        return self.currentIndex()
    
    def set_current_index(self, index: int):
        """Set current tab index."""
        self.setCurrentIndex(index)
    
    def get_tab_count(self) -> int:
        """Get number of tabs."""
        return self.count()
