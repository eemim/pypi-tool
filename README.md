# PyPI-tool

## INTRODUCTION

Dependency management is a key part of any software project, ensuring you stay up to date with secure and supported packages. Deprecating (and sometimes undeprecating) gives providers control over the lifecycle of their packages and versions. The **npm registry** makes this process clear by allowing creators to flag unmaintained packages and warning developers when they’re about to install deprecated ones.

But what about the **Python Package Index**? Yes, it’s possible — but digging into forum threads on this topic shows that it requires a LOT of work from the maintainer.

And sure, you can use commands like `pip list --outdated`, but that only tells you the latest version. It won’t tell you if the package hasn’t been updated in six years.

Do you really want to be ***dependable*** (pun totally intended) on another coder's motivation to go through all that hassle just for some old project?

If not...

Enter the **PyPI-tool** !

## WHAT DOES IT DO?

- Searches the dependency file in your project, wheter it's a `.lock` file or `requirements.txt`
- Scans the dependencies and looks them up on **PyPI**
- Shows your project’s dependency version, the latest **PyPI** version, and ***clearly indicates how long it’s been since the package was last updated on PyPI***
- Comes with a clear color coding and suitable icons for an engaging UX/UI experience!

## HOW TO USE?

Just copy the code into your project and run it from the root directory via the terminal!
