"""Main application module for PyPSA Explorer dashboard."""

import dash
import dash_bootstrap_components as dbc
import pypsa
import pypsa.consistency

from pypsa_explorer.callbacks import register_all_callbacks
from pypsa_explorer.config import get_html_template, setup_plotly_theme
from pypsa_explorer.layouts.dashboard import create_dashboard_layout
from pypsa_explorer.utils.helpers import resolve_default_network_path
from pypsa_explorer.utils.network_loader import load_networks


def create_app(
    networks_input: dict[str, pypsa.Network | str] | str | None = None,
    title: str = "PyPSA Explorer",
    debug: bool = False,  # noqa: ARG001
    *,
    load_default_on_start: bool = True,
    default_network_path: str = "demo-network.nc",
) -> dash.Dash:
    """
    Create and configure the Dash application.

    Parameters
    ----------
    networks_input : dict, str, or None
        Networks to load. Can be:
        - dict: {label: network_object_or_path}
        - str: Path to a single network file
        - None: Behaviour depends on ``load_default_on_start``
    title : str
        Dashboard title
    debug : bool
        Whether to run in debug mode
    load_default_on_start : bool
        When ``True`` (default) load the bundled demo network if ``networks_input`` is ``None``.
        When ``False`` start without networks and rely on runtime uploads or sample loading.
    default_network_path : str
        Filesystem path to the bundled demo network used when loading the example network.

    Returns
    -------
    dash.Dash
        Configured Dash application instance
    """
    # Setup Plotly theme
    setup_plotly_theme()

    resolved_default_path = resolve_default_network_path(default_network_path)
    default_path_str = str(resolved_default_path) if resolved_default_path else default_network_path

    # Load networks while allowing empty start states
    if networks_input is None and not load_default_on_start:
        networks: dict[str, pypsa.Network] = {}
    else:
        networks = load_networks(networks_input, default_network_path=default_path_str)

    # Get the first network as the active network initially (if any)
    network_labels = list(networks.keys())
    active_network_label = network_labels[0] if network_labels else None

    # Initialize Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title=title,
    )

    # Set custom HTML template with embedded CSS
    app.index_string = get_html_template()

    # Create layout
    app.layout = create_dashboard_layout(
        networks,
        active_network_label,
        default_network_path=default_path_str,
    )

    # Register all callbacks
    register_all_callbacks(app, networks, default_network_path=default_path_str)

    return app


def run_dashboard(
    networks_input: dict[str, pypsa.Network | str] | str | None = None,
    debug: bool = True,
    host: str = "127.0.0.1",
    port: int = 8050,
    *,
    load_default_on_start: bool = True,
    default_network_path: str = "demo-network.nc",
) -> None:
    """
    Run the PyPSA Explorer dashboard.

    Parameters
    ----------
    networks_input : dict, str, or None
        Networks to load. Can be:
        - dict: {label: network_object_or_path} mapping labels to Network objects or file paths
        - str: Single path to a network file
        - None: Behaviour depends on ``load_default_on_start``
    debug : bool
        Whether to run in debug mode
    host : str
        Host to run the server on
    port : int
        Port to run the server on
    load_default_on_start : bool
        Controls whether the bundled demo network loads automatically when ``networks_input`` is ``None``.
    default_network_path : str
        Filesystem path to the bundled demo network used for the sample loader.
    """
    app = create_app(
        networks_input,
        debug=debug,
        load_default_on_start=load_default_on_start,
        default_network_path=default_network_path,
    )

    print(f"Starting PyPSA Explorer Dashboard on http://{host}:{port}")
    print("Press Ctrl+C to stop the server")

    app.run(debug=debug, host=host, port=port)
