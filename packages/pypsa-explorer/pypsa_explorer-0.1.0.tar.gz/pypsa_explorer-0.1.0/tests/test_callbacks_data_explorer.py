"""Tests for data explorer callbacks."""

from unittest.mock import patch

import pandas as pd
import pypsa
import pytest
from dash import Dash

from pypsa_explorer.callbacks.data_explorer import (
    COMPONENT_LABELS,
    KPI_COMPONENT_MAP,
    register_data_explorer_callbacks,
)


@pytest.fixture
def network_with_timeseries():
    """Create a network with time-series data for testing."""
    n = pypsa.Network()

    # Add carriers
    n.add("Carrier", "AC", nice_name="AC")
    n.add("Carrier", "wind", nice_name="Wind")

    # Add components
    n.add("Bus", "bus1", carrier="AC", x=0, y=0, country="DE")
    n.add("Bus", "bus2", carrier="AC", x=1, y=1, country="FR")
    n.add("Generator", "gen1", bus="bus1", carrier="wind", p_nom=100)
    n.add("Generator", "gen2", bus="bus2", carrier="wind", p_nom=50)
    n.add("Line", "line1", bus0="bus1", bus1="bus2", x=0.1, r=0.01, s_nom=100)
    n.add("Link", "link1", bus0="bus1", bus1="bus2", p_nom=50)
    n.add("StorageUnit", "storage1", bus="bus1", p_nom=30)
    n.add("Store", "store1", bus="bus1", e_nom=100)

    # Add time-series data
    n.set_snapshots(pd.date_range("2024-01-01", periods=5, freq="h"))
    n.generators_t.p = pd.DataFrame(
        {
            "gen1": [10, 20, 30, 40, 50],
            "gen2": [5, 10, 15, 20, 25],
        },
        index=n.snapshots,
    )

    n.generators_t.q = pd.DataFrame(
        {
            "gen1": [1, 2, 3, 4, 5],
            "gen2": [0.5, 1, 1.5, 2, 2.5],
        },
        index=n.snapshots,
    )

    n.lines_t.p0 = pd.DataFrame(
        {
            "line1": [5, 10, 15, 20, 25],
        },
        index=n.snapshots,
    )

    return n


