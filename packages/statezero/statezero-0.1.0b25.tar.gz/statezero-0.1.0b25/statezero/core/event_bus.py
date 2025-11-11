from statezero.core.context_storage import current_operation_id, current_canonical_id
import logging
from typing import Any, Type, Union, List
from fastapi.encoders import jsonable_encoder
from uuid import uuid4

from statezero.core.interfaces import AbstractEventEmitter, AbstractORMProvider
from statezero.core.types import ActionType, ORMModel, ORMQuerySet

logger = logging.getLogger(__name__)


class EventBus:
    def __init__(
        self,
        broadcast_emitter: AbstractEventEmitter,
        orm_provider: AbstractORMProvider = None,
    ) -> None:
        """
        Initialize the EventBus with a broadcast emitter.

        Parameters:
        -----------
        broadcast_emitter: AbstractEventEmitter
            Emitter responsible for broadcasting events to clients
        orm_provider : AbstractORMProvider
            The orm provider to be used to get the default namespace for events
        """
        self.broadcast_emitter: AbstractEventEmitter = broadcast_emitter
        self.orm_provider = orm_provider

    def set_registry(self, registry):
        """Set the model registry after initialization if needed."""
        from statezero.core.config import Registry

        self.registry: Registry = registry

    def emit_event(self, action_type: ActionType, instance: Any) -> None:
        """
        Emit an event for a model instance to appropriate namespaces.

        Uses namespace subscriptions to selectively notify only interested clients.

        Parameters:
        -----------
        action_type: ActionType
            The type of event (CREATE, UPDATE, DELETE)
        instance: Any
            The model instance that triggered the event
        """
        # Unused actions, no need to broadcast
        if action_type in (ActionType.PRE_DELETE, ActionType.PRE_UPDATE):
            return

        if not self.broadcast_emitter or not self.orm_provider:
            return

        try:
            from django.core.cache import cache
            from statezero.core.namespace_utils import (
                should_notify_namespace,
                update_namespace_cache,
                get_namespace_hash,
            )

            # Get model class and name
            model_class = instance.__class__
            model_name = self.orm_provider.get_model_name(instance)
            pk_field_name = instance._meta.pk.name
            pk_value = instance.pk

            # Get all active namespace subscriptions for this model
            try:
                from statezero.adaptors.django.namespace_models import NamespaceSubscription

                subscriptions = NamespaceSubscription.objects.filter(
                    model_name=model_name
                ).values('namespace').distinct()

                # Process each unique namespace
                for sub in subscriptions:
                    namespace_dict = sub['namespace']
                    namespace_hash = get_namespace_hash(namespace_dict)
                    cache_key = f"namespace_pks:{model_name}:{namespace_hash}"

                    # Get cached PKs for this namespace
                    cached_pks = cache.get(cache_key, set())

                    # Check if this namespace should be notified
                    if should_notify_namespace(instance, namespace_dict, cached_pks):
                        # Generate a unique canonical_id for this namespace
                        namespace_canonical_id = str(uuid4())

                        # Create event data
                        data = {
                            "event": action_type.value,
                            "model": model_name,
                            "operation_id": current_operation_id.get(),
                            "canonical_id": namespace_canonical_id,
                            "instances": [pk_value],
                            "pk_field_name": pk_field_name,
                            "namespace": namespace_dict,
                        }

                        # Emit to this specific namespace
                        namespace_channel = f"{model_name}:{namespace_hash}"
                        try:
                            self.broadcast_emitter.emit(
                                namespace_channel, action_type, jsonable_encoder(data)
                            )
                            logger.debug(
                                "Emitted %s event for %s to namespace %s",
                                action_type.value,
                                model_name,
                                namespace_dict
                            )
                        except Exception as e:
                            logger.exception(
                                "Error emitting to namespace %s: %s",
                                namespace_dict,
                                e,
                            )

                        # Update the namespace PK cache
                        update_namespace_cache(cache, model_name, namespace_dict, instance)

            except ImportError:
                # Namespace models not available, fall back to default behavior
                logger.debug("Namespace models not available, using default broadcast")
                default_namespace = self.orm_provider.get_model_name(model_class)
                data = {
                    "event": action_type.value,
                    "model": model_name,
                    "operation_id": current_operation_id.get(),
                    "canonical_id": current_canonical_id.get(),
                    "instances": [pk_value],
                    "pk_field_name": pk_field_name,
                }
                self.broadcast_emitter.emit(
                    default_namespace, action_type, jsonable_encoder(data)
                )

        except Exception as e:
            logger.exception(
                "Error in broadcast emitter dispatching event %s for instance %s: %s",
                action_type,
                instance,
                e,
            )

    def emit_bulk_event(
        self, action_type: ActionType, instances: Union[List[Any], ORMQuerySet]
    ) -> None:
        """
        Emit a bulk event for multiple instances.

        Parameters:
        -----------
        action_type: ActionType
            The type of bulk event (e.g., BULK_UPDATE, BULK_DELETE)
        instances: Union[List[Any], ORMQuerySet]
            The instances affected by the bulk operation (can be a list or queryset)
        """
        # Convert QuerySet to list if needed
        if hasattr(instances, "all") and callable(getattr(instances, "all")):
            instances = list(instances)

        if not instances:
            return

        # Get the model class from the first instance
        first_instance = instances[0]
        model_class = first_instance.__class__

        if not self.broadcast_emitter or not self.orm_provider:
            return

        try:
            # Get model config
            model_config = None
            if hasattr(self, "registry"):
                try:
                    model_config = self.registry.get_config(model_class)
                except (ValueError, AttributeError):
                    pass

            default_namespace = self.orm_provider.get_model_name(model_class)

            # Create payload data from instances
            model_name = self.orm_provider.get_model_name(first_instance)
            pk_field_name = first_instance._meta.pk.name
            pks = [instance.pk for instance in instances]

            data = {
                "event": action_type.value,
                "model": model_name,
                "operation_id": current_operation_id.get(),
                "canonical_id": current_canonical_id.get(),
                "instances": pks,
                "pk_field_name": pk_field_name,
            }

            # Create a dictionary to group instances by namespace
            namespaces = ["global", default_namespace]

            for namespace in namespaces:
                try:
                    # Emit data to this namespace
                    self.broadcast_emitter.emit(
                        namespace, action_type, jsonable_encoder(data)
                    )
                except Exception as e:
                    logger.exception(
                        "Error emitting bulk event to namespace %s: %s",
                        namespace,
                        e,
                    )
        except Exception as e:
            logger.exception(
                "Error in broadcast emitter dispatching bulk event %s: %s",
                action_type,
                e,
            )
