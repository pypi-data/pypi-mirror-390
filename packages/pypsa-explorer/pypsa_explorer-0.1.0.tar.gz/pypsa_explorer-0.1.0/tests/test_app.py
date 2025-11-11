"""Tests for main application module."""

from dash import dcc

from pypsa_explorer.app import create_app


def test_create_app_with_demo_network(demo_network):
    """Test app creation with a demo network."""
    app = create_app({"Test": demo_network})
    assert app is not None
    assert app.title == "PyPSA Explorer"


def test_create_app_with_network_path(demo_network_path):
    """Test app creation with network file path."""
    app = create_app(demo_network_path)
    assert app is not None


def test_create_app_with_dict(networks_dict):
    """Test app creation with multiple networks."""
    app = create_app(networks_dict)
    assert app is not None


def test_create_app_with_none():
    """Test app creation with default network (uses demo-network.nc if available)."""
    # This test will pass if demo-network.nc exists in the project root
    try:
        app = create_app(None)
        assert app is not None
    except FileNotFoundError:
        # This is also acceptable if demo-network.nc doesn't exist
        pass


def test_create_app_without_initial_networks():
    """Starting without networks should provide an empty registry for uploads."""
    app = create_app(None, load_default_on_start=False)
    assert app is not None

    def _find_store(component, target_id):
        if isinstance(component, dcc.Store) and component.id == target_id:
            return component
        children = getattr(component, "children", None)
        if isinstance(children, list):
            for child in children:
                found = _find_store(child, target_id)
                if found is not None:
                    return found
        elif children is not None:
            return _find_store(children, target_id)
        return None

    registry_store = _find_store(app.layout, "network-registry")
    assert registry_store is not None
    assert registry_store.data["order"] == []


def test_example_button_enabled_with_demo_network(demo_network_path):
    """Example button should be enabled when demo network path exists."""
    from pypsa_explorer.layouts.dashboard import create_dashboard_layout

    layout = create_dashboard_layout({}, None, default_network_path=demo_network_path)

    def _find_component(component, target_id):
        if getattr(component, "id", None) == target_id:
            return component
        children = getattr(component, "children", None)
        if isinstance(children, list):
            for child in children:
                found = _find_component(child, target_id)
                if found is not None:
                    return found
        elif children is not None:
            return _find_component(children, target_id)
        return None

    example_button = _find_component(layout, "load-example-network-btn")
    assert example_button is not None
    assert getattr(example_button, "disabled", None) is False


def test_create_app_custom_title(demo_network):
    """Test app creation with custom title."""
    app = create_app({"Test": demo_network}, title="Custom Dashboard")
    assert app.title == "Custom Dashboard"


def test_app_has_layout(demo_network):
    """Test that created app has a layout."""
    app = create_app({"Test": demo_network})
    assert app.layout is not None


def test_app_has_callbacks(demo_network):
    """Test that callbacks are registered."""
    app = create_app({"Test": demo_network})
    # Check that callbacks exist
    assert len(app.callback_map) > 0
