"""Command-line interface for PyPSA Explorer."""

from typing import TYPE_CHECKING, Annotated, cast

if TYPE_CHECKING:
    import pypsa

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from pypsa_explorer import __version__
from pypsa_explorer.app import run_dashboard
from pypsa_explorer.utils.network_loader import parse_cli_network_args

app = typer.Typer(
    name="pypsa-explorer",
    help="🔌 Interactive dashboard for visualizing PyPSA energy system networks",
    add_completion=True,
    rich_markup_mode="rich",
    no_args_is_help=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"[bold cyan]pypsa-explorer[/bold cyan] version [green]{__version__}[/green]")
        raise typer.Exit()


@app.command()
def main(
    networks: Annotated[
        list[str] | None,
        typer.Argument(
            help="Network files to load. Format: path or path:label",
            show_default=False,
        ),
    ] = None,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Host to run the server on",
            rich_help_panel="Server Options",
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Port to run the server on",
            rich_help_panel="Server Options",
        ),
    ] = 8050,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug/--no-debug",
            help="Enable or disable debug mode",
            rich_help_panel="Server Options",
        ),
    ] = True,
    _version: Annotated[
        bool | None,
        typer.Option(
            "--version",
            "-v",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit",
        ),
    ] = None,
) -> None:
    """
    Launch the PyPSA Explorer dashboard.

    [dim]Examples:[/dim]

    [cyan]# Launch interactive landing page (drag-and-drop networks)[/cyan]
    $ pypsa-explorer

    [cyan]# Run with a single network[/cyan]
    $ pypsa-explorer /path/to/network.nc

    [cyan]# Run with multiple networks (with labels)[/cyan]
    $ pypsa-explorer network1.nc:Region1 network2.nc:Region2

    [cyan]# Run with custom host and port[/cyan]
    $ pypsa-explorer --host 0.0.0.0 --port 8080

    [cyan]# Run in production mode (no debug)[/cyan]
    $ pypsa-explorer --no-debug
    """
    # Parse network arguments
    networks_input = None
    if networks:
        try:
            network_paths = parse_cli_network_args(networks)
            networks_input = cast("dict[str, pypsa.Network | str]", network_paths)

            # Display network info
            network_table = Table(title="📊 Networks to Load", show_header=True, header_style="bold magenta")
            network_table.add_column("Label", style="cyan", no_wrap=True)
            network_table.add_column("Path", style="green")

            for label, path in network_paths.items():
                network_table.add_row(label, str(path))

            console.print(network_table)
            console.print()

        except Exception as e:
            console.print(f"[bold red]❌ Error parsing network arguments:[/bold red] {e}")
            raise typer.Exit(1) from None

    # Display startup banner
    network_summary = len(networks_input) if networks_input else "interactive"

    startup_panel = Panel.fit(
        f"""[bold cyan]PyPSA Explorer[/bold cyan] [green]v{__version__}[/green]

🌐 Server: [yellow]{host}:{port}[/yellow]
🐛 Debug Mode: [yellow]{"enabled" if debug else "disabled"}[/yellow]
📁 Networks: [yellow]{network_summary}[/yellow]

[dim]Press Ctrl+C to stop the server[/dim]""",
        title="🔌 Starting Dashboard",
        border_style="cyan",
    )
    console.print(startup_panel)
    console.print()

    # Run the dashboard
    try:
        run_dashboard(
            networks_input=networks_input,
            debug=debug,
            host=host,
            port=port,
            load_default_on_start=networks_input is not None,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]⏹  Shutting down PyPSA Explorer...[/yellow]")
        raise typer.Exit(0) from None
    except Exception as e:
        console.print(f"[bold red]❌ Error:[/bold red] {e}")
        raise typer.Exit(1) from e


def cli() -> None:
    """CLI entry point wrapper."""
    app()


if __name__ == "__main__":
    cli()
