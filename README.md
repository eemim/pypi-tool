# PyPI-tool

## INTRODUCTION

Dependency management is a key part of any software project, ensuring you stay up to date with secure and supported packages. Deprecating (and sometimes undeprecating) gives providers control over the lifecycle of their packages and versions. The **npm registry** makes this process clear by allowing creators to flag unmaintained packages and warning developers when they’re about to install deprecated ones.

But what about the **Python Package Index**? Yes, it’s possible — but digging into forum threads on this topic shows that it requires a LOT of work from the maintainer.

And sure, you can use commands like `pip list --outdated`, but that only tells you the latest version. It won’t tell you if the package hasn’t been updated in six years.

Do you really want to be ***dependable*** (pun totally intended) on another coder's motivation to go through all that hassle just for some old project?

If not...

Enter the **PyPI-tool** !

## WHAT DOES IT DO?

- Searches your project for a dependency file whether that's a `requirements.txt`, `pyproject.toml`, `Pipfile`, `setup.cfg` or a `.lock` file for full transitive dependency inspection
- Scans the dependencies and looks them up on **PyPI**
- Shows your project’s dependency version, the latest **PyPI** version, and ***clearly indicates how long it’s been since the package was last updated on PyPI***
- Comes with a clear color coding for an engaging UX/UI experience!

## HOW TO USE?
> ***TBD***

Run the tool in your project directory:

```bash
pypi-tool
```

### FLAGS

| Flag           | Description                                                                                   |
|----------------|-----------------------------------------------------------------------------------------------|
| `--transitive` | Use the project's `.lock` file to include transitive dependencies instead of just direct ones |
| `--json`       | Output results as JSON instead of the default terminal output                                 |

### EXAMPLES

```bash
# Check direct dependencies
pypi-tool

# Check all dependencies including transitive
pypi-tool --transitive

# Output results as JSON
pypi-tool --json

# Combine flags
pypi-tool --transitive --json
```
#### Example output

```bash
click
• Latest PyPI version: 8.4.1
• Project dependency: 8.0.0
• Last updated in PyPI: 10 days ago

packaging
• Latest PyPI version: 26.2
• Project dependency: 21.0
• Last updated in PyPI: 37 days ago

pytest
• Latest PyPI version: 9.0.3
• Project dependency: 8.3.5
• Last updated in PyPI: 54 days ago
```

