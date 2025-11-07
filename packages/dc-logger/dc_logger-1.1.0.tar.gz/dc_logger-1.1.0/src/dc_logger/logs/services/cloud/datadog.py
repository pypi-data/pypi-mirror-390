__all__ = ["DatadogServiceConfig", "DatadogHandler"]

import asyncio
import concurrent.futures
import socket
import requests
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


from dc_logger.client.base import OutputMode
from dc_logger.client.enums import LogLevel
from dc_logger.client.exceptions import LogConfigError, LogHandlerError
from dc_logger.client.models import LogEntry
from dc_logger.handlers.cloud.base import CloudHandler
from dc_logger.services.base import CloudServiceConfig


@dataclass
class DatadogServiceConfig(CloudServiceConfig):
    """Datadog-specific log configuration"""

    output_mode: OutputMode = "cloud"
    cloud_provider: str = "datadog"

    api_key: Optional[str] = field(default=None, repr=False)
    app_key: Optional[str] = field(default=None, repr=False)

    site: str = "datadoghq.com"
    service: str = "dc_logger"
    env: str = "production"

    @staticmethod
    def _derive_intake_url(site: str) -> str:
        if site == "datadoghq.com":
            return "https://http-intake.logs.datadoghq.com/v1/input"

        elif site.startswith("us"):
            region = site.replace(".datadoghq.com", "")
            return f"https://http-intake.logs.{region}.datadoghq.com/v1/input"

        return f"https://http-intake.logs.{site}/v1/input"

    def derive_intake_url(self) -> str:
        return self._derive_intake_url(site=self.site)

    def to_platform_config(self) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "app_key": self.app_key,
            "site": self.site,
            "service": self.service,
            "env": self.env,
            "cloud_provider": self.cloud_provider,
        }

    def validate_config(self) -> bool:
        if not self.api_key:
            raise LogConfigError("Datadog API key is required")
        return True


class DatadogHandler(CloudHandler):
    """Datadog log handler using direct HTTP API"""

    def __init__(self, config: Any) -> None:
        super().__init__(config)
        self.config = config  # Store original config object
        self.cloud_config = config.to_platform_config()
        self._validate_config()

    def _validate_config(self) -> bool:
        """Validate Datadog configuration"""
        api_key = self.cloud_config.get("api_key")
        if not api_key:
            raise LogHandlerError("Datadog API key is required")
        return True

    def validate_config(self) -> bool:
        """Validate the configuration - required by ServiceHandler interface"""
        if not self.config:
            raise ValueError("Datadog configuration is not set.")
        return self.config.validate_config()

    def _get_hostname(self) -> str:
        """Get the actual hostname/IP address of the machine"""
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            return ip_address
        except Exception:
            return "127.0.0.1"

    def _convert_log_level(self, level: LogLevel) -> str:
        """Convert LogLevel enum to Datadog log level"""
        level_mapping = {
            LogLevel.DEBUG: "debug",
            LogLevel.INFO: "info",
            LogLevel.WARNING: "warning",
            LogLevel.ERROR: "error",
            LogLevel.CRITICAL: "critical",
        }
        return level_mapping.get(level, "info")

    def _safe_serialize(self, obj: Any) -> Any:
        """Safely serialize objects for JSON, handling complex types"""
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, list):
            return [self._safe_serialize(item) for item in obj]
        if isinstance(obj, dict):
            return {key: self._safe_serialize(value) for key, value in obj.items()}
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            try:
                return self._safe_serialize(obj.to_dict())
            except Exception:
                return str(obj)
        if hasattr(obj, "__dict__"):
            try:
                return self._safe_serialize(obj.__dict__)
            except Exception:
                return str(obj)
        str_repr = str(obj)
        if len(str_repr) > 1000:
            return str_repr[:1000] + "... (truncated)"
        return str_repr

    def _convert_entry_for_provider(self, entries: List[LogEntry]) -> List[dict]:
        """Convert LogEntry objects to Datadog log format"""
        logs_data = []
        hostname = self._get_hostname()
        for entry in entries:
            log_data = {
                "message": entry.message,
                "ddsource": "domolibrary",
                "service": self.cloud_config.get("service", "domolibrary"),
                "hostname": hostname,
                "status": self._convert_log_level(entry.level),
                "ddtags": f"env:{self.cloud_config.get('env', 'production')},service:{self.cloud_config.get('service', 'domolibrary')}",
                
            }
            if entry.entity:
                log_data["entity"] = self._safe_serialize(entry.entity)
            if entry.correlation:
                log_data["correlation"] = {
                    "trace_id": entry.correlation.trace_id,
                    "span_id": entry.correlation.span_id,
                    "parent_span_id": entry.correlation.parent_span_id,
                }
            if entry.multi_tenant:
                log_data["multi_tenant"] = {
                    "user_id": entry.multi_tenant.user_id,
                    "session_id": entry.multi_tenant.session_id,
                    "tenant_id": entry.multi_tenant.tenant_id,
                    "organization_id": entry.multi_tenant.organization_id,
                }
            if entry.http_details:
                log_data["http_details"] = {
                    "method": entry.http_details.method,
                    "url": entry.http_details.url,
                    "status_code": entry.http_details.status_code,
                    "params": self._safe_serialize(entry.http_details.params),
                    "request_body": self._safe_serialize(
                        entry.http_details.request_body
                    ),
                    "response_body": (
                        entry.http_details.response_body
                        if isinstance(
                            entry.http_details.response_body,
                            (str, int, float, bool, type(None)),
                        )
                        else str(entry.http_details.response_body)[:500]
                    ),
                    "response_size": entry.http_details.response_size,
                }
            if entry.extra:
                log_data["extra"] = self._safe_serialize(entry.extra)
            logs_data.append(log_data)
        return logs_data

    def _send_logs_simple_api(self, entries: List[LogEntry]) -> bool:
        """Send logs using direct HTTP requests to Datadog (synchronous)"""
        if requests is None:
            raise ImportError(
                "requests library is required for DatadogHandler. "
                "Install it with: pip install requests"
            )

        intake_url = self.config.derive_intake_url()
        api_key = self.cloud_config.get("api_key")
        headers = {"Content-Type": "application/json", "DD-API-KEY": api_key}
        logs_data = self._convert_entry_for_provider(entries)
        if not logs_data:
            print("DatadogHandler: No log data to send.")
            return False
        print(f"DatadogHandler: Sending {len(logs_data)} log entries to {intake_url}")
        response = requests.post(
            intake_url, json=logs_data, headers=headers, timeout=10
        )
        if response.status_code not in [200, 202]:
            print(
                f"DatadogHandler: Failed to send logs - Status {response.status_code}: {response.text}"
            )
            return False
        print(
            f"DatadogHandler: Successfully sent {len(logs_data)} log entries to Datadog"
        )
        return True

    async def _send_to_cloud(self, entries: List[LogEntry]) -> bool:
        """Send log entries to Datadog - implements abstract method from CloudHandler"""
        def submit_logs():
            return self._send_logs_simple_api(entries)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(submit_logs)
            result = await asyncio.wrap_future(future)
            return bool(result)