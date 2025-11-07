# Custom UI Components for PyQt6 - Complete Documentation

[![PyPI version](https://badge.fury.io/py/custom-ui-pyqt6.svg)](https://badge.fury.io/py/custom-ui-pyqt6)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Modern, reusable PyQt6 UI components with glassmorphism effects and smooth animations. Perfect for building beautiful, modern desktop applications.

---

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Component Reference](#component-reference)
   - **Original Components**
     - [CustomMainWindow](#custommainwindow)
     - [CustomTitleBar](#customtitlebar)
     - [CustomButton](#custombutton)
     - [CustomLabel](#customlabel)
     - [CustomInputBox](#custominputbox)
     - [CustomModal](#custommodal)
     - [CustomDropdown](#customdropdown)
     - [CustomMessageDialog](#custommessagedialog)
     - [CustomMenu](#custommenu)
     - [CustomScrollBar](#customscrollbar)
   - **New Form Components**
     - [CustomTextArea](#customtextarea)
     - [CustomCheckBox](#customcheckbox)
     - [CustomRadioButton](#customradiobutton)
     - [CustomSlider](#customslider)
     - [CustomProgressBar](#customprogressbar)
   - **New Display Components**
     - [CustomTabWidget](#customtabwidget)
     - [CustomCard](#customcard)
     - [CustomBadge](#custombadge)
     - [CustomSpinner](#customspinner)
   - **New Feedback Components**
     - [CustomToast](#customtoast)
     - [CustomTooltip](#customtooltip)
   - **New Layout Components**
     - [CustomAccordion](#customaccordion)
5. [CustomMainWindow Guide](#custommainwindow-guide)
6. [Theming System](#theming-system)
7. [Color Palette](#color-palette)
8. [Global Color Management](#global-color-management)
9. [Customization](#customization)
   - [CustomMainWindow Customization](#custommainwindow-customization)
   - [CustomTitleBar Customization](#customtitlebar-customization)
   - [CustomDropdown Customization](#customdropdown-customization)
   - [CustomMessageDialog Customization](#custommessagedialog-customization)
10. [Examples](#examples)
11. [Components Overview](#components-overview)
12. [Requirements](#requirements)
13. [Tips & Best Practices](#tips--best-practices)
14. [GUI Coding Guide - Parent Options & Positioning](#gui-coding-guide---parent-options--positioning)
    - [Understanding CustomMainWindow Structure](#understanding-custommainwindow-structure)
    - [Parent Options Explained](#parent-options-explained)
    - [Complete Positioning Reference](#complete-positioning-reference)
    - [Real-World Example: Token Setup Dialog](#real-world-example-token-setup-dialog)
    - [Best Practices Summary](#best-practices-summary)
15. [Contributing](#contributing)
16. [License](#license)

---

## Features

✨ **Modern Design**
- Solid color backgrounds
- Semi-transparent glassmorphism effects
- Smooth hover transitions
- Professional typography

🎯 **User-Friendly**
- Draggable windows
- Clear visual hierarchy
- Intuitive interactions
- Responsive feedback

🔄 **Reusable**
- Easy to integrate into any PyQt6 project
- Customizable colors and styles
- Modular components
- Well-documented

🎨 **Themeable**
- Runtime color customization
- Custom color support
- Flexible styling system
- Global color palette management

---

## Installation

### From PyPI

```bash
pip install custom-ui-pyqt6
```

### From Source

```bash
git clone https://github.com/yourusername/custom-ui-pyqt6.git
cd custom-ui-pyqt6
pip install -e .
```

---

## Quick Start

### Basic Window Setup

```python
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtGui import QFont
from custom_ui_package import CustomMainWindow

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My Application',
            width=600,
            height=750,
            # Single color background
            bg_color='#1a0f2e'
        )
        
        # Add content
        title = QLabel('Welcome!')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        self.add_content(title)
        
        btn = QPushButton('Click Me')
        self.add_content(btn)
        
        self.add_stretch()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

---

## Component Reference

### CustomMainWindow

A frameless main window with customizable styling. Does NOT include a default title bar - add `CustomTitleBar` manually if needed.

**Use Cases:**
- **Desktop Applications**: Main window for productivity apps, media players, or development tools
- **Settings Windows**: Configuration panels for application preferences and system settings  
- **Dashboard Interfaces**: Control panels for monitoring systems or business analytics
- **Media Applications**: Music players, video editors, or streaming interfaces
- **Development Tools**: IDE windows, code editors, or debugging consoles

**Constructor Parameters:**
```python
CustomMainWindow(
    title='Custom Window',           # Window title
    width=600,                       # Window width in pixels
    height=750,                      # Window height in pixels
    bg_color=None,                   # Background color (solid color only)
                                     # If None, uses global palette 'background' (#0a0e27)
    use_custom_scrollbar=False,      # Enable custom scrollbar styling
    scrollbar_color=None,            # Scrollbar handle color
    scrollbar_width=8,               # Scrollbar width in pixels
    content_margins=(40, 30, 40, 30),# Content area margins (left, top, right, bottom)
    content_spacing=15,              # Spacing between content widgets
    custom_colors=None               # Custom color overrides
)
```

**Color Behavior:**
- **When `bg_color=None`**: Uses global palette default `'background'` (#0a0e27)
- **Solid colors only**: All backgrounds use solid colors (no gradients)
- **No default title bar**: Add `CustomTitleBar` manually if needed

**Key Methods:**
- `add_content(widget)` - Add widget to content area
- `add_stretch()` - Add stretch to push content to top
- `set_title(title)` - Update window title
- `set_custom_colors(colors_dict)` - Override colors
- `get_theme_colors()` - Get current colors
- `set_content_margins(left, top, right, bottom)` - Set margins
- `set_content_spacing(spacing)` - Set widget spacing
- `create_custom_label(text, size, position, font_size, bold, color)` - Create positioned label

**Example:**
```python
from custom_ui_package import CustomMainWindow, CustomTitleBar

# Create main window with solid color background
window = CustomMainWindow(
    title='My App',
    width=700,
    height=600,
    bg_color='#1a0f2e'
)

# Add custom title bar manually
title_bar = CustomTitleBar(
    parent=window,
    title='My App',
    bg_color='#7a00ff',
    text_color='#e8f0ff'
)

layout = window.centralWidget().layout()
layout.insertWidget(0, title_bar)

# Use default colors (no parameters)
window = CustomMainWindow(
    title='My App',
    width=700,
    height=600
    # bg_color defaults to global palette
)

# Get current colors
colors = window.get_theme_colors()
print(colors['text_primary'])
```

---

### CustomModal

Reusable modal dialog for collecting setup inputs with built-in validation, customization options, and signal support.

**Use Cases:**
- **User Authentication**: Login screens with username/password fields and validation
- **Settings Configuration**: Application preferences and system settings dialogs
- **Data Entry Forms**: Contact forms, registration screens, or survey inputs
- **Confirmation Dialogs**: Delete confirmations, save prompts, or action verification
- **API Configuration**: Token setup, API key management, or service connections

**Features:**
- Frameless window with custom title bar
- Built-in CustomInputBox fields for various input types
- CustomButton for OK/Cancel actions
- Input validation (required fields, regex patterns, custom callbacks)
- Data collection and retrieval methods
- Extensive color customization
- Font customization
- Draggable title bar
- Dynamic field management
- Signal support for user interactions

**Constructor Parameters:**
```python
CustomModal(
    parent=None,                          # Parent widget
    title="Modal Dialog",                 # Modal title text
    width=500,                            # Modal width in pixels
    height=400,                           # Modal height in pixels
    fields=[],                            # List of field dictionaries (see below)
    ok_text="OK",                         # OK button text
    cancel_text="Cancel",                 # Cancel button text
    border_radius=12,                     # Border radius in pixels
    border_width=1,                       # Border width in pixels
    padding=20,                           # Inner padding in pixels
    spacing=16,                           # Spacing between elements
    animation_name="smooth",              # Animation: 'smooth', 'bounce', 'elastic', 'none'
    # Colors
    bg_color="#1a1a2e",                   # Background color (hex or rgba)
    border_color="rgba(168, 85, 247, 0.3)", # Border color (hex or rgba)
    title_color="#ffffff",                # Title text color (hex or rgba)
    title_bg_color="rgba(168, 85, 247, 0.1)", # Title background color
    label_color="#e8f0ff",                # Label text color (hex or rgba)
    # Fonts
    title_font_family="Segoe UI",         # Title font family
    title_font_size=14,                   # Title font size in pixels
    label_font_family="Segoe UI",         # Label font family
    label_font_size=11,                   # Label font size in pixels
    # Buttons
    ok_button_color="#a855f7",            # OK button background color
    ok_button_text_color="#ffffff",       # OK button text color
    cancel_button_color="rgba(168, 85, 247, 0.2)", # Cancel button background
    cancel_button_text_color="#e8f0ff",   # Cancel button text color
    button_height=40,                     # Button height in pixels
    button_width=120,                     # Button width in pixels
    button_font_size=11,                  # Font size for both buttons
    ok_button_bold=True,                  # Whether OK button text is bold
    cancel_button_bold=False,             # Whether Cancel button text is bold
    # Input boxes
    input_bg_color="#0f0f1e",             # Input box background color
    input_text_color="#ffffff",           # Input box text color
    input_border_color="rgba(168, 85, 247, 0.3)", # Input box border color
    input_focus_color="#a855f7",          # Input box focus color
    input_height=40,                      # Input box height in pixels
    # Validation
    validation_callback=None,             # Custom validation function
    validation_error_color="#ef4444",     # Error message color
    # Behavior
    modal=True,                           # Whether dialog is modal
    draggable=True,                       # Whether title bar is draggable
    closable=True                         # Whether close button is visible
)
```

**Field Dictionary Format:**
```python
{
    "name": "field_id",                    # Required: field identifier
    "label": "Display Label",              # Required: display label
    "type": "text",                        # Optional: text, password, email, number
    "placeholder": "Enter value",          # Optional: placeholder text
    "default_value": "initial",            # Optional: default value
    "required": True,                      # Optional: required field
    "validation_regex": r"^pattern$"       # Optional: regex validation
}
```

**Key Methods:**
- `get_inputs()` - Get all input values as dict
- `get_input(field_name)` - Get specific field value
- `set_input(field_name, value)` - Set specific field value
- `clear_inputs()` - Clear all input values
- `set_colors()` - Update colors at runtime
- `set_title()` - Set modal title
- `add_field()` - Add field dynamically
- `remove_field()` - Remove field dynamically

**Signals:**
- `accepted_custom` - Emitted with data dict when OK clicked
- `rejected_custom` - Emitted when Cancel clicked
- `input_changed` - Emitted when any input changes (field_name, value)

**Example:**
```python
from custom_ui_package import CustomModal

fields = [
    {"name": "username", "label": "Username", "type": "text", "required": True},
    {"name": "password", "label": "Password", "type": "password", "required": True},
    {"name": "email", "label": "Email", "type": "email"}
]

modal = CustomModal(
    parent=None,
    title="Login",
    width=500,
    height=350,
    fields=fields,
    ok_text="Login",
    cancel_text="Cancel"
)

modal.accepted_custom.connect(lambda data: print(f"Data: {data}"))

if modal.exec() == modal.DialogCode.Accepted:
    data = modal.get_inputs()
```

---

### CustomDropdown

A modern dropdown/combobox widget with glassmorphism effects.

**Use Cases:**
- **Language Selection**: Choose interface language or locale settings
- **Theme Selection**: Switch between light/dark modes or color schemes
- **File Format Selection**: Choose export formats (PDF, CSV, JSON, etc.)
- **Priority Levels**: Task priority selection (Low, Medium, High, Urgent)
- **Status Selection**: Workflow states (Draft, Review, Approved, Published)

**Variants:**
- `CustomDropdown` - Standard size
- `CustomDropdownCompact` - Compact size
- `CustomDropdownLarge` - Large size

**Key Methods:**
- `add_items_with_icons(items_dict)` - Add items with optional icons
- `get_selected_text()` - Get selected item text
- `get_selected_value()` - Get selected item value
- `set_custom_colors(bg_color, border_color, text_color, hover_color)` - Customize colors

**Example:**
```python
from custom_ui_package import CustomDropdown, CustomDropdownCompact, CustomDropdownLarge

# Standard dropdown
dropdown = CustomDropdown()
dropdown.add_items_with_icons({
    'Option 1': 'value1',
    'Option 2': 'value2',
    'Option 3': 'value3'
})

# Compact version
compact = CustomDropdownCompact()
compact.add_items_with_icons({'A': 'a', 'B': 'b'})

# Large version
large = CustomDropdownLarge()
large.add_items_with_icons({'Item 1': 'i1', 'Item 2': 'i2'})

# Custom colors
dropdown.set_custom_colors(
    bg_color='rgba(20, 25, 50, 0.8)',
    border_color='#7c3aed',
    text_color='#e0e7ff',
    hover_color='#a78bfa'
)

# Get selected value
selected_text = dropdown.get_selected_text()
selected_value = dropdown.get_selected_value()
```

---

### CustomMessageDialog

A modern message dialog with draggable interface and icon support.

**Use Cases:**
- **Error Notifications**: Display critical errors, validation failures, or system issues
- **Success Confirmations**: Show completion of operations like file saves or data submissions
- **Warning Alerts**: Alert users about potentially harmful actions or important notices
- **Information Messages**: Provide helpful tips, feature announcements, or status updates
- **Confirmation Prompts**: Ask for user acknowledgment before proceeding with actions

**Icon Types:**
- `'info'` - Information icon
- `'warning'` - Warning icon
- `'error'` - Error icon

**Example:**
```python
from custom_ui_package import CustomMessageDialog

# Info dialog
dialog = CustomMessageDialog(
    'Information',
    'This is an info message',
    'info',
    parent_widget
)
dialog.exec()

# Warning dialog
dialog = CustomMessageDialog(
    'Warning',
    'This is a warning message',
    'warning',
    parent_widget
)
dialog.exec()

# Error dialog
dialog = CustomMessageDialog(
    'Error',
    'This is an error message',
    'error',
    parent_widget
)
dialog.exec()
```

---

### CustomTitleBar

A modern custom title bar for frameless windows with configurable colors.

**Use Cases:**
- **Application Windows**: Main application windows with custom branding and controls
- **Dialog Windows**: Secondary windows for settings, preferences, or tool dialogs
- **Media Players**: Music/video player windows with custom title bars
- **Development Tools**: IDE windows, code editors, or debugging interfaces
- **System Utilities**: Configuration tools, system monitors, or admin panels

**Features:**
- Draggable window
- Minimize button (optional)
- Close button (optional)
- Icon support
- Custom title
- Configurable solid background colors

**Constructor Parameters:**
```python
CustomTitleBar(
    parent=None,                     # Parent widget
    title="Application",            # Title bar text
    icon_path=None,                  # Path to window icon
    show_minimize=True,              # Show minimize button
    show_close=True,                 # Show close button
    bg_color=None,                   # Background color (solid color only)
    text_color=None,                 # Title text color
    border_color=None,               # Border color
    border_bg=None,                  # Button hover background color
    font_size=13,                    # Font size for title text
    bold=True                        # Whether title text should be bold
)
```

**Example:**
```python
from custom_ui_package import CustomMainWindow, CustomTitleBar

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My Application',
            width=700,
            height=600,
            bg_color='#1a0f2e'
        )
        
        # Create and add custom title bar manually
        title_bar = CustomTitleBar(
            parent=self,
            title='My Application',
            icon_path=None,
            show_minimize=True,
            show_close=True,
            bg_color='#7a00ff',
            text_color='#e8f0ff',
            border_color='rgba(168, 85, 247, 0.3)',
            border_bg='rgba(168, 85, 247, 0.1)',
            font_size=16,
            bold=True
        )
        
        # Add title bar to the top of the layout
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        # Alternative: Smaller non-bold title bar
        # title_bar_small = CustomTitleBar(
        #     parent=self,
        #     title='Compact App',
        #     bg_color='#1a0f2e',
        #     text_color='#f3e8ff',
        #     font_size=12,
        #     bold=False,
        #     show_minimize=True,
        #     show_close=True
        # )
        # layout.insertWidget(0, title_bar_small)
        
        # Add your content here
        self.setup_ui()
    
    def setup_ui(self):
        # Add widgets to self.content_widget
        pass

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

### Compact Title Bar Example

```python
from custom_ui_package import CustomMainWindow, CustomTitleBar

class CompactApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Compact App',
            width=600,
            height=400,
            bg_color='#1a0f2e'
        )
        
        # Create compact title bar with smaller, non-bold text
        title_bar = CustomTitleBar(
            parent=self,
            title='Compact App',
            bg_color='#1a0f2e',
            text_color='#f3e8ff',
            font_size=12,
            bold=False,
            show_minimize=True,
            show_close=True
        )
        
        # Add title bar to the top of the layout
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        # Add content here
        self.setup_ui()
    
    def setup_ui(self):
        # Add compact content
        pass

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = CompactApp()
    window.show()
    sys.exit(app.exec())
```

---

### CustomButton

A reusable, fully‑configurable button widget.

**Use Cases:**
- **Form Submission**: Submit buttons for login, registration, or data entry forms
- **Navigation Controls**: Next/Previous buttons, menu toggles, or page navigation
- **Action Triggers**: Save, delete, export, or import operations
- **Dialog Controls**: OK/Cancel buttons in confirmation dialogs
- **Interactive Elements**: Play/pause controls, reset buttons, or action shortcuts

**Constructor Parameters:**
```python
CustomButton(
    parent=None,
    title="Button",
    size=(100, 30),   # width, height in pixels
    position=(0, 0),   # x, y coordinates (ignored when added via layout)
    font_size=10,
    color=None,        # Text color (hex or rgba). Uses global palette 'text' color if None
    bg_color=None,     # Background color (hex or rgba). Uses global palette 'primary' color if None
    bold=False         # Whether text should be bold
)
```

**Example Usage:**
```python
from custom_ui_package import CustomButton

# Basic button
btn = CustomButton(
    parent=self,
    title="Press Me",
    size=(150, 45),
    font_size=12
)
btn.clicked.connect(lambda: print("Custom button clicked!"))
self.add_content(btn)

# Button with custom color
btn_custom = CustomButton(
    parent=self,
    title="Custom Button",
    size=(150, 45),
    font_size=12,
    color="#13179c",
    bg_color="#dff9fb",
    bold=True
)
self.add_content(btn_custom)

# Button with overlay positioning
btn_overlay = CustomButton(
    parent=self.overlay_widget,
    title="Next",
    size=(160, 45),
    position=(169, 205),
    font_size=12,
    color="#13179c",
    bg_color="#dff9fb",
    bold=True
)
btn_overlay.clicked.connect(self.on_next)
```

---

### CustomLabel

A reusable, customizable label widget with global color palette support.

**Use Cases:**
- **Form Labels**: Field labels for input boxes, dropdowns, or checkboxes
- **Status Indicators**: Display current status, progress, or system state
- **Section Headers**: Title text for different sections or panels
- **Descriptive Text**: Instructions, help text, or contextual information
- **Dynamic Content**: Display changing values like counters, timers, or live data

**Constructor Parameters:**
```python
CustomLabel(
    parent=None,
    text="Label",
    size=(100, 30),      # width, height in pixels
    position=(0, 0),     # x, y coordinates
    font_size=10,
    bold=False,
    color=None           # Text color (uses global palette if None)
)
```

**Key Methods:**
- `set_position(x, y)` - Change label position at runtime

**Example Usage:**
```python
from custom_ui_package import CustomLabel

# 1. Content Area Label (Layout-managed positioning)
# Use this for labels that should flow with other content in the layout
label = CustomLabel(
    parent=self.content_widget,  # Parent is content widget
    text="Hello World",
    size=(150, 30),
    font_size=12,
    bold=True
)
self.add_content(label)  # Add to layout - position is automatic

# 2. Overlay Label (Absolute positioning)
# Use this for labels that need exact positioning (titles, headers, etc.)
overlay_label = CustomLabel(
    parent=self.overlay_widget,  # Parent is overlay widget
    text="Section Title",
    size=(200, 40),
    position=(40, 20),  # x, y coordinates - works in overlay
    font_size=16,
    bold=True,
    color='#a855f7'
)
# Don't call self.add_content() for overlay widgets

# 3. Custom Color Label
custom_label = CustomLabel(
    parent=self.content_widget,
    text="Custom Color Label",
    size=(200, 30),
    font_size=14,
    color='#ec4899'
)
self.add_content(custom_label)

# 4. Update position at runtime (for overlay labels only)
overlay_label.set_position(100, 50)
```

---

### CustomInputBox

A modern, fully customizable text input component with multiple shape options, animations, and shadow effects.

**Use Cases:**
- **User Credentials**: Username and password fields for login/authentication
- **Search Inputs**: Search bars for filtering content or finding items
- **Configuration Values**: API keys, tokens, or system configuration settings
- **Form Fields**: Contact information, addresses, or personal details
- **Data Entry**: Numeric values, codes, or identifiers with validation

**Features:**
- Multiple shape variants (rounded rectangle, circular, custom path)
- Full color customization (background, text, border, hover, focus, disabled, shadow)
- Animation support (smooth, bounce, elastic, none)
- Drop shadow effects with customizable blur and offset
- Custom signals for text changes and focus events
- Global color palette integration

**Constructor Parameters:**
```python
CustomInputBox(
    parent=None,                    # Parent widget
    placeholder="Enter text...",    # Placeholder text
    size=(200, 40),                 # (width, height) in pixels
    position=(0, 0),                # (x, y) position in parent
    font_size=11,                   # Font size in points
    shape="rounded_rectangle",      # Shape: "rounded_rectangle", "circular", "custom_path"
    border_radius=8,                # Border radius in pixels
    bg_color=None,                  # Background color (hex or rgba)
    text_color=None,                # Text color (hex or rgba)
    border_color=None,              # Border color (hex or rgba)
    hover_color=None,               # Hover state color (hex or rgba)
    focus_color=None,               # Focus state color (hex or rgba)
    disabled_color=None,            # Disabled state color (hex or rgba)
    animation_name="smooth",        # Animation: "smooth", "bounce", "elastic", "none"
    shadow_blur=10,                 # Shadow blur radius
    shadow_color=None,              # Shadow color (hex or rgba)
    shadow_offset=(0, 2),           # (x, y) shadow offset
    border_width=1,                 # Border width in pixels
    padding="8px 12px"              # Padding value
)
```

**Key Methods:**
- `get_text()` - Get current text value
- `set_text(text)` - Set text value
- `clear_text()` - Clear the input
- `set_colors(bg_color, text_color, border_color, hover_color, focus_color, disabled_color)` - Update colors
- `set_shape(shape)` - Change shape type
- `set_border_radius(radius)` - Update border radius
- `set_size(width, height)` - Change size
- `set_position(x, y)` - Change position
- `set_shadow(blur_radius, offset_x, offset_y, color)` - Update shadow
- `set_animation(animation_name)` - Change animation type
- `set_placeholder(text)` - Update placeholder text
- `is_focused()` - Check if input has focus

**Signals:**
- `text_changed_custom(str)` - Emitted when text changes
- `focus_in()` - Emitted when input gains focus
- `focus_out()` - Emitted when input loses focus

**Example Usage:**
```python
from custom_ui_package import CustomMainWindow, CustomInputBox

# Create main window
window = CustomMainWindow(
    title='Input Box Example',
    width=500,
    height=400,
    bg_color='#1a0f2e'
)
central_widget = window.centralWidget()

# Basic input box
input_box = CustomInputBox(
    parent=central_widget,
    placeholder="Enter your name...",
    size=(300, 40),
    font_size=11
)

# Input box with custom colors
input_custom = CustomInputBox(
    parent=central_widget,
    placeholder="Custom colors...",
    size=(300, 40),
    bg_color='#1a0f2e',
    text_color='#f3e8ff',
    border_color='rgba(168, 85, 247, 0.3)',
    hover_color='#a855f7',
    focus_color='#a855f7'
)

# Circular input box
input_circle = CustomInputBox(
    parent=central_widget,
    placeholder="Search",
    size=(150, 150),
    shape="circular",
    border_radius=75
)

# Connect to signals
input_box.text_changed_custom.connect(lambda text: print(f"Text: {text}"))
input_box.focus_in.connect(lambda: print("Input focused"))
input_box.focus_out.connect(lambda: print("Input unfocused"))

# Update at runtime
input_box.set_colors(
    bg_color='#2a1a4e',
    border_color='rgba(255, 100, 100, 0.5)',
    focus_color='#ff6464'
)

window.show()
```

**Shape Types:**
- `"rounded_rectangle"` - Rectangle with rounded corners (default)
- `"circular"` - Perfect circle (use square size)
- `"custom_path"` - Asymmetric borders for unique look

**Animation Types:**
- `"smooth"` - Smooth color transitions (default)
- `"bounce"` - Bounce effect on focus (framework ready)
- `"elastic"` - Elastic scaling effect (framework ready)
- `"none"` - No animation

---

### CustomMenu

A modern menu component with glassmorphism effects and smooth animations.

**Use Cases:**
- **Application Menus**: File, Edit, View, Help menus in desktop applications
- **Context Menus**: Right-click menus for specific items or areas
- **Toolbar Menus**: Dropdown menus attached to toolbar buttons
- **Navigation Menus**: Application navigation or section selection
- **Settings Panels**: Configuration options with checkable items

**Constructor Parameters:**
```python
CustomMenu(
    parent=None,
    title='',                          # Menu title
    bg_color=None,                     # Background color (uses global surface)
    text_color=None,                   # Text color (uses global text)
    hover_color=None,                  # Hover color (uses global primary)
    border_color=None,                 # Border color (uses global border)
    border_width=1,                    # Border width in pixels
    border_radius=8,                   # Border radius in pixels
    font_size=11,                      # Font size in pixels
    font_family='Segoe UI',            # Font family
    bold=False,                        # Bold font
    opacity=0.95,                      # Background opacity (0-1)
    icon_size=16,                      # Icon size in pixels
    item_height=32,                    # Menu item height
    item_padding=10,                   # Item padding in pixels
    animation_duration=150             # Animation duration in ms
)
```

**Key Methods:**
- `add_item(text, callback=None, icon_path=None, shortcut=None, enabled=True, checkable=False, checked=False)` - Add menu item
- `add_separator()` - Add separator line
- `add_submenu(title, parent=None)` - Add submenu
- `update_colors(bg_color, text_color, hover_color, border_color)` - Update colors at runtime
- `update_styling(font_size, font_family, bold, border_radius, item_height, item_padding)` - Update styling
- `set_opacity(opacity)` - Set background opacity
- `clear_items()` - Clear all items
- `get_item_by_text(text)` - Get item by text
- `enable_item(text, enabled)` - Enable/disable item
- `check_item(text, checked)` - Check/uncheck item
- `is_item_checked(text)` - Check if item is checked

**Signals:**
- `item_hovered(QAction)` - Emitted when item is hovered
- `item_clicked(QAction)` - Emitted when item is clicked

**Example Usage:**
```python
from custom_ui_package import CustomMenu

# Basic menu
menu = CustomMenu(title='File')
menu.add_item('New', callback=lambda: print('New'))
menu.add_item('Open', callback=lambda: print('Open'))
menu.add_separator()
menu.add_item('Exit', callback=lambda: print('Exit'))

# Custom colors
menu = CustomMenu(
    title='Edit',
    bg_color='#1a0f2e',
    text_color='#f3e8ff',
    hover_color='#a855f7',
    border_color='rgba(168, 85, 247, 0.3)'
)

# With icons and shortcuts
menu.add_item('Copy', icon_path='path/to/copy.png', shortcut='Ctrl+C')
menu.add_item('Paste', icon_path='path/to/paste.png', shortcut='Ctrl+V')

# Submenu
submenu = menu.add_submenu('Recent Files')
submenu.add_item('File 1.txt')
submenu.add_item('File 2.txt')

# Checkable items
menu.add_item('Show Grid', checkable=True, checked=True)

# Connect to signals
menu.item_clicked.connect(lambda action: print(f"Clicked: {action.text()}"))
```

---

### CustomScrollBar

A modern scrollbar component with glassmorphism effects.

**Use Cases:**
- **Long Content Areas**: Scroll through large documents, articles, or data lists
- **Data Tables**: Navigate through spreadsheet-like data or database results
- **Text Editors**: Scroll through code files, documents, or text content
- **Chat Interfaces**: Navigate through message history or conversation logs
- **Image Galleries**: Browse through photo collections or media libraries

**Constructor Parameters:**
```python
CustomScrollBar(
    orientation=Qt.Orientation.Vertical,  # Qt.Vertical or Qt.Horizontal
    parent=None,
    handle_color=None,                    # Handle color (uses global primary)
    handle_hover_color=None,              # Hover color (auto-lightened)
    background_color=None,                # Background color (uses global surface)
    border_color=None,                    # Border color (uses global border)
    border_width=1,                       # Border width in pixels
    border_radius=6,                      # Border radius in pixels
    handle_width=8,                       # Handle width (for vertical)
    handle_height=8,                      # Handle height (for horizontal)
    opacity=0.9,                          # Background opacity (0-1)
    hover_opacity=1.0,                    # Hover opacity (0-1)
    min_handle_size=20                    # Minimum handle size
)
```

**Variants:**
- `CustomScrollBar` - Generic scrollbar
- `CustomVerticalScrollBar` - Vertical scrollbar (convenience class)
- `CustomHorizontalScrollBar` - Horizontal scrollbar (convenience class)

**Key Methods:**
- `update_colors(handle_color, handle_hover_color, background_color, border_color)` - Update colors
- `update_styling(handle_width, handle_height, border_radius, opacity, hover_opacity)` - Update styling
- `set_opacity(opacity)` - Set background opacity
- `set_hover_opacity(opacity)` - Set hover opacity

**Example Usage:**
```python
from custom_ui_package import CustomMainWindow, CustomVerticalScrollBar

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My App',
            width=600,
            height=750,
            bg_color='#1a0f2e',
            use_custom_scrollbar=True,
            scrollbar_color='#a855f7',
            scrollbar_width=10
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Add content
        for i in range(50):
            self.add_content(CustomLabel(
                parent=self.content_widget,
                text=f"Item {i+1}",
                size=(200, 30),
                font_size=11
            ))

# Or create scrollbar manually
from custom_ui_package import CustomVerticalScrollBar

v_scrollbar = CustomVerticalScrollBar(
    handle_color='#a855f7',
    handle_width=10,
    border_radius=8,
    opacity=0.8,
    hover_opacity=1.0
)

# Update colors at runtime
v_scrollbar.update_colors(
    handle_color='#ec4899',
    background_color='#2d1b4e'
)

# Update styling at runtime
v_scrollbar.update_styling(
    handle_width=12,
  - Use consistent styling with your application theme

---

## CustomTextArea

### Creating a Custom Window

```python
from custom_ui_package import CustomMainWindow
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtGui import QFont
import sys

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My Application',
            width=600,
            height=750,
            bg_color='#1a0f2e'
        )
        
        # Add custom title bar
        from custom_ui_package import CustomTitleBar
        title_bar = CustomTitleBar(
            parent=self,
            title='My Application',
            bg_color='#7a00ff',
            text_color='#e8f0ff'
        )
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        # Add widgets
        self.setup_ui()
    
    def setup_ui(self):
        title = QLabel('Welcome to My App')
        title.setFont(QFont('Segoe UI', 20, QFont.Weight.Bold))
        self.add_content(title)
        
        btn = QPushButton('Click Me')
        btn.clicked.connect(self.on_button_click)
        self.add_content(btn)
        
        self.add_stretch()
    
    def on_button_click(self):
        print("Button clicked!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec())
```

### Layout Control

```python
# Set custom margins (left, top, right, bottom)
window.set_content_margins(50, 40, 50, 40)

# Set spacing between widgets
window.set_content_spacing(20)

# Add content
window.add_content(widget)

# Add stretch to push content to top
window.add_stretch()
```

---


## Theming System

### Configurable Colors

Custom UI components now support solid color configuration:

- **Solid Colors Only** - Use a single solid color for all backgrounds
- **Hex Format** - Standard hex color codes (#RRGGBB)
- **RGBA Format** - RGBA colors with transparency (rgba(r, g, b, a))

### Using Solid Colors

```python
from custom_ui_package import CustomMainWindow

# Create window with solid color background
window = CustomMainWindow(
    title='My App',
    width=600,
    height=750,
    bg_color='#1a0f2e'
)
```

### Custom Color Overrides

You can override specific colors:

```python
# Create with custom color overrides
custom_colors = {
    'button_color': '#ff6b6b',
    'button_hover_color': '#ff8787',
    'button_pressed_color': '#ee5a6f',
}

window = CustomMainWindow(
    title='My App',
    bg_color='#1a1a2e',
    custom_colors=custom_colors
)
```

### Global Color Palette

Define colors once and use them everywhere:

```python
from custom_ui_package import set_global_color_palette, get_global_color

# Set global palette at app startup
set_global_color_palette({
    'primary': '#a855f7',
    'secondary': '#e9d5ff',
    'background': '#1a0f2e',
    'surface': '#2d1b4e',
    'text': '#f3e8ff',
    'border': 'rgba(168, 85, 247, 0.3)',
    'border_hover': 'rgba(168, 85, 247, 0.1)',
})

# Use colors throughout your app
color = get_global_color('primary')
```

### Update Colors at Runtime

```python
# Change colors after window creation
new_colors = {
    'button_start': '#ff1493',
    'button_end': '#ff69b4',
}

window.set_custom_colors(new_colors)
```

### Get Current Theme Colors

```python
# Retrieve current color configuration
current_colors = window.get_theme_colors()
print(current_colors)

# Use colors for child widgets
colors = window.get_theme_colors()
label.setStyleSheet(f"color: {colors['text_primary']};")
```

---

## Color Palette

### Default Color Scheme

| Color | Hex | Usage |
|-------|-----|-------|
| Primary | #6366f1 | Indigo - Main buttons |
| Secondary | #4f46e5 | Purple - Secondary accent |
| Accent | #a5f3fc | Cyan - Secondary text |
| Background | #0a0e27 | Dark Blue - Window background |
| Text Primary | #e8f0ff | Light Blue - Main text |
| Text Secondary | #a5f3fc | Cyan - Secondary text |
| Warning | #eab308 | Yellow - Warning elements |
| Error | #ef4444 | Red - Error elements |
| Success | #10b981 | Green - Success elements |

### Color Keys Reference

All color dictionaries should include these keys:

| Key | Purpose |
|-----|---------|
| `bg_color` | Background color |
| `button_color` | Button color |
| `button_hover_color` | Button hover color |
| `button_pressed_color` | Button pressed color |
| `text_primary` | Primary text color |
| `text_secondary` | Secondary text color |
| `border_color` | Border color (usually with alpha) |
| `border_bg` | Border background color (usually with alpha) |

---

## Global Color Management

Centralize color management across your entire application using the global color palette system.

### Setting Global Colors

Define your color palette once at application startup:

```python
from custom_ui_package import set_global_color_palette, get_global_color

# Set global palette at app startup
set_global_color_palette({
    'primary': '#a855f7',
    'secondary': '#e9d5ff',
    'background': '#1a0f2e',
    'surface': '#2d1b4e',
    'text': '#f3e8ff',
    'border': 'rgba(168, 85, 247, 0.3)',
    'border_hover': 'rgba(168, 85, 247, 0.1)',
})
```

### Using Global Colors

Access colors throughout your application:

```python
from custom_ui_package import get_global_color

# Get a color from the global palette
primary_color = get_global_color('primary')
text_color = get_global_color('text', default='#ffffff')

# Use in components
label.setStyleSheet(f"color: {get_global_color('text')};")
```

### Benefits

- **Define Once, Use Everywhere** - Set colors once, use in all components
- **Easy Theme Switching** - Change entire theme by updating global palette
- **Consistent Styling** - Ensure color consistency across your app
- **Flexible Format Support** - Supports hex (#RRGGBB) and RGBA colors
- **Default Values** - Provide fallback colors if key not found

### Example: Theme Switching

```python
from custom_ui_package import set_global_color_palette

# Light theme
light_theme = {
    'primary': '#3b82f6',
    'background': '#ffffff',
    'text': '#1f2937',
}

# Dark theme
dark_theme = {
    'primary': '#a855f7',
    'background': '#1a0f2e',
    'text': '#f3e8ff',
}

# Switch themes at runtime
def switch_to_light():
    set_global_color_palette(light_theme)

def switch_to_dark():
    set_global_color_palette(dark_theme)
```

---

## Customization

### CustomMainWindow Customization

```python
from custom_ui_package import CustomMainWindow

window = CustomMainWindow(
    title='My App',
    width=700,
    height=600,
    bg_color='#1a0f2e'
)

# Add custom title bar
from custom_ui_package import CustomTitleBar
title_bar = CustomTitleBar(
    parent=window,
    title='My App',
    bg_color='#7a00ff',
    text_color='#e8f0ff'
)
layout = window.centralWidget().layout()
layout.insertWidget(0, title_bar)

# Customize layout
window.set_content_margins(50, 40, 50, 40)
window.set_content_spacing(20)

# Update colors
window.set_custom_colors({'button_color': '#ff69b4'})
```

### CustomTitleBar Customization

```python
from custom_ui_package import CustomTitleBar

title_bar = CustomTitleBar(
    parent=window,
    title='My Window',
    icon_path='path/to/icon.png',
    show_minimize=True,
    show_close=True,
    bg_color='#a855f7',
    text_color='#f3e8ff',
    border_color='rgba(168, 85, 247, 0.3)',
    border_bg='rgba(168, 85, 247, 0.1)',
    font_size=16,
    bold=True
)
```

### CustomDropdown Customization

```python
from custom_ui_package import CustomDropdown

dropdown = CustomDropdown()

# Add items with icons
dropdown.add_items_with_icons({
    'Docker': 'docker',
    'Python': 'python',
    'JavaScript': 'javascript'
})

# Customize colors
dropdown.set_custom_colors(
    bg_color='rgba(20, 25, 50, 0.8)',
    border_color='#7c3aed',
    text_color='#e0e7ff',
    hover_color='#a78bfa'
)

# Connect to selection change
dropdown.currentIndexChanged.connect(lambda: print(dropdown.get_selected_text()))
```

### CustomMessageDialog Customization

```python
from custom_ui_package import CustomMessageDialog, CustomMainWindow

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='My App',
            width=600,
            height=500,
            bg_color='#1a0f2e'
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Create different types of dialogs
        info_btn = CustomButton(
            parent=self.content_widget,
            title='Show Info',
            size=(120, 40),
            font_size=11
        )
        info_btn.clicked.connect(self.show_info)
        self.add_content(info_btn)
    
    def show_info(self):
        info_dialog = CustomMessageDialog(
            'Info',
            'This is an information message',
            'info',
            self
        )
        info_dialog.exec()

# Or create dialogs directly
warning_dialog = CustomMessageDialog(
    'Warning',
    'This is a warning message',
    'warning',
    parent_window
)
warning_dialog.exec()

error_dialog = CustomMessageDialog(
    'Error',
    'This is an error message',
    'error',
    parent_window
)
error_dialog.exec()
```

---

## Examples

### Example 1: Simple Application with Single Color

```python
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtGui import QFont
from custom_ui_package import CustomMainWindow, CustomLabel

class SimpleApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Simple App',
            width=500,
            height=400,
            bg_color='#1a0f2e'
        )
        
        # Using CustomLabel for consistent styling
        title = CustomLabel(
            parent=self.overlay_widget,
            text='Hello World!',
            size=(200, 40),
            position=(150, 50),
            font_size=18,
            bold=True,
            color='#f3e8ff'
        )
        
        btn = QPushButton('Say Hello')
        btn.clicked.connect(lambda: print('Hello!'))
        self.add_content(btn)
        
        self.add_stretch()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SimpleApp()
    window.show()
    sys.exit(app.exec())
```

### Example 2: Solid Color Background with Custom Title Bar

```python
import sys
from PyQt6.QtWidgets import QApplication, QPushButton, QLabel
from PyQt6.QtGui import QFont
from custom_ui_package import CustomMainWindow, CustomTitleBar, CustomLabel, CustomButton

class SolidColorApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Solid Color App',
            width=600,
            height=500,
            bg_color='#1a0f2e'
        )
        
        # Add custom title bar manually
        title_bar = CustomTitleBar(
            parent=self,
            title='Solid Color App',
            bg_color='#a855f7',
            text_color='#f3e8ff',
            show_minimize=True,
            show_close=True
        )
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        # Using CustomLabel for overlay
        title = CustomLabel(
            parent=self.overlay_widget,
            text='Beautiful Solid Color Background',
            size=(300, 40),
            position=(40, 20),
            font_size=16,
            bold=True,
            color='#f3e8ff'
        )
        
        # Add content
        description = CustomLabel(
            parent=self.content_widget,
            text='This window uses a solid color background',
            size=(400, 30),
            font_size=12,
            color='#a5f3fc'
        )
        self.add_content(description)
        
        btn = CustomButton(
            parent=self.content_widget,
            title='Click Me',
            size=(150, 45),
            font_size=12
        )
        btn.clicked.connect(lambda: print('Button clicked!'))
        self.add_content(btn)
        
        self.add_stretch()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SolidColorApp()
    window.show()
    sys.exit(app.exec())
```

### Example 3: Complete Application with Multiple Components

```python
import sys
from PyQt6.QtWidgets import QApplication
from custom_ui_package import (
    CustomMainWindow, CustomTitleBar, CustomDropdown, 
    CustomMessageDialog, CustomLabel, CustomButton
)

# Define colors directly
PRIMARY_COLOR = '#a855f7'
BACKGROUND_COLOR = '#1a0f2e'
TEXT_COLOR = '#f3e8ff'
SECONDARY_TEXT = '#a5f3fc'

class CompleteApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Complete App',
            width=600,
            height=700,
            bg_color=BACKGROUND_COLOR
        )
        
        # Add custom title bar
        title_bar = CustomTitleBar(
            parent=self,
            title='Complete App',
            bg_color=PRIMARY_COLOR,
            text_color=TEXT_COLOR,
            show_minimize=True,
            show_close=True
        )
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        # Title using CustomLabel
        title = CustomLabel(
            parent=self.overlay_widget,
            text='Select Your Options',
            size=(250, 40),
            position=(175, 20),
            font_size=20,
            bold=True,
            color=TEXT_COLOR
        )
        
        # Dropdown 1
        label1 = CustomLabel(
            parent=self.content_widget,
            text='Programming Language:',
            size=(200, 30),
            font_size=12,
            color=SECONDARY_TEXT
        )
        self.add_content(label1)
        
        dropdown1 = CustomDropdown()
        dropdown1.add_items_with_icons({
            'Python': 'python',
            'JavaScript': 'javascript',
            'Go': 'go'
        })
        self.add_content(dropdown1)
        
        # Dropdown 2
        label2 = CustomLabel(
            parent=self.content_widget,
            text='Framework:',
            size=(200, 30),
            font_size=12,
            color=SECONDARY_TEXT
        )
        self.add_content(label2)
        
        dropdown2 = CustomDropdown()
        dropdown2.add_items_with_icons({
            'Django': 'django',
            'Flask': 'flask',
            'FastAPI': 'fastapi'
        })
        self.add_content(dropdown2)
        
        # Submit button
        submit_btn = CustomButton(
            parent=self.content_widget,
            title='Submit',
            size=(150, 45),
            font_size=12
        )
        submit_btn.clicked.connect(
            lambda: self.show_selection(dropdown1, dropdown2)
        )
        self.add_content(submit_btn)
        
        self.add_stretch()
    
    def show_selection(self, dd1, dd2):
        msg = f"Language: {dd1.get_selected_text()}\nFramework: {dd2.get_selected_text()}"
        dialog = CustomMessageDialog('Selection', msg, 'info', self)
        dialog.exec()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CompleteApp()
    window.show()
    sys.exit(app.exec())
```

---

## New Components Documentation (v1.1.0+)

### CustomTextArea

Multi-line text input widget with custom styling, animations, and effects.

**Use Cases:**
- **Comments and Feedback**: User feedback forms, bug reports, or feature requests
- **Code Editors**: Basic code editing, configuration files, or script input
- **Long Text Input**: Articles, descriptions, or detailed notes
- **Message Composition**: Email drafts, forum posts, or chat messages
- **Configuration Files**: JSON/XML editing, settings files, or data templates

**Constructor Parameters:**
```python
CustomTextArea(
    parent=None,
    placeholder="Enter text...",
    width=300,
    height=150,
    shape="rounded_rectangle",  # rounded_rectangle, circular, custom_path
    border_radius=12,
    border_width=2,
    padding=12,
    animation_name="smooth",  # smooth, bounce, elastic, none
    bg_color="#1a1a2e",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)",
    hover_color="#a855f7",
    focus_color="#a855f7",
    disabled_color="rgba(168, 85, 247, 0.1)",
    shadow_color="rgba(168, 85, 247, 0.2)",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `get_text()` - Get current text
- `set_text(text)` - Set text
- `clear_text()` - Clear all text
- `set_colors()` - Update colors at runtime
- `set_animation(animation_name)` - Change animation type
- `set_placeholder(text)` - Update placeholder

**Signals:**
- `text_changed_custom` - Emitted when text changes
- `focus_in` - Emitted when widget gains focus
- `focus_out` - Emitted when widget loses focus

---

### CustomCheckBox

Checkbox widget with custom styling and animations.

**Use Cases:**
- **Feature Toggles**: Enable/disable application features or settings
- **Multiple Selection**: Choose multiple options from a list (interests, skills, etc.)
- **Settings Panels**: Application preferences, notification settings, or privacy options
- **Terms Acceptance**: Agree to terms of service, privacy policies, or user agreements
- **Filter Options**: Content filters, search criteria, or display preferences

**Constructor Parameters:**
```python
CustomCheckBox(
    parent=None,
    label="Option",
    checked=False,
    size=20,
    shape="rounded",  # square, rounded, circle
    border_width=2,
    animation_name="smooth",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)",
    check_color="#a855f7",
    hover_color="#a855f7",
    focus_color="#a855f7",
    disabled_color="rgba(168, 85, 247, 0.1)",
    text_color="#ffffff",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `is_checked()` - Check if checked
- `set_checked(checked)` - Set checked state
- `set_label(label)` - Update label text
- `set_size(size)` - Change checkbox size
- `set_colors()` - Update colors

**Signals:**
- `state_changed_custom` - Emitted when state changes

---

### CustomRadioButton

Radio button widget with custom styling and animations.

**Use Cases:**
- **Single Choice Selection**: Choose one option from mutually exclusive choices
- **Mode Switching**: Light/dark theme selection, view modes, or operation modes
- **Priority Selection**: Task priorities, importance levels, or urgency indicators
- **Payment Methods**: Credit card, PayPal, or bank transfer selection
- **Shipping Options**: Standard, express, or overnight delivery choices

**Constructor Parameters:**
```python
CustomRadioButton(
    parent=None,
    label="Option",
    checked=False,
    size=20,
    border_width=2,
    animation_name="smooth",
    bg_color="#1a1a2e",
    border_color="rgba(168, 85, 247, 0.3)",
    check_color="#a855f7",
    hover_color="#a855f7",
    focus_color="#a855f7",
    disabled_color="rgba(168, 85, 247, 0.1)",
    text_color="#ffffff",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `is_checked()` - Check if checked
- `set_checked(checked)` - Set checked state
- `set_label(label)` - Update label text
- `set_size(size)` - Change radio button size
- `set_colors()` - Update colors

**Signals:**
- `toggled_custom` - Emitted when toggled

---

### CustomSlider

Range slider with custom track and handle styling.

**Use Cases:**
- **Volume Controls**: Audio playback volume, system sound levels, or microphone sensitivity
- **Brightness Settings**: Screen brightness, display contrast, or lighting intensity
- **Progress Adjustment**: Task completion percentage, skill levels, or achievement progress
- **Value Selection**: Price ranges, age selection, or quantity controls
- **Parameter Tuning**: Application settings, game difficulty, or customization options

**Constructor Parameters:**
```python
CustomSlider(
    parent=None,
    orientation=Qt.Orientation.Horizontal,
    min_value=0,
    max_value=100,
    current_value=50,
    width=300,
    height=30,
    handle_size=20,
    track_height=6,
    animation_name="smooth",
    track_color="rgba(168, 85, 247, 0.2)",
    groove_color="#a855f7",
    handle_color="#a855f7",
    hover_color="#c084fc",
    focus_color="#a855f7",
    disabled_color="rgba(168, 85, 247, 0.1)"
)
```

**Key Methods:**
- `get_value()` / `set_value(value)` - Manage value
- `set_range(min_value, max_value)` - Set value range
- `set_colors()` - Update colors
- `set_handle_size(size)` - Change handle size
- `set_track_height(height)` - Change track height

**Signals:**
- `value_changed_custom` - Emitted when value changes
- `slider_moved_custom` - Emitted when slider is moved

---

### CustomProgressBar

Progress indicator with animations.

**Use Cases:**
- **File Upload Progress**: Document uploads, image transfers, or data synchronization
- **Installation Progress**: Software installation, updates, or system setup
- **Task Completion Status**: Long-running operations, batch processing, or data analysis
- **Download Progress**: File downloads, streaming content, or resource loading
- **Form Submission Progress**: Multi-step processes, validation, or data processing

**Constructor Parameters:**
```python
CustomProgressBar(
    parent=None,
    min_value=0,
    max_value=100,
    current_value=0,
    width=300,
    height=20,
    border_radius=10,
    animation_name="smooth",
    show_text=True,
    show_percentage=True,
    bg_color="rgba(168, 85, 247, 0.1)",
    progress_color="#a855f7",
    text_color="#ffffff",
    disabled_color="rgba(168, 85, 247, 0.05)",
    font_family="Segoe UI",
    font_size=10
)
```

**Key Methods:**
- `get_value()` / `set_value(value)` - Manage progress
- `get_percentage()` / `set_percentage(percentage)` - Percentage control
- `set_range(min_value, max_value)` - Set value range
- `set_colors()` - Update colors
- `set_text_visible(visible)` - Toggle text display

**Signals:**
- `progress_changed_custom` - Emitted when progress changes

---

### CustomTabWidget

Tabbed interface with custom tab styling.

**Use Cases:**
- **Application Sections**: Organize different app areas like Home, Profile, Settings, Help
- **Settings Categories**: Group related settings (General, Appearance, Security, Advanced)
- **Document Tabs**: Multiple open documents, files, or editing sessions
- **Content Categories**: Blog posts by category, products by type, or content by topic
- **Workflow Stages**: Multi-step processes, wizards, or guided experiences

**Constructor Parameters:**
```python
CustomTabWidget(
    parent=None,
    tab_height=40,
    tab_width=120,
    border_radius=8,
    animation_name="smooth",
    bg_color="#1a1a2e",
    tab_color="rgba(168, 85, 247, 0.2)",
    active_color="#a855f7",
    text_color="#ffffff",
    hover_color="rgba(168, 85, 247, 0.4)",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `add_tab(widget, label, icon)` - Add a tab
- `remove_tab(index)` - Remove a tab
- `get_current_index()` / `set_current_index(index)` - Manage active tab
- `get_tab_count()` - Get number of tabs
- `set_colors()` - Update colors
- `set_tab_size(width, height)` - Change tab size

**Signals:**
- `tab_changed_custom` - Emitted when active tab changes

---

### CustomCard

Card container with shadows, hover effects, and flexible content layout.

**Use Cases:**
- **User Profiles**: Display user information, avatars, and account details
- **Product Listings**: Showcase products with images, descriptions, and pricing
- **Dashboard Widgets**: Status panels, metrics cards, and summary information
- **Content Previews**: Article teasers, video thumbnails, or document summaries
- **Settings Panels**: Configuration options grouped in organized containers

**Constructor Parameters:**
```python
CustomCard(
    parent=None,                          # Parent widget
    title="Card Title",                   # Card title text
    width=300,                            # Card width in pixels
    height=200,                           # Card height in pixels
    border_radius=12,                     # Border radius in pixels
    border_width=1,                       # Border width in pixels
    padding=16,                           # Inner padding in pixels
    animation_name="smooth",              # Animation: 'smooth', 'bounce', 'elastic', 'none'
    bg_color="#1a1a2e",                   # Background color (hex or rgba)
    border_color="rgba(168, 85, 247, 0.3)", # Border color (hex or rgba)
    title_color="#ffffff",                # Title text color (hex or rgba)
    shadow_color="rgba(168, 85, 247, 0.2)", # Shadow color (hex or rgba)
    shadow_blur=12,                       # Shadow blur radius (default state)
    shadow_offset_x=0,                    # Shadow X offset in pixels
    shadow_offset_y=4,                    # Shadow Y offset in pixels
    hover_shadow_blur=20,                 # Shadow blur radius on hover
    font_family="Segoe UI",               # Font family name
    font_size=12                          # Font size in pixels
)
```

**Key Methods:**
- `set_title(title)` / `get_title()` - Manage card title
- `set_content_widget(widget)` - Set content widget (replaces existing)
- `set_colors(bg_color, border_color, title_color, shadow_color)` - Update colors at runtime
- `set_size(width, height)` - Change card dimensions
- `set_border_radius(radius)` - Update border radius
- `set_shadow(blur_radius, offset_x, offset_y, color)` - Update shadow properties
- `set_animation(animation_name)` - Change animation type

**Signals:**
- `clicked_custom` - Emitted when card is clicked

**Example Usage:**
```python
from custom_ui_package import CustomMainWindow, CustomCard, CustomLabel

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Card Example',
            width=600,
            height=500,
            bg_color='#0f0f1e'
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Basic card
        card = CustomCard(
            parent=self.content_widget,
            title="User Profile",
            width=300,
            height=250,
            border_radius=12,
            bg_color="#1a1a2e",
            title_color="#a855f7"
        )
        self.add_content(card)
        
        # Card with custom shadow
        shadow_card = CustomCard(
            parent=self.content_widget,
            title="Statistics",
            width=350,
            height=200,
            bg_color="#2d1b4e",
            border_color="#a855f7",
            title_color="#f3e8ff",
            shadow_color="#a855f7",
            shadow_blur=20,
            shadow_offset_y=8,
            hover_shadow_blur=30,
            animation_name="smooth"
        )
        self.add_content(shadow_card)
        
        # Card with content widget
        content_card = CustomCard(
            parent=self.content_widget,
            title="Details",
            width=400,
            height=300,
            bg_color="#1a1a2e",
            border_color="rgba(168, 85, 247, 0.5)"
        )
        
        # Add content to card
        content_label = CustomLabel(
            parent=content_card.content_widget,
            text="This is card content",
            size=(350, 30),
            font_size=12,
            color="#f3e8ff"
        )
        content_card.set_content_widget(content_label)
        self.add_content(content_card)
        
        # Connect click signal
        card.clicked_custom.connect(lambda: print("Card clicked!"))
        
        # Update card at runtime
        card.set_title("Updated Title")
        card.set_colors(
            bg_color="#2d1b4e",
            title_color="#ec4899"
        )
        card.set_shadow(25, 0, 10, "#ec4899")
```

**Shadow Behavior:**
- Default shadow is subtle for visual hierarchy
- Hover shadow increases blur for depth effect
- Shadow animates smoothly when hovering (if animation enabled)
- Shadow offset controls position relative to card

**Best Practices:**
- Use cards to group related information
- Keep card content concise and organized
- Use consistent shadow and border colors with theme
- Enable animations for better visual feedback
- Set appropriate padding for content readability
- Use `set_content_widget()` to add custom content

---

### CustomBadge

Status badges/chips/tags widget.

**Use Cases:**
- **Notification Counts**: Unread messages, pending tasks, or alert indicators
- **Status Indicators**: Online/offline status, approval states, or workflow stages
- **Tag Systems**: Content categories, skill tags, or interest labels
- **Priority Levels**: Task urgency, importance ranking, or severity indicators
- **Category Labels**: Product types, file formats, or content classifications

**Constructor Parameters:**
```python
CustomBadge(
    parent=None,
    text="Badge",
    shape="pill",  # rounded, pill, square
    size="medium",  # small, medium, large
    closable=False,
    animation_name="smooth",
    bg_color="#a855f7",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.5)",
    hover_color="#c084fc",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `set_text(text)` / `get_text()` - Manage badge text
- `set_colors()` - Update colors
- `set_shape(shape)` - Change shape
- `set_size(size)` - Change size
- `set_closable(closable)` - Toggle close button

**Signals:**
- `closed_custom` - Emitted when badge is closed
- `clicked_custom` - Emitted when badge is clicked

---

### CustomSpinner

Loading indicator with animations.

**Use Cases:**
- **Page Loading**: Website content loading or application startup screens
- **Background Tasks**: File processing, data synchronization, or batch operations
- **Data Processing**: Database queries, calculations, or analysis operations
- **File Operations**: Uploads, downloads, or file system operations
- **Network Requests**: API calls, server communication, or remote data fetching

**Constructor Parameters:**
```python
CustomSpinner(
    parent=None,
    size=50,
    line_width=4,
    animation_speed=50,
    spinner_color="#a855f7",
    bg_color="rgba(168, 85, 247, 0.1)",
    animation_style="rotating"  # rotating, pulsing, bouncing
)
```

**Key Methods:**
- `start()` / `stop()` - Control animation
- `is_running()` - Check animation state
- `set_colors(spinner_color, bg_color)` - Update colors
- `set_size(size)` - Change spinner size
- `set_animation_style(style)` - Change animation style
- `set_animation_speed(speed)` - Change animation speed

---

### CustomToast

Notification/toast messages with auto-dismiss and animations.

**Use Cases:**
- **Action Confirmations**: Successful save, delete, or update operations
- **Error Notifications**: Validation failures, connection issues, or system errors
- **Success Messages**: Completed tasks, successful submissions, or positive feedback
- **Warning Alerts**: Important notices, deprecated features, or caution messages
- **Status Updates**: Connection status, background task progress, or system alerts

**Constructor Parameters:**
```python
CustomToast(
    parent=None,                          # Parent widget (None for screen-level)
    message="Notification",               # Toast message text
    toast_type="info",                    # Type: 'info', 'success', 'warning', 'error'
    duration=3000,                        # Display duration in milliseconds (0 = no auto-dismiss)
    position="bottom-right",              # Position: 'top-left', 'top-right', 'bottom-left', 'bottom-right'
    width=300,                            # Toast width in pixels
    border_radius=8,                      # Border radius in pixels
    animation_name="smooth",              # Animation: 'smooth', 'bounce', 'elastic', 'none'
    bg_color=None,                        # Background color (hex/rgba). Auto-set by toast_type if None
    text_color="#ffffff",                 # Text color (hex or rgba)
    border_color=None,                    # Border color (hex/rgba). Auto-set by toast_type if None
    font_family="Segoe UI",               # Font family name
    font_size=11                          # Font size in pixels
)
```

**Key Methods:**
- `show_toast()` - Display the toast notification
- `set_message(message)` - Update toast message
- `get_message()` - Get current toast message
- `set_colors(bg_color, text_color, border_color)` - Update colors at runtime
- `set_duration(duration)` - Set display duration in milliseconds
- `set_position(position)` - Change toast position on screen
- `get_toast_type()` - Get toast type (info, success, warning, error)

**Toast Types & Auto-Colors:**
- `"info"` - Blue background (#0ea5e9), dark blue border (#0c4a6e)
- `"success"` - Green background (#10b981), dark green border (#064e3b)
- `"warning"` - Orange background (#f59e0b), dark orange border (#78350f)
- `"error"` - Red background (#ef4444), dark red border (#7f1d1d)

**Example Usage:**
```python
from custom_ui_package import CustomToast

# Basic info toast
toast = CustomToast(
    parent=None,
    message="Operation completed successfully!",
    toast_type="info",
    duration=3000,
    position="bottom-right"
)
toast.show_toast()

# Success toast with custom colors
success_toast = CustomToast(
    parent=None,
    message="File saved successfully",
    toast_type="success",
    duration=2000,
    position="top-right",
    width=350,
    font_size=12
)
success_toast.show_toast()

# Error toast with custom styling
error_toast = CustomToast(
    parent=None,
    message="An error occurred. Please try again.",
    toast_type="error",
    duration=4000,
    position="bottom-left",
    bg_color="#dc2626",
    text_color="#fecaca",
    border_color="#991b1b",
    border_radius=12,
    animation_name="smooth"
)
error_toast.show_toast()

# Warning toast without auto-dismiss
warning_toast = CustomToast(
    parent=None,
    message="This action cannot be undone",
    toast_type="warning",
    duration=0,  # No auto-dismiss
    position="top-center",
    font_size=13,
    bold=True
)
warning_toast.show_toast()

# Update toast at runtime
toast.set_message("New message")
toast.set_colors(bg_color="#1e40af", text_color="#dbeafe")
toast.set_duration(5000)
```

**Positioning Guide:**
- `"top-left"` - Upper left corner with 20px margin
- `"top-right"` - Upper right corner with 20px margin
- `"bottom-left"` - Lower left corner with 20px margin
- `"bottom-right"` - Lower right corner with 20px margin (default)

**Best Practices:**
- Use `parent=None` for screen-level toasts (recommended)
- Set `duration=0` for persistent toasts that require user action
- Use appropriate `toast_type` for visual feedback
- Keep messages concise (under 100 characters)
- Use `animation_name="none"` for immediate display

---

### CustomTooltip

Hover tooltips with custom styling.

**Use Cases:**
- **Help Text**: Explain button functions, form fields, or complex features
- **Field Explanations**: Describe input requirements, formats, or validation rules
- **Button Descriptions**: Clarify action buttons, toolbar icons, or menu items
- **Context Information**: Show additional details about data, status, or options
- **Guided Assistance**: Provide onboarding tips, tutorials, or feature highlights

**Constructor Parameters:**
```python
CustomTooltip(
    parent=None,
    text="Tooltip",
    delay=500,
    position="top",  # top, bottom, left, right
    width=200,
    border_radius=6,
    animation_name="smooth",
    bg_color="#2d2d44",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)",
    font_family="Segoe UI",
    font_size=10
)
```

**Key Methods:**
- `show_at(widget, offset_x, offset_y)` - Show tooltip at widget
- `set_text(text)` - Update tooltip text
- `set_colors()` - Update colors
- `set_delay(delay)` - Set show delay
- `set_position(position)` - Change position

---

### CustomAccordion

Collapsible panels/sections.

**Use Cases:**
- **FAQ Sections**: Frequently asked questions with expandable answers
- **Settings Panels**: Application preferences organized in collapsible groups
- **Navigation Menus**: Multi-level navigation with expandable categories
- **Content Organization**: Articles, tutorials, or documentation divided into sections
- **Form Wizards**: Multi-step forms with collapsible sections for better UX

**Constructor Parameters:**
```python
CustomAccordion(
    parent=None,
    header_height=40,
    animation_name="smooth",
    bg_color="#1a1a2e",
    header_color="rgba(168, 85, 247, 0.2)",
    content_color="#0f0f1e",
    text_color="#ffffff",
    border_color="rgba(168, 85, 247, 0.3)",
    hover_color="rgba(168, 85, 247, 0.4)",
    font_family="Segoe UI",
    font_size=11
)
```

**Key Methods:**
- `add_item(title, content_widget)` - Add accordion item
- `expand_item(index)` / `collapse_item(index)` - Control item state
- `expand_all()` / `collapse_all()` - Control all items
- `set_colors()` - Update colors
- `get_item_count()` - Get number of items

**Signals:**
- `item_expanded` - Emitted when item is expanded
- `item_collapsed` - Emitted when item is collapsed

---

## Components Overview

### Original Components (10)
| Component | Purpose | Features |
|-----------|---------|----------|
| `CustomMainWindow` | Main application window | Frameless, custom title bar, themeable, draggable |
| `CustomTitleBar` | Window title bar | Minimize/close buttons, draggable, icon support |
| `CustomButton` | Reusable button widget | Configurable size, font, position, global color support |
| `CustomLabel` | Reusable label widget | Configurable text, size, position, bold, global color support |
| `CustomInputBox` | Text input widget | Multiple shapes, animations, shadow effects, custom colors, signals |
| `CustomModal` | Modal dialog for input collection | Built-in validation, customizable fields, draggable, signal support |
| `CustomDropdown` | Standard dropdown | Glassmorphism, smooth animations, custom colors |
| `CustomMessageDialog` | Message dialog | Frameless, draggable, icon support |
| `CustomMenu` | Context/application menu | Glassmorphism, icons, submenus, checkable items, custom colors |
| `CustomScrollBar` | Custom scrollbar | Glassmorphism, smooth animations, vertical/horizontal |

### New Form Components (5)
| Component | Purpose | Features |
|-----------|---------|----------|
| `CustomTextArea` | Multi-line text input | Scrollbars, shapes, animations, shadows, custom colors |
| `CustomCheckBox` | Checkbox input | Multiple shapes, animations, hover effects, signals |
| `CustomRadioButton` | Radio button input | Circular shape, animations, radio groups, signals |
| `CustomSlider` | Range slider | Track/handle styling, animations, value range, signals |
| `CustomProgressBar` | Progress indicator | Percentage display, animations, custom colors, signals |

### New Display Components (4)
| Component | Purpose | Features |
|-----------|---------|----------|
| `CustomTabWidget` | Tabbed interface | Custom tab styling, animations, icon support, signals |
| `CustomCard` | Card container | Shadow effects, hover animations, content areas, signals |
| `CustomBadge` | Status badges/tags | Multiple shapes/sizes, close button, hover effects, signals |
| `CustomSpinner` | Loading indicator | Multiple animation styles, continuous rotation, signals |

### New Feedback Components (2)
| Component | Purpose | Features |
|-----------|---------|----------|
| `CustomToast` | Notification messages | Auto-dismiss, type-based colors, positioning, signals |
| `CustomTooltip` | Hover tooltips | Arrow pointing, delay, smooth animations, signals |

### New Layout Components (1)
| Component | Purpose | Features |
|-----------|---------|----------|
| `CustomAccordion` | Collapsible sections | Expand/collapse animations, multiple items, signals |

**Total: 22 Components**

---

## Requirements

- Python 3.8+
- PyQt6 >= 6.0.0

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

If you encounter any issues or have questions, please open an issue on the [GitHub repository](https://github.com/yourusername/custom-ui-pyqt6/issues).

---

## Tips & Best Practices

- Use `get_theme_colors()` to access current colors for styling child widgets
- Use `set_global_color_palette()` at app startup to define colors once
- Color values support both hex (#RRGGBB) and rgba() formats
- For gradient backgrounds, provide both `bg_color` and `bg_color_end`
- For single color backgrounds, only provide `bg_color`
- Custom colors override default colors without replacing the entire theme

---

## GUI Coding Guide - Parent Options & Positioning

This guide explains how to effectively use different parent options and positioning strategies when building GUIs with CustomMainWindow.

### Understanding CustomMainWindow Structure

CustomMainWindow provides two main areas for placing widgets:

```
┌─────────────────────────────────────────┐
│         CustomMainWindow                │
├─────────────────────────────────────────┤
│  ┌───────────────────────────────────┐  │
│  │   content_widget (Layout Area)    │  │
│  │  - Managed by QVBoxLayout         │  │
│  │  - Widgets stack vertically       │  │
│  │  - Position parameter ignored     │  │
│  │  - Use add_content() to add       │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  overlay_widget (Absolute Area)   │  │
│  │  - Absolute positioning           │  │
│  │  - Position parameter works       │  │
│  │  - Don't call add_content()       │  │
│  │  - Floats above content_widget    │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Parent Options Explained

#### Option 1: `parent=self.content_widget` (Layout-Managed)

**Use this when:** You want widgets to flow vertically in a layout, automatically stacking.

**Characteristics:**
- Widgets are managed by a QVBoxLayout
- Position parameter is **ignored**
- Widgets stack vertically
- Must call `self.add_content(widget)` to add to layout
- Responsive to window resizing

**Example:**
```python
from custom_ui_package import CustomMainWindow, CustomButton, CustomLabel

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Layout Example',
            width=600,
            height=400,
            bg_color='#1a0f2e'
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Button 1 - will be at top
        btn1 = CustomButton(
            parent=self.content_widget,
            title="Button 1",
            size=(150, 45),
            font_size=12
        )
        self.add_content(btn1)
        
        # Button 2 - will be below Button 1
        btn2 = CustomButton(
            parent=self.content_widget,
            title="Button 2",
            size=(150, 45),
            font_size=12
        )
        self.add_content(btn2)
        
        # Label - will be below Button 2
        label = CustomLabel(
            parent=self.content_widget,
            text="This is a label",
            size=(200, 30),
            font_size=11
        )
        self.add_content(label)
```

**When to use:**
- Forms with multiple input fields
- Lists of items
- Sequential content
- Responsive layouts

---

#### Option 2: `parent=self.overlay_widget` (Absolute Positioning)

**Use this when:** You need exact pixel-perfect positioning for widgets.

**Characteristics:**
- Widgets use absolute positioning
- Position parameter **works correctly**
- Floats above the content_widget
- Don't call `self.add_content()` - it will override positioning
- Fixed positioning (doesn't respond to window resizing)

**Example:**
```python
from custom_ui_package import CustomMainWindow, CustomButton, CustomLabel, CustomInputBox

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Overlay Example',
            width=600,
            height=400,
            bg_color='#1a0f2e'
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Title at top-left
        title = CustomLabel(
            parent=self.overlay_widget,
            text="Token Setup",
            size=(200, 40),
            position=(20, 20),  # x=20, y=20
            font_size=16,
            bold=True,
            color='#a855f7'
        )
        
        # Input box below title
        input_box = CustomInputBox(
            parent=self.overlay_widget,
            placeholder="Enter token...",
            size=(300, 45),
            position=(150, 80),  # x=150, y=80
            font_size=12
        )
        
        # Button at bottom-right
        btn = CustomButton(
            parent=self.overlay_widget,
            title="Submit",
            size=(150, 45),
            position=(225, 320),  # x=225, y=320
            font_size=12
        )
        btn.clicked.connect(self.on_submit)
    
    def on_submit(self):
        print("Form submitted!")
```

**When to use:**
- Dialog boxes with fixed layouts
- Setup/wizard screens
- Floating buttons or panels
- Exact positioning requirements

---

#### Option 3: `parent=self` (Window-Level)

**Use this when:** You want widgets added to the main window but managed by layout.

**Characteristics:**
- Equivalent to `parent=self.content_widget` with `add_content()`
- Position parameter is **ignored**
- Widgets are layout-managed
- Must call `self.add_content(widget)` to add to layout

**Example:**
```python
from custom_ui_package import CustomMainWindow, CustomButton

class MyApp(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Window Parent Example',
            width=600,
            height=400,
            bg_color='#1a0f2e'
        )
        self.setup_ui()
    
    def setup_ui(self):
        # Using parent=self (same as parent=self.content_widget)
        btn = CustomButton(
            parent=self,
            title="Click Me",
            size=(150, 45),
            font_size=12
        )
        self.add_content(btn)
```

**When to use:**
- Simple layouts
- When you don't need to distinguish between content and overlay
- Standard form applications

---

#### Option 4: `parent=None` (Standalone Widget)

**Use this when:** You're creating widgets outside of a window context.

**Characteristics:**
- Widget is not attached to any parent
- Position parameter works but widget won't be visible until parented
- Useful for creating reusable widget instances

**Example:**
```python
from custom_ui_package import CustomButton

# Create button without parent
btn = CustomButton(
    parent=None,
    title="Standalone",
    size=(150, 45),
    font_size=12
)

# Later, add it to a window
window.add_content(btn)
```

---

### Complete Positioning Reference

| Parent Option | Position Works? | Layout Managed? | Add to Layout? | Use Case |
|---|---|---|---|---|
| `self.content_widget` | ❌ No | ✅ Yes | ✅ Yes | Vertical stacking |
| `self.overlay_widget` | ✅ Yes | ❌ No | ❌ No | Absolute positioning |
| `self` | ❌ No | ✅ Yes | ✅ Yes | Simple layouts |
| `None` | ✅ Yes | ❌ No | Later | Standalone widgets |

---

### Real-World Example: Token Setup Dialog

```python
from custom_ui_package import CustomMainWindow, CustomTitleBar, CustomInputBox, CustomButton, CustomLabel

class TokenSetupWindow(CustomMainWindow):
    def __init__(self):
        super().__init__(
            title='Token Setup',
            width=550,
            height=350,
            bg_color='#041d1e'
        )
        
        # Add title bar
        title_bar = CustomTitleBar(
            parent=self,
            title='NotionPresence v1.0.2 Token Setup',
            bg_color='#13179c',
            text_color='#dff9fb',
            font_size=16,
            bold=True,
            show_minimize=True,
            show_close=True
        )
        
        layout = self.centralWidget().layout()
        layout.insertWidget(0, title_bar)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Use overlay_widget for absolute positioning
        
        # Discord Token Label
        discord_label = CustomLabel(
            parent=self.overlay_widget,
            text="Discord Token:",
            size=(150, 30),
            position=(40, 80),
            font_size=12,
            bold=True,
            color='#dff9fb'
        )
        
        # Discord Token Input
        self.discord_input = CustomInputBox(
            parent=self.overlay_widget,
            placeholder="Enter Discord Token",
            size=(300, 45),
            position=(200, 75),
            font_size=12
        )
        
        # Notion Token Label
        notion_label = CustomLabel(
            parent=self.overlay_widget,
            text="Notion Token:",
            size=(150, 30),
            position=(40, 160),
            font_size=12,
            bold=True,
            color='#dff9fb'
        )
        
        # Notion Token Input
        self.notion_input = CustomInputBox(
            parent=self.overlay_widget,
            placeholder="Enter Notion Integration Token",
            size=(300, 45),
            position=(200, 155),
            font_size=12
        )
        
        # Next Button
        next_btn = CustomButton(
            parent=self.overlay_widget,
            title="Next",
            size=(150, 45),
            position=(200, 270),
            font_size=12,
            color="#13179c",
            bg_color="#dff9fb",
            bold=True
        )
        next_btn.clicked.connect(self.on_next)
    
    def on_next(self):
        discord_token = self.discord_input.get_text()
        notion_token = self.notion_input.get_text()
        
        if discord_token and notion_token:
            print(f"Tokens received: {discord_token}, {notion_token}")
            self.close()
        else:
            print("Please fill in all fields")

if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = TokenSetupWindow()
    window.show()
    sys.exit(app.exec())
```

---

### Best Practices Summary

1. **Choose the right parent:**
   - Use `self.overlay_widget` for dialogs and fixed layouts
   - Use `self.content_widget` for responsive, flowing layouts
   - Use `self` for simple cases

2. **Position parameter:**
   - Only works with `self.overlay_widget` or `parent=None`
   - Ignored when using `self.content_widget` or `self` with `add_content()`

3. **Adding to layout:**
   - Always call `self.add_content()` for content_widget widgets
   - Never call `self.add_content()` for overlay_widget widgets
   - Overlay widgets are automatically displayed

4. **Coordinate system:**
   - Position (0, 0) is top-left of the parent widget
   - X increases to the right
   - Y increases downward
   - Use pixel values for precise positioning

5. **Responsive design:**
   - Use content_widget for responsive layouts
   - Use overlay_widget for fixed UI elements
   - Combine both for complex UIs

6. **Common mistakes to avoid:**
   - ❌ Using `position` with `self.content_widget`
   - ❌ Calling `add_content()` on overlay_widget widgets
   - ❌ Forgetting to call `add_content()` for content_widget widgets
   - ❌ Using overlay_widget for all widgets (not responsive)
- For better UX, use consistent spacing and margins across your application
- Consider using the same color palette throughout your application for visual consistency
- Test your custom colors with different lighting conditions
- Use RGBA colors for transparency effects (e.g., borders with alpha channel)

---

## CustomModal

Reusable modal dialog for collecting setup inputs with validation and customization.

**Constructor Parameters:**
```python
CustomModal(
    parent=None,                          # Parent widget
    title="Modal Dialog",                 # Modal title text
    width=500,                            # Modal width in pixels
    height=400,                           # Modal height in pixels
    fields=[],                            # List of field dictionaries (see below)
    ok_text="OK",                         # OK button text
    cancel_text="Cancel",                 # Cancel button text
    border_radius=12,                     # Border radius in pixels
    border_width=1,                       # Border width in pixels
    padding=20,                           # Inner padding in pixels
    spacing=16,                           # Spacing between elements
    animation_name="smooth",              # Animation: 'smooth', 'bounce', 'elastic', 'none'
    # Colors
    bg_color="#1a1a2e",                   # Background color (hex or rgba)
    border_color="rgba(168, 85, 247, 0.3)", # Border color (hex or rgba)
    title_color="#ffffff",                # Title text color (hex or rgba)
    title_bg_color="rgba(168, 85, 247, 0.1)", # Title background color
    label_color="#e8f0ff",                # Label text color (hex or rgba)
    # Fonts
    title_font_family="Segoe UI",         # Title font family
    title_font_size=14,                   # Title font size in pixels
    label_font_family="Segoe UI",         # Label font family
    label_font_size=11,                   # Label font size in pixels
    # Buttons
    ok_button_color="#a855f7",            # OK button background color
    ok_button_text_color="#ffffff",       # OK button text color
    cancel_button_color="rgba(168, 85, 247, 0.2)", # Cancel button background
    cancel_button_text_color="#e8f0ff",   # Cancel button text color
    button_height=40,                     # Button height in pixels
    button_width=120,                     # Button width in pixels
    button_font_size=11,                  # Font size for both buttons
    ok_button_bold=True,                  # Whether OK button text is bold
    cancel_button_bold=False,             # Whether Cancel button text is bold
    # Input boxes
    input_bg_color="#0f0f1e",             # Input box background color
    input_text_color="#ffffff",           # Input box text color
    input_border_color="rgba(168, 85, 247, 0.3)", # Input box border color
    input_focus_color="#a855f7",          # Input box focus color
    input_height=40,                      # Input box height in pixels
    # Validation
    validation_callback=None,             # Custom validation function
    validation_error_color="#ef4444",     # Error message color
    # Behavior
    modal=True,                           # Whether dialog is modal
    draggable=True,                       # Whether title bar is draggable
    closable=True                         # Whether close button is visible
)
```

**Field Dictionary Format:**
```python
{
    "name": "username",                   # Field identifier (required)
    "label": "Username",                  # Display label (required)
    "type": "text",                       # 'text', 'password', 'email', 'number'
    "placeholder": "Enter username",      # Placeholder text (optional)
    "default_value": "",                  # Default value (optional)
    "required": True,                     # Whether field is required (optional)
    "validation_regex": r"^[a-zA-Z0-9_]+$"  # Regex pattern for validation (optional)
}
```

**Key Methods:**
- `get_inputs()` - Get all input values as dictionary
- `get_input(field_name)` - Get specific field value
- `set_input(field_name, value)` - Set specific field value
- `clear_inputs()` - Clear all input values
- `set_colors(bg_color, border_color, title_color, label_color)` - Update colors
- `set_title(title)` - Set modal title
- `add_field(field)` - Add new field dynamically
- `remove_field(field_name)` - Remove field dynamically

**Signals:**
- `accepted_custom` - Emitted when OK clicked with valid inputs (emits data dict)
- `rejected_custom` - Emitted when Cancel clicked
- `input_changed` - Emitted when any input changes (emits field_name, value)

**Example Usage:**
```python
from custom_ui_package import CustomModal

# Define fields
fields = [
    {
        "name": "username",
        "label": "Username",
        "type": "text",
        "placeholder": "Enter username",
        "required": True
    },
    {
        "name": "password",
        "label": "Password",
        "type": "password",
        "placeholder": "Enter password",
        "required": True
    },
    {
        "name": "email",
        "label": "Email",
        "type": "email",
        "placeholder": "user@example.com",
        "validation_regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    }
]

# Create modal
modal = CustomModal(
    parent=None,
    title="Login",
    width=500,
    height=350,
    fields=fields,
    ok_text="Login",
    cancel_text="Cancel"
)

# Connect signals
modal.accepted_custom.connect(lambda data: print(f"Inputs: {data}"))
modal.rejected_custom.connect(lambda: print("Cancelled"))
modal.input_changed.connect(lambda name, value: print(f"{name}: {value}"))

# Show modal
if modal.exec() == modal.DialogCode.Accepted:
    data = modal.get_inputs()
    print(f"Username: {data['username']}")
    print(f"Password: {data['password']}")
```

**Custom Validation Example:**
```python
def validate_inputs(data):
    """Custom validation function"""
    if len(data['password']) < 8:
        print("Password must be at least 8 characters")
        return False
    return True

modal = CustomModal(
    parent=None,
    title="Setup",
    fields=fields,
    validation_callback=validate_inputs
)
```

**Dynamic Field Management:**
```python
modal = CustomModal(parent=None, title="Dynamic Modal", fields=[])

# Add fields dynamically
modal.add_field({
    "name": "field1",
    "label": "Field 1",
    "type": "text"
})

# Remove field
modal.remove_field("field1")

# Update values
modal.set_input("username", "john_doe")
value = modal.get_input("username")
```

**Customization Examples:**
```python
# Dark theme modal
dark_modal = CustomModal(
    parent=None,
    title="Dark Modal",
    fields=fields,
    bg_color="#0a0e27",
    border_color="#6366f1",
    title_color="#e8f0ff",
    label_color="#d1d5db",
    ok_button_color="#6366f1"
)

# Light theme modal
light_modal = CustomModal(
    parent=None,
    title="Light Modal",
    fields=fields,
    bg_color="#ffffff",
    border_color="#e5e7eb",
    title_color="#1f2937",
    label_color="#374151",
    ok_button_color="#3b82f6"
)

# Compact modal
compact_modal = CustomModal(
    parent=None,
    title="Compact",
    width=400,
    height=300,
    fields=fields,
    padding=12,
    spacing=8,
    button_height=32,
    button_width=100
)
```

**Best Practices:**
- Use `required=True` for mandatory fields
- Add validation regex for email, phone, or specific formats
- Use custom validation callback for complex logic
- Keep field names simple and descriptive
