"""Filter-related callbacks for PyPSA Explorer dashboard."""

from typing import Any

from dash import Input, Output


def register_filter_callbacks(app) -> None:
    """Register filter-related callbacks."""

    @app.callback(
        [
            Output("global-country-selector", "disabled"),
            Output("global-country-selector", "value"),
        ],
        [Input("global-country-mode", "value")],
    )
    def toggle_global_country_selector(mode: str) -> tuple[bool, list[Any]]:
        """Enable/disable country selector based on mode."""
        if mode == "All":
            return True, []
        else:
            return False, []

    @app.callback(
        [
            Output("global-carrier-selector-container", "style"),
            Output("carrier-not-applicable-text", "style"),
            Output("active-tab-store", "data"),
        ],
        [Input("tabs", "value")],
    )
    def handle_tab_specific_ui(active_tab: str) -> tuple[dict[str, str], dict[str, str], str]:
        """Handle UI elements based on the active tab."""
        if active_tab in ["capex", "opex"]:
            # Hide carrier selector for CAPEX/OPEX tabs
            return {"display": "none"}, {"display": "block"}, active_tab
        else:
            # Show carrier selector for other tabs
            return {"display": "block"}, {"display": "none"}, active_tab
