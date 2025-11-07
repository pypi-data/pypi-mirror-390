# Custom UI Components for PyQt6

[![PyPI version](https://badge.fury.io/py/custom-ui-pyqt6.svg)](https://badge.fury.io/py/custom-ui-pyqt6)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, reusable PyQt6 UI components with glassmorphism effects and smooth animations. Perfect for building beautiful, modern desktop applications with solid color theming.

## ✨ Features

🎨 **Modern Design**
- Solid color backgrounds with transparency effects
- Semi-transparent glassmorphism effects
- Smooth hover transitions and animations
- Professional typography and spacing

🎯 **User-Friendly**
- Draggable frameless windows
- Clear visual hierarchy
- Intuitive interactions
- Responsive visual feedback

🔄 **Reusable & Flexible**
- Easy to integrate into any PyQt6 project
- Highly customizable colors and styles
- Modular component architecture
- Well-documented with examples

🎨 **Solid Color Theming**
- Direct color assignment (no complex gradient setup)
- Runtime color updates
- Hex (#RRGGBB) and RGBA color support
- Consistent color palette across components

✨ **Expanded Component Library**
- **21 total components** (9 original + 12 new)
- **5 component categories**: Form, Display, Feedback, Layout, Original
- **Full customization** for all components
- **Multiple animation types**: smooth, bounce, elastic, none
- **Comprehensive signal system** for event handling

## 📦 Installation

Install from PyPI:
```bash
pip install custom-ui-pyqt6
```

Or install from source:
```bash
git clone https://github.com/yourusername/custom-ui-pyqt6.git
cd custom-ui-pyqt6
pip install -e .
```

## 🚀 Quick Start

### Basic Application

```python
import sys
from PyQt6.QtWidgets import QApplication
from custom_ui_package import CustomMainWindow, CustomTitleBar, CustomLabel, CustomButton

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My Application',
            width=600,
            height=500,
            bg_color='#1a0f2e'  # Solid color background
        )

        # Add custom title bar
        title_bar = CustomTitleBar(
            parent=self,
            title='My Application',
            bg_color='#7a00ff',
            text_color='#e8f0ff',
            font_size=16,
            bold=True
        )
        self.centralWidget().layout().insertWidget(0, title_bar)

        # Add content
        welcome_label = CustomLabel(
            parent=self.overlay_widget,
            text='Welcome to My App!',
            size=(300, 40),
            position=(40, 30),
            font_size=20,
            bold=True,
            color='#a855f7'
        )

        button = CustomButton(
            parent=self.content_widget,
            title='Get Started',
            size=(150, 45),
            font_size=12
        )
        button.clicked.connect(self.get_started)
        self.add_content(button)

        self.add_stretch()

    def get_started(self):
        print("Getting started!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

### Using New Components

```python
from custom_ui_package import (
    CustomTextArea, CustomCheckBox, CustomSlider,
    CustomProgressBar, CustomCard, CustomToast
)

# Multi-line text input
textarea = CustomTextArea(
    placeholder="Enter your text...",
    width=300, height=150,
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)"
)

# Checkbox with custom styling
checkbox = CustomCheckBox(
    label="Accept terms and conditions",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)"
)

# Range slider
slider = CustomSlider(
    min_value=0, max_value=100, current_value=50,
    track_color="rgba(168, 85, 247, 0.2)",
    groove_color="#a855f7"
)

# Progress bar
progress = CustomProgressBar(
    min_value=0, max_value=100, current_value=65,
    bg_color="rgba(168, 85, 247, 0.1)",
    progress_color="#a855f7"
)

# Card container
card = CustomCard(
    title="Information",
    width=300, height=200,
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)"
)

# Toast notification
toast = CustomToast(
    message="Operation completed successfully!",
    toast_type="success",
    duration=3000
)
toast.show_toast()
```

## 🎛️ Components

### CustomMainWindow

Frameless main window with solid color backgrounds and customizable styling.

```python
from custom_ui_package import CustomMainWindow

