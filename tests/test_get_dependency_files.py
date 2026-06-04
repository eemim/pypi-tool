import pytest
from pypi_tool.parsers import get_dependency_file

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def setup_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "myproject"\n'
        'version = "0.1.0"\n'
        'description = "A sample project"\n'
        "dependencies = [\n"
        '        "requests==2.28.0"\n'
        "]\n"
    )
    (tmp_path / "uv.lock").write_text(
        "[[package]]\n" 'name = "click"\n' 'version = "8.0.0"\n'
    )
    return tmp_path


# ── get_dependency_file ───────────────────────────────────────────────────────


def test_get_dependency_file_no_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        get_dependency_file()


def test_get_dependency_file_transitive_false(setup_files):
    result = get_dependency_file(transitive=False)
    assert "requests" in result
    assert "click" not in result


def test_get_dependency_file_transitive_uses_lockfile(setup_files):
    result = get_dependency_file(transitive=True)
    assert "click" in result
    assert "requests" not in result


def test_pyproject_toml_preferred_over_requirements(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n" "dependencies = [\n" '    "requests==2.28.0"\n' "]\n"
    )
    (tmp_path / "requirements.txt").write_text("click>=8.0.0\n")
    result = get_dependency_file(transitive=False)
    assert "requests" in result
    assert "click" not in result
