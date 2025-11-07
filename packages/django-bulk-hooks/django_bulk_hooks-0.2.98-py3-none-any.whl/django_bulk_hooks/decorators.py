import inspect
import logging
from functools import wraps

from django.core.exceptions import FieldDoesNotExist

from django_bulk_hooks.enums import DEFAULT_PRIORITY
from django_bulk_hooks.registry import register_hook

logger = logging.getLogger(__name__)


def hook(event, *, model, condition=None, priority=DEFAULT_PRIORITY):
    """
    Decorator to annotate a method with multiple hooks hook registrations.
    If no priority is provided, uses Priority.NORMAL (50).
    """

    def decorator(fn):
        if not hasattr(fn, "hooks_hooks"):
            fn.hooks_hooks = []
        fn.hooks_hooks.append((model, event, condition, priority))
        return fn

    return decorator


def select_related(*related_fields):
    """
    Decorator that preloads related fields in-place on `new_records`, before the hook logic runs.

    - Works with instance methods (resolves `self`)
    - Avoids replacing model instances
    - Populates Django's relation cache to avoid extra queries
    - Uses Django ORM __ notation for related field paths (e.g., 'parent__parent__value')
    """

    def decorator(func):
        sig = inspect.signature(func)

        def preload_related(records, *, model_cls=None, skip_fields=None):
            if not isinstance(records, list):
                raise TypeError(
                    f"@select_related expects a list of model instances, got {type(records)}",
                )

            if not records:
                return

            if model_cls is None:
                model_cls = records[0].__class__

            if skip_fields is None:
                skip_fields = set()

            # Validate field notation upfront
            for field in related_fields:
                if "." in field:
                    raise ValueError(
                        f"Invalid field notation '{field}'. Use Django ORM __ notation (e.g., 'parent__field')",
                    )

            direct_relation_fields = {}
            validated_fields = []

            for field in related_fields:
                if "__" in field:
                    validated_fields.append(field)
                    continue

                try:
                    if hasattr(model_cls, "_meta"):
                        relation_field = model_cls._meta.get_field(field)
                    else:
                        continue
                except (FieldDoesNotExist, AttributeError):
                    continue

                if relation_field.is_relation and not relation_field.many_to_many and not relation_field.one_to_many:
                    validated_fields.append(field)
                    direct_relation_fields[field] = relation_field

            unsaved_related_ids_by_field = {field: set() for field in direct_relation_fields}

            saved_ids_to_fetch = []
            for obj in records:
                if obj.pk is not None:
                    needs_fetch = False
                    if hasattr(obj, "_state") and hasattr(obj._state, "fields_cache"):
                        try:
                            needs_fetch = any(field not in obj._state.fields_cache for field in related_fields)
                        except (TypeError, AttributeError):
                            needs_fetch = True
                    else:
                        needs_fetch = True

                    if needs_fetch:
                        saved_ids_to_fetch.append(obj.pk)
                    continue

                fields_cache = None
                if hasattr(obj, "_state") and hasattr(obj._state, "fields_cache"):
                    fields_cache = obj._state.fields_cache

                for field_name, relation_field in direct_relation_fields.items():
                    if fields_cache is not None and field_name in fields_cache:
                        continue

                    try:
                        related_id = getattr(obj, relation_field.get_attname(), None)
                    except AttributeError:
                        continue

                    if related_id is not None:
                        unsaved_related_ids_by_field[field_name].add(related_id)

            fetched_saved = {}
            if saved_ids_to_fetch and validated_fields:
                base_manager = getattr(model_cls, "_base_manager", None)
                if base_manager is not None:
                    try:
                        fetched_saved = base_manager.select_related(
                            *validated_fields,
                        ).in_bulk(saved_ids_to_fetch)
                    except Exception:
                        fetched_saved = {}

            fetched_unsaved_by_field = {field: {} for field in direct_relation_fields}

            for field_name, relation_field in direct_relation_fields.items():
                related_ids = unsaved_related_ids_by_field[field_name]
                if not related_ids:
                    continue

                related_model = getattr(relation_field.remote_field, "model", None)
                if related_model is None:
                    continue

                manager = getattr(related_model, "_base_manager", None)
                if manager is None:
                    continue

                try:
                    fetched_unsaved_by_field[field_name] = manager.in_bulk(related_ids)
                except Exception:
                    fetched_unsaved_by_field[field_name] = {}

            for obj in records:
                fields_cache = None
                if hasattr(obj, "_state") and hasattr(obj._state, "fields_cache"):
                    fields_cache = obj._state.fields_cache

                if obj.pk is not None:
                    preloaded = fetched_saved.get(obj.pk)
                    if not preloaded:
                        continue

                    for field in related_fields:
                        # Skip preloading if this relationship conflicts with FK field being updated
                        if field in skip_fields:
                            continue

                        if fields_cache is not None and field in fields_cache:
                            continue

                        relation_field = direct_relation_fields.get(field)
                        if relation_field is None and "__" not in field:
                            continue

                        try:
                            rel_obj = getattr(preloaded, field)
                        except AttributeError:
                            continue

                        setattr(obj, field, rel_obj)
                        if fields_cache is not None:
                            fields_cache[field] = rel_obj
                    continue

                for field_name, relation_field in direct_relation_fields.items():
                    # Skip preloading if this relationship conflicts with FK field being updated
                    if field_name in skip_fields:
                        continue

                    if fields_cache is not None and field_name in fields_cache:
                        continue

                    try:
                        related_id = getattr(obj, relation_field.get_attname(), None)
                    except AttributeError:
                        continue

                    if related_id is None:
                        continue

                    rel_obj = fetched_unsaved_by_field[field_name].get(related_id)
                    if rel_obj is None:
                        continue

                    setattr(obj, field_name, rel_obj)
                    if fields_cache is not None:
                        fields_cache[field_name] = rel_obj

        def preload_with_skip_fields(records, *, model_cls=None, skip_fields=None):
            """Wrapper that applies skip_fields logic to the preload function"""
            if skip_fields is None:
                skip_fields = set()
            return preload_related(records, model_cls=model_cls, skip_fields=skip_fields)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            bound.apply_defaults()

            if "new_records" not in bound.arguments:
                raise TypeError(
                    "@preload_related requires a 'new_records' argument in the decorated function",
                )

            new_records = bound.arguments["new_records"]

            if not isinstance(new_records, list):
                raise TypeError(
                    f"@select_related expects a list of model instances, got {type(new_records)}",
                )

            if not new_records:
                # Empty list, nothing to preload
                return func(*args, **kwargs)

            # Validate field notation upfront (same as in preload_related)
            for field in related_fields:
                if "." in field:
                    raise ValueError(
                        f"Invalid field notation '{field}'. Use Django ORM __ notation (e.g., 'parent__field')",
                    )

            # Don't preload here - let the dispatcher handle it
            # The dispatcher will call the preload function with skip_fields
            return func(*args, **kwargs)

        wrapper._select_related_preload = preload_with_skip_fields
        wrapper._select_related_fields = related_fields

        return wrapper

    return decorator


