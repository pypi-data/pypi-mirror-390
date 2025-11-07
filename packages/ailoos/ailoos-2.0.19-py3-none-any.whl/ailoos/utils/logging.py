"""
Logging utilities for Ailoos library.
Provides structured logging for development and debugging.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logging for Ailoos.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        format_string: Custom format string

    Returns:
        Configured logger instance

    Example:
        logger = setup_logging(level="DEBUG", log_file="ailoos.log")
        logger.info("Ailoos initialized")
    """
    # Convert string level to logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Default format with more context for debugging
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    # Configure formatter
    formatter = logging.Formatter(format_string)

    # Setup root logger
    logger = logging.getLogger("ailoos")
    logger.setLevel(numeric_level)

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent duplicate messages from parent loggers
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Module name (e.g., "ailoos.core.node")

    Returns:
        Logger instance

    Example:
        logger = get_logger(__name__)
        logger.debug("Debug message")
    """
    return logging.getLogger(f"ailoos.{name}")


class AiloosLogger:
    """
    Enhanced logger with Ailoos-specific features.
    """

    def __init__(self, name: str = "ailoos", level: str = "INFO"):
        self.logger = get_logger(name)
        # Set up logging if not already done
        setup_logging(level=level)

    def log_training_progress(
        self,
        round_num: int,
        accuracy: float,
        loss: float,
        node_id: Optional[str] = None
    ):
        """Log federated training progress."""
        extra = f" [Node: {node_id}]" if node_id else ""
        self.logger.info(
            f"Training Round {round_num}: Accuracy={accuracy:.2f}%, Loss={loss:.4f}{extra}"
        )

    def log_node_status(self, node_id: str, status: str, details: Optional[dict] = None):
        """Log node status changes."""
        details_str = f" - {details}" if details else ""
        self.logger.info(f"Node {node_id}: {status}{details_str}")

    def log_model_operation(self, operation: str, model_name: str, success: bool):
        """Log model operations."""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Model {operation}: {model_name} - {status}")

    def log_network_error(self, operation: str, error: str, node_id: Optional[str] = None):
        """Log network-related errors."""
        node_info = f" [Node: {node_id}]" if node_id else ""
        self.logger.error(f"Network {operation} failed{node_info}: {error}")

    def log_performance_metric(self, metric: str, value: float, unit: str = ""):
        """Log performance metrics."""
        unit_str = f" {unit}" if unit else ""
        self.logger.info(f"Performance - {metric}: {value:.2f}{unit_str}")

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)


# Global logger instance
_default_logger = None


def get_default_logger() -> AiloosLogger:
    """Get the default Ailoos logger instance."""
    global _default_logger
    if _default_logger is None:
        _default_logger = AiloosLogger()
    return _default_logger