"""
Django implementation of namespace subscription models.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


User = get_user_model()


class SocketConnection(models.Model):
    """
    Tracks active WebSocket connections.

    Automatically cleaned up on disconnect.
    """
    socket_id = models.CharField(max_length=255, unique=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    connected_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'statezero'
        db_table = 'statezero_socket_connection'
        indexes = [
            models.Index(fields=['socket_id']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        user_str = f"user:{self.user.id}" if self.user else "anonymous"
        return f"SocketConnection({self.socket_id}, {user_str})"


class NamespaceSubscription(models.Model):
    """
    Tracks which namespaces each socket connection is subscribed to.

    When deleted on disconnect, all subscriptions are automatically removed.
    """
    connection = models.ForeignKey(
        SocketConnection,
        on_delete=models.CASCADE,
        related_name='subscriptions'
    )
    model_name = models.CharField(max_length=255, db_index=True)
    namespace = models.JSONField()  # e.g., {'room_id': 5}
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'statezero'
        db_table = 'statezero_namespace_subscription'
        indexes = [
            models.Index(fields=['model_name']),
            models.Index(fields=['connection']),
        ]
        # Prevent duplicate subscriptions
        unique_together = [['connection', 'model_name', 'namespace']]

    def __str__(self):
        return f"Subscription({self.connection.socket_id}, {self.model_name}, {self.namespace})"
