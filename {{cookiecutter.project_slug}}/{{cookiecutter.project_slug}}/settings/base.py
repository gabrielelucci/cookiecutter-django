import re
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
# Only read dotenv file when loading development settings module
if "development" in env.str("DJANGO_SETTINGS_MODULE", ""):
    environ.Env.read_env(env_file=BASE_DIR / ".env")

DEBUG = env.bool("DJANGO_DEBUG", default=False)

TIME_ZONE = env.str("DJANGO_TIME_ZONE", default="UTC")

LANGUAGE_CODE = env.str("DJANGO_LANGUAGE_CODE", default="en")

LANGUAGES = [
    ("en", "English"),
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

DATABASES = {
    "default": {
        **env.db("DJANGO_DATABASE_URL", default="postgres://postgres:debug@db:5432/postgres"),
        "DISABLE_SERVER_SIDE_CURSORS": False,
        "OPTIONS": {
            "options": "-c jit=off -c statement_timeout=30000",
            "server_side_binding": True,
            # See: https://www.psycopg.org/psycopg3/docs/api/pool.html#psycopg_pool.ConnectionPool
            "pool": {
                "min_size": env.int("DJANGO_DB_POOL_MIN_SIZE", default=1),
                "max_size": env.int("DJANGO_DB_POOL_MAX_SIZE", default=10),
                "timeout": env.int("DJANGO_DB_POOL_TIMEOUT", default=10),
            },
        },
    },
}

USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1

ROOT_URLCONF = "{{ cookiecutter.project_slug }}.urls"

INSTALLED_APPS = [
{%- if cookiecutter.use_rest_api == "y" %}
    "corsheaders",
{%- endif %}
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.postgres",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
{%- if cookiecutter.use_vite == "y" %}
    "django_vite",
{%- endif %}
{%- if cookiecutter.use_rest_api == "y" %}
    # REST API
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    # Project apps
    "{{ cookiecutter.project_slug }}.apps.api",
{%- endif %}
    "{{ cookiecutter.project_slug }}.apps.core",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
{%- if cookiecutter.use_rest_api == "y" %}
    "corsheaders.middleware.CorsMiddleware",
{%- endif %}
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            PROJECT_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django.contrib.staticfiles.finders.FileSystemFinder",
]

_PUBLIC_DIR = BASE_DIR / "public"

STATIC_ROOT = _PUBLIC_DIR / "static"
STATIC_URL = "/static/"

MEDIA_ROOT = _PUBLIC_DIR / "media"
MEDIA_URL = "/media/"

{% if cookiecutter.use_vite == "y" -%}
# Django Vite Configuration
_PREFIX = "dist"

DJANGO_VITE = {
    "default": {
        "dev_mode": False,
        "manifest_path": BASE_DIR / "static" / "dist" / "manifest.json",
        "static_url_prefix": _PREFIX,
    }
}

STATICFILES_DIRS = [
    (_PREFIX, BASE_DIR / "static" / _PREFIX),
]


def _immutable_file_test(path, url):
    # Match vite (rollup)-generated hashes, e.g. `main-CNOCtvu6.js`
    return re.match(r"^.+[.-][0-9a-zA-Z_-]{8,12}\..+$", url)


WHITENOISE_IMMUTABLE_FILE_TEST = _immutable_file_test

{% endif -%}
X_FRAME_OPTIONS = "SAMEORIGIN"

# Default domain used for the Django Site, CSRF trusted origins, and CORS origins
DJANGO_DEFAULT_DOMAIN = env.str("DJANGO_DEFAULT_DOMAIN", default="{{ cookiecutter.domain_name }}")

# CSRF settings - build trusted origins from default domain + env overrides
_csrf_origins = []
if DJANGO_DEFAULT_DOMAIN:
    _csrf_origins = [
        f"https://{DJANGO_DEFAULT_DOMAIN}",
        f"http://{DJANGO_DEFAULT_DOMAIN}",
    ]
_csrf_origins += env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
CSRF_TRUSTED_ORIGINS = _csrf_origins
{%- if cookiecutter.use_rest_api == "y" %}

# CORS settings - restrict API access to same-domain only
_cors_origins = []
if DJANGO_DEFAULT_DOMAIN:
    _cors_origins = [
        f"https://{DJANGO_DEFAULT_DOMAIN}",
        f"http://{DJANGO_DEFAULT_DOMAIN}",
    ]
_cors_origins += env.list("DJANGO_CORS_ALLOWED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = _cors_origins
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True
{%- endif %}

# Cookie security settings
CSRF_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_SAMESITE = "Strict"
{%- if cookiecutter.use_rest_api == "y" %}

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "{{ cookiecutter.project_slug }}.apps.api.pagination.MetadataPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "{{ cookiecutter.project_name }} API",
    "DESCRIPTION": "REST API for {{ cookiecutter.project_name }}",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
}
{%- endif %}
