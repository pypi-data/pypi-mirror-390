"""
Centralized logging configuration for CLI.

Provides consistent logging setup across all CLI modules.
"""

import logging
import sys
import atexit
import threading
from pathlib import Path
from typing import Optional, List
from rich.logging import RichHandler

# Lazy import to prevent circular dependency
_config_module = None
_config_lock = threading.Lock()


def _get_config():
    """Lazy import of config module to prevent circular imports (thread-safe)."""
    global _config_module
    if _config_module is None:
        with _config_lock:
            if _config_module is None:
                from cli import config as _config_module
    return _config_module.get_config()


# Track file handlers for cleanup (thread-safe)
_file_handlers: List[logging.FileHandler] = []
_handlers_lock = threading.Lock()


def _cleanup_handlers():
    """Clean up file handlers on exit (thread-safe)."""
    with _handlers_lock:
        for handler in _file_handlers[:]:  # Copy list to avoid modification during iteration
            try:
                handler.close()
            except Exception:
                pass
        _file_handlers.clear()


# Register cleanup on exit
atexit.register(_cleanup_handlers)


def setup_cli_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    use_rich: bool = True
) -> logging.Logger:
    """
    Set up logging for CLI application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        use_rich: Use Rich handler for beautiful console output
    
    Returns:
        Configured root logger
    """
    try:
        config = _get_config()
    except Exception as e:
        # If config can't be loaded, log warning and use defaults
        import sys
        print(f"Warning: Could not load configuration: {e}", file=sys.stderr)
        config = None
    
    # Use provided log_level or from config
    if log_level:
        level_str = log_level.upper()
    elif config:
        level_str = config.log_level.upper()
    else:
        level_str = "INFO"
    
    level = getattr(logging, level_str, logging.INFO)
    
    # Use provided log_file or from config
    if log_file:
        log_file_path = log_file
    elif config and config.log_file:
        log_file_path = config.log_file
    else:
        log_file_path = None
    
    # Create logs directory if file logging is enabled
    if log_file_path:
        try:
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
        except (OSError, ValueError):
            log_file_path = None
    
    # Configure root logger (thread-safe)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates (thread-safe)
    with _handlers_lock:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
            # Close file handlers
            if isinstance(handler, logging.FileHandler):
                try:
                    handler.close()
                except Exception:
                    pass
                # Remove from tracking list
                if handler in _file_handlers:
                    _file_handlers.remove(handler)
    
    # Console handler
    if use_rich:
        # Use Rich handler for beautiful console output
        console_handler = RichHandler(
            rich_tracebacks=True,
            show_path=True,
            show_time=True,
            console=None,  # Use default console
            level=level
        )
        console_handler.setFormatter(logging.Formatter("%(message)s", datefmt="[%X]"))
    else:
        # Standard console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
    
    root_logger.addHandler(console_handler)
    
    # File handler (if log file is specified) - thread-safe
    if log_file_path:
        try:
            file_handler = logging.FileHandler(
                str(log_file_path),
                encoding='utf-8',
                mode='a'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(
                logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
            )
            root_logger.addHandler(file_handler)
            # Track for cleanup (thread-safe)
            with _handlers_lock:
                _file_handlers.append(file_handler)
        except (OSError, PermissionError) as e:
            # If we can't write to log file, just log to console
            root_logger.warning(f"Could not set up file logging: {e}")
    
    # Suppress noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


# Thread-safe setup tracking
_setup_lock = threading.RLock()  # Use RLock for reentrant locking
_setup_done = False


def ensure_logging_setup():
    """Ensure logging is set up (idempotent and thread-safe with atomic operations)."""
    global _setup_done
    if not _setup_done:
        with _setup_lock:
            if not _setup_done:
                try:
                    setup_cli_logging()
                    _setup_done = True
                except Exception as e:
                    import sys
                    print(f"Warning: Logging setup failed: {e}", file=sys.stderr)
                    # Don't set _setup_done to allow retry
