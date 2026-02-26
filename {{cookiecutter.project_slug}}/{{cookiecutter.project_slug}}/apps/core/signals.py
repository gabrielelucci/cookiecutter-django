from typing import Any

from django.conf import settings
from django.db.models.signals import post_migrate


def update_default_site_domain(sender: Any, **kwargs: Any) -> None:
    """
    Update the default Site's domain and name from the DJANGO_DEFAULT_DOMAIN
    setting after migrations run. Creates the site if it doesn't exist.
    """
    domain = getattr(settings, "DJANGO_DEFAULT_DOMAIN", "")
    if not domain:
        return

    from django.contrib.sites.models import Site  # noqa: PLC0415

    Site.objects.update_or_create(
        pk=settings.SITE_ID,
        defaults={"domain": domain, "name": domain},
    )


def connect() -> None:
    post_migrate.connect(update_default_site_domain)
