import click
from .commands import (
    api,
    run
)



@click.group()
def cli():
    """CLI para tai-keycloak. Una herramienta para gestionar Keycloak."""
    pass

cli.add_command(api)
cli.add_command(run)

if __name__ == '__main__':
    cli()