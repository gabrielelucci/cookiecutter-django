# cookiecutter-django

An opinionated [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Django 6.0 projects, containerized with Podman/Docker Compose and PostgreSQL.

## Features

- **Django 6.0** on Python 3.14 with [Granian](https://github.com/emmett-framework/granian) WSGI server
- **PostgreSQL 18** with connection pooling (psycopg3) and tuned configuration
- **Caddy** reverse proxy with automatic HTTPS for production
- **uv** for fast, reproducible Python dependency management and lightweight container builds
- **Optional Vite** integration with Biome for JS/CSS bundling and linting
- **Optional REST API** scaffolding with DRF, drf-spectacular, django-filter, and django-cors-headers
- **Multi-stage container builds** (Alpine-based) for minimal production images
- **Dev tooling**: Ruff, mypy, djade, pytest, coverage, commitizen

## Usage

```bash
# With cookiecutter
cookiecutter gh:YOUR_USERNAME/cookiecutter-django

# Or with cruft
cruft create gh:YOUR_USERNAME/cookiecutter-django
```

### Template variables

| Variable | Default | Description |
|---|---|---|
| `project_name` | My Project | Human-readable project name |
| `project_slug` | *(auto)* | Python package name (derived from project_name) |
| `description` | A Django project. | Short project description |
| `author_name` | Your Name | Author full name |
| `author_email` | you@example.com | Author email |
| `domain_name` | localhost | Production domain for Caddy |
| `python_version` | 3.14 | Python version |
| `postgres_version` | 18 | PostgreSQL version |
| `node_version` | 24 | Node.js version (when Vite is enabled) |
| `use_vite` | n | Include Vite + Biome frontend tooling |
| `use_rest_api` | n | Include DRF + API scaffolding |

## Running the generated project

```bash
# Development
docker compose up

# Production
docker compose -f compose.yaml -f compose.prod.yaml up -d
```

## License

[CC0 1.0 Universal](LICENSE) — Public Domain Dedication
