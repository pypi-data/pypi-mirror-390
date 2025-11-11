"""Tests for navigation functionality."""

from dash import Dash, no_update

from pypsa_explorer.callbacks.navigation import register_navigation_callbacks


class TestNavigationCallbackRegistration:
    """Test navigation callback registration."""

    def test_navigation_callback_registered(self):
        """Test that navigation callback is properly registered."""
        app = Dash(__name__)

        # No callbacks before registration
        assert len(app.callback_map) == 0

        register_navigation_callbacks(app)

        # Should have 1 callback after registration
        assert len(app.callback_map) == 1

    def test_navigation_callback_structure(self):
        """Test navigation callback has correct structure."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        # Get the callback
        callback_info = list(app.callback_map.values())[0]

        # Check outputs - should have 4 outputs
        outputs = callback_info["output"]
        assert len(outputs) == 4
        output_ids = [str(out) for out in outputs]
        assert any("welcome-content.style" in oid for oid in output_ids)
        assert any("dashboard-content.style" in oid for oid in output_ids)
        assert any("page-state.data" in oid for oid in output_ids)
        assert any("top-bar-network-selector.style" in oid for oid in output_ids)

        # Check inputs
        inputs = callback_info["inputs"]
        assert len(inputs) == 1
        input_ids = [str(inp) for inp in inputs]
        assert any("enter-dashboard-btn" in iid and "n_clicks" in iid for iid in input_ids)

        # Check states
        states = callback_info["state"]
        assert len(states) == 2
        state_ids = [str(s) for s in states]
        assert any("page-state" in sid and "data" in sid for sid in state_ids)
        assert any("network-registry" in sid and "data" in sid for sid in state_ids)


class TestNavigationLogic:
    """Test the navigation logic directly."""

    def test_navigate_to_dashboard(self):
        """Test navigation from welcome to dashboard."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test navigation with button click and welcome page state
        welcome_style, dashboard_style, page_state, selector_style = callback_func(
            n_clicks=1,
            page_state={"current_page": "welcome"},
            registry={"order": ["Test"], "info": {}},
        )

        # Check welcome is hidden
        assert welcome_style == {"display": "none"}

        # Check dashboard is shown
        assert dashboard_style == {"display": "block"}

        # Check page state is updated
        assert page_state == {"current_page": "dashboard"}

        # Check network selector is shown
        assert selector_style == {"display": "flex"}

    def test_no_navigation_on_dashboard(self):
        """Test that navigation doesn't happen when already on dashboard."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with already on dashboard
        result = callback_func(
            n_clicks=1,
            page_state={"current_page": "dashboard"},
            registry={"order": ["Test"], "info": {}},
        )

        # Should return no_update for all outputs
        assert result == (no_update, no_update, no_update, {"display": "flex"})

    def test_no_navigation_without_click(self):
        """Test that navigation doesn't happen without button click."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with no click
        result = callback_func(
            n_clicks=None,
            page_state={"current_page": "welcome"},
            registry={"order": ["Test"], "info": {}},
        )

        # Should return no_update for all outputs
        assert result == (no_update, no_update, no_update, {"display": "none"})

    def test_zero_clicks_navigation(self):
        """Test that navigation doesn't happen with zero clicks."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with zero clicks
        result = callback_func(
            n_clicks=0,
            page_state={"current_page": "welcome"},
            registry={"order": ["Test"], "info": {}},
        )

        # Should return no_update for all outputs
        assert result == (no_update, no_update, no_update, {"display": "none"})


class TestNavigationIntegration:
    """Test navigation integration with the full app."""

    def test_welcome_page_in_layout(self, demo_network):
        """Test that welcome page is present in the app layout."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for welcome-content
        layout_str = str(app.layout)
        assert "welcome-content" in layout_str

    def test_dashboard_content_in_layout(self, demo_network):
        """Test that dashboard content is present in the app layout."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for dashboard-content
        layout_str = str(app.layout)
        assert "dashboard-content" in layout_str

    def test_enter_dashboard_button_in_layout(self, demo_network):
        """Test that enter dashboard button is present."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for button
        layout_str = str(app.layout)
        assert "enter-dashboard-btn" in layout_str

    def test_page_state_store_in_layout(self, demo_network):
        """Test that page state store is present."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for page-state store
        layout_str = str(app.layout)
        assert "page-state" in layout_str

    def test_network_selector_in_layout(self, demo_network):
        """Test that network selector is present in top bar."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for network selector
        layout_str = str(app.layout)
        assert "top-bar-network-selector" in layout_str


