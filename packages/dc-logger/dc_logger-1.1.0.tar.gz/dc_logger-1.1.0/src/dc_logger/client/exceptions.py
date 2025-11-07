# Logging-specific exceptions
class LoggingError(Exception):
    """Base exception for logging errors"""


class LogHandlerError(LoggingError):
    """Exception for log handler errors"""


class LogConfigError(LoggingError):
    """Exception for log configuration errors"""


class LogWriteError(LoggingError):
    """Exception for log write errors"""


class LogFlushError(LoggingError):
    """Exception for log flush errors"""
