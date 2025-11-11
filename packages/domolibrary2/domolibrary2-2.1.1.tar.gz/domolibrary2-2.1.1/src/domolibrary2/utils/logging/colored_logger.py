"""
Colored logger wrapper that automatically applies colors to log levels.

This module provides a ColoredLogger class that wraps dc_logger and automatically
applies appropriate colors to different log levels for better visual distinction
in console output.
"""

from typing import Any, Optional

from dc_logger.client.base import Logger, get_global_logger, set_global_logger
from dc_logger.color_utils import colorize


class ColoredLogger(Logger):
    """
    Logger that automatically colorizes messages by log level.

    Default colors:
        - DEBUG: cyan
        - INFO: green
        - WARNING: yellow
        - ERROR: red
        - CRITICAL: bold_red

    Example:
        >>> from domolibrary2.utils.logging import get_colored_logger
        >>> logger = get_colored_logger()
        >>> await logger.info("This will be green")
        >>> await logger.warning("This will be yellow")
        >>> await logger.error("This will be red")
    """

    # Log level hierarchy
    _LEVEL_HIERARCHY = {
        "DEBUG": 10,
        "INFO": 20,
        "WARNING": 30,
        "ERROR": 40,
        "CRITICAL": 50,
    }

    def __init__(
        self,
        base_logger: Logger,
        debug_color: str = "cyan",
        info_color: str = "green",
        warning_color: str = "yellow",
        error_color: str = "bold_red",
        critical_color: str = "bold_red",
        min_level: str = "INFO",
    ):
        """
        Initialize colored logger wrapper.

        Args:
            base_logger: The underlying dc_logger Logger instance
            debug_color: Color for debug messages (default: cyan)
            info_color: Color for info messages (default: green)
            warning_color: Color for warning messages (default: yellow)
            error_color: Color for error messages (default: bold_red)
            critical_color: Color for critical messages (default: bold_red)
            min_level: Minimum log level to display (default: INFO)
        """
        # Don't call super().__init__() - we're wrapping, not inheriting data
        self._logger = base_logger
        self.debug_color = debug_color
        self.info_color = info_color
        self.warning_color = warning_color
        self.error_color = error_color
        self.critical_color = critical_color
        self._min_level = self._LEVEL_HIERARCHY[min_level.upper()]

    def _should_log(self, level: str) -> bool:
        """Check if a message at the given level should be logged."""
        return self._LEVEL_HIERARCHY.get(level.upper(), 0) >= self._min_level

    async def debug(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        color: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log DEBUG level message with automatic coloring."""
        if not self._should_log("DEBUG"):
            return False
        colored_msg = colorize(message, color or self.debug_color)
        return await self._logger.debug(
            colored_msg, method=method, level_name=level_name, **context
        )

    async def info(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        color: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log INFO level message with automatic coloring."""
        if not self._should_log("INFO"):
            return False
        colored_msg = colorize(message, color or self.info_color)
        return await self._logger.info(
            colored_msg, method=method, level_name=level_name, **context
        )

    async def warning(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        color: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log WARNING level message with automatic coloring."""
        if not self._should_log("WARNING"):
            return False
        colored_msg = colorize(message, color or self.warning_color)
        return await self._logger.warning(
            colored_msg, method=method, level_name=level_name, **context
        )

    async def error(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        color: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log ERROR level message with automatic coloring."""
        if not self._should_log("ERROR"):
            return False
        colored_msg = colorize(message, color or self.error_color)
        return await self._logger.error(
            colored_msg, method=method, level_name=level_name, **context
        )

    async def critical(
        self,
        message: str,
        method: str = "COMMENT",
        level_name: Optional[str] = None,
        color: Optional[str] = None,
        **context: Any,
    ) -> bool:
        """Log CRITICAL level message with automatic coloring."""
        if not self._should_log("CRITICAL"):
            return False
        colored_msg = colorize(message, color or self.critical_color)
        return await self._logger.critical(
            colored_msg, method=method, level_name=level_name, **context
        )

    # Delegate all other methods to the underlying logger
    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying logger."""
        return getattr(self._logger, name)

    def set_level(self, level: str):
        """
        Set the minimum log level for this logger.

        Args:
            level: Log level name - 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

        Example:
            >>> logger = get_colored_logger()
            >>> logger.set_level('WARNING')  # Only show WARNING and above
            >>> logger.set_level('ERROR')    # Only show ERROR and CRITICAL
            >>> logger.set_level('INFO')     # Show INFO and above (default)
        """
        level_upper = level.upper()
        if level_upper not in self._LEVEL_HIERARCHY:
            valid_levels = ", ".join(self._LEVEL_HIERARCHY.keys())
            raise ValueError(
                f"Invalid log level '{level}'. Valid levels: {valid_levels}"
            )

        self._min_level = self._LEVEL_HIERARCHY[level_upper]
        return self

    def get_level(self) -> str:
        """
        Get the current minimum log level.

        Returns:
            Current log level name (e.g., 'INFO', 'WARNING', 'ERROR')

        Example:
            >>> logger = get_colored_logger()
            >>> logger.get_level()
            'INFO'
        """
        for name, value in self._LEVEL_HIERARCHY.items():
            if value == self._min_level:
                return name
        return "INFO"  # Default


# Global colored logger instance
_colored_logger = None
_user_has_set_global_logger = False


def get_colored_logger(
    debug_color: str = "cyan",
    info_color: str = "green",
    warning_color: str = "yellow",
    error_color: str = "bold_red",
    critical_color: str = "bold_red",
    set_as_global: bool = True,
    force: bool = False,
) -> ColoredLogger:
    """
    Get or create a colored logger instance.

    IMPORTANT: By default, this does NOT override the global logger to respect
    user configuration. If you want to set it as global, explicitly pass
    set_as_global=True or use set_domolibrary_logger().

    Args:
        debug_color: Color for debug messages (default: cyan)
        info_color: Color for info messages (default: green)
        warning_color: Color for warning messages (default: yellow)
        error_color: Color for error messages (default: bold_red)
        critical_color: Color for critical messages (default: bold_red)
        set_as_global: Set this as dc_logger's global logger (default: False)
        force: Force setting as global even if user has configured logger (default: False)

    Returns:
        ColoredLogger instance with automatic color application

    Example:
        >>> # Get colored logger without affecting global logger
        >>> logger = get_colored_logger()
        >>> await logger.info("Success!")  # Will be green
        >>>
        >>> # Set as global logger for domolibrary
        >>> logger = get_colored_logger(set_as_global=True)
        >>> # Now all @log_call decorators will use colored output
    """
    global _colored_logger, _user_has_set_global_logger

    # Check if user has already configured a custom global logger
    current_global = get_global_logger()

    # If this is the first call and a non-default logger exists, mark it as user-configured
    if _colored_logger is None and not isinstance(current_global, ColoredLogger):
        # Check if the global logger has been customized (not the default dc_logger instance)
        # by checking if it has custom attributes or configurations
        _user_has_set_global_logger = True

    if _colored_logger is None:
        base_logger = current_global
        _colored_logger = ColoredLogger(
            base_logger=base_logger,
            debug_color=debug_color,
            info_color=info_color,
            warning_color=warning_color,
            error_color=error_color,
            critical_color=critical_color,
        )

        # Only set as global if explicitly requested and (not user-configured OR forced)
        if set_as_global and (not _user_has_set_global_logger or force):
            set_global_logger(_colored_logger)

    return _colored_logger


def set_domolibrary_logger(
    logger: ColoredLogger | None = None,
    set_as_global: bool = True,
    **kwargs,
) -> ColoredLogger:
    """
    Explicitly set the domolibrary logger, optionally making it the global logger.

    This is the recommended way to configure logging for domolibrary if you want
    colored output throughout the library.

    Args:
        logger: Existing ColoredLogger instance, or None to create a new one
        set_as_global: Set this as dc_logger's global logger (default: True)
        **kwargs: Arguments to pass to get_colored_logger if creating a new instance

    Returns:
        The ColoredLogger instance

    Example:
        >>> # Option 1: Use default colored logger
        >>> from domolibrary2.utils.logging import set_domolibrary_logger
        >>> logger = set_domolibrary_logger()
        >>>
        >>> # Option 2: Create with custom colors
        >>> logger = set_domolibrary_logger(
        ...     info_color="blue",
        ...     error_color="magenta"
        ... )
        >>>
        >>> # Option 3: Use your own ColoredLogger
        >>> my_logger = ColoredLogger(base_logger=my_base_logger)
        >>> set_domolibrary_logger(logger=my_logger)
    """
    global _colored_logger, _user_has_set_global_logger

    if logger is None:
        logger = get_colored_logger(set_as_global=True, **kwargs)

    _colored_logger = logger
    _user_has_set_global_logger = True

    if set_as_global:
        set_global_logger(logger)

    return logger
