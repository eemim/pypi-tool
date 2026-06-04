import asyncio
import httpx
import sys

from packaging.version import parse

from .parsers import get_dependency_file
from .display import print_package_info
from .utils import days_since


async def fetch_newest_release(package: str, client: httpx.AsyncClient) -> dict | None:
    try:
        res = await client.get(
            url=f"https://pypi.org/pypi/{package}/json",
            headers={"Accept": "application/json"},
        )
        data = res.json()

        # Handle KeyError for not found packages
        if "releases" not in data or not data["releases"]:
            print(f"\nNo PyPi releases found for: {package}", file=sys.stderr)
            return None

        releases = data["releases"]

        # Sort versions, newest first
        versions = sorted(releases.keys(), key=parse, reverse=True)

        # Handle empty release and return latest release according to (version)number
        for version in versions:
            if releases[version]:
                last_release_data = releases[version][-1]
                return dict(release=version, date=last_release_data["upload_time"])

        print(f"\nNo valid release files found for package: {package}", file=sys.stderr)
        return None

    # Handle errors outside previous checks
    except (KeyError, IndexError, httpx.HTTPError) as e:
        print(f"\nFailed to fetch release for '{package}': {e}", file=sys.stderr)
        return None


async def run_check(transitive: bool = False, json_output: bool = False):
    deps = get_dependency_file(transitive=transitive)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[fetch_newest_release(name, client) for name in deps]
        )

    output = []

    for (name, project_version), new_version in zip(deps.items(), results):
        if new_version:
            days = days_since(new_version["date"])
            if json_output:
                output.append(
                    {
                        "name": name,
                        "latest_pypi_version": new_version["release"],
                        "project_version": project_version,
                        "days_since_pypi_update": days,
                    }
                )
            else:
                print_package_info(name, new_version, project_version, days)

    return output if json_output else None
