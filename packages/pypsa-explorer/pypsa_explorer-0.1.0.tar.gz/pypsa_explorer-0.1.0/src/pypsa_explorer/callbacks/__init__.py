"""Callback functions for PyPSA Explorer dashboard interactivity."""

from pypsa_explorer.callbacks.data_explorer import register_data_explorer_callbacks
from pypsa_explorer.callbacks.filters import register_filter_callbacks
from pypsa_explorer.callbacks.navigation import register_navigation_callbacks
from pypsa_explorer.callbacks.network import register_network_callbacks
from pypsa_explorer.callbacks.theme import register_theme_callbacks
from pypsa_explorer.callbacks.visualizations import register_visualization_callbacks

__all__ = [
    "register_data_explorer_callbacks",
    "register_filter_callbacks",
    "register_navigation_callbacks",
    "register_network_callbacks",
    "register_theme_callbacks",
    "register_visualization_callbacks",
]


def register_all_callbacks(app, networks: dict, *, default_network_path: str) -> None:
    """
    Register all dashboard callbacks.

    Parameters
    ----------
    app : dash.Dash
        The Dash application instance
    networks : dict
        Dictionary of loaded PyPSA networks
    """
    register_filter_callbacks(app)
    register_navigation_callbacks(app)
    register_network_callbacks(app, networks, default_network_path=default_network_path)
    register_visualization_callbacks(app, networks)
    register_data_explorer_callbacks(app, networks)
    register_theme_callbacks(app)
