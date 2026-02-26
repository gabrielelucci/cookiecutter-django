import uuid

from django.db import models
from django.utils.functional import (
    cached_property,
)


class UUIDv7(models.Func):
    """
    Generate a UUIDv7 using the database's native function.

    Only compatible with PostgreSQL 18+.
    """

    function = "uuidv7"
    output_field = models.UUIDField()


class CreatedAtModelMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedAtModelMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TimestampedModel(CreatedAtModelMixin, UpdatedAtModelMixin, models.Model):
    """
    Abstract model that provides created_at and updated_at timestamp fields.
    """

    class Meta:
        abstract = True


class UUIDv7Model(models.Model):
    """
    Abstract model that provides a UUIDv7 primary key.
    """

    id = models.UUIDField(
        primary_key=True,
        default=UUIDv7(),
        editable=False,
    )

    class Meta:
        abstract = True

    @cached_property
    def created(self) -> int:
        return uuid.UUID(bytes=self.id.bytes, version=7).time


class SlugModel(models.Model):
    """
    Abstract model that provides a slug field.
    """

    slug = models.SlugField(unique=True, max_length=100)

    class Meta:
        abstract = True
