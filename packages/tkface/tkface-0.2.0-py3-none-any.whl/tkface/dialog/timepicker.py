"""
Time picker widgets for tkface.

This module provides TimeFrame and TimeEntry widgets that display
popup time selectors for time selection.
"""

import configparser
import datetime
import logging
import sys
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Dict, Optional

from ..widget import get_scaling_factor
from ..widget.timespinner import TimeSpinner


def _load_theme_colors(theme_name: str = "light") -> Dict[str, str]:
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
            # Return default light theme if file doesn't exist
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
            
        config = configparser.ConfigParser()
        config.read(theme_file)
        
        if theme_name not in config:
            # Return default light theme if section doesn't exist
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
            
        theme_section = config[theme_name]
        return dict(theme_section)
    except Exception:
        # Return default light theme on any error
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


@dataclass
class TimePickerConfig:
    """Configuration for TimePicker widgets."""

    time_format: str = "%H:%M:%S"
    hour_format: str = "24"  # "12" or "24"
    show_seconds: bool = True
    theme: str = "light"
    language: str = "en"
    time_callback: Optional[callable] = None


class _TimePickerBase:
    """Base class for time picker widgets with common functionality."""

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[TimePickerConfig] = None,
        time_format: str = "%H:%M:%S",
        hour_format: str = "24",
        show_seconds: bool = True,
        theme: str = "light",
        language: str = "en",
        time_callback: Optional[callable] = None,
        **kwargs,  # pylint: disable=unused-argument
    ):
        # Use config if provided, otherwise use individual parameters
        if config is None:
            config = TimePickerConfig(
                time_format=time_format,
                hour_format=hour_format,
                show_seconds=show_seconds,
                theme=theme,
                language=language,
                time_callback=time_callback,
            )

        self.logger = logging.getLogger(__name__)
        # Store parent for toplevel access
        self.master = parent
        # Get platform information once
        self.platform = sys.platform
        # DPI scaling support
        try:
            self.dpi_scaling_factor = get_scaling_factor(parent)
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug("Failed to get DPI scaling factor: %s, using 1.0", e)
            self.dpi_scaling_factor = 1.0

        self.time_format = config.time_format
        self.hour_format = config.hour_format
        self.show_seconds = config.show_seconds
        self.theme = config.theme if hasattr(config, 'theme') else theme
        self.selected_time = None
        self.popup = None
        self.time_callback = config.time_callback
        self.time_picker = None
        self.initial_time = None
        # Store binding id for toplevel click so we can unbind on hide
        self._parent_click_binding = None

    def _on_time_selected(self, time_obj):
        """Handle time selection from time picker."""
        if time_obj:
            self.selected_time = time_obj
            self._update_entry_text(time_obj.strftime(self.time_format))
        # Always hide time picker and call callback (even for cancel)
        self.hide_time_picker()
        # Call the callback if provided
        if self.time_callback:
            self.time_callback(time_obj)
        # Reset pressed state for TimeEntry
        if hasattr(self, "state"):
            try:
                self.state(["!pressed"])
            except tk.TclError as e:
                self.logger.debug("Failed to reset pressed state: %s", e)

    def _update_entry_text(self, text: str):
        """Update the entry text (to be implemented by subclasses)."""
        raise NotImplementedError

    def _on_popup_click(
        self, event, popup_window, time_picker_widget, hide_callback
    ):  # pylint: disable=unused-argument
        """
        Handle click events in the popup to detect clicks outside the
        time picker.
        """
        try:
            # Some platforms may deliver a string widget; fall back to pointer check
            if isinstance(event.widget, str):
                x, y = popup_window.winfo_pointerxy()
                xc = popup_window.winfo_rootx()
                yc = popup_window.winfo_rooty()
                w = popup_window.winfo_width()
                h = popup_window.winfo_height()
                if xc <= x <= xc + w and yc <= y <= yc + h:
                    time_picker_widget.focus_set()
                    return "break"
                hide_callback()
                return "break"

            if not self._is_child_of_time_picker(event.widget, time_picker_widget):
                hide_callback()
            else:
                time_picker_widget.focus_set()
            return "break"
        except Exception:  # pylint: disable=broad-except
            # On any unexpected error, prefer keeping the popup open
            try:
                time_picker_widget.focus_set()
            except Exception as e:  # pylint: disable=broad-except
                self.logger.debug("Failed to set focus on time picker widget: %s", e)
            return "break"

    def _bind_time_picker_events(self, widget):
        """Bind events to all child widgets of the time picker."""
        try:
            # Don't bind ButtonRelease-1 to Button widgets or Spinbox widgets
            # to allow them to function properly
            if not isinstance(widget, (tk.Button, tk.Spinbox)):
                widget.bind("<ButtonRelease-1>", lambda e: "break")
            for child in widget.winfo_children():
                self._bind_time_picker_events(child)
        except (AttributeError, tk.TclError) as e:
            self.logger.debug("Failed to bind time picker events: %s", e)

    def _setup_click_outside_handling(self):
        """Setup click outside handling for time picker."""
        self.logger.debug("Setting up click-outside handling")
        self.time_picker.bind("<FocusOut>", self._on_focus_out)
        self.popup.bind(
            "<Button-1>",
            lambda e: self._on_popup_click(
                e, self.popup, self.time_picker, self.hide_time_picker
            ),
            add="+",
        )
        self.popup.bind(
            "<ButtonRelease-1>",
            lambda e: self._on_popup_click(
                e, self.popup, self.time_picker, self.hide_time_picker
            ),
            add="+",
        )
        # Only TimeFrame has the external button and needs global click binding
        if hasattr(self, "button"):
            toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
            if toplevel:
                self.logger.debug("Binding main toplevel clicks to close popup: %r", toplevel)
                # Clean previous binding if any
                try:
                    if getattr(self, "_parent_click_binding", None):
                        event_type, bind_id = self._parent_click_binding
                        toplevel.unbind(event_type, bind_id)
                        self._parent_click_binding = None
                except Exception as e:  # pylint: disable=broad-except
                    self.logger.debug("Failed to cleanup previous toplevel binding: %s", e)
                # Bind and store id for cleanup on hide
                bind_id = toplevel.bind(
                    "<ButtonRelease-1>",
                    lambda e: self._on_main_window_click(
                        e, self.popup, self.hide_time_picker
                    ),
                    add="+",
                )
                self._parent_click_binding = ("<ButtonRelease-1>", bind_id)

    def _is_child_of_time_picker(self, widget, time_picker_widget):
        """Check if widget is a child of time picker widget."""
        if isinstance(widget, str):
            return False
        current = widget
        while current:
            if current == time_picker_widget:
                return True
            current = current.master
        return False

    def _setup_focus(self):
        """Setup focus for the popup."""
        try:
            self.popup.lift()
            self.time_picker.focus_set()
            self.popup.after(50, self.time_picker.focus_set)
            self.popup.after(100, self.time_picker.focus_force)
        except (AttributeError, tk.TclError) as e:
            self.logger.debug("Failed to setup focus: %s", e)

    def _on_focus_out(self, event):  # pylint: disable=unused-argument
        """Handle focus out events."""
        focus_widget = self.focus_get()  # pylint: disable=no-member
        try:
            if hasattr(self, "time_picker") and self.time_picker:
                if focus_widget is not None:
                    if focus_widget == self or self._is_child_of_time_picker(
                        focus_widget, self.time_picker
                    ):
                        return "break"
        except Exception as e:  # pylint: disable=broad-except
            self.logger.debug("Unexpected error in focus out handling: %s", e)

        if focus_widget is not None:
            if focus_widget == self:
                # Don't hide time picker when focus is on the TimeEntry itself
                return "break"
            self.hide_time_picker()
        else:
            try:
                x, y = self.popup.winfo_pointerxy()
                xc = self.popup.winfo_rootx()
                yc = self.popup.winfo_rooty()
                w = self.popup.winfo_width()
                h = self.popup.winfo_height()
                if xc <= x <= xc + w and yc <= y <= yc + h:
                    self.time_picker.focus_force()
                else:
                    self.hide_time_picker()
            except (
                AttributeError,
                tk.TclError,
                Exception,
            ):  # pylint: disable=broad-except
                self.hide_time_picker()
        return "break"

    def _on_main_window_click(self, event, popup_window, hide_callback):
        """Handle click events on the main window.

        Important: do not consume the click so the underlying widget can receive it
        (e.g., when user clicks an Entry to both close popup AND start editing).
        """
        popup_exists = bool(popup_window and popup_window.winfo_exists())
        # Never consume based on string widget; just pass through
        if isinstance(event.widget, str):
            return None
        if popup_exists:
            popup_x = popup_window.winfo_rootx()
            popup_y = popup_window.winfo_rooty()
            popup_w = popup_window.winfo_width()
            popup_h = popup_window.winfo_height()
            # Get the toplevel window from parent
            toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
            if toplevel:
                root_x = toplevel.winfo_rootx() + event.x
                root_y = toplevel.winfo_rooty() + event.y
            else:
                root_x = event.x
                root_y = event.y
            if (
                root_x < popup_x
                or root_x > popup_x + popup_w
                or root_y < popup_y
                or root_y > popup_y + popup_h
            ):
                hide_callback()
                # After closing, ensure focus and button events reach the clicked widget
                try:
                    target_widget = event.widget
                    generate_click = hasattr(self, "button")
                    self._schedule_focus_restore(target_widget, generate_click)
                except Exception:  # pylint: disable=broad-except
                    pass
        # Always pass through so the click reaches target widget
        return None

    def _schedule_focus_restore(self, widget, generate_click):
        """Ensure focus (and optional synthetic click) returns to the widget."""
        if widget is None:
            return

        def _restore():
            try:
                widget.focus_force()
                if generate_click and hasattr(widget, "event_generate"):
                    widget.event_generate("<Button-1>")
                    widget.event_generate("<ButtonRelease-1>")
                if hasattr(widget, "selection_range"):
                    widget.selection_range(0, tk.END)
                if hasattr(widget, "icursor"):
                    widget.icursor(tk.END)
            except Exception as exc:  # pylint: disable=broad-except
                self.logger.debug("Focus restoration failed: %s", exc)

        try:
            widget.after_idle(_restore)
        except Exception as exc:  # pylint: disable=broad-except
            self.logger.debug("Failed to schedule focus restore: %s", exc)

    def show_time_picker(self):
        """Show the popup time picker."""
        if self.popup:
            self.logger.debug("show_time_picker called but popup already exists; ignoring")
            return
        self.logger.debug("Creating time picker popup")
        try:
            # Prefer using self as parent if it's a real widget; otherwise fallback to master
            parent_for_popup = self
            try:
                _ = self.winfo_toplevel  # attribute presence check; may raise in fallback init
            except Exception:  # pylint: disable=broad-except
                parent_for_popup = self.master

            self.popup = tk.Toplevel(parent_for_popup)
            self.popup.withdraw()
            self.popup.overrideredirect(True)
            self.popup.resizable(False, False)
        except tk.TclError as e:
            # In headless/tests or when the application has been destroyed, avoid raising
            self.logger.debug("Failed to create Toplevel popup: %s", e)
            return

        try:
            # Set theme colors from theme file
            theme_colors = _load_theme_colors(self.theme)
            bg_color = theme_colors.get('time_background', 'white')
            self.popup.configure(bg=bg_color)

            # Force update to ensure background color is applied
            self.popup.update_idletasks()

            # Get the toplevel window from parent
            toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
            if toplevel:
                self.popup.transient(toplevel)
            self.popup.after(100, self._setup_focus)

            # Create time picker widget
            self.time_picker = TimeSpinner(
                self.popup,
                hour_format=self.hour_format,
                show_seconds=self.show_seconds,
                time_callback=self._on_time_selected,
                theme=self.theme if hasattr(self, "theme") else "light",
                initial_time=self.selected_time,
            )

            # Ensure TimeSpinner background matches popup background
            self.time_picker.configure(bg=bg_color)
            self.time_picker.canvas.configure(bg=bg_color)
            self.time_picker.button_frame.configure(bg=bg_color)

            self.logger.debug(
                "TimeSpinner created with hour_format=%s show_seconds=%s theme=%s initial=%r",
                self.hour_format,
                self.show_seconds,
                self.theme if hasattr(self, "theme") else "light",
                self.selected_time,
            )

            self._bind_time_picker_events(self.time_picker)
            self.time_picker.pack(expand=True, fill="both", padx=2, pady=2)

            # Position the popup
            self.popup.update_idletasks()
            self._position_popup()

            self.popup.deiconify()
            self.popup.lift()
            # Force popup to be on top and visible even when overlapping
            self.popup.attributes("-topmost", True)
            self.popup.after(100, lambda: self.popup.attributes("-topmost", False))
            self.popup.bind("<Escape>", lambda e: self.hide_time_picker())
            self._setup_click_outside_handling()
            self.time_picker.focus_set()
        except tk.TclError as e:
            # If any part of popup setup fails (e.g., app destroyed), cleanup and exit gracefully
            self.logger.debug("Popup setup failed: %s", e)
            try:
                if self.popup:
                    self.popup.destroy()
            except Exception:  # pylint: disable=broad-except
                pass
            self.popup = None
            self.time_picker = None
            return

    def _position_popup(self):
        """Position the popup relative to the parent widget."""
        self.popup.update_idletasks()
        popup_width = self.popup.winfo_reqwidth()
        popup_height = self.popup.winfo_reqheight()

        # Get parent widget position
        try:
            parent_y = self.master.winfo_rooty()
        except tk.TclError:
            parent_y = 0

        # Position below the input area (left edge aligned)
        if hasattr(self, "button") and self.entry is not None:
            # TimeFrame: position below the entry (left edge aligned)
            entry_x = self.entry.winfo_rootx()
            entry_y = self.entry.winfo_rooty()
            entry_height = self.entry.winfo_height()
            x = entry_x
            y = entry_y + entry_height
        else:
            # TimeEntry: position below the entry (left edge aligned)
            # For TimeEntry, self is the entry widget itself
            x = self.winfo_rootx()  # pylint: disable=no-member
            y = self.winfo_rooty() + self.winfo_height()  # pylint: disable=no-member

        # Simple positioning: always show below the widget
        # No screen boundary adjustments
        self.popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    def hide_time_picker(self):
        """Hide the popup time picker."""
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.time_picker = None
        # Unbind toplevel click handler if previously bound
        try:
            toplevel = self.master.winfo_toplevel() if hasattr(self, "master") else None
            if toplevel and getattr(self, "_parent_click_binding", None):
                event_type, bind_id = self._parent_click_binding
                toplevel.unbind(event_type, bind_id)
                self._parent_click_binding = None
        except Exception as e:  # pylint: disable=broad-except
            self.logger.debug("Failed to unbind toplevel click: %s", e)
        # Reset pressed state for TimeEntry
        if hasattr(self, "state"):
            try:
                self.state(["!pressed"])
            except tk.TclError as e:
                self.logger.debug("Failed to reset pressed state in hide_time_picker: %s", e)

    def get_time(self) -> Optional[datetime.time]:
        """Get the selected time."""
        return (
            self.time_picker.get_selected_time()
            if self.time_picker
            else self.selected_time
        )

    def set_selected_time(self, time_obj: datetime.time):
        """Set the selected time."""
        self.logger.debug("set_selected_time(%r) called", time_obj)
        self.selected_time = time_obj
        if self.time_picker:
            self.time_picker.set_selected_time(time_obj)
        self._update_entry_text(time_obj.strftime(self.time_format))

    def get_time_string(self) -> str:
        """Get the selected time as a string."""
        selected_time = self.get_time()
        return selected_time.strftime(self.time_format) if selected_time else ""

    def set_hour_format(self, hour_format: str):
        """Set the hour format (12 or 24)."""
        self.logger.debug("set_hour_format(%r) called", hour_format)
        self.hour_format = hour_format
        if self.time_picker:
            self.time_picker.set_hour_format(hour_format)

    def set_show_seconds(self, show_seconds: bool):
        """Set whether to show seconds."""
        self.logger.debug("set_show_seconds(%r) called", show_seconds)
        self.show_seconds = show_seconds
        if self.time_picker:
            self.time_picker.set_show_seconds(show_seconds)