window = CustomMainWindow(
    title='My App',
    width=800,
    height=600,
    bg_color='#1a0f2e'  # Solid background color
)

# Runtime color updates
window.set_custom_colors({
    'button_color': '#ec4899',
    'text_primary': '#f3e8ff'
})
```

### CustomTitleBar

Custom title bar for frameless windows with configurable fonts and colors.

```python
from custom_ui_package import CustomTitleBar

title_bar = CustomTitleBar(
    parent=window,
    title="My Application",
    bg_color='#7a00ff',
    text_color='#e8f0ff',
    font_size=16,        # Custom font size
    bold=True,           # Bold text
    show_minimize=True,
    show_close=True
)
```

### CustomLabel

Configurable label with support for both layout-managed and absolute positioning.

```python
from custom_ui_package import CustomLabel

# Content area label (layout-managed)
content_label = CustomLabel(
    parent=self.content_widget,
    text="Hello World",
    size=(150, 30),
    font_size=12,
    bold=True
)
self.add_content(content_label)

# Overlay label (absolute positioning)
overlay_label = CustomLabel(
    parent=self.overlay_widget,
    text="Section Title",
    size=(200, 40),
    position=(40, 20),
    font_size=16,
    color='#a855f7'
)
```

### CustomButton

Modern button component with hover effects and custom styling.

```python
from custom_ui_package import CustomButton

button = CustomButton(
    parent=self.content_widget,
    title="Click Me",
    size=(150, 45),
    font_size=12,
    color='#ec4899'  # Custom button color
)
button.clicked.connect(self.handle_click)
self.add_content(button)
```

### CustomDropdown

Modern dropdown with glassmorphism effects and smooth animations.

```python
from custom_ui_package import CustomDropdown

dropdown = CustomDropdown()
dropdown.add_items_with_icons({
    'Python': 'python',
    'JavaScript': 'javascript',
    'Go': 'go'
})

# Customize colors
dropdown.set_custom_colors(
    bg_color='rgba(20, 25, 50, 0.8)',
    text_color='#e0e7ff',
    hover_color='#a78bfa'
)

selected_text = dropdown.get_selected_text()
```

### CustomMessageDialog

Modern message dialog with draggable interface and multiple dialog types.

```python
from custom_ui_package import CustomMessageDialog

# Different dialog types
info_dialog = CustomMessageDialog(
    'Information',
    'This is an info message',
    'info',
    parent_window
)

warning_dialog = CustomMessageDialog(
    'Warning',
    'This is a warning',
    'warning',
    parent_window
)

error_dialog = CustomMessageDialog(
    'Error',
    'This is an error',
    'error',
    parent_window
)

info_dialog.exec()
```

### CustomMenu

Context/application menu with glassmorphism effects, icons, and submenus.

```python
from custom_ui_package import CustomMenu

menu = CustomMenu(title='File')
menu.add_item('New', callback=lambda: print('New'))
menu.add_item('Open', callback=lambda: print('Open'))
menu.add_separator()
menu.add_item('Exit', callback=lambda: print('Exit'))

# With icons and shortcuts
menu.add_item('Copy', icon_path='copy.png', shortcut='Ctrl+C')
menu.add_item('Paste', icon_path='paste.png', shortcut='Ctrl+V')

# Submenu
submenu = menu.add_submenu('Recent Files')
submenu.add_item('File 1.txt')
submenu.add_item('File 2.txt')

# Checkable items
menu.add_item('Show Grid', checkable=True, checked=True)
```

### CustomScrollBar

Modern scrollbar with glassmorphism effects and smooth animations.

```python
from custom_ui_package import CustomMainWindow, CustomVerticalScrollBar

class MyScrollableApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Scrollable App',
            width=600,
            height=750,
            bg_color='#1a0f2e',
            use_custom_scrollbar=True,
            scrollbar_color='#a855f7',
            scrollbar_width=10
        )

# Or create manually
from custom_ui_package import CustomVerticalScrollBar

