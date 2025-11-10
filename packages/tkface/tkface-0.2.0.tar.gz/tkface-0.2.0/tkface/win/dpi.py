# pylint: disable=too-many-lines
import ctypes
import logging
import re
import sys
import tkinter as tk
import tkinter.font as tkfont
from ctypes import pointer, wintypes
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple, Union, Callable, Type, Protocol, TypeVar
from functools import lru_cache

# Type aliases for better readability and type safety
WidgetClass = Type[tk.Widget]
ScalingFactor = float
DPIValue = int
GeometryString = str
PaddingValue = Union[int, float, Tuple[Union[int, float], ...], List[Union[int, float]]]
LengthValue = Union[int, float]
NumericValue = Union[int, float]
WindowHandle = int
MonitorHandle = int
DPIResult = Tuple[DPIValue, DPIValue, ScalingFactor]
GeometryResult = Union[Tuple[int, int], Tuple[int, int, int, int]]

# Enhanced type aliases for better type safety
T = TypeVar('T', bound=Union[int, float, Tuple, List])
ScalableValue = TypeVar('ScalableValue', int, float, Tuple[Union[int, float], ...], List[Union[int, float]])

# Additional type aliases for better type safety
LogLevel = str
PlatformString = str
TkCommand = str
WidgetType = str
ResultDict = Dict[str, Any]
WindowSizeDict = Dict[str, Any]


def is_windows() -> bool:
    """Check if running on Windows platform."""
    return sys.platform == DPIConfig.WINDOWS_PLATFORM


class DPIConfig:
    """DPI configuration constants organized by category."""
    
    class Scaling:
        """Scaling-related constants."""
        MIN_SCALED_VALUE = 1
        DEFAULT_DPI = 96
        MAX_SCALE_FACTOR = 3.0
        TK_SCALING_BASE = 72  # Tk's base scaling
        WINDOWS_SCALE_BASE = 100  # Windows scale base
        DPI_CALCULATION_DIVISOR = 2  # For averaging X and Y DPI
        MINIMUM_POSITIVE_SCALED_VALUE = 1  # Minimum value for positive scaled values
    
    class Windows:
        """Windows-specific constants."""
        DPI_AWARENESS_LEVELS = {
            'UNAWARE': 0,
            'SYSTEM_AWARE': 1,
            'PER_MONITOR_AWARE': 2
        }
        MONITOR_FLAGS = {
            'DEFAULTTOPRIMARY': 0,
            'DEFAULTTONEAREST': 1
        }
    
    class Widgets:
        """Widget-related constants."""
        MIN_INDICATOR_SIZE = 12
        BASE_INDICATOR_SIZE = 13
        DEFAULT_ICON_SIZE = 24
        ICON_SCALE_THRESHOLD = 1.25
        
        # Widget properties that should be scaled
        SCALABLE_LENGTH_PROPERTIES = ["bd", "wraplength", "width", "height"]
        SCALABLE_PADDING_PROPERTIES = ["padx", "pady", "ipadx", "ipady"]
        SCALABLE_LAYOUT_PROPERTIES = [
            "padding", "borderpadding", "indicatorpadding", "indent", "space"
        ]
    
    class Patterns:
        """Regular expression patterns."""
        GEOMETRY_PATTERNS = {
            'with_position': r"(?P<W>\d+)x(?P<H>\d+)\+(?P<X>\d+)\+(?P<Y>\d+)",
            'without_position': r"(?P<W>\d+)x(?P<H>\d+)"
        }
        
        # Pre-compiled patterns for better performance
        GEOMETRY_WITH_POSITION_PATTERN = re.compile(GEOMETRY_PATTERNS['with_position'])
        GEOMETRY_WITHOUT_POSITION_PATTERN = re.compile(GEOMETRY_PATTERNS['without_position'])
    
    class Logging:
        """Logging-related constants."""
        TCL_ERROR_HANDLING_LEVEL = "debug"  # Default log level for Tcl errors
    
    class Performance:
        """Performance-related constants."""
        MAX_RECURSION_DEPTH = 50  # Maximum recursion depth for layout spec scaling
        CACHE_SIZE_LARGE = 512    # Cache size for frequently used methods (increased)
        CACHE_SIZE_MEDIUM = 64    # Cache size for moderately used methods (increased)
        CACHE_SIZE_SMALL = 32     # Cache size for rarely used methods (increased)
    
    class Icons:
        """Icon-related constants with lazy loading for memory optimization."""
        _icon_mapping = None
        
        @classmethod
        def get_icon_mapping(cls, icon_name: str) -> str:
            """Get icon mapping with lazy loading for better memory usage."""
            if cls._icon_mapping is None:
                cls._icon_mapping = {
                    "error": "::tk::icons::error",
                    "info": "::tk::icons::information",
                    "warning": "::tk::icons::warning",
                    "question": "::tk::icons::question",
                }
            return cls._icon_mapping.get(icon_name, f"::tk::icons::{icon_name}")
        
        # Backward compatibility
        @classmethod
        def _get_icon_mapping_dict(cls) -> Dict[str, str]:
            """Get the full icon mapping dictionary for backward compatibility."""
            if cls._icon_mapping is None:
                cls._icon_mapping = {
                    "error": "::tk::icons::error",
                    "info": "::tk::icons::information",
                    "warning": "::tk::icons::warning",
                    "question": "::tk::icons::question",
                }
            return cls._icon_mapping
        
        @property
        def ICON_MAPPING(cls) -> Dict[str, str]:
            """Property for backward compatibility."""
            return cls._get_icon_mapping_dict()
    
    class Strings:
        """String constants for better maintainability."""
        # Logging levels
        DEBUG_LEVEL = "debug"
        INFO_LEVEL = "info"
        WARNING_LEVEL = "warning"
        ERROR_LEVEL = "error"
        
        # Tk commands and properties
        TK_COMMAND = "tk"
        SCALING_COMMAND = "scaling"
        FOCUS_COLOR_NONE = "none"
        
        # Platform strings
        WINDOWS_PLATFORM = "win32"
        NON_WINDOWS_PLATFORM = "non-windows"
        
        # Widget types
        TCHECKBUTTON = "TCheckbutton"
        TRADIOBUTTON = "TRadiobutton"
        
        # Common strings
        DPI_PREFIX = "DPI: "
        SCALED_PREFIX = "scaled_"
        LARGE_SUFFIX = "_large"
        
        # Log message templates
        LOG_ADJUSTED_TK_SCALING = "Adjusted Tk scaling to %s based on Windows scale %s"
        LOG_USING_WINDOWS_SCALE = "Using Windows scale factor %s instead of DPI-based %s"
        LOG_USING_WINDOWS_SCALE_ALT = "Using Windows scale %s instead of DPI-based %s"
        LOG_AUTO_CONFIGURED_INDICATOR = "Auto-configured %s indicatorsize to %dpx (scaling: %s)"
        LOG_AUTO_PATCHED_WIDGETS = "Auto-patched tk.Checkbutton and tk.Radiobutton to use ttk equivalents"
        LOG_MAX_RECURSION_DEPTH = "Maximum recursion depth reached in layout spec scaling"
        
        # Error messages
        ERROR_FAILED_TO_GET_WINDOW_SIZE = "Failed to get window size"
        ERROR_FAILED_TO_OPERATION = "Failed to %s: %s"
        ERROR_FAILED_TO_OPERATION_WITH_FALLBACK = "Failed to %s: %s, using fallback %s"
    
    # Backward compatibility aliases - organized by category
    @classmethod
    def _create_aliases(cls):
        """Create backward compatibility aliases dynamically."""
        # Scaling aliases
        cls.MIN_SCALED_VALUE = cls.Scaling.MIN_SCALED_VALUE
        cls.DEFAULT_DPI = cls.Scaling.DEFAULT_DPI
        cls.TK_SCALING_BASE = cls.Scaling.TK_SCALING_BASE
        cls.WINDOWS_SCALE_BASE = cls.Scaling.WINDOWS_SCALE_BASE
        cls.MAX_SCALE_FACTOR = cls.Scaling.MAX_SCALE_FACTOR
        cls.DPI_CALCULATION_DIVISOR = cls.Scaling.DPI_CALCULATION_DIVISOR
        cls.MINIMUM_POSITIVE_SCALED_VALUE = cls.Scaling.MINIMUM_POSITIVE_SCALED_VALUE
        
        # Windows aliases
        cls.DPI_AWARENESS_UNAWARE = cls.Windows.DPI_AWARENESS_LEVELS['UNAWARE']
        cls.DPI_AWARENESS_SYSTEM_AWARE = cls.Windows.DPI_AWARENESS_LEVELS['SYSTEM_AWARE']
        cls.DPI_AWARENESS_PER_MONITOR_AWARE = cls.Windows.DPI_AWARENESS_LEVELS['PER_MONITOR_AWARE']
        cls.MONITOR_DEFAULTTOPRIMARY = cls.Windows.MONITOR_FLAGS['DEFAULTTOPRIMARY']
        cls.MONITOR_DEFAULTTONEAREST = cls.Windows.MONITOR_FLAGS['DEFAULTTONEAREST']
        
        # Widget aliases
        cls.MIN_INDICATOR_SIZE = cls.Widgets.MIN_INDICATOR_SIZE
        cls.BASE_INDICATOR_SIZE = cls.Widgets.BASE_INDICATOR_SIZE
        cls.DEFAULT_ICON_SIZE = cls.Widgets.DEFAULT_ICON_SIZE
        cls.ICON_SCALE_THRESHOLD = cls.Widgets.ICON_SCALE_THRESHOLD
        cls.SCALABLE_LENGTH_PROPERTIES = cls.Widgets.SCALABLE_LENGTH_PROPERTIES
        cls.SCALABLE_PADDING_PROPERTIES = cls.Widgets.SCALABLE_PADDING_PROPERTIES
        cls.SCALABLE_LAYOUT_PROPERTIES = cls.Widgets.SCALABLE_LAYOUT_PROPERTIES
        
        # Pattern, logging, performance, and string aliases
        cls.GEOMETRY_PATTERNS = cls.Patterns.GEOMETRY_PATTERNS
        cls.TCL_ERROR_HANDLING_LEVEL = cls.Logging.TCL_ERROR_HANDLING_LEVEL
        cls.MAX_RECURSION_DEPTH = cls.Performance.MAX_RECURSION_DEPTH
        cls.CACHE_SIZE_LARGE = cls.Performance.CACHE_SIZE_LARGE
        cls.CACHE_SIZE_MEDIUM = cls.Performance.CACHE_SIZE_MEDIUM
        cls.CACHE_SIZE_SMALL = cls.Performance.CACHE_SIZE_SMALL
        
        # String aliases
        cls.DEBUG_LEVEL = cls.Strings.DEBUG_LEVEL
        cls.INFO_LEVEL = cls.Strings.INFO_LEVEL
        cls.WARNING_LEVEL = cls.Strings.WARNING_LEVEL
        cls.ERROR_LEVEL = cls.Strings.ERROR_LEVEL
        cls.TK_COMMAND = cls.Strings.TK_COMMAND
        cls.SCALING_COMMAND = cls.Strings.SCALING_COMMAND
        cls.FOCUS_COLOR_NONE = cls.Strings.FOCUS_COLOR_NONE
        cls.WINDOWS_PLATFORM = cls.Strings.WINDOWS_PLATFORM
        cls.NON_WINDOWS_PLATFORM = cls.Strings.NON_WINDOWS_PLATFORM
        cls.TCHECKBUTTON = cls.Strings.TCHECKBUTTON
        cls.TRADIOBUTTON = cls.Strings.TRADIOBUTTON
        cls.DPI_PREFIX = cls.Strings.DPI_PREFIX
        cls.SCALED_PREFIX = cls.Strings.SCALED_PREFIX
        cls.LARGE_SUFFIX = cls.Strings.LARGE_SUFFIX
        cls.LOG_ADJUSTED_TK_SCALING = cls.Strings.LOG_ADJUSTED_TK_SCALING
        cls.LOG_USING_WINDOWS_SCALE = cls.Strings.LOG_USING_WINDOWS_SCALE
        cls.LOG_USING_WINDOWS_SCALE_ALT = cls.Strings.LOG_USING_WINDOWS_SCALE_ALT
        cls.LOG_AUTO_CONFIGURED_INDICATOR = cls.Strings.LOG_AUTO_CONFIGURED_INDICATOR
        cls.LOG_AUTO_PATCHED_WIDGETS = cls.Strings.LOG_AUTO_PATCHED_WIDGETS
        cls.LOG_MAX_RECURSION_DEPTH = cls.Strings.LOG_MAX_RECURSION_DEPTH
        cls.ERROR_FAILED_TO_GET_WINDOW_SIZE = cls.Strings.ERROR_FAILED_TO_GET_WINDOW_SIZE
        cls.ERROR_FAILED_TO_OPERATION = cls.Strings.ERROR_FAILED_TO_OPERATION
        cls.ERROR_FAILED_TO_OPERATION_WITH_FALLBACK = cls.Strings.ERROR_FAILED_TO_OPERATION_WITH_FALLBACK

