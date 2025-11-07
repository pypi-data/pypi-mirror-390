"""
CustomModal - Reusable modal dialog for collecting setup inputs.

A fully customizable modal dialog with support for:
- Frameless window style with custom title bar
- Built-in CustomInputBox fields for common inputs
- CustomButton for OK/Cancel with custom actions
- Input validation logic
- Data collection and retrieval
- Customizable colors, fonts, and styling
- Smooth animations and transitions
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QWidget
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QBrush, QPen
from typing import Optional, Dict, List, Callable, Any
from .custom_input_box import CustomInputBox
from .custom_button import CustomButton
from .colors.color_palette import get_global_color


class CustomModal(QDialog):
    """
    Reusable modal dialog for collecting setup inputs.
    
    Features:
    - Frameless window with custom title bar
    - Built-in CustomInputBox fields for inputs
    - CustomButton for OK/Cancel actions
    - Input validation logic
    - Data collection and retrieval
    - Customizable colors, fonts, and styling
    - Smooth animations and transitions
    
    Signals:
        accepted_custom: Emitted when OK button is clicked with valid inputs
        rejected_custom: Emitted when Cancel button is clicked
        input_changed: Emitted when any input value changes
    
    Example:
        modal = CustomModal(
            parent=None,
            title="Setup Dialog",
            width=500,
            height=400,
            fields=[
                {"name": "username", "label": "Username", "type": "text"},
                {"name": "password", "label": "Password", "type": "password"}
            ]
        )
        if modal.exec() == QDialog.DialogCode.Accepted:
            data = modal.get_inputs()
    """
    
    accepted_custom = pyqtSignal(dict)  # Emits collected data
    rejected_custom = pyqtSignal()
    input_changed = pyqtSignal(str, str)  # field_name, value
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        title: str = "Modal Dialog",
        width: int = 500,
        height: int = 400,
        fields: Optional[List[Dict[str, Any]]] = None,
        ok_text: str = "OK",
        cancel_text: str = "Cancel",
        border_radius: int = 12,
        border_width: int = 1,
        padding: int = 20,
        spacing: int = 16,
        animation_name: str = "smooth",
        # Colors
        bg_color: str = "#1a1a2e",
        border_color: str = "rgba(168, 85, 247, 0.3)",
        title_color: str = "#ffffff",
        title_bg_color: str = "rgba(168, 85, 247, 0.1)",
        label_color: str = "#e8f0ff",
        # Fonts
        title_font_family: str = "Segoe UI",
        title_font_size: int = 14,
        label_font_family: str = "Segoe UI",
        label_font_size: int = 11,
        # Buttons
        ok_button_color: str = "#a855f7",
        ok_button_text_color: str = "#ffffff",
        cancel_button_color: str = "rgba(168, 85, 247, 0.2)",
        cancel_button_text_color: str = "#e8f0ff",
        button_height: int = 40,
        button_width: int = 120,
        button_font_size: int = 11,
        ok_button_bold: bool = True,
        cancel_button_bold: bool = False,
        # Input boxes
        input_bg_color: str = "#0f0f1e",
        input_text_color: str = "#ffffff",
        input_border_color: str = "rgba(168, 85, 247, 0.3)",
        input_focus_color: str = "#a855f7",
        input_height: int = 40,
        # Validation
        validation_callback: Optional[Callable[[Dict[str, str]], bool]] = None,
        validation_error_color: str = "#ef4444",
        # Behavior
        modal: bool = True,
        draggable: bool = True,
        closable: bool = True,
    ):
        """
        Initialize CustomModal.
        
        Args:
            parent: Parent widget
            title: Modal title text
            width: Modal width in pixels
            height: Modal height in pixels
            fields: List of field dictionaries with keys:
                - name: Field identifier (required)
                - label: Display label (required)
                - type: 'text', 'password', 'email', 'number' (default: 'text')
                - placeholder: Placeholder text (optional)
                - default_value: Default value (optional)
                - required: Whether field is required (default: False)
                - validation_regex: Regex pattern for validation (optional)
            ok_text: Text for OK button
            cancel_text: Text for Cancel button
            border_radius: Border radius in pixels
            border_width: Border width in pixels
            padding: Inner padding in pixels
            spacing: Spacing between elements in pixels
            animation_name: Animation type - 'smooth', 'bounce', 'elastic', 'none'
            bg_color: Background color (hex or rgba)
            border_color: Border color (hex or rgba)
            title_color: Title text color (hex or rgba)
            title_bg_color: Title background color (hex or rgba)
            label_color: Label text color (hex or rgba)
            title_font_family: Title font family
            title_font_size: Title font size in pixels
            label_font_family: Label font family
            label_font_size: Label font size in pixels
            ok_button_color: OK button background color
            ok_button_text_color: OK button text color
            cancel_button_color: Cancel button background color
            cancel_button_text_color: Cancel button text color
            button_height: Button height in pixels
            button_width: Button width in pixels
            button_font_size: Font size for both buttons
            ok_button_bold: Whether OK button text is bold
            cancel_button_bold: Whether Cancel button text is bold
            input_bg_color: Input box background color
            input_text_color: Input box text color
            input_border_color: Input box border color
            input_focus_color: Input box focus color
            input_height: Input box height in pixels
            validation_callback: Custom validation function
            validation_error_color: Error message color
            modal: Whether dialog is modal
            draggable: Whether title bar is draggable
            closable: Whether close button is visible
        """
        super().__init__(parent)
        
        # Store properties
        self.title_text = title
        self.border_radius = border_radius
        self.border_width = border_width
        self.padding = padding
        self.spacing = spacing
        self.animation_name = animation_name
        self.draggable = draggable
        self.drag_position = None
        
        # Colors
        self.bg_color = bg_color
        self.border_color = border_color
        self.title_color = title_color
        self.title_bg_color = title_bg_color
        self.label_color = label_color
        
        # Fonts
        self.title_font_family = title_font_family
        self.title_font_size = title_font_size
        self.label_font_family = label_font_family
        self.label_font_size = label_font_size
        
        # Buttons
        self.ok_button_color = ok_button_color
        self.ok_button_text_color = ok_button_text_color
        self.cancel_button_color = cancel_button_color
        self.cancel_button_text_color = cancel_button_text_color
        self.button_height = button_height
        self.button_width = button_width
        self.button_font_size = button_font_size
        self.ok_button_bold = ok_button_bold
        self.cancel_button_bold = cancel_button_bold
        
        # Input boxes
        self.input_bg_color = input_bg_color
        self.input_text_color = input_text_color
        self.input_border_color = input_border_color
        self.input_focus_color = input_focus_color
        self.input_height = input_height
        
        # Validation
        self.validation_callback = validation_callback
        self.validation_error_color = validation_error_color
        
        # Fields storage
        self.fields = fields or []
        self.input_widgets: Dict[str, CustomInputBox] = {}
        self.error_labels: Dict[str, QLabel] = {}
        
        # Set window properties
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(width, height)
        self.setModal(modal)
        
        # Create UI
        self._create_ui()
        self._apply_stylesheet()
    
    def _create_ui(self):
        """Create the modal UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Title bar
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)
        
        # Content area
        content_frame = QFrame()
        content_frame.setStyleSheet(f"background-color: {self.bg_color}; border: none;")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(self.padding, self.padding, self.padding, self.padding)
        content_layout.setSpacing(self.spacing)
        
        # Scroll area for fields
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: {self.bg_color};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {self.bg_color};
                width: 8px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: rgba(168, 85, 247, 0.3);
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: rgba(168, 85, 247, 0.5);
            }}
        """)
        
        # Fields container
        fields_widget = QWidget()
        fields_layout = QVBoxLayout(fields_widget)
        fields_layout.setContentsMargins(0, 0, 0, 0)
        fields_layout.setSpacing(self.spacing)
        
        # Create input fields
        for field in self.fields:
            field_layout = self._create_field(field, fields_layout)
        
        fields_layout.addStretch()
        scroll_area.setWidget(fields_widget)
        content_layout.addWidget(scroll_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = CustomButton(
            parent=content_frame,
            title=self.cancel_text,
            size=(self.button_width, self.button_height),
            font_size=self.button_font_size,
            color=self.cancel_button_text_color,
            bg_color=self.cancel_button_color,
            bold=self.cancel_button_bold
        )
        cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(cancel_btn)
        
        # OK button
        ok_btn = CustomButton(
            parent=content_frame,
            title=self.ok_text,
            size=(self.button_width, self.button_height),
            font_size=self.button_font_size,
            color=self.ok_button_text_color,
            bg_color=self.ok_button_color,
            bold=self.ok_button_bold
        )
        ok_btn.clicked.connect(self._on_ok)
        button_layout.addWidget(ok_btn)
        
        content_layout.addLayout(button_layout)
        main_layout.addWidget(content_frame)
    
    def _create_title_bar(self) -> QFrame:
        """Create the title bar frame."""
        title_bar = QFrame()
        title_bar.setStyleSheet(f"background-color: {self.title_bg_color}; border: none;")
        title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)
        title_layout.setSpacing(8)
        
        # Title label
        title_label = QLabel(self.title_text)
        title_font = QFont(self.title_font_family, self.title_font_size)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {self.title_color}; background: transparent;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # Close button
        close_btn = CustomButton(
            parent=title_bar,
            title="✕",
            size=(32, 32),
            font_size=14,
            color="#e8f0ff",
            bg_color="transparent",
            bold=False
        )
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #e8f0ff;
                font-size: 16px;
                padding: 0px;
            }
            QPushButton:hover {
                background: rgba(239, 68, 68, 0.3);
                border-radius: 6px;
            }
            QPushButton:pressed {
                background: rgba(239, 68, 68, 0.5);
            }
        """)
        close_btn.clicked.connect(self._on_cancel)
        title_layout.addWidget(close_btn)
        
        return title_bar
    
    def _create_field(self, field: Dict[str, Any], parent_layout: QVBoxLayout) -> QVBoxLayout:
        """Create a single input field."""
        field_layout = QVBoxLayout()
        field_layout.setContentsMargins(0, 0, 0, 0)
        field_layout.setSpacing(6)
        
        # Label
        label_text = field.get("label", field.get("name", ""))
        if field.get("required", False):
            label_text += " *"
        
        label = QLabel(label_text)
        label_font = QFont(self.label_font_family, self.label_font_size)
        label.setFont(label_font)
        label.setStyleSheet(f"color: {self.label_color}; background: transparent;")
        field_layout.addWidget(label)
        
        # Input box
        field_name = field.get("name", "")
        field_type = field.get("type", "text")
        placeholder = field.get("placeholder", "")
        default_value = field.get("default_value", "")
        
        input_box = CustomInputBox(
            parent=None,
            shape="rounded_rectangle",
            width=400,
            height=self.input_height,
            border_radius=6,
            border_width=1,
            padding=10,
            animation_name=self.animation_name,
            bg_color=self.input_bg_color,
            text_color=self.input_text_color,
            border_color=self.input_border_color,
            focus_color=self.input_focus_color,
            placeholder=placeholder,
            font_size=11
        )
        
        # Set input type
        if field_type == "password":
            input_box.setEchoMode(input_box.EchoMode.Password)
        
        # Set default value
        if default_value:
            input_box.set_text(default_value)
        
        # Connect signal
        input_box.text_changed_custom.connect(
            lambda text: self.input_changed.emit(field_name, text)
        )
        
        self.input_widgets[field_name] = input_box
        field_layout.addWidget(input_box)
        
        # Error label
        error_label = QLabel("")
        error_label.setStyleSheet(f"color: {self.validation_error_color}; font-size: 10px; background: transparent;")
        error_label.setVisible(False)
        self.error_labels[field_name] = error_label
        field_layout.addWidget(error_label)
        
        parent_layout.addLayout(field_layout)
        return field_layout
    
    def _apply_stylesheet(self):
        """Apply custom stylesheet."""
        stylesheet = f"""
            QDialog {{
                background-color: {self.bg_color};
                border: {self.border_width}px solid {self.border_color};
                border-radius: {self.border_radius}px;
            }}
        """
        self.setStyleSheet(stylesheet)
    
    def _validate_inputs(self) -> bool:
        """Validate all inputs."""
        is_valid = True
        
        for field in self.fields:
            field_name = field.get("name", "")
            input_box = self.input_widgets.get(field_name)
            error_label = self.error_labels.get(field_name)
            
            if not input_box or not error_label:
                continue
            
            value = input_box.get_text()
            error_message = ""
            
            # Check required
            if field.get("required", False) and not value:
                error_message = "This field is required"
                is_valid = False
            
            # Check regex validation
            if value and field.get("validation_regex"):
                import re
                if not re.match(field["validation_regex"], value):
                    error_message = "Invalid format"
                    is_valid = False
            
            # Show/hide error label
            if error_message:
                error_label.setText(error_message)
                error_label.setVisible(True)
            else:
                error_label.setVisible(False)
        
        # Custom validation callback
        if is_valid and self.validation_callback:
            data = self.get_inputs()
            if not self.validation_callback(data):
                is_valid = False
        
        return is_valid
    
    def _on_ok(self):
        """Handle OK button click."""
        if self._validate_inputs():
            data = self.get_inputs()
            self.accepted_custom.emit(data)
            self.accept()
    
    def _on_cancel(self):
        """Handle Cancel button click."""
        self.rejected_custom.emit()
        self.reject()
    
    def paintEvent(self, event):
        """Paint the modal with border radius."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw background with border radius
        path = QPainterPath()
        path.addRoundedRect(self.rect(), self.border_radius, self.border_radius)
        
        painter.fillPath(path, QBrush(QColor(self.bg_color)))
        painter.strokePath(path, QPen(QColor(self.border_color), self.border_width))
        
        painter.end()
        super().paintEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging."""
        if self.draggable and event.button() == Qt.MouseButton.LeftButton:
            if event.position().y() < 50:  # Title bar height
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging."""
        if self.draggable and event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def get_inputs(self) -> Dict[str, str]:
        """
        Get all input values.
        
        Returns:
            Dictionary with field names as keys and input values as values
        """
        data = {}
        for field_name, input_box in self.input_widgets.items():
            data[field_name] = input_box.get_text()
        return data
    
    def set_input(self, field_name: str, value: str):
        """
        Set input value for a specific field.
        
        Args:
            field_name: Name of the field
            value: Value to set
        """
        if field_name in self.input_widgets:
            self.input_widgets[field_name].set_text(value)
    
    def get_input(self, field_name: str) -> str:
        """
        Get input value for a specific field.
        
        Args:
            field_name: Name of the field
            
        Returns:
            Input value or empty string if field not found
        """
        if field_name in self.input_widgets:
            return self.input_widgets[field_name].get_text()
        return ""
    
    def clear_inputs(self):
        """Clear all input values."""
        for input_box in self.input_widgets.values():
            input_box.clear_text()
    
    def set_colors(
        self,
        bg_color: Optional[str] = None,
        border_color: Optional[str] = None,
        title_color: Optional[str] = None,
        label_color: Optional[str] = None,
    ):
        """
        Update colors at runtime.
        
        Args:
            bg_color: Background color (hex or rgba)
            border_color: Border color (hex or rgba)
            title_color: Title text color (hex or rgba)
            label_color: Label text color (hex or rgba)
        """
        if bg_color:
            self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        if title_color:
            self.title_color = title_color
        if label_color:
            self.label_color = label_color
        
        self._apply_stylesheet()
        self.update()
    
    def set_title(self, title: str):
        """Set modal title."""
        self.title_text = title
        self.update()
    
    def add_field(self, field: Dict[str, Any]):
        """
        Add a new field to the modal.
        
        Args:
            field: Field dictionary with name, label, type, etc.
        """
        self.fields.append(field)
        # Note: Recreate UI to add the field
    
    def remove_field(self, field_name: str):
        """
        Remove a field from the modal.
        
        Args:
            field_name: Name of the field to remove
        """
        self.fields = [f for f in self.fields if f.get("name") != field_name]
        if field_name in self.input_widgets:
            del self.input_widgets[field_name]
        if field_name in self.error_labels:
            del self.error_labels[field_name]
