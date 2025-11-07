import logging

from django_bulk_hooks.changeset import ChangeSet
from django_bulk_hooks.changeset import RecordChange
from django_bulk_hooks.constants import DEFAULT_BULK_UPDATE_BATCH_SIZE
from django_bulk_hooks.dispatcher import HookDispatcher
from django_bulk_hooks.dispatcher import get_dispatcher
from django_bulk_hooks.factory import clear_hook_factories
from django_bulk_hooks.factory import configure_hook_container
from django_bulk_hooks.factory import configure_nested_container
from django_bulk_hooks.factory import create_hook_instance
from django_bulk_hooks.factory import is_container_configured
from django_bulk_hooks.factory import set_default_hook_factory
from django_bulk_hooks.factory import set_hook_factory
from django_bulk_hooks.handler import Hook as HookClass
from django_bulk_hooks.helpers import build_changeset_for_create
from django_bulk_hooks.helpers import build_changeset_for_delete
from django_bulk_hooks.helpers import build_changeset_for_update
from django_bulk_hooks.helpers import dispatch_hooks_for_operation
from django_bulk_hooks.manager import BulkHookManager
from django_bulk_hooks.operations import BulkExecutor

# Service layer (NEW architecture)
from django_bulk_hooks.operations import BulkOperationCoordinator
from django_bulk_hooks.operations import ModelAnalyzer
from django_bulk_hooks.operations import MTIHandler

__all__ = [
    "BulkHookManager",
    "HookClass",
    "set_hook_factory",
    "set_default_hook_factory",
    "configure_hook_container",
    "configure_nested_container",
    "clear_hook_factories",
    "create_hook_instance",
    "is_container_configured",
    "DEFAULT_BULK_UPDATE_BATCH_SIZE",
    # Dispatcher-centric architecture
    "ChangeSet",
    "RecordChange",
    "get_dispatcher",
    "HookDispatcher",
    "build_changeset_for_create",
    "build_changeset_for_update",
    "build_changeset_for_delete",
    "dispatch_hooks_for_operation",
    # Service layer (composition-based architecture)
    "BulkOperationCoordinator",
    "ModelAnalyzer",
    "BulkExecutor",
    "MTIHandler",
]
