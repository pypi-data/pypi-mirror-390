import importlib.metadata

import click


@click.command()
def cli() -> None:
    version = importlib.metadata.version("digquant")
    click.echo(version)


if __name__ == "__main__":
    cli()
