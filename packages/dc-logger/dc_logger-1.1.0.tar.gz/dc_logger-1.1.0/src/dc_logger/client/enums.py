from enum import Enum


class LogLevel(str, Enum):
    """Standard logging levels"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_string(cls, level_str: str) -> "LogLevel":
        """Convert string to LogLevel enum"""
        try:
            return cls(level_str.upper())
        except ValueError:
            return cls.INFO  # default fallback

    def should_log(self, other: "LogLevel") -> bool:
        """Check if this level should log the other level"""
        levels = list(LogLevel)
        return levels.index(self) <= levels.index(other)
