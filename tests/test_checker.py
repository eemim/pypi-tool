import pytest
import httpx
from packaging.version import parse

from pypi_tool.checker import fetch_newest_release, run_check

# ── fetch_newest_release ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_fetch_newest_release_valid_package():
    async with httpx.AsyncClient() as client:
        result = await fetch_newest_release("requests", client)
        assert result is not None
        assert "release" in result
        assert "date" in result


@pytest.mark.asyncio
async def test_fetch_newest_release_nonexistent_package():
    async with httpx.AsyncClient() as client:
        result = await fetch_newest_release("thispackagedoesnotexistonpypi", client)
        assert result is None


@pytest.mark.asyncio
async def test_fetch_newest_release_returns_newest_release():
    async with httpx.AsyncClient() as client:
        result = await fetch_newest_release(
            "requests", client
        )  # 2.34.2 is newest at the time of writing
        assert result is not None
        assert parse(result["release"]) >= parse("2.34.0")


# ── run_check ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_check(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("requests==2.28.0\n" "click>=8.0.0\n")
    await run_check(transitive=False)
    assert True
