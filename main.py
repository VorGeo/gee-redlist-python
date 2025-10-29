import typer
from typing_extensions import Annotated
from ee_auth import print_authentication_status

app = typer.Typer(
    name="gee-redlist-python",
    help="Google Earth Engine tools for IUCN Red List analysis",
    add_completion=False,
)


@app.command()
def test_auth():
    """Test Earth Engine authentication status."""
    print("Testing Earth Engine authentication...")
    print_authentication_status()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool,
        typer.Option("--version", "-v", help="Show version and exit"),
    ] = False,
):
    """Main entry point for gee-redlist-python CLI."""
    if version:
        print("gee-redlist-python version 0.1.0")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        print("Hello from gee-redlist-python!")
        print("\nUse --help to see available commands")


if __name__ == "__main__":
    app()