scrollbar = CustomVerticalScrollBar(
    handle_color='#a855f7',
    handle_width=10,
    border_radius=8,
    opacity=0.8
)
```

### 🎯 New Form Components

#### CustomTextArea

Multi-line text input with scrollbars and custom styling.

```python
from custom_ui_package import CustomTextArea

textarea = CustomTextArea(
    placeholder="Enter your text here...",
    width=300, height=150,
    shape="rounded_rectangle",  # rounded_rectangle, circular, custom_path
    animation_name="smooth",  # smooth, bounce, elastic, none
    bg_color="#1a1a2e",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)",
    hover_color="#a855f7",
    focus_color="#a855f7"
)

# Get/set text
text = textarea.get_text()
textarea.set_text("New text")

# Clear text
textarea.clear_text()

# Update colors at runtime
textarea.set_colors(
    bg_color="#0f0f1e",
    border_color="#a855f7"
)

# Signals: text_changed_custom, focus_in, focus_out
textarea.text_changed_custom.connect(on_text_changed)
```

#### CustomCheckBox

Checkbox with custom styling and animations.

```python
from custom_ui_package import CustomCheckBox

checkbox = CustomCheckBox(
    label="Accept terms and conditions",
    checked=False,
    size=20,
    shape="rounded",  # square, rounded, circle
    animation_name="smooth",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)",
    check_color="#a855f7"
)

# Get/set checked state
is_checked = checkbox.is_checked()
checkbox.set_checked(True)

# Update label
checkbox.set_label("New label text")

# Signals: state_changed_custom
checkbox.state_changed_custom.connect(on_state_changed)
```

#### CustomRadioButton

Radio button with custom styling and animations.

```python
from custom_ui_package import CustomRadioButton

radio = CustomRadioButton(
    label="Option 1",
    checked=False,
    size=20,
    animation_name="smooth",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)",
    check_color="#a855f7"
)

# Get/set checked state
is_checked = radio.is_checked()
radio.set_checked(True)

# Update label
radio.set_label("New option")

# Signals: toggled_custom
radio.toggled_custom.connect(on_toggled)
```

#### CustomSlider

Range slider with custom track and handle styling.

```python
from custom_ui_package import CustomSlider

slider = CustomSlider(
    min_value=0, max_value=100, current_value=50,
    width=300, height=30,
    handle_size=20, track_height=6,
    animation_name="smooth",
    track_color="rgba(168, 85, 247, 0.2)",
    groove_color="#a855f7",
    handle_color="#a855f7"
)

# Get/set value
value = slider.get_value()
slider.set_value(75)

# Set range
slider.set_range(0, 200)

# Signals: value_changed_custom, slider_moved_custom
slider.value_changed_custom.connect(on_value_changed)
```

#### CustomProgressBar

Progress indicator with animations.

```python
from custom_ui_package import CustomProgressBar

progress = CustomProgressBar(
    min_value=0, max_value=100, current_value=0,
    width=300, height=20,
    animation_name="smooth",
    bg_color="rgba(168, 85, 247, 0.1)",
    progress_color="#a855f7"
)

# Get/set progress
current = progress.get_value()
progress.set_value(75)

# Set percentage
progress.set_percentage(50)

# Signals: progress_changed_custom
progress.progress_changed_custom.connect(on_progress_changed)
```

### 🎯 New Display Components

#### CustomTabWidget

Tabbed interface with custom tab styling.

```python
from custom_ui_package import CustomTabWidget

tabs = CustomTabWidget(
    tab_height=40, tab_width=120,
    border_radius=8,
    animation_name="smooth",
    bg_color="#1a1a2e",
    tab_color="rgba(168, 85, 247, 0.2)",
    active_color="#a855f7"
)

# Add tabs
tab1_widget = QLabel("Tab 1 Content")
tabs.add_tab(tab1_widget, "Tab 1")

tab2_widget = QLabel("Tab 2 Content")
tabs.add_tab(tab2_widget, "Tab 2", icon=QIcon("tab2.png"))

# Remove tabs
tabs.remove_tab(0)

# Get tab info
current_index = tabs.get_current_index()
tab_count = tabs.get_tab_count()

