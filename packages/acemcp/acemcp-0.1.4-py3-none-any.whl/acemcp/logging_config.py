"""Global logging configuration for acemcp."""

from pathlib import Path

from loguru import logger

# Flag to track if logging has been configured
_logging_configured = False
# Store handler IDs to avoid removing them
_console_handler_id: int | None = None
_file_handler_id: int | None = None


def setup_logging() -> None:
    """Setup global logging configuration with file rotation.

    Configures loguru to write logs to ~/.acemcp/log/acemcp.log with:
    - Maximum file size: 5MB
    - Maximum number of files: 10 (rotation)
    - Log format with timestamp, level, and message

    This function can be called multiple times safely - it will only configure once.
    Note: This function preserves any existing handlers (e.g., WebSocket log broadcaster).
    """
    global _logging_configured, _console_handler_id, _file_handler_id  # noqa: PLW0603

    if _logging_configured:
        return

    # Define log directory and file
    log_dir = Path.home() / ".acemcp" / "log"
    log_file = log_dir / "acemcp.log"

    # Create log directory if it doesn't exist
    log_dir.mkdir(parents=True, exist_ok=True)

    # Remove only the default handler (handler_id=0) to avoid duplicate logs
    # This preserves any custom handlers like the WebSocket broadcaster
    try:
        logger.remove(0)
    except ValueError:
        # Handler 0 might already be removed, that's fine
        pass

    # Add console handler with INFO level
    _console_handler_id = logger.add(
        sink=lambda msg: print(msg, end=""),
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # Add file handler with rotation
    _file_handler_id = logger.add(
        sink=str(log_file),
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="5 MB",  # Rotate when file reaches 5MB
        retention=10,      # Keep at most 10 files
        compression="zip", # Compress rotated files
        encoding="utf-8",
        enqueue=True,      # Thread-safe logging
    )

    _logging_configured = True
    logger.info(f"Logging configured: log file at {log_file}")

