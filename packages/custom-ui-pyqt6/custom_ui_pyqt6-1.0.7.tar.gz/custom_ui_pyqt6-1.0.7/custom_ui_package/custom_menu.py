"""
Custom Menu Component for PyQt6
A modern, customizable menu with glassmorphism effects and smooth animations
"""

from PyQt6.QtWidgets import QMenu, QWidget, QVBoxLayout
from PyQt6.QtGui import QAction, QFont, QIcon, QColor
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtCore import pyqtSignal

from .colors.color_palette import get_global_color


class CustomMenu(QMenu):
    """
    A modern custom menu with glassmorphism effects and smooth animations.
    
    Features:
    - Customizable colors (background, text, hover, border)
    - Smooth hover animations
    - Icon support for menu items
    - Separator support
    - Customizable font and size
    - Glassmorphism effects
    - Adjustable border radius and opacity
    
    Args:
        parent (QWidget, optional): Parent widget
        title (str): Menu title (default: '')
        bg_color (str): Background color (hex or rgba). Default: global surface color
        text_color (str): Text color (hex or rgba). Default: global text color
        hover_color (str): Hover background color. Default: global primary color
        border_color (str): Border color. Default: global border color
        border_width (int): Border width in pixels. Default: 1
        border_radius (int): Border radius in pixels. Default: 8
        font_size (int): Font size in pixels. Default: 11
        font_family (str): Font family. Default: 'Segoe UI'
        bold (bool): Bold font. Default: False
        opacity (float): Background opacity (0-1). Default: 0.95
        icon_size (int): Icon size in pixels. Default: 16
        item_height (int): Menu item height in pixels. Default: 32
        item_padding (int): Item padding in pixels. Default: 10
        animation_duration (int): Animation duration in ms. Default: 150
        
    Signals:
        item_hovered(QAction): Emitted when item is hovered
        item_clicked(QAction): Emitted when item is clicked
        
    Examples:
        # Basic menu
        menu = CustomMenu(title='File')
        menu.add_item('New', icon_path='path/to/icon.png')
        menu.add_item('Open')
        menu.add_separator()
        menu.add_item('Exit')
        
        # Custom colors
        menu = CustomMenu(
            title='Edit',
            bg_color='#1a0f2e',
            text_color='#f3e8ff',
            hover_color='#a855f7',
            border_color='rgba(168, 85, 247, 0.3)'
        )
        
        # Custom styling
        menu = CustomMenu(
            title='View',
            font_size=12,
            font_family='Arial',
            bold=True,
            border_radius=12,
            item_height=40
        )
    """
    
    # Custom signals
    item_hovered = pyqtSignal(QAction)
    item_clicked = pyqtSignal(QAction)
    
    def __init__(self, parent=None, title='', 
                 bg_color=None, text_color=None, hover_color=None, border_color=None,
                 border_width=1, border_radius=8, font_size=11, font_family='Segoe UI',
                 bold=False, opacity=0.95, icon_size=16, item_height=32, 
                 item_padding=10, animation_duration=150):
        super().__init__(title, parent)
        
        # Store parameters
        self.bg_color = bg_color or get_global_color('surface', '#2d1b4e')
        self.text_color = text_color or get_global_color('text', '#f3e8ff')
        self.hover_color = hover_color or get_global_color('primary', '#a855f7')
        self.border_color = border_color or get_global_color('border', 'rgba(168, 85, 247, 0.3)')
        self.border_width = border_width
        self.border_radius = border_radius
        self.font_size = font_size
        self.font_family = font_family
        self.bold = bold
        self.opacity = opacity
        self.icon_size = icon_size
        self.item_height = item_height
        self.item_padding = item_padding
        self.animation_duration = animation_duration
        
        # Store actions for tracking
        self.menu_items = []
        
        # Apply styling
        self._apply_stylesheet()
        
        # Connect signals
        self.hovered.connect(self._on_item_hovered)
        self.triggered.connect(self._on_item_clicked)
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet to menu"""
        # Convert opacity to alpha value (0-255)
        alpha = int(255 * self.opacity)
        
        # Extract RGB from bg_color if it's hex
        if self.bg_color.startswith('#'):
            hex_color = self.bg_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            bg_rgba = f"rgba({r}, {g}, {b}, {alpha})"
        else:
            bg_rgba = self.bg_color
        
        # Font weight
        font_weight = 'bold' if self.bold else 'normal'
        
        stylesheet = f"""
            QMenu {{
                background-color: {bg_rgba};
                color: {self.text_color};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.border_radius}px;
                padding: 5px 0px;
                font-family: {self.font_family};
                font-size: {self.font_size}px;
                font-weight: {font_weight};
            }}
            
            QMenu::item {{
                padding: {self.item_padding}px 15px;
                height: {self.item_height}px;
                background-color: transparent;
                margin: 2px 5px;
                border-radius: {self.border_radius - 2}px;
            }}
            
            QMenu::item:selected {{
                background-color: {self.hover_color};
                color: {self.text_color};
            }}
            
            QMenu::item:pressed {{
                background-color: {self.hover_color};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {self.border_color};
                margin: 5px 0px;
            }}
            
            QMenu::icon {{
                margin-right: 10px;
            }}
        """
        
        self.setStyleSheet(stylesheet)
    
    def add_item(self, text, callback=None, icon_path=None, shortcut=None, 
                 enabled=True, checkable=False, checked=False):
        """
        Add a menu item with optional icon and callback.
        
        Args:
            text (str): Item text
            callback (callable, optional): Function to call when item is clicked
            icon_path (str, optional): Path to icon file
            shortcut (str, optional): Keyboard shortcut (e.g., 'Ctrl+N')
            enabled (bool): Item enabled state. Default: True
            checkable (bool): Make item checkable. Default: False
            checked (bool): Initial checked state. Default: False
            
        Returns:
            QAction: The created action
        """
        action = QAction(text, self)
        
        # Set icon if provided
        if icon_path:
            icon = QIcon(icon_path)
            action.setIcon(icon)
        
        # Set shortcut if provided
        if shortcut:
            action.setShortcut(shortcut)
        
        # Set enabled state
        action.setEnabled(enabled)
        
        # Set checkable state
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        
        # Connect callback if provided
        if callback:
            action.triggered.connect(callback)
        
        # Add action to menu
        self.addAction(action)
        self.menu_items.append(action)
        
        return action
    
    def add_separator(self):
        """Add a separator line to the menu"""
        separator = self.addSeparator()
        return separator
    
    def add_submenu(self, title, parent=None):
        """
        Add a submenu to the menu.
        
        Args:
            title (str): Submenu title
            parent (CustomMenu, optional): Parent menu for the submenu
            
        Returns:
            CustomMenu: The created submenu
        """
        submenu = CustomMenu(
            parent=parent or self,
            title=title,
            bg_color=self.bg_color,
            text_color=self.text_color,
            hover_color=self.hover_color,
            border_color=self.border_color,
            border_width=self.border_width,
            border_radius=self.border_radius,
            font_size=self.font_size,
            font_family=self.font_family,
            bold=self.bold,
            opacity=self.opacity,
            icon_size=self.icon_size,
            item_height=self.item_height,
            item_padding=self.item_padding,
            animation_duration=self.animation_duration
        )
        
        self.addMenu(submenu)
        return submenu
    
    def update_colors(self, bg_color=None, text_color=None, hover_color=None, border_color=None):
        """
        Update menu colors at runtime.
        
        Args:
            bg_color (str, optional): New background color
            text_color (str, optional): New text color
            hover_color (str, optional): New hover color
            border_color (str, optional): New border color
        """
        if bg_color:
            self.bg_color = bg_color
        if text_color:
            self.text_color = text_color
        if hover_color:
            self.hover_color = hover_color
        if border_color:
            self.border_color = border_color
        
        self._apply_stylesheet()
    
    def update_styling(self, font_size=None, font_family=None, bold=None, 
                      border_radius=None, item_height=None, item_padding=None):
        """
        Update menu styling at runtime.
        
        Args:
            font_size (int, optional): New font size
            font_family (str, optional): New font family
            bold (bool, optional): New bold state
            border_radius (int, optional): New border radius
            item_height (int, optional): New item height
            item_padding (int, optional): New item padding
        """
        if font_size is not None:
            self.font_size = font_size
        if font_family:
            self.font_family = font_family
        if bold is not None:
            self.bold = bold
        if border_radius is not None:
            self.border_radius = border_radius
        if item_height is not None:
            self.item_height = item_height
        if item_padding is not None:
            self.item_padding = item_padding
        
        self._apply_stylesheet()
    
    def set_opacity(self, opacity):
        """
        Set menu background opacity.
        
        Args:
            opacity (float): Opacity value (0-1)
        """
        self.opacity = max(0, min(1, opacity))
        self._apply_stylesheet()
    
    def clear_items(self):
        """Clear all menu items"""
        self.clear()
        self.menu_items.clear()
    
    def get_item_by_text(self, text):
        """
        Get menu item by text.
        
        Args:
            text (str): Item text to search for
            
        Returns:
            QAction: The action if found, None otherwise
        """
        for action in self.menu_items:
            if action.text() == text:
                return action
        return None
    
    def _on_item_hovered(self, action):
        """Handle item hover event"""
        self.item_hovered.emit(action)
    
    def _on_item_clicked(self, action):
        """Handle item click event"""
        self.item_clicked.emit(action)
    
    def enable_item(self, text, enabled=True):
        """
        Enable or disable a menu item by text.
        
        Args:
            text (str): Item text
            enabled (bool): Enable state
        """
        action = self.get_item_by_text(text)
        if action:
            action.setEnabled(enabled)
    
    def check_item(self, text, checked=True):
        """
        Check or uncheck a checkable menu item by text.
        
        Args:
            text (str): Item text
            checked (bool): Checked state
        """
        action = self.get_item_by_text(text)
        if action and action.isCheckable():
            action.setChecked(checked)
    
    def is_item_checked(self, text):
        """
        Check if a menu item is checked.
        
        Args:
            text (str): Item text
            
        Returns:
            bool: True if checked, False otherwise
        """
        action = self.get_item_by_text(text)
        if action and action.isCheckable():
            return action.isChecked()
        return False