def bulk_hook(model_cls, event, when=None, priority=None):
    """
    Decorator to register a bulk hook for a model.

    Args:
        model_cls: The model class to hook into
        event: The event to hook into (e.g., BEFORE_UPDATE, AFTER_UPDATE)
        when: Optional condition for when the hook should run
        priority: Optional priority for hook execution order
    """

    def decorator(func):
        # Create a simple handler class for the function
        class FunctionHandler:
            def __init__(self):
                self.func = func

            def handle(self, changeset=None, new_records=None, old_records=None, **kwargs):
                # Support both old and new hook signatures for backward compatibility
                # Old signature: def hook(self, new_records, old_records, **kwargs)
                # New signature: def hook(self, changeset, new_records, old_records, **kwargs)

                # Check function signature to determine which format to use
                import inspect

                sig = inspect.signature(func)
                params = list(sig.parameters.keys())

                if "changeset" in params:
                    # New signature with changeset
                    return self.func(changeset, new_records, old_records, **kwargs)
                # Old signature without changeset
                # Only pass changeset in kwargs if the function accepts **kwargs
                if "kwargs" in params or any(param.startswith("**") for param in sig.parameters):
                    kwargs["changeset"] = changeset
                    return self.func(new_records, old_records, **kwargs)
                # Function doesn't accept **kwargs, just call with positional args
                return self.func(new_records, old_records)

        # Register the hook using the registry
        register_hook(
            model=model_cls,
            event=event,
            handler_cls=FunctionHandler,
            method_name="handle",
            condition=when,
            priority=priority or DEFAULT_PRIORITY,
        )

        # Set attribute to indicate the function has been registered as a bulk hook
        func._bulk_hook_registered = True

        return func

    return decorator
