"""
Time spinner widget for tkface.

This module provides TimeSpinner widget that displays time selection
using canvas-based spinboxes for hours, minutes, seconds, and AM/PM.
"""

import configparser
import datetime
import sys
import tkinter as tk
from pathlib import Path
from typing import Dict, Any, Optional

from ..lang import get as lang_get
from . import get_scaling_factor

# Import flat button for Windows only
FlatButton = None
if sys.platform == "win32":
    try:
        from ..win.button import FlatButton
    except ImportError:
        FlatButton = None


def _load_theme(theme_name: str = "light") -> Dict[str, str]:
    """
    Load theme colors from .ini file.
    
    Args:
        theme_name: Name of the theme ('light' or 'dark')
        
    Returns:
        Dict with color values
    """
    try:
        current_dir = Path(__file__).parent.parent / "themes"
        theme_file = current_dir / f"{theme_name}.ini"
        
        if not theme_file.exists():
            return _get_default_theme()
            
        config = configparser.ConfigParser()
        config.read(theme_file)
        
        if theme_name not in config:
            return _get_default_theme()
            
        theme_section = config[theme_name]
        return dict(theme_section)
    except Exception:
        return _get_default_theme()


def _get_default_theme() -> Dict[str, str]:
    """
    Get default theme colors (light theme).
    
    Returns:
        Dict with default color values
    """
    return {
        'time_background': 'white',
        'time_foreground': '#333333',
        'time_spinbox_bg': '#f0f0f0',
        'time_spinbox_button_bg': 'white',
        'time_spinbox_hover_bg': '#e0e0e0',
        'time_spinbox_active_bg': '#d0d0d0',
        'time_spinbox_outline': '#cccccc',
        'time_separator_color': '#333333',
        'time_label_color': '#333333',
        'time_toggle_bg': '#f0f0f0',
        'time_toggle_slider_bg': 'white',
        'time_toggle_outline': '#cccccc',
        'time_toggle_active_fg': '#333333',
        'time_toggle_inactive_fg': '#999999',
        'time_button_bg': 'white',
        'time_button_fg': '#000000',
        'time_button_active_bg': '#f5f5f5',
        'time_button_active_fg': '#000000'
    }


