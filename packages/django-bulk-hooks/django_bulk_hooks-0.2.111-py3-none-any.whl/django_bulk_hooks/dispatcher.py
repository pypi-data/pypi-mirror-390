"""
HookDispatcher: Deterministic, priority-ordered hook execution system.

Provides a single execution path for all hooks with proper lifecycle management,
similar to Salesforce's hook framework.
"""

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OperationKey:
    """Immutable key for tracking hook execution to prevent duplicates."""

    event: str
    model_name: str
    operation_type: str
    record_ids: Tuple[Any, ...]
    update_kwargs: Tuple[Tuple[str, str], ...]

    @classmethod
    def from_changeset(cls, event: str, changeset) -> "OperationKey":
        """Create operation key from changeset."""
        record_ids = cls._extract_record_ids(changeset)
        update_kwargs = cls._extract_update_kwargs(changeset)

        return cls(
            event=event,
            model_name=changeset.model_cls.__name__,
            operation_type=getattr(changeset, "operation_type", "unknown"),
            record_ids=record_ids,
            update_kwargs=update_kwargs,
        )

    @staticmethod
    def _extract_record_ids(changeset) -> Tuple[Any, ...]:
        """Extract and sort record IDs from changeset."""
        record_ids = set()

        for change in changeset.changes:
            if change.new_record and change.new_record.pk:
                record_ids.add(change.new_record.pk)
            if change.old_record and change.old_record.pk:
                record_ids.add(change.old_record.pk)

        try:
            return tuple(sorted(record_ids, key=str))
        except (TypeError, AttributeError):
            return tuple(record_ids)

    @staticmethod
    def _extract_update_kwargs(changeset) -> Tuple[Tuple[str, str], ...]:
        """Extract update kwargs for queryset operations."""
        operation_meta = getattr(changeset, "operation_meta", {}) or {}
        update_kwargs = operation_meta.get("update_kwargs", {})

        if not update_kwargs:
            return ()

        try:
            return tuple(sorted((k, str(v)) for k, v in update_kwargs.items()))
        except (TypeError, AttributeError):
            return tuple(sorted(update_kwargs.keys()))


