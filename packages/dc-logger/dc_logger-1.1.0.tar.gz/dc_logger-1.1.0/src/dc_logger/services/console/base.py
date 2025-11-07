__all__ = ["ConsoleServiceConfig", "ConsoleHandler"]

import json
from dataclasses import dataclass
from typing import List

from dc_logger.client.base import LogEntry, OutputMode, ServiceConfig, ServiceHandler


@dataclass
class ConsoleServiceConfig(ServiceConfig):
    """Console-specific log configuration"""

    output_mode: OutputMode = "console"
    output_type: str = "text"  # "text" or "json"

    def validate_config(self) -> bool:
        if self.output_type not in ["text", "json"]:
            raise ValueError(
                f"output_type must be 'text' or 'json', got {self.output_type}"
            )
        return True


class ConsoleHandler(ServiceHandler):
    """Handler for console output"""

    async def _write_json(self, entry: LogEntry) -> str:
        """Write log entry as properly formatted JSON."""
        try:
            # Get the dictionary representation
            log_dict = entry.to_dict()

            # Ensure proper JSON serialization with consistent formatting
            message = json.dumps(log_dict, indent=2, default=str, ensure_ascii=False)
            print(message)
            return message
        except Exception as e:
            # Fallback to basic JSON if serialization fails
            fallback_dict = {
                "timestamp": entry.timestamp,
                "level": entry.level.value,
                "message": entry.message,
                "error": f"JSON serialization failed: {str(e)}",
            }
            message = json.dumps(fallback_dict, indent=2, default=str)
            print(message)
            return message

    async def _write_text(self, entry: LogEntry) -> str:
        """Write log entry as formatted text."""
        # Create a clean text format
        timestamp = entry.timestamp
        level = entry.level.value
        message = entry.message

        # Build the basic log line
        log_line = f"[{timestamp}] {level} - {message}"

        # Add context information if present
        context_parts = []

        if entry.user:
            context_parts.append(f"user={entry.user}")

        if entry.action:
            context_parts.append(f"action={entry.action}")

        if entry.entity:
            entity_info = (
                f"entity={entry.entity.type}:{entry.entity.id}"
                if entry.entity.type and entry.entity.id
                else f"entity={entry.entity.name or 'unknown'}"
            )
            context_parts.append(entity_info)

        if entry.status and entry.status != "info":
            context_parts.append(f"status={entry.status}")

        if entry.duration_ms:
            context_parts.append(f"duration={entry.duration_ms}ms")

        # Add context if we have any
        if context_parts:
            log_line += f" ({', '.join(context_parts)})"

        print(log_line)
        return log_line

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to console"""
        if not isinstance(entries, list):
            entries = [entries]

        # Get output type from config
        output_type = "text"  # default
        if self.service_config and hasattr(self.service_config, "output_type"):
            output_type = self.service_config.output_type

        try:
            for entry in entries:
                if output_type == "json":
                    await self._write_json(entry)
                else:
                    await self._write_text(entry)
            return True

        except Exception as e:
            print(f"Error writing to console: {e}")
            return False

    async def flush(self) -> bool:
        """Console output doesn't need flushing"""
        return True
