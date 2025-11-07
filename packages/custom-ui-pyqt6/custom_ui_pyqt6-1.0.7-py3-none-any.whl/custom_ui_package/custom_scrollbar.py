"""
Custom Scrollbar Component for PyQt6
A modern, customizable scrollbar with glassmorphism effects
"""

from PyQt6.QtWidgets import QScrollBar, QWidget
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QSize

from .colors.color_palette import get_global_color


class CustomScrollBar(QScrollBar):
    """
    A modern custom scrollbar with glassmorphism effects and smooth styling.
    
    Features:
    - Customizable colors (handle, background, hover)
    - Smooth hover animations
    - Adjustable width/height
    - Border radius support
    - Opacity control
    - Works for both vertical and horizontal scrollbars
    
    Args:
        orientation (Qt.Orientation): Qt.Vertical or Qt.Horizontal
        parent (QWidget, optional): Parent widget
        handle_color (str): Scrollbar handle color (hex or rgba). Default: global primary
        handle_hover_color (str): Handle hover color. Default: lighter primary
        background_color (str): Background color. Default: global surface
        border_color (str): Border color. Default: global border
        border_width (int): Border width in pixels. Default: 1
        border_radius (int): Border radius in pixels. Default: 6
        handle_width (int): Handle width in pixels (for vertical). Default: 8
        handle_height (int): Handle height in pixels (for horizontal). Default: 8
        opacity (float): Background opacity (0-1). Default: 0.9
        hover_opacity (float): Hover opacity (0-1). Default: 1.0
        min_handle_size (int): Minimum handle size in pixels. Default: 20
        
    Examples:
        # Basic vertical scrollbar
        scrollbar = CustomScrollBar(Qt.Orientation.Vertical)
        
        # Custom colors
        scrollbar = CustomScrollBar(
            Qt.Orientation.Vertical,
            handle_color='#a855f7',
            handle_hover_color='#d946ef',
            background_color='#1a0f2e',
            border_color='rgba(168, 85, 247, 0.3)'
        )
        
        # Custom styling
        scrollbar = CustomScrollBar(
            Qt.Orientation.Vertical,
            handle_width=12,
            border_radius=8,
            opacity=0.8
        )
    """
    
    def __init__(self, orientation=Qt.Orientation.Vertical, parent=None,
                 handle_color=None, handle_hover_color=None, background_color=None,
                 border_color=None, border_width=1, border_radius=6, 
                 handle_width=8, handle_height=8, opacity=0.9, hover_opacity=1.0,
                 min_handle_size=20):
        super().__init__(orientation, parent)
        
        # Store parameters
        self.handle_color = handle_color or get_global_color('primary', '#a855f7')
        self.handle_hover_color = handle_hover_color or self._lighten_color(self.handle_color)
        self.background_color = background_color or get_global_color('surface', '#2d1b4e')
        self.border_color = border_color or get_global_color('border', 'rgba(168, 85, 247, 0.3)')
        self.border_width = border_width
        self.border_radius = border_radius
        self.handle_width = handle_width
        self.handle_height = handle_height
        self.opacity = opacity
        self.hover_opacity = hover_opacity
        self.min_handle_size = min_handle_size
        self.is_hovered = False
        
        # Set scrollbar size
        if orientation == Qt.Orientation.Vertical:
            self.setFixedWidth(handle_width + 4)
        else:
            self.setFixedHeight(handle_height + 4)
        
        # Apply styling
        self._apply_stylesheet()
        
        # Connect signals
        self.sliderMoved.connect(self._on_slider_moved)
    
    def _lighten_color(self, color):
        """Lighten a color for hover effect"""
        if color.startswith('#'):
            hex_color = color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            # Lighten by increasing RGB values
            r = min(255, int(r * 1.3))
            g = min(255, int(g * 1.3))
            b = min(255, int(b * 1.3))
            return f"#{r:02x}{g:02x}{b:02x}"
        return color
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet to scrollbar"""
        # Convert opacity to alpha
        bg_alpha = int(255 * self.opacity)
        handle_alpha = int(255 * self.hover_opacity)
        
        # Convert colors to RGBA if needed
        if self.background_color.startswith('#'):
            hex_color = self.background_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            bg_rgba = f"rgba({r}, {g}, {b}, {bg_alpha})"
        else:
            bg_rgba = self.background_color
        
        if self.handle_color.startswith('#'):
            hex_color = self.handle_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            handle_rgba = f"rgba({r}, {g}, {b}, {handle_alpha})"
        else:
            handle_rgba = self.handle_color
        
        # Handle hover color
        if self.handle_hover_color.startswith('#'):
            hex_color = self.handle_hover_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            hover_rgba = f"rgba({r}, {g}, {b}, {handle_alpha})"
        else:
            hover_rgba = self.handle_hover_color
        
        stylesheet = f"""
            QScrollBar {{
                background-color: {bg_rgba};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.border_radius}px;
                margin: 0px;
                padding: 0px;
            }}
            
            QScrollBar::handle {{
                background-color: {handle_rgba};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.border_radius}px;
                min-height: {self.min_handle_size}px;
                min-width: {self.min_handle_size}px;
                margin: 2px;
            }}
            
            QScrollBar::handle:hover {{
                background-color: {hover_rgba};
                border: {self.border_width}px solid {self.handle_hover_color};
            }}
            
            QScrollBar::handle:pressed {{
                background-color: {hover_rgba};
            }}
            
            QScrollBar::add-line {{
                border: none;
                background: none;
            }}
            
            QScrollBar::sub-line {{
                border: none;
                background: none;
            }}
            
            QScrollBar::add-page {{
                background: none;
            }}
            
            QScrollBar::sub-page {{
                background: none;
            }}
            
            QScrollBar::up-arrow {{
                background: none;
            }}
            
            QScrollBar::down-arrow {{
                background: none;
            }}
            
            QScrollBar::left-arrow {{
                background: none;
            }}
            
            QScrollBar::right-arrow {{
                background: none;
            }}
        """
        
        self.setStyleSheet(stylesheet)
    
    def update_colors(self, handle_color=None, handle_hover_color=None, 
                     background_color=None, border_color=None):
        """
        Update scrollbar colors at runtime.
        
        Args:
            handle_color (str, optional): New handle color
            handle_hover_color (str, optional): New hover color
            background_color (str, optional): New background color
            border_color (str, optional): New border color
        """
        if handle_color:
            self.handle_color = handle_color
        if handle_hover_color:
            self.handle_hover_color = handle_hover_color
        if background_color:
            self.background_color = background_color
        if border_color:
            self.border_color = border_color
        
        self._apply_stylesheet()
    
    def update_styling(self, handle_width=None, handle_height=None, 
                      border_radius=None, opacity=None, hover_opacity=None):
        """
        Update scrollbar styling at runtime.
        
        Args:
            handle_width (int, optional): New handle width
            handle_height (int, optional): New handle height
            border_radius (int, optional): New border radius
            opacity (float, optional): New background opacity
            hover_opacity (float, optional): New hover opacity
        """
        if handle_width is not None:
            self.handle_width = handle_width
            if self.orientation() == Qt.Orientation.Vertical:
                self.setFixedWidth(handle_width + 4)
        
        if handle_height is not None:
            self.handle_height = handle_height
            if self.orientation() == Qt.Orientation.Horizontal:
                self.setFixedHeight(handle_height + 4)
        
        if border_radius is not None:
            self.border_radius = border_radius
        
        if opacity is not None:
            self.opacity = max(0, min(1, opacity))
        
        if hover_opacity is not None:
            self.hover_opacity = max(0, min(1, hover_opacity))
        
        self._apply_stylesheet()
    
    def set_opacity(self, opacity):
        """
        Set scrollbar background opacity.
        
        Args:
            opacity (float): Opacity value (0-1)
        """
        self.opacity = max(0, min(1, opacity))
        self._apply_stylesheet()
    
    def set_hover_opacity(self, opacity):
        """
        Set scrollbar handle hover opacity.
        
        Args:
            opacity (float): Opacity value (0-1)
        """
        self.hover_opacity = max(0, min(1, opacity))
        self._apply_stylesheet()
    
    def _on_slider_moved(self):
        """Handle slider movement"""
        pass


class CustomVerticalScrollBar(CustomScrollBar):
    """Convenience class for vertical scrollbar"""
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(Qt.Orientation.Vertical, parent, **kwargs)


class CustomHorizontalScrollBar(CustomScrollBar):
    """Convenience class for horizontal scrollbar"""
    
    def __init__(self, parent=None, **kwargs):
        super().__init__(Qt.Orientation.Horizontal, parent, **kwargs)
