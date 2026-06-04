import pytest
from pypistale.parsers import (
    parse_requirement,
    parse_lockfile,
    parse_tomlfile,
    parse_pipfile,
    parse_setupcfg,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def requirements_txt(tmp_path):
    f = tmp_path / "requirements.txt"
    f.write_text(
        "requests==2.28.0\n"
        "click>=8.0.0\n"
        "httpx\n"
        "# this is a comment\n"
        "\n"
        "packaging>=21.0,<23\n"
    )
    return str(f)


@pytest.fixture
def lock_file(tmp_path):
    f = tmp_path / "uv.lock"
    f.write_text(
        "[[package]]\n"
        'name = "requests"\n'
        'version = "2.28.0"\n'
        "\n"
        "[[package]]\n"
        'name = "click"\n'
        'version = "8.0.0"\n'
        "\n"
        "[[package]]\n"
        'name = "httpx"\n'  # no version field, should be skipped
    )
    return str(f)


@pytest.fixture
def pyproject_toml_pep621(tmp_path):
    f = tmp_path / "pyproject.toml"
    f.write_text(
        "[project]\n"
        'name = "myproject"\n'
        'version = "0.1.0"\n'
        'description = "A sample project"\n'
        "dependencies = [\n"
        '    "requests==2.28.0",\n'
        '    "click>=8.0.0",\n'
        "]\n"
    )
    return str(f)


@pytest.fixture
def pyproject_toml_poetry(tmp_path):
    f = tmp_path / "pyproject.toml"
    f.write_text(
        "[tool.poetry.dependencies]\n"
        'requests = "^2.28.0"\n'
        'click = "^8.0.0"\n'
        "\n"
        "[tool.poetry.dev-dependencies]\n"
        'pytest = "^7.0.0"\n'
    )
    return str(f)


@pytest.fixture
def pipfile(tmp_path):
    f = tmp_path / "Pipfile"
    f.write_text(
        "[packages]\n"
        'requests = "==2.28.0"\n'
        'click = ">=8.0.0"\n'
        "\n"
        "[dev-packages]\n"
        'pytest = "*"\n'
    )
    return str(f)


@pytest.fixture
def setup_cfg(tmp_path):
    f = tmp_path / "setup.cfg"
    f.write_text(
        "[options]\n"
        "install_requires =\n"
        "    requests==2.28.0\n"
        "    click>=8.0.0\n"
    )
    return str(f)


# ── parse_requirement ─────────────────────────────────────────────────────────


def test_parse_requirement_happy_path(requirements_txt):
    result = parse_requirement(requirements_txt)
    assert "requests" in result
    assert "click" in result
    assert "packaging" in result


def test_parse_requirement_versionless(requirements_txt):
    result = parse_requirement(requirements_txt)
    assert "httpx" in result
    assert result["httpx"] == ""
    assert "packaging" in result


def test_parse_requirement_ignores_comments(requirements_txt):
    result = parse_requirement(requirements_txt)
    assert not any(k.startswith("#") for k in result)


def test_parse_requirement_ignores_blank_lines(requirements_txt):
    result = parse_requirement(requirements_txt)
    assert "" not in result


# ── parse_lockfile ────────────────────────────────────────────────────────────


def test_parse_lockfile_happy_path(lock_file):
    result = parse_lockfile(lock_file)
    assert result["requests"] == "2.28.0"
    assert result["click"] == "8.0.0"


def test_parse_lockfile_empty(tmp_path):
    f = tmp_path / "uv.lock"
    f.write_text("")
    result = parse_lockfile(str(f))
    assert result == {}


def test_parse_lockfile_missing_version(lock_file):
    result = parse_lockfile(lock_file)
    assert "requests" in result
    assert "httpx" not in result


# ── parse_tomlfile ────────────────────────────────────────────────────────────


def test_parse_tomlfile_pep621(pyproject_toml_pep621):
    result = parse_tomlfile(pyproject_toml_pep621)
    assert "requests" in result
    assert "click" in result


def test_parse_tomlfile_poetry(pyproject_toml_poetry):
    result = parse_tomlfile(pyproject_toml_poetry)
    assert "requests" in result
    assert "click" in result
    assert "pytest" in result  # dev deps included


# ── parse_pipfile ─────────────────────────────────────────────────────────────


def test_parse_pipfile_happy_path(pipfile):
    result = parse_pipfile(pipfile)
    assert "requests" in result
    assert "click" in result


def test_parse_pipfile_includes_dev(pipfile):
    result = parse_pipfile(pipfile)
    assert "pytest" in result


# ── parse_setupcfg ────────────────────────────────────────────────────────────


def test_parse_setupcfg_happy_path(setup_cfg):
    result = parse_setupcfg(setup_cfg)
    assert "requests" in result
    assert "click" in result


def test_parse_setupcfg_no_options_section(tmp_path):
    f = tmp_path / "setup.cfg"
    f.write_text("[metadata]\nname = myproject\n")
    result = parse_setupcfg(str(f))
    assert result == {}