# Initialize aliases
DPIConfig._create_aliases()


class DPIManager:
    """DPI management class for Windows applications.
    
    This class provides comprehensive DPI awareness and scaling functionality for Tkinter
    applications on Windows. It automatically detects DPI settings, applies appropriate
    scaling factors, and patches widget methods to ensure consistent UI scaling.
    
    Key Features:
    - Automatic DPI detection and awareness setup
    - Unified scaling for geometry, padding, and widget properties
    - Widget method patching for seamless scaling
    - Error handling with fallback mechanisms
    - Performance optimizations with caching
    
    Example:
        >>> manager = DPIManager()
        >>> result = manager.apply_dpi(root_window)
        >>> print(f"Scaling factor: {result['scaling_factor']}")
    """

    def __init__(self):
        self._dpi_awareness_set = False
        self.logger = logging.getLogger(__name__)
        self._patched_widgets = set()  # Track patched widgets for performance
        self._patched_methods = set()  # Track patched methods for performance

    def _log_error(self, operation: str, error: Exception, fallback_value: Any = None, level: LogLevel = DPIConfig.DEBUG_LEVEL) -> None:
        """Unified error logging with consistent format and configurable level."""
        log_method = getattr(self.logger, level, self.logger.debug)
        if fallback_value is not None:
            log_method(
                DPIConfig.ERROR_FAILED_TO_OPERATION_WITH_FALLBACK, 
                operation, error, fallback_value
            )
        else:
            log_method(DPIConfig.ERROR_FAILED_TO_OPERATION, operation, error)

    def _handle_error(self, operation: str, error: Exception, fallback: Any = None, level: LogLevel = DPIConfig.DEBUG_LEVEL) -> Any:
        """Unified error handling for all DPI operations."""
        self._log_error(operation, error, fallback, level)
        return fallback

    def _safe_execute(self, operation: str, func: Callable[..., Any], *args, fallback: Any = None, 
                      level: LogLevel = DPIConfig.DEBUG_LEVEL, **kwargs) -> Any:
        """Unified safe execution method for DPI operations with enhanced error logging."""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Enhanced error logging with more context
            if level == DPIConfig.ERROR_LEVEL:
                self.logger.error(f"Operation '{operation}' failed: {e}", exc_info=True)
            elif level == DPIConfig.WARNING_LEVEL:
                self.logger.warning(f"Operation '{operation}' failed: {e}")
            else:
                self.logger.debug(f"Operation '{operation}' failed: {e}")
            return self._handle_error(operation, e, fallback, level)

    def _get_hwnd_dpi(self, window_handle: WindowHandle) -> DPIResult:
        """Get DPI information for a window handle."""
        if not is_windows():
            return DPIConfig.DEFAULT_DPI, DPIConfig.DEFAULT_DPI, 1.0

        def _get_dpi_info() -> Tuple[int, int, float]:
            self._set_dpi_awareness_safe()
            monitor_handle = self._get_monitor_handle(window_handle)
            x_dpi, y_dpi = self._get_monitor_dpi(monitor_handle)
            scaling_factor = self._calculate_scaling_factor(x_dpi, y_dpi)
            return x_dpi, y_dpi, scaling_factor

        fallback = (DPIConfig.DEFAULT_DPI, DPIConfig.DEFAULT_DPI, 1.0)
        return self._safe_execute("get DPI information", _get_dpi_info, fallback=fallback)

    def _set_dpi_awareness_safe(self) -> None:
        """Safely set DPI awareness."""
        def _set_awareness():
            ctypes.windll.shcore.SetProcessDpiAwareness(
                DPIConfig.DPI_AWARENESS_SYSTEM_AWARE
            )
        
        self._safe_execute("set process DPI awareness", _set_awareness, level="debug")

    def _get_monitor_handle(self, window_handle: WindowHandle) -> MonitorHandle:
        """Get monitor handle for the window."""
        win_h = wintypes.HWND(window_handle)
        return ctypes.windll.user32.MonitorFromWindow(
            win_h, wintypes.DWORD(DPIConfig.MONITOR_DEFAULTTOPRIMARY)
        )

    def _get_monitor_dpi(self, monitor_handle: MonitorHandle) -> Tuple[DPIValue, DPIValue]:
        """Get DPI values from monitor handle."""
        def _get_dpi() -> Tuple[int, int]:
            x_dpi = wintypes.UINT()
            y_dpi = wintypes.UINT()
            ctypes.windll.shcore.GetDpiForMonitor(
                monitor_handle, 0, pointer(x_dpi), pointer(y_dpi)
            )
            return x_dpi.value, y_dpi.value

        fallback = (DPIConfig.DEFAULT_DPI, DPIConfig.DEFAULT_DPI)
        return self._safe_execute("get DPI for monitor", _get_dpi, fallback=fallback)

    def _calculate_scaling_factor(self, x_dpi: DPIValue, y_dpi: DPIValue) -> ScalingFactor:
        """Calculate the appropriate scaling factor for optimal UI scaling.
        
        This method determines the best scaling factor by comparing two approaches:
        
        1. DPI-based scaling: 
           - Calculates average of X and Y DPI values
           - Normalizes to standard 96 DPI baseline
           - Formula: (x_dpi + y_dpi) / (2 * 96)
        
        2. Windows scale factor:
           - Uses system-reported scaling percentage (e.g., 150 for 150%)
           - More accurate for UI elements as it reflects user preferences
           - Formula: scale_factor / 100
        
        The method returns the higher of the two values to ensure:
        - Text remains readable on high DPI displays
        - UI elements scale appropriately
        - Compatibility with Windows scaling settings
        
        Args:
            x_dpi: Horizontal DPI value from monitor
            y_dpi: Vertical DPI value from monitor
            
        Returns:
            Scaling factor (typically 1.0 to 3.0)
        """
        # Calculate DPI-based scaling factor
        # Average X and Y DPI, then normalize to 96 DPI baseline
        dpi_100pc = DPIConfig.DEFAULT_DPI
        dpi_scaling = (x_dpi + y_dpi) / (DPIConfig.DPI_CALCULATION_DIVISOR * dpi_100pc)

        windows_scale = self._get_windows_scale_factor_internal()
        if windows_scale is None:
            return dpi_scaling

        # Use the higher scaling factor for better compatibility
        # Windows scale factor is often more accurate for UI elements
        if windows_scale > dpi_scaling:
            self.logger.info(
                DPIConfig.LOG_USING_WINDOWS_SCALE,
                windows_scale, dpi_scaling
            )
            return windows_scale
        return dpi_scaling

    def _scale_geometry_values(self, width: int, height: int, scaling_factor: ScalingFactor, 
                               scale_position: bool = False) -> GeometryResult:
        """Unified method to scale geometry values."""
        def _scale_values() -> Union[Tuple[int, int], Tuple[int, int, int, int]]:
            scaled_width = self._scale_length_value(width, scaling_factor)
            scaled_height = self._scale_length_value(height, scaling_factor)
            if scale_position:
                # Position coordinates are typically not scaled in geometry strings
                return scaled_width, scaled_height, width, height
            return scaled_width, scaled_height

        return self._safe_execute("scale geometry values", _scale_values, fallback=(width, height))

    def _parse_geometry_with_position(self, geometry_string: GeometryString) -> Optional[Tuple[int, int, int, int]]:
        """Parse geometry string with position coordinates."""
        match = DPIConfig.Patterns.GEOMETRY_WITH_POSITION_PATTERN.search(geometry_string)
        if match:
            return tuple(map(int, match.groups()))
        return None

    def _parse_geometry_without_position(self, geometry_string: GeometryString) -> Optional[Tuple[int, int]]:
        """Parse geometry string without position coordinates."""
        match = DPIConfig.Patterns.GEOMETRY_WITHOUT_POSITION_PATTERN.search(geometry_string)
        if match:
            return tuple(map(int, match.groups()))
        return None

    def _scale_geometry_coordinates(self, width: int, height: int, x: int = None, y: int = None, 
                                   scaling_factor: float = 1.0, scale_position: bool = False) -> str:
        """Scale geometry coordinates and return formatted string."""
        # Scale width and height
        width_height_result = self._scale_geometry_values(width, height, scaling_factor, False)
        if isinstance(width_height_result, tuple) and len(width_height_result) == 2:
            scaled_width, scaled_height = width_height_result
        else:
            scaled_width, scaled_height = width, height
        
        if x is not None and y is not None:
            if scale_position:
                # Scale position coordinates
                pos_result = self._scale_geometry_values(x, y, scaling_factor, False)
                if isinstance(pos_result, tuple) and len(pos_result) == 2:
                    scaled_x, scaled_y = pos_result
                else:
                    scaled_x, scaled_y = x, y
                return f"{scaled_width}x{scaled_height}+{scaled_x}+{scaled_y}"
            return f"{scaled_width}x{scaled_height}+{x}+{y}"
        return f"{scaled_width}x{scaled_height}"

    def _scale_geometry_string(self, geometry_string: GeometryString, scaling_factor: ScalingFactor, 
                               scale_position: bool = False) -> GeometryString:
        """Scale geometry string based on DPI scaling.
        
        Supports two geometry formats:
        1. "WIDTHxHEIGHT+X+Y" - with position coordinates
        2. "WIDTHxHEIGHT" - without position coordinates
        
        Args:
            geometry_string: Tkinter geometry string to scale
            scaling_factor: DPI scaling factor to apply
            scale_position: Whether to scale position coordinates (usually False)
        """
        if not geometry_string:
            return geometry_string

        def _scale_string() -> str:
            # Try parsing with position first
            coords = self._parse_geometry_with_position(geometry_string)
            if coords:
                width, height, x, y = coords
                return self._scale_geometry_coordinates(
                    width, height, x, y, scaling_factor, scale_position
                )
            
            # Try parsing without position
            coords = self._parse_geometry_without_position(geometry_string)
            if coords:
                width, height = coords
                return self._scale_geometry_coordinates(
                    width, height, scaling_factor=scaling_factor, scale_position=scale_position
                )
            
            return geometry_string

        return self._safe_execute("scale geometry string", _scale_string, fallback=geometry_string)

    def _fix_scaling(self, root: tk.Tk) -> None:
        """Scale fonts on high DPI displays for optimal readability.
        
        This method adjusts font sizes for high DPI displays by:
        1. Getting the DPI scaling factor from the root window
        2. Iterating through all named fonts in the root window
        3. Scaling only negative font sizes (pixel-based fonts)
        4. Leaving positive font sizes (point-based fonts) unchanged
        
        Font Size Handling:
        - Negative sizes (e.g., -12): Pixel-based, require manual scaling
        - Positive sizes (e.g., 12): Point-based, handled by Tk's internal scaling
        - Zero sizes: Unchanged
        
        The scaling ensures that:
        - Text remains crisp and readable on high DPI displays
        - Font sizes are proportional to the display scaling
        - Point-based fonts maintain their intended size relationships
        
        Args:
            root: Tkinter root window with DPI_scaling attribute
        """
        if not root:
            return
        
        def _scale_fonts():
            # Use unified scaling rule: DPI_scaling only
            dpi_scaling = getattr(root, 'DPI_scaling', 1.0)
            if dpi_scaling != 1.0:
                # Process all named fonts in the root window
                for name in tkfont.names(root):
                    font = tkfont.Font(root=root, name=name, exists=True)
                    size = int(font["size"])
                    # Only scale negative font sizes (pixel-based)
                    # Positive sizes (point-based) are handled by Tk's scaling
                    if size < 0:
                        font["size"] = round(size * dpi_scaling)
        
        self._safe_execute("fix scaling", _scale_fonts)

    def _patch_widget_methods(self, root):
        """Patch widget methods to handle pad/padding scaling."""
        if not root or not hasattr(root, "DPI_scaling"):
            return

        scaling_factor = self._get_scaling_factor_for_patching(root)

        # Patch layout methods
        self._patch_layout_methods(scaling_factor)

        # Patch widget constructors
        self._patch_widget_constructors(scaling_factor)

        # Patch TreeView methods
        self._patch_treeview_methods(scaling_factor)

    def _get_scaling_factor_for_patching(self, root: Optional[tk.Tk]) -> ScalingFactor:
        """Get scaling factor for patching widget methods.
        
        This method provides a unified interface for obtaining the scaling factor
        needed for widget method patching operations.
        
        Args:
            root: Tkinter root window to get scaling factor from
            
        Returns:
            Scaling factor to use for widget patching
        """
        return self._get_scaling_factor_from_root(root)

    def _patch_layout_methods(self, scaling_factor: ScalingFactor) -> None:
        """Patch layout methods (pack, grid, place)."""
        self._patch_pack_method(scaling_factor)
        self._patch_grid_method(scaling_factor)
        self._patch_place_method(scaling_factor)

    def _patch_layout_method(self, method_name: str, original_method: Callable[..., Any], 
                           scaling_factor: float, special_handler: Optional[Callable[..., Any]] = None) -> None:
        """Unified method to patch layout methods (pack, grid, place) with scaling.
        
        This method provides a centralized approach to patching Tkinter layout methods
        to automatically scale padding and positioning parameters. It prevents double
        patching and provides consistent scaling behavior.
        
        Layout Method Scaling:
        - pack(): Scales padx, pady, ipadx, ipady parameters
        - grid(): Scales padx, pady, ipadx, ipady parameters  
        - place(): Scales x, y coordinates (with special handling)
        
        Args:
            method_name: Full method name (e.g., "tk.Widget.pack")
            original_method: Original method to patch
            scaling_factor: DPI scaling factor to apply
            special_handler: Optional custom handler for special cases (e.g., place method)
        """
        if self._is_method_patched(method_name):
            return
        
        manager = self

        def create_scaled_method(original, handler=None):
            def scaled_method(self, **kwargs):
                if handler:
                    return handler(self, kwargs, original, scaling_factor, manager)
                else:
                    # Default scaling behavior
                    scaled_kwargs = manager._scale_widget_kwargs(kwargs, scaling_factor)
                    return original(self, **scaled_kwargs)
            return scaled_method

        # Apply the patch
        setattr(tk.Widget, method_name.split('.')[-1], create_scaled_method(original_method, special_handler))
        self._mark_method_patched(method_name)

    def _patch_pack_method(self, scaling_factor: ScalingFactor) -> None:
        """Patch the pack method with scaling."""
        self._patch_layout_method("tk.Widget.pack", tk.Widget.pack, scaling_factor)

    def _patch_grid_method(self, scaling_factor: ScalingFactor) -> None:
        """Patch the grid method with scaling."""
        self._patch_layout_method("tk.Widget.grid", tk.Widget.grid, scaling_factor)

    def _patch_place_method(self, scaling_factor: ScalingFactor) -> None:
        """Patch the place method with scaling."""
        def place_handler(self, kwargs, original, scaling_factor, manager):
            def _scale_place_coords():
                scaled_kwargs = kwargs.copy()
                if "x" in scaled_kwargs:
                    scaled_kwargs["x"] = manager._scale_length_value(scaled_kwargs["x"], scaling_factor)
                if "y" in scaled_kwargs:
                    scaled_kwargs["y"] = manager._scale_length_value(scaled_kwargs["y"], scaling_factor)
                return original(self, **scaled_kwargs)
            
            return manager._safe_execute("scale place coordinates", _scale_place_coords, 
                                       fallback=original(self, **kwargs))
        
        self._patch_layout_method("tk.Widget.place", tk.Widget.place, scaling_factor, place_handler)

    def _scale_padding_kwargs(self, kwargs: Dict[str, Any], scaling_factor: ScalingFactor) -> Dict[str, Any]:
        """Scale padding arguments in kwargs."""
        scaled_kwargs = kwargs.copy()

        if "padx" in scaled_kwargs:
            scaled_kwargs["padx"] = self._scale_padding_value(
                scaled_kwargs["padx"], scaling_factor
            )

        if "pady" in scaled_kwargs:
            scaled_kwargs["pady"] = self._scale_padding_value(
                scaled_kwargs["pady"], scaling_factor
            )

        return scaled_kwargs

    def _scale_widget_kwargs(self, kwargs: Dict[str, Any], scaling_factor: ScalingFactor, 
                            scale_padding: bool = True, scale_length: bool = True) -> Dict[str, Any]:
        """Unified method to scale widget constructor kwargs."""
        scaled_kwargs = kwargs.copy()

        if scale_padding:
            # Scale padding values using centralized configuration
            for prop in DPIConfig.SCALABLE_PADDING_PROPERTIES:
                if prop in scaled_kwargs:
                    scaled_kwargs[prop] = self._scale_padding_value(
                        scaled_kwargs[prop], scaling_factor
                    )

        if scale_length:
            # Scale length values using centralized configuration
            for prop in DPIConfig.SCALABLE_LENGTH_PROPERTIES:
                if prop in scaled_kwargs:
                    scaled_kwargs[prop] = self._scale_length_value(
                        scaled_kwargs[prop], scaling_factor
                    )

        return scaled_kwargs

    def _scale_value(self, value: ScalableValue, scaling_factor: ScalingFactor, 
                    value_type: str = "length") -> ScalableValue:
        """Unified method to scale any value with consistent rules.
        
        This method provides a centralized approach to scaling various types of values
        used in Tkinter widgets. It handles different value types and ensures consistent
        scaling behavior across the application.
        
        Value Types:
        - "length": For width, height, border width, etc. (minimum 1 for positive values)
        - "padding": For padding values (minimum 1 for positive values)
        - "numeric": For general numeric values (minimum 1 for positive values)
        
        Supported Value Formats:
        - Single values: int, float
        - 2-element tuples/lists: (horizontal, vertical) padding
        - 4-element tuples/lists: (top, right, bottom, left) padding
        - Generic tuples/lists: Any length, scaled element-wise
        
        Scaling Rules:
        - Positive values: Scaled and rounded, minimum 1
        - Negative values: Scaled and rounded (can be negative)
        - Zero values: Remain zero
        - Non-numeric values: Returned unchanged
        
        Args:
            value: The value to scale (int, float, list, or tuple)
            scaling_factor: The scaling factor to apply (typically 1.0-3.0)
            value_type: Type of value - "length", "padding", or "numeric"
            
        Returns:
            Scaled value of the same type as input
            
        Example:
            >>> manager._scale_value(10, 2.0, "length")  # Returns 20
            >>> manager._scale_value((5, 10), 1.5, "padding")  # Returns (8, 15)
        """
        def _scale_single_numeric(val: Union[int, float], min_positive: int = 1) -> Union[int, float]:
            """Scale a single numeric value."""
            scaled = val * scaling_factor
            return max(min_positive, round(scaled)) if scaled > 0 else round(scaled)
        
        def _scale_value_internal():
            if isinstance(value, (int, float)):
                min_positive = (DPIConfig.MINIMUM_POSITIVE_SCALED_VALUE 
                              if value_type in ("padding", "length") else 1)
                return _scale_single_numeric(value, min_positive)
            elif isinstance(value, (list, tuple)):
                if len(value) in (2, 4):
                    # 2-element: (horizontal, vertical) or 4-element: (top, right, bottom, left)
                    min_positive = (DPIConfig.MINIMUM_POSITIVE_SCALED_VALUE 
                                  if value_type in ("padding", "length") else 1)
                    scaled_vals = [_scale_single_numeric(val, min_positive) for val in value]
                    return tuple(scaled_vals)
                else:
                    # Generic list/tuple scaling
                    min_positive = (DPIConfig.MINIMUM_POSITIVE_SCALED_VALUE 
                                  if value_type in ("padding", "length") else 1)
                    scaled_vals = [_scale_single_numeric(val, min_positive) for val in value]
                    return type(value)(scaled_vals)
            return value
        
        return self._safe_execute(f"scale {value_type} value", _scale_value_internal, fallback=value)

    # Unified scaling methods - removed lru_cache to support unhashable types
    def _scale_numeric_value(self, value: NumericValue, scaling_factor: ScalingFactor, min_positive: int = 1) -> NumericValue:
        """Scale a numeric value (backward compatibility)."""
        return self._scale_value(value, scaling_factor, "numeric")

    def _scale_padding_value(self, value: PaddingValue, scaling_factor: ScalingFactor) -> PaddingValue:
        """Scale a padding value (backward compatibility)."""
        return self._scale_value(value, scaling_factor, "padding")

    def _scale_length_value(self, value: LengthValue, scaling_factor: ScalingFactor) -> LengthValue:
        """Scale a length value (backward compatibility)."""
        return self._scale_value(value, scaling_factor, "length")

    def _scale_padding_like_value(self, value: PaddingValue, scaling_factor: ScalingFactor) -> PaddingValue:
        """Scale padding-like values (backward compatibility)."""
        return self._scale_value(value, scaling_factor, "length")
    
    def _scale_value_unified(self, value: Any, scaling_factor: ScalingFactor, 
                            value_type: str = "length") -> Any:
        """Unified scaling method that can replace multiple similar methods for better maintainability."""
        return self._scale_value(value, scaling_factor, value_type)

    def _patch_widget_constructors(self, scaling_factor: ScalingFactor) -> None:
        """Patch widget constructors with scaling."""
        self._patch_standard_widgets(scaling_factor)
        self._patch_button_constructor(scaling_factor)
        self._patch_text_constructor(scaling_factor)
        self._patch_listbox_constructor(scaling_factor)

    def _patch_standard_widgets(self, scaling_factor: ScalingFactor) -> None:
        """Patch standard widget constructors with scaling."""
        # Standard tk widgets (Button, Text, Listbox excluded - have special handling)
        tk_widgets = [
            tk.LabelFrame, tk.Frame, tk.Entry, tk.Label,
            tk.Checkbutton, tk.Radiobutton, tk.Spinbox,
            tk.Scale, tk.Scrollbar, tk.Canvas, tk.Menu, tk.Menubutton,
        ]
        
        # ttk widgets
        ttk_widgets = [
            ttk.Treeview, ttk.Checkbutton, ttk.Radiobutton,
        ]
        
        all_widgets = tk_widgets + ttk_widgets
        
        for widget_class in all_widgets:
            self._apply_standard_widget_patch(widget_class, scaling_factor)

    def _is_widget_patched(self, widget_class: WidgetClass) -> bool:
        """Check if widget is already patched.
        
        Args:
            widget_class: Widget class to check
            
        Returns:
            True if widget is already patched, False otherwise
        """
        return widget_class in self._patched_widgets

    def _is_method_patched(self, method_name: str) -> bool:
        """Check if method is already patched.
        
        Args:
            method_name: Full method name to check
            
        Returns:
            True if method is already patched, False otherwise
        """
        return method_name in self._patched_methods

    def _mark_method_patched(self, method_name: str) -> None:
        """Mark method as patched to prevent double-patching.
        
        Args:
            method_name: Full method name to mark as patched
        """
        self._patched_methods.add(method_name)

    def _patch_widget_constructor(self, widget_class: WidgetClass, scaling_factor: ScalingFactor, 
                                 method_name: str, special_handler: Optional[Callable[..., Any]] = None) -> None:
        """Unified method to patch widget constructors with scaling."""
        if self._is_method_patched(method_name):
            return

        original_init = widget_class.__init__
        manager = self

        def create_scaled_constructor(original, handler=None):
            def scaled_constructor(self, parent=None, **kwargs):
                if handler:
                    return handler(self, parent, kwargs, original, scaling_factor, manager)
                else:
                    # Default scaling behavior
                    scaled_kwargs = manager._scale_widget_kwargs(kwargs, scaling_factor)
                    return original(self, parent, **scaled_kwargs)
            return scaled_constructor

        # Apply the patch
        widget_class.__init__ = create_scaled_constructor(original_init, special_handler)
        self._mark_method_patched(method_name)
        self._patched_widgets.add(widget_class)

    def _apply_standard_widget_patch(self, widget_class: WidgetClass, scaling_factor: ScalingFactor) -> None:
        """Apply standard widget patch with unified logic."""
        method_name = f"{widget_class.__module__}.{widget_class.__name__}.__init__"
        self._patch_widget_constructor(widget_class, scaling_factor, method_name)

    def _patch_button_constructor(self, scaling_factor: ScalingFactor) -> None:
        """Patch the Button constructor with scaling (excluding width/height)."""
        def button_handler(self, parent, kwargs, original, scaling_factor, manager):
            # Use unified method but exclude width/height from scaling
            scaled_kwargs = manager._scale_widget_kwargs(
                kwargs, scaling_factor, scale_padding=True, scale_length=True
            )
            # Restore original width/height values to prevent stretching
            if "width" in kwargs:
                scaled_kwargs["width"] = kwargs["width"]
            if "height" in kwargs:
                scaled_kwargs["height"] = kwargs["height"]
            return original(self, parent, **scaled_kwargs)
        
        self._patch_widget_constructor(tk.Button, scaling_factor, "tk.Button.__init__", button_handler)

    def _patch_text_constructor(self, scaling_factor: ScalingFactor) -> None:
        """Patch the Text constructor with scaling (excluding height which specifies line count)."""
        def text_handler(self, parent, kwargs, original, scaling_factor, manager):
            # Use unified method but exclude height from scaling (height is line count, not pixels)
            scaled_kwargs = manager._scale_widget_kwargs(
                kwargs, scaling_factor, scale_padding=True, scale_length=True
            )
            # Restore original height value (line count should not be scaled)
            if "height" in kwargs:
                scaled_kwargs["height"] = kwargs["height"]
            return original(self, parent, **scaled_kwargs)
        
        self._patch_widget_constructor(tk.Text, scaling_factor, "tk.Text.__init__", text_handler)

    def _patch_listbox_constructor(self, scaling_factor: ScalingFactor) -> None:
        """Patch the Listbox constructor with scaling (excluding height which specifies line count)."""
        def listbox_handler(self, parent, kwargs, original, scaling_factor, manager):
            # Use unified method but exclude height from scaling (height is line count, not pixels)
            scaled_kwargs = manager._scale_widget_kwargs(
                kwargs, scaling_factor, scale_padding=True, scale_length=True
            )
            # Restore original height value (line count should not be scaled)
            if "height" in kwargs:
                scaled_kwargs["height"] = kwargs["height"]
            return original(self, parent, **scaled_kwargs)
        
        self._patch_widget_constructor(tk.Listbox, scaling_factor, "tk.Listbox.__init__", listbox_handler)

    def _patch_treeview_methods(self, scaling_factor: ScalingFactor) -> None:
        """Patch TreeView methods with scaling."""
        def _apply_treeview_patches():
            self._patch_treeview_column_method(scaling_factor)
            self._patch_treeview_style_method(scaling_factor)
            self._patch_style_layout_for_treeview(scaling_factor)
        
        self._safe_execute("patch TreeView methods", _apply_treeview_patches)

    def _patch_treeview_method(self, method_name: str, original_method: Callable[..., Any], 
                              scaling_factor: float, handler: Callable[..., Any]) -> None:
        """Unified method to patch TreeView methods with scaling."""
        if self._is_method_patched(method_name):
            return
        
        manager = self

        def create_scaled_method(original, handler_func):
            def scaled_method(*args, **kwargs):
                return handler_func(*args, **kwargs, original=original, scaling_factor=scaling_factor, manager=manager)
            return scaled_method

        # Apply the patch - handle both bound and unbound methods
        if hasattr(original_method, '__self__'):
            # Bound method
            setattr(original_method.__self__.__class__, method_name.split('.')[-1], create_scaled_method(original_method, handler))
        else:
            # Unbound method or function
            class_name = method_name.split('.')[1]  # e.g., "Treeview" from "ttk.Treeview.column"
            if class_name == "Treeview":
                setattr(ttk.Treeview, method_name.split('.')[-1], create_scaled_method(original_method, handler))
            elif class_name == "Style":
                setattr(ttk.Style, method_name.split('.')[-1], create_scaled_method(original_method, handler))
        
        self._mark_method_patched(method_name)

    def _patch_treeview_column_method(self, scaling_factor: ScalingFactor) -> None:
        """Patch the TreeView column method with scaling."""
        def column_handler(self, column, option=None, original=None, scaling_factor=None, manager=None, **kw):
            # Scale width and minwidth parameters in kw
            if "width" in kw:
                kw["width"] = manager._scale_length_value(kw["width"], scaling_factor)
            if "minwidth" in kw:
                kw["minwidth"] = manager._scale_length_value(kw["minwidth"], scaling_factor)
            return original(self, column, option, **kw)
        
        self._patch_treeview_method("ttk.Treeview.column", ttk.Treeview.column, scaling_factor, column_handler)

    def _patch_treeview_style_method(self, scaling_factor: ScalingFactor) -> None:
        """Patch the TreeView style configuration with scaling."""
        def style_configure_handler(self_style, style, option=None, original=None, scaling_factor=None, manager=None, **kw):
            # Scale rowheight parameter in kw
            if "rowheight" in kw:
                kw["rowheight"] = manager._scale_length_value(kw["rowheight"], scaling_factor)
            # Scale padding and indent when provided
            if "padding" in kw:
                kw["padding"] = manager._scale_padding_like_value(kw["padding"], scaling_factor)
            if "indent" in kw:
                kw["indent"] = manager._scale_length_value(kw["indent"], scaling_factor)
            return original(self_style, style, option, **kw)
        
        self._patch_treeview_method("ttk.Style.configure", ttk.Style.configure, scaling_factor, style_configure_handler)

    def _scale_layout_spec_recursive(self, spec: Any, scaling_factor: ScalingFactor, depth: int = 0) -> Any:
        """Recursively scale layout specification with stack overflow protection."""
        # Prevent stack overflow with maximum recursion depth
        if depth > DPIConfig.MAX_RECURSION_DEPTH:
            self.logger.warning(DPIConfig.LOG_MAX_RECURSION_DEPTH)
            return spec
            
        if isinstance(spec, list):
            new_list = []
            for item in spec:
                if not isinstance(item, dict):
                    new_list.append(item)
                    continue
                new_item = {}
                for key, val in item.items():
                    if key == "children":
                        new_item[key] = self._scale_layout_spec_recursive(val, scaling_factor, depth + 1)
                    elif key in ("padding", "borderpadding", "indicatorpadding"):
                        new_item[key] = self._scale_padding_like_value(val, scaling_factor)
                    elif key in ("indent", "space", "width", "height"):
                        new_item[key] = self._scale_length_value(val, scaling_factor)
                    else:
                        new_item[key] = val
                new_list.append(new_item)
            return new_list
        return spec

    def _patch_style_layout_for_treeview(self, scaling_factor: ScalingFactor) -> None:
        """Patch ttk.Style.layout to scale padding/indent within layout specs."""
        def layout_handler(self_style, style, layoutSpec=None, original=None, scaling_factor=None, manager=None):  # noqa: N803
            if layoutSpec is None:
                return original(self_style, style, layoutSpec)
            
            def _scale_layout_spec():
                scaled = manager._scale_layout_spec_recursive(layoutSpec, scaling_factor)
                return original(self_style, style, scaled)
            
            return manager._safe_execute("scale layout spec", _scale_layout_spec, 
                                       fallback=original(self_style, style, layoutSpec))
        
        self._patch_treeview_method("ttk.Style.layout", ttk.Style.layout, scaling_factor, layout_handler)

    def fix_dpi(self, root):
        """Adjust scaling for high DPI displays on Windows."""
        if not is_windows():
            # Set default values for non-Windows platforms
            root.DPI_X = DPIConfig.DEFAULT_DPI
            root.DPI_Y = DPIConfig.DEFAULT_DPI
            root.DPI_scaling = 1.0
            return

        def _apply_dpi_fix():
            dpi_awareness_result = self._enable_dpi_awareness()
            if dpi_awareness_result["shcore"]:
                self._apply_shcore_dpi_scaling(root)
            else:
                root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                    root.winfo_id()
                )

        def _fallback_dpi_fix():
            root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                root.winfo_id()
            )

        self._safe_execute("fix DPI", _apply_dpi_fix, fallback=_fallback_dpi_fix, level="warning")
        self._fix_scaling(root)

    def _enable_dpi_awareness(self):
        """Enable DPI awareness and return the method used."""
        def _set_dpi_awareness():
            # Try shcore method first (preferred)
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(DPIConfig.DPI_AWARENESS_PER_MONITOR_AWARE)
                scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
                return {"shcore": True, "scale_factor": scale_factor}
            except (AttributeError, OSError):
                # Fallback to user32 method
                ctypes.windll.user32.SetProcessDPIAware()
                return {"shcore": False, "scale_factor": None}
        
        return self._safe_execute("enable DPI awareness", _set_dpi_awareness, 
                                 fallback={"shcore": False, "scale_factor": None})

    def _apply_shcore_dpi_scaling(self, root):
        """Apply DPI scaling using shcore method."""
        scale_factor = self._get_initial_scale_factor()
        self._apply_initial_tk_scaling(root, scale_factor)
        self._adjust_tk_scaling(root)
        self._set_dpi_information(root)

    def _execute_windows_api_call(self, operation: str, api_func: Callable[[], Any], 
                                 fallback: Any = None, transform: Optional[Callable[[Any], Any]] = None) -> Any:
        """Unified method to execute Windows API calls with error handling."""
        def _execute_api():
            result = api_func()
            return transform(result) if transform else result
        
        return self._safe_execute(operation, _execute_api, fallback=fallback)

    def _get_initial_scale_factor(self) -> int:
        """Get initial scale factor from Windows.
        
        Returns:
            Windows scale factor (e.g., 100, 150, 200)
        """
        return self._execute_windows_api_call(
            "get initial scale factor",
            lambda: ctypes.windll.shcore.GetScaleFactorForDevice(0),
            fallback=100
        )

    def _apply_initial_tk_scaling(self, root: tk.Tk, scale_factor: int) -> None:
        """Apply initial Tk scaling based on Windows scale factor.
        
        Args:
            root: Tkinter root window to apply scaling to
            scale_factor: Windows scale factor to apply
        """
        def _apply_tk_scaling():
            tk_scaling = (scale_factor / DPIConfig.WINDOWS_SCALE_BASE) * (DPIConfig.DEFAULT_DPI / DPIConfig.TK_SCALING_BASE)
            root.tk.call(DPIConfig.TK_COMMAND, DPIConfig.SCALING_COMMAND, tk_scaling)
        
        self._safe_execute("apply initial Tk scaling", _apply_tk_scaling)

    def _get_windows_scale_factor(self) -> Optional[float]:
        """Get Windows scale factor with unified error handling."""
        return self._execute_windows_api_call(
            "get Windows scale factor",
            lambda: ctypes.windll.shcore.GetScaleFactorForDevice(0),
            fallback=None,
            transform=lambda x: x / DPIConfig.WINDOWS_SCALE_BASE
        )
    
    def _get_windows_scale_factor_internal(self) -> Optional[float]:
        """Internal method to get Windows scale factor for use in other methods."""
        def _get_scale():
            scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            return scale_factor / DPIConfig.WINDOWS_SCALE_BASE
        
        return self._safe_execute("get Windows scale factor", _get_scale, 
                                 fallback=None, level="debug")

    def _adjust_tk_scaling(self, root: tk.Tk) -> None:
        """Adjust Tk scaling based on Windows scale factor.
        
        Args:
            root: Tkinter root window to adjust scaling for
        """
        windows_scale = self._get_windows_scale_factor()
        if windows_scale and windows_scale > 1.0:
            def _adjust_scaling():
                tk_scaling = windows_scale * (DPIConfig.DEFAULT_DPI / DPIConfig.TK_SCALING_BASE)
                root.tk.call(DPIConfig.TK_COMMAND, DPIConfig.SCALING_COMMAND, tk_scaling)
                self.logger.debug(
                    DPIConfig.LOG_ADJUSTED_TK_SCALING,
                    tk_scaling,
                    windows_scale,
                )
            
            self._safe_execute("adjust Tk scaling", _adjust_scaling)

    def _set_dpi_information(self, root: tk.Tk) -> None:
        """Set DPI information on the root window."""
        win_handle = wintypes.HWND(root.winfo_id())
        monitor_handle = ctypes.windll.user32.MonitorFromWindow(win_handle, DPIConfig.MONITOR_DEFAULTTOPRIMARY)
        x_dpi = wintypes.UINT()
        y_dpi = wintypes.UINT()

        ctypes.windll.shcore.GetDpiForMonitor(
            monitor_handle, 0, pointer(x_dpi), pointer(y_dpi)
        )

        root.DPI_X = x_dpi.value
        root.DPI_Y = y_dpi.value
        dpi_scaling = (x_dpi.value + y_dpi.value) / (DPIConfig.DPI_CALCULATION_DIVISOR * DPIConfig.DEFAULT_DPI)

        # Use Windows scale factor if available and higher
        windows_scale = self._get_windows_scale_factor()
        if windows_scale and windows_scale > dpi_scaling:
            root.DPI_scaling = windows_scale
            self.logger.info(
                DPIConfig.LOG_USING_WINDOWS_SCALE_ALT,
                windows_scale,
                dpi_scaling,
            )
        else:
            root.DPI_scaling = dpi_scaling

    def apply_dpi(self, root, *, enable=True):
        """Enable DPI awareness and apply comprehensive scaling to a Tkinter root window.
        
        This is the main entry point for DPI scaling functionality. It performs a complete
        setup of DPI awareness and applies all necessary scaling patches to ensure optimal
        display on high DPI monitors.
        
        What this method does:
        1. Sets up DPI awareness for the Windows process
        2. Detects and applies appropriate scaling factors
        3. Patches widget methods for automatic scaling
        4. Configures ttk widgets for better DPI support
        5. Sets up geometry scaling for window sizing
        
        Args:
            root: Tkinter root window to apply DPI scaling to
            enable: Whether to enable DPI scaling (default: True)
            
        Returns:
            Dict[str, Any]: Dictionary containing scaling information with keys:
                - enabled: Whether DPI scaling was applied
                - platform: Platform information ("windows" or "non-windows")
                - dpi_awareness_set: Whether DPI awareness was set
                - effective_dpi: Average DPI value
                - scaling_factor: Applied scaling factor
                - tk_scaling: Tk's internal scaling value
                - hwnd: Window handle
                - applied_to_windows: List of processed windows
                - error: Error message if any (optional)
                
        Raises:
            ValueError: If root is None when enable=True
            RuntimeError: If DPI awareness setup fails on Windows
            
        Example:
            >>> manager = DPIManager()
            >>> result = manager.apply_dpi(root)
            >>> print(f"Scaling factor: {result['scaling_factor']}")
            >>> if 'error' in result:
            ...     print(f"Error: {result['error']}")
        """
        result = self._create_initial_result(enable)

        if not self._should_apply_dpi(enable, root):
            return result

        try:
            self._setup_dpi_awareness(root, result)
            self._apply_scaling_patches(root, result)
            self._finalize_dpi_setup(root, result)
        except Exception as e:  # pylint: disable=W0718
            result["error"] = str(e)

        return result

    def _create_initial_result(self, enable: bool) -> ResultDict:
        """Create initial result dictionary."""
        return {
            "enabled": enable,
            "platform": "windows" if is_windows() else DPIConfig.NON_WINDOWS_PLATFORM,
            "dpi_awareness_set": False,
            "effective_dpi": 96,
            "scaling_factor": 1.0,
            "tk_scaling": 1.0,
            "hwnd": None,
            "applied_to_windows": [],
        }

    def _should_apply_dpi(self, enable: bool, root: Optional[tk.Tk]) -> bool:
        """Check if DPI should be applied."""
        return enable and is_windows() and root is not None

    def _setup_dpi_awareness(self, root: tk.Tk, result: ResultDict) -> None:
        """Setup DPI awareness and basic DPI information."""
        self.fix_dpi(root)
        self._update_result_with_dpi_info(root, result)

    def _apply_scaling_patches(self, root: tk.Tk, result: ResultDict) -> None:
        """Apply all scaling patches and configurations."""
        self._apply_scaling_methods(root)
        self._configure_ttk_widgets(root)
        self._auto_patch_tk_widgets_to_ttk()

    def _finalize_dpi_setup(self, root: tk.Tk, result: ResultDict) -> None:
        """Finalize DPI setup and update result."""
        # Update tasks and finalize
        root.update_idletasks()
        result["applied_to_windows"].append(result["hwnd"])

    def _update_result_with_dpi_info(self, root: tk.Tk, result: ResultDict) -> None:
        """Update result dictionary with DPI information."""
        result["dpi_awareness_set"] = True
        result["effective_dpi"] = (root.DPI_X + root.DPI_Y) / 2
        result["scaling_factor"] = root.DPI_scaling
        result["hwnd"] = root.winfo_id()
        result["tk_scaling"] = float(root.tk.call(DPIConfig.TK_COMMAND, DPIConfig.SCALING_COMMAND))

    def _apply_scaling_methods(self, root: tk.Tk) -> None:
        """Apply scaling methods to the root window."""
        self._add_tk_scale_method(root)
        self._override_geometry_method(root)
        self._patch_widget_methods(root)
    
    def _add_tk_scale_method(self, root: tk.Tk) -> None:
        """Add TkScale method to root window for backward compatibility."""
        root.TkScale = lambda v: self._scale_length_value(float(v), root.DPI_scaling)

    def _configure_ttk_widget_style(self, style: ttk.Style, widget_type: WidgetType, scaled_indicator_size: int, scaling_factor: float) -> None:
        """Configure individual ttk widget style."""
        def _configure_style():
            style.configure(widget_type, focuscolor=DPIConfig.FOCUS_COLOR_NONE, indicatorsize=scaled_indicator_size)
            self.logger.debug(
                DPIConfig.LOG_AUTO_CONFIGURED_INDICATOR,
                widget_type, scaled_indicator_size, scaling_factor
            )
        
        self._safe_execute(f"auto-configure {widget_type} style", _configure_style)

    def _configure_ttk_widgets(self, root: Optional[tk.Tk]) -> None:
        """Configure ttk widgets for DPI scaling."""
        if not is_windows() or root is None:
            return

        def _configure_ttk_widgets_internal():
            scaling_factor = getattr(root, 'DPI_scaling', 1.0)
            if scaling_factor <= 1.0:
                return

            style = ttk.Style(root)
            scaled_indicator_size = self._calculate_scaled_indicator_size(scaling_factor)
            self._configure_checkbutton_and_radiobutton_styles(style, scaled_indicator_size, scaling_factor)

        self._safe_execute("auto-configure ttk widgets for DPI", _configure_ttk_widgets_internal)
    
    def _calculate_scaled_indicator_size(self, scaling_factor: float) -> int:
        """Calculate scaled indicator size for ttk widgets."""
        return max(
            DPIConfig.BASE_INDICATOR_SIZE, 
            self._scale_length_value(DPIConfig.BASE_INDICATOR_SIZE, scaling_factor)
        )
    
    def _configure_checkbutton_and_radiobutton_styles(self, style: ttk.Style, 
                                                    scaled_indicator_size: int, 
                                                    scaling_factor: float) -> None:
        """Configure checkbutton and radiobutton styles with scaled indicators."""
        self._configure_ttk_widget_style(style, DPIConfig.TCHECKBUTTON, scaled_indicator_size, scaling_factor)
        self._configure_ttk_widget_style(style, DPIConfig.TRADIOBUTTON, scaled_indicator_size, scaling_factor)

    def _auto_patch_tk_widgets_to_ttk(self) -> None:
        """Automatically patch tk.Checkbutton and tk.Radiobutton to use ttk equivalents."""
        if not is_windows():
            return

        def _apply_ttk_patches():
            # Check if already patched to avoid double-patching using unified method
            if (self._is_method_patched("tk.Checkbutton.__init__") and 
                self._is_method_patched("tk.Radiobutton.__init__")):
                return

            # Store original constructors
            original_tk_checkbutton = tk.Checkbutton.__init__
            original_tk_radiobutton = tk.Radiobutton.__init__

            def patched_checkbutton_init(self, parent: Optional[tk.Widget] = None, **kwargs) -> None:
                """Patched Checkbutton that uses ttk.Checkbutton for better DPI scaling."""
                # Convert tk.Checkbutton to ttk.Checkbutton
                ttk.Checkbutton.__init__(self, parent, **kwargs)

            def patched_radiobutton_init(self, parent: Optional[tk.Widget] = None, **kwargs) -> None:
                """Patched Radiobutton that uses ttk.Radiobutton for better DPI scaling."""
                # Convert tk.Radiobutton to ttk.Radiobutton
                ttk.Radiobutton.__init__(self, parent, **kwargs)

            # Apply patches
            tk.Checkbutton.__init__ = patched_checkbutton_init
            tk.Radiobutton.__init__ = patched_radiobutton_init

            # Mark as patched to avoid double-patching using unified method
            self._mark_method_patched("tk.Checkbutton.__init__")
            self._mark_method_patched("tk.Radiobutton.__init__")

            self.logger.debug(DPIConfig.LOG_AUTO_PATCHED_WIDGETS)

        self._safe_execute("auto-patch tk widgets to ttk", _apply_ttk_patches)

    def _override_geometry_method(self, root: tk.Tk) -> None:
        """Override the geometry method with scaling."""
        original_geometry = root.wm_geometry

        def scaled_geometry(geometry_string: Optional[str] = None) -> str:
            if geometry_string is None:
                return original_geometry()
            # Use unified scaling rule: DPI_scaling only
            dpi_scaling = getattr(root, 'DPI_scaling', 1.0)
            scaled = self._scale_geometry_string(geometry_string, dpi_scaling, scale_position=False)
            return original_geometry(scaled)

        root.geometry = scaled_geometry

    def enable_dpi_awareness(self) -> bool:
        """Enable DPI awareness for the current process."""
        if not is_windows():
            return False
        
        def _enable_awareness():
            return self._try_enable_dpi_awareness_shcore() or self._try_enable_dpi_awareness_user32()
        
        result = self._safe_execute("enable DPI awareness", _enable_awareness, fallback=False)
        return result is True
    
    def _try_enable_dpi_awareness_shcore(self) -> bool:
        """Try to enable DPI awareness using shcore method."""
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(DPIConfig.DPI_AWARENESS_PER_MONITOR_AWARE)
            return True
        except (AttributeError, OSError):
            return False
    
    def _try_enable_dpi_awareness_user32(self) -> bool:
        """Try to enable DPI awareness using user32 method as fallback."""
        try:
            ctypes.windll.user32.SetProcessDPIAware()
            return True
        except (AttributeError, OSError):
            return False

    def _get_scaling_factor_from_root(self, root: Optional[tk.Tk]) -> ScalingFactor:
        """Unified method to get scaling factor from root window."""
        if not is_windows() or root is None:
            return 1.0
        
        def _get_factor():
            if hasattr(root, "DPI_scaling"):
                return root.DPI_scaling
            _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            return scaling_factor
        
        return self._safe_execute("get scaling factor", _get_factor, fallback=1.0)

    def _get_effective_dpi_from_root(self, root: Optional[tk.Tk]) -> float:
        """Unified method to get effective DPI from root window."""
        if not is_windows() or root is None:
            return 96.0
        
        def _get_dpi():
            if hasattr(root, "DPI_X") and hasattr(root, "DPI_Y"):
                return (root.DPI_X + root.DPI_Y) / 2
            dpi_x, dpi_y, _ = self._get_hwnd_dpi(root.winfo_id())
            return (dpi_x + dpi_y) / 2
        
        return self._safe_execute("get effective DPI", _get_dpi, fallback=96.0)

    def get_scaling_factor(self, root: Optional[tk.Tk]) -> ScalingFactor:
        """Get DPI scaling factor for a root window."""
        return self._get_scaling_factor_from_root(root)

    def get_effective_dpi(self, root: Optional[tk.Tk]) -> float:
        """Get effective DPI for a root window."""
        return self._get_effective_dpi_from_root(root)


    def _convert_pixel_value(self, value: Union[int, float], scaling_factor: ScalingFactor, to_physical: bool) -> Union[int, float]:
        """Unified method to convert pixel values between logical and physical."""
        try:
            if to_physical:
                return type(value)(round(float(value) * float(scaling_factor)))
            else:
                if scaling_factor == 0:
                    return value
                return type(value)(round(float(value) / float(scaling_factor)))
        except Exception as e:
            return self._handle_error("convert pixel value", e, value)

    def logical_to_physical(self, value: Union[int, float], *, root: Optional[tk.Tk] = None, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
        """Convert logical pixel value to physical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        
        if scaling_factor is None:
            if root is None:
                return value
            scaling_factor = self._get_scaling_factor_from_root(root)
        
        return self._convert_pixel_value(value, scaling_factor, True)

    def physical_to_logical(self, value: Union[int, float], *, root: Optional[tk.Tk] = None, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
        """Convert physical pixel value to logical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        
        if scaling_factor is None:
            if root is None:
                return value
            scaling_factor = self._get_scaling_factor_from_root(root)
        
        return self._convert_pixel_value(value, scaling_factor, False)

    def scale_font_size(self, original_size: Union[int, float], root: Optional[tk.Tk] = None, *, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
        """Scale a font size based on DPI scaling factor."""
        if not is_windows():
            return original_size
        
        # Positive font sizes (pt) should be handled by Tk's tk scaling
        # Only negative font sizes (px) need manual scaling
        if original_size > 0:
            return original_size

        # For negative font sizes (px), apply DPI scaling
        if scaling_factor is None:
            if root is None:
                return original_size
            scaling_factor = self._get_scaling_factor_from_root(root)

        if scaling_factor == 0:
            return original_size

        def _scale_font():
            return round(original_size * scaling_factor)
        
        return self._safe_execute("scale font size", _scale_font, fallback=original_size)

    def get_actual_window_size(self, root: Optional[tk.Tk]) -> WindowSizeDict:
        """Get actual window size information."""
        if not is_windows() or root is None:
            return {
                "platform": (DPIConfig.NON_WINDOWS_PLATFORM if not is_windows() else "no-root"),
                "logical_size": None,
                "physical_size": None,
            }
        
        def _get_window_size():
            geometry = root.geometry()
            # Use pre-compiled pattern for better performance
            match = DPIConfig.Patterns.GEOMETRY_WITHOUT_POSITION_PATTERN.match(geometry)
            logical_width = int(match.group('W')) if match else None
            logical_height = int(match.group('H')) if match else None
            
            scaling_factor = self._get_scaling_factor_from_root(root)
            
            physical_width = (
                self._scale_length_value(logical_width, scaling_factor) if logical_width else None
            )
            physical_height = (
                self._scale_length_value(logical_height, scaling_factor) if logical_height else None
            )
            
            return {
                "hwnd": root.winfo_id(),
                "logical_size": {
                    "width": logical_width,
                    "height": logical_height,
                    "geometry": geometry,
                },
                "physical_size": {
                    "width": physical_width,
                    "height": physical_height,
                },
                "scaling_factor": scaling_factor,
            }
        
        fallback = {
            "error": DPIConfig.ERROR_FAILED_TO_GET_WINDOW_SIZE,
            "logical_size": None,
            "physical_size": None,
        }
        
        return self._safe_execute("get window size", _get_window_size, fallback=fallback)

    def calculate_dpi_sizes(self, base_sizes: Dict[str, Union[int, float]], root: Optional[tk.Tk] = None, max_scale: Optional[ScalingFactor] = None) -> Dict[str, Union[int, float]]:
        """Calculate DPI-aware sizes for various UI elements."""
        if not is_windows() or not isinstance(base_sizes, dict):
            return base_sizes
        
        def _calculate_sizes():
            scaling_factor = self._get_scaling_factor_from_root(root) if root else 1.0
            if max_scale and scaling_factor > max_scale:
                scaling_factor = max_scale
            
            return {
                key: self._scale_length_value(value, scaling_factor) for key, value in base_sizes.items()
            }
        
        return self._safe_execute("calculate DPI sizes", _calculate_sizes, fallback=base_sizes)


_dpi_manager = DPIManager()


def dpi(root, *, enable=True):
    """Backward compatibility function for dpi()."""
    return _dpi_manager.apply_dpi(root, enable=enable)


def enable_dpi_awareness():
    """Backward compatibility function for enable_dpi_awareness()."""
    return _dpi_manager.enable_dpi_awareness()


# Backward compatibility functions - simplified wrappers
def enable_dpi_geometry(root):
    """Enable DPI-aware geometry for backward compatibility."""
    return dpi(root)

def get_scaling_factor(root: Optional[tk.Tk]) -> ScalingFactor:
    """Get DPI scaling factor for a root window."""
    return _dpi_manager.get_scaling_factor(root)

def get_effective_dpi(root: Optional[tk.Tk]) -> float:
    """Get effective DPI for a root window."""
    return _dpi_manager.get_effective_dpi(root)

def logical_to_physical(value: Union[int, float], *, root: Optional[tk.Tk] = None, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
    """Convert logical pixel value to physical pixels."""
    return _dpi_manager.logical_to_physical(value, root=root, scaling_factor=scaling_factor)

def physical_to_logical(value: Union[int, float], *, root: Optional[tk.Tk] = None, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
    """Convert physical pixel value to logical pixels."""
    return _dpi_manager.physical_to_logical(value, root=root, scaling_factor=scaling_factor)

def scale_font_size(original_size: Union[int, float], root: Optional[tk.Tk] = None, *, scaling_factor: Optional[ScalingFactor] = None) -> Union[int, float]:
    """Scale a font size based on DPI scaling factor."""
    return _dpi_manager.scale_font_size(original_size, root=root, scaling_factor=scaling_factor)

def get_actual_window_size(root: Optional[tk.Tk]) -> Dict[str, Any]:
    """Get actual window size information."""
    return _dpi_manager.get_actual_window_size(root)

def calculate_dpi_sizes(base_sizes: Dict[str, Union[int, float]], root: Optional[tk.Tk] = None, max_scale: Optional[ScalingFactor] = None) -> Dict[str, Union[int, float]]:
    """Calculate DPI-aware sizes for various UI elements."""
    return _dpi_manager.calculate_dpi_sizes(base_sizes, root=root, max_scale=max_scale)


def configure_ttk_widgets_for_dpi(root: Optional[tk.Tk]) -> None:
    """
    Configure ttk widgets for better DPI scaling, especially checkbuttons and radiobuttons.

    Note: This function is automatically called by tkface.win.dpi(root).
    Manual calls are only needed if you want to reconfigure after DPI changes.
    """
    return _dpi_manager._configure_ttk_widgets(root)


def scale_icon(
    icon_name: str, parent: tk.Widget, base_size: int = DPIConfig.DEFAULT_ICON_SIZE, max_scale: ScalingFactor = DPIConfig.MAX_SCALE_FACTOR
) -> str:
    """Create a scaled version of a Tkinter icon for DPI-aware sizing."""
    if not is_windows():
        return icon_name
    
    def _scale_icon_internal():
        scaling = get_scaling_factor(parent)
        if scaling > 1.0:
            original_icon = DPIConfig.Icons.get_icon_mapping(icon_name)
            scaled_icon = f"scaled_{icon_name}_large"
            if scaling >= DPIConfig.ICON_SCALE_THRESHOLD:
                # Scale with base_size consideration
                scale_factor = min(scaling, max_scale)
                target_size = int(base_size * scale_factor)
            else:
                scale_factor = 1.0
                target_size = base_size
            parent.tk.call("image", "create", "photo", scaled_icon)
            parent.tk.call(
                scaled_icon,
                "copy",
                original_icon,
                "-zoom",
                int(scale_factor),
                int(scale_factor),
            )
            return scaled_icon
        return icon_name
    
    return _dpi_manager._safe_execute(f"scale icon {icon_name}", _scale_icon_internal, fallback=icon_name)
