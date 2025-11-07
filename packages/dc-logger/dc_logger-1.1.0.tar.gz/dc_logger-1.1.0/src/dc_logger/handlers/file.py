import os
from typing import Any, List

from ..client.exceptions import LogConfigError, LogHandlerError, LogWriteError
from ..client.models import LogEntry
from .base import LogHandler


class FileHandler(LogHandler):
    """Handler for file output"""

    def __init__(self, config: Any) -> None:
        super().__init__(config)
        if not config.destination:
            raise LogConfigError("File destination is required for FileHandler")
        self.file_path = config.destination

        # Only create directory if the file path has a directory component
        file_dir = os.path.dirname(self.file_path)
        if file_dir:  # Only create directory if there's a directory path
            try:
                os.makedirs(file_dir, exist_ok=True)
            except PermissionError as e:
                raise LogHandlerError(
                    f"Permission denied creating directory for {self.file_path}: {e}"
                )
            except OSError as e:
                raise LogHandlerError(
                    f"OS error creating directory for {self.file_path}: {e}"
                )

    async def write(self, entries: List[LogEntry]) -> bool:
        """Write entries to file"""
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                for entry in entries:
                    if self.config.format == "json":
                        f.write(entry.to_json() + "\n")
                    else:
                        f.write(
                            f"[{entry.timestamp}] {entry.level.value} {entry.app_name}: {entry.message}\n"
                        )
            return True
        except PermissionError as e:
            raise LogWriteError(
                f"Permission denied writing to file {self.file_path}: {e}"
            )
        except OSError as e:
            raise LogWriteError(f"OS error writing to file {self.file_path}: {e}")
        except OSError as e:
            raise LogWriteError(f"IO error writing to file {self.file_path}: {e}")
        except Exception as e:
            raise LogWriteError(
                f"Unexpected error writing to file {self.file_path}: {e}"
            )

    async def flush(self) -> bool:
        """File writes are synchronous, no flush needed"""
        return True
