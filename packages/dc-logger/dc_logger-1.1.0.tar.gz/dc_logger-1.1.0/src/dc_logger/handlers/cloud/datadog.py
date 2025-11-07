import asyncio
import concurrent.futures
import socket
from typing import Any, List

from ...client.enums import LogLevel
from ...client.exceptions import LogHandlerError
from ...client.models import LogEntry
from .base import CloudHandler


class DatadogHandler(CloudHandler):
    """Datadog log handler using direct HTTP API"""

    def __init__(self, config: Any) -> None:
        super().__init__(config)
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate Datadog configuration"""
        api_key = self.cloud_config.get("api_key")
        if not api_key:
            raise LogHandlerError("Datadog API key is required")

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

        # Handle basic JSON-serializable types
        if isinstance(obj, (str, int, float, bool)):
            return obj

        # Handle lists
        if isinstance(obj, list):
            return [self._safe_serialize(item) for item in obj]

        # Handle dictionaries
        if isinstance(obj, dict):
            return {key: self._safe_serialize(value) for key, value in obj.items()}

        # Handle objects with to_dict method
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            try:
                return self._safe_serialize(obj.to_dict())
            except Exception:
                return str(obj)

        # Handle objects with __dict__
        if hasattr(obj, "__dict__"):
            try:
                return self._safe_serialize(obj.__dict__)
            except Exception:
                return str(obj)

        # Fallback to string representation, truncated for large objects
        str_repr = str(obj)
        if len(str_repr) > 1000:
            return str_repr[:1000] + "... (truncated)"
        return str_repr

    def _send_logs_simple_api(self, entries: List[LogEntry]) -> bool:
        """Send logs using direct HTTP requests to Datadog"""
        try:
            import requests

            # Get configuration
            api_key = self.cloud_config.get("api_key")
            site = self.cloud_config.get("site", "datadoghq.com")

            # Determine the intake URL based on site
            if site == "datadoghq.com":
                intake_url = "https://http-intake.logs.datadoghq.com/v1/input"
            elif site.startswith("us"):
                region = site.replace(".datadoghq.com", "")
                intake_url = f"https://http-intake.logs.{region}.datadoghq.com/v1/input"
            else:
                intake_url = f"https://http-intake.logs.{site}/v1/input"

            # Convert entries to log format
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
                    "timestamp": entry.timestamp,
                }

                # Add structured data with safe serialization
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

            # Send via HTTP POST
            headers = {"Content-Type": "application/json", "DD-API-KEY": api_key}

            # Debug: Print first log entry for troubleshooting
            if logs_data:
                print(
                    f"DatadogHandler: Sending {len(logs_data)} log entries to {intake_url}"
                )
                # Print a sample of the first log entry (truncated for readability)
                sample_log = logs_data[0].copy()
                if len(str(sample_log)) > 500:
                    print(
                        f"DatadogHandler: Sample log entry: {str(sample_log)[:500]}..."
                    )
                else:
                    print(f"DatadogHandler: Sample log entry: {sample_log}")

            response = requests.post(
                intake_url, json=logs_data, headers=headers, timeout=10
            )

            if response.status_code in [200, 202]:
                print(
                    f"DatadogHandler: Successfully sent {len(logs_data)} log entries to Datadog"
                )
                return True
            else:
                print(
                    f"DatadogHandler: Failed to send logs - Status {response.status_code}: {response.text}"
                )
                return False

        except (TypeError, ValueError) as e:
            print(f"DatadogHandler: JSON serialization error - {e}")
            print(f"DatadogHandler: Problematic data: {logs_data}")
            return False
        except Exception as e:
            print(f"DatadogHandler: Failed to send logs - {e}")
            return False

    async def _send_to_cloud(self, entries: List[LogEntry]) -> bool:
        """Send log entries to Datadog using direct HTTP API"""

        def submit_logs() -> Any:
            return self._send_logs_simple_api(entries)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(submit_logs)
            result = await asyncio.wrap_future(future)
            return bool(result)
