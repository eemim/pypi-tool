import sys
from pathlib import Path
from collections.abc import Callable
from configparser import ConfigParser
from packaging.requirements import Requirement

try:
    import tomllib  # Python 3.11+

    def load_toml(file):
        return tomllib.load(file)

except ImportError:
    import tomli as tomllib

    def load_toml(file):
        return tomllib.load(file)


# Handle requirements.txt file
def parse_requirement(dependency_file: str) -> dict[str, str]:
    packages = {}
    with open(dependency_file, "r") as file:
        lines = file.readlines()

    for line in lines:
        if line.strip() and not line.strip().startswith("#"):
            req = _parse_requirement_line(line)
            if req:
                name, specifier = req
                packages[name] = specifier
    return packages


# Handle .lock files
# Works for both Poetry and uv.lock files since they have the same format for package entries
def parse_lockfile(dependency_file: str) -> dict[str, str]:
    packages = {}
    with open(dependency_file, "r") as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        if lines[i].strip() == "[[package]]":
            name = version = None
            j = i + 1
            while j < len(lines) and lines[j].strip() != "[[package]]":
                if lines[j].strip().startswith("name ="):
                    name = lines[j].split("=", 1)[1].strip().strip('"')
                elif lines[j].strip().startswith("version ="):
                    version = lines[j].split("=", 1)[1].strip().strip('"')
                j += 1
            if name and version:
                packages[name] = version
            i = j
        else:
            i += 1
    return packages


# Handle pyproject.toml file
def parse_tomlfile(dependency_file: str) -> dict[str, str]:
    with open(dependency_file, "rb") as file:
        data = load_toml(file)

    packages = {}

    # PEP 621 [project.dependencies]
    _parse_dep_list(data.get("project", {}).get("dependencies", []), packages)

    # PEP 621 [project.optional-dependencies] - all groups including dev
    for group_deps in data.get("project", {}).get("optional-dependencies", {}).values():
        _parse_dep_list(group_deps, packages)

    # PEP 735 [dependency-groups] - uv and newer tools
    for group_deps in data.get("dependency-groups", {}).values():
        _parse_dep_list(group_deps, packages)

    # Poetry [tool.poetry.dependencies] and [tool.poetry.dev-dependencies]
    poetry = data.get("tool", {}).get("poetry", {})
    for section in ["dependencies", "dev-dependencies"]:
        packages.update(poetry.get(section, {}))

    # Poetry newer group format [tool.poetry.group.X.dependencies]
    for group in poetry.get("group", {}).values():
        packages.update(group.get("dependencies", {}))

    return packages


# Handle Pipfile file
def parse_pipfile(dependency_file: str) -> dict[str, str]:
    with open(dependency_file, "rb") as file:
        data = load_toml(file)

    packages = {}
    for section in ["packages", "dev-packages"]:
        if section in data:
            packages.update(data[section])
    return packages


# Handle setup.cfg file
def parse_setupcfg(dependency_file: str) -> dict[str, str]:

    config = ConfigParser()
    config.read(dependency_file)

    packages = {}
    if "options" in config and "install_requires" in config["options"]:
        for line in config["options"]["install_requires"].splitlines():
            if line.strip():
                req = _parse_requirement_line(line)
                if req:
                    name, specifier = req
                    packages[name] = specifier
    return packages


# --transitive not set, so we only parse direct dependencies from the main files
# We check for pyproject.toml first, then Pipfile, then setup.cfg, and finally requirements.txt
DIRECT_PARSERS: dict[str, Callable] = {
    "pyproject.toml": parse_tomlfile,
    "Pipfile": parse_pipfile,
    "setup.cfg": parse_setupcfg,
    "requirements.txt": parse_requirement,
}

# --transitive set, so we also parse transitive dependencies from lock files
TRANSITIVE_PARSERS: dict[str, Callable] = {
    "*.lock": parse_lockfile,
}


# Get dependency file and handle it appropriately
def get_dependency_file(transitive: bool = False) -> dict[str, str]:
    if transitive:
        for pattern, parser in TRANSITIVE_PARSERS.items():
            matches = list(Path(".").glob(pattern))
            if matches:
                return parser(str(matches[0]))
        raise FileNotFoundError("No lock file found.")

    # For direct deps, check for pyproject.toml/Pipfile/setup.cfg first
    for pattern, parser in DIRECT_PARSERS.items():
        if pattern.startswith("requirements"):
            continue
        matches = list(Path(".").glob(pattern))
        if matches:
            result = parser(str(matches[0]))
            if result:  # only return if actually found dependencies
                return result

    # Fall back to requirements files, merging all of them (requirements.txt + requirements-dev.txt)
    packages = {}
    for pattern in ["requirements*.txt"]:
        for match in Path(".").glob(pattern):
            packages.update(parse_requirement(str(match)))
    if packages:
        return packages

    raise FileNotFoundError("No supported dependency file found.")


def _parse_requirement_line(line: str) -> tuple[str, str] | None:
    try:
        req = Requirement(line.strip())
        name = req.name
        specifier = str(req.specifier) if req.specifier else ""
        return name, specifier
    except Exception as e:
        print(f"Failed to parse line '{line.strip()}': {e}", file=sys.stderr)
        return None


def _parse_dep_list(deps: list, packages: dict) -> None:
    for dep in deps:
        if isinstance(dep, str):  # skip PEP 735 dicts like {include-group = "typing"}
            req = _parse_requirement_line(dep)
            if req:
                name, specifier = req
                packages[name] = specifier
