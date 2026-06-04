# PyPIstale

## INTRODUCTION

Dependency management is a key part of any software project, ensuring you stay up to date with secure and supported packages. Deprecating (and sometimes undeprecating) gives providers control over the lifecycle of their packages and versions. The **npm registry** makes this process clear by allowing creators to flag unmaintained packages and warning developers when they’re about to install deprecated ones.

But what about the **Python Package Index**? Yes, it’s possible — but digging into forum threads on this topic shows that it requires a LOT of work from the maintainer.

And sure, you can use commands like `pip list --outdated`, but that only tells you the latest version. It won’t tell you if the package hasn’t been updated in six years.

Do you really want to be ***dependable*** (pun totally intended) on another coder's motivation to go through all that hassle just for some old project?

If not...

Enter the **PyPIstale** !

## WHAT DOES IT DO?

- Searches your project for a dependency file whether that's a `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.cfg` or a `uv/poetry.lock` file for full transitive dependency inspection
- Scans the dependencies and looks them up on **PyPI**
- Shows your project’s dependency version, the latest **PyPI** version, and ***clearly indicates how long it’s been since the package was last updated on PyPI***
- Comes with a clear color coding for an engaging UX/UI experience!

## HOW TO USE?

Run the tool in your project directory:

```bash
pypistale
```

### FLAGS

| Flag           | Description                                                                                   |
|----------------|-----------------------------------------------------------------------------------------------|
| `--transitive` | Use the project's `.lock` file to include transitive dependencies instead of just direct ones |
| `--json`       | Output results as JSON instead of the default terminal output                                 |

### EXAMPLES

```bash
# Check direct dependencies
pypistale

# Check all dependencies including transitive
pypistale --transitive

# Output results as JSON
pypistale --json

# Combine flags
pypistale --transitive --json
```
#### Example output

```bash
click
• Latest PyPI version: 8.4.1
• Project dependency: 8.0.0
• Last updated in PyPI: 13 days ago

packaging
• Latest PyPI version: 26.2
• Project dependency: 21.0
• Last updated in PyPI: 40 days ago

tomli
• Latest PyPI version: 2.4.1
• Project dependency: 2.0.0
• Last updated in PyPI: 70 days ago
```

#### Example output `--json`

```json
[
  {
    "name": "click",
    "latest_pypi_version": "8.4.1",
    "project_version": ">=8.0.0",
    "days_since_pypi_update": 13
  },
  {
    "name": "packaging",
    "latest_pypi_version": "26.2",
    "project_version": ">=21.0",
    "days_since_pypi_update": 40
  },
  {
    "name": "tomli",
    "latest_pypi_version": "2.4.1",
    "project_version": ">=2.0.0",
    "days_since_pypi_update": 70
  }
]
```
