from . import dialog, lang, widget, win

# Export messagebox and simpledialog for backward compatibility
from .dialog import messagebox, pathchooser, simpledialog
from .dialog.datepicker import DateEntry, DateFrame
from .dialog.timepicker import TimeEntry, TimeFrame

# Export Calendar and DateEntry for backward compatibility
from .widget.calendar import Calendar
from .widget.timespinner import TimeSpinner

# Export Windows-specific flat button as Button
from .win.button import FlatButton as Button

# Export DPI functions for easy access
from .win.dpi import enable_dpi_geometry as dpi

__version__ = "0.2.0"
__all__ = [
    "lang",
    "win",
    "widget",
    "dialog",
    "Button",
    "dpi",
    "Calendar",
    "DateFrame",
    "DateEntry",
    "TimeFrame",
    "TimeEntry",
    "TimeSpinner",
    "messagebox",
    "simpledialog",
    "pathchooser",
]
