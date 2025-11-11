"""Navigation callbacks for PyPSA Explorer dashboard."""

from typing import cast

from dash import Input, Output, State, no_update


def register_navigation_callbacks(app) -> None:
    """Register navigation-related callbacks."""

    @app.callback(
        [
            Output("welcome-content", "style"),
            Output("dashboard-content", "style"),
            Output("page-state", "data"),
            Output("top-bar-network-selector", "style"),
        ],
        [Input("enter-dashboard-btn", "n_clicks")],
        [
            State("page-state", "data"),
            State("network-registry", "data"),
        ],
    )
    def navigate_pages(
        n_clicks: int | None,
        page_state: dict[str, str],
        registry: dict[str, list[str]] | None = None,
    ) -> tuple[dict[str, str], dict[str, str], dict[str, str], dict[str, str]]:
        """Manage navigation between welcome page and dashboard."""
        page_state = page_state or {}
        has_network = bool(registry and registry.get("order"))
        current_page = page_state.get("current_page")

        if n_clicks and current_page == "welcome" and has_network:
            return (
                {"display": "none"},
                {"display": "block"},
                {"current_page": "dashboard"},
                {"display": "flex"},
            )
        if current_page == "dashboard" and has_network:
            return (
                cast(dict[str, str], no_update),
                cast(dict[str, str], no_update),
                cast(dict[str, str], no_update),
                {"display": "flex"},
            )

        # No networks or still on welcome page keeps selector hidden
        return (
            cast(dict[str, str], no_update),
            cast(dict[str, str], no_update),
            cast(dict[str, str], no_update),
            {"display": "none"},
        )
