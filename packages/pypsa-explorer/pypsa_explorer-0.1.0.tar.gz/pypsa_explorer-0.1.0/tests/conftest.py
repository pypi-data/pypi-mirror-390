"""Pytest configuration and fixtures for PyPSA Explorer tests."""

import pytest

pypsa = pytest.importorskip("pypsa")


@pytest.fixture
def demo_network():
    """Create a simple demo PyPSA network for testing."""
    n = pypsa.Network()

    # Add carriers first
    n.add("Carrier", "AC", nice_name="AC", color="#0000ff")
    n.add("Carrier", "wind", nice_name="Wind", color="#74c6f2")
    n.add("Carrier", "solar", nice_name="Solar", color="#ffea00")

    # Add basic components for testing
    n.add("Bus", "bus1", carrier="AC", x=0, y=0, country="DE")
    n.add("Bus", "bus2", carrier="AC", x=1, y=1, country="FR")

    n.add("Generator", "gen1", bus="bus1", carrier="wind", p_nom=100)
    n.add("Generator", "gen2", bus="bus2", carrier="solar", p_nom=50)

    n.add("Line", "line1", bus0="bus1", bus1="bus2", x=0.1, r=0.01, s_nom=100)

    # Add metadata
    n.meta = {"name": "Test Network", "version": "1.0", "wildcards": {"run": "test", "planning_horizons": "2030"}}

    return n


@pytest.fixture
def networks_dict(demo_network):
    """Create a dictionary of networks for multi-network testing."""
    return {
        "Network 1": demo_network,
        "Network 2": demo_network.copy(),
    }


@pytest.fixture
def demo_network_path(tmp_path, demo_network):
    """Save demo network to temporary file and return path."""
    network_file = tmp_path / "demo_network.nc"
    demo_network.export_to_netcdf(network_file)
    return str(network_file)
