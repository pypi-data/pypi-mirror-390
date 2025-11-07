import datetime as dt
import json
import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Literal, Optional

from .enums import LogLevel

# LogMethod type for HTTP methods
LogMethod = Literal["POST", "PUT", "DELETE", "PATCH", "COMMENT", "GET"]


@dataclass
class LogEntity:
    """Entity information for logging"""

    type: str
    id: Optional[str] = None
    name: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_any(cls, obj: Any) -> Optional["LogEntity"]:
        if isinstance(obj, dict) and obj:
            return cls(**obj)
        elif isinstance(obj, cls):
            return obj
        return None

    @classmethod
    def from_entity(cls, entity: "Entity") -> Optional["LogEntity"]:
        """Convert Entity to LogEntity"""
        if not entity:
            return None
        return cls(
            type=entity.type,
            id=entity.id,
            name=entity.name,
            additional_info=entity.additional_info,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "id": self.id,
            "name": self.name,
            "additional_info": self.additional_info,
        }


@dataclass
class Entity:
    """Entity information for logging (legacy - use LogEntity instead)"""

    type: str  # dataset, card, user, dataflow, page, etc.
    id: Optional[str] = None
    name: Optional[str] = None
    additional_info: Dict[str, Any] = field(default_factory=dict)
    parent: Any = None  # instance of a class

    def get_additional_info(
        self, info_fn: Optional[Callable[..., Any]] = None
    ) -> Dict[str, Any]:
        """Populate additional_info when we don't have a full parent object"""
        if info_fn:
            self.additional_info = info_fn(self)
            return self.additional_info

        # Only populate additional_info if we don't have a parent object
        # This avoids duplication - use parent for full objects, additional_info for context
        if self.parent:
            return self.additional_info

        additional_info = {}
        if hasattr(self.parent, "description"):
            additional_info["description"] = getattr(self.parent, "description", "")
        if hasattr(self.parent, "owner"):
            additional_info["owner"] = getattr(self.parent, "owner", {})
        if hasattr(self.parent, "display_type"):
            additional_info["display_type"] = getattr(self.parent, "display_type", "")
        if hasattr(self.parent, "data_provider_type"):
            additional_info["data_provider_type"] = getattr(
                self.parent, "data_provider_type", ""
            )

        # Get auth instance info
        if hasattr(self.parent, "auth") and self.parent.auth:
            additional_info["domo_instance"] = getattr(
                self.parent.auth, "domo_instance", None
            )

        self.additional_info = additional_info
        return self.additional_info

    def to_dict(self) -> Dict[str, Any]:
        """Convert Entity to dictionary for JSON serialization"""
        parent_dict = None
        if self.parent:
            parent_dict = self._serialize_parent(self.parent)

        result: Dict[str, Any] = {
            "type": self.type,
            "id": self.id or "",
            "name": self.name or "",
        }

        # Include parent if we have a full object, otherwise include additional_info for context
        if parent_dict:
            result["parent"] = parent_dict
        elif self.additional_info:
            result["additional_info"] = self.additional_info

        return result

    def _serialize_parent(self, parent: Any) -> Optional[Dict[str, Any]]:
        """Safely serialize parent object to dictionary"""
        if parent is None:
            return None

        # If parent has a to_dict method, use it
        if hasattr(parent, "to_dict") and callable(getattr(parent, "to_dict")):
            try:
                parent_dict = parent.to_dict()  # type: ignore
                # Add metadata about the parent object
                parent_dict["_metadata"] = {
                    "class_name": type(parent).__name__,
                    "module": getattr(type(parent), "__module__", "unknown"),
                }
                return parent_dict
            except Exception:
                # If to_dict fails, fall back to manual extraction
                pass

        # Extract key attributes from parent object
        parent_info: Dict[str, Any] = {
            "_metadata": {
                "class_name": type(parent).__name__,
                "module": getattr(type(parent), "__module__", "unknown"),
            }
        }

        # Common attributes to extract from Domo entities
        common_attrs = [
            "id",
            "name",
            "display_name",
            "description",
            "owner",
            "display_type",
            "data_provider_type",
            "row_count",
            "column_count",
            "created_dt",
            "last_updated_dt",
            "last_touched_dt",
            "stream_id",
            "cloud_id",
            "formula",
            "status",
        ]

        for attr in common_attrs:
            if hasattr(parent, attr):
                value = getattr(parent, attr, None)
                if value is not None:
                    # Handle datetime objects
                    if hasattr(value, "isoformat"):
                        parent_info[attr] = value.isoformat()
                    # Handle simple types
                    elif isinstance(value, (str, int, float, bool)):
                        parent_info[attr] = value
                    # Handle dictionaries
                    elif isinstance(value, dict):
                        parent_info[attr] = value
                    # Handle lists (but limit size)
                    elif isinstance(value, list) and len(value) < 10:
                        parent_info[attr] = value
                    # Convert complex objects to string representation (truncated)
                    else:
                        str_value = str(value)
                        if len(str_value) > 200:
                            parent_info[attr] = str_value[:200] + "... (truncated)"
                        else:
                            parent_info[attr] = str_value

        # Extract auth information if available
        if hasattr(parent, "auth") and parent.auth:
            auth_info = {}
            if hasattr(parent.auth, "domo_instance"):
                auth_info["domo_instance"] = parent.auth.domo_instance
            if hasattr(parent.auth, "user_id"):
                auth_info["user_id"] = parent.auth.user_id
            if auth_info:
                parent_info["auth"] = auth_info

        # If we didn't extract much useful info, include a summary
        if len(parent_info) <= 1:  # Only metadata
            parent_info["summary"] = str(parent)[:500] + (
                "..." if len(str(parent)) > 500 else ""
            )

        # Special handling for common Domo classes that might not have to_dict
        if hasattr(parent, "__class__"):
            class_name = type(parent).__name__
            if "DomoDataset" in class_name:
                # Extract specific DomoDataset attributes
                dataset_attrs = [
                    "id",
                    "name",
                    "description",
                    "owner",
                    "display_type",
                    "data_provider_type",
                    "row_count",
                    "column_count",
                    "stream_id",
                    "cloud_id",
                    "created_dt",
                    "last_updated_dt",
                    "last_touched_dt",
                ]
                for attr in dataset_attrs:
                    if hasattr(parent, attr) and attr not in parent_info:
                        value = getattr(parent, attr, None)
                        if value is not None:
                            if hasattr(value, "isoformat"):
                                parent_info[attr] = value.isoformat()
                            elif isinstance(value, (str, int, float, bool, dict)):
                                parent_info[attr] = value
                            else:
                                str_value = str(value)
                                if len(str_value) > 200:
                                    parent_info[attr] = (
                                        str_value[:200] + "... (truncated)"
                                    )
                                else:
                                    parent_info[attr] = str_value

        return parent_info

    @classmethod
    def from_domo_entity(
        cls, domo_entity: Any, info_fn: Optional[Callable[..., Any]] = None
    ) -> Optional["Entity"]:
        """Create Entity from a DomoEntity object"""

        if not domo_entity:
            return None

        # Extract entity type from class name (e.g., DomoDataset -> dataset)
        entity_type = cls._extract_entity_type(type(domo_entity).__name__)

        entity = cls(
            type=entity_type,
            parent=domo_entity,
            id=getattr(domo_entity, "id", None),
            name=getattr(domo_entity, "name", None),
        )
        entity.get_additional_info(info_fn=info_fn)

        return entity

    @staticmethod
    def _extract_entity_type(class_name: str) -> str:
        """Extract entity type from DomoEntity class name"""
        # Remove 'Domo' prefix and convert to lowercase
        if class_name.startswith("Domo"):
            return class_name[4:].lower()
        return class_name.lower()


