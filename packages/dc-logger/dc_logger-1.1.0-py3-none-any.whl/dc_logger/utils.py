import inspect
from typing import Any, Dict, Optional

from .client.models import Entity, LogEntity


def _find_calling_context() -> Dict[str, Any]:
    """Walk up the call stack to find calling context and Domo entity objects"""
    result: Dict[str, Any] = {
        "entity": None,
        "calling_chain": [],
        "primary_caller": None,
    }

    try:
        # Get the current frame and walk up the stack
        current_frame = inspect.currentframe()

        # Walk up the call stack (skip current frame and decorator frames)
        frame = current_frame
        for depth in range(15):  # Increased limit for better context
            if frame is None:
                break
            frame = frame.f_back
            if frame is None:
                break

            # Get frame information
            frame_info = {
                "function": frame.f_code.co_name,
                "filename": frame.f_code.co_filename,
                "line": frame.f_lineno,
                "depth": depth,
            }

            # Get local variables from this frame
            frame_locals = frame.f_locals

            # Look for 'self' parameter that might be a Domo entity
            if "self" in frame_locals:
                self_obj = frame_locals["self"]
                class_name = type(self_obj).__name__

                # Check if this is a Domo entity class instance (generic check)
                if _is_domo_entity(self_obj):
                    # Found a Domo entity in the call stack!
                    if result["entity"] is None:
                        result["entity"] = Entity.from_domo_entity(self_obj)

                    # Add to calling chain with class context
                    frame_info["class"] = class_name
                    frame_info["method"] = f"{class_name}.{frame.f_code.co_name}"
                    frame_info["is_domo_entity"] = True

                    # Set as primary caller if it's the first meaningful one we find
                    if result[
                        "primary_caller"
                    ] is None and frame.f_code.co_name not in [
                        "wrapper",
                        "__call__",
                        "__init__",
                    ]:
                        result["primary_caller"] = frame_info["method"]

                elif hasattr(self_obj, "__class__"):
                    # Regular class method
                    frame_info["class"] = class_name
                    frame_info["method"] = f"{class_name}.{frame.f_code.co_name}"
                    frame_info["is_domo_entity"] = False

            # Skip decorator and wrapper functions for cleaner call chain
            if frame.f_code.co_name not in [
                "wrapper",
                "decorator",
                "async_wrapper",
                "sync_wrapper",
                "__call__",
            ]:
                result["calling_chain"].append(frame_info)

    except Exception:
        # If anything goes wrong with stack inspection, just continue
        pass

    return result


def _find_calling_entity() -> Optional[LogEntity]:
    """Walk up the call stack to find Domo entity objects in calling methods"""
    context = _find_calling_context()
    return context.get("entity")


def create_dynamic_action_name(
    base_action: str, calling_context: Optional[Dict[str, Any]] = None
) -> str:
    """Create a dynamic action name that includes calling context"""
    if calling_context is None:
        calling_context = _find_calling_context()

    # Start with the base action
    action_parts = [base_action]

    # Add primary caller if available
    if calling_context.get("primary_caller"):
        action_parts.insert(0, calling_context["primary_caller"])

    # Create hierarchical action name
    if len(action_parts) > 1:
        return " -> ".join(action_parts)
    else:
        return base_action


def _is_domo_entity(obj: Any) -> bool:
    """Check if an object is a Domo entity (has id and auth attributes)"""
    return (
        hasattr(obj, "id")
        and hasattr(obj, "auth")
        and hasattr(obj, "__class__")
        and "Domo" in str(type(obj))
    )


def _extract_entity_id_from_params(kwargs: dict) -> Optional[tuple]:
    """Extract entity ID from any *_id parameter"""
    for param_name, param_value in kwargs.items():
        if param_name.endswith("_id") and isinstance(param_value, str):
            # Convert parameter name to entity type (e.g., dataset_id -> dataset)
            entity_type = param_name.replace("_id", "")
            return entity_type, param_value
    return None


def enhance_entity_from_response(
    entity: Optional[LogEntity], result: Any
) -> Optional[LogEntity]:
    """Enhance entity information from function response data - works for any entity type"""
    if not entity or not hasattr(result, "response"):
        return entity

    if not isinstance(result.response, dict):
        return entity

    response_data = result.response

    # Only enhance if the response ID matches the entity ID
    if response_data.get("id") == entity.id:
        # Generic field mapping that works for most entity types
        common_fields = {
            "name": "name",
            "description": "description",
            "displayType": "display_type",
            "dataProviderType": "data_provider_type",
            "rowCount": "row_count",
            "columnCount": "column_count",
            "owner": "owner",
            "streamId": "stream_id",
            "cloudId": "cloud_id",
            "created": "created_dt",
            "lastUpdated": "last_updated_dt",
            "lastTouched": "last_touched_dt",
            # User fields
            "displayName": "display_name",
            "email": "email",
            "role": "role",
            # Page fields
            "parentId": "parent_id",
            "cardCount": "card_count",
            # Card fields
            "datasources": "datasources",
            "visualization": "visualization",
            # Generic fields
            "type": "entity_type",
            "status": "status",
        }

        # Update entity with available fields from response
        for response_key, entity_key in common_fields.items():
            if response_key in response_data:
                entity.additional_info[entity_key] = response_data[response_key]

        # Also update the entity name
        if "name" in response_data:
            entity.name = response_data["name"]
        elif "displayName" in response_data:
            entity.name = response_data["displayName"]

    return entity


def extract_entity_from_args(args: Any, kwargs: Any) -> Optional[LogEntity]:
    """Extract entity information from function arguments and call stack"""

    # 1. Check if any argument is a Domo entity object
    for arg in args:
        if _is_domo_entity(arg):
            entity = Entity.from_domo_entity(arg)
            return LogEntity.from_entity(entity) if entity else None

    # 2. Check for 'self' parameter which might be a Domo entity (for class methods)
    if args and _is_domo_entity(args[0]):
        entity = Entity.from_domo_entity(args[0])
        return LogEntity.from_entity(entity) if entity else None

    # 3. Walk up the call stack to find Domo entity objects
    # This is crucial for get_data calls from DomoDataset methods
    calling_entity = _find_calling_entity()
    if calling_entity:
        return calling_entity

    # 4. Extract basic entity info from parameters (for route functions)
    result = _extract_entity_id_from_params(kwargs)
    entity_type = None
    entity_id = None
    if result:
        entity_type, entity_id = result

    if entity_type and entity_id:
        additional_info = {}

        # Add parent class info if available
        parent_class = kwargs.get("parent_class")
        if parent_class:
            additional_info["parent_class"] = str(parent_class)

        # Extract domo instance from auth if available
        auth = kwargs.get("auth")
        if auth and hasattr(auth, "domo_instance"):
            additional_info["domo_instance"] = auth.domo_instance

        return LogEntity(
            type=entity_type,
            id=entity_id,
            name=None,  # Will be populated from response if available
            additional_info=additional_info,
        )

    return None
