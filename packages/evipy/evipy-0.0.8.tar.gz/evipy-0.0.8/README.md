# evipy

[![PyPI version](https://badge.fury.io/py/evipy.svg)](https://badge.fury.io/py/evipy)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A Python library for controlling Eviqo devices via cloud connection. Monitor your Eviqo charging stations and retrieve real-time data through WebSocket communication.

## Features

- Real-time monitoring of Eviqo charging stations
- WebSocket-based communication with Eviqo cloud services
- Live widget updates and device status tracking
- Automatic session management and authentication
- Type-safe data models with Pydantic

## Installation

Install evipy from PyPI:

```bash
pip install evipy
```

## Quick Start

### Prerequisites

Before using evipy, you need to set up your Eviqo credentials as environment variables:

```bash
export EVIQO_EMAIL="your-email@example.com"
export EVIQO_PASSWORD="your-password"
```

Alternatively, create a `.env` file in your project directory:

```env
EVIQO_EMAIL=your-email@example.com
EVIQO_PASSWORD=your-password
```

### Running the Monitor

To start monitoring your Eviqo devices in real-time:

```bash
python -m evipy.evipy
```

This will:
1. Connect to the Eviqo cloud service
2. Authenticate using your credentials
3. Discover your devices
4. Display live updates from your charging stations

### Example Output

```
14:23:15 - evipy - login:195 - Found device name='Home Charger' deviceId=89349
14:23:16 - evipy - parse_widget_update:344 - {'widget_id': '5', 'widget_name': 'Charging Power', 'device_id': '89349', 'widget_value': '241.29'}
```

## Requirements

- Python 3.12 or higher
- Eviqo account with device access
- Internet connection for cloud communication

## Development

### Setting up Development Environment

1. Clone the repository:
```bash
git clone https://github.com/zacharyasmith/evipy.git
cd evipy
```

2. Install development dependencies:
```bash
pip install -e ".[dev]"
```

3. Set up your environment variables as described above.

### Code Quality

**Just use pre-commit for standard checks!**

This project uses:
- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Pydantic** for data validation
- **pytest** for testing

Run quality checks:
```bash
pre-commit run --all
```

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Ensure `pre-commit` is installed
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Issues and Support

If you encounter any issues or have questions:

- **Bug Reports**: [GitHub Issues](https://github.com/zacharyasmith/evipy/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/zacharyasmith/evipy/issues)
- **Questions**: [GitHub Discussions](https://github.com/zacharyasmith/evipy/discussions)

When reporting bugs, please include:
- Python version
- evipy version (`pip show evipy`)
- Error messages and stack traces
- Steps to reproduce the issue

## Related Projects

- **eviqo-hacs**: Home Assistant Custom Component for Eviqo integration

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This is an unofficial library and is not affiliated with or endorsed by Eviqo. Use at your own risk.
