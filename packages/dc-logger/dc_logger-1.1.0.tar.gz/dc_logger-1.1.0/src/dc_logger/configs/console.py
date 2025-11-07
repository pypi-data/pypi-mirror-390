"""Console-specific log configuration"""

from dataclasses import dataclass
from typing import Any, Dict

from .base import LogConfig


@dataclass
class ConsoleLogConfig(LogConfig):
    """Console-specific log configuration"""

    def to_platform_config(self) -> Dict[str, Any]:
        return {"provider": "console"}

    def validate_config(self) -> bool:
        return True