class CanvasSpinbox:
    """Canvas-based spinbox with modern appearance."""

    def __init__(
        self,
        canvas,
        x,
        y,
        width,
        height,
        from_=0,
        to=99,
        value=0,
        format_str="%02d",
        callback=None,
        theme_colors=None,
    ):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.from_ = from_
        self.to = to
        self.value = value
        self.format_str = format_str
        self.callback = callback
        
        # UI elements IDs
        self.bg_rect = None
        self.up_button = None
        self.down_button = None
        self.value_text = None
        self.up_triangle = None
        self.down_triangle = None
        
        # Colors from theme
        if theme_colors is None:
            theme_colors = _get_default_theme()
        self.bg_color = theme_colors.get('time_spinbox_bg', '#f0f0f0')
        self.hover_color = theme_colors.get('time_spinbox_hover_bg', '#e0e0e0')
        self.active_color = theme_colors.get('time_spinbox_active_bg', '#d0d0d0')
        self.text_color = theme_colors.get('time_foreground', '#000000')
        self.button_color = theme_colors.get('time_spinbox_button_bg', '#ffffff')
        self.outline_color = theme_colors.get('time_spinbox_outline', '#cccccc')
        self.triangle_color = theme_colors.get('time_foreground', '#333333')
        
        self._create_elements()
        self._bind_events()

    def _create_elements(self):
        """Create canvas elements for the spinbox."""
        # Background rectangle
        self.bg_rect = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.bg_color, outline=self.outline_color, width=1
        )
        
        # Button dimensions
        btn_height = self.height // 3
        btn_y_up = self.y
        btn_y_down = self.y + self.height - btn_height
        
        # Up button background
        self.up_button = self.canvas.create_rectangle(
            self.x, btn_y_up, self.x + self.width, btn_y_up + btn_height,
            fill=self.button_color, outline=self.outline_color, width=1
        )
        
        # Up triangle
        tri_size = btn_height // 3
        tri_x = self.x + self.width // 2
        tri_y = btn_y_up + btn_height // 2
        self.up_triangle = self.canvas.create_polygon(
            tri_x, tri_y - tri_size // 2,
            tri_x - tri_size, tri_y + tri_size // 2,
            tri_x + tri_size, tri_y + tri_size // 2,
            fill=self.triangle_color, outline=""
        )
        
        # Down button background
        self.down_button = self.canvas.create_rectangle(
            self.x, btn_y_down, self.x + self.width, btn_y_down + btn_height,
            fill=self.button_color, outline=self.outline_color, width=1
        )
        
        # Down triangle
        tri_y = btn_y_down + btn_height // 2
        self.down_triangle = self.canvas.create_polygon(
            tri_x, tri_y + tri_size // 2,
            tri_x - tri_size, tri_y - tri_size // 2,
            tri_x + tri_size, tri_y - tri_size // 2,
            fill=self.triangle_color, outline=""
        )
        
        # Value text in the middle
        text_y = self.y + self.height // 2
        # Scale font size based on height (default 12 for height 85)
        font_size = max(8, int(12 * self.height / 85))
        self.value_text = self.canvas.create_text(
            tri_x, text_y,
            text=self.format_str % self.value,
            font=("Arial", font_size, "bold"),
            fill=self.text_color
        )

    def _bind_events(self):
        """Bind mouse events."""
        # Up button
        self.canvas.tag_bind(self.up_button, "<Button-1>", lambda e: self._increment())
        self.canvas.tag_bind(self.up_triangle, "<Button-1>", lambda e: self._increment())
        self.canvas.tag_bind(self.up_button, "<Enter>", lambda e: self._on_hover_up(True))
        self.canvas.tag_bind(self.up_triangle, "<Enter>", lambda e: self._on_hover_up(True))
        self.canvas.tag_bind(self.up_button, "<Leave>", lambda e: self._on_hover_up(False))
        self.canvas.tag_bind(self.up_triangle, "<Leave>", lambda e: self._on_hover_up(False))
        
        # Down button
        self.canvas.tag_bind(self.down_button, "<Button-1>", lambda e: self._decrement())
        self.canvas.tag_bind(self.down_triangle, "<Button-1>", lambda e: self._decrement())
        self.canvas.tag_bind(self.down_button, "<Enter>", lambda e: self._on_hover_down(True))
        self.canvas.tag_bind(self.down_triangle, "<Enter>", lambda e: self._on_hover_down(True))
        self.canvas.tag_bind(self.down_button, "<Leave>", lambda e: self._on_hover_down(False))
        self.canvas.tag_bind(self.down_triangle, "<Leave>", lambda e: self._on_hover_down(False))
        
        # Mouse wheel on all elements (Windows uses Button-4/5, Linux/Mac use MouseWheel)
        for item in [self.bg_rect, self.value_text]:
            try:
                self.canvas.tag_bind(item, "<MouseWheel>", self._on_mouse_wheel)
            except tk.TclError:
                # Windows doesn't support MouseWheel, use Button-4/5 instead
                pass
            self.canvas.tag_bind(item, "<Button-4>", lambda e: self._increment())
            self.canvas.tag_bind(item, "<Button-5>", lambda e: self._decrement())

    def _on_hover_up(self, enter):
        """Handle hover on up button."""
        color = self.hover_color if enter else self.button_color
        self.canvas.itemconfig(self.up_button, fill=color)

    def _on_hover_down(self, enter):
        """Handle hover on down button."""
        color = self.hover_color if enter else self.button_color
        self.canvas.itemconfig(self.down_button, fill=color)

    def _increment(self):
        """Increment the value with wraparound."""
        self.value += 1
        if self.value > self.to:
            self.value = self.from_
        self._update_display()
        if self.callback:
            self.callback()

    def _decrement(self):
        """Decrement the value with wraparound."""
        self.value -= 1
        if self.value < self.from_:
            self.value = self.to
        self._update_display()
        if self.callback:
            self.callback()

    def _on_mouse_wheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.delta > 0:
            self._increment()
        else:
            self._decrement()

    def _update_display(self):
        """Update the display value."""
        self.canvas.itemconfig(self.value_text, text=self.format_str % self.value)

    def get(self):
        """Get the current value."""
        return self.value

    def set(self, value):
        """Set the value."""
        if self.from_ <= value <= self.to:
            self.value = value
            self._update_display()

    def destroy(self):
        """Remove all canvas elements."""
        for item in [self.bg_rect, self.up_button, self.down_button, 
                     self.value_text, self.up_triangle, self.down_triangle]:
            if item:
                self.canvas.delete(item)


