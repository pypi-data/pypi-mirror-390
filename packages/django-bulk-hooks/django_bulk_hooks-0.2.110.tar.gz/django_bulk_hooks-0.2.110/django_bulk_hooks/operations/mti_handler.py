"""
Multi-table inheritance (MTI) handler service.

Handles detection and planning for multi-table inheritance operations.
This handler is pure logic - it does not execute database operations.
It returns plans (data structures) that the BulkExecutor executes.
"""

import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from django.db.models import AutoField
from django.db.models import Model
from django.db.models import UniqueConstraint

from django_bulk_hooks.helpers import get_fields_for_model
from django_bulk_hooks.operations.field_utils import get_field_value_for_db
from django_bulk_hooks.operations.field_utils import handle_auto_now_fields_for_inheritance_chain
from django_bulk_hooks.operations.mti_plans import ModelFieldGroup
from django_bulk_hooks.operations.mti_plans import MTICreatePlan
from django_bulk_hooks.operations.mti_plans import MTIUpdatePlan
from django_bulk_hooks.operations.mti_plans import ParentLevel

logger = logging.getLogger(__name__)


class MTIHandler:
    """
    Handles multi-table inheritance (MTI) operation planning.

    This service detects MTI models and builds execution plans without
    executing database operations.

    Responsibilities:
    - Detect MTI models
    - Build inheritance chains
    - Create parent/child instances (in-memory only)
    - Return execution plans for bulk operations
    """

    def __init__(self, model_cls: type[Model]) -> None:
        """
        Initialize MTI handler for a specific model.

        Args:
            model_cls: The Django model class to handle
        """
        self.model_cls = model_cls
        self._inheritance_chain: Optional[List[type[Model]]] = None

    def is_mti_model(self) -> bool:
        """
        Determine if the model uses multi-table inheritance.

        Returns:
            True if model has concrete parent models, False otherwise
        """
        for parent in self.model_cls._meta.parents.keys():
            if self._is_concrete_parent(parent):
                return True
        return False

    def get_inheritance_chain(self) -> List[type[Model]]:
        """
        Get the complete inheritance chain from root to child.

        Returns:
            Model classes ordered from root parent to current model.
            Returns empty list if not MTI model.
        """
        if self._inheritance_chain is None:
            self._inheritance_chain = self._compute_chain()
        return self._inheritance_chain

    def get_parent_models(self) -> List[type[Model]]:
        """
        Get all parent models in the inheritance chain.

        Returns:
            Parent model classes (excludes current model)
        """
        chain = self.get_inheritance_chain()
        return chain[:-1] if len(chain) > 1 else []

    def get_local_fields_for_model(self, model_cls: type[Model]) -> list:
        """
        Get fields defined directly on a specific model.

        Args:
            model_cls: Model class to get fields for

        Returns:
            Field objects defined on this model
        """
        return list(model_cls._meta.local_fields)

    def find_model_with_unique_fields(self, unique_fields: List[str]) -> type[Model]:
        """
        Find which model in the chain contains all unique constraint fields.

        For MTI upsert operations, determines if parent records exist to
        properly fire AFTER_CREATE vs AFTER_UPDATE hooks.

        Args:
            unique_fields: List of field names forming the unique constraint

        Returns:
            Model class containing all unique fields
        """
        if not unique_fields:
            return self.model_cls

        inheritance_chain = self.get_inheritance_chain()

        if len(inheritance_chain) > 1:
            # Walk from child to parent to find model with all unique fields
            for model in reversed(inheritance_chain):
                model_field_names = {f.name for f in model._meta.local_fields}
                if all(field in model_field_names for field in unique_fields):
                    return model

        return self.model_cls

    def build_create_plan(
        self,
        objs: List[Model],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        unique_fields: Optional[List[str]] = None,
        update_fields: Optional[List[str]] = None,
        existing_record_ids: Optional[Set[int]] = None,
        existing_pks_map: Optional[Dict[int, int]] = None,
    ) -> Optional[MTICreatePlan]:
        """
        Build an execution plan for bulk creating MTI model instances.

        Does not execute database operations - returns a plan for execution.

        Args:
            objs: Model instances to create
            batch_size: Number of objects per batch
            ignore_conflicts: Whether to ignore conflicts (skip duplicates)
            update_conflicts: Enable UPSERT on conflict
            unique_fields: Fields for conflict detection
            update_fields: Fields to update on conflict
            existing_record_ids: Set of id() for existing DB objects
            existing_pks_map: Dict mapping id(obj) -> pk for existing records

        Returns:
            MTICreatePlan object or None if no objects

        Raises:
            ValueError: If called on non-MTI model
        """
        if not objs:
            return None

        inheritance_chain = self.get_inheritance_chain()
        if len(inheritance_chain) <= 1:
            raise ValueError(f"build_create_plan called on non-MTI model: {self.model_cls.__name__}")

        batch_size = batch_size or len(objs)
        existing_record_ids = existing_record_ids or set()
        existing_pks_map = existing_pks_map or {}
        
        logger.debug("🔧 MTI_CREATE_PLAN: model=%s, ignore_conflicts=%s, update_conflicts=%s, unique_fields=%s, update_fields=%s",
                   self.model_cls.__name__, ignore_conflicts, update_conflicts, unique_fields, update_fields)

        # Set PKs on existing objects for proper updates
        self._set_existing_pks(objs, existing_pks_map)

        # Build parent levels
        parent_levels = self._build_parent_levels(
            objs=objs,
            inheritance_chain=inheritance_chain,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            unique_fields=unique_fields,
            update_fields=update_fields,
            existing_record_ids=existing_record_ids,
            existing_pks_map=existing_pks_map,
        )

        # Build child templates without parent links
        child_objects = [self._create_child_instance_template(obj, inheritance_chain[-1]) for obj in objs]

        # Pre-compute child-specific fields
        child_unique_fields = get_fields_for_model(inheritance_chain[-1], unique_fields or [])
        child_update_fields = get_fields_for_model(inheritance_chain[-1], update_fields or [])

        return MTICreatePlan(
            inheritance_chain=inheritance_chain,
            parent_levels=parent_levels,
            child_objects=child_objects,
            child_model=inheritance_chain[-1],
            original_objects=objs,
            batch_size=batch_size,
            existing_record_ids=existing_record_ids,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            unique_fields=unique_fields or [],
            update_fields=update_fields or [],
            child_unique_fields=child_unique_fields,
            child_update_fields=child_update_fields,
        )

    def build_update_plan(
        self,
        objs: List[Model],
        fields: List[str],
        batch_size: Optional[int] = None,
    ) -> Optional[MTIUpdatePlan]:
        """
        Build an execution plan for bulk updating MTI model instances.

        Does not execute database operations - returns a plan for execution.

        Args:
            objs: Model instances to update
            fields: Field names to update (auto_now fields included by executor)
            batch_size: Number of objects per batch

        Returns:
            MTIUpdatePlan object or None if no objects

        Raises:
            ValueError: If called on non-MTI model
        """
        if not objs:
            return None

        inheritance_chain = self.get_inheritance_chain()
        if len(inheritance_chain) <= 1:
            raise ValueError(f"build_update_plan called on non-MTI model: {self.model_cls.__name__}")

        batch_size = batch_size or len(objs)

        # Group fields by model
        field_groups = self._group_fields_by_model(inheritance_chain, fields)

        return MTIUpdatePlan(
            inheritance_chain=inheritance_chain,
            field_groups=field_groups,
            objects=objs,
            batch_size=batch_size,
        )

    # ==================== Private Helper Methods ====================

    def _is_concrete_parent(self, parent: type[Model]) -> bool:
        """Check if parent is a concrete (non-abstract, non-proxy) model."""
        return not parent._meta.abstract and parent._meta.concrete_model != self.model_cls._meta.concrete_model

    def _compute_chain(self) -> List[type[Model]]:
        """
        Compute the inheritance chain from root parent to child.

        Returns:
            Model classes in order [RootParent, ..., Child]
        """
        chain = []
        current_model = self.model_cls

        while current_model:
            if not current_model._meta.proxy and not current_model._meta.abstract:
                chain.append(current_model)
                logger.debug(
                    f"MTI_CHAIN_ADD: {current_model.__name__} (abstract={current_model._meta.abstract}, proxy={current_model._meta.proxy})"
                )

            # Get concrete parent models
            parents = [parent for parent in current_model._meta.parents.keys() if not parent._meta.proxy and not parent._meta.abstract]
            logger.debug(f"MTI_PARENTS: {current_model.__name__} concrete parents: {[p.__name__ for p in parents]}")

            current_model = parents[0] if parents else None

        chain.reverse()  # Root to child order
        logger.debug(f"MTI_CHAIN_FINAL: {[m.__name__ for m in chain]} (length={len(chain)})")
        return chain

    def _set_existing_pks(self, objs: List[Model], existing_pks_map: Dict[int, int]) -> None:
        """Set primary keys on existing objects for proper updates."""
        if not existing_pks_map:
            return

        for obj in objs:
            obj_id = id(obj)
            if obj_id in existing_pks_map:
                pk_value = existing_pks_map[obj_id]
                obj.pk = pk_value
                obj.id = pk_value

    def _build_parent_levels(
        self,
        objs: List[Model],
        inheritance_chain: List[type[Model]],
        ignore_conflicts: bool,
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
        update_fields: Optional[List[str]],
        existing_record_ids: Set[int],
        existing_pks_map: Dict[int, int],
    ) -> List[ParentLevel]:
        """
        Build parent level objects for each level in the inheritance chain.

        Pure in-memory object creation - no DB operations.

        Returns:
            List of ParentLevel objects
        """
        parent_levels = []
        parent_instances_map: Dict[int, Dict[type[Model], Model]] = {}

        for level_idx, model_class in enumerate(inheritance_chain[:-1]):
            parent_objs_for_level = []

            for obj in objs:
                # Get parent from previous level if exists
                current_parent = self._get_previous_level_parent(obj, level_idx, inheritance_chain, parent_instances_map)

                # Create parent instance
                parent_obj = self._create_parent_instance(obj, model_class, current_parent)
                parent_objs_for_level.append(parent_obj)

                # Store in map
                if id(obj) not in parent_instances_map:
                    parent_instances_map[id(obj)] = {}
                parent_instances_map[id(obj)][model_class] = parent_obj

            # Determine upsert parameters
            upsert_config = self._determine_level_upsert_config(
                model_class=model_class,
                update_conflicts=update_conflicts,
                unique_fields=unique_fields,
                update_fields=update_fields,
            )

            # Create parent level
            parent_level = ParentLevel(
                model_class=model_class,
                objects=parent_objs_for_level,
                original_object_map={id(p): id(o) for p, o in zip(parent_objs_for_level, objs)},
                ignore_conflicts=ignore_conflicts,
                update_conflicts=upsert_config["update_conflicts"],
                unique_fields=upsert_config["unique_fields"],
                update_fields=upsert_config["update_fields"],
            )
            parent_levels.append(parent_level)

        return parent_levels

    def _get_previous_level_parent(
        self,
        obj: Model,
        level_idx: int,
        inheritance_chain: List[type[Model]],
        parent_instances_map: Dict[int, Dict[type[Model], Model]],
    ) -> Optional[Model]:
        """Get parent instance from previous level if it exists."""
        if level_idx == 0:
            return None

        prev_parents = parent_instances_map.get(id(obj), {})
        return prev_parents.get(inheritance_chain[level_idx - 1])

    def _determine_level_upsert_config(
        self,
        model_class: type[Model],
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
        update_fields: Optional[List[str]],
    ) -> Dict[str, any]:
        """
        Determine upsert configuration for a specific parent level.

        Returns:
            Dict with keys: update_conflicts, unique_fields, update_fields
        """
        if not update_conflicts:
            return {
                "update_conflicts": False,
                "unique_fields": [],
                "update_fields": [],
            }

        model_fields_by_name = {f.name: f for f in model_class._meta.local_fields}

        # Normalize unique fields
        normalized_unique = self._normalize_unique_fields(unique_fields or [], model_fields_by_name)

        # Check if this level has matching constraint
        if normalized_unique and self._has_matching_constraint(model_class, normalized_unique):
            return self._build_constraint_based_upsert(model_class, model_fields_by_name, normalized_unique, update_fields)

        # Fallback: PK-based upsert for parent levels without constraint
        return self._build_pk_based_upsert(model_class, model_fields_by_name)

    def _normalize_unique_fields(self, unique_fields: List[str], model_fields_by_name: Dict[str, any]) -> List[str]:
        """Normalize unique fields, handling _id suffix for FK fields."""
        normalized = []
        for field_name in unique_fields:
            if field_name in model_fields_by_name:
                normalized.append(field_name)
            elif field_name.endswith("_id") and field_name[:-3] in model_fields_by_name:
                normalized.append(field_name[:-3])
        return normalized

    def _build_constraint_based_upsert(
        self,
        model_class: type[Model],
        model_fields_by_name: Dict[str, any],
        normalized_unique: List[str],
        update_fields: Optional[List[str]],
    ) -> Dict[str, any]:
        """Build upsert config for levels with matching unique constraints."""
        logger.debug("🔧 UPSERT_CONFIG: model=%s, incoming_update_fields=%s, local_fields=%s",
                   model_class.__name__, update_fields, list(model_fields_by_name.keys()))
        
        filtered_updates = [uf for uf in (update_fields or []) if uf in model_fields_by_name]
        
        logger.debug("🔧 UPSERT_FILTERED: model=%s, filtered_update_fields=%s",
                   model_class.__name__, filtered_updates)

        # Add auto_now fields (critical for timestamp updates)
        auto_now_fields = self._get_auto_now_fields(model_class, model_fields_by_name)
        if auto_now_fields:
            filtered_updates = list(set(filtered_updates) | set(auto_now_fields))

        # Use dummy update if no real updates (prevents constraint violations)
        if not filtered_updates and normalized_unique:
            filtered_updates = [normalized_unique[0]]

        if filtered_updates:
            return {
                "update_conflicts": True,
                "unique_fields": normalized_unique,
                "update_fields": filtered_updates,
            }

        return {"update_conflicts": False, "unique_fields": [], "update_fields": []}

    def _build_pk_based_upsert(self, model_class: type[Model], model_fields_by_name: Dict[str, any]) -> Dict[str, any]:
        """Build PK-based upsert config for parent levels without constraints."""
        pk_field = model_class._meta.pk
        if not pk_field or pk_field.name not in model_fields_by_name:
            return {"update_conflicts": False, "unique_fields": [], "update_fields": []}

        pk_field_name = pk_field.name

        # Prefer auto_now fields, fallback to any non-PK field
        update_fields_for_upsert = self._get_auto_now_fields(model_class, model_fields_by_name)

        if not update_fields_for_upsert:
            non_pk_fields = [name for name in model_fields_by_name.keys() if name != pk_field_name]
            if non_pk_fields:
                update_fields_for_upsert = [non_pk_fields[0]]

        if update_fields_for_upsert:
            return {
                "update_conflicts": True,
                "unique_fields": [pk_field_name],
                "update_fields": update_fields_for_upsert,
            }

        return {"update_conflicts": False, "unique_fields": [], "update_fields": []}

    def _get_auto_now_fields(self, model_class: type[Model], model_fields_by_name: Dict[str, any]) -> List[str]:
        """
        Get auto_now (not auto_now_add) fields for a model.

        Args:
            model_class: Model class to get fields for
            model_fields_by_name: Dict of valid field names

        Returns:
            List of auto_now field names
        """
        auto_now_fields = []
        for field in model_class._meta.local_fields:
            if getattr(field, "auto_now", False) and not getattr(field, "auto_now_add", False) and field.name in model_fields_by_name:
                auto_now_fields.append(field.name)
        return auto_now_fields

    def _has_matching_constraint(self, model_class: type[Model], normalized_unique: List[str]) -> bool:
        """Check if model has a unique constraint matching the given fields."""
        provided_set = set(normalized_unique)

        # Check UniqueConstraints
        constraint_sets = self._get_unique_constraint_sets(model_class)

        # Check unique_together
        unique_together_sets = self._get_unique_together_sets(model_class)

        # Check individual unique fields
        unique_field_sets = self._get_unique_field_sets(model_class)

        all_constraint_sets = constraint_sets + unique_together_sets + unique_field_sets

        return any(provided_set == set(group) for group in all_constraint_sets)

    def _get_unique_constraint_sets(self, model_class: type[Model]) -> List[Tuple[str, ...]]:
        """Get unique constraint field sets."""
        try:
            return [tuple(c.fields) for c in model_class._meta.constraints if isinstance(c, UniqueConstraint)]
        except Exception:
            return []

    def _get_unique_together_sets(self, model_class: type[Model]) -> List[Tuple[str, ...]]:
        """Get unique_together field sets."""
        unique_together = getattr(model_class._meta, "unique_together", ()) or ()

        if isinstance(unique_together, tuple) and unique_together:
            if not isinstance(unique_together[0], (list, tuple)):
                unique_together = (unique_together,)

        return [tuple(group) for group in unique_together]

    def _get_unique_field_sets(self, model_class: type[Model]) -> List[Tuple[str, ...]]:
        """Get individual unique field sets."""
        return [(field.name,) for field in model_class._meta.local_fields if field.unique and not field.primary_key]

    def _create_parent_instance(
        self,
        source_obj: Model,
        parent_model: type[Model],
        current_parent: Optional[Model],
    ) -> Model:
        """
        Create a parent instance from source object (in-memory only).

        Args:
            source_obj: Original object with data
            parent_model: Parent model class to create
            current_parent: Parent from previous level (if any)

        Returns:
            Parent model instance (not saved)
        """
        parent_obj = parent_model()

        # Copy field values
        self._copy_fields_to_parent(parent_obj, source_obj, parent_model)

        # Link to parent from previous level
        if current_parent is not None:
            self._link_to_parent(parent_obj, current_parent, parent_model)

        # Copy object state
        self._copy_object_state(parent_obj, source_obj)

        # Handle auto_now fields
        handle_auto_now_fields_for_inheritance_chain([parent_model], [parent_obj], for_update=False)

        return parent_obj

    def _copy_fields_to_parent(self, parent_obj: Model, source_obj: Model, parent_model: type[Model]) -> None:
        """Copy field values from source to parent instance."""
        for field in parent_model._meta.local_fields:
            # Handle AutoField (PK) specially for existing records
            if isinstance(field, AutoField):
                if hasattr(source_obj, "pk") and source_obj.pk is not None:
                    setattr(parent_obj, field.attname, source_obj.pk)
                continue

            if hasattr(source_obj, field.name):
                value = get_field_value_for_db(source_obj, field.name, source_obj.__class__)
                if value is not None:
                    setattr(parent_obj, field.attname, value)

    def _link_to_parent(self, parent_obj: Model, current_parent: Model, parent_model: type[Model]) -> None:
        """Link parent object to its parent from previous level."""
        for field in parent_model._meta.local_fields:
            if hasattr(field, "remote_field") and field.remote_field and field.remote_field.model == current_parent.__class__:
                setattr(parent_obj, field.name, current_parent)
                break

    def _create_child_instance_template(self, source_obj: Model, child_model: type[Model]) -> Model:
        """
        Create a child instance template (in-memory, no parent links).

        Executor will add parent links after creating parent objects.

        Args:
            source_obj: Original object with data
            child_model: Child model class

        Returns:
            Child model instance (not saved, no parent links)
        """
        child_obj = child_model()

        # Get inherited field names to skip
        parent_fields = self._get_inherited_field_names(child_model)

        # Copy child-specific fields only
        for field in child_model._meta.local_fields:
            if isinstance(field, AutoField):
                continue

            # Skip parent link fields
            if self._is_parent_link_field(child_model, field):
                continue

            # Skip inherited fields
            if field.name in parent_fields:
                continue

            if hasattr(source_obj, field.name):
                value = get_field_value_for_db(source_obj, field.name, source_obj.__class__)
                if value is not None:
                    setattr(child_obj, field.attname, value)

        # Copy object state
        self._copy_object_state(child_obj, source_obj)

        # Handle auto_now fields
        handle_auto_now_fields_for_inheritance_chain([child_model], [child_obj], for_update=False)

        return child_obj

    def _get_inherited_field_names(self, child_model: type[Model]) -> Set[str]:
        """Get field names inherited from parent models."""
        parent_fields = set()
        for parent_model in child_model._meta.parents.keys():
            parent_fields.update(f.name for f in parent_model._meta.local_fields)
        return parent_fields

    def _is_parent_link_field(self, child_model: type[Model], field: any) -> bool:
        """Check if field is a parent link field."""
        if not field.is_relation or not hasattr(field, "related_model"):
            return False
        return child_model._meta.get_ancestor_link(field.related_model) == field

    def _copy_object_state(self, target_obj: Model, source_obj: Model) -> None:
        """Copy Django object state from source to target."""
        if hasattr(source_obj, "_state") and hasattr(target_obj, "_state"):
            target_obj._state.adding = source_obj._state.adding
            if hasattr(source_obj._state, "db"):
                target_obj._state.db = source_obj._state.db

    def _group_fields_by_model(self, inheritance_chain: List[type[Model]], fields: List[str]) -> List[ModelFieldGroup]:
        """
        Group fields by the model they belong to in the inheritance chain.

        Args:
            inheritance_chain: Models in order from root to child
            fields: Field names to group

        Returns:
            List of ModelFieldGroup objects
        """
        field_groups = []

        logger.debug(
            f"MTI_UPDATE_FIELD_GROUPING: Processing {len(fields)} fields "
            f"for {len(inheritance_chain)} models: "
            f"{[m.__name__ for m in inheritance_chain]}"
        )

        for model_idx, model in enumerate(inheritance_chain):
            model_fields = self._get_fields_for_model(model, fields)

            if model_fields:
                filter_field = self._get_filter_field_for_model(model, model_idx, inheritance_chain)

                field_groups.append(
                    ModelFieldGroup(
                        model_class=model,
                        fields=model_fields,
                        filter_field=filter_field,
                    )
                )

        return field_groups

    def _get_fields_for_model(self, model: type[Model], fields: List[str]) -> List[str]:
        """Get fields that belong to specific model (excluding auto_now_add)."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none
        
        model_fields = []

        for field_name in fields:
            # Use cached field lookup
            field = _get_field_or_none(self.model_cls, field_name)

            if field and field in model._meta.local_fields:
                # Skip auto_now_add fields for updates
                if not getattr(field, "auto_now_add", False):
                    model_fields.append(field_name)
                    logger.debug(f"MTI_UPDATE_FIELD_ASSIGNED: '{field_name}' → {model.__name__}")
            elif field is None:
                logger.debug(f"MTI_UPDATE_FIELD_ERROR: '{field_name}' on {model.__name__}: field not found")

        return model_fields

    def _get_filter_field_for_model(self, model: type[Model], model_idx: int, inheritance_chain: List[type[Model]]) -> str:
        """Get the field to use for filtering in bulk updates."""
        if model_idx == 0:
            return "pk"

        # Find parent link
        for parent_model in inheritance_chain:
            if parent_model in model._meta.parents:
                parent_link = model._meta.parents[parent_model]
                return parent_link.attname

        return "pk"
