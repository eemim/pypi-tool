import sys

from .utils import format_specifier, severity_for_days


def print_package_info(name: str, new_version: str, project_version: str, days: int):
    if not sys.stdout.isatty():
        print(
            f"{name}: {project_version} -> {new_version['release']} (updated in PyPI {days} days ago)"
        )
        return

    bullet, color, reset = severity_for_days(days)
    print(
        f"\n{color}{name}\n"
        f"{bullet} Latest PyPI version: {new_version['release']}\n"
        f"{bullet} Project dependency: {format_specifier(project_version)}\n"
        f"{bullet} Last updated in PyPI: {days} days ago"
    )
