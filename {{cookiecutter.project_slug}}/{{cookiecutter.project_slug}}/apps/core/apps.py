from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "{{ cookiecutter.project_slug }}.apps.core"
    verbose_name = "Core"

    def ready(self) -> None:
        from {{ cookiecutter.project_slug }}.apps.core import signals  # noqa: PLC0415

        signals.connect()
