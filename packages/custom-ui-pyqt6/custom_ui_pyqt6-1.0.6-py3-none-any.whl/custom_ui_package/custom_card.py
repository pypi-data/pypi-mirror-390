"""
CustomCard - Card container with shadows and theming.

A fully customizable card widget with support for:
- Custom colors (background, border, shadow)
- Configurable border radius and shadow
- Hover effects
- Title and content areas
- Flexible layout
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional


class CustomCard(QWidget):
    """
    Card widget with custom styling and shadow effects.
    
    Signals:
        clicked_custom: Emitted when card is clicked
    """
    
    clicked_custom = pyqtSignal()
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "Card Title",
        width: int = 300,
        height: int = 200,
        border_radius: int = 12,
        border_width: int = 1,
        padding: int = 16,
        animation_name: str = "smooth",
        bg_color: str = "#1a1a2e",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        title_color: str = "#ffffff",
        shadow_color: str = "rgba(168, 85, 247, 0.2)",
        shadow_blur: int = 12,
        shadow_offset_x: int = 0,
        shadow_offset_y: int = 4,
        hover_shadow_blur: int = 20,
        font_family: str = "Segoe UI",
        font_size: int = 12,
    ):
        """
        Initialize CustomCard.
        
        Args:
            parent: Parent widget
            title: Card title
            width: Card width in pixels
            height: Card height in pixels
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            padding: Padding in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            border_color: Border color (hex or rgba)
            title_color: Title text color (hex or rgba)
            shadow_color: Shadow color (hex or rgba)
            shadow_blur: Shadow blur radius
            shadow_offset_x: Shadow X offset
            shadow_offset_y: Shadow Y offset
            hover_shadow_blur: Shadow blur on hover
            font_family: Font family name
            font_size: Font size in pixels
        """
        super().__init__(parent)
        
        # Store properties
        self.border_radius = border_radius
        self.border_width = border_width
        self.padding = padding
        self.animation_name = animation_name
        
        # Colors
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color
        self.shadow_color = shadow_color
        self.shadow_blur = shadow_blur
        self.shadow_offset_x = shadow_offset_x
        self.shadow_offset_y = shadow_offset_y
        self.hover_shadow_blur = hover_shadow_blur
        self.current_shadow_blur = shadow_blur
        
        # State tracking
        self.is_hovered = False
        
        # Set size
        self.setFixedSize(width, height)
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(padding, padding, padding, padding)
        self.layout.setSpacing(8)
        
        # Create title label
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont(font_family, font_size, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {title_color};")
        self.layout.addWidget(self.title_label)
        
        # Content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.content_widget)
        
        # Apply stylesheet
        self._apply_stylesheet()
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)
        self.animation_progress = 0.0
        
        # Set cursor
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QWidget {{
                background-color: {self.bg_color};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.border_radius}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def paintEvent(self, event):
        """Paint the card with shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw shadow
        shadow_color = QColor(self.shadow_color)
        shadow_color.setAlpha(int(255 * (self.current_shadow_blur / 20)))
        
        for i in range(self.current_shadow_blur, 0, -1):
            shadow_color.setAlpha(int(255 * (i / self.current_shadow_blur) * 0.3))
            painter.setPen(QPen(shadow_color, 1))
            
            rect = QRect(
                self.shadow_offset_x - i,
                self.shadow_offset_y - i,
                self.width() + i * 2,
                self.height() + i * 2
            )
            painter.drawRoundedRect(rect, self.border_radius, self.border_radius)
        
        # Draw main card
        painter.fillRect(self.rect(), QBrush(QColor(self.bg_color)))
        painter.setPen(QPen(QColor(self.border_color), self.border_width))
        painter.drawRoundedRect(self.rect(), self.border_radius, self.border_radius)
        
        painter.end()
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press event."""
        super().mousePressEvent(event)
        self.clicked_custom.emit()
    
    def enterEvent(self, event):
        """Handle mouse enter event."""
        super().enterEvent(event)
        self.is_hovered = True
        self._start_animation()
    
    def leaveEvent(self, event):
        """Handle mouse leave event."""
        super().leaveEvent(event)
        self.is_hovered = False
        self._start_animation()
    
    def _start_animation(self):
        """Start animation."""
        if self.animation_name == "none":
            self._update_shadow()
            return
        
        self.animation_progress = 0.0
        self.animation_timer.start(16)
    
    def _update_animation(self):
        """Update animation progress."""
        self.animation_progress += 0.05
        
        if self.animation_progress >= 1.0:
            self.animation_progress = 1.0
            self.animation_timer.stop()
        
        self._update_shadow()
    
    def _update_shadow(self):
        """Update shadow based on state."""
        if self.is_hovered:
            target_blur = self.hover_shadow_blur
        else:
            target_blur = self.shadow_blur
        
        if self.animation_name != "none":
            self.current_shadow_blur = self.shadow_blur + (
                target_blur - self.shadow_blur
            ) * self.animation_progress
        else:
            self.current_shadow_blur = target_blur
        
        self.update()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        border_color: Optional[str] = None,
        title_color: Optional[str] = None,
        shadow_color: Optional[str] = None,
    ):
        """Update colors at runtime."""
        if bg_color:
            self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        if title_color:
            self.title_color = title_color
            self.title_label.setStyleSheet(f"color: {title_color};")
        if shadow_color:
            self.shadow_color = shadow_color
        
        self._apply_stylesheet()
        self.update()
    
    def set_title(self, title: str):
        """Set card title."""
        self.title_label.setText(title)
    
    def get_title(self) -> str:
        """Get card title."""
        return self.title_label.text()
    
    def set_content_widget(self, widget: QWidget):
        """Set content widget."""
        # Remove old widget
        while self.content_layout.count():
            self.content_layout.takeAt(0).widget().deleteLater()
        
        # Add new widget
        self.content_layout.addWidget(widget)
    
    def set_size(self, width: int, height: int):
        """Change dimensions."""
        self.setFixedSize(width, height)
    
    def set_border_radius(self, radius: int):
        """Update border radius."""
        self.border_radius = radius
        self._apply_stylesheet()
        self.update()
    
    def set_shadow(
        self, blur_radius: int, offset_x: int, offset_y: int, color: str
    ):
        """Update shadow properties."""
        self.shadow_blur = blur_radius
        self.shadow_offset_x = offset_x
        self.shadow_offset_y = offset_y
        self.shadow_color = color
        self.update()
    
    def set_animation(self, animation_name: str):
        """Change animation type."""
        self.animation_name = animation_name
