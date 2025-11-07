import logging

from django.db import models

from django_bulk_hooks.manager import BulkHookManager

logger = logging.getLogger(__name__)


class HookModelMixin(models.Model):
    """Mixin providing hook functionality."""

    objects = BulkHookManager()

    class Meta:
        abstract = True

    def clean(self, bypass_hooks=False):
        """
        Override clean() to hook validation hooks.
        This ensures that when Django calls clean() (like in admin forms),
        it hooks the VALIDATE_* hooks for validation only.
        """
        super().clean()

        # If bypass_hooks is True, skip validation hooks
        if bypass_hooks:
            return

        # Delegate to coordinator (consistent with save/delete)
        is_create = self.pk is None
        self.__class__.objects.get_queryset().coordinator.clean(
            [self],
            is_create=is_create,
        )

    def save(self, *args, bypass_hooks=False, **kwargs):
        """
        Save the model instance.

        Delegates to bulk_create/bulk_update which handle all hook logic
        including MTI parent hooks.
        """
        if bypass_hooks:
            # Use super().save() to call Django's default save without our hook logic
            return super().save(*args, **kwargs)

        is_create = self.pk is None

        logger.debug("💾 SAVE_START: model=%s, pk=%s, is_create=%s, __dict__=%s",
                    self.__class__.__name__, self.pk, is_create, list(self.__dict__.keys()))

        if is_create:
            # Delegate to bulk_create which handles all hook logic
            result = self.__class__.objects.bulk_create([self])
            return result[0] if result else self
        # Delegate to bulk_update which handles all hook logic
        update_fields = kwargs.get("update_fields")
        if update_fields is None:
            # Update all non-auto fields
            update_fields = [f.name for f in self.__class__._meta.fields if not f.auto_created and f.name != "id"]

        logger.debug("💾 SAVE_UPDATE_FIELDS: fields=%s (count=%d)", update_fields, len(update_fields))

        # Log FK field values before bulk_update
        for field in self.__class__._meta.fields:
            if field.get_internal_type() == 'ForeignKey' and field.name in update_fields:
                fk_id_value = getattr(self, field.attname, 'NO_ATTR')
                fk_obj_value = getattr(self, field.name, 'NO_ATTR')
                logger.debug("💾 SAVE_FK_CHECK: field=%s, %s=%s, %s=%s (has_pk=%s)",
                            field.name, field.attname, fk_id_value, field.name, fk_obj_value,
                            hasattr(fk_obj_value, 'pk') if fk_obj_value != 'NO_ATTR' else 'N/A')

        self.__class__.objects.bulk_update([self], update_fields)
        return self

    def delete(self, *args, bypass_hooks=False, **kwargs):
        """
        Delete the model instance.

        Delegates to bulk_delete which handles all hook logic
        including MTI parent hooks.
        """
        if bypass_hooks:
            # Use super().delete() to call Django's default delete without our hook logic
            return super().delete(*args, **kwargs)

        # Delegate to bulk_delete (handles both MTI and non-MTI)
        return self.__class__.objects.filter(pk=self.pk).delete()
