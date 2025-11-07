__all__ = ["FileServiceConfig", "FileHandler"]

import csv
import json
import os
from dataclasses import dataclass
from typing import List, Literal

from dc_logger.client.base import LogEntry, ServiceConfig, ServiceHandler
from dc_logger.client.exceptions import LogConfigError, LogHandlerError, LogWriteError


@dataclass
class FileServiceConfig(ServiceConfig):
    """Configuration for file-based logging output"""

    destination: str = ""  # Will be validated in validate_config
    output_mode: Literal["file"] = "file"
    format: Literal["json", "text", "csv"] = "text"
    append: bool = True  # optional flag for overwrite or append

    def validate_config(self) -> bool:
        if not self.destination:
            raise LogConfigError("File destination must be provided.")
        if self.format not in ("json", "text", "csv"):
            raise LogConfigError(f"Unsupported file format: {self.format}")
        return True


@dataclass
class FileHandler(ServiceHandler):
    """Handler for file output"""

    def __post_init__(self) -> None:
        """Initialize file handler after dataclass initialization"""
        if not self.service_config:
            raise LogHandlerError("Service config is required for FileHandler")
        if not isinstance(self.service_config, FileServiceConfig):
            raise LogHandlerError("FileHandler requires FileServiceConfig")
        self.service_config.validate_config()
        self.file_path = self.service_config.destination
        self.append_mode = "a" if self.service_config.append else "w"
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """Create parent directories in case they don't exist."""
        file_dir = os.path.dirname(self.file_path)
        if not file_dir:
            return
        try:
            os.makedirs(file_dir, exist_ok=True)
        except PermissionError as e:
            raise LogHandlerError(
                f"Permissions denied creating directory {file_dir}: {e}"
            ) from e
        except OSError as e:
            raise LogHandlerError(
                f"OS error creating the directory {file_dir}: {e}"
            ) from e

    async def _write_json(self, entry: LogEntry) -> bool:
        """Write log entry to JSON file, maintaining proper JSON array format."""
        try:
            # Check if file exists and has content
            file_exists = os.path.exists(self.file_path)
            file_has_content = False

            if file_exists:
                try:
                    with open(self.file_path, encoding="utf-8") as f:
                        content = f.read().strip()
                        file_has_content = len(content) > 0
                except Exception:
                    file_has_content = False

            # Read existing logs if file exists and has content
            existing_logs = []
            if file_exists and file_has_content:
                try:
                    with open(self.file_path, encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            existing_logs = json.loads(content)
                            if not isinstance(existing_logs, list):
                                existing_logs = []
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_logs = []

            # Add new entry
            existing_logs.append(entry.to_dict())

            # Write back to file
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(existing_logs, f, indent=2, ensure_ascii=False, default=str)

            return True
        except Exception as e:
            raise LogWriteError(
                f"Error writing JSON to file {self.file_path}: {e}"
            ) from e

    async def _write_text(self, entry: LogEntry) -> bool:
        try:
            # Get all fields from the entry
            entry_dict = entry.to_dict()

            # Build the main log line
            level = entry.level.value if hasattr(entry.level, "value") else entry.level
            line = f"[{entry.timestamp}] {level} - {entry.message}"

            # Collect metadata (all fields except timestamp, level, and message)
            metadata_parts = []
            for key, value in entry_dict.items():
                if key not in ["timestamp", "level", "message"]:
                    if isinstance(value, dict):
                        # Format nested dicts
                        nested_parts = [
                            f"{key}.{k}={v}" for k, v in value.items() if v is not None
                        ]
                        metadata_parts.extend(nested_parts)
                    elif value is not None:
                        metadata_parts.append(f"{key}={value}")

            # Add metadata if present
            if metadata_parts:
                line += " | " + ", ".join(metadata_parts)

            line += "\n"

            with open(self.file_path, self.append_mode, encoding="utf-8") as f:
                f.write(line)
            return True
        except Exception as e:
            raise LogWriteError(
                f"Error writing text to file {self.file_path}: {e}"
            ) from e

    def _flatten_dict(self, d: dict, parent_key: str = "", sep: str = ".") -> dict:
        """Flatten nested dictionaries into dot notation"""
        items: List[tuple] = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and v:
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    async def _write_csv(self, entry: LogEntry) -> bool:
        try:
            file_exists = os.path.exists(self.file_path)
            entry_dict = entry.to_dict()

            # Flatten the entry dictionary to handle nested objects
            flattened_entry = self._flatten_dict(entry_dict)

            # Get existing fieldnames if file exists
            existing_fieldnames: List[str] = []
            if file_exists and os.path.getsize(self.file_path) > 0:
                with open(self.file_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    existing_fieldnames = (
                        list(reader.fieldnames) if reader.fieldnames else []
                    )

            # Merge existing fieldnames with new ones, preserving order
            # Priority order: timestamp, level, app_name, message first
            priority_fields = ["timestamp", "level", "app_name", "message"]
            new_fields = set(flattened_entry.keys())

            # Start with priority fields that exist
            fieldnames = [f for f in priority_fields if f in new_fields]

            # Add existing fields that aren't priority fields
            for field in existing_fieldnames:
                if field not in fieldnames:
                    fieldnames.append(field)

            # Add new fields that aren't already in the list
            for field in sorted(new_fields - set(fieldnames)):
                fieldnames.append(field)

            # Determine if we need to rewrite the file (new columns added)
            needs_rewrite = file_exists and set(fieldnames) != set(existing_fieldnames)

            if needs_rewrite:
                # Read existing data
                existing_data = []
                with open(self.file_path, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    existing_data = list(reader)

                # Rewrite file with new headers
                with open(self.file_path, "w", newline="", encoding="utf-8") as f:  # type: ignore
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for row in existing_data:
                        writer.writerow(row)
                    writer.writerow(flattened_entry)
            else:
                # Normal append or new file
                with open(
                    self.file_path, self.append_mode, newline="", encoding="utf-8"
                ) as f:  # type: ignore
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    if not file_exists or os.path.getsize(self.file_path) == 0:
                        writer.writeheader()
                    writer.writerow(flattened_entry)

            return True
        except Exception as e:
            raise LogWriteError(
                f"Error writing CSV to file {self.file_path}: {e}"
            ) from e

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write log entries to the file"""
        if not isinstance(entries, list):
            entries = [entries]

        try:
            if not self.service_config:
                raise LogHandlerError("Service config is required for FileHandler")
            if not isinstance(self.service_config, FileServiceConfig):
                raise LogHandlerError("FileHandler requires FileServiceConfig")
            output_format = self.service_config.format

            for entry in entries:
                if output_format == "json":
                    await self._write_json(entry)
                elif output_format == "csv":
                    await self._write_csv(entry)
                elif output_format == "text":
                    await self._write_text(entry)
                else:
                    raise LogConfigError(f"Unsupported output format: {output_format}")

            return True

        except Exception as e:
            raise LogWriteError(f"Error writing to file {self.file_path}: {e}") from e

    async def flush(self) -> bool:
        """File writes are immediate; no flush needed"""
        return True
