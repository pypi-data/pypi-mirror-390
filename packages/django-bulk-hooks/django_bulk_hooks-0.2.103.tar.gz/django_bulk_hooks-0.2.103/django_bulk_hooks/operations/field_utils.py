"""
Utilities for field value extraction and normalization.

Single source of truth for converting model instance field values
to their database representation. This eliminates duplicate FK handling
logic scattered across multiple components.
"""

import logging

from django.db.models import ForeignKey

logger = logging.getLogger(__name__)


def get_field_value_for_db(obj, field_name, model_cls=None):
    """
    Get a field value from an object in its database-ready form.

    For regular fields: returns the field value as-is
    For FK fields: returns the PK (integer) instead of the related object

    This ensures consistent handling across all operations (upsert classification,
    bulk create, bulk update, etc.)

    Args:
        obj: Model instance
        field_name: Name of the field to extract
        model_cls: Model class (optional, will infer from obj if not provided)

    Returns:
        Database-ready value (FK as integer, regular fields as-is)
    """
    if model_cls is None:
        model_cls = obj.__class__

    logger.debug("FIELD_VALUE_EXTRACTION: Getting field '%s' from %s instance (pk=%s)",
                 field_name, obj.__class__.__name__, getattr(obj, 'pk', 'None'))

    try:
        field = model_cls._meta.get_field(field_name)
        logger.debug("FIELD_VALUE_FIELD_FOUND: Field '%s' is %s on %s",
                     field_name, type(field).__name__, field.model.__name__)
    except Exception:  # noqa: BLE001
        # Field doesn't exist - just get attribute
        logger.debug("FIELD_VALUE_FIELD_NOT_FOUND: Field '%s' not found via _meta.get_field, falling back to getattr", field_name)
        value = getattr(obj, field_name, None)
        logger.debug("FIELD_VALUE_FALLBACK: getattr result for '%s': %s (type: %s)", field_name, value, type(value))
        return value

    # Check if it's a ForeignKey
    if isinstance(field, ForeignKey):
        return _extract_fk_value(obj, field_name, field, model_cls)

    # Regular field - get normally
    return _extract_regular_value(obj, field_name, model_cls)


def _extract_fk_value(obj, field_name, field, model_cls):
    """Extract value for a ForeignKey field with MTI handling."""
    attname = field.attname

    # Check if field was explicitly set on this instance
    # If attname is in __dict__, the field was explicitly set (even to None)
    field_was_explicitly_set = attname in obj.__dict__

    logger.debug("🔍 FK_EXTRACT_START: field='%s', attname='%s', obj_class=%s, target_model=%s, obj.pk=%s",
                 field_name, attname, obj.__class__.__name__, model_cls.__name__, getattr(obj, 'pk', 'None'))
    logger.debug("🔍 FK_DICT_CHECK: '%s' in obj.__dict__ = %s, __dict__ keys = %s",
                 attname, field_was_explicitly_set, list(obj.__dict__.keys()))

    # Try direct access first
    # For MTI scenarios, try __dict__ first to avoid Django descriptor database lookups
    if obj.__class__ != model_cls and attname in obj.__dict__:
        value = obj.__dict__[attname]
        logger.debug("🔍 FK_DIRECT_ACCESS_DICT: obj.__dict__['%s'] = %s (type: %s) [MTI bypass]",
                     attname, value, type(value).__name__ if value is not None else 'None')
    else:
        value = getattr(obj, attname, None)
        logger.debug("🔍 FK_DIRECT_ACCESS: getattr(obj, '%s') = %s (type: %s)",
                     attname, value, type(value).__name__ if value is not None else 'None')

    # For MTI scenarios where parent field access fails on child instance
    # OR when the _id field is None but the relationship field is set (common in MTI)
    if value is None:
        logger.debug("🔍 FK_VALUE_NONE: Trying MTI fallback strategies...")

        # Try accessing via relationship object (this handles the MTI case where
        # obj.business is set but obj.business_id is None)
        rel_value = getattr(obj, field_name, None)
        logger.debug("🔍 FK_RELATION_ACCESS: getattr(obj, '%s') = %s (type: %s)",
                     field_name, rel_value, type(rel_value).__name__ if rel_value is not None else 'None')

        if rel_value is not None:
            logger.debug("🔍 FK_RELATION_ATTRS: hasattr(rel_value, 'pk') = %s, pk_value = %s",
                        hasattr(rel_value, 'pk'), getattr(rel_value, 'pk', 'NO_PK_ATTR'))

            if hasattr(rel_value, 'pk'):
                value = rel_value.pk
                logger.debug("✅ FK_MTI_RELATION_SUCCESS: Extracted pk=%s from relationship object", value)
            else:
                logger.debug("❌ FK_RELATION_NO_PK: Relationship object exists but has no pk attribute")
        else:
            logger.debug("🔍 FK_RELATION_NULL: Relationship field is None, checking if DB refresh needed")
            is_mti_case = obj.__class__ != model_cls
            logger.debug("🔍 FK_MTI_CHECK: is_mti=%s (obj_class=%s vs model_cls=%s), explicitly_set=%s",
                        is_mti_case, obj.__class__.__name__, model_cls.__name__, field_was_explicitly_set)

            if is_mti_case and not field_was_explicitly_set:
                logger.debug("🔄 FK_DB_REFRESH: Attempting database refresh for MTI field...")
                value = _try_db_refresh_for_field(obj, model_cls, attname)
            elif is_mti_case and field_was_explicitly_set:
                logger.debug("⚠️ FK_EXPLICIT_NULL: MTI field was explicitly set to None, skipping DB refresh")
            else:
                logger.debug("ℹ️ FK_NO_REFRESH: Not an MTI case, keeping None value")

    logger.debug("🏁 FK_EXTRACT_FINAL: field='%s' → value=%s (type: %s), explicitly_set=%s",
                 field_name, value, type(value).__name__ if value is not None else 'None', field_was_explicitly_set)
    return value


