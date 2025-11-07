import json
from typing import List

from ..client.enums import LogLevel
from ..client.models import LogEntry
from ..color_utils import colorize
from .base import LogHandler

# Default color mapping for log levels
DEFAULT_LOG_COLORS = {
    LogLevel.DEBUG: "green",
    LogLevel.INFO: "green",
    LogLevel.WARNING: "yellow",
    LogLevel.ERROR: "red",
    LogLevel.CRITICAL: "red",
}


class ConsoleHandler(LogHandler):
    """Handler for console output"""

    def _get_color_for_entry(self, entry: LogEntry) -> str:
        """Get the color for a log entry, using default if not specified"""
        # If color is explicitly set, use it
        if entry.color:
            return entry.color

        # Otherwise, use default color based on log level
        return DEFAULT_LOG_COLORS.get(entry.level, "green")

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to console"""
        try:
            for entry in entries:
                # Get the color to use (explicit or default)
                color = self._get_color_for_entry(entry)

                if self.config.format == "json":
                    if self.config.pretty_print:
                        # Pretty print JSON for development
                        json_output = json.dumps(entry.to_dict(), indent=2, default=str)
                        # Apply color to the entire JSON output
                        json_output = colorize(json_output, color)
                        print(json_output)
                        print("-" * 80)  # Separator for readability
                    else:
                        json_output = entry.to_json()
                        # Apply color to the entire JSON output
                        json_output = colorize(json_output, color)
                        print(json_output)
                else:
                    # Text format
                    log_line = f"[{entry.timestamp}] {entry.level.value} {entry.app_name}: {entry.message}"
                    # Apply color to the entire log line
                    log_line = colorize(log_line, color)
                    print(log_line)
            return True
        except Exception as e:
            print(f"Error writing to console: {e}")
            return False

    async def flush(self) -> bool:
        """Console output doesn't need flushing"""
        return True