class CanvasAMPMSpinbox:
    """Canvas-based AM/PM spinbox."""

    def __init__(self, canvas, x, y, width, height, value="AM", callback=None, theme_colors=None):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.values = ["AM", "PM"]
        self.current_index = 0 if value == "AM" else 1
        self.callback = callback
        
        # UI elements IDs
        self.bg_rect = None
        self.up_button = None
        self.down_button = None
        self.value_text = None
        self.up_triangle = None
        self.down_triangle = None
        
        # Colors from theme
        if theme_colors is None:
            theme_colors = _get_default_theme()
        self.bg_color = theme_colors.get('time_spinbox_bg', '#f0f0f0')
        self.hover_color = theme_colors.get('time_spinbox_hover_bg', '#e0e0e0')
        self.text_color = theme_colors.get('time_foreground', '#000000')
        self.button_color = theme_colors.get('time_spinbox_button_bg', '#ffffff')
        self.outline_color = theme_colors.get('time_spinbox_outline', '#cccccc')
        self.triangle_color = theme_colors.get('time_foreground', '#333333')
        
        self._create_elements()
        self._bind_events()

    def _create_elements(self):
        """Create canvas elements for the AM/PM spinbox."""
        # Background rectangle
        self.bg_rect = self.canvas.create_rectangle(
            self.x, self.y, self.x + self.width, self.y + self.height,
            fill=self.bg_color, outline=self.outline_color, width=1
        )
        
        # Button dimensions
        btn_height = self.height // 3
        btn_y_up = self.y
        btn_y_down = self.y + self.height - btn_height
        
        # Up button
        self.up_button = self.canvas.create_rectangle(
            self.x, btn_y_up, self.x + self.width, btn_y_up + btn_height,
            fill=self.button_color, outline=self.outline_color, width=1
        )
        
        # Up triangle
        tri_size = btn_height // 3
        tri_x = self.x + self.width // 2
        tri_y = btn_y_up + btn_height // 2
        self.up_triangle = self.canvas.create_polygon(
            tri_x, tri_y - tri_size // 2,
            tri_x - tri_size, tri_y + tri_size // 2,
            tri_x + tri_size, tri_y + tri_size // 2,
            fill=self.triangle_color, outline=""
        )

        # Down button
        self.down_button = self.canvas.create_rectangle(
            self.x, btn_y_down, self.x + self.width, btn_y_down + btn_height,
            fill=self.button_color, outline=self.outline_color, width=1
        )
        
        # Down triangle
        tri_y = btn_y_down + btn_height // 2
        self.down_triangle = self.canvas.create_polygon(
            tri_x, tri_y + tri_size // 2,
            tri_x - tri_size, tri_y - tri_size // 2,
            tri_x + tri_size, tri_y - tri_size // 2,
            fill=self.triangle_color, outline=""
        )
        
        # Value text
        text_y = self.y + self.height // 2
        # Scale font size based on height (default 11 for height 85)
        font_size = max(7, int(11 * self.height / 85))
        self.value_text = self.canvas.create_text(
            tri_x, text_y,
            text=self.values[self.current_index],
            font=("Arial", font_size, "bold"),
            fill=self.text_color
        )

    def _bind_events(self):
        """Bind mouse events."""
        # Up button
        self.canvas.tag_bind(self.up_button, "<Button-1>", lambda e: self._toggle())
        self.canvas.tag_bind(self.up_triangle, "<Button-1>", lambda e: self._toggle())
        self.canvas.tag_bind(self.up_button, "<Enter>", lambda e: self._on_hover_up(True))
        self.canvas.tag_bind(self.up_triangle, "<Enter>", lambda e: self._on_hover_up(True))
        self.canvas.tag_bind(self.up_button, "<Leave>", lambda e: self._on_hover_up(False))
        self.canvas.tag_bind(self.up_triangle, "<Leave>", lambda e: self._on_hover_up(False))
        
        # Down button
        self.canvas.tag_bind(self.down_button, "<Button-1>", lambda e: self._toggle())
        self.canvas.tag_bind(self.down_triangle, "<Button-1>", lambda e: self._toggle())
        self.canvas.tag_bind(self.down_button, "<Enter>", lambda e: self._on_hover_down(True))
        self.canvas.tag_bind(self.down_triangle, "<Enter>", lambda e: self._on_hover_down(True))
        self.canvas.tag_bind(self.down_button, "<Leave>", lambda e: self._on_hover_down(False))
        self.canvas.tag_bind(self.down_triangle, "<Leave>", lambda e: self._on_hover_down(False))
        
        # Mouse wheel and click on value
        for item in [self.bg_rect, self.value_text]:
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self._toggle())
            try:
                self.canvas.tag_bind(item, "<MouseWheel>", lambda e: self._toggle())
            except tk.TclError:
                # Windows doesn't support MouseWheel, use Button-4/5 instead
                pass
            self.canvas.tag_bind(item, "<Button-4>", lambda e: self._toggle())
            self.canvas.tag_bind(item, "<Button-5>", lambda e: self._toggle())

    def _on_hover_up(self, enter):
        """Handle hover on up button."""
        color = self.hover_color if enter else self.button_color
        self.canvas.itemconfig(self.up_button, fill=color)

    def _on_hover_down(self, enter):
        """Handle hover on down button."""
        color = self.hover_color if enter else self.button_color
        self.canvas.itemconfig(self.down_button, fill=color)

    def _toggle(self):
        """Toggle between AM and PM."""
        self.current_index = (self.current_index + 1) % 2
        self._update_display()
        if self.callback:
            self.callback()

    def _update_display(self):
        """Update the display value."""
        self.canvas.itemconfig(self.value_text, text=self.values[self.current_index])

    def get(self):
        """Get the current value."""
        return self.values[self.current_index]

    def set(self, value):
        """Set the value."""
        if value in self.values:
            self.current_index = self.values.index(value)
            self._update_display()

    def destroy(self):
        """Remove all canvas elements."""
        for item in [self.bg_rect, self.up_button, self.down_button,
                     self.value_text, self.up_triangle, self.down_triangle]:
            if item:
                self.canvas.delete(item)