@dataclass
class HTTPDetails:
    """HTTP request/response details"""

    method: Optional[str] = None
    url: Optional[str] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    response_size: Optional[int] = None
    request_body: Optional[Any] = None
    response_body: Optional[Any] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert HTTPDetails to dictionary for JSON serialization"""
        return {
            "method": self.method,
            "url": self.url,
            "status_code": self.status_code,
            "headers": self.headers,
            "params": self.params,
            "response_size": self.response_size,
            "request_body": self.request_body,
            "response_body": self.response_body,
        }

    @classmethod
    def from_kwargs(cls, kwargs: Dict[str, Any]) -> Optional["HTTPDetails"]:
        """Create HTTPDetails from kwargs"""
        # Check if http_details is directly provided
        http_details = kwargs.get("http_details")
        if isinstance(http_details, dict) and http_details:
            return cls(**http_details)
        elif isinstance(http_details, cls):
            return http_details

        # Check for individual fields
        if any(
            k in kwargs
            for k in ["method", "url", "status_code", "headers", "response_size"]
        ):
            # Don't create HTTPDetails if method is COMMENT (not a real HTTP method)
            method = kwargs.get("method")
            if method == "COMMENT":
                return None

            return cls(
                method=kwargs.get("method"),
                url=kwargs.get("url"),
                status_code=kwargs.get("status_code"),
                headers=kwargs.get("headers"),
                response_size=kwargs.get("response_size"),
                request_body=kwargs.get("request_body"),
                response_body=kwargs.get("response_body"),
            )

        return None


@dataclass
class Correlation:
    """Correlation information for distributed tracing"""

    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    parent_span_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert Correlation to dictionary for JSON serialization"""
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
        }


