__all__ = ["CloudServiceConfig", "CloudHandler"]

import asyncio
import concurrent.futures
import socket
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List

from dc_logger.client.base import LogEntry, ServiceConfig, ServiceHandler
from dc_logger.client.exceptions import LogWriteError


@dataclass
class CloudServiceConfig(ServiceConfig):
    """stores auth and connection information to a service provider"""

    cloud_provider: str = ""  # Will be validated in validate_config

    @abstractmethod
    def to_platform_config(self) -> Dict[str, Any]:
        """Get cloud provider specific configuration"""
        raise NotImplementedError()


@dataclass
class CloudHandler(ServiceHandler):
    """base class for communicating with service provider (route functions)"""

    # def __init__(self, config):
    #     super().__init__(config)

    @abstractmethod
    async def _send_logs_simple_api(self, entries: List[LogEntry]) -> Any:
        """Send logs using simple API - must be implemented by subclasses"""
        pass

    #     self.cloud_config = config.to_platform_config()
    #     config.validate_config()

    """should i pool logs"""

    async def _send_to_cloud(self, entries: List[LogEntry]) -> bool:
        """Send log entries to Datadog using direct HTTP API"""

        def submit_logs() -> Any:
            return self._send_logs_simple_api(entries)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(submit_logs)
            result = await asyncio.wrap_future(future)
            return bool(result)

    async def _write_pooling(self, entry: Any) -> bool:
        # if pool:
        #     await self._send_to_cloud(self.buffer)
        return True

    async def write(self, entry: Any) -> bool:
        """Write entries to cloud provider"""
        try:
            return await self._write_pooling(entry)
        except Exception as e:
            raise LogWriteError(f"Error sending logs to cloud provider: {e}") from e

    def _get_hostname(self) -> str:
        """Get the actual hostname/IP address of the machine"""
        try:
            # Try to get the hostname, fallback to IP if needed
            hostname = socket.gethostname()
            # Get the IP address for more specific identification
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception:
            # Fallback to localhost if hostname resolution fails
            return "127.0.0.1"
