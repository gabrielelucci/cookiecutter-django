import math
from typing import Any

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class MetadataPagination(PageNumberPagination):
    """Custom pagination that includes metadata about the result set and available filters."""

    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data: list[Any]) -> Response:
        if self.page is None or self.request is None:
            msg = "Cannot build paginated response without a page and request."
            raise ValueError(msg)
        total_count = self.page.paginator.count
        page_size = self.get_page_size(self.request) or self.page_size
        if page_size is None:
            msg = "page_size must be set for paginated responses."
            raise ValueError(msg)
        return Response(
            {
                "meta": {
                    "total_count": total_count,
                    "page_count": math.ceil(total_count / page_size),
                    "page_size": page_size,
                    "current_page": self.page.number,
                    "filters": self._get_available_filters(),
                },
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        return {
            "type": "object",
            "required": ["meta", "links", "results"],
            "properties": {
                "meta": {
                    "type": "object",
                    "properties": {
                        "total_count": {
                            "type": "integer",
                            "example": 42,
                        },
                        "page_count": {
                            "type": "integer",
                            "example": 3,
                        },
                        "page_size": {
                            "type": "integer",
                            "example": 20,
                        },
                        "current_page": {
                            "type": "integer",
                            "example": 1,
                        },
                        "filters": {
                            "type": "object",
                            "description": "Available filter options for this endpoint.",
                        },
                    },
                },
                "links": {
                    "type": "object",
                    "properties": {
                        "next": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "example": "http://api.example.org/items/?page=2",
                        },
                        "previous": {
                            "type": "string",
                            "nullable": True,
                            "format": "uri",
                            "example": "http://api.example.org/items/?page=1",
                        },
                    },
                },
                "results": schema,
            },
        }

    def _get_available_filters(self) -> dict[str, Any]:
        """Extract available filter options from the view's filterset class."""
        request = getattr(self, "request", None)
        if request is None:
            return {}
        view = request.parser_context.get("view")
        if view is None:
            return {}
        return self._get_filterset_options(view)

    def _get_filterset_options(self, view: Any) -> dict[str, Any]:
        """Extract filter choices from the view's filterset_class."""
        filterset_class = getattr(view, "filterset_class", None)
        if not filterset_class:
            return {}

        filters: dict[str, Any] = {}
        for name, filter_field in filterset_class.base_filters.items():
            choices = getattr(filter_field.field, "choices", None)
            if choices is None:
                choices = getattr(filter_field, "choices", None)
            if choices is not None:
                items = choices() if callable(choices) else choices
                options = [
                    {"value": str(value), "label": str(label)}
                    for value, label in items
                    if value  # Skip empty choices
                ]
                if options:
                    filters[name] = {"type": "choices", "options": options}
            elif hasattr(filter_field, "lookup_expr"):
                filters[name] = {
                    "type": filter_field.lookup_expr or "exact",
                }

        return filters
