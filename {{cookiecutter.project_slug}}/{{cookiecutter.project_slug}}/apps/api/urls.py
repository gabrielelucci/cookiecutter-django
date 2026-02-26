from typing import TYPE_CHECKING

from django.conf import settings
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

app_name = "api"

# ──────────────────────────────────────────────
# Root router
# ──────────────────────────────────────────────
router = routers.DefaultRouter()
# Register your viewsets here:
# router.register("items", ItemViewSet, basename="item")

# ──────────────────────────────────────────────
# URL patterns
# ──────────────────────────────────────────────
urlpatterns: list[URLResolver | URLPattern] = [
    path("", include(router.urls)),
]

if settings.DEBUG:
    # OpenAPI schema & documentation
    urlpatterns.extend(
        [
            path("schema/", SpectacularAPIView.as_view(), name="schema"),
            path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
            path("redoc/", SpectacularRedocView.as_view(url_name="api:schema"), name="redoc"),
        ]
    )
