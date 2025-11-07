"""
Custom Main Window - A reusable frameless main window
Provides a base class for creating modern windows with customizable styling
"""

from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .colors.color_palette import GLOBAL_COLOR_PALETTE, create_background_style, get_global_color, set_global_color_palette


# Predefined color themes have been removed
# Use GLOBAL_COLOR_PALETTE and set_global_color_palette() instead
THEMES = {}


class CustomMainWindow(QMainWindow):
    """
    A frameless main window with customizable styling.
    
    Features:
    - Frameless window design
    - Solid color background
    - Smooth button transitions
    - Customizable color themes
    - Easy to extend for custom applications
    - No default title bar (add CustomTitleBar manually if needed)
    
    Args:
        title (str): Window title (default: 'Custom Window')
        width (int): Window width in pixels (default: 600)
        height (int): Window height in pixels (default: 750)
        theme (str): Theme name from THEMES dict (default: None)
        custom_colors (dict, optional): Custom color dictionary to override theme
        bg_color (str, optional): Background color (solid color only). Hex or rgba format
        use_custom_scrollbar (bool): Enable custom scrollbar styling (default: False)
        scrollbar_color (str, optional): Scrollbar handle color. Default: global primary color
        scrollbar_width (int): Scrollbar width in pixels (default: 8)
        content_margins (tuple): Content area margins (left, top, right, bottom) (default: (40, 30, 40, 30))
        content_spacing (int): Spacing between content widgets (default: 15)
    
    Examples:
        # Single color background
        window = CustomMainWindow(title='App', bg_color='#a855f7')
        
        # With custom scrollbar
        window = CustomMainWindow(
            title='App',
            bg_color='#a855f7',
            use_custom_scrollbar=True,
            scrollbar_color='#ec4899',
            scrollbar_width=10
        )
        
        # Add custom title bar manually
        from custom_ui_package import CustomTitleBar
        title_bar = CustomTitleBar(parent=window, title='My App', bg_color='#7a00ff')
        layout = window.centralWidget().layout()
        layout.insertWidget(0, title_bar)
    """
    
    def __init__(self, title='Custom Window', width=600, height=750, 
                 theme=None, custom_colors=None, 
                 bg_color=None, use_custom_scrollbar=False, scrollbar_color=None, scrollbar_width=8,
                 content_margins=(40, 30, 40, 30), content_spacing=15):
        super().__init__()
        self.setGeometry(100, 100, width, height)
        self.setWindowTitle(title)
        self.title_bar = None  # No default title bar
        
        # Apply frameless window style - removes default title bar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        
        # Disable window shadows and effects
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        
        # Initialize colors from global palette
        self.colors = {
            'bg_color': GLOBAL_COLOR_PALETTE.get('background', '#0a0e27'),
            'button_color': GLOBAL_COLOR_PALETTE.get('primary', '#6366f1'),
            'button_hover_color': GLOBAL_COLOR_PALETTE.get('primary', '#6366f1'),
            'button_pressed_color': GLOBAL_COLOR_PALETTE.get('primary', '#6366f1'),
            'text_primary': GLOBAL_COLOR_PALETTE.get('text', '#e8f0ff'),
            'text_secondary': GLOBAL_COLOR_PALETTE.get('secondary', '#a5f3fc'),
            'border_color': GLOBAL_COLOR_PALETTE.get('border', 'rgba(99, 102, 241, 0.3)'),
            'border_bg': GLOBAL_COLOR_PALETTE.get('border_hover', 'rgba(99, 102, 241, 0.1)'),
        }
        
        # Override with background color parameter if provided
        if bg_color:
            self.colors['bg_color'] = bg_color
        
        # Override with custom colors if provided
        if custom_colors:
            self.colors.update(custom_colors)
        
        # Apply stylesheet with theme colors
        self._apply_stylesheet()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create content area widget (to be populated by subclasses)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(*content_margins)
        self.content_layout.setSpacing(content_spacing)
        
        layout.addWidget(self.content_widget)
        
        # Apply custom scrollbar if enabled
        if use_custom_scrollbar:
            from .custom_scrollbar import CustomVerticalScrollBar, CustomHorizontalScrollBar
            
            # Create custom scrollbars
            v_scrollbar = CustomVerticalScrollBar(
                handle_color=scrollbar_color or get_global_color('primary', '#a855f7'),
                handle_width=scrollbar_width
            )
            h_scrollbar = CustomHorizontalScrollBar(
                handle_color=scrollbar_color or get_global_color('primary', '#a855f7'),
                handle_height=scrollbar_width
            )
            
            # Set scrollbars on content widget
            self.content_widget.setVerticalScrollBar(v_scrollbar)
            self.content_widget.setHorizontalScrollBar(h_scrollbar)
        
        # Create overlay widget for absolute-positioned elements (labels, buttons with position)
        self.overlay_widget = QWidget(self.content_widget)
        self.overlay_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        
        # Store content margins for overlay sizing
        self._content_margins = content_margins
    
    def closeEvent(self, event):
        """Handle window close event - properly exit the application"""
        import os
        import sys
        from PyQt6.QtWidgets import QApplication
        
        # Accept the close event first
        event.accept()
        
        # Quit the Qt application
        QApplication.quit()
        
        # Force immediate termination of the entire process
        # os._exit() bypasses cleanup and exits immediately
        os._exit(0)
    
    def resizeEvent(self, event):
        """Update overlay widget geometry when window is resized"""
        super().resizeEvent(event)
        if hasattr(self, 'overlay_widget') and hasattr(self, 'content_widget'):
            self.overlay_widget.setGeometry(0, 0, self.content_widget.width(), self.content_widget.height())
    
    def _apply_stylesheet(self):
        """Apply stylesheet with current theme colors"""
        # Build stylesheet with solid colors
        stylesheet = f"""
            * {{
                margin: 0px;
                padding: 0px;
            }}
            QWidget {{ 
                background: {self.colors['bg_color']};
            }}
            QPushButton {{
                background: {self.colors['button_color']};
                border: none;
                border-radius: 12px;
                padding: 15px 20px;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
                outline: none;
            }}
            QPushButton:hover {{
                background: {self.colors['button_hover_color']};
            }}
            QPushButton:pressed {{
                background: {self.colors['button_pressed_color']};
            }}
            QPushButton:focus {{
                outline: none;
            }}
        """
        self.setAutoFillBackground(True)
        self.setStyleSheet(stylesheet)
        # Also apply to central widget
        if hasattr(self, 'centralWidget') and self.centralWidget():
            self.centralWidget().setStyleSheet(stylesheet)
    
    
    
    def create_custom_label(self, text, size=(100, 30), position=(0, 0), font_size=10, bold=False, color=None):
        """
        Create a custom label with absolute positioning.
        
        Args:
            text (str): Label text
            size (tuple): Label size (width, height)
            position (tuple): Label position (x, y)
            font_size (int): Font size
            bold (bool): Whether text should be bold
            color (str): Text color (hex or rgba). Uses global palette 'text' color if None
            
        Returns:
            CustomLabel: Configured label ready to use
        """
        from .custom_label import CustomLabel
        label = CustomLabel(
            parent=self.overlay_widget,
            text=text,
            size=size,
            position=position,
            font_size=font_size,
            bold=bold,
            color=color
        )
        label.show()
        return label
    
    def set_custom_colors(self, colors_dict):
        """
        Set custom colors for the window.
        
        Args:
            colors_dict (dict): Dictionary with color keys to override
                Expected keys: bg_gradient_start, bg_gradient_end, button_start, button_end,
                              button_hover_start, button_hover_end, button_pressed_start, 
                              button_pressed_end, text_primary, text_secondary, 
                              border_color, border_bg
        """
        self.colors.update(colors_dict)
        self._apply_stylesheet()
    
    def get_theme_colors(self):
        """
        Get current theme colors.
        
        Returns:
            dict: Current color configuration
        """
        return self.colors.copy()
    
    def add_content(self, widget):
        """
        Add a widget to the content area.
        
        Args:
            widget (QWidget): Widget to add to content area
        """
        self.content_layout.addWidget(widget)
    
    def add_stretch(self):
        """Add stretch to push remaining content to top"""
        self.content_layout.addStretch()
    
    def set_title(self, title):
        """
        Update the window title.
        
        Args:
            title (str): New title text
        """
        self.setWindowTitle(title)
        self.title_bar.set_title(title)
    
    def set_content_margins(self, left, top, right, bottom):
        """
        Set content area margins.
        
        Args:
            left (int): Left margin in pixels
            top (int): Top margin in pixels
            right (int): Right margin in pixels
            bottom (int): Bottom margin in pixels
        """
        self.content_layout.setContentsMargins(left, top, right, bottom)
    
    def set_content_spacing(self, spacing):
        """
        Set spacing between content widgets.
        
        Args:
            spacing (int): Spacing in pixels
        """
        self.content_layout.setSpacing(spacing)
    
    def get_global_color(self, key, default='#ffffff'):
        """
        Get a color from the global palette.
        
        Args:
            key (str): Color key (e.g., 'primary', 'text', 'border')
            default (str): Default color if key not found
            
        Returns:
            str: Color value (hex or rgba)
        """
        return get_global_color(key, default)
