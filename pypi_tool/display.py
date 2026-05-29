import sys


POSITIVE = ("\U00002022", "\033[0;32m", "\033[96m")
NEUTRAL = ("\U00002022", "\033[0;33m", "\033[96m")
NEGATIVE = ("\U00002022", "\033[0;31m", "\033[96m")
RESET = "\033[0m"

def format_print(result: int):
    if result <= 365:
        return POSITIVE
    elif result >= 730:
        return NEGATIVE
    return NEUTRAL

def print_package_info(name: str, new_version: str, old_version: str, days: int):
    if not sys.stdout.isatty():
        print(f"{name}: {old_version} -> {new_version['release']} (updated {days} days ago)")
        return

    bullet, color, reset = format_print(days)
    print(
        f"{color}{name}\n"
        f"{bullet} Newest version: {new_version['release']}\n"
        f"{bullet} Project dependency: {old_version}\n"
        f"{bullet} Last updated in PyPI: {days} days ago\n"
        f"{reset}"
    )