class TimeSpinner(tk.Frame):
    """Canvas-based time spinner widget with modern appearance."""

    def __init__(  # pylint: disable=too-many-positional-arguments
        self,
        parent,
        hour_format="24",
        show_seconds=True,
        time_callback=None,
        theme="light",
        initial_time=None,
    ):
        # Load theme colors
        self.theme_colors = _load_theme(theme)
        bg_color = self.theme_colors.get('time_background', 'white')
        
        super().__init__(parent, bg=bg_color)
        self.hour_format = hour_format
        self.show_seconds = show_seconds
        self.time_callback = time_callback
        self.theme = theme
        self.selected_time = None

        # Set initial values
        if initial_time is not None:
            self.selected_time = initial_time
        else:
            self.selected_time = datetime.datetime.now().time()

        # Get platform information and DPI scaling
        self.platform = sys.platform
        try:
            self.dpi_scaling_factor = get_scaling_factor(parent)
        except (ImportError, AttributeError, TypeError):
            self.dpi_scaling_factor = 1.0

        # Unified scaling configuration
        self._setup_scaling_config()
        
        # Store background color for later use
        self.bg_color = bg_color
        
        # Create canvas (size will be set by _update_canvas_size)
        self.canvas = tk.Canvas(self, bg=bg_color, highlightthickness=0)
        self.canvas.pack(padx=self.canvas_padx, pady=(self.canvas_pady_top, self.canvas_pady_bottom))
        
        # Create button frame
        self.button_frame = tk.Frame(self, bg=bg_color)
        self.button_frame.pack(pady=(0, self.button_pady))
        
        # Spinbox references
        self.hour_spinbox = None
        self.minute_spinbox = None
        self.second_spinbox = None
        self.am_pm_spinbox = None
        
        # Format toggle button references
        self.format_toggle_rect = None
        self.format_toggle_text = None
        
        # OK/Cancel buttons (regular tkinter buttons)
        self.ok_button = None
        self.cancel_button = None

        self._create_widgets()

    def _setup_scaling_config(self):
        """Setup unified scaling configuration for all dimensions and margins."""
        # Base dimensions (optimized for Mac as baseline)
        base_dimensions = {
            'spinbox_width': 22,
            'spinbox_height': 42,
            'separator_width': 9,
            'toggle_width': 50,
            'toggle_height': 17,
            'margin': 20,
            'extra_height': 40,
            'bottom_margin': 10,
            'label_offset': 15,
            'toggle_y': 2,
            'canvas_padx': 5,
            'canvas_pady_top': 5,
            'canvas_pady_bottom': 2,
            'button_pady': 5
        }
        
        # Calculate unified scaling factor (all platforms use same base scale)
        self.unified_scale = self.dpi_scaling_factor
        self.margin_scale = self.dpi_scaling_factor
        
        # Apply scaling to all dimensions
        self.spinbox_width = int(base_dimensions['spinbox_width'] * self.unified_scale)
        self.spinbox_height = int(base_dimensions['spinbox_height'] * self.unified_scale)
        self.separator_width = int(base_dimensions['separator_width'] * self.unified_scale)
        self.format_toggle_width = int(base_dimensions['toggle_width'] * self.unified_scale)
        self.format_toggle_height = int(base_dimensions['toggle_height'] * self.unified_scale)
        
        # Apply scaling to margins and padding
        self.margin = int(base_dimensions['margin'] * self.margin_scale)
        self.extra_height = int(base_dimensions['extra_height'] * self.margin_scale)
        self.bottom_margin = int(base_dimensions['bottom_margin'] * self.margin_scale)
        self.label_offset = int(base_dimensions['label_offset'] * self.margin_scale)
        self.toggle_y = int(base_dimensions['toggle_y'] * self.margin_scale)
        
        # Canvas padding
        self.canvas_padx = int(base_dimensions['canvas_padx'] * self.margin_scale)
        self.canvas_pady_top = int(base_dimensions['canvas_pady_top'] * self.margin_scale)
        self.canvas_pady_bottom = int(base_dimensions['canvas_pady_bottom'] * self.margin_scale)
        self.button_pady = int(base_dimensions['button_pady'] * self.margin_scale)

    def _update_canvas_size(self):
        """Update canvas size based on current settings."""
        # Calculate canvas size for maximum case (with seconds and AM/PM)
        max_spinboxes = 4  # hour, minute, second, am/pm
        max_separators = 3  # between hour:minute:second:am/pm
        
        # Use unified scaling values
        canvas_width = (max_spinboxes * self.spinbox_width + 
                       max_separators * self.separator_width + self.margin)
        canvas_height = self.spinbox_height + self.format_toggle_height + self.extra_height
        
        # Update canvas size (fixed size regardless of current format)
        self.canvas.config(width=canvas_width, height=canvas_height)

    def _create_widgets(self):
        """Create all canvas widgets."""
        # Update canvas size first
        self._update_canvas_size()
        
        # Update canvas background color from theme
        self.canvas.configure(bg=self.bg_color)
        
        # Update main frame background color
        self.configure(bg=self.bg_color)
        
        # Clear canvas
        self.canvas.delete("all")
        
        # Starting position - calculate from bottom of canvas, centered horizontally
        # Calculate y_offset from bottom: canvas_height - spinbox_height - margin
        # Use unified scaling values
        extra_height = self.extra_height
        bottom_margin = self.bottom_margin
        
        canvas_height = self.spinbox_height + self.format_toggle_height + extra_height
        y_offset = canvas_height - self.spinbox_height - bottom_margin
        
        # Calculate total width needed for current spinboxes
        num_spinboxes = 2 + (1 if self.show_seconds else 0) + (1 if self.hour_format == "12" else 0)
        num_separators = 1 + (1 if self.show_seconds else 0)
        total_width = num_spinboxes * self.spinbox_width + num_separators * self.separator_width
        
        # Calculate maximum canvas width
        max_spinboxes = 4  # hour, minute, second, am/pm
        max_separators = 3  # between hour:minute:second:am/pm
        # Use unified scaling values
        max_canvas_width = max_spinboxes * self.spinbox_width + max_separators * self.separator_width + self.margin
        
        # Center the spinboxes horizontally
        x_offset = (max_canvas_width - total_width) // 2
        
        # Get root for language support
        root = self.winfo_toplevel()

        # Hour
        hour_label = lang_get("timepicker.hour", root)
        # Scale font size based on spinbox size
        label_font_size = max(6, int(8 * self.spinbox_height / 85))
        # Use unified scaling values for label offset
        label_offset = self.label_offset
        label_color = self.theme_colors.get('time_label_color', '#333333')
        self.canvas.create_text(
            x_offset + self.spinbox_width // 2, y_offset - label_offset,
            text=hour_label, font=("Arial", label_font_size), fill=label_color
        )
        
        hour_value = self.selected_time.hour
        if self.hour_format == "12":
            if hour_value == 0:
                hour_value = 12
            elif hour_value > 12:
                hour_value -= 12
        
        self.hour_spinbox = CanvasSpinbox(
            self.canvas, x_offset, y_offset, self.spinbox_width, self.spinbox_height,
            from_=1 if self.hour_format == "12" else 0,
            to=12 if self.hour_format == "12" else 23,
            value=hour_value,
            format_str="%02d",
            callback=self._on_time_change,
            theme_colors=self.theme_colors
        )
        x_offset += self.spinbox_width

        # Separator - draw dots instead of colon
        center_x = x_offset + self.separator_width // 2 + 1  # Adjust position slightly right
        center_y = y_offset + self.spinbox_height // 2
        dot_size = max(1, int(1 * self.spinbox_height / 42))  # Even smaller dots, scale based on spinbox height
        dot_spacing = max(4, int(6 * self.spinbox_height / 42))  # More spacing between dots
        separator_color = self.theme_colors.get('time_separator_color', '#333333')
        
        # Draw two dots vertically centered with more spacing
        self.canvas.create_oval(
            center_x - dot_size, center_y - dot_size - dot_spacing // 2,
            center_x + dot_size, center_y + dot_size - dot_spacing // 2,
            fill=separator_color, outline=""
        )
        self.canvas.create_oval(
            center_x - dot_size, center_y - dot_size + dot_spacing // 2,
            center_x + dot_size, center_y + dot_size + dot_spacing // 2,
            fill=separator_color, outline=""
        )
        x_offset += self.separator_width

        # Minute
        minute_label = lang_get("timepicker.minute", root)
        self.canvas.create_text(
            x_offset + self.spinbox_width // 2, y_offset - label_offset,
            text=minute_label, font=("Arial", label_font_size), fill=label_color
        )
        
        self.minute_spinbox = CanvasSpinbox(
            self.canvas, x_offset, y_offset, self.spinbox_width, self.spinbox_height,
            from_=0, to=59, value=self.selected_time.minute,
            format_str="%02d",
            callback=self._on_time_change,
            theme_colors=self.theme_colors
        )
        x_offset += self.spinbox_width

        # Seconds (if enabled)
        if self.show_seconds:
            # Separator - draw dots instead of colon
            center_x = x_offset + self.separator_width // 2 + 1  # Adjust position slightly right
            center_y = y_offset + self.spinbox_height // 2
            dot_size = max(1, int(1 * self.spinbox_height / 42))  # Even smaller dots, scale based on spinbox height
            dot_spacing = max(4, int(6 * self.spinbox_height / 42))  # More spacing between dots
            
            # Draw two dots vertically centered with more spacing
            self.canvas.create_oval(
                center_x - dot_size, center_y - dot_size - dot_spacing // 2,
                center_x + dot_size, center_y + dot_size - dot_spacing // 2,
                fill=separator_color, outline=""
            )
            self.canvas.create_oval(
                center_x - dot_size, center_y - dot_size + dot_spacing // 2,
                center_x + dot_size, center_y + dot_size + dot_spacing // 2,
                fill=separator_color, outline=""
            )
            x_offset += self.separator_width

            second_label = lang_get("timepicker.second", root)
            self.canvas.create_text(
                x_offset + self.spinbox_width // 2, y_offset - label_offset,
                text=second_label, font=("Arial", label_font_size), fill=label_color
            )
            
            self.second_spinbox = CanvasSpinbox(
                self.canvas, x_offset, y_offset, self.spinbox_width, self.spinbox_height,
                from_=0, to=59, value=self.selected_time.second,
                format_str="%02d",
                callback=self._on_time_change,
                theme_colors=self.theme_colors
            )
            x_offset += self.spinbox_width

        # AM/PM (if 12-hour format)
        if self.hour_format == "12":
            am_pm_value = "AM" if self.selected_time.hour < 12 else "PM"
            self.am_pm_spinbox = CanvasAMPMSpinbox(
                self.canvas, x_offset, y_offset, self.spinbox_width, self.spinbox_height,
                value=am_pm_value,
                callback=self._on_time_change,
                theme_colors=self.theme_colors
            )
            x_offset += self.spinbox_width
        
        # 12/24H format toggle button (positioned above the time spinners, centered)
        # Use fixed canvas width for consistent positioning
        max_spinboxes = 4  # hour, minute, second, am/pm
        max_separators = 3  # between hour:minute:second:am/pm
        # Use unified scaling values
        margin = self.margin
        toggle_y = self.toggle_y
        canvas_width = max_spinboxes * self.spinbox_width + max_separators * self.separator_width + margin
        toggle_x = (canvas_width - self.format_toggle_width) // 2
        
        # Get toggle colors from theme
        toggle_bg = self.theme_colors.get('time_toggle_bg', '#f0f0f0')
        toggle_outline = self.theme_colors.get('time_toggle_outline', '#cccccc')
        toggle_slider_bg = self.theme_colors.get('time_toggle_slider_bg', 'white')
        toggle_active_fg = self.theme_colors.get('time_toggle_active_fg', '#333333')
        toggle_inactive_fg = self.theme_colors.get('time_toggle_inactive_fg', '#999999')
        
        # Create toggle switch background
        self.format_toggle_rect = self.canvas.create_rectangle(
            toggle_x, toggle_y,
            toggle_x + self.format_toggle_width, toggle_y + self.format_toggle_height,
            fill=toggle_bg, outline=toggle_outline, width=1
        )
        
        # Create toggle switch slider
        slider_width = self.format_toggle_width // 2 - 2
        slider_height = self.format_toggle_height - 4
        if self.hour_format == "24":
            slider_x = toggle_x + 2
        else:
            slider_x = toggle_x + self.format_toggle_width - slider_width - 2
            
        self.format_toggle_slider = self.canvas.create_rectangle(
            slider_x, toggle_y + 2,
            slider_x + slider_width, toggle_y + slider_height,
            fill=toggle_slider_bg, outline=toggle_outline, width=1
        )
        
        # Create toggle switch labels
        label_y = toggle_y + self.format_toggle_height // 2
        # Scale font size based on toggle height
        toggle_font_size = max(7, int(9 * self.format_toggle_height / 35))
        self.format_toggle_12h = self.canvas.create_text(
            toggle_x + self.format_toggle_width // 4, label_y,
            text="12H", font=("Arial", toggle_font_size, "bold"), 
            fill=toggle_active_fg if self.hour_format == "12" else toggle_inactive_fg
        )
        self.format_toggle_24h = self.canvas.create_text(
            toggle_x + 3 * self.format_toggle_width // 4, label_y,
            text="24H", font=("Arial", toggle_font_size, "bold"), 
            fill=toggle_active_fg if self.hour_format == "24" else toggle_inactive_fg
        )
        
        # Bind toggle button
        self.canvas.tag_bind(self.format_toggle_rect, "<Button-1>", lambda e: self._toggle_format())
        self.canvas.tag_bind(self.format_toggle_slider, "<Button-1>", lambda e: self._toggle_format())
        self.canvas.tag_bind(self.format_toggle_12h, "<Button-1>", lambda e: self._toggle_format())
        self.canvas.tag_bind(self.format_toggle_24h, "<Button-1>", lambda e: self._toggle_format())
        self.canvas.tag_bind(self.format_toggle_rect, "<Enter>", lambda e: self._on_hover_toggle(True))
        self.canvas.tag_bind(self.format_toggle_slider, "<Enter>", lambda e: self._on_hover_toggle(True))
        self.canvas.tag_bind(self.format_toggle_rect, "<Leave>", lambda e: self._on_hover_toggle(False))
        self.canvas.tag_bind(self.format_toggle_slider, "<Leave>", lambda e: self._on_hover_toggle(False))
        
        # Create OK and Cancel buttons (regular tkinter buttons)
        self._create_buttons()
        
        # Keyboard shortcuts
        self.bind("<Return>", lambda e: self._on_ok())
        self.bind("<Escape>", lambda e: self._on_cancel())
        
        # Set focus to canvas for keyboard events
        self.canvas.focus_set()

    def _create_buttons(self):
        """Create OK and Cancel buttons."""
        # Destroy existing buttons if they exist
        if self.ok_button:
            self.ok_button.destroy()
        if self.cancel_button:
            self.cancel_button.destroy()
            
        # Update button frame background color
        self.button_frame.configure(bg=self.bg_color)
            
        # Get root for language support
        root = self.winfo_toplevel()

        # Use default button colors (not from theme)
        button_bg = 'white'
        button_fg = '#000000'
        button_active_bg = '#f5f5f5'
        button_active_fg = '#000000'

        # Choose button class based on platform
        if self.platform == "win32" and FlatButton is not None:
            ButtonClass = FlatButton
        else:
            ButtonClass = tk.Button

        # OK button
        ok_text = lang_get("timepicker.ok", root)
        self.ok_button = ButtonClass(
            self.button_frame,
            text=ok_text,
            command=self._on_ok,
            width=6,
            font=("Arial", 8),
            bg=button_bg,
            fg=button_fg,
            activebackground=button_active_bg,
            activeforeground=button_active_fg,
            highlightthickness=0,
            highlightbackground=button_bg,
            bd=0
        )
        self.ok_button.pack(side="left", padx=(0, 5))

        # Cancel button
        cancel_text = lang_get("timepicker.cancel", root)
        self.cancel_button = ButtonClass(
            self.button_frame,
            text=cancel_text,
            command=self._on_cancel,
            font=("Arial", 8),
            bg=button_bg,
            fg=button_fg,
            activebackground=button_active_bg,
            activeforeground=button_active_fg,
            highlightthickness=0,
            highlightbackground=button_bg,
            bd=0
        )
        self.cancel_button.pack(side="left")

    def _on_hover_toggle(self, enter):
        """Handle hover on format toggle button."""
        hover_color = self.theme_colors.get('time_spinbox_active_bg', '#d0d0d0')
        normal_color = self.theme_colors.get('time_spinbox_hover_bg', '#e0e0e0')
        color = hover_color if enter else normal_color
        self.canvas.itemconfig(self.format_toggle_rect, fill=color)


    def _toggle_format(self):
        """Toggle between 12-hour and 24-hour format."""
        # Save current time before switching
        self._on_time_change()
        
        # Store current time
        current_time = self.selected_time
        
        # Toggle format
        self.hour_format = "24" if self.hour_format == "12" else "12"
        
        # Restore time and recreate widgets
        self.selected_time = current_time
        self._create_widgets()

    def _on_time_change(self, event=None):  # pylint: disable=unused-argument
        """Handle time component changes."""
        try:
            hour = self.hour_spinbox.get()
            minute = self.minute_spinbox.get()
            second = self.second_spinbox.get() if self.show_seconds else 0

            if self.hour_format == "12":
                am_pm = self.am_pm_spinbox.get()
                if am_pm == "PM" and hour != 12:
                    hour += 12
                elif am_pm == "AM" and hour == 12:
                    hour = 0

            # Validate time
            if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                self.selected_time = datetime.time(hour, minute, second)
        except (ValueError, TypeError, AttributeError):
            pass

    def _on_ok(self):
        """Handle OK button click."""
        self._on_time_change()
        if self.time_callback:
            self.time_callback(self.selected_time)

    def _on_cancel(self):
        """Handle Cancel button click."""
        if self.time_callback:
            self.time_callback(None)

    def get_selected_time(self) -> Optional[datetime.time]:
        """Get the selected time."""
        return self.selected_time

    def set_selected_time(self, time_obj: datetime.time):
        """Set the selected time."""
        self.selected_time = time_obj
        # Recreate widgets to reflect the new time
        self._create_widgets()

    def set_hour_format(self, hour_format: str):
        """Set the hour format (12 or 24)."""
        self.hour_format = hour_format
        self._create_widgets()
        # Recreate buttons
        self._create_buttons()

    def set_show_seconds(self, show_seconds: bool):
        """Set whether to show seconds."""
        self.show_seconds = show_seconds
        self._create_widgets()
        # Recreate buttons
        self._create_buttons()
        
    def set_theme(self, theme: str):
        """Set the theme and reload colors."""
        self.theme = theme
        self.theme_colors = _load_theme(theme)
        self.bg_color = self.theme_colors.get('time_background', 'white')
        
        # Update main frame background
        self.configure(bg=self.bg_color)
        
        # Recreate widgets with new theme
        self._create_widgets()
        self._create_buttons()


# Legacy classes for backwards compatibility (not used anymore)
class CustomSpinbox(tk.Frame):
    """Deprecated: Legacy custom spinbox - use CanvasSpinbox instead."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Empty implementation for compatibility


class CustomAMPMSpinbox(tk.Frame):
    """Deprecated: Legacy custom AM/PM spinbox - use CanvasAMPMSpinbox instead."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Empty implementation for compatibility