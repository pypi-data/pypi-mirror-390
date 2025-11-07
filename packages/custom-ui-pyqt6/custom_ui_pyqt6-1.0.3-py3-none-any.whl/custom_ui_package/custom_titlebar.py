"""
Custom Title Bar Widget - Modern, reusable title bar with control buttons
Features: Frameless window support, minimize/close buttons, draggable, icon support
"""

from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from .colors.color_palette import get_global_color


class CustomTitleBar(QFrame):
    """
    Modern custom title bar with:
    - Window icon
    - Title text
    - Minimize button
    - Close button
    - Draggable support
    - Modern styling
    - Configurable solid background colors
    
    Args:
        parent: Parent widget
        title (str): Title bar text
        icon_path (str, optional): Path to window icon
        show_minimize (bool): Show minimize button
        show_close (bool): Show close button
        bg_color (str, optional): Background color (solid color only)
        text_color (str, optional): Title text color
        border_color (str, optional): Border color
        border_bg (str, optional): Button hover background color
        font_size (int): Font size for title text (default: 13)
        bold (bool): Whether title text should be bold (default: True)
    
    Examples:
        # Basic title bar with large bold text
        titlebar = CustomTitleBar(
            title='My App',
            bg_color='#a855f7',
            font_size=16,
            bold=True
        )
        
        # Smaller non-bold title
        titlebar = CustomTitleBar(
            title='Small App',
            bg_color='#1a0f2e',
            text_color='#f3e8ff',
            font_size=12,
            bold=False
        )
    """
    
    def __init__(self, parent=None, title="Application", icon_path=None, show_minimize=True, show_close=True,
                 bg_color=None, text_color=None, border_color=None, border_bg=None,
                 font_size=13, bold=True):
        super().__init__(parent)
        self.parent_window = parent
        self.drag_position = None
        
        # Configure frame
        self.setObjectName("titleBar")
        self.setFixedHeight(40)
        
        # Store color parameters with sensible defaults
        self.bg_color = bg_color or '#a855f7'
        self.text_color = text_color or '#f3e8ff'
        self.border_color = border_color or 'rgba(168, 85, 247, 0.3)'
        self.border_bg = border_bg or 'rgba(168, 85, 247, 0.1)'
        
        # Store font parameters
        self.font_size = font_size
        self.bold = bold
        
        # Apply initial styling
        self._apply_titlebar_style()
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)
        
        # Window icon
        if icon_path:
            icon_label = QLabel()
            icon_label.setObjectName("titleIcon")
            try:
                icon_pixmap = QIcon(icon_path).pixmap(24, 24)
                icon_label.setPixmap(icon_pixmap)
                icon_label.setFixedSize(24, 24)
                layout.addWidget(icon_label)
            except:
                pass
        
        # Title label
        title_label = QLabel(title)
        title_label.setObjectName("titleLabel")
        font_weight = "bold" if self.bold else "normal"
        title_label.setStyleSheet(f"font-weight: {font_weight}; font-size: {self.font_size}px; color: {self.text_color}; margin-left: 8px;")
        layout.addWidget(title_label)
        layout.addStretch()
        
        # Minimize button
        if show_minimize:
            self.minimize_btn = QPushButton('−')
            self.minimize_btn.setObjectName("minimizeBtn")
            self.minimize_btn.setFixedSize(32, 32)
            self.minimize_btn.setStyleSheet("""
                QPushButton#minimizeBtn {
                    background: transparent;
                    border: none;
                    color: #e8f0ff;
                    font-size: 18px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton#minimizeBtn:hover {
                    background: rgba(99, 102, 241, 0.2);
                    border-radius: 6px;
                }
                QPushButton#minimizeBtn:pressed {
                    background: rgba(99, 102, 241, 0.4);
                }
            """)
            if parent:
                # Connect to minimize - will minimize to taskbar, not tray
                self.minimize_btn.clicked.connect(lambda: parent.setWindowState(parent.windowState() | Qt.WindowState.WindowMinimized))
            layout.addWidget(self.minimize_btn)
        
        # Close button
        if show_close:
            self.close_btn = QPushButton('✕')
            self.close_btn.setObjectName("closeBtn")
            self.close_btn.setFixedSize(32, 32)
            self.close_btn.setStyleSheet("""
                QPushButton#closeBtn {
                    background: transparent;
                    border: none;
                    color: #e8f0ff;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 0px;
                }
                QPushButton#closeBtn:hover {
                    background: rgba(239, 68, 68, 0.8);
                    border-radius: 6px;
                }
                QPushButton#closeBtn:pressed {
                    background: rgba(239, 68, 68, 0.5);
                }
            """)
            if parent:
                # Connect to quit the application
                from PyQt6.QtWidgets import QApplication
                self.close_btn.clicked.connect(QApplication.quit)
            layout.addWidget(self.close_btn)
    
    def _apply_titlebar_style(self):
        """Apply title bar styling with colors"""
        # Build background style with solid color
        bg_style = f"background: {self.bg_color};" if self.bg_color else "background: rgba(10, 14, 39, 0.95);"
        
        # Apply title bar stylesheet
        self.setStyleSheet(f"""
            #titleBar {{
                {bg_style}
                margin: 0px;
                padding: 0px;
            }}
            #titleLabel {{
                background: transparent;
                margin: 0px;
                padding: 0px;
            }}
            QLabel {{
                background: transparent;
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton and self.parent_window:
            self.drag_position = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None and self.parent_window:
            self.parent_window.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def set_title(self, title):
        """Update title text"""
        # Find and update title label
        for widget in self.findChildren(QLabel):
            if widget.objectName() == "titleLabel":
                widget.setText(title)
                break
    
    def set_icon(self, icon_path):
        """Update window icon"""
        try:
            for widget in self.findChildren(QLabel):
                if widget.objectName() == "titleIcon":
                    icon_pixmap = QIcon(icon_path).pixmap(24, 24)
                    widget.setPixmap(icon_pixmap)
                    break
        except:
            pass
    
    def hide_minimize_button(self):
        """Hide minimize button"""
        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.hide()
    
    def hide_close_button(self):
        """Hide close button"""
        if hasattr(self, 'close_btn'):
            self.close_btn.hide()
    
    def show_minimize_button(self):
        """Show minimize button"""
        if hasattr(self, 'minimize_btn'):
            self.minimize_btn.show()
    
    def show_close_button(self):
        """Show close button"""
        if hasattr(self, 'close_btn'):
            self.close_btn.show()
