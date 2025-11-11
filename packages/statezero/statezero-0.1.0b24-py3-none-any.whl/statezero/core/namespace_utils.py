"""
Utilities for namespace-based event filtering.

Namespaces allow selective notification of clients based on simple query filters.
Supports equality checks and __in lookups, including nested fields.
"""
from typing import Any, Dict, List, Optional, Set
import hashlib
import json


def get_direct_value(instance: Any, field_name: str) -> Any:
    """
    Get value from a direct field on the instance (no nested lookups).

    This avoids N+1 queries by only accessing fields directly on the instance,
    not traversing relationships.

    Examples:
        get_direct_value(message, 'room_id') → message.room_id (OK)
        get_direct_value(message, 'status') → message.status (OK)

    Args:
        instance: The model instance
        field_name: Direct field name (no __ allowed)

    Returns:
        The field value, or None if field doesn't exist
    """
    return getattr(instance, field_name, None)


def should_emit_to_namespace(instance: Any, namespace: Dict[str, Any]) -> bool:
    """
    Check if an instance matches a namespace filter.

    IMPORTANT: Only direct fields are supported (no nested lookups with __).
    This prevents N+1 queries during event emission.

    Supported:
    - Simple equality: {'room_id': 5}
    - Direct FK fields: {'user_id': 123}
    - __in lookups: {'status__in': ['active', 'pending']}

    NOT supported (silently ignored):
    - Nested lookups: {'room__organization_id': 10}

    Args:
        instance: The model instance to check
        namespace: Dict of field filters (direct fields only)

    Returns:
        True if instance matches all namespace conditions

    Examples:
        >>> message = Message(room_id=5, status='active')
        >>> should_emit_to_namespace(message, {'room_id': 5})
        True
        >>> should_emit_to_namespace(message, {'room_id': 7})
        False
        >>> should_emit_to_namespace(message, {'status__in': ['active', 'pending']})
        True
    """
    for key, expected_value in namespace.items():
        # Handle __in lookups
        if key.endswith('__in'):
            field_name = key[:-4]  # Remove '__in'

            # Check for nested lookups (not allowed) - silently skip
            if '__' in field_name:
                continue

            actual_value = get_direct_value(instance, field_name)

            if actual_value not in expected_value:
                return False
        else:
            # Simple equality check

            # Check for nested lookups (not allowed) - silently skip
            if '__' in key:
                continue

            actual_value = get_direct_value(instance, key)

            if actual_value != expected_value:
                return False

    return True


def get_matching_namespaces(
    instance: Any,
    namespaces: list[Dict[str, Any]],
    old_instance: Optional[Any] = None
) -> set[str]:
    """
    Get all namespaces that should be notified about this instance change.

    For updates, checks both old and new state to catch:
    - Additions to namespace (didn't match before, matches now)
    - Removals from namespace (matched before, doesn't match now)

    Args:
        instance: The current/new instance state
        namespaces: List of namespace dicts to check
        old_instance: The previous instance state (for updates)

    Returns:
        Set of namespace JSON strings that should be notified

    Examples:
        >>> message_before = Message(room_id=5)
        >>> message_after = Message(room_id=7)
        >>> namespaces = [{'room_id': 5}, {'room_id': 7}]
        >>> get_matching_namespaces(message_after, namespaces, message_before)
        {'{"room_id": 5}', '{"room_id": 7}'}  # Both notified
    """
    import json

    matching = set()

    for namespace in namespaces:
        # For updates, check both before and after
        if old_instance is not None:
            # Was it in this namespace before? (removal)
            if should_emit_to_namespace(old_instance, namespace):
                matching.add(json.dumps(namespace, sort_keys=True))

            # Is it in this namespace now? (addition)
            if should_emit_to_namespace(instance, namespace):
                matching.add(json.dumps(namespace, sort_keys=True))
        else:
            # Create/Delete: only check current state
            if should_emit_to_namespace(instance, namespace):
                matching.add(json.dumps(namespace, sort_keys=True))

    return matching


def extract_namespace_from_filter(query_filter: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract namespace-compatible filters from a query filter.

    Only includes simple equality and __in lookups.
    Excludes complex filters like __gte, __lt, __contains, etc.

    Args:
        query_filter: Full query filter dict

    Returns:
        Namespace dict with only supported filters

    Examples:
        >>> extract_namespace_from_filter({
        ...     'room_id': 5,
        ...     'created_at__gte': '2024-01-01',
        ...     'type__in': ['user', 'system']
        ... })
        {'room_id': 5, 'type__in': ['user', 'system']}
    """
    namespace = {}

    # List of unsupported lookup suffixes
    unsupported = [
        '__gte', '__gt', '__lte', '__lt',
        '__contains', '__icontains',
        '__startswith', '__endswith',
        '__istartswith', '__iendswith',
        '__range', '__isnull',
        '__regex', '__iregex'
    ]

    for key, value in query_filter.items():
        # Skip unsupported lookups
        if any(key.endswith(suffix) for suffix in unsupported):
            continue

        # Include simple equality and __in
        namespace[key] = value

    return namespace


def get_namespace_hash(namespace: Dict[str, Any]) -> str:
    """
    Generate a stable hash for a namespace.

    Args:
        namespace: Namespace dict

    Returns:
        Hash string for use in cache keys

    Examples:
        >>> get_namespace_hash({'room_id': 5})
        'a1b2c3...'
    """
    namespace_json = json.dumps(namespace, sort_keys=True)
    return hashlib.md5(namespace_json.encode()).hexdigest()


def should_notify_namespace(
    instance: Any,
    namespace: Dict[str, Any],
    cached_pks: Set[Any]
) -> bool:
    """
    Determine if a namespace should be notified about an instance change.

    A namespace should be notified if:
    - Instance WAS in the cached queryset (removal or update)
    - Instance NOW matches the namespace (addition or update)

    Args:
        instance: The instance after the change
        namespace: The namespace filter
        cached_pks: Set of PKs that were previously in this namespace's queryset

    Returns:
        True if namespace should be notified

    Examples:
        >>> # Instance was in queryset, still matches
        >>> should_notify_namespace(message, {'room_id': 5}, {1, 2, 3})
        True

        >>> # Instance was in queryset, no longer matches (moved rooms)
        >>> message.room_id = 7
        >>> should_notify_namespace(message, {'room_id': 5}, {3})
        True  # Notify about removal

        >>> # Instance wasn't in queryset, now matches (new message)
        >>> should_notify_namespace(new_message, {'room_id': 5}, set())
        True  # Notify about addition
    """
    instance_pk = instance.pk
    was_in_queryset = instance_pk in cached_pks
    matches_now = should_emit_to_namespace(instance, namespace)

    # Notify if it was there OR is there now
    return was_in_queryset or matches_now


def update_namespace_cache(
    cache,
    model_name: str,
    namespace: Dict[str, Any],
    instance: Any,
    timeout: int = 3600
) -> None:
    """
    Update the PK cache for a namespace after an instance change.

    Args:
        cache: Django cache instance
        model_name: Model name
        namespace: Namespace dict
        instance: The instance that changed
        timeout: Cache timeout in seconds (default 1 hour)
    """
    namespace_hash = get_namespace_hash(namespace)
    cache_key = f"namespace_pks:{model_name}:{namespace_hash}"

    # Get current cached PKs
    cached_pks = cache.get(cache_key, set())

    # Update based on whether instance matches namespace
    if should_emit_to_namespace(instance, namespace):
        cached_pks.add(instance.pk)
    else:
        cached_pks.discard(instance.pk)

    # Save back to cache
    cache.set(cache_key, cached_pks, timeout)