class CorrelationManager:
    """Manages correlation IDs and context propagation"""

    def __init__(self) -> None:
        self.trace_id_var: ContextVar[Optional[str]] = ContextVar(
            "trace_id", default=None
        )
        self.request_id_var: ContextVar[Optional[str]] = ContextVar(
            "request_id", default=None
        )
        self.session_id_var: ContextVar[Optional[str]] = ContextVar(
            "session_id", default=None
        )
        self.span_id_var: ContextVar[Optional[str]] = ContextVar(
            "span_id", default=None
        )
        self.correlation_var: ContextVar[Optional[Correlation]] = ContextVar(
            "correlation", default=None
        )
        # Track last span_id per trace_id for proper parent span relationships
        self._trace_span_history: Dict[str, Optional[str]] = {}

    def generate_trace_id(self) -> str:
        """Generate a new trace ID"""
        return str(uuid.uuid4())

    def generate_request_id(self) -> str:
        """Generate a new request ID"""
        return uuid.uuid4().hex[:12]

    def generate_span_id(self) -> str:
        """Generate a new span ID"""
        return uuid.uuid4().hex[:16]

    def generate_session_id(self) -> str:
        """Generate a new session ID"""
        # Simple random session ID
        # Auth-based session ID generation can be implemented in domain-specific libraries
        return uuid.uuid4().hex[:12]

    def get_or_create_correlation(self) -> Correlation:
        """Get or create correlation with automatic span chaining.

        Each call creates a NEW span that chains to the previous span,
        enabling span-per-log microservices-style tracing.
        """
        # Get or create trace_id (persists across logs)
        current_trace_id = self.trace_id_var.get()
        if not current_trace_id:
            current_trace_id = self.generate_trace_id()
            self.trace_id_var.set(current_trace_id)

        # Get previous span_id to set as parent
        previous_span_id = self._trace_span_history.get(current_trace_id)

        # ALWAYS generate a NEW span_id for this log
        new_span_id = self.generate_span_id()

        # Update context and history
        self.span_id_var.set(new_span_id)
        self._trace_span_history[current_trace_id] = new_span_id

        # Create correlation with chaining
        correlation = Correlation(
            trace_id=current_trace_id,
            span_id=new_span_id,
            parent_span_id=previous_span_id,  # Chain to previous span
        )
        self.correlation_var.set(correlation)

        return correlation

    def start_new_trace(self) -> str:
        """Start a completely new trace (clear existing trace_id).

        Use this to group separate bundles of logs:
        - Bundle 1: User login flow -> trace_A
        - Bundle 2: Data processing -> trace_B

        Returns the new trace_id.
        """
        # Clear existing trace context
        self.trace_id_var.set(None)
        self.request_id_var.set(None)
        self.span_id_var.set(None)
        self.correlation_var.set(None)

        # Generate new trace_id (next log will use this)
        new_trace_id = self.generate_trace_id()
        self.trace_id_var.set(new_trace_id)

        return new_trace_id

    def start_request(
        self,
        parent_trace_id: Optional[str] = None,
        auth: Any = None,
        is_pagination_request: bool = False,
    ) -> str:
        """Start a new request context"""
        # Use existing trace_id if available, otherwise generate new one
        # Only generate new trace_id if we don't have one in context AND no parent provided
        current_trace_id = self.trace_id_var.get()
        trace_id = parent_trace_id or current_trace_id or self.generate_trace_id()

        request_id = self.generate_request_id()

        # Use existing session_id or generate new one
        session_id = self.session_id_var.get() or self.generate_session_id()
        span_id = self.generate_span_id()

        # Handle parent span for pagination vs regular requests
        if is_pagination_request:
            # For pagination requests, use the original parent span for this trace
            # This ensures all pagination requests have the same parent
            parent_span_id = self._trace_span_history.get(f"{trace_id}_original_parent")
            if not parent_span_id:
                # If no original parent stored, this is the first pagination request
                # Store current span as original parent for future pagination requests
                parent_span_id = self._trace_span_history.get(trace_id)
                self._trace_span_history[f"{trace_id}_original_parent"] = (
                    parent_span_id or None
                )
        else:
            # For regular requests, use normal span chaining
            parent_span_id = self._trace_span_history.get(trace_id)
            # Store this as the original parent for future pagination requests
            self._trace_span_history[f"{trace_id}_original_parent"] = parent_span_id

        # Update the span history with the current span_id for this trace
        self._trace_span_history[trace_id] = span_id

        # Set context variables
        self.trace_id_var.set(trace_id)
        self.request_id_var.set(request_id)
        self.session_id_var.set(session_id)
        self.span_id_var.set(span_id)

        # Create correlation object
        correlation = Correlation(
            trace_id=trace_id, span_id=span_id, parent_span_id=parent_span_id
        )
        self.correlation_var.set(correlation)

        return request_id

    def get_current_context(self) -> Dict[str, Any]:
        """Get current correlation context"""
        correlation = self.correlation_var.get()
        return {
            "trace_id": self.trace_id_var.get(),
            "request_id": self.request_id_var.get(),
            "session_id": self.session_id_var.get(),
            "span_id": self.span_id_var.get(),
            "correlation": correlation,
        }

    def set_context_value(self, key: str, value: Any) -> None:
        """Set a value in the correlation context"""
        correlation = self.correlation_var.get()
        if correlation:
            correlation_dict = correlation.__dict__.copy()
            correlation_dict[key] = value
            self.correlation_var.set(Correlation(**correlation_dict))