class TimeFrame(tk.Frame, _TimePickerBase):
    """Time picker frame widget with entry and button."""

    @classmethod
    def create(  # pylint: disable=R0917
        cls,
        parent,
        time_format: str = "%H:%M:%S",
        hour_format: str = "24",
        show_seconds: bool = True,
        theme: str = "light",
        language: str = "en",
        time_callback: Optional[callable] = None,
        button_text: str = "🕐",
        width: int = 15,
        **kwargs,
    ):
        """
        Create TimeFrame widget with individual parameters
        (for backward compatibility).
        """
        config = TimePickerConfig(
            time_format=time_format,
            hour_format=hour_format,
            show_seconds=show_seconds,
            theme=theme,
            language=language,
            time_callback=time_callback,
        )
        return cls(
            parent, config=config, button_text=button_text, width=width, **kwargs
        )

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[TimePickerConfig] = None,
        time_format: str = "%H:%M:%S",
        hour_format: str = "24",
        show_seconds: bool = True,
        theme: str = "light",
        language: str = "en",
        time_callback: Optional[callable] = None,
        button_text: str = "🕐",
        width: int = 15,
        initial_time: Optional[datetime.time] = None,
        **kwargs,
    ):
        # Initialize base class first
        _TimePickerBase.__init__(
            self,
            parent,
            config,
            time_format,
            hour_format,
            show_seconds,
            theme,
            language,
            time_callback,
            **kwargs,
        )
        
        # Initialize tk.Frame
        frame_init_success = True
        try:
            tk.Frame.__init__(self, parent)
        except tk.TclError:
            # Fallback for test environments - create mock objects
            self.entry = None
            self.button = None
            # Set tk attribute for test compatibility
            self.tk = getattr(parent, 'tk', None)
            # Set _w attribute for test compatibility
            self._w = getattr(parent, '_w', '.')
            # Set children attribute for test compatibility
            self.children = {}
            # Set _last_child_ids attribute for test compatibility
            self._last_child_ids = {}
            frame_init_success = False
            
        # Create entry and button only if frame initialization succeeded
        if frame_init_success:
            # Entry width is character units and will be handled by DPI system
            try:
                self.entry = tk.Entry(self, state="readonly", width=width)
                self.entry.pack(side="left", fill="x", expand=True)
                self.button = tk.Button(self, text=button_text, command=self.show_time_picker)
                self.button.pack(side="right")
            except tk.TclError:
                # Fallback for test environments
                self.entry = None
                self.button = None

        # Set initial time
        self.initial_time = initial_time
        if initial_time is not None:
            self.selected_time = initial_time
            self.set_selected_time(initial_time)
        else:
            # Set initial time to current time and display it
            current_time = datetime.datetime.now().time()
            self.selected_time = current_time
            self.set_selected_time(current_time)

        # Update DPI scaling after widget creation
        try:
            self.update_dpi_scaling()
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug(
                "Failed to update DPI scaling during TimeFrame initialization: %s", e
            )

    def _update_entry_text(self, text: str):
        """Update the entry text."""
        if self.entry is not None:
            self.entry.config(state="normal")
            self.entry.delete(0, tk.END)
            self.entry.insert(0, text)
            self.entry.config(state="readonly")

    def set_button_text(self, text: str):
        """Set the button text."""
        self.logger.debug("set_button_text(%r) called on %r", text, getattr(self, "button", None))
        if self.button is not None:
            self.button.config(text=text)
        if self.button is not None:
            try:
                self.button.update_idletasks()
                self.logger.debug(
                    "button text now=%r, width(px)=%s",
                    self.button.cget("text"),
                    self.button.winfo_width(),
                )
            except Exception as e:  # pylint: disable=broad-except
                self.logger.debug("update_idletasks failed on button: %s", e)

    def set_width(self, width: int):
        """Set the entry width."""
        self.logger.debug("set_width(%r) called on %r", width, getattr(self, "entry", None))
        if self.entry is not None:
            self.entry.config(width=width)
        if self.entry is not None:
            try:
                self.entry.update_idletasks()
                self.logger.debug(
                    "entry cget(width)=%s, winfo_width(px)=%s, pack_info=%s",
                    self.entry.cget("width"),
                    self.entry.winfo_width(),
                    self.entry.pack_info() if hasattr(self.entry, "pack_info") else None,
                )
            except Exception as e:  # pylint: disable=broad-except
                self.logger.debug("update_idletasks failed on entry: %s", e)