class RelationshipPreloader:
    """Handles efficient relationship preloading to prevent N+1 queries."""

    def __init__(self, model_cls):
        self.model_cls = model_cls

    def preload_for_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool = True,
    ) -> None:
        """
        Preload relationships for a list of records.

        Args:
            records: List of model instances
            relationships: Set of relationship field names
            preserve_fk_values: Whether to preserve FK _id values after setattr
        """
        if not records or not relationships:
            return

        saved_records = [r for r in records if r.pk is not None]
        unsaved_records = [r for r in records if r.pk is None]

        if saved_records:
            self._preload_saved_records(saved_records, relationships, preserve_fk_values)

        if unsaved_records:
            self._preload_unsaved_records(unsaved_records, relationships, preserve_fk_values)

    def _preload_saved_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Preload relationships for saved records using select_related."""
        pks = [r.pk for r in records]
        relationship_list = list(relationships)

        preloaded = self.model_cls.objects.filter(pk__in=pks).select_related(*relationship_list).in_bulk()

        for record in records:
            if record.pk not in preloaded:
                continue

            preloaded_record = preloaded[record.pk]
            self._attach_relationships(
                record,
                preloaded_record,
                relationships,
                preserve_fk_values,
            )

    def _preload_unsaved_records(
        self,
        records: List[Any],
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Preload relationships for unsaved records by bulk-loading FK targets."""
        # Collect FK IDs for each relationship
        field_ids_map = {rel: set() for rel in relationships}

        for record in records:
            for rel in relationships:
                fk_id = getattr(record, f"{rel}_id", None)
                if fk_id is not None:
                    field_ids_map[rel].add(fk_id)

        # Bulk load related objects
        field_objects_map = self._bulk_load_related_objects(field_ids_map)

        # Attach relationships
        for record in records:
            for rel in relationships:
                fk_id = getattr(record, f"{rel}_id", None)
                if fk_id and rel in field_objects_map:
                    related_obj = field_objects_map[rel].get(fk_id)
                    if related_obj:
                        self._attach_single_relationship(
                            record,
                            rel,
                            related_obj,
                            preserve_fk_values,
                        )

    def _bulk_load_related_objects(
        self,
        field_ids_map: dict[str, Set[Any]],
    ) -> dict[str, dict[Any, Any]]:
        """Bulk load related objects for multiple fields."""
        field_objects_map = {}

        for field, ids in field_ids_map.items():
            if not ids:
                continue

            try:
                related_model = self._get_related_model(field)
                if related_model:
                    field_objects_map[field] = related_model.objects.in_bulk(ids)
                    logger.debug(f"Preloaded {len(field_objects_map[field])} {related_model.__name__} objects for '{field}'")
            except Exception as e:
                logger.warning(f"Failed to preload field '{field}': {e}")
                field_objects_map[field] = {}

        return field_objects_map

    def _attach_relationships(
        self,
        target_record: Any,
        source_record: Any,
        relationships: Set[str],
        preserve_fk_values: bool,
    ) -> None:
        """Attach relationships from source to target record."""
        for rel in relationships:
            if hasattr(source_record, rel):
                related_obj = getattr(source_record, rel)
                self._attach_single_relationship(
                    target_record,
                    rel,
                    related_obj,
                    preserve_fk_values,
                )

    def _attach_single_relationship(
        self,
        record: Any,
        field_name: str,
        related_obj: Any,
        preserve_fk_values: bool,
    ) -> None:
        """Attach a single relationship while optionally preserving FK values."""
        fk_field_name = f"{field_name}_id"

        # Preserve FK value if requested and it was explicitly set
        preserved_fk = None
        should_restore = False

        if preserve_fk_values and fk_field_name in record.__dict__:
            preserved_fk = record.__dict__[fk_field_name]
            should_restore = True

        # Set the relationship
        setattr(record, field_name, related_obj)

        # Restore FK value if needed
        if should_restore:
            record.__dict__[fk_field_name] = preserved_fk

            # Clear cache if FK is None to prevent stale relationship access
            if preserved_fk is None and hasattr(record, "_state"):
                if hasattr(record._state, "fields_cache"):
                    record._state.fields_cache.pop(field_name, None)

    @lru_cache(maxsize=128)
    def _get_related_model(self, field_name: str):
        """Get the related model for a field (cached)."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none
        
        field = _get_field_or_none(self.model_cls, field_name)
        if field and field.is_relation and hasattr(field, "remote_field"):
            return field.remote_field.model
        return None

    @lru_cache(maxsize=128)
    def is_relationship_field(self, field_name: str) -> bool:
        """Check if a field is a relationship field (cached)."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none
        
        field = _get_field_or_none(self.model_cls, field_name)
        return field is not None and field.is_relation and not field.many_to_many


class ConditionAnalyzer:
    """Analyzes hook conditions to extract relationship dependencies."""

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.preloader = RelationshipPreloader(model_cls)

    def extract_relationships(self, condition) -> Set[str]:
        """
        Extract relationship paths that a condition might access.

        Args:
            condition: HookCondition instance

        Returns:
            Set of relationship field names to preload
        """
        if not self._is_valid_condition(condition):
            return set()

        relationships = set()

        # Extract from field attribute
        if hasattr(condition, "field"):
            relationships.update(self._extract_from_field(condition.field))

        # Handle composite conditions (AND, OR)
        if hasattr(condition, "cond1") and hasattr(condition, "cond2"):
            relationships.update(self.extract_relationships(condition.cond1))
            relationships.update(self.extract_relationships(condition.cond2))

        # Handle NOT conditions
        if hasattr(condition, "cond"):
            relationships.update(self.extract_relationships(condition.cond))

        return relationships

    def _is_valid_condition(self, condition) -> bool:
        """Check if object is a valid condition (not a Mock or invalid type)."""
        return hasattr(condition, "check") and not hasattr(condition, "_mock_name")

    def _extract_from_field(self, field_path: str) -> Set[str]:
        """Extract relationships from a field path (e.g., 'status__value' -> 'status')."""
        if not isinstance(field_path, str):
            return set()

        relationships = set()

        if "__" in field_path:
            # Extract first part: "status__value" -> "status"
            rel_field = field_path.split("__")[0]
        else:
            rel_field = field_path

        # Normalize FK field names: business_id -> business
        rel_field = self._normalize_fk_field(rel_field)

        # Only add if it's actually a relationship
        if self.preloader.is_relationship_field(rel_field):
            relationships.add(rel_field)

        return relationships

    def _normalize_fk_field(self, field_name: str) -> str:
        """Convert FK field names (business_id -> business) if applicable."""
        if field_name.endswith("_id"):
            potential_field = field_name[:-3]
            if self.preloader.is_relationship_field(potential_field):
                return potential_field
        return field_name


