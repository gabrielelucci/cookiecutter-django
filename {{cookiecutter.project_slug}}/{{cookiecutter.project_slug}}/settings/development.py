from {{ cookiecutter.project_slug }}.settings.base import *

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

{% if cookiecutter.use_rest_api == "y" -%}
# Additional CORS allowed origins for development
CORS_ALLOWED_ORIGIN_REGEXES = [r"^http://(?:localhost|127\.0\.0\.1)(?::\d+)?$"]

{% endif -%}
INSTALLED_APPS += ["django_watchfiles"]
{%- if cookiecutter.use_vite == "y" %}

# Vite dev mode: uses HMR dev server instead of built assets
# Overrides base settings to enable live reloading during development
DJANGO_VITE["default"]["dev_mode"] = DEBUG
{%- endif %}
