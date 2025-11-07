"""
HookDispatcher: Single execution path for all hooks.

Provides deterministic, priority-ordered hook execution,
similar to Salesforce's hook framework.
"""

import logging

logger = logging.getLogger(__name__)


class HookDispatcher:
    """
    Single execution path for all hooks.

    Responsibilities:
    - Execute hooks in priority order
    - Filter records based on conditions
    - Provide ChangeSet context to hooks
    - Fail-fast error propagation
    - Manage complete operation lifecycle (VALIDATE, BEFORE, AFTER)
    """

    def __init__(self, registry):
        """
        Initialize the dispatcher.

        Args:
            registry: The hook registry (provides get_hooks method)
        """
        self.registry = registry

    def execute_operation_with_hooks(
        self,
        changeset,
        operation,
        event_prefix,
        bypass_hooks=False,
    ):
        """
        Execute operation with full hook lifecycle.

        This is the high-level method that coordinates the complete lifecycle:
        1. VALIDATE_{event}
        2. BEFORE_{event}
        3. Actual operation
        4. AFTER_{event}

        Args:
            changeset: ChangeSet for the operation
            operation: Callable that performs the actual DB operation
            event_prefix: 'create', 'update', or 'delete'
            bypass_hooks: Skip all hooks if True

        Returns:
            Result of operation
        """
        if bypass_hooks:
            return operation()

        # VALIDATE phase
        self.dispatch(changeset, f"validate_{event_prefix}", bypass_hooks=False)

        # BEFORE phase
        self.dispatch(changeset, f"before_{event_prefix}", bypass_hooks=False)

        # Execute the actual operation
        result = operation()

        # AFTER phase - use result if operation returns modified data
        if result and isinstance(result, list) and event_prefix == "create":
            # For create, rebuild changeset with assigned PKs
            from django_bulk_hooks.helpers import build_changeset_for_create

            changeset = build_changeset_for_create(changeset.model_cls, result)

        self.dispatch(changeset, f"after_{event_prefix}", bypass_hooks=False)

        return result

    def dispatch(self, changeset, event, bypass_hooks=False):
        """
        Dispatch hooks for a changeset with deterministic ordering.

        This is the single execution path for ALL hooks in the system.

        Args:
            changeset: ChangeSet instance with record changes
            event: Event name (e.g., 'after_update', 'before_create')
            bypass_hooks: If True, skip all hook execution

        Raises:
            Exception: Any exception raised by a hook (fails fast)
            RecursionError: If hooks create an infinite loop (Python's built-in limit)
        """
        if bypass_hooks:
            return

        # Get hooks sorted by priority (deterministic order)
        hooks = self.registry.get_hooks(changeset.model_cls, event)

        logger.debug(f"🧵 DISPATCH: changeset.model_cls={changeset.model_cls.__name__}, event={event}")
        logger.debug(
            f"🎣 HOOKS_FOUND: {len(hooks)} hooks for {changeset.model_cls.__name__}.{event}: {[f'{h[0].__name__}.{h[1]}' for h in hooks]}"
        )

        if not hooks:
            return

        # Create an operation key that includes the changeset model to avoid
        # deduplicating hooks across different operations on the same records
        # This prevents the same hook from executing multiple times for MTI inheritance chains
        # but allows different operations on the same records to execute their hooks
        record_ids = set()
        for change in changeset.changes:
            if change.new_record and change.new_record.pk:
                record_ids.add(change.new_record.pk)
            if change.old_record and change.old_record.pk:
                record_ids.add(change.old_record.pk)

        # Sort record IDs safely (handle Mock objects and other non-comparable types)
        try:
            sorted_record_ids = tuple(sorted(record_ids, key=lambda x: str(x)))
        except (TypeError, AttributeError):
            # Fallback for non-comparable objects (like Mock objects in tests)
            sorted_record_ids = tuple(record_ids)

        # Include changeset model and operation details to make the key more specific
        operation_meta = getattr(changeset, "operation_meta", {}) or {}
        operation_type = getattr(changeset, "operation_type", "unknown")

        # Include update_kwargs if present to distinguish different queryset operations
        update_kwargs = operation_meta.get("update_kwargs", {})
        if update_kwargs:
            try:
                # Convert to a hashable representation
                update_kwargs_key = tuple(sorted((k, str(v)) for k, v in update_kwargs.items()))
            except (TypeError, AttributeError):
                # Fallback if values are not convertible to string
                update_kwargs_key = tuple(sorted(update_kwargs.keys()))
        else:
            update_kwargs_key = ()

        operation_key = (event, changeset.model_cls.__name__, operation_type, sorted_record_ids, update_kwargs_key)

        # Track executed hooks to prevent duplicates in MTI inheritance chains
        if not hasattr(self, "_executed_hooks"):
            self._executed_hooks = set()

        # Filter out hooks that have already been executed for this operation
        unique_hooks = []
        skipped_hooks = []
        for handler_cls, method_name, condition, priority in hooks:
            hook_key = (handler_cls, method_name, operation_key)
            if hook_key not in self._executed_hooks:
                unique_hooks.append((handler_cls, method_name, condition, priority))
                self._executed_hooks.add(hook_key)
            else:
                skipped_hooks.append((handler_cls.__name__, method_name))

        # Debug logging for hook deduplication
        if skipped_hooks:
            logger.debug(f"⏭️ SKIPPED_DUPS: {len(skipped_hooks)} duplicate hooks: {[f'{cls}.{method}' for cls, method in skipped_hooks]}")

        if unique_hooks:
            logger.debug(f"✅ EXECUTING_UNIQUE: {len(unique_hooks)} unique hooks: {[f'{h[0].__name__}.{h[1]}' for h in unique_hooks]}")

        if not unique_hooks:
            return

        # Execute hooks in priority order
        logger.info(f"🔥 HOOKS: Executing {len(unique_hooks)} hooks for {changeset.model_cls.__name__}.{event}")
        for handler_cls, method_name, condition, priority in unique_hooks:
            logger.info(f"  → {handler_cls.__name__}.{method_name} (priority={priority})")
            self._execute_hook(handler_cls, method_name, condition, changeset, event)

    def _reset_executed_hooks(self):
        """Reset the executed hooks tracking for a new operation."""
        self._executed_hooks = set()

    def _execute_hook(self, handler_cls, method_name, condition, changeset, event):
        """
        Execute a single hook with condition checking.

        Args:
            handler_cls: The hook handler class
            method_name: Name of the method to call
            condition: Optional condition to filter records
            changeset: ChangeSet with all record changes
            event: The hook event (e.g., 'before_create')
        """
        # Use DI factory to create handler instance EARLY to access method decorators
        from django_bulk_hooks.factory import create_hook_instance

        handler = create_hook_instance(handler_cls)
        method = getattr(handler, method_name)

        # PRELOAD @select_related RELATIONSHIPS BEFORE CONDITION EVALUATION
        # This ensures both conditions and hook methods have access to preloaded relationships

        # Check if method has @select_related decorator
        preload_func = getattr(method, "_select_related_preload", None)
        if preload_func:
            # Preload relationships to prevent N+1 queries in both conditions and hook methods
            try:
                model_cls_override = getattr(handler, "model_cls", None)

                # Get FK fields being updated to avoid preloading conflicting relationships
                skip_fields = changeset.operation_meta.get("fk_fields_being_updated", set())

                # Preload for new_records (needed for condition evaluation and hook execution)
                if changeset.new_records:
                    preload_func(
                        changeset.new_records,
                        model_cls=model_cls_override,
                        skip_fields=skip_fields,
                    )

                # Also preload for old_records (for conditions that check previous values)
                if changeset.old_records:
                    preload_func(
                        changeset.old_records,
                        model_cls=model_cls_override,
                        skip_fields=skip_fields,
                    )

                # Mark that relationships have been preloaded to avoid duplicate condition preloading
                changeset.operation_meta["relationships_preloaded"] = True
                logger.debug(f"🔗 @select_related: Preloaded relationships for {handler_cls.__name__}.{method_name}")

            except Exception as e:
                logger.warning(f"Failed to preload relationships for {handler_cls.__name__}.{method_name}: {e}")

        # SPECIAL HANDLING: Explicit @select_related support for BEFORE_CREATE hooks
        # (This can stay for additional BEFORE_CREATE-specific logic if needed)
        select_related_fields = getattr(method, "_select_related_fields", None)
        if select_related_fields and event == "before_create" and changeset.new_records:
            self._preload_select_related_for_before_create(changeset, select_related_fields)

        # NOW condition evaluation is safe - relationships are preloaded
        if condition:
            # Skip per-hook preloading if relationships were already preloaded upfront
            if not changeset.operation_meta.get("relationships_preloaded", False):
                condition_relationships = self._extract_condition_relationships(condition, changeset.model_cls)
                logger.info(
                    f"🔍 CONDITION: {handler_cls.__name__}.{method_name} has condition, extracted relationships: {condition_relationships}"
                )
                if condition_relationships:
                    logger.info(f"🔗 PRELOADING: Preloading condition relationships for {len(changeset.changes)} records")
                    self._preload_condition_relationships(changeset, condition_relationships)
            else:
                logger.debug(f"🔍 CONDITION: {handler_cls.__name__}.{method_name} has condition (relationships already preloaded)")

        # Filter records based on condition (now safe - relationships are preloaded)
        if condition:
            logger.info(f"⚡ EVALUATING: Checking condition for {handler_cls.__name__}.{method_name} on {len(changeset.changes)} records")
            filtered_changes = [change for change in changeset.changes if condition.check(change.new_record, change.old_record)]
            logger.info(f"✅ CONDITION: {len(filtered_changes)}/{len(changeset.changes)} records passed condition filter")

            if not filtered_changes:
                # No records match condition, skip this hook
                return

            # Create filtered changeset
            from django_bulk_hooks.changeset import ChangeSet

            filtered_changeset = ChangeSet(
                changeset.model_cls,
                filtered_changes,
                changeset.operation_type,
                changeset.operation_meta,
            )
        else:
            # No condition, use full changeset
            filtered_changeset = changeset

        # Execute hook with ChangeSet
        #
        # ARCHITECTURE NOTE: Hook Contract
        # ====================================
        # All hooks must accept **kwargs for forward compatibility.
        # We pass: changeset, new_records, old_records
        #
        # Old hooks that don't use changeset: def hook(self, new_records, old_records, **kwargs)
        # New hooks that do use changeset:    def hook(self, changeset, new_records, old_records, **kwargs)
        #
        # This is standard Python framework design (see Django signals, Flask hooks, etc.)
        logger.info(f"    🚀 Executing: {handler_cls.__name__}.{method_name}")
        try:
            method(
                changeset=filtered_changeset,
                new_records=filtered_changeset.new_records,
                old_records=filtered_changeset.old_records,
            )
            logger.info(f"    ✅ Completed: {handler_cls.__name__}.{method_name}")
        except Exception as e:
            # Fail-fast: re-raise to rollback transaction
            logger.error(
                f"Hook {handler_cls.__name__}.{method_name} failed: {e}",
                exc_info=True,
            )
            raise

    def _extract_condition_relationships(self, condition, model_cls):
        """
        Extract relationship paths that a condition might access.

        Args:
            condition: HookCondition instance
            model_cls: The model class

        Returns:
            set: Set of relationship field names to preload
        """
        relationships = set()

        # Guard against Mock objects and non-condition objects
        if not hasattr(condition, "check") or hasattr(condition, "_mock_name"):
            return relationships

        # Handle different condition types
        if hasattr(condition, "field"):
            # Extract relationships from field path (e.g., "status__value" -> "status")
            field_path = condition.field
            if isinstance(field_path, str):
                if "__" in field_path:
                    # Take the first part before __ (the relationship to preload)
                    rel_field = field_path.split("__")[0]

                    # Normalize FK field names: business_id -> business
                    if rel_field.endswith("_id"):
                        potential_field_name = rel_field[:-3]  # Remove '_id'
                        if self._is_relationship_field(model_cls, potential_field_name):
                            rel_field = potential_field_name

                    relationships.add(rel_field)
                else:
                    # Handle single field (no __ notation)
                    rel_field = field_path

                    # Normalize FK field names: business_id -> business
                    if rel_field.endswith("_id"):
                        potential_field_name = rel_field[:-3]  # Remove '_id'
                        if self._is_relationship_field(model_cls, potential_field_name):
                            rel_field = potential_field_name

                    # Only add if it's actually a relationship field
                    if self._is_relationship_field(model_cls, rel_field):
                        relationships.add(rel_field)

        # Handle composite conditions (AndCondition, OrCondition)
        if hasattr(condition, "cond1") and hasattr(condition, "cond2"):
            relationships.update(self._extract_condition_relationships(condition.cond1, model_cls))
            relationships.update(self._extract_condition_relationships(condition.cond2, model_cls))

        # Handle NotCondition
        if hasattr(condition, "cond"):
            relationships.update(self._extract_condition_relationships(condition.cond, model_cls))

        return relationships

    def _is_relationship_field(self, model_cls, field_name):
        """Check if a field is a relationship field."""
        try:
            field = model_cls._meta.get_field(field_name)
            return field.is_relation and not field.many_to_many
        except:
            return False

    def _preload_condition_relationships(self, changeset, relationships):
        """
        Preload relationships needed for condition evaluation.

        This prevents N+1 queries when conditions access relationships on both
        old_records and new_records (e.g., HasChanged conditions).

        Args:
            changeset: ChangeSet with records
            relationships: Set of relationship field names to preload
        """
        if not relationships:
            return

        # Use Django's select_related to preload relationships
        relationship_list = list(relationships)

        # Collect all unique PKs from both new_records and old_records
        all_ids = set()

        # Add PKs from new_records
        if changeset.new_records:
            all_ids.update(obj.pk for obj in changeset.new_records if obj.pk is not None)

        # Add PKs from old_records
        if changeset.old_records:
            all_ids.update(obj.pk for obj in changeset.old_records if obj.pk is not None)

        # Bulk preload relationships for all records that have PKs
        if all_ids:
            preloaded = changeset.model_cls.objects.filter(pk__in=list(all_ids)).select_related(*relationship_list).in_bulk()

            # Update new_records with preloaded relationships
            if changeset.new_records:
                for obj in changeset.new_records:
                    if obj.pk and obj.pk in preloaded:
                        preloaded_obj = preloaded[obj.pk]
                        for rel in relationship_list:
                            if hasattr(preloaded_obj, rel):
                                # Preserve FK _id values in __dict__ before setattr (MTI fix)
                                id_field_name = f"{rel}_id"
                                field_was_in_dict = id_field_name in obj.__dict__
                                preserved_id = obj.__dict__.get(id_field_name) if field_was_in_dict else None

                                logger.debug("🔄 PRESERVE_FK_NEW: obj.pk=%s, %s in __dict__=%s, preserved=%s",
                                           obj.pk, id_field_name, field_was_in_dict, preserved_id)

                                setattr(obj, rel, getattr(preloaded_obj, rel))

                                after_setattr = obj.__dict__.get(id_field_name, "NOT_IN_DICT")
                                logger.debug("🔄 AFTER_SETATTR_NEW: obj.pk=%s, %s=%s (was %s)",
                                           obj.pk, id_field_name, after_setattr, preserved_id)

                                # Restore FK _id if it was in __dict__ (prevents Django descriptor from clearing it)
                                # This includes restoring None if that's what was explicitly set
                                if field_was_in_dict:
                                    obj.__dict__[id_field_name] = preserved_id
                                    logger.debug("🔄 RESTORED_FK_NEW: obj.pk=%s, %s=%s",
                                               obj.pk, id_field_name, obj.__dict__.get(id_field_name))

            # Update old_records with preloaded relationships
            if changeset.old_records:
                for obj in changeset.old_records:
                    if obj.pk and obj.pk in preloaded:
                        preloaded_obj = preloaded[obj.pk]
                        for rel in relationship_list:
                            if hasattr(preloaded_obj, rel):
                                # Preserve FK _id values in __dict__ before setattr (MTI fix)
                                id_field_name = f"{rel}_id"
                                field_was_in_dict = id_field_name in obj.__dict__
                                preserved_id = obj.__dict__.get(id_field_name) if field_was_in_dict else None

                                logger.debug("🔄 PRESERVE_FK_OLD: obj.pk=%s, %s in __dict__=%s, preserved=%s",
                                           obj.pk, id_field_name, field_was_in_dict, preserved_id)

                                setattr(obj, rel, getattr(preloaded_obj, rel))

                                after_setattr = obj.__dict__.get(id_field_name, "NOT_IN_DICT")
                                logger.debug("🔄 AFTER_SETATTR_OLD: obj.pk=%s, %s=%s (was %s)",
                                           obj.pk, id_field_name, after_setattr, preserved_id)

                                # Restore FK _id if it was in __dict__ (prevents Django descriptor from clearing it)
                                # This includes restoring None if that's what was explicitly set
                                if field_was_in_dict:
                                    obj.__dict__[id_field_name] = preserved_id
                                    logger.debug("🔄 RESTORED_FK_OLD: obj.pk=%s, %s=%s",
                                               obj.pk, id_field_name, obj.__dict__.get(id_field_name))

        # Log final state after preloading
        if changeset.new_records:
            for obj in changeset.new_records:
                if "business_id" in obj.__dict__:
                    logger.debug("🔄 FINAL_STATE_NEW: obj.pk=%s, business_id=%s",
                               obj.pk, obj.__dict__.get("business_id"))

        # Handle unsaved new_records by preloading their FK targets (bulk query to avoid N+1)
        if changeset.new_records:
            # Collect FK IDs for each relationship from unsaved records
            field_ids_map = {rel: set() for rel in relationship_list}

            for obj in changeset.new_records:
                if obj.pk is None:  # Unsaved object
                    for rel in relationship_list:
                        if hasattr(obj, f"{rel}_id"):
                            rel_id = getattr(obj, f"{rel}_id")
                            if rel_id:
                                field_ids_map[rel].add(rel_id)

            # Bulk load relationships for unsaved records
            field_objects_map = {}
            for rel, ids in field_ids_map.items():
                if not ids:
                    continue
                try:
                    rel_model = getattr(changeset.model_cls._meta.get_field(rel).remote_field, "model")
                    field_objects_map[rel] = rel_model.objects.in_bulk(ids)
                except Exception:
                    field_objects_map[rel] = {}

            # Attach relationships to unsaved records
            for obj in changeset.new_records:
                if obj.pk is None:  # Unsaved object
                    for rel in relationship_list:
                        rel_id = getattr(obj, f"{rel}_id", None)
                        if rel_id and rel in field_objects_map:
                            rel_obj = field_objects_map[rel].get(rel_id)
                            if rel_obj:
                                setattr(obj, rel, rel_obj)

    def _preload_select_related_for_before_create(self, changeset, select_related_fields):
        """
        Explicit bulk preloading for @select_related on BEFORE_CREATE hooks.

        This method provides guaranteed N+1 elimination by:
        1. Collecting all FK IDs from unsaved new_records
        2. Bulk querying related objects
        3. Attaching relationships to each record

        Args:
            changeset: ChangeSet with new_records (unsaved objects)
            select_related_fields: List of field names to preload (e.g., ['financial_account'])
        """
        # Ensure select_related_fields is actually iterable (not a Mock in tests)
        if not select_related_fields or not changeset.new_records or not hasattr(select_related_fields, "__iter__"):
            return

        logger.info(f"🔗 BULK PRELOAD: Preloading {select_related_fields} for {len(changeset.new_records)} unsaved records")

        # Collect FK IDs for each field
        field_ids_map = {field: set() for field in select_related_fields}

        for record in changeset.new_records:
            for field in select_related_fields:
                fk_id = getattr(record, f"{field}_id", None)
                if fk_id is not None:
                    field_ids_map[field].add(fk_id)

        # Bulk query related objects for each field
        field_objects_map = {}
        for field, ids in field_ids_map.items():
            if not ids:
                continue

            try:
                # Get the related model
                relation_field = changeset.model_cls._meta.get_field(field)
                if not relation_field.is_relation:
                    continue

                related_model = relation_field.remote_field.model

                # Bulk query: related_model.objects.filter(id__in=ids)
                field_objects_map[field] = related_model.objects.in_bulk(ids)
                logger.info(f"  ✅ Bulk loaded {len(field_objects_map[field])} {related_model.__name__} objects for field '{field}'")

            except Exception as e:
                logger.warning(f"  ❌ Failed to bulk load field '{field}': {e}")
                field_objects_map[field] = {}

        # Attach relationships to each record
        for record in changeset.new_records:
            for field in select_related_fields:
                fk_id = getattr(record, f"{field}_id", None)
                if fk_id is not None and field in field_objects_map:
                    related_obj = field_objects_map[field].get(fk_id)
                    if related_obj is not None:
                        setattr(record, field, related_obj)
                        # Also cache in Django's fields_cache for consistency
                        if hasattr(record, "_state") and hasattr(record._state, "fields_cache"):
                            record._state.fields_cache[field] = related_obj

        logger.info(f"🔗 BULK PRELOAD: Completed relationship attachment for {len(changeset.new_records)} records")


# Global dispatcher instance
_dispatcher: HookDispatcher | None = None


def get_dispatcher():
    """
    Get the global dispatcher instance.

    Creates the dispatcher on first access (singleton pattern).

    Returns:
        HookDispatcher instance
    """
    global _dispatcher
    if _dispatcher is None:
        # Import here to avoid circular dependency
        from django_bulk_hooks.registry import get_registry

        # Create dispatcher with the registry instance
        _dispatcher = HookDispatcher(get_registry())
    return _dispatcher


def reset_dispatcher():
    """
    Reset the global dispatcher instance.

    Useful for testing to ensure clean state between tests.
    """
    global _dispatcher
    _dispatcher = None
