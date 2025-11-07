"""
Global color palette for all custom UI components
Define colors once and use them everywhere
"""

# Global color palette for centralized color management
GLOBAL_COLOR_PALETTE = {
    'primary': '#a855f7',
    'secondary': '#e9d5ff',
    'background': '#1a0f2e',
    'surface': '#2d1b4e',
    'text': '#f3e8ff',
    'border': 'rgba(168, 85, 247, 0.3)',
    'border_hover': 'rgba(168, 85, 247, 0.1)',
}


def create_background_style(color):
    """
    Create a background style with a single color.
    
    Args:
        color (str): Color in hex or rgba format
        
    Returns:
        str: CSS background style
        
    Examples:
        create_background_style('#a855f7')
        create_background_style('rgba(168, 85, 247, 0.5)')
    """
    return f"background: {color};"


def get_global_color(key, default='#ffffff'):
    """
    Get a color from the global palette.
    
    Args:
        key (str): Color key (e.g., 'primary', 'text', 'border')
        default (str): Default color if key not found
        
    Returns:
        str: Color value (hex or rgba)
    """
    # If key is already a color value (starts with # or rgba), return it directly
    if isinstance(key, str) and (key.startswith('#') or key.startswith('rgba') or key.startswith('rgb')):
        return key
    return GLOBAL_COLOR_PALETTE.get(key, default)


def set_global_color_palette(palette):
    """
    Set the global color palette for all UI elements.
    This allows you to define colors once and use them everywhere.
    
    Args:
        palette (dict): Color palette with keys like:
            - primary: Main accent color (hex or rgba)
            - secondary: Secondary accent color (hex or rgba)
            - background: Background color (hex or rgba)
            - surface: Surface color (hex or rgba)
            - text: Text color (hex or rgba)
            - border: Border color (hex or rgba)
            - border_hover: Border hover color (hex or rgba)
    
    Example:
        set_global_color_palette({
            'primary': '#59ff1b',
            'secondary': '#a5f3fc',
            'background': '#0a0e27',
            'surface': '#0f1535',
            'text': '#f3e8ff',
            'border': 'rgba(168, 85, 247, 0.3)',
            'border_hover': 'rgba(168, 85, 247, 0.1)',
        })
    """
    global GLOBAL_COLOR_PALETTE
    GLOBAL_COLOR_PALETTE.update(palette)