# Global correlation manager instance
correlation_manager = CorrelationManager()


@dataclass
class MultiTenant:
    """Multi-tenant information"""

    user_id: Optional[str] = None
    session_id: Optional[str] = None
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert MultiTenant to dictionary for JSON serialization"""
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "organization_id": self.organization_id,
        }

    @classmethod
    def from_kwargs(
        cls, kwargs: Dict[str, Any], user: Optional[str] = None
    ) -> Optional["MultiTenant"]:
        """Create MultiTenant from kwargs or individual fields"""
        # Check if multi_tenant is directly provided
        multi_tenant = kwargs.get("multi_tenant")
        if isinstance(multi_tenant, dict) and multi_tenant:
            return cls(**multi_tenant)
        elif isinstance(multi_tenant, cls):
            return multi_tenant

        # Check for individual fields
        if any(
            k in kwargs
            for k in ["user_id", "session_id", "tenant_id", "organization_id"]
        ):
            return cls(
                user_id=kwargs.get("user_id") or user,
                session_id=kwargs.get("session_id"),
                tenant_id=kwargs.get("tenant_id"),
                organization_id=kwargs.get("organization_id"),
            )

        return None


@dataclass
class LogEntry:
    """Enhanced log entry with structured JSON format"""

    # Core log fields
    timestamp: str
    level: LogLevel
    message: str
    method: LogMethod = "COMMENT"
    app_name: str = "default"

    # Business context
    user: Optional[str] = None
    action: Optional[str] = None
    level_name: Optional[str] = None
    entity: Optional[LogEntity] = None
    status: str = "info"
    duration_ms: Optional[int] = None

    # Distributed tracing
    correlation: Optional[Correlation] = None

    # Multi-tenant context
    multi_tenant: Optional[MultiTenant] = None

    # HTTP details (for API calls)
    http_details: Optional[HTTPDetails] = None

    # Flexible metadata
    extra: Dict[str, Any] = field(default_factory=dict)

    # Console output customization
    # Color for console output (e.g., 'red', 'green', 'blue', 'yellow', 'bold_red', 'dim_blue')
    color: Optional[str] = None

    def __post_init__(self) -> None:
        # Only override method from http_details if method is still default
        if self.http_details and self.method == "COMMENT" and self.http_details.method:
            self.method = self.http_details.method  # type: ignore

    def to_dict(self) -> Dict[str, Any]:
        """Convert LogEntry to dictionary for JSON serialization with proper formatting."""
        result = {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "app_name": self.app_name,
            "message": self.message,
            "method": self.method,
            "status": self.status,
            "duration_ms": self.duration_ms,
        }

        # Only include action if it's not None
        if self.action is not None:
            result["action"] = self.action

        # Only include level_name if it's not None
        if self.level_name is not None:
            result["level_name"] = self.level_name

        # Add user (with fallback to multi_tenant.user_id)
        user = self.user
        if not user and self.multi_tenant and self.multi_tenant.user_id:
            user = self.multi_tenant.user_id
        if user:
            result["user"] = user

        # Add entity (serialize if present)
        if self.entity:
            result["entity"] = self.entity.to_dict()

        # Add correlation (serialize if present)
        if self.correlation:
            result["correlation"] = (
                self.correlation.to_dict()
                if hasattr(self.correlation, "to_dict")
                else self.correlation.__dict__
            )

        # Add multi_tenant (serialize if present)
        if self.multi_tenant:
            result["multi_tenant"] = (
                self.multi_tenant.to_dict()
                if hasattr(self.multi_tenant, "to_dict")
                else self.multi_tenant.__dict__
            )

        # Add http_details (serialize if present)
        if self.http_details:
            result["http_details"] = self.http_details.to_dict()

        # Add extra (only if not empty)
        if self.extra:
            result["extra"] = self.extra

        # Add color (only if specified)
        if self.color:
            result["color"] = self.color

        return result

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def create(
        cls, level: LogLevel, message: str, app_name: str = "default", **kwargs: Any
    ) -> "LogEntry":
        """Factory method to create a LogEntry with current timestamp"""
        timestamp = dt.datetime.now().isoformat() + "Z"
        user = kwargs.get("user")
        action = kwargs.get("action")
        level_name = kwargs.get("level_name")
        status = kwargs.get("status", "info")
        duration_ms = kwargs.get("duration_ms")
        method = kwargs.get("method", "COMMENT")  # Extract method from kwargs
        extra = kwargs.get("extra", {})
        color = kwargs.get("color")

        entity_obj = LogEntity.from_any(kwargs.get("entity"))

        # Handle correlation - can be dict or Correlation object
        correlation_param = kwargs.get("correlation")
        if isinstance(correlation_param, Correlation):
            correlation_obj = correlation_param
        elif isinstance(correlation_param, dict):
            correlation_obj = Correlation(**correlation_param)
        else:
            correlation_obj = None

        multi_tenant_obj = MultiTenant.from_kwargs(kwargs, user)
        http_details_obj = HTTPDetails.from_kwargs(kwargs)

        if not user and multi_tenant_obj and multi_tenant_obj.user_id:
            user = multi_tenant_obj.user_id

        return cls(
            timestamp=timestamp,
            level=level,
            app_name=app_name,
            message=message,
            method=method,  # Pass method to constructor
            user=user,
            action=action,
            level_name=level_name,
            entity=entity_obj,
            status=status,
            duration_ms=duration_ms,
            correlation=correlation_obj,
            multi_tenant=multi_tenant_obj,
            http_details=http_details_obj,
            extra=extra,
            color=color,
        )

    def _serialize_http_details(self) -> Optional[Dict[str, Any]]:
        """Serialize HTTP details for logging, filtering sensitive data"""
        if not self.http_details:
            return None

        http_details_dict = {}

        if self.http_details.method:
            http_details_dict["method"] = self.http_details.method

        if self.http_details.url:
            http_details_dict["url"] = self.http_details.url

        if self.http_details.headers:
            # Only include important headers, not sensitive ones
            safe_headers = {}
            for k, v in self.http_details.headers.items():
                if k.lower() not in [
                    "authorization",
                    "cookie",
                    "x-domo-authentication",
                ]:
                    safe_headers[k] = v
            if safe_headers:
                http_details_dict["headers"] = safe_headers

        if self.http_details.params:
            http_details_dict["params"] = self.http_details.params

        if self.http_details.request_body:
            # Truncate large request bodies
            if (
                isinstance(self.http_details.request_body, str)
                and len(self.http_details.request_body) > 500
            ):
                http_details_dict["request_body"] = (
                    self.http_details.request_body[:500] + "..."
                )
            else:
                http_details_dict["request_body"] = self.http_details.request_body

        if self.http_details.response_body:
            # Truncate large response bodies
            if (
                isinstance(self.http_details.response_body, str)
                and len(self.http_details.response_body) > 500
            ):
                http_details_dict["response_body"] = (
                    self.http_details.response_body[:500] + "..."
                )
            else:
                http_details_dict["response_body"] = self.http_details.response_body

        return http_details_dict if http_details_dict else None
