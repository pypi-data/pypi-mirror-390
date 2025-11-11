"""Tab components for PyPSA Explorer dashboard."""

import dash_bootstrap_components as dbc
from dash import dcc, html

# Tab styling constants
TAB_STYLE = {
    "padding": "12px 16px",
    "backgroundColor": "transparent",
    "border": "none",
    "borderBottom": "3px solid transparent",
}

TAB_SELECTED_STYLE = {
    "padding": "12px 16px",
    "backgroundColor": "transparent",
    "border": "none",
    "borderBottom": "3px solid transparent",
}


def create_energy_balance_tab() -> dcc.Tab:
    """Create the Energy Balance (timeseries) tab."""
    return dcc.Tab(
        label="📈 Energy Balance Timeseries",
        value="energy-balance",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([html.Div(id="energy-balance-charts-container")], className="chart-card-body"),
                className="mt-3",
            )
        ],
    )


def create_energy_balance_aggregated_tab() -> dcc.Tab:
    """Create the Aggregated Energy Balance tab."""
    return dcc.Tab(
        label="📊 Energy Balance Totals",
        value="energy-balance-aggregated",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([html.Div(id="agg-energy-balance-charts-container")], className="chart-card-body"),
                className="mt-3",
            )
        ],
    )


def create_capacity_tab() -> dcc.Tab:
    """Create the Capacity tab."""
    return dcc.Tab(
        label="⚡ Capacity Totals",
        value="capacity",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([dbc.Row(id="capacity-charts-container")], className="chart-card-body"),
                className="mt-3",
            )
        ],
    )


def create_capex_totals_tab() -> dcc.Tab:
    """Create the CAPEX Totals tab."""
    return dcc.Tab(
        label="💰 CAPEX Totals",
        value="capex",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([dbc.Row(id="capex-charts-container")], className="chart-card-body"),
                className="mt-3",
            )
        ],
    )


def create_opex_totals_tab() -> dcc.Tab:
    """Create the OPEX Totals tab."""
    return dcc.Tab(
        label="💵 OPEX Totals",
        value="opex",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody([dbc.Row(id="opex-charts-container")], className="chart-card-body"),
                className="mt-3",
            )
        ],
    )


def create_network_map_tab() -> dcc.Tab:
    """Create the Network Configuration tab with map and metadata."""
    return dcc.Tab(
        label="🗺️ Network Configuration",
        value="network-config",
        style=TAB_STYLE,
        selected_style=TAB_SELECTED_STYLE,
        children=[
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                # Left column: Network Metadata
                                dbc.Col(
                                    [
                                        html.H4("Network Metadata", className="mb-3"),
                                        html.Div(
                                            id="network-metadata",
                                            className="bg-light p-3 border rounded",
                                            style={
                                                "height": "700px",
                                                "overflow": "auto",
                                                "white-space": "pre-wrap",
                                                "font-family": "monospace",
                                            },
                                        ),
                                    ],
                                    width=6,
                                ),
                                # Right column: Network Map
                                dbc.Col(
                                    [
                                        html.H4("Network Map", className="mb-3"),
                                        html.Iframe(
                                            id="network-map",
                                            style={
                                                "width": "100%",
                                                "height": "700px",
                                                "border": "1px solid #E2E8F0",
                                            },
                                        ),
                                        html.Div(
                                            [
                                                dbc.Button(
                                                    "Refresh Map",
                                                    id="refresh-map-button",
                                                    color="primary",
                                                    className="mt-3",
                                                )
                                            ],
                                            className="text-center",
                                        ),
                                    ],
                                    width=6,
                                ),
                            ]
                        ),
                    ]
                ),
                className="mt-3",
            )
        ],
    )