# Signals: tab_changed_custom
tabs.tab_changed_custom.connect(on_tab_changed)
```

#### CustomCard

Card container with shadows and theming.

```python
from custom_ui_package import CustomCard

card = CustomCard(
    title="Card Title",
    width=300, height=200,
    border_radius=12,
    animation_name="smooth",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)",
    title_color="#ffffff",
    shadow_color="rgba(168, 85, 247, 0.2)",
    shadow_blur=12
)

# Set content
content_widget = QLabel("Card content")
card.set_content_widget(content_widget)

# Update title
card.set_title("New Title")
title = card.get_title()

# Signals: clicked_custom
card.clicked_custom.connect(on_card_clicked)
```

#### CustomBadge

Status badges/chips/tags widget.

```python
from custom_ui_package import CustomBadge

badge = CustomBadge(
    text="New",
    shape="pill",  # rounded, pill, square
    size="medium",  # small, medium, large
    closable=False,
    animation_name="smooth",
    bg_color="#a855f7",
    text_color="#ffffff"
)

# Update text
badge.set_text("Updated")
text = badge.get_text()

# Change appearance
badge.set_shape("rounded")
badge.set_size("large")
badge.set_closable(True)

# Signals: closed_custom, clicked_custom
badge.closed_custom.connect(on_badge_closed)
badge.clicked_custom.connect(on_badge_clicked)
```

#### CustomSpinner

Loading indicator with animations.

```python
from custom_ui_package import CustomSpinner

spinner = CustomSpinner(
    size=50, line_width=4,
    animation_speed=50,
    spinner_color="#a855f7",
    bg_color="rgba(168, 85, 247, 0.1)",
    animation_style="rotating"  # rotating, pulsing, bouncing
)

# Control animation
spinner.start()
spinner.stop()
is_running = spinner.is_running()

# Update appearance
spinner.set_colors("#c084fc", "rgba(192, 132, 252, 0.1)")
spinner.set_size(60)
spinner.set_animation_style("pulsing")
```

### 🎯 New Feedback Components

#### CustomToast

Notification/toast messages.

```python
from custom_ui_package import CustomToast

# Different toast types
toast = CustomToast(
    message="Operation completed successfully!",
    toast_type="success",  # info, success, warning, error
    duration=3000,
    position="bottom-right",  # top-left, top-right, bottom-left, bottom-right
    width=300,
    bg_color=None,  # Auto-set based on toast_type
    text_color="#ffffff"
)

# Show toast
toast.show_toast()

# Update message
toast.set_message("New message")

# Configure
toast.set_duration(5000)
toast.set_position("top-left")
```

#### CustomTooltip

Hover tooltips with custom styling.

```python
from custom_ui_package import CustomTooltip

tooltip = CustomTooltip(
    text="Helpful information about this element",
    delay=500,
    position="top",  # top, bottom, left, right
    width=200,
    border_radius=6,
    animation_name="smooth",
    bg_color="#2d2d44",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)"
)

# Show tooltip at widget position
tooltip.show_at(target_widget, offset_x=10, offset_y=10)

# Update text
tooltip.set_text("New tooltip text")

# Configure
tooltip.set_delay(1000)
tooltip.set_position("right")
```

### 🎯 New Layout Components

#### CustomAccordion

Collapsible panels/sections.

```python
from custom_ui_package import CustomAccordion

accordion = CustomAccordion(
    header_height=40,
    animation_name="smooth",
    bg_color="#1a1a2e",
    header_color="rgba(168, 85, 247, 0.2)",
    content_color="#0f0f1e",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)",
    hover_color="rgba(168, 85, 247, 0.4)"
)

# Add items
item1_content = QLabel("Content for section 1")
accordion.add_item("Section 1", item1_content)

item2_content = QLabel("Content for section 2")
accordion.add_item("Section 2", item2_content)

# Control items
accordion.expand_item(0)
accordion.collapse_item(1)
accordion.expand_all()
accordion.collapse_all()

# Get info
item_count = accordion.get_item_count()