def _extract_regular_value(obj, field_name, model_cls):
    """Extract value for a regular field with MTI handling."""
    # Check if field was explicitly set on this instance
    field_was_explicitly_set = field_name in obj.__dict__

    value = getattr(obj, field_name, None)

    # For MTI scenarios where parent field access fails on child instance
    # Only try fallback if the field was NOT explicitly set
    if value is None and obj.__class__ != model_cls and not field_was_explicitly_set:
        logger.debug("FIELD_VALUE_MTI_REGULAR_FALLBACK: Direct access to '%s' failed on %s, trying MTI fallback",
                     field_name, obj.__class__.__name__)
        value = _try_db_refresh_for_field(obj, model_cls, field_name)

    logger.debug("FIELD_VALUE_REGULAR_EXTRACTION: Regular field '%s', value: %s (type: %s), explicitly_set: %s",
                 field_name, value, type(value), field_was_explicitly_set)
    return value


def _try_db_refresh_for_field(obj, model_cls, field_name):
    """Try to get field value from database for MTI parent fields."""
    logger.debug("🔄 DB_REFRESH_START: Attempting to fetch field='%s' for pk=%s from model=%s",
                 field_name, getattr(obj, 'pk', 'None'), model_cls.__name__)
    try:
        if hasattr(obj, 'pk') and obj.pk is not None:
            logger.debug("🔄 DB_REFRESH_QUERY: Querying %s.objects.filter(pk=%s).first()",
                        model_cls.__name__, obj.pk)
            parent_instance = model_cls.objects.filter(pk=obj.pk).first()

            if parent_instance:
                value = getattr(parent_instance, field_name, None)
                logger.debug("✅ DB_REFRESH_SUCCESS: Found parent instance, field='%s' value=%s (type: %s)",
                            field_name, value, type(value).__name__ if value is not None else 'None')
                return value
            else:
                logger.debug("❌ DB_REFRESH_NO_PARENT: No parent instance found for pk=%s in %s",
                            obj.pk, model_cls.__name__)
        else:
            logger.debug("❌ DB_REFRESH_NO_PK: Object has no pk or pk is None")
    except Exception as e:  # noqa: BLE001
        logger.debug("❌ DB_REFRESH_ERROR: Database refresh failed: %s", e)

    logger.debug("🔄 DB_REFRESH_RETURN_NONE: Returning None")
    return None


def get_field_values_for_db(obj, field_names, model_cls=None):
    """
    Get multiple field values from an object in database-ready form.

    Args:
        obj: Model instance
        field_names: List of field names
        model_cls: Model class (optional)

    Returns:
        Dict of {field_name: db_value}
    """
    if model_cls is None:
        model_cls = obj.__class__

    return {field_name: get_field_value_for_db(obj, field_name, model_cls) for field_name in field_names}


