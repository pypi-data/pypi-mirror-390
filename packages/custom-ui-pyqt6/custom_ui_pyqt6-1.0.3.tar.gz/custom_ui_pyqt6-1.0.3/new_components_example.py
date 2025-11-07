"""
Example application demonstrating all new custom UI components.

This example shows how to use:
- CustomTextArea
- CustomCheckBox
- CustomRadioButton
- CustomSlider
- CustomProgressBar
- CustomTabWidget
- CustomCard
- CustomBadge
- CustomSpinner
- CustomToast
- CustomTooltip
- CustomAccordion
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QScrollArea
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from custom_ui_package import (
    CustomMainWindow,
    CustomTitleBar,
    CustomTextArea,
    CustomCheckBox,
    CustomRadioButton,
    CustomSlider,
    CustomProgressBar,
    CustomTabWidget,
    CustomCard,
    CustomBadge,
    CustomSpinner,
    CustomToast,
    CustomTooltip,
    CustomAccordion,
)


class NewComponentsDemo(CustomMainWindow):
    """Demo application for all new custom UI components."""
    
    def __init__(self):
        super().__init__(
            title="Custom UI Components Demo",
            width=1200,
            height=800,
            bg_color="#0f0f1e",
        )
        
        # Create title bar
        self.title_bar = CustomTitleBar(
            parent=self,
            title="Custom UI Components - Complete Demo",
            bg_color="#a855f7",
            text_color="#ffffff",
        )
        
        # Insert title bar at top
        layout = self.centralWidget().layout()
        layout.insertWidget(0, self.title_bar)
        
        # Create main content
        self._create_content()
        
        # Set window properties
        self.setGeometry(100, 100, 1200, 800)
    
    def _create_content(self):
        """Create the main content with all components."""
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0f0f1e;
                border: none;
            }
        """)
        
        # Create main container
        container = QWidget()
        main_layout = QVBoxLayout(container)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add component sections
        main_layout.addWidget(self._create_form_section())
        main_layout.addWidget(self._create_display_section())
        main_layout.addWidget(self._create_feedback_section())
        main_layout.addWidget(self._create_layout_section())
        main_layout.addStretch()
        
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        
        # Add to main window
        self.content_widget.layout().addWidget(scroll)
    
    def _create_form_section(self):
        """Create form components section."""
        card = CustomCard(
            title="📝 Form Components",
            width=1100,
            height=300,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # TextArea
        label = QLabel("CustomTextArea:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        textarea = CustomTextArea(
            placeholder="Enter your text here...",
            width=1050,
            height=80,
            bg_color="#0f0f1e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        layout.addWidget(textarea)
        
        # CheckBox
        checkbox = CustomCheckBox(
            label="I agree to the terms and conditions",
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        layout.addWidget(checkbox)
        
        # RadioButton
        radio1 = CustomRadioButton(
            label="Option 1",
            checked=True,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        radio2 = CustomRadioButton(
            label="Option 2",
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        layout.addWidget(radio1)
        layout.addWidget(radio2)
        
        card.set_content_widget(QWidget())
        card.content_widget.setLayout(layout)
        
        return card
    
    def _create_display_section(self):
        """Create data display components section."""
        card = CustomCard(
            title="📊 Data Display Components",
            width=1100,
            height=350,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Slider
        label = QLabel("CustomSlider:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        slider = CustomSlider(
            min_value=0,
            max_value=100,
            current_value=50,
            width=1050,
            height=30,
            track_color="rgba(168, 85, 247, 0.2)",
            groove_color="#a855f7",
        )
        layout.addWidget(slider)
        
        # ProgressBar
        label = QLabel("CustomProgressBar:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        progress = CustomProgressBar(
            min_value=0,
            max_value=100,
            current_value=65,
            width=1050,
            height=20,
            bg_color="rgba(168, 85, 247, 0.1)",
            progress_color="#a855f7",
        )
        layout.addWidget(progress)
        
        # Animate progress
        self.progress_timer = QTimer()
        self.progress_value = 65
        self.progress_timer.timeout.connect(lambda: self._update_progress(progress))
        self.progress_timer.start(50)
        
        # Spinner
        label = QLabel("CustomSpinner:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        spinner = CustomSpinner(
            size=40,
            spinner_color="#a855f7",
            animation_style="rotating",
        )
        layout.addWidget(spinner)
        
        card.set_content_widget(QWidget())
        card.content_widget.setLayout(layout)
        
        return card
    
    def _create_feedback_section(self):
        """Create feedback components section."""
        card = CustomCard(
            title="💬 Feedback & Status Components",
            width=1100,
            height=200,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Badges
        label = QLabel("CustomBadge:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        badge_layout = QHBoxLayout()
        
        badge1 = CustomBadge(
            text="Info",
            shape="pill",
            size="medium",
            bg_color="#0ea5e9",
        )
        badge2 = CustomBadge(
            text="Success",
            shape="pill",
            size="medium",
            bg_color="#10b981",
        )
        badge3 = CustomBadge(
            text="Warning",
            shape="pill",
            size="medium",
            bg_color="#f59e0b",
            closable=True,
        )
        badge4 = CustomBadge(
            text="Error",
            shape="pill",
            size="medium",
            bg_color="#ef4444",
        )
        
        badge_layout.addWidget(badge1)
        badge_layout.addWidget(badge2)
        badge_layout.addWidget(badge3)
        badge_layout.addWidget(badge4)
        badge_layout.addStretch()
        
        layout.addLayout(badge_layout)
        
        # Toast button
        toast_button = QPushButton("Show Toast Notification")
        toast_button.setStyleSheet("""
            QPushButton {
                background-color: #a855f7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c084fc;
            }
        """)
        toast_button.clicked.connect(self._show_toast)
        layout.addWidget(toast_button)
        
        card.set_content_widget(QWidget())
        card.content_widget.setLayout(layout)
        
        return card
    
    def _create_layout_section(self):
        """Create layout components section."""
        card = CustomCard(
            title="🎯 Navigation & Layout Components",
            width=1100,
            height=400,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.3)",
        )
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # TabWidget
        label = QLabel("CustomTabWidget:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        tabs = CustomTabWidget(
            tab_height=40,
            tab_width=120,
            bg_color="#0f0f1e",
            tab_color="rgba(168, 85, 247, 0.2)",
            active_color="#a855f7",
        )
        
        tab1_widget = QWidget()
        tab1_layout = QVBoxLayout(tab1_widget)
        tab1_layout.addWidget(QLabel("Tab 1 Content"))
        tabs.add_tab(tab1_widget, "Tab 1")
        
        tab2_widget = QWidget()
        tab2_layout = QVBoxLayout(tab2_widget)
        tab2_layout.addWidget(QLabel("Tab 2 Content"))
        tabs.add_tab(tab2_widget, "Tab 2")
        
        layout.addWidget(tabs)
        
        # Accordion
        label = QLabel("CustomAccordion:")
        label.setStyleSheet("color: #a855f7; font-weight: bold;")
        layout.addWidget(label)
        
        accordion = CustomAccordion(
            header_height=40,
            bg_color="#0f0f1e",
            header_color="rgba(168, 85, 247, 0.2)",
            content_color="#1a1a2e",
        )
        
        item1_content = QWidget()
        item1_layout = QVBoxLayout(item1_content)
        item1_layout.addWidget(QLabel("Item 1 Content"))
        accordion.add_item("Item 1", item1_content)
        
        item2_content = QWidget()
        item2_layout = QVBoxLayout(item2_content)
        item2_layout.addWidget(QLabel("Item 2 Content"))
        accordion.add_item("Item 2", item2_content)
        
        layout.addWidget(accordion)
        
        card.set_content_widget(QWidget())
        card.content_widget.setLayout(layout)
        
        return card
    
    def _update_progress(self, progress):
        """Update progress bar animation."""
        self.progress_value = (self.progress_value + 1) % 101
        progress.set_value(self.progress_value)
    
    def _show_toast(self):
        """Show a toast notification."""
        toast = CustomToast(
            parent=self,
            message="✅ This is a success notification!",
            toast_type="success",
            duration=3000,
            position="bottom-right",
        )
        toast.show_toast()


def main():
    """Run the demo application."""
    app = QApplication([])
    
    # Create and show main window
    window = NewComponentsDemo()
    window.show()
    
    app.exec()


if __name__ == "__main__":
    main()
