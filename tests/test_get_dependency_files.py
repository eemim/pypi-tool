import pytest
from pypi_tool.parsers import get_dependency_file

# ── get_dependency_file ───────────────────────────────────────────────────────


def test_get_dependency_file_no_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(FileNotFoundError):
        get_dependency_file()


def test_get_dependency_file_transitive_false(tmp_path, monkeypatch):
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
    result = get_dependency_file(transitive=False)
    assert "requests" in result


def test_get_dependency_file_transitive_uses_lockfile(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "pyproject.toml").write_text(
        "[project]\n"
        'name = "myproject"\n'
        'version = "0.1.0"\n'
        'description = "A sample project"\n'
        "dependencies = [\n"
        '        "click==8.0.0"\n'
        "]\n"
    )
    (tmp_path / "uv.lock").write_text(
        "[[package]]\n" 'name = "requests"\n' 'version = "2.28.0"\n'
    )
    result = get_dependency_file(transitive=True)
    assert "requests" in result
