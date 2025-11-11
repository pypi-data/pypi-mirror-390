# GTFS-flex-to-GOFS

[![Build Status](https://github.com/TransitApp/GTFS-flex-to-GOFS/actions/workflows/pull-request.yml/badge.svg)](https://github.com/TransitApp/GTFS-flex-to-GOFS/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python tool to convert [GTFS-Flex](https://github.com/MobilityData/gtfs-flex) (General Transit Feed Specification - Flexible services) data to the [GOFS](https://gofs.org) (General On-demand Feed Specification) format.

This tool processes on-demand and flexible transit services data from GTFS-Flex feeds and outputs standardized GOFS files for consumption by trip planning applications and mobility platforms.

## Installation

Install from PyPI:
```bash
pip install GTFS-flex-to-GOFS
```

Or install from source:
```bash
git clone https://github.com/TransitApp/GTFS-flex-to-GOFS.git
cd GTFS-flex-to-GOFS
uv sync --extra dev
```

## Usage

```bash
gtfs-flex-to-gofs --gtfs-dir <input_dir> --gofs-dir <output_dir> --url <base_url>
```

### Command Line Options

```
optional arguments:
  -h, --help           show this help message and exit
  --gtfs-dir Dir       input gtfs directory
  --gofs-dir Dir       output gofs directory
  --url URL            auto-discovery url. Base URL indicate for where each files will be uploaded (and downloadable)
  --ttl TTL            time to live of the generated gofs files in seconds (default: 86400)
  --no-warning         Silence warnings
```

## Development

### Running Tests

```bash
uv run python -m pytest .
# or for verbose output:
uv run python -m pytest tests/ -v
```

### Regenerating Test Fixtures

```bash
./createTests.sh
```

## Features

- Converts GTFS-Flex pure microtransit services to GOFS format
- Supports zone-based on-demand transit operations
- Generates all required GOFS files (zones, calendars, fares, booking rules, etc.)
- Optional split-by-route output for multi-service feeds
- Automated CI/CD with GitHub Actions

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [GTFS-Flex Specification](https://github.com/MobilityData/gtfs-flex)
- [GOFS Specification](https://gofs.org)
- [py-gtfs-loader](https://github.com/TransitApp/py-gtfs-loader)
