import pytest

from pypistale.utils import format_specifier

# ── format_specifier ───────────────────────────────────────────────────────────


def test_clean_specifier_pinned():
    assert format_specifier("==2.28.0") == "2.28.0"


def test_clean_specifier_range():
    assert format_specifier(">=8.0.0") == "8.0.0"


def test_clean_specifier_unpinned():
    assert "unpinned" in format_specifier("")
