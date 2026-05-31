import asyncio
import httpx

from datetime import datetime
from packaging.version import parse

from .parsers import get_dependency_file
from .display import print_package_info


async def fetch_newest_release(package: str, client: httpx.AsyncClient) -> dict | None:
    try:
        res = await client.get(
            url=f"https://pypi.org/pypi/{package}/json",
            headers={"Accept": "application/json"},
        )
        data = res.json()

        # Handle KeyError for not found packages
        if "releases" not in data or not data["releases"]:
            print(f"No PyPi releases found for: {package}\n")
            return None

        releases = data["releases"]

        # Sort versions, newest first
        versions = sorted(releases.keys(), key=parse, reverse=True)

        # Handle empty release and return latest release according to (version)number
        for version in versions:
            if releases[version]:
                last_release_data = releases[version][-1]
                return dict(release=version, date=last_release_data["upload_time"])

        print(f"No valid release files found for package: {package}\n")
        return None

    # Handle errors outside previous checks
    except (KeyError, IndexError, httpx.HTTPError) as e:
        print(f"Failed to fetch release for '{package}': {e}\n")
        return None


async def run_check(transitive: bool = False):
    deps = get_dependency_file(transitive=transitive)

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[fetch_newest_release(name, client) for name in deps]
        )
        for (name, old_version), new_version in zip(deps.items(), results):
            if new_version:
                days = _days_since(new_version["date"])
                print_package_info(name, new_version, old_version, days)

def _days_since(date: str) -> int:
    return (datetime.now() - datetime.fromisoformat(date)).days
