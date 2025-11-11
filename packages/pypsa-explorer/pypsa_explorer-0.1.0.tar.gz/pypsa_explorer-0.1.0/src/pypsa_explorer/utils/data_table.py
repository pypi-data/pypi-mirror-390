"""Utility functions for DataTable conversion and optimization."""

import pandas as pd
import pypsa


def dataframe_to_datatable(df: pd.DataFrame, max_rows: int = 5000) -> tuple[list[dict], list[dict]]:
    """
    Convert DataFrame to DataTable format with optional uniform sampling.

    For large datasets, uses uniform sampling to maintain temporal/spatial distribution
    while keeping initial load performant.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to convert
    max_rows : int
        Maximum rows to include before sampling (default: 5000)

    Returns
    -------
    tuple[list[dict], list[dict]]
        (data, columns) - Data as list of dicts, columns as list of column definitions
    """
    # Reset index and handle NaN values
    df_reset = df.reset_index()

    # Replace NaN values with empty strings to avoid React key warnings
    df_reset = df_reset.fillna("")

    if len(df_reset) > max_rows:
        # Uniform sampling for better representation
        step = max(1, len(df_reset) // max_rows)
        df_display = df_reset.iloc[::step]
        columns = [{"name": col, "id": col} for col in df_reset.columns]
        # Add sampling info to first column header
        columns[0]["name"] = f"{columns[0]['name']} (showing {len(df_display):,} of {len(df_reset):,} rows)"
        return df_display.to_dict("records"), columns

    return df_reset.to_dict("records"), [{"name": col, "id": col} for col in df_reset.columns]


def get_timeseries_attributes(n: pypsa.Network, component: str) -> list[str]:
    """
    Get available time-series attributes for a component efficiently.

    Uses PyPSA's component metadata instead of introspecting all attributes.

    Parameters
    ----------
    n : pypsa.Network
        The PyPSA network object
    component : str
        Component name (e.g., 'generators', 'lines')

    Returns
    -------
    list[str]
        List of time-varying attribute names that have data
    """
    ts_component = f"{component}_t"
    if not hasattr(n, ts_component):
        return []

    ts_obj = getattr(n, ts_component)

    # Get varying attributes from component metadata
    if hasattr(n, "component_attrs") and component.rstrip("s") in n.component_attrs:
        # PyPSA stores singular form in component_attrs
        singular = component.rstrip("s")
        if singular.endswith("ie"):
            singular = singular[:-2] + "y"  # e.g., 'carriers' -> 'carrier'

        varying_attrs = n.component_attrs[singular].query("varying").index.tolist()

        # Filter to only attributes that exist and have data
        available = []
        for attr in varying_attrs:
            if hasattr(ts_obj, attr):
                attr_data = getattr(ts_obj, attr)
                if isinstance(attr_data, pd.DataFrame) and not attr_data.empty:
                    available.append(attr)
        return available

    # Fallback: check common time-series attributes
    common_attrs = ["p", "q", "p0", "p1", "s", "e", "state_of_charge"]
    available = []
    for attr in common_attrs:
        if hasattr(ts_obj, attr):
            attr_data = getattr(ts_obj, attr)
            if isinstance(attr_data, pd.DataFrame) and not attr_data.empty:
                available.append(attr)

    return available


# Standard DataTable configuration for consistency
DATATABLE_BASE_CONFIG = {
    "page_action": "native",
    "page_size": 50,
    "page_current": 0,
    "sort_action": "native",
    "filter_action": "native",
    "virtualization": True,  # Enable for performance
    "style_table": {
        "overflowX": "auto",
        "maxHeight": "500px",
    },
    "style_cell": {
        "textAlign": "left",
        "padding": "8px",
        "fontSize": "0.9rem",
    },
    "style_header": {
        "fontWeight": "600",
        "backgroundColor": "#FAFBFC",
        "position": "sticky",
        "top": 0,
        "zIndex": 1,
    },
    "style_data_conditional": [
        {
            "if": {"row_index": "odd"},
            "backgroundColor": "#FAFBFC",
        }
    ],
    "export_format": "csv",
}
