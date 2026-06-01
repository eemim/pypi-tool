import re

from datetime import datetime

POSITIVE = ("\U00002022", "\033[0;32m", "\033[96m")
NEUTRAL = ("\U00002022", "\033[0;33m", "\033[96m")
NEGATIVE = ("\U00002022", "\033[0;31m", "\033[96m")
RESET = "\033[0m"

ITALIC = "\033[3m"
RESET_ITALIC = "\033[23m"


def severity_for_days(result: int):
    if result <= 365:
        return POSITIVE
    elif result <= 1095:
        return NEUTRAL
    return NEGATIVE


def format_specifier(specifier: str) -> str:
    """Display specifier in a more user-friendly way, removing operators and formatting unpinned dependencies."""
    if not specifier:
        return f"{ITALIC}unpinned{RESET_ITALIC}"
    return re.sub(r"^[=<>!~^]+", "", specifier).strip()


def days_since(date: str) -> int:
    return (datetime.now() - datetime.fromisoformat(date)).days