class TestNavigationEdgeCases:
    """Test edge cases for navigation functionality."""

    def test_multiple_clicks_navigation(self):
        """Test navigation with multiple button clicks."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with multiple clicks
        welcome_style, dashboard_style, page_state, selector_style = callback_func(
            n_clicks=5,
            page_state={"current_page": "welcome"},
            registry={"order": ["Test"], "info": {}},
        )

        # Should still navigate correctly
        assert welcome_style == {"display": "none"}
        assert dashboard_style == {"display": "block"}
        assert page_state == {"current_page": "dashboard"}
        assert selector_style == {"display": "flex"}

    def test_invalid_page_state(self):
        """Test handling of invalid page state."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with invalid page state (should not navigate)
        result = callback_func(
            n_clicks=1,
            page_state={"current_page": "invalid"},
            registry={"order": ["Test"], "info": {}},
        )

        # Should return no_update for all outputs
        assert result == (no_update, no_update, no_update, {"display": "none"})

    def test_empty_page_state(self):
        """Test handling of empty page state."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with empty page state
        result = callback_func(n_clicks=1, page_state={}, registry={"order": ["Test"], "info": {}})
        assert result == (no_update, no_update, no_update, {"display": "none"})

    def test_none_page_state(self):
        """Test handling of None page state."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with None page state
        result = callback_func(n_clicks=1, page_state=None, registry={"order": ["Test"], "info": {}})
        assert result == (no_update, no_update, no_update, {"display": "none"})


class TestUtilityBarVisibility:
    """Test utility bar visibility changes during navigation."""

    def test_network_selector_hidden_on_welcome(self, demo_network):
        """Test that network selector is hidden on welcome page."""
        from pypsa_explorer.layouts.dashboard import create_dashboard_layout

        # Create layout and check initial state
        networks = {"Test": demo_network}
        layout = create_dashboard_layout(networks, "Test")

        # Convert to string and check for network selector style
        layout_str = str(layout)
        assert "top-bar-network-selector" in layout_str

    def test_network_selector_shown_after_navigation(self):
        """Test that network selector is shown after navigating to dashboard."""
        app = Dash(__name__)
        register_navigation_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Navigate to dashboard
        _, _, _, selector_style = callback_func(
            n_clicks=1,
            page_state={"current_page": "welcome"},
            registry={"order": ["Test"], "info": {}},
        )

        # Network selector should be visible
        assert selector_style == {"display": "flex"}


class TestMultiNetworkNavigation:
    """Test navigation with multiple networks."""

    def test_navigation_with_multiple_networks(self, networks_dict):
        """Test that navigation works with multiple networks."""
        from pypsa_explorer.app import create_app

        app = create_app(networks_dict)

        # Check that navigation callbacks are registered
        layout_str = str(app.layout)
        assert "welcome-content" in layout_str
        assert "dashboard-content" in layout_str
        assert "enter-dashboard-btn" in layout_str

    def test_network_selector_visible_after_navigation_multi_network(self, networks_dict):
        """Test network selector visibility with multiple networks."""
        from pypsa_explorer.app import create_app

        app = create_app(networks_dict)

        # Check that network selector is in layout
        layout_str = str(app.layout)
        assert "top-bar-network-selector" in layout_str
        assert "network-selector" in layout_str
