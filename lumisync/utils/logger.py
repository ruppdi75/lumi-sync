"""
Logging Configuration and Utilities
Centralized logging setup for LumiSync
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional
import sys

from ..config.settings import LOGGING_CONFIG, LOG_FILE


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = (
                f"{self.COLORS[record.levelname]}{record.levelname}"
                f"{self.COLORS['RESET']}"
            )
        
        return super().format(record)


def setup_logging(log_level: str = 'INFO', console_output: bool = True) -> logging.Logger:
    """
    Set up logging configuration for LumiSync.
    
    Args:
        log_level: Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        console_output: Whether to output logs to console
        
    Returns:
        Configured logger instance
    """
    # Ensure log directory exists
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Create a copy of the logging config
    config = LOGGING_CONFIG.copy()
    
    # Update file handler path
    config['handlers']['file']['filename'] = str(LOG_FILE)
    config['handlers']['file']['level'] = log_level
    
    # Configure console handler
    if console_output:
        config['handlers']['console']['level'] = log_level
        # Use colored formatter for console
        config['formatters']['colored'] = {
            '()': ColoredFormatter,
            'format': '%(levelname)s: %(message)s'
        }
        config['handlers']['console']['formatter'] = 'colored'
    else:
        # Remove console handler if not needed
        config['handlers'].pop('console', None)
        config['loggers']['lumisync']['handlers'] = ['file']
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Get the main logger
    logger = logging.getLogger('lumisync')
    logger.info(f"Logging initialized - Level: {log_level}, Console: {console_output}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the logger (usually __name__)
        
    Returns:
        Logger instance
    """
    # Ensure the name is under the lumisync hierarchy
    if not name.startswith('lumisync'):
        name = f'lumisync.{name}'
    
    return logging.getLogger(name)


class LogCapture:
    """Context manager to capture log messages for testing or display."""
    
    def __init__(self, logger_name: str = 'lumisync', level: int = logging.INFO):
        self.logger_name = logger_name
        self.level = level
        self.handler = None
        self.messages = []
    
    def __enter__(self):
        # Create a custom handler that captures messages
        self.handler = logging.Handler()
        self.handler.setLevel(self.level)
        
        # Custom emit method to capture messages
        def capture_emit(record):
            self.messages.append(self.handler.format(record))
        
        self.handler.emit = capture_emit
        
        # Add handler to logger
        logger = logging.getLogger(self.logger_name)
        logger.addHandler(self.handler)
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.handler:
            logger = logging.getLogger(self.logger_name)
            logger.removeHandler(self.handler)
    
    def get_messages(self) -> list:
        """Get captured log messages."""
        return self.messages.copy()
    
    def clear(self):
        """Clear captured messages."""
        self.messages.clear()


def log_function_call(func):
    """
    Decorator to log function calls with arguments and return values.
    Useful for debugging.
    """
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function entry
        args_str = ', '.join([str(arg) for arg in args])
        kwargs_str = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
        all_args = ', '.join(filter(None, [args_str, kwargs_str]))
        
        logger.debug(f"Calling {func.__name__}({all_args})")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} returned: {result}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} raised {type(e).__name__}: {e}")
            raise
    
    return wrapper


def log_performance(func):
    """
    Decorator to log function execution time.
    """
    import time
    
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper


def setup_exception_logging():
    """Set up global exception logging."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            # Don't log keyboard interrupts
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = get_logger('lumisync.exceptions')
        logger.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
    
    sys.excepthook = handle_exception


def create_progress_logger(name: str, total_steps: int) -> 'ProgressLogger':
    """
    Create a progress logger for long-running operations.
    
    Args:
        name: Name of the operation
        total_steps: Total number of steps
        
    Returns:
        ProgressLogger instance
    """
    return ProgressLogger(name, total_steps)


class ProgressLogger:
    """Logger for tracking progress of long-running operations."""
    
    def __init__(self, operation_name: str, total_steps: int):
        self.operation_name = operation_name
        self.total_steps = total_steps
        self.current_step = 0
        self.logger = get_logger('lumisync.progress')
        
        self.logger.info(f"Starting {operation_name} ({total_steps} steps)")
    
    def step(self, message: str = ""):
        """Advance to the next step."""
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        
        progress_msg = f"{self.operation_name}: Step {self.current_step}/{self.total_steps} ({percentage:.1f}%)"
        if message:
            progress_msg += f" - {message}"
        
        self.logger.info(progress_msg)
    
    def complete(self, message: str = ""):
        """Mark the operation as complete."""
        complete_msg = f"{self.operation_name} completed"
        if message:
            complete_msg += f" - {message}"
        
        self.logger.info(complete_msg)
    
    def error(self, message: str):
        """Log an error during the operation."""
        self.logger.error(f"{self.operation_name} failed at step {self.current_step}: {message}")


# Initialize logging when module is imported
_logger_initialized = False

def ensure_logging_initialized():
    """Ensure logging is initialized (called automatically)."""
    global _logger_initialized
    if not _logger_initialized:
        setup_logging()
        setup_exception_logging()
        _logger_initialized = True

# Auto-initialize logging
ensure_logging_initialized()
