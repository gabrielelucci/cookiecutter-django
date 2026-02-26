from typing import TYPE_CHECKING

from django.conf import settings
from django.contrib import admin
from django.urls import {% if cookiecutter.use_rest_api == "y" %}include, {% endif %}path

from {{ cookiecutter.project_slug }}.apps.core.views import healthz

if TYPE_CHECKING:
    from django.urls import URLPattern, URLResolver

urlpatterns: list[URLResolver | URLPattern] = [
    path("healthz/", healthz, name="healthz"),
    path("admin/", admin.site.urls),
{%- if cookiecutter.use_rest_api == "y" %}
    path("api/v1/", include("{{ cookiecutter.project_slug }}.apps.api.urls")),
{%- endif %}
]

# Serve media files in development
if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
