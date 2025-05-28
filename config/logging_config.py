#config/logging_config.py
"""
Logging configuration for the Agentic AI Workflow.
Provides structured logging with file rotation and different log levels.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Dict, Optional

from config.settings import get_settings

settings = get_settings()


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        log_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset_color = self.COLORS['RESET']
        
        # Add color to level name
        record.levelname = f"{log_color}{record.levelname}{reset_color}"
        
        return super().format(record)


class StructuredFormatter(logging.Formatter):
    """Structured formatter for file logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        # Add extra context
        if hasattr(record, 'agent_type'):
            record.context = f"[{record.agent_type}]"
        elif hasattr(record, 'workflow_id'):
            record.context = f"[Workflow:{record.workflow_id}]"
        else:
            record.context = ""
        
        return super().format(record)


def setup_logging() -> None:
    """
    Set up comprehensive logging configuration.
    Creates console and file handlers with appropriate formatters.
    """
    # Create logs directory
    logs_dir = settings.logs_dir
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Application log file handler with rotation
    app_log_file = logs_dir / "application.log"
    app_handler = logging.handlers.RotatingFileHandler(
        app_log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    app_handler.setLevel(getattr(logging, settings.log_level))
    app_formatter = StructuredFormatter(
        fmt='%(asctime)s | %(levelname)s | %(name)s %(context)s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    app_handler.setFormatter(app_formatter)
    root_logger.addHandler(app_handler)
    
    # Workflow-specific log file
    workflow_log_file = logs_dir / "workflow.log"
    workflow_handler = logging.handlers.RotatingFileHandler(
        workflow_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    workflow_handler.setLevel(logging.INFO)
    workflow_handler.addFilter(WorkflowLogFilter())
    workflow_handler.setFormatter(app_formatter)
    root_logger.addHandler(workflow_handler)
    
    # Error log file for errors only
    error_log_file = logs_dir / "error.log"
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(app_formatter)
    root_logger.addHandler(error_handler)
    
    # Configure third-party loggers
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)


class WorkflowLogFilter(logging.Filter):
    """Filter to only include workflow-related log messages."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter workflow-related messages."""
        workflow_loggers = [
            'src.workflow',
            'src.agents',
            'src.integrations'
        ]
        return any(record.name.startswith(logger) for logger in workflow_loggers)


def get_logger(name: str, **context) -> logging.Logger:
    """
    Get a logger with optional context.
    
    Args:
        name: Logger name (usually __name__)
        **context: Additional context to include in logs
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Add context to logger
    if context:
        logger = logging.LoggerAdapter(logger, context)
    
    return logger


def log_function_call(func):
    """Decorator to log function calls with parameters and results."""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {e}")
            raise
    
    return wrapper


def log_agent_activity(agent_type: str, activity: str, **details):
    """Log agent-specific activities."""
    logger = get_logger('src.agents', agent_type=agent_type)
    
    detail_str = " | ".join([f"{k}={v}" for k, v in details.items()])
    message = f"{activity}"
    if detail_str:
        message += f" | {detail_str}"
    
    logger.info(message)


def log_workflow_state(workflow_id: str, state: str, **details):
    """Log workflow state changes."""
    logger = get_logger('src.workflow', workflow_id=workflow_id)
    
    detail_str = " | ".join([f"{k}={v}" for k, v in details.items()])
    message = f"State: {state}"
    if detail_str:
        message += f" | {detail_str}"
    
    logger.info(message)


# Initialize logging when module is imported
setup_logging()
