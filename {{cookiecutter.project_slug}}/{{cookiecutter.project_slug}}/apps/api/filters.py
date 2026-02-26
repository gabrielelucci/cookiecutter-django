from typing import TYPE_CHECKING, Any

import django_filters
from django import forms
from django.core.cache import cache
from django.db.models import Q

if TYPE_CHECKING:
    from collections.abc import Callable

_DEFAULT_CHOICES_TTL = 300  # 5 minutes


def cached_choices(
    cache_key: str,
    queryset_factory: Callable[[], list[tuple[str, str]]],
    ttl: int = _DEFAULT_CHOICES_TTL,
) -> Callable[[], list[tuple[str, str]]]:
    """Return a callable suitable for ``django_filters.Filter(choices=...)``.

    The first call executes *queryset_factory*, caches the result under
    *cache_key* for *ttl* seconds, and subsequent calls within the TTL
    window return the cached value without hitting the database.
    """

    def _choices() -> list[tuple[str, str]]:
        cached_value = cache.get(cache_key)
        if cached_value is not None:
            return cached_value
        choices = queryset_factory()
        cache.set(cache_key, choices, ttl)
        return choices

    return _choices


class GroupedCSVWidget(forms.TextInput):
    """Widget that reads repeated query params, splitting each by comma.

    Produces a list of groups (list of lists) enabling both OR and AND
    semantics:

    - Repeated params provide OR groups:  ``?tags=a&tags=b``  → ``[["a"], ["b"]]``
    - Comma-separated values provide AND:  ``?tags=a,b``      → ``[["a", "b"]]``
    - Combined:  ``?tags=a,b&tags=c``                         → ``[["a", "b"], ["c"]]``
    """

    def value_from_datadict(self, data: Any, files: Any, name: str) -> list[list[str]]:
        values = data.getlist(name)
        groups: list[list[str]] = []
        for raw in values:
            group = [v.strip() for v in raw.split(",") if v.strip()]
            if group:
                groups.append(group)
        return groups


class GroupedCSVField(forms.Field):
    """Form field that passes through the list-of-lists from :class:`GroupedCSVWidget`."""

    widget = GroupedCSVWidget

    def clean(self, value: list[list[str]]) -> list[list[str]]:
        # Skip the parent's type coercion but preserve the ``required`` check.
        if not value and self.required:
            raise forms.ValidationError(self.error_messages["required"], code="required")
        return value or []


class TagGroupFilter(django_filters.Filter):
    """Filter supporting OR between repeated params and AND within CSV values.

    Designed for tag-like many-to-many relationships::

        ?tags=nutrition&tags=health        →  nutrition OR health
        ?tags=nutrition,health             →  nutrition AND health
        ?tags=nutrition,health&tags=sport  →  (nutrition AND health) OR sport
    """

    field_class = GroupedCSVField

    def filter(self, qs: Any, value: list[list[str]]) -> Any:
        if not value:
            return qs

        # Fast path: all single-value groups → simple OR via __in
        if all(len(group) == 1 for group in value):
            tags = [group[0] for group in value]
            return qs.filter(**{f"{self.field_name}__in": tags}).distinct()

        # Mixed OR / AND
        combined_q = Q()
        for group in value:
            if len(group) == 1:
                combined_q |= Q(**{self.field_name: group[0]})
            else:
                # AND: item must match ALL tags in this group
                sub = qs.model.objects.all()
                for tag in group:
                    sub = sub.filter(**{self.field_name: tag})
                combined_q |= Q(pk__in=sub.values("pk"))

        return qs.filter(combined_q).distinct()
