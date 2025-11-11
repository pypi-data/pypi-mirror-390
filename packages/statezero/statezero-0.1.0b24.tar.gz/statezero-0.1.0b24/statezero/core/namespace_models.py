"""
Database models for namespace-based subscription tracking.

These models are ORM-agnostic interfaces that should be implemented
by each ORM adapter (Django, SQLAlchemy, etc.)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AbstractSocketConnection(ABC):
    """
    Tracks active WebSocket connections.

    When a client connects via WebSocket, a connection record is created.
    When they disconnect, the record is deleted along with all their subscriptions.
    """

    @abstractmethod
    def get_socket_id(self) -> str:
        """Unique identifier for this socket connection (from Pusher/etc)"""
        pass

    @abstractmethod
    def get_user(self) -> Any:
        """The authenticated user for this connection (optional)"""
        pass

    @abstractmethod
    def get_connected_at(self):
        """Timestamp when connection was established"""
        pass


class AbstractNamespaceSubscription(ABC):
    """
    Tracks which namespaces a client is subscribed to.

    When a client queries data with a namespace (e.g., room_id=5),
    they subscribe to that namespace to receive relevant events.
    """

    @abstractmethod
    def get_connection(self) -> AbstractSocketConnection:
        """The socket connection this subscription belongs to"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Model name like 'Message' or 'django_app.Message'"""
        pass

    @abstractmethod
    def get_namespace(self) -> Dict[str, Any]:
        """
        The namespace filter.
        Examples:
        - {'room_id': 5}
        - {'room__organization_id': 10, 'type__in': ['user', 'system']}
        """
        pass

    @abstractmethod
    def get_created_at(self):
        """Timestamp when subscription was created"""
        pass
