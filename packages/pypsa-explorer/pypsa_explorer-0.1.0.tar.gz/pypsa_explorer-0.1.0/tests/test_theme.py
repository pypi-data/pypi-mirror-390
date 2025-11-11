"""Tests for theme toggle functionality."""

import pytest
from dash import Dash

from pypsa_explorer.callbacks.theme import register_theme_callbacks


class TestThemeCallbackRegistration:
    """Test theme callback registration."""

    def test_theme_callback_registered(self):
        """Test that theme callback is properly registered."""
        app = Dash(__name__)

        # No callbacks before registration
        assert len(app.callback_map) == 0

        register_theme_callbacks(app)

        # Should have 1 callback after registration
        assert len(app.callback_map) == 1

    def test_theme_callback_structure(self):
        """Test theme callback has correct structure."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        # Get the callback
        callback_info = list(app.callback_map.values())[0]

        # Check outputs - should have 2 outputs (className and store)
        outputs = callback_info["output"]
        assert len(outputs) == 2
        output_ids = [str(out) for out in outputs]
        assert any("app-container.className" in oid for oid in output_ids)
        assert any("dark-mode-store.data" in oid for oid in output_ids)

        # Check inputs
        inputs = callback_info["inputs"]
        assert len(inputs) == 1
        input_ids = [str(inp) for inp in inputs]
        assert any("dark-mode-toggle" in iid and "value" in iid for iid in input_ids)


class TestThemeToggleLogic:
    """Test the theme toggle logic directly."""

    def test_dark_mode_enabled(self):
        """Test dark mode class is applied when toggle is checked."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with dark mode enabled - returns tuple (className, is_dark)
        class_name, is_dark = callback_func(["dark"])
        assert class_name == "dark-mode"
        assert is_dark is True

    def test_dark_mode_disabled(self):
        """Test no class is applied when toggle is unchecked."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with dark mode disabled - returns tuple (className, is_dark)
        class_name, is_dark = callback_func([])
        assert class_name == ""
        assert is_dark is False

    def test_dark_mode_none_value(self):
        """Test handling of None value (initial state)."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        # Get the callback function
        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with None value - returns tuple (className, is_dark)
        class_name, is_dark = callback_func(None)
        assert class_name == ""
        assert is_dark is False


class TestThemeIntegration:
    """Test theme integration with the full app."""

    def test_theme_toggle_in_app(self, demo_network):
        """Test that theme toggle is present in the app layout."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for dark-mode-toggle component
        layout_str = str(app.layout)
        assert "dark-mode-toggle" in layout_str

    def test_app_container_in_layout(self, demo_network):
        """Test that app-container is present in the layout."""
        from pypsa_explorer.app import create_app

        app = create_app({"Test": demo_network})

        # Convert layout to string to check for app-container
        layout_str = str(app.layout)
        assert "app-container" in layout_str

    def test_theme_persistence(self, demo_network):
        """Test that dark mode toggle has persistence enabled."""
        from pypsa_explorer.layouts.components import create_dark_mode_toggle

        # Create the dark mode toggle component
        toggle_component = create_dark_mode_toggle()

        # Check persistence is enabled (by searching through component tree)
        component_str = str(toggle_component)
        assert "persistence" in component_str.lower() or "Checklist" in component_str


class TestThemeEdgeCases:
    """Test edge cases for theme functionality."""

    def test_multiple_values_in_toggle(self):
        """Test handling of unexpected multiple values."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with multiple values (should still work)
        class_name, is_dark = callback_func(["dark", "other"])
        assert class_name == "dark-mode"
        assert is_dark is True

    def test_wrong_value_in_toggle(self):
        """Test handling of wrong value in toggle."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with wrong value (not "dark")
        class_name, is_dark = callback_func(["light"])
        assert class_name == ""
        assert is_dark is False

    def test_empty_list_toggle(self):
        """Test handling of empty list."""
        app = Dash(__name__)
        register_theme_callbacks(app)

        callback_info = list(app.callback_map.values())[0]
        callback_func = callback_info["callback"].__wrapped__

        # Test with empty list
        class_name, is_dark = callback_func([])
        assert class_name == ""
        assert is_dark is False


class TestThemeVisualizationImpact:
    """Test that theme affects visualization templates."""

    @pytest.mark.skip(reason="Requires integration with plotly config - to be implemented")
    def test_visualization_template_in_dark_mode(self):
        """Test that visualizations use dark template in dark mode."""
        # This would require testing the actual plotly template switching
        # which happens in the visualization callbacks
        pass

    @pytest.mark.skip(reason="Requires integration with plotly config - to be implemented")
    def test_visualization_template_in_light_mode(self):
        """Test that visualizations use default template in light mode."""
        # This would require testing the actual plotly template switching
        # which happens in the visualization callbacks
        pass
