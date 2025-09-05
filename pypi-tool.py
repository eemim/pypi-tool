import httpx
from packaging.version import parse
import os
from packaging.requirements import Requirement
from packaging.specifiers import Specifier
from datetime import datetime
import asyncio

POSITIVE= ("\U00002022", "\033[0;32m", "\U0001F600", "\033[96m")
NEUTRAL= ("\U00002022", "\033[0;33m", "\U0001F914", "\033[96m")
NEGATIVE= ("\U00002022", "\033[0;31m", "\U0001F4A9", "\033[96m")


async def fetch_newest_release(package: str, client: httpx.AsyncClient):
    try:
        res = await client.get(
            url=f'https://pypi.org/pypi/{package}/json',
            headers={"Accept": "application/json"}
        )
        data = res.json()

        # Handle KeyError for not found packages
        if 'releases' not in data or not data['releases']:
            print(f"No PyPi releases found for: {package}\n")
            return None

        releases = data['releases']

        # Sort versions, newest first
        versions = sorted(releases.keys(), key=parse, reverse=True)

        # Handle empty release and return latest release according to (version)number
        for version in versions:
            if releases[version]:
                last_release_data = releases[version][-1]
                return dict(release=version, date=last_release_data['upload_time'])

        print(f"No valid release files found for package: {package}\n")
        return None
    
    # Handle errors outside previous checks
    except (KeyError, IndexError, httpx.HTTPError) as e:
        print(f"Failed to fetch release for '{package}': {e}\n")
        return None

'''
Now runs in cwd, optional solution to run where the script is:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    for file in os.listdir(SCRIPT_DIR):
'''

# Get dependency file and handle it appropriately
def get_dependency_file():
    for file in os.listdir("."):
        if file == "requirements.txt":
            return get_requirement_dependencies(file)
        elif file.endswith(".lock"):
            return get_lockfile_dependencies(file)
    raise FileNotFoundError("No dependency file detected")

# Handle requirements.txt file
def get_requirement_dependencies(dependency_file: str):
    packages={}
    with open(dependency_file, 'r') as file:
        lines = file.readlines()

    for line in lines:
        if line.strip() and not line.strip().startswith('#'):
            req = Requirement(line)
            packages.update({req.name: Specifier(str(req.specifier)).version})
    return packages

# Handle .lock files
def get_lockfile_dependencies(dependency_file: str):
    packages={}
    with open(dependency_file, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.strip() == '[[package]]':
            # boundary check
            if i + 1 < len(lines):
                packages.update(
                    { lines[i + 1].strip().removeprefix('name = ').replace('"', '')
                    : lines[i + 2].strip().removeprefix('version = ').replace('"', '')}
                    )
    return packages

def format_print(result: int):
    if result <= 365:
        return POSITIVE
    elif result >= 730:
        return NEGATIVE
    return NEUTRAL

def handle_dates(date: str):
    delta = datetime.now() - datetime.fromisoformat(date)
    
    return delta.days

async def compare_dependencies():
    deps = get_dependency_file()

    async with httpx.AsyncClient() as client:
        coros = [
            fetch_newest_release(name, client)
            for name in deps.keys()
        ]
        results = await asyncio.gather(*coros)

        for dep_version, new_version in zip(deps.items(), results):
            name, old_version = dep_version
            if new_version:
                days = handle_dates(new_version['date'])
                bullet, color, face, reset = format_print(days)

                print( 
                f"{color}{name}\n"
                f"{bullet} Newest version: {new_version.get('release')}\n"
                f"{bullet} Project dependency: {old_version}\n"
                f"{bullet} Last updated: {days} days ago {face}\n"
                f"{reset}"
                    )

# run the tool
if __name__ == "__main__":

    asyncio.run(compare_dependencies())