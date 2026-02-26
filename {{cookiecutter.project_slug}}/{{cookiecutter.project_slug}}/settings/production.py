from {{ cookiecutter.project_slug }}.settings.base import *

SECRET_KEY = env.str("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    *env.list("DJANGO_ALLOWED_HOSTS", default=[DJANGO_DEFAULT_DOMAIN]),
]

# Security settings for production deployment
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
