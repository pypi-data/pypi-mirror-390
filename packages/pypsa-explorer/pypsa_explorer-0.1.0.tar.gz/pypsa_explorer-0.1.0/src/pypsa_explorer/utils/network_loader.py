"""Network loading utilities for PyPSA Explorer."""

import os

import pypsa


def load_networks(
    network_input: dict[str, pypsa.Network | str] | str | None = None,
    default_network_path: str = "demo-network.nc",
) -> dict[str, pypsa.Network]:
    """
    Load PyPSA networks from various input formats.

    Parameters
    ----------
    network_input : dict, str, or None
        Can be:
        - dict: {label: network_object_or_path} mapping labels to Network objects or file paths
        - str: Single path to a network file
        - None: Load default demo network
    default_network_path : str
        Path to default network file when network_input is None

    Returns
    -------
    dict[str, pypsa.Network]
        Dictionary mapping labels to loaded Network objects

    Raises
    ------
    FileNotFoundError
        If a specified network file does not exist
    ValueError
        If no valid networks could be loaded
    """
    networks: dict[str, pypsa.Network] = {}

    if network_input is None:
        # Load default network
        if os.path.exists(default_network_path):
            networks = {"Network": pypsa.Network(default_network_path)}
        else:
            raise FileNotFoundError(f"Default network file not found: {default_network_path}")

    elif isinstance(network_input, str):
        # Single network path provided
        if os.path.exists(network_input):
            networks = {"Network": pypsa.Network(network_input)}
        else:
            raise FileNotFoundError(f"Network file not found: {network_input}")

    elif isinstance(network_input, dict):
        # Dictionary of networks provided
        for label, net_or_path in network_input.items():
            if isinstance(net_or_path, str):
                if os.path.exists(net_or_path):
                    networks[label] = pypsa.Network(net_or_path)
                else:
                    print(f"Warning: Network file not found: {net_or_path}")
            elif isinstance(net_or_path, pypsa.Network):
                networks[label] = net_or_path
            else:
                print(f"Warning: Invalid type for network {label}. Skipping.")
    else:
        raise ValueError("network_input must be either a string path, a dictionary {label: path}, or None")

    if not networks:
        raise ValueError("No valid networks were loaded")

    return networks


def parse_cli_network_args(args: list[str]) -> dict[str, str]:
    """
    Parse command line arguments for network loading.

    Format: path:label or just path (label will be derived from filename)

    Parameters
    ----------
    args : list[str]
        Command line arguments in format "path:label" or "path"

    Returns
    -------
    dict[str, str]
        Dictionary mapping labels to file paths
    """
    network_paths = {}

    for arg in args:
        if ":" in arg:
            path, label = arg.split(":", 1)
        else:
            path = arg
            # Create default label from filename
            label = os.path.splitext(os.path.basename(path))[0]

        network_paths[label] = path

    return network_paths