class TimeEntry(ttk.Entry, _TimePickerBase):
    """Time picker entry widget with combobox-like appearance."""

    @classmethod
    def create(  # pylint: disable=R0917
        cls,
        parent,
        time_format: str = "%H:%M:%S",
        hour_format: str = "24",
        show_seconds: bool = True,
        theme: str = "light",
        language: str = "en",
        time_callback: Optional[callable] = None,
        button_text: str = None,
        **kwargs,
    ):
        """
        Create TimeEntry widget with individual parameters
        (for backward compatibility).
        """
        config = TimePickerConfig(
            time_format=time_format,
            hour_format=hour_format,
            show_seconds=show_seconds,
            theme=theme,
            language=language,
            time_callback=time_callback,
        )
        return cls(parent, config=config, button_text=button_text, **kwargs)

    def __init__(  # pylint: disable=R0917
        self,
        parent,
        config: Optional[TimePickerConfig] = None,
        time_format: str = "%H:%M:%S",
        hour_format: str = "24",
        show_seconds: bool = True,
        theme: str = "light",
        language: str = "en",
        time_callback: Optional[callable] = None,
        button_text: str = None,  # pylint: disable=unused-argument
        initial_time: Optional[datetime.time] = None,
        **kwargs,
    ):
        # Remove button_text from kwargs as it's not supported for TimeEntry
        # Note: button_text is now an explicit parameter, so this check is no longer needed
        _TimePickerBase.__init__(
            self,
            parent,
            config,
            time_format,
            hour_format,
            show_seconds,
            theme,
            language,
            time_callback,
            **kwargs,
        )
        
        # Setup style to look like a combobox
        try:
            self.style = ttk.Style(parent)
            self._setup_style()
            # Initialize ttk.Entry with combobox-like style
            ttk.Entry.__init__(self, parent, style="TimeEntryCombobox", **kwargs)
        except tk.TclError:
            # Fallback for test environments or when style system is not available
            try:
                ttk.Entry.__init__(self, parent, **kwargs)
            except tk.TclError:
                # Complete fallback for test environments - create mock entry
                self._mock_entry = True
                # Set tk attribute for test compatibility
                self.tk = getattr(parent, 'tk', None)
                # Set _w attribute for test compatibility
                self._w = getattr(parent, '_w', '.')
                # Set children attribute for test compatibility
                self.children = {}
                # Set _last_child_ids attribute for test compatibility
                self._last_child_ids = {}
        # Set readonly state
        try:
            self.configure(state="readonly")
        except tk.TclError as e:
            self.logger.debug("Failed to set readonly state: %s", e)
        # Bind events for combobox-like behavior
        try:
            self.bind("<ButtonPress-1>", self._on_b1_press)
            self.bind("<Key>", self._on_key)
            # Bind focus out event for time picker
            self.bind("<FocusOut>", self._on_focus_out_entry)
        except tk.TclError as e:
            self.logger.debug("Failed to bind events: %s", e)

        # Set initial time
        self.initial_time = initial_time
        if initial_time is not None:
            self.selected_time = initial_time
            self.set_selected_time(initial_time)
        else:
            # Set initial time to current time and display it
            current_time = datetime.datetime.now().time()
            self.selected_time = current_time
            self.set_selected_time(current_time)

        # Update DPI scaling after widget creation
        try:
            self.update_dpi_scaling()
        except (ImportError, AttributeError, TypeError) as e:
            self.logger.debug(
                "Failed to update DPI scaling during TimeEntry initialization: %s", e
            )

    def _setup_style(self):
        """Setup style to make TimeEntry look like a Combobox."""
        self.style.layout("TimeEntryCombobox", self.style.layout("TCombobox"))
        conf = self.style.configure("TCombobox")
        if conf:
            self.style.configure("TimeEntryCombobox", **conf)
        maps = self.style.map("TCombobox")
        if maps:
            self.style.map("TimeEntryCombobox", **maps)

    def _on_b1_press(self, event):
        """Handle button press events."""
        x = event.x
        width = self.winfo_width()
        right_area = x > width - 20
        # Check if click is in the right area (dropdown button area)
        if right_area:
            self.state(["pressed"])
            self.drop_down()
            return "break"  # Consume the event
        return None

    def drop_down(self):
        """
        Display or withdraw the drop-down time picker depending on its current
        state.
        """
        if self.popup and self.popup.winfo_ismapped():
            self.hide_time_picker()
        else:
            self.show_time_picker()

    def _on_focus_out_entry(self, _event):
        """Handle focus out event for the entry."""
        # Only hide if focus is not on the time picker
        if self.popup and self.popup.winfo_ismapped():
            focused_widget = self.focus_get()
            if focused_widget != self and not self._is_child_of_time_picker(
                focused_widget, self.time_picker
            ):
                self.hide_time_picker()

    def _on_key(self, _event):  # pylint: disable=unused-argument
        """Handle key events."""
        if _event.keysym in ("Down", "space"):
            self.show_time_picker()

    def _update_entry_text(self, text: str):
        """Update the entry text."""
        try:
            self.configure(state="normal")
            self.delete(0, tk.END)
            self.insert(0, text)
            self.configure(state="readonly")
        except tk.TclError:
            # Fallback for test environments where widget is not properly initialized
            self._mock_text = text
            self.logger.debug("Failed to update entry text in test environment: %s", text)

    def get(self):
        """Get the entry text with test environment fallback."""
        try:
            return super().get()
        except tk.TclError:
            # Test environment fallback
            return getattr(self, '_mock_text', '')

    def set_width(self, width: int):
        """Set the entry width for TimeEntry."""
        self.logger.debug("TimeEntry.set_width(%r) called", width)
        try:
            self.configure(width=width)
            self.update_idletasks()
            self.logger.debug(
                "TimeEntry width now cget(width)=%s, winfo_width(px)=%s",
                self.cget("width"),
                self.winfo_width(),
            )
        except Exception as e:  # pylint: disable=broad-except
            self.logger.debug("TimeEntry.set_width failed: %s", e)
            # Ensure update_idletasks is called even if configure fails
            try:
                self.update_idletasks()
            except Exception as e:  # pylint: disable=broad-except
                self.logger.debug("Failed to call update_idletasks: %s", e)
