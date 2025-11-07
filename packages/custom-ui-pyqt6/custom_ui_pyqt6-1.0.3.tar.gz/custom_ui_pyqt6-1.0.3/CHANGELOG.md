# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release
- `CustomDropdown` - Modern dropdown widget with glassmorphism effects
- `CustomDropdownCompact` - Compact variant of dropdown
- `CustomDropdownLarge` - Large variant of dropdown
- `CustomMessageDialog` - Modern message dialog with draggable interface
- `CustomTitleBar` - Custom title bar for frameless windows
- `custom_ui_styles.qss` - Modern stylesheet with color palette
- Comprehensive documentation and examples
- PyPI package distribution

### Features
- Glassmorphism effects with semi-transparent backgrounds
- Smooth hover and focus transitions
- Customizable colors and styling
- Draggable windows and dialogs
- Icon support for dialogs
- Professional typography and design

## [1.1.0] - 2025-11-06

### Added
- **12 New Form & Display Components**:
  - `CustomTextArea` - Multi-line text input with scrollbars and custom styling
  - `CustomCheckBox` - Checkbox with custom styling and animations
  - `CustomRadioButton` - Radio button with custom styling
  - `CustomSlider` - Range slider with custom track/handle styling
  - `CustomProgressBar` - Progress indicator with animations
  - `CustomTabWidget` - Tabbed interface with custom tab styling
  - `CustomCard` - Card container with shadows and theming
  - `CustomBadge` - Status badges/chips/tags
  - `CustomSpinner` - Loading indicator with animations
  - `CustomToast` - Notification/toast messages
  - `CustomTooltip` - Hover tooltips with custom styling
  - `CustomAccordion` - Collapsible panels/sections

### Features
- Full color customization (hex, rgba, rgb) for all components
- Multiple animation types: smooth, bounce, elastic, none
- Comprehensive signal/event system
- Hover and focus state handling
- Drop shadow effects (where applicable)
- Smooth state transitions
- Type hints and full docstrings on all components

### Changed
- Updated `__init__.py` to export all 12 new components
- Enhanced package structure for better organization
- Improved component consistency across the library

### Documentation
- Added comprehensive component reference for all new components
- Added method signatures and parameter documentation
- Added signal/event documentation
- Added usage examples for each component

## [Unreleased]

### Planned
- Dark/Light theme support
- Additional data display components (Table, List, Tree)
- Date/Time picker components
- Color picker component
- Search bar with suggestions
- Context menu component
- File dialog component
- Multi-step wizard component
- Accessibility improvements

---

## How to Update This File

When releasing a new version:

1. Create a new section with `## [X.Y.Z] - YYYY-MM-DD`
2. Add subsections: Added, Changed, Deprecated, Removed, Fixed, Security
3. Update the Unreleased section if needed
4. Link the version at the bottom: `[X.Y.Z]: https://github.com/yourusername/custom-ui-pyqt6/releases/tag/vX.Y.Z`

### Example Format:

```markdown
## [1.1.0] - 2024-02-XX

### Added
- New feature description

### Changed
- Changed behavior description

### Fixed
- Bug fix description

### Deprecated
- Deprecated feature description

### Removed
- Removed feature description

### Security
- Security fix description
```
