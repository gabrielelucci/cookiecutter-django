"""Post-generation hook for cookiecutter-django template."""

import os
import shutil

USE_VITE = "{{ cookiecutter.use_vite }}" == "y"
USE_REST_API = "{{ cookiecutter.use_rest_api }}" == "y"


def remove_path(path: str) -> None:
    """Remove a file or directory if it exists."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def main() -> None:
    project_slug = "{{ cookiecutter.project_slug }}"

    # Make manage.py executable
    os.chmod("manage.py", 0o755)

    # Make devcontainer scripts executable
    for script in [".devcontainer/on-create.sh", ".devcontainer/post-create.sh"]:
        if os.path.isfile(script):
            os.chmod(script, 0o755)

    # Make container start script executable
    start_script = os.path.join("containers", "django", "start")
    if os.path.isfile(start_script):
        os.chmod(start_script, 0o755)

    if not USE_REST_API:
        remove_path(os.path.join(project_slug, "apps", "api"))
        # Remove core/filters.py (depends on django-filter)
        remove_path(os.path.join(project_slug, "apps", "core", "filters.py"))

    if not USE_VITE:
        remove_path("package.json")
        remove_path("package-lock.json")
        remove_path("vite.config.js")
        remove_path("biome.jsonc")
        remove_path(".npmrc")
        remove_path("static")

    print()
    print("=" * 60)
    print(f"  Project '{{ cookiecutter.project_name }}' created successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print()
    print("  cd {{ cookiecutter.project_slug }}")
    print("  git init")
    print("  uv sync")
    if USE_VITE:
        print("  npm install")
        print("  npm run build")
    print("  cp .env.example .env  # Edit with your settings")
    print("  uv run python manage.py migrate")
    print("  uv run python manage.py createsuperuser")
    print("  uv run python manage.py runserver")
    print()
    if USE_REST_API:
        print("  API docs available at: /api/v1/docs/ (in DEBUG mode)")
        print()


if __name__ == "__main__":
    main()
