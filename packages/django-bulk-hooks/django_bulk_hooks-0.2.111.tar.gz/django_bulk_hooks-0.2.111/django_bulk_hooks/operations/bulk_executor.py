"""
Bulk executor service for database operations.

Coordinates bulk database operations with validation and MTI handling.
This service is the only component that directly calls Django ORM methods.
"""

import logging
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

from django.db import transaction
from django.db.models import AutoField
from django.db.models import Case
from django.db.models import ForeignKey
from django.db.models import Model
from django.db.models import QuerySet
from django.db.models import Value
from django.db.models import When
from django.db.models.constants import OnConflict
from django.db.models.functions import Cast

from django_bulk_hooks.helpers import tag_upsert_metadata
from django_bulk_hooks.operations.field_utils import get_field_value_for_db
from django_bulk_hooks.operations.field_utils import handle_auto_now_fields_for_inheritance_chain

logger = logging.getLogger(__name__)


class BulkExecutor:
    """
    Executes bulk database operations.

    Coordinates validation, MTI handling, and database operations.
    This is the only service that directly calls Django ORM methods.

    All dependencies are explicitly injected via constructor for testability.
    """

    def __init__(
        self,
        queryset: QuerySet,
        analyzer: Any,
        mti_handler: Any,
        record_classifier: Any,
    ) -> None:
        """
        Initialize bulk executor with explicit dependencies.

        Args:
            queryset: Django QuerySet instance
            analyzer: ModelAnalyzer instance (validation and field tracking)
            mti_handler: MTIHandler instance
            record_classifier: RecordClassifier instance
        """
        self.queryset = queryset
        self.analyzer = analyzer
        self.mti_handler = mti_handler
        self.record_classifier = record_classifier
        self.model_cls = queryset.model

    def bulk_create(
        self,
        objs: List[Model],
        batch_size: Optional[int] = None,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: Optional[List[str]] = None,
        unique_fields: Optional[List[str]] = None,
        existing_record_ids: Optional[Set[int]] = None,
        existing_pks_map: Optional[Dict[int, int]] = None,
        **kwargs: Any,
    ) -> List[Model]:
        """
        Execute bulk create operation.

        NOTE: Coordinator validates inputs before calling this method.
        This executor trusts that inputs are pre-validated.

        Args:
            objs: Model instances to create (pre-validated)
            batch_size: Objects per batch
            ignore_conflicts: Whether to ignore conflicts
            update_conflicts: Whether to update on conflict
            update_fields: Fields to update on conflict
            unique_fields: Fields for conflict detection
            existing_record_ids: Pre-classified existing record IDs
            existing_pks_map: Pre-classified existing PK mapping
            **kwargs: Additional arguments

        Returns:
            List of created/updated objects
        """
        if not objs:
            return objs

        # Route to appropriate handler
        if self.mti_handler.is_mti_model():
            result = self._handle_mti_create(
                objs=objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
                existing_record_ids=existing_record_ids,
                existing_pks_map=existing_pks_map,
            )
        else:
            result = self._execute_standard_bulk_create(
                objs=objs,
                batch_size=batch_size,
                ignore_conflicts=ignore_conflicts,
                update_conflicts=update_conflicts,
                update_fields=update_fields,
                unique_fields=unique_fields,
                **kwargs,
            )

        # Tag upsert metadata
        self._handle_upsert_metadata_tagging(
            result_objects=result,
            objs=objs,
            update_conflicts=update_conflicts,
            unique_fields=unique_fields,
            existing_record_ids=existing_record_ids,
            existing_pks_map=existing_pks_map,
        )

        return result

    def bulk_update(self, objs: List[Model], fields: List[str], batch_size: Optional[int] = None) -> int:
        """
        Execute bulk update operation.

        NOTE: Coordinator validates inputs before calling this method.
        This executor trusts that inputs are pre-validated.

        Args:
            objs: Model instances to update (pre-validated)
            fields: Field names to update
            batch_size: Objects per batch

        Returns:
            Number of objects updated
        """
        if not objs:
            return 0

        # Debug: Check FK values at bulk_update entry point
        for obj in objs:
            logger.debug("🚀 BULK_UPDATE_ENTRY: obj.pk=%s, business_id in __dict__=%s, value=%s",
                        getattr(obj, 'pk', 'None'),
                        'business_id' in obj.__dict__,
                        obj.__dict__.get('business_id', 'NOT_IN_DICT'))

        # Ensure auto_now fields are included
        fields = self._add_auto_now_fields(fields, objs)

        # Route to appropriate handler
        if self.mti_handler.is_mti_model():
            logger.info(f"Using MTI bulk update for {self.model_cls.__name__}")
            plan = self.mti_handler.build_update_plan(objs, fields, batch_size=batch_size)
            return self._execute_mti_update_plan(plan)

        # Standard bulk update
        base_qs = self._get_base_queryset()
        return base_qs.bulk_update(objs, fields, batch_size=batch_size)

    def delete_queryset(self) -> Tuple[int, Dict[str, int]]:
        """
        Execute delete on the queryset.

        NOTE: Coordinator validates inputs before calling this method.

        Returns:
            Tuple of (count, details dict)
        """
        if not self.queryset:
            return 0, {}

        return QuerySet.delete(self.queryset)

    # ==================== Private: Create Helpers ====================

    def _handle_mti_create(
        self,
        objs: List[Model],
        batch_size: Optional[int],
        ignore_conflicts: bool,
        update_conflicts: bool,
        update_fields: Optional[List[str]],
        unique_fields: Optional[List[str]],
        existing_record_ids: Optional[Set[int]],
        existing_pks_map: Optional[Dict[int, int]],
    ) -> List[Model]:
        """Handle MTI model creation with classification and planning."""
        # Classify records if not pre-classified
        if existing_record_ids is None or existing_pks_map is None:
            existing_record_ids, existing_pks_map = self._classify_mti_records(objs, update_conflicts, unique_fields)

        # Build and execute plan
        plan = self.mti_handler.build_create_plan(
            objs=objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
            existing_record_ids=existing_record_ids,
            existing_pks_map=existing_pks_map,
        )

        return self._execute_mti_create_plan(plan)

    def _classify_mti_records(
        self,
        objs: List[Model],
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
    ) -> Tuple[Set[int], Dict[int, int]]:
        """Classify MTI records for upsert operations."""
        if not update_conflicts or not unique_fields:
            return set(), {}

        # Find correct model to query
        query_model = self.mti_handler.find_model_with_unique_fields(unique_fields)
        logger.info(f"MTI upsert: querying {query_model.__name__} for unique fields {unique_fields}")

        existing_record_ids, existing_pks_map = self.record_classifier.classify_for_upsert(objs, unique_fields, query_model=query_model)

        logger.info(f"MTI classification: {len(existing_record_ids)} existing, {len(objs) - len(existing_record_ids)} new")

        return existing_record_ids, existing_pks_map

    def _execute_standard_bulk_create(
        self,
        objs: List[Model],
        batch_size: Optional[int],
        ignore_conflicts: bool,
        update_conflicts: bool,
        update_fields: Optional[List[str]],
        unique_fields: Optional[List[str]],
        **kwargs: Any,
    ) -> List[Model]:
        """Execute Django's native bulk_create for non-MTI models."""
        base_qs = self._get_base_queryset()

        return base_qs.bulk_create(
            objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields,
            unique_fields=unique_fields,
        )

    def _handle_upsert_metadata_tagging(
        self,
        result_objects: List[Model],
        objs: List[Model],
        update_conflicts: bool,
        unique_fields: Optional[List[str]],
        existing_record_ids: Optional[Set[int]],
        existing_pks_map: Optional[Dict[int, int]],
    ) -> None:
        """
        Tag upsert metadata on result objects.

        Centralizes metadata tagging logic for both MTI and non-MTI paths.

        Args:
            result_objects: Objects returned from bulk operation
            objs: Original objects passed to bulk_create
            update_conflicts: Whether this was an upsert operation
            unique_fields: Fields used for conflict detection
            existing_record_ids: Pre-classified existing record IDs
            existing_pks_map: Pre-classified existing PK mapping
        """
        if not (update_conflicts and unique_fields):
            return

        # Classify if needed
        if existing_record_ids is None or existing_pks_map is None:
            existing_record_ids, existing_pks_map = self.record_classifier.classify_for_upsert(objs, unique_fields)

        tag_upsert_metadata(result_objects, existing_record_ids, existing_pks_map)

    # ==================== Private: Update Helpers ====================

    def _add_auto_now_fields(self, fields: List[str], objs: List[Model]) -> List[str]:
        """
        Add auto_now fields to update list for all models in chain.

        Handles both MTI and non-MTI models uniformly.

        Args:
            fields: Original field list
            objs: Objects being updated

        Returns:
            Field list with auto_now fields included
        """
        fields = list(fields)  # Copy to avoid mutation

        # Get models to check
        if self.mti_handler.is_mti_model():
            models_to_check = self.mti_handler.get_inheritance_chain()
        else:
            models_to_check = [self.model_cls]

        # Handle auto_now fields uniformly
        auto_now_fields = handle_auto_now_fields_for_inheritance_chain(models_to_check, objs, for_update=True)

        # Add to fields list if not present
        for auto_now_field in auto_now_fields:
            if auto_now_field not in fields:
                fields.append(auto_now_field)

        return fields

    # ==================== Private: MTI Create Execution ====================

    def _execute_mti_create_plan(self, plan: Any) -> List[Model]:
        """
        Execute an MTI create plan.

        Handles INSERT and UPDATE for upsert operations.

        Args:
            plan: MTICreatePlan from MTIHandler

        Returns:
            List of created/updated objects with PKs assigned
        """
        if not plan:
            return []

        with transaction.atomic(using=self.queryset.db, savepoint=False):
            # Step 1: Upsert all parent levels
            parent_instances_map = self._upsert_parent_levels(plan)

            # Step 2: Link children to parents
            self._link_children_to_parents(plan, parent_instances_map)

            # Step 3: Handle child objects (insert new, update existing)
            self._handle_child_objects(plan)

            # Step 4: Copy PKs and auto-fields back to original objects
            self._copy_fields_to_original_objects(plan, parent_instances_map)

        return plan.original_objects

    def _upsert_parent_levels(self, plan: Any) -> Dict[int, Dict[type, Model]]:
        """
        Upsert all parent objects level by level.

        Returns:
            Mapping of original obj id() -> {model: parent_instance}
        """
        parent_instances_map: Dict[int, Dict[type, Model]] = {}

        for parent_level in plan.parent_levels:
            base_qs = QuerySet(model=parent_level.model_class, using=self.queryset.db)

            # Build bulk_create kwargs
            bulk_kwargs = {"batch_size": len(parent_level.objects)}

            # Add ignore_conflicts if specified
            if parent_level.ignore_conflicts:
                bulk_kwargs["ignore_conflicts"] = True

            # Add upsert kwargs if update_conflicts is enabled
            if parent_level.update_conflicts:
                self._add_upsert_kwargs(bulk_kwargs, parent_level)

            # Execute upsert
            upserted_parents = base_qs.bulk_create(parent_level.objects, **bulk_kwargs)

            # Copy generated fields back
            self._copy_generated_fields(upserted_parents, parent_level.objects, parent_level.model_class)

            # Map parents to original objects
            self._map_parents_to_originals(parent_level, parent_instances_map)

        return parent_instances_map

    def _add_upsert_kwargs(self, bulk_kwargs: Dict[str, Any], parent_level: Any) -> None:
        """Add upsert parameters to bulk_create kwargs."""
        bulk_kwargs["update_conflicts"] = True
        bulk_kwargs["unique_fields"] = parent_level.unique_fields

        # Filter update fields
        parent_model_fields = {field.name for field in parent_level.model_class._meta.local_fields}
        filtered_update_fields = [field for field in parent_level.update_fields if field in parent_model_fields]

        if filtered_update_fields:
            bulk_kwargs["update_fields"] = filtered_update_fields

    def _copy_generated_fields(
        self,
        upserted_parents: List[Model],
        parent_objs: List[Model],
        model_class: type[Model],
    ) -> None:
        """Copy generated fields from upserted objects back to parent objects."""
        for upserted_parent, parent_obj in zip(upserted_parents, parent_objs):
            for field in model_class._meta.local_fields:
                # Use attname for FK fields to avoid queries
                field_attr = field.attname if isinstance(field, ForeignKey) else field.name
                upserted_value = getattr(upserted_parent, field_attr, None)
                if upserted_value is not None:
                    setattr(parent_obj, field_attr, upserted_value)

            parent_obj._state.adding = False
            parent_obj._state.db = self.queryset.db

    def _map_parents_to_originals(self, parent_level: Any, parent_instances_map: Dict[int, Dict[type, Model]]) -> None:
        """Map parent instances back to original objects."""
        for parent_obj in parent_level.objects:
            orig_obj_id = parent_level.original_object_map[id(parent_obj)]
            if orig_obj_id not in parent_instances_map:
                parent_instances_map[orig_obj_id] = {}
            parent_instances_map[orig_obj_id][parent_level.model_class] = parent_obj

    def _link_children_to_parents(self, plan: Any, parent_instances_map: Dict[int, Dict[type, Model]]) -> None:
        """Link child objects to their parent objects and set PKs."""
        for child_obj, orig_obj in zip(plan.child_objects, plan.original_objects):
            parent_instances = parent_instances_map.get(id(orig_obj), {})

            for parent_model, parent_instance in parent_instances.items():
                parent_link = plan.child_model._meta.get_ancestor_link(parent_model)

                if parent_link:
                    parent_pk = parent_instance.pk
                    setattr(child_obj, parent_link.attname, parent_pk)
                    setattr(child_obj, parent_link.name, parent_instance)
                    # In MTI, child PK equals parent PK
                    child_obj.pk = parent_pk
                    child_obj.id = parent_pk
                else:
                    logger.warning(f"No parent link found for {parent_model} in {plan.child_model}")

    def _handle_child_objects(self, plan: Any) -> None:
        """Handle child object insertion and updates."""
        base_qs = QuerySet(model=plan.child_model, using=self.queryset.db)

        # Split objects: new vs existing
        objs_without_pk, objs_with_pk = self._split_child_objects(plan, base_qs)

        # Update existing children
        if objs_with_pk and plan.update_fields:
            self._update_existing_children(base_qs, objs_with_pk, plan)

        # Insert new children
        if objs_without_pk:
            self._insert_new_children(base_qs, objs_without_pk, plan)

    def _split_child_objects(self, plan: Any, base_qs: QuerySet) -> Tuple[List[Model], List[Model]]:
        """Split child objects into new and existing."""
        if not plan.update_conflicts:
            return plan.child_objects, []

        # Check which child records exist
        parent_pks = [
            getattr(child_obj, plan.child_model._meta.pk.attname, None)
            for child_obj in plan.child_objects
            if getattr(child_obj, plan.child_model._meta.pk.attname, None)
        ]

        existing_child_pks = set()
        if parent_pks:
            existing_child_pks = set(base_qs.filter(pk__in=parent_pks).values_list("pk", flat=True))

        objs_without_pk = []
        objs_with_pk = []

        for child_obj in plan.child_objects:
            child_pk = getattr(child_obj, plan.child_model._meta.pk.attname, None)
            if child_pk and child_pk in existing_child_pks:
                objs_with_pk.append(child_obj)
            else:
                objs_without_pk.append(child_obj)

        return objs_without_pk, objs_with_pk

    def _update_existing_children(self, base_qs: QuerySet, objs_with_pk: List[Model], plan: Any) -> None:
        """Update existing child records."""
        child_model_fields = {field.name for field in plan.child_model._meta.local_fields}
        filtered_child_update_fields = [field for field in plan.update_fields if field in child_model_fields]

        if filtered_child_update_fields:
            base_qs.bulk_update(objs_with_pk, filtered_child_update_fields)

        for obj in objs_with_pk:
            obj._state.adding = False
            obj._state.db = self.queryset.db

    def _insert_new_children(self, base_qs: QuerySet, objs_without_pk: List[Model], plan: Any) -> None:
        """Insert new child records using _batched_insert."""
        base_qs._prepare_for_bulk_create(objs_without_pk)
        opts = plan.child_model._meta

        # Get fields for insertion
        filtered_fields = [f for f in opts.local_fields if not f.generated]

        # Build upsert kwargs
        kwargs = self._build_batched_insert_kwargs(plan, len(objs_without_pk))

        # Execute insert
        returned_columns = base_qs._batched_insert(objs_without_pk, filtered_fields, **kwargs)

        # Process returned columns
        self._process_returned_columns(objs_without_pk, returned_columns, opts)

    def _build_batched_insert_kwargs(self, plan: Any, batch_size: int) -> Dict[str, Any]:
        """Build kwargs for _batched_insert call."""
        kwargs = {"batch_size": batch_size}

        # Handle ignore_conflicts (takes precedence)
        if plan.ignore_conflicts:
            kwargs["on_conflict"] = OnConflict.IGNORE
            return kwargs

        # Handle update_conflicts
        if not (plan.update_conflicts and plan.child_unique_fields):
            return kwargs

        batched_unique_fields = plan.child_unique_fields
        batched_update_fields = plan.child_update_fields

        if batched_update_fields:
            on_conflict = OnConflict.UPDATE
        else:
            # No update fields on child - use IGNORE
            on_conflict = OnConflict.IGNORE
            batched_update_fields = None

        kwargs.update(
            {
                "on_conflict": on_conflict,
                "update_fields": batched_update_fields,
                "unique_fields": batched_unique_fields,
            },
        )

        return kwargs

    def _process_returned_columns(self, objs: List[Model], returned_columns: Any, opts: Any) -> None:
        """Process returned columns from _batched_insert."""
        if returned_columns:
            for obj, results in zip(objs, returned_columns):
                if hasattr(opts, "db_returning_fields"):
                    for result, field in zip(results, opts.db_returning_fields):
                        setattr(obj, field.attname, result)
                obj._state.adding = False
                obj._state.db = self.queryset.db
        else:
            for obj in objs:
                obj._state.adding = False
                obj._state.db = self.queryset.db

    def _copy_fields_to_original_objects(self, plan: Any, parent_instances_map: Dict[int, Dict[type, Model]]) -> None:
        """Copy PKs and auto-generated fields to original objects."""
        pk_field_name = plan.child_model._meta.pk.name

        for orig_obj, child_obj in zip(plan.original_objects, plan.child_objects):
            # Copy PK
            child_pk = getattr(child_obj, pk_field_name)
            setattr(orig_obj, pk_field_name, child_pk)

            # Copy auto-generated fields from all levels
            self._copy_auto_generated_fields(orig_obj, child_obj, plan, parent_instances_map, pk_field_name)

            # Update state
            orig_obj._state.adding = False
            orig_obj._state.db = self.queryset.db

    def _copy_auto_generated_fields(
        self,
        orig_obj: Model,
        child_obj: Model,
        plan: Any,
        parent_instances_map: Dict[int, Dict[type, Model]],
        pk_field_name: str,
    ) -> None:
        """Copy auto-generated fields from all inheritance levels."""
        parent_instances = parent_instances_map.get(id(orig_obj), {})

        for model_class in plan.inheritance_chain:
            # Get source object
            if model_class in parent_instances:
                source_obj = parent_instances[model_class]
            elif model_class == plan.child_model:
                source_obj = child_obj
            else:
                continue

            # Copy auto-generated fields
            for field in model_class._meta.local_fields:
                if field.name == pk_field_name:
                    continue

                # Skip parent link fields
                if self._is_parent_link_field(field, plan.child_model, model_class):
                    continue

                # Copy auto_now, auto_now_add, and db_returning fields
                if self._is_auto_generated_field(field):
                    source_value = getattr(source_obj, field.name, None)
                    if source_value is not None:
                        setattr(orig_obj, field.name, source_value)

    def _is_parent_link_field(self, field: Any, child_model: type[Model], model_class: type[Model]) -> bool:
        """Check if field is a parent link field."""
        if not (hasattr(field, "remote_field") and field.remote_field):
            return False

        parent_link = child_model._meta.get_ancestor_link(model_class)
        return parent_link and field.name == parent_link.name

    def _is_auto_generated_field(self, field: Any) -> bool:
        """Check if field is auto-generated."""
        return getattr(field, "auto_now_add", False) or getattr(field, "auto_now", False) or getattr(field, "db_returning", False)

    # ==================== Private: MTI Update Execution ====================

    def _execute_mti_update_plan(self, plan: Any) -> int:
        """
        Execute an MTI update plan.

        Updates each table in the inheritance chain using CASE/WHEN.

        Args:
            plan: MTIUpdatePlan from MTIHandler

        Returns:
            Number of objects updated
        """
        if not plan:
            return 0

        root_pks = self._get_root_pks(plan.objects)
        if not root_pks:
            return 0

        total_updated = 0

        with transaction.atomic(using=self.queryset.db, savepoint=False):
            for field_group in plan.field_groups:
                if not field_group.fields:
                    continue

                updated_count = self._update_field_group(field_group, root_pks, plan.objects)
                total_updated += updated_count

        return total_updated

    def _get_root_pks(self, objs: List[Model]) -> List[Any]:
        """Extract primary keys from objects."""
        return [
            getattr(obj, "pk", None) or getattr(obj, "id", None) for obj in objs if getattr(obj, "pk", None) or getattr(obj, "id", None)
        ]

    def _update_field_group(self, field_group: Any, root_pks: List[Any], objs: List[Model]) -> int:
        """Update a single field group."""
        base_qs = QuerySet(model=field_group.model_class, using=self.queryset.db)

        # Check if records exist
        if not self._check_records_exist(base_qs, field_group, root_pks):
            return 0

        # Build CASE statements
        case_statements = self._build_case_statements(field_group, root_pks, objs)

        if not case_statements:
            logger.debug(f"No CASE statements for {field_group.model_class.__name__}")
            return 0

        # Execute update
        return self._execute_field_group_update(base_qs, field_group, root_pks, case_statements)

    def _check_records_exist(self, base_qs: QuerySet, field_group: Any, root_pks: List[Any]) -> bool:
        """Check if any records exist for update."""
        existing_count = base_qs.filter(**{f"{field_group.filter_field}__in": root_pks}).count()
        return existing_count > 0

    def _build_case_statements(self, field_group: Any, root_pks: List[Any], objs: List[Model]) -> Dict[str, Case]:
        """Build CASE statements for all fields in the group."""
        case_statements = {}

        logger.debug(f"Building CASE statements for {field_group.model_class.__name__} with {len(field_group.fields)} fields")

        # Debug: Check if business_id is still in __dict__ before field extraction
        for obj in objs:
            if 'business_id' in obj.__dict__ or 'business' in field_group.fields:
                logger.debug("🏗️ CASE_BUILD_START: obj.pk=%s, business_id in __dict__=%s, value=%s",
                            getattr(obj, 'pk', 'None'),
                            'business_id' in obj.__dict__,
                            obj.__dict__.get('business_id', 'NOT_IN_DICT'))

        for field_name in field_group.fields:
            case_stmt = self._build_field_case_statement(field_name, field_group, root_pks, objs)
            if case_stmt:
                case_statements[field_name] = case_stmt

        return case_statements

    def _build_field_case_statement(
        self,
        field_name: str,
        field_group: Any,
        root_pks: List[Any],
        objs: List[Model],
    ) -> Optional[Case]:
        """Build CASE statement for a single field."""
        from django_bulk_hooks.operations.field_utils import _get_field_or_none
        
        field = _get_field_or_none(field_group.model_class, field_name)
        if field is None:
            logger.warning(f"Field '{field_name}' not found on {field_group.model_class.__name__}")
            return None
            
        when_statements = []

        for pk, obj in zip(root_pks, objs):
            obj_pk = getattr(obj, "pk", None) or getattr(obj, "id", None)
            if obj_pk is None:
                continue

            # Get and convert field value
            value = get_field_value_for_db(obj, field_name, field_group.model_class)
            
            # Debug: Track business field extraction
            if field_name == 'business':
                logger.debug("🔧 CASE_FIELD_VALUE: obj.pk=%s, field='%s', raw_value=%s, business_id in __dict__=%s",
                           obj_pk, field_name, value,
                           'business_id' in obj.__dict__ if hasattr(obj, '__dict__') else 'N/A')
            
            value = field.to_python(value)

            # Create WHEN with type casting
            when_statement = When(
                **{field_group.filter_field: pk},
                then=Cast(Value(value), output_field=field),
            )
            when_statements.append(when_statement)

        if when_statements:
            return Case(*when_statements, output_field=field)

        return None

    def _execute_field_group_update(
        self,
        base_qs: QuerySet,
        field_group: Any,
        root_pks: List[Any],
        case_statements: Dict[str, Case],
    ) -> int:
        """Execute the actual update query."""
        logger.debug(f"Executing update for {field_group.model_class.__name__} with {len(case_statements)} fields")
        logger.debug(f"📝 UPDATE_FIELDS: {field_group.model_class.__name__} updating fields: {list(case_statements.keys())}")

        try:
            query_qs = base_qs.filter(**{f"{field_group.filter_field}__in": root_pks})
            updated_count = query_qs.update(**case_statements)

            logger.debug(f"Updated {updated_count} records in {field_group.model_class.__name__}")

            return updated_count

        except Exception as e:
            logger.error(f"MTI bulk update failed for {field_group.model_class.__name__}: {e}")
            raise

    # ==================== Private: Utilities ====================

    def _get_base_queryset(self) -> QuerySet:
        """Get base Django QuerySet to avoid recursion."""
        return QuerySet(model=self.model_cls, using=self.queryset.db)
