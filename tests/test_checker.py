import pytest
import httpx
from packaging.version import parse

from pypi_tool.checker import fetch_newest_release, run_check

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def setup_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "requirements.txt").write_text("requests==2.28.0\n")

    (tmp_path / "uv.lock").write_text(
        "[[package]]\n" 'name = "click"\n' 'version = "8.0.0"\n'
    )
    return tmp_path


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
        result = await fetch_newest_release("requests", client)
        assert result is not None
        assert parse(result["release"]) >= parse("2.34.0")


# ── run_check ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_run_check(setup_files):
    # smoke test: just check it completes without raising exceptions
    await run_check(transitive=False)


@pytest.mark.asyncio
async def test_run_check_json_output(setup_files):
    result = await run_check(transitive=False, json_output=True)

    assert isinstance(result, list)
    assert len(result) > 0

    assert "latest_pypi_version" in result[0]
    assert "project_version" in result[0]

    assert result[0]["name"] == "requests"
    assert isinstance(result[0]["days_since_pypi_update"], int)


@pytest.mark.asyncio
async def test_run_check_json_returns_none_without_flag(setup_files):
    result = await run_check(transitive=False, json_output=False)
    assert result is None


@pytest.mark.asyncio
async def test_run_check_transitive_json_output(setup_files):
    result = await run_check(transitive=True, json_output=True)

    assert isinstance(result, list)
    assert len(result) > 0

    assert "latest_pypi_version" in result[0]
    assert "project_version" in result[0]

    assert result[0]["name"] == "click"
    assert isinstance(result[0]["days_since_pypi_update"], int)