# Signals: item_expanded, item_collapsed
accordion.item_expanded.connect(on_item_expanded)
accordion.item_collapsed.connect(on_item_collapsed)
```

## 🎨 Color Theming

### Solid Color System

The library now uses a simple solid color system instead of complex gradients:

```python
# Define colors directly
PRIMARY_COLOR = '#a855f7'
BACKGROUND_COLOR = '#1a0f2e'
TEXT_COLOR = '#f3e8ff'

# Use in components
window = CustomMainWindow(bg_color=BACKGROUND_COLOR)

title_bar = CustomTitleBar(
    bg_color=PRIMARY_COLOR,
    text_color=TEXT_COLOR
)

button = CustomButton(color=PRIMARY_COLOR)
```

### Color Formats Supported

- **Hex**: `#RRGGBB` (e.g., `#a855f7`)
- **RGBA**: `rgba(r, g, b, a)` (e.g., `rgba(168, 85, 247, 0.8)`)

### Runtime Color Updates

```python
# Update window colors
window.set_custom_colors({
    'button_color': '#ec4899',
    'text_primary': '#f3e8ff'
})

# Update component colors
dropdown.set_custom_colors(
    bg_color='rgba(20, 25, 50, 0.8)',
    text_color='#e0e7ff'
)

# Update scrollbar colors
scrollbar.update_colors(
    handle_color='#a855f7',
    background_color='#2d1b4e'
)
```

## 📋 Components Overview

### Original Components (9)
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `CustomMainWindow` | Main application window | Frameless, solid backgrounds, layout management |
| `CustomTitleBar` | Window title bar | Configurable fonts, colors, minimize/close buttons |
| `CustomButton` | Interactive buttons | Hover effects, custom colors, click handling |
| `CustomLabel` | Text display | Layout-managed or absolute positioning |
| `CustomDropdown` | Selection dropdown | Glassmorphism, icons, smooth animations |
| `CustomMessageDialog` | Message dialogs | Draggable, multiple types (info/warning/error) |
| `CustomMenu` | Context menus | Icons, submenus, checkable items, shortcuts |
| `CustomScrollBar` | Custom scrollbars | Glassmorphism, vertical/horizontal variants |

### New Form Components (5)
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `CustomTextArea` | Multi-line text input | Scrollbars, shapes, animations, shadows, custom colors |
| `CustomCheckBox` | Checkbox input | Multiple shapes, animations, hover effects, signals |
| `CustomRadioButton` | Radio button input | Circular shape, animations, radio groups, signals |
| `CustomSlider` | Range slider | Track/handle styling, animations, value range, signals |
| `CustomProgressBar` | Progress indicator | Percentage display, animations, custom colors, signals |

### New Display Components (4)
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `CustomTabWidget` | Tabbed interface | Custom tab styling, animations, icon support, signals |
| `CustomCard` | Card container | Shadow effects, hover animations, content areas, signals |
| `CustomBadge` | Status badges/tags | Multiple shapes/sizes, close button, hover effects, signals |
| `CustomSpinner` | Loading indicator | Multiple animation styles, continuous rotation, signals |

### New Feedback Components (2)
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `CustomToast` | Notification messages | Auto-dismiss, type-based colors, positioning, signals |
| `CustomTooltip` | Hover tooltips | Arrow pointing, delay, smooth animations, signals |

### New Layout Components (1)
| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `CustomAccordion` | Collapsible sections | Expand/collapse animations, multiple items, signals |

**Total: 21 Components**

## 📚 Documentation & Examples

- **[DOCUMENTATION.md](DOCUMENTATION.md)** - Complete user guide with detailed examples
- **[SETUP_AND_PUBLISHING.md](SETUP_AND_PUBLISHING.md)** - Setup and PyPI publishing guide
- **[CHANGELOG.md](CHANGELOG.md)** - Version history and updates

## 🔧 Requirements

- Python 3.8+
- PyQt6 >= 6.0.0

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/yourusername/custom-ui-pyqt6/issues).

---

**Happy building! 🚀**
