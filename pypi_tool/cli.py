import asyncio
import click
import json

from .checker import run_check


@click.command()
@click.option(
    "--transitive", is_flag=True, help="Include transitive dependencies from lock files"
)
@click.option(
    "--json", "json_output", is_flag=True, help="Output results in JSON format"
)
def main(transitive: bool, json_output: bool):
    result = asyncio.run(run_check(transitive=transitive, json_output=json_output))
    if json_output and result:
        click.echo(json.dumps(result, indent=2))