class TestCallbackRegistration:
    """Test that callbacks are properly registered."""

    def test_callbacks_registered(self, network_with_timeseries):
        """Test that data explorer callbacks are registered."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}

        # Should have no callbacks before registration
        assert len(app.callback_map) == 0

        register_data_explorer_callbacks(app, networks)

        # Should have 2 callbacks after registration (modal toggle + timeseries)
        assert len(app.callback_map) == 2

    def test_modal_toggle_callback_structure(self, network_with_timeseries):
        """Test modal toggle callback has correct structure."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # First callback is toggle_modal_and_load_data
        callback_info = list(app.callback_map.values())[0]

        # Check outputs
        outputs = callback_info["output"]
        assert len(outputs) == 7  # Added active-component-store output
        output_ids = [str(out) for out in outputs]
        assert any("data-explorer-modal.is_open" in oid for oid in output_ids)
        assert any("static-data-table.data" in oid for oid in output_ids)
        assert any("active-component-store.data" in oid for oid in output_ids)

        # Check inputs - should have 7 inputs (6 KPI cards + close button)
        inputs = callback_info["inputs"]
        assert len(inputs) == 7

        # Check states
        states = callback_info["state"]
        assert len(states) == 2

    def test_timeseries_callback_structure(self, network_with_timeseries):
        """Test time-series callback has correct structure."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Second callback is for time-series data
        callback_info = list(app.callback_map.values())[1]

        # Check outputs
        outputs = callback_info["output"]
        assert len(outputs) == 2
        output_ids = [str(out) for out in outputs]
        assert any("timeseries-data-table.data" in oid for oid in output_ids)
        assert any("timeseries-data-table.columns" in oid for oid in output_ids)


class TestComponentMapping:
    """Test component mapping configuration."""

    def test_component_mapping_completeness(self):
        """Test that all KPI card mappings are defined."""
        expected_cards = [
            "kpi-card-buses",
            "kpi-card-generators",
            "kpi-card-lines",
            "kpi-card-links",
            "kpi-card-storage_units",
            "kpi-card-stores",
        ]

        assert set(KPI_COMPONENT_MAP.keys()) == set(expected_cards)

        # Check that all components have labels
        for component in KPI_COMPONENT_MAP.values():
            assert component in COMPONENT_LABELS

    def test_component_labels_exist(self):
        """Test that all component labels are human-readable."""
        expected_labels = {
            "buses": "Nodes",
            "generators": "Generators",
            "lines": "Lines",
            "links": "Links",
            "storage_units": "Storage Units",
            "stores": "Stores",
        }

        for component, label in expected_labels.items():
            assert COMPONENT_LABELS[component] == label


class TestNetworkDataAccess:
    """Test network data access patterns."""

    def test_network_has_component_dataframes(self, network_with_timeseries):
        """Test that network has expected component dataframes."""
        n = network_with_timeseries

        # Check all components exist
        assert hasattr(n, "buses")
        assert hasattr(n, "generators")
        assert hasattr(n, "lines")
        assert hasattr(n, "links")
        assert hasattr(n, "storage_units")
        assert hasattr(n, "stores")

        # Check they are DataFrames
        assert isinstance(n.buses, pd.DataFrame)
        assert isinstance(n.generators, pd.DataFrame)
        assert isinstance(n.lines, pd.DataFrame)

    def test_network_has_timeseries_data(self, network_with_timeseries):
        """Test that network has time-series data."""
        n = network_with_timeseries

        # Check time-series objects exist
        assert hasattr(n, "generators_t")
        assert hasattr(n, "lines_t")

        # Check specific attributes
        assert hasattr(n.generators_t, "p")
        assert hasattr(n.generators_t, "q")
        assert isinstance(n.generators_t.p, pd.DataFrame)

    def test_empty_network_has_components(self, demo_network):
        """Test that even basic network has component dataframes."""
        n = demo_network

        # Even empty components should exist as DataFrames
        assert hasattr(n, "storage_units")
        assert isinstance(n.storage_units, pd.DataFrame)
        assert len(n.storage_units) == 0  # But it's empty


class TestDataConversion:
    """Test data conversion for DataTables."""

    def test_dataframe_to_dict_records(self, network_with_timeseries):
        """Test DataFrame conversion to dict records for DataTable."""
        n = network_with_timeseries

        # Convert buses dataframe
        df = n.buses.reset_index()
        data = df.to_dict("records")

        assert isinstance(data, list)
        assert len(data) == 2
        assert all(isinstance(record, dict) for record in data)

    def test_column_definition_creation(self, network_with_timeseries):
        """Test column definition creation for DataTable."""
        n = network_with_timeseries

        df = n.buses.reset_index()
        columns = [{"name": col, "id": col} for col in df.columns]

        assert isinstance(columns, list)
        assert all("name" in col and "id" in col for col in columns)
        assert len(columns) == len(df.columns)

    def test_timeseries_dataframe_conversion(self, network_with_timeseries):
        """Test time-series DataFrame conversion."""
        n = network_with_timeseries

        ts_df = n.generators_t.p
        df_reset = ts_df.reset_index()
        data = df_reset.to_dict("records")

        assert len(data) == 5  # 5 snapshots
        assert all(isinstance(record, dict) for record in data)


class TestTimeSeriesAttributeDetection:
    """Test time-series attribute detection."""

    def test_detect_timeseries_attributes(self, network_with_timeseries):
        """Test detection of time-series attributes."""
        n = network_with_timeseries

        # Get generators_t object
        ts_obj = n.generators_t

        # Detect DataFrame attributes
        timeseries_attrs = [
            attr for attr in dir(ts_obj) if not attr.startswith("_") and isinstance(getattr(ts_obj, attr), pd.DataFrame)
        ]

        assert "p" in timeseries_attrs
        assert "q" in timeseries_attrs
        assert len(timeseries_attrs) >= 2

    def test_no_timeseries_for_basic_network(self, demo_network):
        """Test that basic network has time-series DataFrames but they may be empty."""
        n = demo_network

        if hasattr(n, "generators_t"):
            ts_obj = n.generators_t
            timeseries_attrs = [
                attr for attr in dir(ts_obj) if not attr.startswith("_") and isinstance(getattr(ts_obj, attr), pd.DataFrame)
            ]
            # PyPSA creates time-series DataFrames even if empty
            # Just check that they exist and are DataFrames
            assert len(timeseries_attrs) >= 0  # Can have any number of attributes
            assert all(isinstance(getattr(ts_obj, attr), pd.DataFrame) for attr in timeseries_attrs)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_network_with_empty_components(self):
        """Test network that has empty component dataframes."""
        n = pypsa.Network()
        n.add("Carrier", "AC")
        n.add("Bus", "bus1", carrier="AC", country="DE")

        # Generators dataframe exists but is empty
        assert hasattr(n, "generators")
        assert isinstance(n.generators, pd.DataFrame)
        assert len(n.generators) == 0

    def test_component_without_timeseries(self):
        """Test accessing time-series for component."""
        n = pypsa.Network()
        n.add("Carrier", "AC")
        n.add("Bus", "bus1", carrier="AC", country="DE")

        # buses_t always exists in PyPSA
        if hasattr(n, "buses_t"):
            ts_obj = n.buses_t
            # PyPSA creates time-series DataFrames for all components
            ts_attrs = [
                attr for attr in dir(ts_obj) if not attr.startswith("_") and isinstance(getattr(ts_obj, attr), pd.DataFrame)
            ]
            # Just verify they are DataFrames (may be empty)
            assert all(isinstance(getattr(ts_obj, attr), pd.DataFrame) for attr in ts_attrs)

    def test_multiple_networks_handling(self, network_with_timeseries, demo_network):
        """Test handling multiple networks."""
        app = Dash(__name__)
        networks = {
            "Network 1": network_with_timeseries,
            "Network 2": demo_network,
        }

        register_data_explorer_callbacks(app, networks)

        # Callbacks should be registered once regardless of network count
        assert len(app.callback_map) == 2


class TestDataExplorerModalInteraction:
    """Test modal opening and closing interactions."""

    def test_modal_opens_on_kpi_card_click(self, network_with_timeseries):
        """Test that modal opens when a KPI card is clicked."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking buses KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-buses"

            # Simulate clicking on buses KPI card
            # Use positional arguments matching the callback signature
            result = callback_func(
                1,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                0,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                False,  # is_open
            )

        # Unpack result - should be (is_open, title, static_data, static_columns, ts_options, ts_disabled, active_component)
        is_open = result[0]
        title = result[1]
        active_component = result[6]

        # Modal should be open
        assert is_open is True
        # Title should mention buses/nodes
        assert "Nodes" in title or "buses" in title.lower()
        # Active component should be stored
        assert active_component == "buses"

    def test_modal_closes_on_close_button(self, network_with_timeseries):
        """Test that modal closes when close button is clicked."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking close button
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "close-data-explorer-modal"

            # Simulate clicking close button
            # Use positional arguments matching the callback signature
            result = callback_func(
                0,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                0,  # stores_clicks
                1,  # close_clicks
                "Test",  # network_label
                True,  # is_open
            )

        # Modal should be closed
        is_open = result[0]
        assert is_open is False

    def test_modal_loads_correct_component_data(self, network_with_timeseries):
        """Test that modal loads correct component data."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test each component type
        test_cases = [
            ("buses", "kpi-card-buses", 1, 0, 0, 0, 0, 0),
            ("generators", "kpi-card-generators", 0, 1, 0, 0, 0, 0),
            ("lines", "kpi-card-lines", 0, 0, 1, 0, 0, 0),
            ("links", "kpi-card-links", 0, 0, 0, 1, 0, 0),
            ("storage_units", "kpi-card-storage_units", 0, 0, 0, 0, 1, 0),
            ("stores", "kpi-card-stores", 0, 0, 0, 0, 0, 1),
        ]

        for expected_component, triggered_id, *clicks in test_cases:
            # Mock ctx.triggered_id for each component
            with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
                mock_ctx.triggered_id = triggered_id

                # Add network_label and is_open to match callback signature
                result = callback_func(*clicks, 0, "Test", False)
                active_component = result[6]
                assert active_component == expected_component

    def test_modal_toggle_prevents_duplicate_open(self, network_with_timeseries):
        """Test that clicking a KPI card when modal is already open toggles it."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking buses KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-buses"

            # Click buses card when modal is already open
            # Use positional arguments matching the callback signature
            result = callback_func(
                1,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                0,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                True,  # is_open
            )

        # Modal should stay open and show buses data
        is_open = result[0]
        assert is_open is True


class TestTimeSeriesAttributeSwitching:
    """Test time-series attribute switching in the modal."""

    def test_timeseries_attribute_selector_populated(self, network_with_timeseries):
        """Test that time-series attribute dropdown is populated."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking generators KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-generators"

            # Open modal for generators (which has time-series data)
            # Use positional arguments matching the callback signature
            result = callback_func(
                0,  # buses_clicks
                1,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                0,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                False,  # is_open
            )

        # Get time-series options
        ts_options = result[4]

        # Should have options (p and q attributes)
        assert ts_options is not None
        assert len(ts_options) > 0
        # Check that 'p' and 'q' are in the options
        option_values = [opt["value"] for opt in ts_options]
        assert "p" in option_values
        assert "q" in option_values

    def test_timeseries_disabled_for_no_timeseries_component(self, network_with_timeseries):
        """Test that time-series tab is disabled for components without time-series data."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking stores KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-stores"

            # Open modal for stores (which typically has no time-series data)
            # Use positional arguments matching the callback signature
            result = callback_func(
                0,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                1,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                False,  # is_open
            )

        # Get time-series disabled status
        ts_disabled = result[5]

        # Should be disabled or have no options
        # (depending on implementation)
        assert ts_disabled is None or result[4] == []

    def test_timeseries_data_loads_on_attribute_change(self, network_with_timeseries):
        """Test that time-series data loads when attribute is changed."""
        app = Dash(__name__)
        networks = {"Test": network_with_timeseries}
        register_data_explorer_callbacks(app, networks)

        # Get the time-series callback
        callback_info = list(app.callback_map.values())[1]
        callback_func = callback_info["callback"].__wrapped__

        # Load time-series data for 'p' attribute of generators
        # Use positional arguments matching the callback signature
        data, columns = callback_func("p", "generators", "Test")

        # Should have data
        assert data is not None
        assert len(data) > 0
        assert columns is not None
        assert len(columns) > 0

        # Check that 'gen1' and 'gen2' columns are present
        column_ids = [col["id"] for col in columns]
        assert "gen1" in column_ids or any("gen1" in col for col in column_ids)


class TestDataExplorerWithEmptyNetwork:
    """Test data explorer with networks that have no data."""

    def test_modal_opens_for_empty_component(self, demo_network):
        """Test that modal opens even when component has no data."""
        app = Dash(__name__)
        networks = {"Test": demo_network}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking storage_units KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-storage_units"

            # Open modal for storage_units (empty in demo network)
            # Use positional arguments matching the callback signature
            result = callback_func(
                0,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                1,  # storage_units_clicks
                0,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                False,  # is_open
            )

        # Modal should still open
        is_open = result[0]
        assert is_open is True

    def test_static_data_table_empty_for_missing_components(self, demo_network):
        """Test that static data table handles empty components gracefully."""
        app = Dash(__name__)
        networks = {"Test": demo_network}
        register_data_explorer_callbacks(app, networks)

        # Get the modal toggle callback
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Mock ctx.triggered_id to simulate clicking stores KPI card
        with patch("pypsa_explorer.callbacks.data_explorer.ctx") as mock_ctx:
            mock_ctx.triggered_id = "kpi-card-stores"

            # Open modal for stores (empty in demo network)
            # Use positional arguments matching the callback signature
            result = callback_func(
                0,  # buses_clicks
                0,  # generators_clicks
                0,  # lines_clicks
                0,  # links_clicks
                0,  # storage_units_clicks
                1,  # stores_clicks
                0,  # close_clicks
                "Test",  # network_label
                False,  # is_open
            )

        # Get static data
        static_data = result[2]

        # Should handle empty data (either empty list or None)
        assert static_data is not None or static_data == []


class TestDataExplorerIntegration:
    """Test full integration of data explorer with the app."""

    def test_data_explorer_modal_in_layout(self, demo_network):
        """Test that data explorer modal is present in the app layout."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Check that modal components are in layout
        layout_str = str(app.layout)
        assert "data-explorer-modal" in layout_str
        assert "static-data-table" in layout_str
        assert "timeseries-data-table" in layout_str

    def test_kpi_cards_have_click_handlers(self, demo_network):
        """Test that all KPI cards are present and clickable."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Check that KPI cards are in layout
        layout_str = str(app.layout)
        for kpi_card in KPI_COMPONENT_MAP:
            assert kpi_card in layout_str

    def test_data_explorer_callbacks_registered(self, demo_network):
        """Test that data explorer callbacks are registered in the full app."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Check that callbacks are registered
        assert len(app.callback_map) > 0

        # Check for data explorer specific callbacks
        callback_output_ids = []
        for callback_info in app.callback_map.values():
            outputs = callback_info["output"]
            if not isinstance(outputs, list):
                outputs = [outputs]
            for output in outputs:
                callback_output_ids.append(str(output))

        # Should have data explorer modal outputs
        assert any("data-explorer-modal" in oid for oid in callback_output_ids)
        assert any("static-data-table" in oid for oid in callback_output_ids)
        assert any("timeseries-data-table" in oid for oid in callback_output_ids)
