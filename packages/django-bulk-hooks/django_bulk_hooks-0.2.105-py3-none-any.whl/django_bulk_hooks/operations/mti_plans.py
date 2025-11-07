"""
MTI operation plans - Data structures for multi-table inheritance operations.

These are pure data structures returned by MTIHandler to be executed by BulkExecutor.
This separates planning (logic) from execution (database operations).
"""

from dataclasses import dataclass
from dataclasses import field
from typing import Any


@dataclass
class ParentLevel:
    """
    Represents one level in the parent hierarchy for MTI bulk create.

    Attributes:
        model_class: The parent model class for this level
        objects: List of parent instances to create
        original_object_map: Maps parent instance id() -> original object id()
        update_conflicts: Whether to enable UPSERT for this level
        unique_fields: Fields for conflict detection (if update_conflicts=True)
        update_fields: Fields to update on conflict (if update_conflicts=True)
    """

    model_class: Any
    objects: list[Any]
    original_object_map: dict[int, int] = field(default_factory=dict)
    update_conflicts: bool = False
    unique_fields: list[str] = field(default_factory=list)
    update_fields: list[str] = field(default_factory=list)


@dataclass
class MTICreatePlan:
    """
    Plan for executing bulk_create on an MTI model.

    This plan describes WHAT to create, not HOW to create it.
    The executor is responsible for executing this plan.

    Attributes:
        inheritance_chain: List of model classes from root to child
        parent_levels: List of ParentLevel objects, one per parent model
        child_objects: List of child instances to create (not yet with parent links)
        child_model: The child model class
        original_objects: Original objects provided by user
        batch_size: Batch size for operations
        existing_record_ids: Set of id() of original objects that represent existing DB records
        update_conflicts: Whether this is an upsert operation
        unique_fields: Fields used for conflict detection (original, unfiltered)
        update_fields: Fields to update on conflict (original, unfiltered)
        child_unique_fields: Pre-filtered field objects for child table conflict detection
        child_update_fields: Pre-filtered field objects for child table updates
    """

    inheritance_chain: list[Any]
    parent_levels: list[ParentLevel]
    child_objects: list[Any]
    child_model: Any
    original_objects: list[Any]
    batch_size: int = None
    existing_record_ids: set = field(default_factory=set)
    update_conflicts: bool = False
    unique_fields: list[str] = field(default_factory=list)
    update_fields: list[str] = field(default_factory=list)
    child_unique_fields: list = field(default_factory=list)  # Field objects for child table
    child_update_fields: list = field(default_factory=list)  # Field objects for child table


@dataclass
class ModelFieldGroup:
    """
    Represents fields to update for one model in the inheritance chain.

    Attributes:
        model_class: The model class
        fields: List of field names to update on this model
        filter_field: Field to use for filtering (e.g., 'pk' or parent link attname)
    """

    model_class: Any
    fields: list[str]
    filter_field: str = "pk"


@dataclass
class MTIUpdatePlan:
    """
    Plan for executing bulk_update on an MTI model.

    Attributes:
        inheritance_chain: List of model classes from root to child
        field_groups: List of ModelFieldGroup objects
        objects: Objects to update
        batch_size: Batch size for operations
    """

    inheritance_chain: list[Any]
    field_groups: list[ModelFieldGroup]
    objects: list[Any]
    batch_size: int = None
