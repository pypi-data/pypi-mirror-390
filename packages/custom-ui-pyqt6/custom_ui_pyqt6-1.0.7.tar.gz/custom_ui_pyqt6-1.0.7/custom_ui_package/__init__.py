"""
Custom UI Components - Modern PyQt6 UI components with glassmorphism effects
"""

from .custom_dropdown import (
    CustomDropdown,
    CustomDropdownCompact,
    CustomDropdownLarge,
    CustomDropdownDelegate
)
from .custom_dialog import CustomMessageDialog
from .custom_titlebar import CustomTitleBar
from .custom_main_window import CustomMainWindow, THEMES
from .custom_button import CustomButton
from .custom_label import CustomLabel
from .custom_menu import CustomMenu
from .custom_scrollbar import CustomScrollBar, CustomVerticalScrollBar, CustomHorizontalScrollBar
from .custom_input_box import CustomInputBox
from .custom_textarea import CustomTextArea
from .custom_checkbox import CustomCheckBox
from .custom_radiobutton import CustomRadioButton
from .custom_slider import CustomSlider
from .custom_progressbar import CustomProgressBar
from .custom_tabwidget import CustomTabWidget
from .custom_card import CustomCard
from .custom_badge import CustomBadge
from .custom_spinner import CustomSpinner
from .custom_toast import CustomToast
from .custom_tooltip import CustomTooltip
from .custom_accordion import CustomAccordion, AccordionItem
from .custom_modal import CustomModal
from .colors.color_palette import (
    GLOBAL_COLOR_PALETTE,
    create_background_style,
    get_global_color,
    set_global_color_palette
)

__version__ = "1.0.7"
__author__ = "CrypterENC"
__email__ = "a95899003@gmail.com"
__description__ = "Modern PyQt6 UI components with glassmorphism effects and smooth animations"

__all__ = [
    "CustomDropdown",
    "CustomDropdownCompact",
    "CustomDropdownLarge",
    "CustomDropdownDelegate",
    "CustomMessageDialog",
    "CustomTitleBar",
    "CustomMainWindow",
    "CustomButton",
    "CustomLabel",
    "CustomMenu",
    "CustomScrollBar",
    "CustomVerticalScrollBar",
    "CustomHorizontalScrollBar",
    "CustomInputBox",
    "CustomTextArea",
    "CustomCheckBox",
    "CustomRadioButton",
    "CustomSlider",
    "CustomProgressBar",
    "CustomTabWidget",
    "CustomCard",
    "CustomBadge",
    "CustomSpinner",
    "CustomToast",
    "CustomTooltip",
    "CustomAccordion",
    "AccordionItem",
    "CustomModal",
    "THEMES",
    "GLOBAL_COLOR_PALETTE",
    "create_background_style",
    "get_global_color",
    "set_global_color_palette",
]
