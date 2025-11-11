# PyPSA Explorer

[![PyPI version](https://badge.fury.io/py/pypsa-explorer.svg)](https://badge.fury.io/py/pypsa-explorer)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Interactive dashboard for visualizing and analyzing PyPSA energy system networks. Built with Dash and Plotly, PyPSA Explorer provides a comprehensive web interface for exploring energy system models with powerful filtering and visualization capabilities.

## Features

### 📊 Interactive Visualizations
- **Energy Balance Analysis**: Timeseries and aggregated views of energy flows
- **Capacity Planning**: Visualize optimal capacity distribution by carrier and region
- **Economic Analysis**: CAPEX and OPEX breakdowns across the system
- **Network Maps**: Interactive geographical visualization of network topology
- **Multi-Network Support**: Load and compare multiple networks seamlessly

### 🎯 Advanced Filtering
- Filter by energy carrier (sector)
- Filter by country/region
- Dynamic updates across all visualizations
- Tab-specific filter behavior

### 🚀 Production Ready
- Well-structured, modular codebase
- Comprehensive type hints
- Extensive test coverage
- CI/CD pipeline integration
- Professional documentation

## Installation

### From PyPI (Recommended)

```bash
pip install pypsa-explorer
```

### From Source

```bash
git clone https://github.com/openenergytransition/pypsa-explorer.git
cd pypsa-explorer
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/openenergytransition/pypsa-explorer.git
cd pypsa-explorer
pip install -e ".[dev]"
pre-commit install
```

## Quick Start

### Command Line Interface

Launch the landing page and drag-and-drop networks or load the bundled example:
```bash
pypsa-explorer
```

Run with your own network:
```bash
pypsa-explorer /path/to/network.nc
```

Run with multiple networks:
```bash
pypsa-explorer /path/to/network1.nc:Label1 /path/to/network2.nc:Label2
```

Custom host and port:
```bash
pypsa-explorer --host 0.0.0.0 --port 8080
```

Production mode (no debug):
```bash
pypsa-explorer --no-debug
```

### Python API

```python
from pypsa_explorer import run_dashboard

# Run with default network
run_dashboard()

# Run with custom network
run_dashboard("/path/to/network.nc")

# Run with multiple networks
networks = {
    "Scenario A": "/path/to/network1.nc",
    "Scenario B": "/path/to/network2.nc",
}
run_dashboard(networks, debug=True, host="0.0.0.0", port=8050)

# Run with Network objects
import pypsa
n1 = pypsa.Network("network1.nc")
n2 = pypsa.Network("network2.nc")

run_dashboard({"Network 1": n1, "Network 2": n2})
```

### Programmatic App Creation

```python
from pypsa_explorer import create_app

# Create app instance
app = create_app(networks_input="/path/to/network.nc", title="My Dashboard")

# Run with custom server
app.run(debug=True, host="0.0.0.0", port=8050)
```

## Project Structure

```
pypsa-explorer/
├── src/
│   └── pypsa_explorer/
│       ├── __init__.py           # Package initialization
│       ├── app.py                # Main application factory
│       ├── cli.py                # Command-line interface
│       ├── config.py             # Configuration and theming
│       ├── callbacks/            # Dash callbacks
│       │   ├── __init__.py
│       │   ├── filters.py        # Filter callbacks
│       │   ├── navigation.py     # Navigation callbacks
│       │   ├── network.py        # Network callbacks
│       │   └── visualizations.py # Visualization callbacks
│       ├── layouts/              # UI layouts
│       │   ├── __init__.py
│       │   ├── components.py     # Reusable components
│       │   ├── dashboard.py      # Main dashboard layout
│       │   ├── tabs.py           # Tab definitions
│       │   └── welcome.py        # Welcome page
│       └── utils/                # Utility functions
│           ├── __init__.py
│           ├── helpers.py        # Helper functions
│           └── network_loader.py # Network loading utilities
├── tests/                        # Test suite
├── docs/                         # Documentation
├── examples/                     # Example notebooks and scripts
├── pyproject.toml               # Project configuration
├── README.md                    # This file
├── LICENSE                      # MIT License
└── CHANGELOG.md                 # Version history
```

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/openenergytransition/pypsa-explorer.git
cd pypsa-explorer

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pypsa_explorer --cov-report=html

# Run specific test file
pytest tests/test_app.py
```

### Code Quality

```bash
# Format code
black src/ tests/
ruff format src/ tests/

# Lint code
ruff check src/ tests/ --fix

# Type checking
mypy src/
```

### Building Documentation

```bash
cd docs
make html
```

## Configuration

### Custom Styling

The dashboard theme can be customized by modifying `src/pypsa_explorer/config.py`:

```python
COLORS = {
    "primary": "#2c3e50",
    "secondary": "#3498db",
    "accent": "#2ecc71",
    # ... more colors
}
```

### Default Settings

- **Port**: 8050
- **Host**: 127.0.0.1 (localhost)
- **Debug Mode**: True (disable with `--no-debug`)
- **Default Carriers**: AC, Hydrogen Storage, Low Voltage

## Requirements

- Python >= 3.12
- PyPSA (from GitHub master)
- Dash >= 2.14
- Plotly >= 5.0
- Folium >= 0.14
- dash-bootstrap-components >= 1.5

See `pyproject.toml` for complete dependency list.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

Please ensure:
- All tests pass
- Code is properly formatted (black/ruff)
- Type hints are included
- Documentation is updated

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use PyPSA Explorer in your research, please cite:

```bibtex
@software{pypsa_explorer,
  title = {PyPSA Explorer: Interactive Dashboard for Energy System Analysis},
  author = {Open Energy Transition},
  year = {2024},
  url = {https://github.com/openenergytransition/pypsa-explorer}
}
```

## Acknowledgments

- Built on [PyPSA](https://pypsa.org) - Python for Power System Analysis
- Powered by [Dash](https://dash.plotly.com/) and [Plotly](https://plotly.com/)
- Developed by [Open Energy Transition](https://openenergytransition.org)

## Support

- **Documentation**: [https://pypsa-explorer.readthedocs.io](https://pypsa-explorer.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/openenergytransition/pypsa-explorer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/openenergytransition/pypsa-explorer/discussions)

## Roadmap

- [ ] Export functionality (PNG, PDF, data export)
- [ ] Advanced comparison mode for multiple networks
- [ ] Custom calculation and plotting plugins
- [ ] Real-time data streaming support
- [ ] Collaborative features and sharing
- [ ] Integration with cloud storage (S3, GCS)

## Related Projects

- [PyPSA](https://github.com/PyPSA/PyPSA) - The core power system analysis framework
- [PyPSA-Eur](https://github.com/PyPSA/pypsa-eur) - Open energy system model for Europe
- [PyPSA-Earth](https://github.com/pypsa-meets-earth/pypsa-earth) - Global energy system model
