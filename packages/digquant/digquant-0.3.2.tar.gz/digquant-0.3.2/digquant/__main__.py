import importlib.metadata

import click


@click.group()
def cli() -> None:
    pass


@cli.command()
def test() -> None:
    version = importlib.metadata.version("digquant")
    click.echo(version)


if __name__ == "__main__":
    cli()
