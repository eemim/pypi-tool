import pytest

from pypi_tool.display import clean_specifier

# ── clean_specifier ───────────────────────────────────────────────────────────


def test_clean_specifier_pinned():
    assert clean_specifier("==2.28.0") == "2.28.0"


def test_clean_specifier_range():
    assert clean_specifier(">=8.0.0") == "8.0.0"


def test_clean_specifier_unpinned():
    assert "unpinned" in clean_specifier("")
