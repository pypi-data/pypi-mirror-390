# Bloomr

[![CI](https://github.com/gnathoi/bloomr/actions/workflows/ci.yml/badge.svg)](https://github.com/gnathoi/bloomr/actions/workflows/ci.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/bloomr.svg)](https://pypi.org/project/bloomr/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Made with Rust](https://img.shields.io/badge/Made%20with-Rust-orange.svg)](https://www.rust-lang.org/)

A Python package for solving the Mixed Chinese Postman Problem on road networks with a high-performance Rust backend.

## What is the Mixed Chinese Postman Problem?

The Chinese Postman Problem asks: what is the shortest route that traverses every edge in a graph at least once? This is useful for planning routes that need to, for example, survey every road in an area as efficiently as possible.

The Mixed CPP extends this to real-world road networks where:

- Some streets are bidirectional (two-way streets that can be traversed in either direction)
- Some streets are directed (one-way streets with mandatory direction)

Finding optimal routes in mixed networks is more complex than the classical all-directed or all-undirected versions of the problem. Bloomr solves this using Edmonds' blossom algorithm for efficient minimum-weight perfect matching.

## What Bloomr Does

Bloomr downloads real road network data from OpenStreetMap, identifies one-way and two-way streets, computes an optimal route that covers every street at least once, and outputs the solution as a GPX file for GPS navigation.

The package uses a Python API for ease of use and a Rust backend for computational performance. The Rust implementation uses the blossom algorithm to find perfect matchings that minimize the total distance of repeated streets.

## Installation

```bash
pip install bloomr
```

## Python API

The API provides two main functions:

### Solve CPP for a location

```python
from bloomr import solve_cpp

# Download road network and solve CPP
result = solve_cpp("Jersey, Channel Islands")

# View solution summary
print(result.summary())

# Access result files
print(f"Route saved to: {result.gpx_path}")
print(f"Metrics: {result.metrics}")
```

### Download a graph separately

```python
from bloomr import download_graph

# Download and cache a road network
graph_path = download_graph("San Francisco, California")

# Solve using the cached graph
result = solve_cpp(graphml_path=graph_path)
```

## API Reference

### solve_cpp()

```python
solve_cpp(
    place: Optional[str] = None,
    *,
    graphml_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    method: str = "blossom",
    verbose: bool = False,
    visualize: bool = True
)
```

Solve the Chinese Postman Problem for a road network.

Arguments:

- `place`: Location name for OSMnx (e.g., "Jersey, Channel Islands")
- `graphml_path`: Path to existing GraphML file (alternative to place)
- `output_dir`: Directory for output files (default: "solutions/{region}")
- `network_type`: Type of road network - "drive", "drive_service", "walk", "bike", or "all"
- `simplify`: Whether to simplify the graph topology
- `method`: Graph balancing algorithm - "blossom" (optimal, default)
- `verbose`: Print detailed progress information
- `visualize`: Generate a route visualization map

Returns a `CPPResult` object containing:

- `graphml_path`: Input graph file
- `gpx_path`: Output GPX route file
- `metrics_path`: JSON file with solution metrics
- `metrics`: Dictionary of solution metrics
- `region`: Region name
- `map_path`: Path to visualization (if generated)

### download_graph()

```python
download_graph(
    place: str,
    *,
    output_dir: Optional[Path] = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    force: bool = False
) -> Path
```

Download a road network from OpenStreetMap and save as GraphML.

Arguments:

- `place`: Location name for OSMnx
- `output_dir`: Directory for GraphML file (default: "graphml_data")
- `network_type`: Type of road network
- `simplify`: Whether to simplify the graph topology
- `force`: Force re-download even if cached

Returns the path to the saved GraphML file.

## Solution Metrics

Each solution includes comprehensive metrics:

- `unique_road_segments`: Total number of distinct streets
- `bidirectional_edge_pairs`: Number of two-way streets
- `one_way_edges`: Number of one-way streets
- `duplication_ratio`: Average times each street is traversed
- `total_original_distance_km`: Total length of all streets (traversed once)
- `total_circuit_distance_km`: Actual route distance
- `distance_efficiency`: Ratio of original to circuit distance
- `deadhead_percentage`: Percentage of route that repeats streets

## Output Files

All outputs are stored in `solutions/{region_name}/`:

- `{region}_cpp_route.gpx`: GPS route file for navigation
- `{region}_metrics.json`: Detailed solution metrics

Graphs are cached in `graphml_data/` to avoid re-downloading.
