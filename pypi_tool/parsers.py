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
    for dep in data.get("project", {}).get("dependencies", []):
        req = _parse_requirement_line(dep)
        if req:
            name, specifier = req
            packages[name] = specifier

    # Poetry [tool.poetry.dependencies]
    for section in ["dependencies", "dev-dependencies"]:
        packages.update(data.get("tool", {}).get("poetry", {}).get(section, {}))

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
DIRECT_PARSERS: dict[str, Callable] = {
    "requirements.txt": parse_requirement,
    "pyproject.toml": parse_tomlfile,
    "Pipfile": parse_pipfile,
    "setup.cfg": parse_setupcfg,
}

# --transitive set, so we also parse transitive dependencies from lock files
TRANSITIVE_PARSERS: dict[str, Callable] = {
    "*.lock": parse_lockfile,
}


# Get dependency file and handle it appropriately
def get_dependency_file(transitive: bool = False) -> dict[str, str] | None:
    parsers = TRANSITIVE_PARSERS if transitive else DIRECT_PARSERS
    for pattern, parser in parsers.items():
        matching_files = list(Path(".").glob(pattern))
        if matching_files:
            return parser(str(matching_files[0]))
    raise FileNotFoundError(
        "No supported dependency file found in the current directory."
    )


def _parse_requirement_line(line: str) -> tuple[str, str] | None:
    try:
        req = Requirement(line.strip())
        name = req.name
        specifier = str(req.specifier) if req.specifier else ""
        return name, specifier
    except Exception as e:
        print(f"Failed to parse line '{line.strip()}': {e}")
        return None
