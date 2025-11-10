"""
Windows-specific features for tkface.
This module provides Windows-specific enhancements for Tkinter applications.
All functions in this module are designed to work on Windows platforms and
will gracefully degrade or do nothing on other platforms.
Available features:
- DPI awareness and scaling
- Windows-specific button styling (flat buttons)
- Windows system sounds
- Windows 11 corner rounding control
"""

from .bell import bell
from .button import (
    FlatButton,
    configure_button_for_windows,
    create_flat_button,
    get_button_label_with_shortcut,
)
from .dpi import (
    calculate_dpi_sizes,
    configure_ttk_widgets_for_dpi,
    dpi,
    enable_dpi_awareness,
    enable_dpi_geometry,
    get_actual_window_size,
    get_effective_dpi,
    get_scaling_factor,
    logical_to_physical,
    physical_to_logical,
    scale_font_size,
    scale_icon,
)
from .unround import (
    disable_auto_unround,
    enable_auto_unround,
    is_auto_unround_enabled,
    unround,
)

__all__ = [
    "dpi",
    "get_scaling_factor",
    "enable_dpi_geometry",
    "get_actual_window_size",
    "enable_dpi_awareness",
    "calculate_dpi_sizes",
    "configure_ttk_widgets_for_dpi",
    "scale_icon",
    "scale_font_size",
    "get_effective_dpi",
    "logical_to_physical",
    "physical_to_logical",
    "configure_button_for_windows",
    "get_button_label_with_shortcut",
    "FlatButton",
    "create_flat_button",
    "unround",
    "enable_auto_unround",
    "disable_auto_unround",
    "is_auto_unround_enabled",
    "bell",
]