class HookExecutor:
    """Handles individual hook execution with condition checking and preloading."""

    def __init__(self, model_cls):
        self.model_cls = model_cls
        self.preloader = RelationshipPreloader(model_cls)
        self.condition_analyzer = ConditionAnalyzer(model_cls)

    def execute(
        self,
        handler_cls,
        method_name: str,
        condition,
        changeset,
        event: str,
    ) -> None:
        """
        Execute a single hook with proper preloading and condition checking.

        Args:
            handler_cls: Hook handler class
            method_name: Method name to call
            condition: Optional condition to filter records
            changeset: ChangeSet with record changes
            event: Hook event name
        """
        # Create handler instance
        handler = self._create_handler_instance(handler_cls)
        method = getattr(handler, method_name)

        # Preload relationships from method decorators
        self._preload_method_relationships(handler, method, changeset, event)

        # Preload relationships from conditions
        if condition and not changeset.operation_meta.get("relationships_preloaded"):
            self._preload_condition_relationships(condition, changeset)

        # Apply condition filter if present
        filtered_changeset = self._apply_condition_filter(
            condition,
            changeset,
            handler_cls,
            method_name,
        )

        if filtered_changeset is None:
            return  # No records passed condition

        # Execute the hook
        self._invoke_hook_method(
            method,
            filtered_changeset,
            handler_cls,
            method_name,
        )

    def _create_handler_instance(self, handler_cls):
        """Create hook handler instance using DI factory."""
        from django_bulk_hooks.factory import create_hook_instance

        return create_hook_instance(handler_cls)

    def _preload_method_relationships(
        self,
        handler,
        method,
        changeset,
        event: str,
    ) -> None:
        """Preload relationships specified in method decorators."""
        # Check for @select_related decorator
        preload_func = getattr(method, "_select_related_preload", None)
        if not preload_func:
            return

        try:
            # Get the list of fields being preloaded
            fields = getattr(method, "_select_related_fields", ())
            
            model_cls_override = getattr(handler, "model_cls", None)
            skip_fields = changeset.operation_meta.get("fk_fields_being_updated", set())

            logger.info(f"BULK PRELOAD: Preloading @select_related relationships: {fields}")

            # Preload for new_records
            if changeset.new_records:
                preload_func(
                    changeset.new_records,
                    model_cls=model_cls_override,
                    skip_fields=skip_fields,
                )

            # Preload for old_records
            if changeset.old_records:
                preload_func(
                    changeset.old_records,
                    model_cls=model_cls_override,
                    skip_fields=skip_fields,
                )

            changeset.operation_meta["relationships_preloaded"] = True

        except Exception as e:
            logger.warning(f"Failed to preload relationships: {e}")

    def _preload_condition_relationships(self, condition, changeset) -> None:
        """Preload relationships needed for condition evaluation."""
        relationships = self.condition_analyzer.extract_relationships(condition)

        if not relationships:
            return

        logger.debug(f"Preloading condition relationships: {relationships}")

        # Preload for new_records (preserve FK values for user changes)
        if changeset.new_records:
            self.preloader.preload_for_records(
                changeset.new_records,
                relationships,
                preserve_fk_values=True,
            )

        # Preload for old_records (don't preserve - reflect DB state)
        if changeset.old_records:
            self.preloader.preload_for_records(
                changeset.old_records,
                relationships,
                preserve_fk_values=False,
            )

    def _apply_condition_filter(
        self,
        condition,
        changeset,
        handler_cls,
        method_name: str,
    ):
        """Apply condition filter and return filtered changeset or None."""
        if not condition:
            return changeset

        logger.debug(f"Evaluating condition for {handler_cls.__name__}.{method_name} on {len(changeset.changes)} records")

        filtered_changes = [change for change in changeset.changes if condition.check(change.new_record, change.old_record)]

        logger.debug(f"{len(filtered_changes)}/{len(changeset.changes)} records passed condition")

        if not filtered_changes:
            return None

        # Create filtered changeset
        from django_bulk_hooks.changeset import ChangeSet

        return ChangeSet(
            changeset.model_cls,
            filtered_changes,
            changeset.operation_type,
            changeset.operation_meta,
        )

    def _invoke_hook_method(
        self,
        method: Callable,
        changeset,
        handler_cls,
        method_name: str,
    ) -> None:
        """Invoke the hook method with proper error handling."""
        logger.info(f"Executing: {handler_cls.__name__}.{method_name}")

        try:
            method(
                changeset=changeset,
                new_records=changeset.new_records,
                old_records=changeset.old_records,
            )
            logger.info(f"Completed: {handler_cls.__name__}.{method_name}")
        except Exception as e:
            logger.error(
                f"Hook {handler_cls.__name__}.{method_name} failed: {e}",
                exc_info=True,
            )
            raise


