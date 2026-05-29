import asyncio
import click
from .checker import run_check

@click.command()
@click.option("--transitive", is_flag=True, help="Include transitive dependencies from lock files")
def main(transitive: bool):
    asyncio.run(run_check(transitive=transitive))
