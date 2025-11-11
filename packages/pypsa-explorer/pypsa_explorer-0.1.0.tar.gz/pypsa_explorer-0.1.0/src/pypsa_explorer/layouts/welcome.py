"""Welcome page layout for PyPSA Explorer dashboard."""

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_welcome_page(
    network_labels: list[str],
    networks_info: dict[str, dict[str, int | str]],
    demo_network_available: bool,
) -> dbc.Card:
    """
    Create the welcome page for the dashboard.

    Parameters
    ----------
    network_labels : list[str]
        List of available network labels
    networks_info : dict[str, dict[str, int]]
        Dictionary with network info: {label: {"buses": count, "links": count, "lines": count}}
    demo_network_available : bool
        Whether the bundled example network is available for loading

    Returns
    -------
    dbc.Card
        Welcome page component
    """
    return dbc.Card(
        dbc.CardBody(
            [
                # OET logo in the upper right
                html.Div(
                    html.Img(
                        src="https://openenergytransition.org/assets/img/oet-logo-red-n-subtitle.png",
                        style={
                            "height": "60px",
                            "position": "absolute",
                            "top": "35px",
                            "right": "35px",
                            "zIndex": "10",
                        },
                    ),
                ),
                # Hero Section
                html.Div(
                    [
                        html.Div(
                            "⚡",
                            style={
                                "fontSize": "5rem",
                                "marginBottom": "20px",
                                "display": "inline-block",
                                "animation": "pulse 2s ease-in-out infinite",
                            },
                        ),
                        html.H1(
                            "PyPSA Energy Explorer",
                            className="welcome-header",
                        ),
                        html.P(
                            "Analyze and visualize power system networks with interactive, real-time insights",
                            className="welcome-subtitle",
                        ),
                        html.Div(
                            [
                                html.Span(
                                    "🔋 Advanced Analytics",
                                    style={
                                        "display": "inline-block",
                                        "margin": "0 15px",
                                        "padding": "8px 16px",
                                        "background": "rgba(255, 255, 255, 0.9)",
                                        "borderRadius": "20px",
                                        "fontSize": "0.9rem",
                                        "fontWeight": "500",
                                    },
                                ),
                                html.Span(
                                    "📊 Interactive Visualizations",
                                    style={
                                        "display": "inline-block",
                                        "margin": "0 15px",
                                        "padding": "8px 16px",
                                        "background": "rgba(255, 255, 255, 0.9)",
                                        "borderRadius": "20px",
                                        "fontSize": "0.9rem",
                                        "fontWeight": "500",
                                    },
                                ),
                                html.Span(
                                    "🌍 Multi-Network Support",
                                    style={
                                        "display": "inline-block",
                                        "margin": "0 15px",
                                        "padding": "8px 16px",
                                        "background": "rgba(255, 255, 255, 0.9)",
                                        "borderRadius": "20px",
                                        "fontSize": "0.9rem",
                                        "fontWeight": "500",
                                    },
                                ),
                            ],
                            style={"marginTop": "30px", "marginBottom": "20px"},
                        ),
                    ],
                    className="welcome-card mb-4",
                ),
                # Upload and sample section
                html.Div(
                    [
                        dcc.Upload(
                            id="network-upload",
                            multiple=True,
                            accept=".nc",
                            children=html.Div(
                                [
                                    html.Div(
                                        html.I(
                                            className="fas fa-cloud-upload-alt",
                                            style={"fontSize": "2rem", "marginBottom": "12px"},
                                        ),
                                        className="mb-2",
                                    ),
                                    html.H4("Drop .nc files here", className="mb-2"),
                                    html.P(
                                        "Drag and drop PyPSA NetCDF networks or click to browse.",
                                        className="text-muted",
                                        style={"margin": 0},
                                    ),
                                ],
                                className="upload-dropzone",
                                style={
                                    "border": "2px dashed rgba(0, 102, 204, 0.4)",
                                    "borderRadius": "24px",
                                    "padding": "40px",
                                    "textAlign": "center",
                                    "cursor": "pointer",
                                    "background": "rgba(0, 102, 204, 0.05)",
                                    "transition": "border-color 0.3s ease",
                                },
                            ),
                        ),
                        html.Div(id="upload-feedback", className="mt-3"),
                        html.Div(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-play", style={"marginRight": "8px"}),
                                        "Load Example Network",
                                    ],
                                    id="load-example-network-btn",
                                    color="secondary",
                                    disabled=not demo_network_available,
                                    className="mt-3",
                                ),
                                html.Small(
                                    "Example network unavailable in this build.",
                                    className="text-muted d-block mt-2",
                                    style={"display": "block" if not demo_network_available else "none"},
                                ),
                            ],
                            className="text-center",
                        ),
                    ],
                    className="welcome-upload-section mb-5",
                ),
                dbc.Row(
                    [
                        # Energy Balance Timeseries
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(className="feature-icon", children=html.I(className="fas fa-chart-area")),
                                        html.H5("Energy Balance Timeseries"),
                                        html.P("Visualize energy flows over time for different carriers and countries."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                        # Energy Balance Totals
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(className="feature-icon", children=html.I(className="fas fa-chart-bar")),
                                        html.H5("Energy Balance Totals"),
                                        html.P("Analyze aggregated energy balances across the system."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                        # Capacity Totals
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(className="feature-icon", children=html.I(className="fas fa-solar-panel")),
                                        html.H5("Capacity Totals"),
                                        html.P("Explore optimal capacity distribution by carrier and country."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                    ],
                    className="mb-3",
                ),
                dbc.Row(
                    [
                        # CAPEX Totals
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(className="feature-icon", children=html.I(className="fas fa-coins")),
                                        html.H5("CAPEX Totals"),
                                        html.P("Analyze capital expenditure distribution across the network."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                        # OPEX Totals
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            className="feature-icon", children=html.I(className="fas fa-file-invoice-dollar")
                                        ),
                                        html.H5("OPEX Totals"),
                                        html.P("Review operational expenditure patterns by carrier."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                        # Network Configuration
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.Div(
                                            className="feature-icon", children=html.I(className="fas fa-project-diagram")
                                        ),
                                        html.H5("Network Configuration"),
                                        html.P("Explore network topology and metadata through interactive maps."),
                                    ]
                                ),
                                className="welcome-feature",
                            ),
                            width=4,
                            className="mb-3",
                        ),
                    ],
                    className="mb-4",
                ),
                # Available networks section
                html.Div(
                    [
                        html.H3("Available Networks", className="mt-4 mb-3"),
                        html.Div(
                            id="network-list",
                            children=[  # type: ignore[list-item]
                                html.Div(
                                    [
                                        html.H5(label),
                                        html.P(
                                            f"Nodes: {networks_info[label]['buses']}, "
                                            f"Links: {networks_info[label]['links']}, "
                                            f"Lines: {networks_info[label]['lines']}"
                                        ),
                                    ],
                                    className="network-item",
                                )
                                for label in network_labels
                            ],
                        ),
                        # Enter dashboard button
                        html.Div(
                            [
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-rocket", style={"marginRight": "10px"}),
                                        "Enter Dashboard",
                                    ],
                                    id="enter-dashboard-btn",
                                    size="lg",
                                    className="mt-4",
                                    disabled=not network_labels,
                                    style={
                                        "background": "linear-gradient(135deg, #0066CC 0%, #4ECDC4 100%)",
                                        "border": "none",
                                        "padding": "16px 48px",
                                        "fontSize": "1.1rem",
                                        "fontWeight": "600",
                                        "borderRadius": "50px",
                                        "boxShadow": "0 8px 24px rgba(0, 102, 204, 0.3)",
                                        "transition": "all 0.3s ease",
                                    },
                                )
                            ],
                            className="text-center mt-4 mb-5",
                        ),
                    ],
                    className="mt-4",
                ),
            ]
        ),
        className="mt-3",
    )
