"""
Views for namespace subscription management.
"""
import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from statezero.adaptors.django.namespace_models import (
    SocketConnection,
    NamespaceSubscription,
)
from statezero.adaptors.django.exception_handler import explicit_exception_handler
from statezero.core.namespace_utils import extract_namespace_from_filter

logger = logging.getLogger(__name__)


class NamespaceSubscribeView(APIView):
    """
    Allow clients to subscribe to namespaces for selective event notifications.
    """

    def post(self, request):
        """
        Subscribe to a namespace.

        Expected payload:
        {
            "socket_id": "socket-123",
            "model_name": "django_app.Message",
            "ast": {
                "query": {
                    "type": "read",
                    "filter": {
                        "type": "filter",
                        "conditions": {"room_id": 5, "created_at__gte": "2024-01-01"}
                    }
                }
            }
        }

        Or simplified without AST wrapper:
        {
            "socket_id": "socket-123",
            "model_name": "django_app.Message",
            "filter": {"room_id": 5, "created_at__gte": "2024-01-01"}
        }
        """
        try:
            socket_id = request.data.get('socket_id')
            model_name = request.data.get('model_name')
            ast = request.data.get('ast')
            query_filter = request.data.get('filter')

            if not socket_id:
                return Response(
                    {"error": "socket_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not model_name:
                return Response(
                    {"error": "model_name is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract filter from AST if provided
            if ast and not query_filter:
                query = ast.get('query', {})
                filter_node = query.get('filter', {})
                if filter_node and filter_node.get('type') == 'filter':
                    query_filter = filter_node.get('conditions', {})

            # Extract namespace from filter
            if not query_filter:
                return Response(
                    {"error": "ast or filter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            namespace = extract_namespace_from_filter(query_filter)

            # Import namespace hash utility
            from statezero.core.namespace_utils import get_namespace_hash
            namespace_hash = get_namespace_hash(namespace)

            # Get or create socket connection
            connection, created = SocketConnection.objects.get_or_create(
                socket_id=socket_id,
                defaults={'user': request.user if request.user.is_authenticated else None}
            )

            if created:
                logger.info(f"Created new socket connection: {socket_id}")

            # Create or update subscription
            subscription, created = NamespaceSubscription.objects.get_or_create(
                connection=connection,
                model_name=model_name,
                namespace=namespace
            )

            if created:
                logger.info(
                    f"Created subscription for {socket_id} to {model_name} namespace {namespace}"
                )

            return Response({
                "success": True,
                "socket_id": socket_id,
                "model_name": model_name,
                "namespace": namespace,
                "namespace_hash": namespace_hash,
                "channel": f"{model_name}:{namespace_hash}",
                "created": created
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return explicit_exception_handler(e)


class NamespaceUnsubscribeView(APIView):
    """
    Allow clients to unsubscribe from namespaces.
    """

    def post(self, request):
        """
        Unsubscribe from a namespace.

        Expected payload:
        {
            "socket_id": "socket-123",
            "model_name": "django_app.Message",
            "ast": {...}  # or "filter": {...}
        }
        """
        try:
            socket_id = request.data.get('socket_id')
            model_name = request.data.get('model_name')
            ast = request.data.get('ast')
            query_filter = request.data.get('filter')

            if not socket_id or not model_name:
                return Response(
                    {"error": "socket_id and model_name are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Extract filter from AST if provided
            if ast and not query_filter:
                query = ast.get('query', {})
                filter_node = query.get('filter', {})
                if filter_node and filter_node.get('type') == 'filter':
                    query_filter = filter_node.get('conditions', {})

            # Extract namespace from filter
            if not query_filter:
                return Response(
                    {"error": "ast or filter is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            namespace = extract_namespace_from_filter(query_filter)

            # Find and delete the subscription
            deleted_count, _ = NamespaceSubscription.objects.filter(
                connection__socket_id=socket_id,
                model_name=model_name,
                namespace=namespace
            ).delete()

            if deleted_count > 0:
                logger.info(
                    f"Unsubscribed {socket_id} from {model_name} namespace {namespace}"
                )

            return Response({
                "success": True,
                "deleted": deleted_count > 0
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return explicit_exception_handler(e)


class PusherWebhookView(APIView):
    """
    Handle Pusher webhook events for connection lifecycle.

    This is called by Pusher when events occur (client disconnect, etc).
    Configure in Pusher dashboard: Settings > Webhooks
    """

    # Pusher webhooks don't need authentication (they use webhook signature)
    permission_classes = []

    def post(self, request):
        """
        Handle Pusher webhook events.

        Pusher sends events like:
        {
            "time_ms": 1234567890,
            "events": [
                {
                    "name": "channel_vacated",
                    "channel": "presence-room-5",
                    "socket_id": "socket-123.456"
                }
            ]
        }
        """
        try:
            # Validate webhook signature (optional but recommended)
            if not self._validate_webhook(request):
                logger.warning("Invalid Pusher webhook signature")
                return Response(
                    {"error": "Invalid signature"},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            events = request.data.get('events', [])

            for event in events:
                event_name = event.get('name')

                # Handle different event types
                if event_name == 'channel_vacated':
                    # A channel has been vacated (last member left)
                    self._handle_channel_vacated(event)

                elif event_name == 'member_removed':
                    # A member left a presence channel
                    self._handle_member_removed(event)

                elif event_name == 'member_added':
                    # A member joined a presence channel
                    self._handle_member_added(event)

            return Response({"success": True}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"Error handling Pusher webhook: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _validate_webhook(self, request):
        """
        Validate Pusher webhook signature.

        Pusher signs webhooks with your app secret.
        See: https://pusher.com/docs/channels/server_api/webhooks/#authentication
        """
        from django.conf import settings
        import hmac
        import hashlib

        # Get Pusher secret from STATEZERO_PUSHER settings
        pusher_config = getattr(settings, 'STATEZERO_PUSHER', {})
        webhook_secret = pusher_config.get('SECRET')

        if not webhook_secret:
            # If no webhook secret configured, skip validation (dev mode)
            logger.warning("No STATEZERO_PUSHER['SECRET'] configured, skipping webhook validation")
            return True

        # Get signature from header
        signature = request.headers.get('X-Pusher-Signature')
        if not signature:
            return False

        # Compute expected signature
        body = request.body.decode('utf-8')
        expected = hmac.new(
            webhook_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected)

    def _handle_channel_vacated(self, event):
        """Handle channel_vacated event."""
        channel = event.get('channel')
        logger.info(f"Channel vacated: {channel}")
        # Channel is empty, but we track per-socket, not per-channel

    def _handle_member_removed(self, event):
        """
        Handle member_removed event.

        This is the key event for cleanup - when a user disconnects.
        """
        user_id = event.get('user_id')  # From presence channel
        socket_id = event.get('socket_id')  # May not be present in all events

        if socket_id:
            # Clean up by socket_id (most reliable)
            deleted_count, _ = SocketConnection.objects.filter(
                socket_id=socket_id
            ).delete()

            if deleted_count > 0:
                logger.info(
                    f"Cleaned up socket {socket_id} on member_removed event "
                    f"({deleted_count} connections deleted)"
                )

    def _handle_member_added(self, event):
        """Handle member_added event."""
        user_id = event.get('user_id')
        socket_id = event.get('socket_id')
        logger.debug(f"Member added: user={user_id}, socket={socket_id}")
        # We handle connection creation in NamespaceSubscribeView


class SocketDisconnectView(APIView):
    """
    Manual disconnect endpoint (for testing or explicit cleanup).

    In production, use PusherWebhookView which is called automatically.
    """

    def post(self, request):
        """
        Manually clean up all subscriptions for a socket.

        Expected payload:
        {
            "socket_id": "socket-123"
        }
        """
        try:
            socket_id = request.data.get('socket_id')

            if not socket_id:
                return Response(
                    {"error": "socket_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Delete the connection (cascades to subscriptions)
            deleted_count, _ = SocketConnection.objects.filter(
                socket_id=socket_id
            ).delete()

            if deleted_count > 0:
                logger.info(f"Manually cleaned up socket connection: {socket_id}")

            return Response({
                "success": True,
                "deleted": deleted_count > 0
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return explicit_exception_handler(e)