class HookDispatcher:
    """
    Per-operation hook dispatcher with automatic cleanup.
    
    Following Salesforce's trigger context pattern:
    - Each operation gets a fresh dispatcher instance
    - Context is isolated (no cross-operation state leakage)
    - Automatically garbage collected when operation completes
    
    Responsibilities:
    - Execute hooks in priority order
    - Filter records based on conditions
    - Provide ChangeSet context to hooks
    - Fail-fast error propagation
    - Manage complete operation lifecycle (VALIDATE, BEFORE, AFTER)
    
    Design:
        No global singleton - create one per bulk operation.
        This prevents memory leaks in long-lived processes (web servers).
    """
    
    # Class-level constant for bounded cache
    MAX_PRELOADER_CACHE_SIZE = 50

    def __init__(self, registry):
        """
        Initialize a dispatcher for a single operation.
        
        Creates an isolated context similar to Salesforce's per-transaction
        trigger context. State is automatically cleaned up when the operation
        completes and this instance is garbage collected.

        Args:
            registry: Hook registry providing get_hooks method
        """
        self.registry = registry
        
        # Per-operation state (cleared when dispatcher is GC'd)
        self._executed_hooks: Set[Tuple] = set()
        
        # Bounded cache with automatic eviction to prevent unbounded growth
        self._preloader_cache: dict = {}
    
    def _get_or_create_preloader(self, model_cls):
        """
        Get or create a preloader with bounded cache and automatic eviction.
        
        Prevents unbounded memory growth by evicting the oldest entry
        when cache exceeds MAX_PRELOADER_CACHE_SIZE.
        
        Args:
            model_cls: Django model class
            
        Returns:
            RelationshipPreloader instance for the model
        """
        if model_cls in self._preloader_cache:
            return self._preloader_cache[model_cls]
        
        # Create new preloader
        preloader = RelationshipPreloader(model_cls)
        self._preloader_cache[model_cls] = preloader
        
        # Evict oldest entry if cache is full (simple FIFO eviction)
        if len(self._preloader_cache) > self.MAX_PRELOADER_CACHE_SIZE:
            # Remove first item (oldest insertion)
            first_key = next(iter(self._preloader_cache))
            del self._preloader_cache[first_key]
            logger.debug(
                f"Preloader cache exceeded {self.MAX_PRELOADER_CACHE_SIZE} entries, "
                f"evicted {first_key.__name__}"
            )
        
        return preloader

    def execute_operation_with_hooks(
        self,
        changeset,
        operation: Callable,
        event_prefix: str,
        bypass_hooks: bool = False,
    ):
        """
        Execute operation with full hook lifecycle.

        Lifecycle:
        1. VALIDATE_{event}
        2. BEFORE_{event}
        3. Actual operation
        4. AFTER_{event}

        Args:
            changeset: ChangeSet for the operation
            operation: Callable performing the DB operation
            event_prefix: 'create', 'update', or 'delete'
            bypass_hooks: Skip all hooks if True

        Returns:
            Result of operation
        """
        if bypass_hooks:
            return operation()

        try:
            # VALIDATE phase
            self.dispatch(changeset, f"validate_{event_prefix}")

            # BEFORE phase
            self.dispatch(changeset, f"before_{event_prefix}")

            # Execute operation
            result = operation()

            # AFTER phase - rebuild changeset for create operations
            after_changeset = self._prepare_after_changeset(
                changeset,
                result,
                event_prefix,
            )
            self.dispatch(after_changeset, f"after_{event_prefix}")

            return result
        finally:
            # Reset tracking for next operation
            self._reset_executed_hooks()

    def dispatch(
        self,
        changeset,
        event: str,
        bypass_hooks: bool = False,
    ) -> None:
        """
        Dispatch hooks for a changeset with deterministic ordering.

        This is the single execution path for ALL hooks.

        Args:
            changeset: ChangeSet instance with record changes
            event: Event name (e.g., 'after_update', 'before_create')
            bypass_hooks: Skip all hook execution if True

        Raises:
            Exception: Any exception raised by a hook (fails fast)
        """
        if bypass_hooks:
            return

        # Get hooks sorted by priority
        hooks = self.registry.get_hooks(changeset.model_cls, event)

        logger.debug(f"Dispatching: model={changeset.model_cls.__name__}, event={event}, hooks_found={len(hooks)}")

        if not hooks:
            return

        # Deduplicate hooks for MTI inheritance chains
        operation_key = OperationKey.from_changeset(event, changeset)
        unique_hooks = self._deduplicate_hooks(hooks, operation_key)

        if not unique_hooks:
            return

        # Execute hooks
        logger.info(f"Executing {len(unique_hooks)} hooks for {changeset.model_cls.__name__}.{event}")

        executor = HookExecutor(changeset.model_cls)

        for handler_cls, method_name, condition, priority in unique_hooks:
            logger.info(f"  → {handler_cls.__name__}.{method_name} (priority={priority})")
            executor.execute(handler_cls, method_name, condition, changeset, event)

    def preload_relationships(self, changeset, relationships: Set[str]) -> None:
        """
        Preload relationships for a changeset before hook execution.

        This is called by the coordinator to bulk-preload all relationships needed
        by hook conditions for an operation.

        Optimized to use a single query when new_records and old_records have
        overlapping PKs (common in update operations).

        Args:
            changeset: ChangeSet instance with record changes
            relationships: Set of relationship field names to preload
        """
        if not relationships:
            return

        # Get or create preloader for this model
        model_cls = changeset.model_cls
        preloader = self._get_or_create_preloader(model_cls)

        logger.info(f"BULK PRELOAD: Preloading {len(relationships)} relationships for {model_cls.__name__}: {relationships}")

        # Optimization: Check if we can batch both new and old records together
        new_records = changeset.new_records or []
        old_records = changeset.old_records or []
        
        if new_records and old_records:
            # Collect all unique PKs from both sets
            new_pks = {r.pk for r in new_records if r.pk is not None}
            old_pks = {r.pk for r in old_records if r.pk is not None}
            
            # If there's significant overlap (>30%), batch them together
            overlap = new_pks & old_pks
            if overlap and len(overlap) / max(len(new_pks), len(old_pks)) > 0.3:
                logger.info(f"BULK PRELOAD OPTIMIZATION: Batching {len(new_pks | old_pks)} records (overlap: {len(overlap)})")
                self._batch_preload_records(
                    preloader, 
                    model_cls, 
                    new_records, 
                    old_records, 
                    relationships
                )
                return
        
        # Standard path: separate preloading for new and old records
        # Preload for new_records (preserve FK values for user changes)
        if new_records:
            preloader.preload_for_records(
                new_records,
                relationships,
                preserve_fk_values=True,
            )

        # Preload for old_records (don't preserve - reflect DB state)
        if old_records:
            preloader.preload_for_records(
                old_records,
                relationships,
                preserve_fk_values=False,
            )
    
    def _batch_preload_records(
        self,
        preloader,
        model_cls,
        new_records: List,
        old_records: List,
        relationships: Set[str],
    ) -> None:
        """
        Batch preload relationships for both new and old records in a single query.
        
        This optimization combines PKs from both sets and fetches all related
        objects in one query, then distributes them to the appropriate records.
        
        Args:
            preloader: RelationshipPreloader instance
            model_cls: Model class
            new_records: List of new record instances
            old_records: List of old record instances
            relationships: Set of relationship field names to preload
        """
        # Collect all PKs
        all_pks = set()
        for record in new_records:
            if record.pk is not None:
                all_pks.add(record.pk)
        for record in old_records:
            if record.pk is not None:
                all_pks.add(record.pk)
        
        if not all_pks:
            return
        
        # Single bulk query for all records
        relationship_list = list(relationships)
        preloaded_map = model_cls.objects.filter(pk__in=all_pks).select_related(*relationship_list).in_bulk()
        
        logger.debug(f"Batched preload fetched {len(preloaded_map)} records for {len(all_pks)} PKs")
        
        # Attach relationships to new_records (preserve FK values)
        for record in new_records:
            if record.pk in preloaded_map:
                preloaded_record = preloaded_map[record.pk]
                preloader._attach_relationships(
                    record,
                    preloaded_record,
                    relationships,
                    preserve_fk_values=True,
                )
        
        # Attach relationships to old_records (don't preserve)
        for record in old_records:
            if record.pk in preloaded_map:
                preloaded_record = preloaded_map[record.pk]
                preloader._attach_relationships(
                    record,
                    preloaded_record,
                    relationships,
                    preserve_fk_values=False,
                )

    def _prepare_after_changeset(self, changeset, result, event_prefix: str):
        """Prepare changeset for AFTER hooks, rebuilding if needed."""
        if result and isinstance(result, list) and event_prefix == "create":
            # For create, rebuild changeset with assigned PKs
            from django_bulk_hooks.helpers import build_changeset_for_create

            return build_changeset_for_create(changeset.model_cls, result)
        return changeset

    def _deduplicate_hooks(
        self,
        hooks: List[Tuple],
        operation_key: OperationKey,
    ) -> List[Tuple]:
        """
        Deduplicate hooks to prevent duplicate execution in MTI chains.

        Args:
            hooks: List of (handler_cls, method_name, condition, priority) tuples
            operation_key: Key identifying the current operation

        Returns:
            List of unique hooks to execute
        """
        unique_hooks = []
        skipped_hooks = []

        for handler_cls, method_name, condition, priority in hooks:
            hook_key = (handler_cls, method_name, operation_key)

            if hook_key not in self._executed_hooks:
                unique_hooks.append((handler_cls, method_name, condition, priority))
                self._executed_hooks.add(hook_key)
            else:
                skipped_hooks.append((handler_cls.__name__, method_name))

        if skipped_hooks:
            logger.debug(f"Skipped {len(skipped_hooks)} duplicate hooks: {[f'{cls}.{method}' for cls, method in skipped_hooks]}")

        return unique_hooks

    def _reset_executed_hooks(self) -> None:
        """Reset executed hooks tracking for a new operation."""
        self._executed_hooks.clear()

    def _extract_condition_relationships(self, condition, model_cls) -> Set[str]:
        """
        Extract relationship paths that a condition might access.

        Args:
            condition: HookCondition instance
            model_cls: Model class for context

        Returns:
            Set of relationship field names to preload
        """
        analyzer = ConditionAnalyzer(model_cls)
        return analyzer.extract_relationships(condition)
