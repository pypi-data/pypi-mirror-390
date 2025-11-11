"""Network-related callbacks for PyPSA Explorer dashboard."""

import base64
from pathlib import Path
from typing import Any

import dash_bootstrap_components as dbc
import folium
import pypsa
import pypsa.consistency
import yaml  # type: ignore[import]
from dash import ALL, Input, Output, State, ctx, html, no_update
from dash.development.base_component import Component
from dash.exceptions import PreventUpdate

from pypsa_explorer.layouts.components import create_header
from pypsa_explorer.utils.helpers import get_bus_carrier_options, get_country_options, summarize_network


def register_network_callbacks(app, networks: dict[str, pypsa.Network], *, default_network_path: str) -> None:
    """Register network-related callbacks."""

    uploads_dir = Path("uploaded_networks")
    uploads_dir.mkdir(exist_ok=True)

    def _ensure_registry(data: dict[str, Any] | None) -> dict[str, Any]:
        registry = data.copy() if data else {}
        registry.setdefault("order", [])
        registry.setdefault("info", {})
        registry["defaultNetworkPath"] = default_network_path
        return registry

    def _sanitize_label(raw_label: str) -> str:
        label = raw_label.strip()
        if not label:
            return "Network"
        label = label.replace("_", " ").replace("-", " ")
        label = " ".join(label.split())
        return label[:80]

    def _unique_label(base_label: str, existing: list[str]) -> str:
        candidate = base_label or "Network"
        suffix = 2
        while candidate in existing:
            candidate = f"{base_label} ({suffix})"
            suffix += 1
        return candidate

    def _safe_upload_filename(raw_name: str) -> str:
        cleaned = raw_name.strip()
        if not cleaned:
            raise ValueError("Upload is missing a filename")
        candidate = Path(cleaned)
        if candidate.is_absolute():
            raise ValueError("Absolute upload paths are not allowed")
        if any(part == ".." for part in candidate.parts):
            raise ValueError("Parent path segments are not allowed in upload filenames")
        sanitized = candidate.name
        if not sanitized:
            raise ValueError("Invalid upload filename")
        return sanitized

    def _write_uploaded_file(content: str, filename: str) -> Path:
        if "," not in content:
            raise ValueError("Unexpected upload payload")
        header, encoded = content.split(",", 1)
        if "base64" not in header:
            raise ValueError("Upload payload is not base64 encoded")
        file_bytes = base64.b64decode(encoded)
        sanitized_name = _safe_upload_filename(filename)
        target_path = uploads_dir / sanitized_name
        counter = 1
        stem = target_path.stem or "network"
        suffix = target_path.suffix or ".nc"
        while target_path.exists():
            target_path = uploads_dir / f"{stem}_{counter}{suffix}"
            counter += 1
        target_path.write_bytes(file_bytes)
        return target_path

    @app.callback(
        [
            Output("network-registry", "data"),
            Output("upload-feedback", "children"),
        ],
        [
            Input("network-upload", "contents"),
            Input("load-example-network-btn", "n_clicks"),
        ],
        [
            State("network-upload", "filename"),
            State("network-registry", "data"),
        ],
        prevent_initial_call=True,
    )
    def load_networks_from_ui(
        uploaded_contents: list[str] | str | None,
        example_clicks: int | None,  # noqa: ARG001 - present to satisfy Dash signature
        uploaded_filenames: list[str] | str | None,
        registry_data: dict[str, Any] | None,
    ) -> tuple[Any, Any]:
        triggered = ctx.triggered_id
        if triggered is None:
            raise PreventUpdate

        registry = _ensure_registry(registry_data)
        info: dict[str, Any] = registry.get("info", {})
        order: list[str] = registry.get("order", [])
        feedback_messages: list[Component] = []

        if triggered == "network-upload":
            if not uploaded_contents or not uploaded_filenames:
                raise PreventUpdate

            contents_list = uploaded_contents if isinstance(uploaded_contents, list) else [uploaded_contents]
            filenames_list = uploaded_filenames if isinstance(uploaded_filenames, list) else [uploaded_filenames]

            for content, original_name in zip(contents_list, filenames_list, strict=False):
                try:
                    stored_path = _write_uploaded_file(content, original_name)
                except Exception as exc:  # noqa: BLE001
                    feedback_messages.append(
                        dbc.Alert(
                            f"Failed to save '{original_name}': {exc}",
                            color="danger",
                            className="mb-2",
                        )
                    )
                    continue

                try:
                    network = pypsa.Network(stored_path)
                except Exception as exc:  # noqa: BLE001
                    stored_path.unlink(missing_ok=True)
                    feedback_messages.append(
                        dbc.Alert(
                            f"Failed to load '{original_name}': {exc}",
                            color="danger",
                            className="mb-2",
                        )
                    )
                    continue

                base_label = _sanitize_label(Path(original_name).stem)
                label = _unique_label(base_label, order)
                networks[label] = network
                order = [existing for existing in order if existing != label]
                order.append(label)
                summary = summarize_network(network)
                summary_payload: dict[str, Any] = {
                    "source": str(stored_path),
                    "origin": "upload",
                }
                summary.update(summary_payload)
                info[label] = summary
                feedback_messages.append(
                    dbc.Alert(
                        f"Loaded network '{label}'",
                        color="success",
                        className="mb-2",
                    )
                )

            registry["order"] = order
            registry["info"] = info
            return registry, html.Div(feedback_messages)

        if triggered == "load-example-network-btn":
            demo_path = Path(default_network_path)
            if not demo_path.is_file():
                return no_update, dbc.Alert(
                    "Example network unavailable in this environment.",
                    color="warning",
                    className="mb-0",
                )

            try:
                network = pypsa.Network(demo_path)
                base_label = _sanitize_label(demo_path.stem or "Example")
                label = _unique_label(base_label or "Example", order)
                networks[label] = network
                order = [existing for existing in order if existing != label]
                order.append(label)
                summary = summarize_network(network)
                summary_payload = {
                    "source": str(demo_path),
                    "origin": "example",
                }
                summary.update(summary_payload)
                info[label] = summary
                registry["order"] = order
                registry["info"] = info
                return (
                    registry,
                    dbc.Alert(
                        f"Example network '{label}' loaded.",
                        color="info",
                        className="mb-0",
                    ),
                )
            except Exception as exc:  # noqa: BLE001
                return no_update, dbc.Alert(
                    f"Failed to load example network: {exc}",
                    color="danger",
                    className="mb-0",
                )

        raise PreventUpdate

    @app.callback(
        [
            Output("network-selector", "data"),
            Output({"type": "network-button", "index": ALL}, "className"),
        ],
        [
            Input({"type": "network-button", "index": ALL}, "n_clicks"),
            Input("network-registry", "data"),
        ],
        [
            State({"type": "network-button", "index": ALL}, "id"),
            State("network-selector", "data"),
        ],
    )
    def handle_network_button_click(
        n_clicks: list[int] | None,  # noqa: ARG001
        registry_data: dict[str, Any] | None,
        button_ids: list[dict],
        current_network: str | None,
    ) -> tuple[str | None, list[str]]:
        """Handle network button clicks and update active state."""
        registry = registry_data or {}
        available_labels: list[str] = registry.get("order", []) if isinstance(registry, dict) else []

        if not button_ids:
            return (available_labels[-1] if available_labels else None), []

        if ctx.triggered_id == "network-registry":
            if not available_labels:
                class_names = ["network-button" for _ in button_ids]
                return None, class_names
            active_label = current_network if current_network in available_labels else available_labels[-1]
            class_names = [
                "network-button network-button-active" if btn["index"] == active_label else "network-button"
                for btn in button_ids
            ]
            return active_label, class_names

        if not ctx.triggered_id:
            # Initial load - set active button
            class_names = [
                "network-button network-button-active" if btn["index"] == current_network else "network-button"
                for btn in button_ids
            ]
            return current_network, class_names

        # Get the clicked button's network label
        clicked_network = ctx.triggered_id["index"]

        # Update button styles
        class_names = [
            "network-button network-button-active" if btn["index"] == clicked_network else "network-button"
            for btn in button_ids
        ]

        return clicked_network, class_names

    @app.callback(
        [
            Output("network-button-group", "children"),
            Output("network-list", "children"),
            Output("enter-dashboard-btn", "disabled"),
        ],
        [Input("network-registry", "data")],
        [State("network-selector", "data")],
    )
    def sync_network_ui(
        registry_data: dict[str, Any] | None,
        active_label: str | None,
    ) -> tuple[list[html.Button], list[html.Div], bool]:
        registry = registry_data or {}
        order: list[str] = registry.get("order", [])
        info: dict[str, dict[str, Any]] = registry.get("info", {})

        button_children: list[html.Button] = [
            html.Button(
                label,
                id={"type": "network-button", "index": label},
                n_clicks=0,
                className=f"network-button {'network-button-active' if label == active_label else ''}",
            )
            for label in order
        ]

        if order:
            list_children = [
                html.Div(
                    [
                        html.H5(label),
                        html.P(
                            f"Nodes: {info.get(label, {}).get('buses', 0)}, "
                            f"Links: {info.get(label, {}).get('links', 0)}, "
                            f"Lines: {info.get(label, {}).get('lines', 0)}",
                            className="mb-1",
                        ),
                        html.Small(
                            (
                                "Bundled example"
                                if info.get(label, {}).get("origin") == "example"
                                else (
                                    Path(info.get(label, {}).get("source", "")).name
                                    if info.get(label, {}).get("source")
                                    else "Uploaded"
                                )
                            ),
                            className="text-muted",
                        ),
                    ],
                    className="network-item",
                )
                for label in order
            ]
        else:
            list_children = [
                html.Div(
                    [
                        html.H5("No networks loaded yet", className="text-muted"),
                        html.P(
                            "Drag a .nc file onto the dropzone or load the bundled example.",
                            className="text-muted",
                        ),
                    ],
                    className="network-item",
                )
            ]

        return button_children, list_children, not bool(order)

    @app.callback(
        [
            Output("global-carrier-selector", "options"),
            Output("global-country-selector", "options"),
        ],
        [Input("network-selector", "data")],
    )
    def update_selected_network(selected_network_label: str | None) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
        """Update filter options when user selects a different network."""
        if not selected_network_label or selected_network_label not in networks:
            return [], []

        n = networks[selected_network_label]

        # Update bus carrier options for the new network
        updated_bus_carrier_options = get_bus_carrier_options(n)

        # Update country options for the new network
        updated_country_options = get_country_options(n)

        return updated_bus_carrier_options, updated_country_options

    @app.callback(
        Output("kpi-header-container", "children"),
        [Input("network-selector", "data")],
    )
    def update_kpi_header(selected_network_label: str | None) -> html.Div:
        """Update KPI header when network changes."""
        if not selected_network_label or selected_network_label not in networks:
            return create_header(None)

        n = networks[selected_network_label]
        return create_header(n)

    @app.callback(
        Output("network-map", "srcDoc"),
        [
            Input("refresh-map-button", "n_clicks"),
            Input("network-selector", "data"),
        ],
    )
    def update_map(n_clicks: int | None, selected_network_label: str | None) -> str:  # noqa: ARG001
        """Update network map visualization."""
        if not selected_network_label or selected_network_label not in networks:
            return "<div style='padding:20px;text-align:center;color:#6c757d;'>Load a network to view the map.</div>"

        n = networks[selected_network_label]
        try:
            # Create a folium map using PyPSA's explore method
            # Note: popup and components parameters removed for PyPSA v1.0 compatibility
            map_obj: folium.Map = n.plot.explore(tooltip=True)  # type: ignore[call-arg, attr-defined]
            return map_obj._repr_html_()
        except Exception as e:
            print(f"Error creating map: {e}")
            return f"<div style='padding:20px;'><h2>Map visualization unavailable</h2><p>Error: {str(e)}</p></div>"

    @app.callback(
        Output("network-metadata", "children"),
        [
            Input("refresh-map-button", "n_clicks"),
            Input("network-selector", "data"),
        ],
    )
    def update_metadata(
        n_clicks: int | None,  # noqa: ARG001 - click count unused, present for signature
        selected_network_label: str | None,
    ) -> html.Pre | html.Div:
        """Display network metadata."""
        if not selected_network_label or selected_network_label not in networks:
            return html.Div(
                "Load a network to view metadata.",
                className="text-muted",
                style={"padding": "16px"},
            )

        n = networks[selected_network_label]
        try:
            # Convert network metadata to YAML format
            metadata_yaml: str = yaml.dump(n.meta, default_flow_style=False, sort_keys=False)

            return html.Pre(
                metadata_yaml,
                style={
                    "background-color": "#FAFBFC",
                    "padding": "10px",
                    "border-radius": "5px",
                    "color": "var(--text-color)",
                },
            )
        except Exception as e:
            print(f"Error displaying metadata: {e}")
            return html.Div(
                [
                    html.H5("Metadata Unavailable", className="text-muted"),
                    html.P(f"Error: {str(e)}", className="text-danger"),
                ]
            )
