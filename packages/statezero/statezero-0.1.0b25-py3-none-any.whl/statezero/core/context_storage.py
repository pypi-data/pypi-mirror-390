import contextvars
from uuid import uuid4
from typing import Any, Optional

# This context variable holds the current operation id (from client headers).
current_operation_id = contextvars.ContextVar("current_operation_id", default=None)

# This context variable holds the canonical id (server-generated for cache sharing).
current_canonical_id = contextvars.ContextVar("current_canonical_id", default=None)

# This context variable holds old instance state for update operations (for namespace evaluation).
current_old_instance = contextvars.ContextVar("current_old_instance", default=None)


def get_or_create_canonical_id():
    """
    Get the current canonical_id, or generate a new one if it doesn't exist.
    Canonical IDs are used for cross-client cache sharing.

    Returns:
        str: The canonical ID for this request context
    """
    canonical_id = current_canonical_id.get()
    if canonical_id is None:
        canonical_id = str(uuid4())
        current_canonical_id.set(canonical_id)
    return canonical_id


def set_old_instance(instance: Any) -> None:
    """
    Store the old instance state before an update operation.
    Used for namespace evaluation to detect additions/removals.

    Args:
        instance: The instance before update
    """
    current_old_instance.set(instance)


def get_old_instance() -> Optional[Any]:
    """
    Retrieve the old instance state stored before update.

    Returns:
        The old instance, or None if not set
    """
    return current_old_instance.get()


def clear_old_instance() -> None:
    """
    Clear the old instance state after use.
    """
    current_old_instance.set(None)