"""
Bloomr: Memory-efficient Chinese Postman Problem solver.

Bloomr is a modern Python package for solving the Chinese Postman Problem (CPP)
on road networks. It uses a high-performance Rust backend with the blossom algorithm
for efficient perfect matching.

The package provides a simple, pythonic API for:
- Downloading road networks from OpenStreetMap via OSMnx
- Computing optimal routes that traverse every road segment at least once
- Generating GPS-compatible GPX files for navigation

Basic Usage:
    >>> from bloomr import solve_cpp
    >>>
    >>> # Solve CPP for a region
    >>> result = solve_cpp("Jersey, Channel Islands")
    >>> print(result.summary())
    >>>
    >>> # Access the GPX route file
    >>> print(f"GPX route: {result.gpx_path}")

Advanced Usage:
    >>> from bloomr import download_graph, solve_cpp
    >>>
    >>> # Download and cache a graph
    >>> graph_path = download_graph("San Francisco, California")
    >>>
    >>> # Solve using the cached graph
    >>> result = solve_cpp(graphml_path=graph_path)
"""

from .download import download_graph, sanitize_filename
from .solver import CPPResult, solve_cpp

__version__ = "0.1.1"

__all__ = [
    "solve_cpp",
    "download_graph",
    "sanitize_filename",
    "CPPResult",
]

# Visualization is optional - only import if dependencies are available
try:
    from .visualize import plot_route_map  # noqa: F401

    __all__.append("plot_route_map")
except ImportError:
    pass
