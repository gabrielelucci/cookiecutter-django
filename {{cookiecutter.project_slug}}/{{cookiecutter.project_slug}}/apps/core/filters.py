from functools import reduce
from operator import or_
from typing import TYPE_CHECKING, Any, ClassVar

import django_filters
from django.db.models import Q

if TYPE_CHECKING:
    from django.db.models import QuerySet


class TrigramSearchFilterSetMixin(django_filters.FilterSet):
    """Mixin for adding trigram word-similarity search to FilterSets.

    Define ``search_fields`` in the FilterSet's ``Meta`` class to specify which
    fields to search.

    **Index support** - Each field listed in ``search_fields`` should have a
    GIN index using the ``gin_trgm_ops`` operator class so PostgreSQL can
    accelerate filtering via the ``<%`` (word-similar) operator::

        from django.contrib.postgres.indexes import GinIndex

        class Meta:
            indexes = [
                GinIndex(fields=["title"], opclasses=["gin_trgm_ops"],
                         name="mymodel_title_trgm_idx"),
            ]

    Filtering uses the ``trigram_word_similar`` lookup (``<%`` operator) per
    field, combined with ``OR``.  The similarity threshold is controlled by the
    PostgreSQL session-level ``pg_trgm.word_similarity_threshold`` setting
    (default 0.6).  Results keep the queryset's existing ordering.

    The ``lookup_expr="fulltext"`` on the declared filter is unused for
    filtering; it only documents the filter in the API schema.

    Example usage::

        class MyModelFilter(TrigramSearchFilterSetMixin, django_filters.FilterSet):
            class Meta:
                model = MyModel
                fields = ["name", "description"]
                search_fields = ["name", "description"]
    """

    search = django_filters.CharFilter(
        method="search_fulltext",
        label="Search",
        lookup_expr="fulltext",
    )

    class Meta:
        """Expected Meta configuration for TrigramSearchFilterSetMixin.

        Attributes:
            search_fields: List of model field names to search across.
        """

        search_fields: ClassVar[list[str]] = []

    def search_fulltext(
        self, queryset: QuerySet[Any], field_name: str, value: str
    ) -> QuerySet[Any]:
        """Full text search using trigram word similarity on configured fields.

        Uses ``trigram_word_similar`` lookups (GIN-index-accelerated ``<%``
        operator) to filter candidates.  No per-row scoring is performed;
        the queryset retains its original ordering.
        """
        if not value:
            return queryset

        search_fields = getattr(self.Meta, "search_fields", [])
        if not search_fields:
            return queryset

        trigram_q = reduce(
            or_,
            (Q(**{f"{field}__trigram_word_similar": value}) for field in search_fields),
        )
        return queryset.filter(trigram_q)