def normalize_field_name_to_db(field_name, model_cls):
    """
    Normalize a field name to its database column name.

    For FK fields referenced by relationship name, returns the attname (e.g., 'business' -> 'business_id')
    For regular fields, returns as-is.

    Args:
        field_name: Field name (can be 'business' or 'business_id')
        model_cls: Model class

    Returns:
        Database column name
    """
    try:
        field = model_cls._meta.get_field(field_name)
        if isinstance(field, ForeignKey):
            return field.attname  # Returns 'business_id' for 'business' field
        return field_name
    except Exception:  # noqa: BLE001
        return field_name


def get_changed_fields(old_obj, new_obj, model_cls, skip_auto_fields=False):
    """
    Get field names that have changed between two model instances.

    Uses Django's field.get_prep_value() for proper database-level comparison.
    This is the canonical implementation used by both RecordChange and ModelAnalyzer.

    Args:
        old_obj: The old model instance
        new_obj: The new model instance
        model_cls: The Django model class
        skip_auto_fields: Whether to skip auto_created fields (default False)

    Returns:
        Set of field names that have changed
    """
    changed = set()

    for field in model_cls._meta.fields:
        # Skip primary key fields - they shouldn't change
        if field.primary_key:
            continue

        # Optionally skip auto-created fields (for bulk operations)
        if skip_auto_fields and field.auto_created:
            continue

        old_val = getattr(old_obj, field.name, None)
        new_val = getattr(new_obj, field.name, None)

        # Use field's get_prep_value for database-ready comparison
        # This handles timezone conversions, type coercions, etc.
        try:
            old_prep = field.get_prep_value(old_val)
            new_prep = field.get_prep_value(new_val)
            if old_prep != new_prep:
                changed.add(field.name)
        except (TypeError, ValueError):
            # Fallback to direct comparison if get_prep_value fails
            if old_val != new_val:
                changed.add(field.name)

    return changed


def get_auto_fields(model_cls, include_auto_now_add=True):
    """
    Get auto fields from a model.

    Args:
        model_cls: Django model class
        include_auto_now_add: Whether to include auto_now_add fields

    Returns:
        List of field names
    """
    fields = []
    for field in model_cls._meta.fields:
        if getattr(field, "auto_now", False) or (include_auto_now_add and getattr(field, "auto_now_add", False)):
            fields.append(field.name)
    return fields


def get_auto_now_only_fields(model_cls):
    """Get only auto_now fields (excluding auto_now_add)."""
    return get_auto_fields(model_cls, include_auto_now_add=False)


def get_fk_fields(model_cls):
    """Get foreign key field names for a model."""
    return [field.name for field in model_cls._meta.concrete_fields if field.is_relation and not field.many_to_many]


def collect_auto_now_fields_for_inheritance_chain(inheritance_chain):
    """Collect auto_now fields across an MTI inheritance chain."""
    all_auto_now = set()
    for model_cls in inheritance_chain:
        all_auto_now.update(get_auto_now_only_fields(model_cls))
    return all_auto_now


def handle_auto_now_fields_for_inheritance_chain(models, instances, for_update=True):
    """
    Unified auto-now field handling for any inheritance chain.

    This replaces the separate collect/pre_save logic with a single comprehensive
    method that handles collection, pre-saving, and field inclusion for updates.

    Args:
        models: List of model classes in inheritance chain
        instances: List of model instances to process
        for_update: Whether this is for an update operation (vs create)

    Returns:
        Set of auto_now field names that should be included in updates
    """
    all_auto_now_fields = set()

    for model_cls in models:
        for field in model_cls._meta.local_fields:
            # For updates, only include auto_now (not auto_now_add)
            # For creates, include both
            if getattr(field, "auto_now", False) or (not for_update and getattr(field, "auto_now_add", False)):
                all_auto_now_fields.add(field.name)

                # Pre-save the field on instances
                for instance in instances:
                    if for_update:
                        # For updates, only pre-save auto_now fields
                        field.pre_save(instance, add=False)
                    else:
                        # For creates, pre-save both auto_now and auto_now_add
                        field.pre_save(instance, add=True)

    return all_auto_now_fields


def pre_save_auto_now_fields(objects, inheritance_chain):
    """Pre-save auto_now fields across inheritance chain."""
    # DEPRECATED: Use handle_auto_now_fields_for_inheritance_chain instead
    auto_now_fields = collect_auto_now_fields_for_inheritance_chain(inheritance_chain)

    for field_name in auto_now_fields:
        # Find which model has this field
        for model_cls in inheritance_chain:
            try:
                field = model_cls._meta.get_field(field_name)
                if getattr(field, "auto_now", False):
                    for obj in objects:
                        field.pre_save(obj, add=False)
                    break
            except Exception:
                continue
