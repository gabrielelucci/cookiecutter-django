#!/usr/bin/env python3
"""Sync resolved dependency versions from a rendered project back into the template source.

Reads the rendered project's uv.lock (and optionally its updated package.json),
then patches the template's pyproject.toml and package.json with bumped version
specifiers. Only raises floors — never downgrades.

Usage:
    python scripts/sync_deps.py /path/to/rendered/project

Exit codes:
    0 — changes were made
    1 — everything is already up to date
    2 — error
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

TEMPLATE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PROJECT_DIR = TEMPLATE_DIR / "{{cookiecutter.project_slug}}"
TEMPLATE_PYPROJECT = TEMPLATE_PROJECT_DIR / "pyproject.toml"
TEMPLATE_PACKAGE_JSON = TEMPLATE_PROJECT_DIR / "package.json"

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


def normalize_name(name: str) -> str:
    """PEP 503 package-name normalisation."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse ``"6.1.3"`` → ``(6, 1, 3)``, ignoring pre-release suffixes."""
    m = re.match(r"([0-9]+(?:\.[0-9]+)*)", version_str)
    if not m:
        return (0,)
    return tuple(int(x) for x in m.group(1).split("."))


def is_prerelease(version_str: str) -> bool:
    return bool(re.search(r"(\.dev|a\d|b\d|rc\d|alpha|beta|pre|post)", version_str, re.I))


# ──────────────────────────────────────────────
# uv.lock parsing
# ──────────────────────────────────────────────


def parse_uv_lock(lock_path: Path) -> dict[str, str]:
    """Return ``{normalised_name: version}`` from a ``uv.lock`` file."""
    with lock_path.open("rb") as fh:
        data = tomllib.load(fh)
    return {
        normalize_name(pkg["name"]): pkg["version"]
        for pkg in data.get("package", [])
    }


# ──────────────────────────────────────────────
# Version-specifier update logic
# ──────────────────────────────────────────────


def update_compatible_release(current_spec: str, resolved_version: str) -> str | None:
    """Bump a ``~=`` specifier's floor to match *resolved_version*.

    ``~=X.Y``   → raise Y if resolved minor is higher (same major).
    ``~=X.Y.Z`` → raise Y.Z if resolved is higher   (same major).
    """
    parts = current_spec.split(".")
    resolved = parse_version(resolved_version)

    if len(resolved) < 2:
        return None

    if len(parts) == 2:
        cur_major, cur_minor = int(parts[0]), int(parts[1])
        if resolved[0] == cur_major and resolved[1] > cur_minor:
            return f"{resolved[0]}.{resolved[1]}"
    elif len(parts) >= 3:
        current = parse_version(current_spec)
        if resolved[0] == current[0] and resolved[1:] > current[1:]:
            return ".".join(str(x) for x in resolved[: len(parts)])

    return None


def update_minimum_version(current_spec: str, resolved_version: str) -> str | None:
    """Bump a ``>=`` specifier to *resolved_version* if it is newer."""
    current = parse_version(current_spec)
    resolved = parse_version(resolved_version)

    max_len = max(len(current), len(resolved))
    cur_padded = current + (0,) * (max_len - len(current))
    res_padded = resolved + (0,) * (max_len - len(resolved))

    if res_padded > cur_padded:
        return resolved_version
    return None


# ──────────────────────────────────────────────
# Template patching — pyproject.toml
# ──────────────────────────────────────────────

# Matches: "django~=6.0"  "psycopg[c,pool]~=3.3"  "django-vite>=3.1.0"
_DEP_RE = re.compile(
    r'"(?P<name>[a-zA-Z0-9][-a-zA-Z0-9._]*)'
    r"(?P<extras>\[[^\]]*\])?"
    r"(?P<op>~=|>=)"
    r'(?P<version>[0-9]+(?:\.[0-9]+)*)"'
)


def update_pyproject(resolved: dict[str, str]) -> list[str]:
    """Regex-patch version specifiers in the **template** ``pyproject.toml``.

    Returns a list of human-readable change descriptions.
    """
    content = TEMPLATE_PYPROJECT.read_text()
    changes: list[str] = []

    def _replace(m: re.Match[str]) -> str:
        pkg_name = m.group("name")
        extras = m.group("extras") or ""
        op = m.group("op")
        ver = m.group("version")

        norm = normalize_name(pkg_name)
        if norm not in resolved:
            return m.group(0)

        res_ver = resolved[norm]

        # Skip pre-release resolutions
        if is_prerelease(res_ver):
            return m.group(0)

        if op == "~=":
            new_ver = update_compatible_release(ver, res_ver)
        elif op == ">=":
            new_ver = update_minimum_version(ver, res_ver)
        else:
            return m.group(0)

        if new_ver is None:
            return m.group(0)

        changes.append(f"  {pkg_name}: {op}{ver} → {op}{new_ver} (resolved {res_ver})")
        return f'"{pkg_name}{extras}{op}{new_ver}"'

    new_content = _DEP_RE.sub(_replace, content)

    if new_content != content:
        TEMPLATE_PYPROJECT.write_text(new_content)

    return changes


# ──────────────────────────────────────────────
# Template patching — package.json
# ──────────────────────────────────────────────


def update_package_json(rendered_path: Path) -> list[str]:
    """Copy bumped ``devDependencies`` from the rendered project back to the template."""
    rendered_pkg = rendered_path / "package.json"
    if not rendered_pkg.exists() or not TEMPLATE_PACKAGE_JSON.exists():
        return []

    rendered_data = json.loads(rendered_pkg.read_text())
    template_data = json.loads(TEMPLATE_PACKAGE_JSON.read_text())

    changes: list[str] = []
    rendered_dev = rendered_data.get("devDependencies", {})
    template_dev = template_data.get("devDependencies", {})

    for pkg, old_ver in template_dev.items():
        if pkg in rendered_dev and rendered_dev[pkg] != old_ver:
            changes.append(f"  {pkg}: {old_ver} → {rendered_dev[pkg]}")
            template_dev[pkg] = rendered_dev[pkg]

    if changes:
        TEMPLATE_PACKAGE_JSON.write_text(json.dumps(template_data, indent="\t") + "\n")

    return changes


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <rendered-project-path>", file=sys.stderr)
        return 2

    rendered = Path(sys.argv[1])
    lock_path = rendered / "uv.lock"

    if not lock_path.exists():
        print(f"Error: {lock_path} not found", file=sys.stderr)
        return 2

    resolved = parse_uv_lock(lock_path)

    py_changes = update_pyproject(resolved)
    js_changes = update_package_json(rendered)

    if py_changes or js_changes:
        print("### Dependency Updates\n")
        if py_changes:
            print("**Python (pyproject.toml)**")
            for c in sorted(py_changes):
                print(c)
            print()
        if js_changes:
            print("**JavaScript (package.json)**")
            for c in sorted(js_changes):
                print(c)
            print()
        return 0

    print("All template dependencies are up to date.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
