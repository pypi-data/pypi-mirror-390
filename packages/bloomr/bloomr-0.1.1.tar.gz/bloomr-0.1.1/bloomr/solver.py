"""
Chinese Postman Problem solver using Rust blossom algorithm.

This module provides the main solver function that interfaces with the Rust
backend implementation of the blossom algorithm for efficient perfect matching.
"""

import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional, Union

from .download import download_graph, sanitize_filename


def _get_platform_suffix() -> str:
    """
    Get the platform-specific suffix for the Rust binary.

    Returns:
        Platform suffix like 'linux-x86_64', 'macos-aarch64', etc.

    Raises:
        RuntimeError: If the platform is not supported
    """
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize machine architecture
    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("arm64", "aarch64"):
        arch = "aarch64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    # Map to platform suffixes
    if system == "linux":
        return f"linux-{arch}"
    elif system == "darwin":
        return f"macos-{arch}"
    elif system == "windows":
        return f"windows-{arch}"
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


def _find_rust_binary() -> Path:
    """
    Find the Rust binary in either the packaged location or development location.

    Tries in order:
    1. Packaged binary in bloomr/bin/ (platform-specific)
    2. Development release build in bloomr-rust/target/release/
    3. Development debug build in bloomr-rust/target/debug/

    Returns:
        Path to the Rust binary

    Raises:
        RuntimeError: If binary cannot be found
    """
    package_dir = Path(__file__).parent
    project_root = package_dir.parent

    # Try packaged binary first
    try:
        platform_suffix = _get_platform_suffix()
        binary_name = f"bloomr-rust-{platform_suffix}"
        if sys.platform == "win32":
            binary_name += ".exe"

        packaged_binary = package_dir / "bin" / binary_name
        if packaged_binary.exists():
            return packaged_binary
    except RuntimeError:
        # Platform not supported for packaged binary, fall through to dev builds
        pass

    # Try development builds
    binary_name = "bloomr-rust.exe" if sys.platform == "win32" else "bloomr-rust"

    # Try release build
    dev_release_binary = project_root / "bloomr-rust" / "target" / "release" / binary_name
    if dev_release_binary.exists():
        return dev_release_binary

    # Try debug build
    dev_debug_binary = project_root / "bloomr-rust" / "target" / "debug" / binary_name
    if dev_debug_binary.exists():
        return dev_debug_binary

    raise RuntimeError("Rust binary not found in any expected location")


class CPPResult:
    """
    Results from solving the Chinese Postman Problem.

    Attributes:
        graphml_path: Path to the input GraphML file
        gpx_path: Path to the generated GPX route file
        metrics_path: Path to the metrics JSON file
        map_path: Path to the route visualization PNG (if generated)
        metrics: Dictionary containing solution metrics
        region: Region name
    """

    def __init__(
        self,
        graphml_path: Path,
        gpx_path: Path,
        metrics_path: Path,
        metrics: dict,
        region: str,
        map_path: Optional[Path] = None,
    ):
        self.graphml_path = graphml_path
        self.gpx_path = gpx_path
        self.metrics_path = metrics_path
        self.map_path = map_path
        self.metrics = metrics
        self.region = region

    def __repr__(self) -> str:
        return (
            f"CPPResult(region='{self.region}', "
            f"distance={self.metrics.get('total_circuit_distance_km', 0):.2f}km, "
            f"efficiency={self.metrics.get('distance_efficiency', 0):.4f})"
        )

    def summary(self) -> str:
        """
        Get a formatted summary of the solution.

        Returns:
            Multi-line string with key metrics
        """
        m = self.metrics
        map_line = f"  Map:                       {self.map_path}\n" if self.map_path else ""

        unique_segments = m.get("unique_road_segments", 0)
        base_edges = m.get("base_graph_edges", 0)
        circuit_edges = m.get("circuit_length", 0)
        bidirectional = m.get("bidirectional_edge_pairs", 0)
        oneway = m.get("one_way_edges", 0)

        orig_dist = m.get("total_original_distance_km", 0)
        circuit_dist = m.get("total_circuit_distance_km", 0)
        extra_dist = circuit_dist - orig_dist
        actual_dup = m.get("duplication_ratio", 0)

        dist_eff = m.get("distance_efficiency", 0)
        time_eff = m.get("time_efficiency", 0)
        deadhead = m.get("deadhead_percentage", 0)

        return f"""
Bloomr CPP Solution (Mixed CPP) for {self.region}
{'='*70}

GRAPH STRUCTURE:
  Unique road segments:      {unique_segments}
    - Bidirectional (two-way): {bidirectional}
    - One-way:                 {oneway}
  Base graph edges:          {base_edges}
    (bidirectional edges stored in both directions for Mixed CPP)

SOLUTION METRICS:
  Duplication ratio: {actual_dup:.4f}
    - How many times each road is traversed on average
    - Ratio: circuit_edges / unique_segments
    - {circuit_edges} / {unique_segments} = {actual_dup:.4f}

  Total original distance: {orig_dist:.2f} km (all roads once)
  Total circuit distance:  {circuit_dist:.2f} km (actual route)
  Extra distance needed:   {extra_dist:.2f} km ({deadhead:.1f}%)

  Distance efficiency: {dist_eff * 100:.1f}%
  Time efficiency:     {time_eff * 100:.1f}%

OUTPUT FILES:
  GPX route:                 {self.gpx_path}
  Metrics:                   {self.metrics_path}
{map_line}{'='*70}
"""


def solve_cpp(
    place: Optional[str] = None,
    *,
    graphml_path: Optional[Union[Path, str]] = None,
    output_dir: Optional[Union[Path, str]] = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    method: str = "blossom",
    verbose: bool = False,
    visualize: bool = True,
) -> CPPResult:
    """
    Solve the Chinese Postman Problem for a road network.

    This function finds an optimal route that traverses every road segment at least once,
    using the Rust implementation for efficient perfect matching.

    You can either:
    1. Provide a place name, and the graph will be downloaded automatically
    2. Provide a path to an existing GraphML file

    Args:
        place: OSMnx place query (e.g., "Jersey, Channel Islands").
               If provided, the graph will be downloaded automatically.
        graphml_path: Path to an existing GraphML file from OSMnx.
                     If provided, this takes precedence over place.
        output_dir: Output directory for solution files (GPX, metrics).
                   Defaults to "solutions/<region_name>"
        network_type: Type of network to download if place is provided.
                     Options: "drive", "drive_service", "walk", "bike", "all"
        simplify: Whether to simplify the downloaded graph. Only used if place is provided.
        method: Graph balancing algorithm to use.
               Only "blossom" is supported: Optimal O(n³) algorithm using Edmonds' blossom
               algorithm for minimum weight perfect matching.
        verbose: Enable verbose logging from the Rust solver
        visualize: Whether to generate a map visualization PNG.
                  Requires matplotlib and contextily (install with: pip install 'bloomr[viz]')

    Returns:
        CPPResult object containing paths to output files and solution metrics

    Raises:
        ValueError: If neither place nor graphml_path is provided, or if both are provided
        FileNotFoundError: If graphml_path is provided but doesn't exist
        RuntimeError: If the Rust solver fails

    Examples:
        >>> from bloomr import solve_cpp
        >>>
        >>> # Solve for a place (downloads graph automatically)
        >>> result = solve_cpp("Jersey, Channel Islands")
        >>> print(result.summary())
        >>>
        >>> # Solve for an existing GraphML file
        >>> result = solve_cpp(graphml_path="my_graph.graphml")
        >>> print(f"Route saved to: {result.gpx_path}")
    """
    # Validate inputs
    if place is None and graphml_path is None:
        raise ValueError("Either 'place' or 'graphml_path' must be provided")

    if place is not None and graphml_path is not None:
        raise ValueError("Provide either 'place' or 'graphml_path', not both")

    # Validate method
    if method != "blossom":
        raise ValueError(f"Invalid method '{method}'. Only 'blossom' is supported")

    # Determine region name
    if place is not None:
        region = sanitize_filename(place)
        # Download graph
        print(f"Downloading graph for: {place}")
        graphml_path = download_graph(
            place,
            network_type=network_type,
            simplify=simplify,
        )
    else:
        assert graphml_path is not None  # Type narrowing for mypy
        graphml_path = Path(graphml_path)
        if not graphml_path.exists():
            raise FileNotFoundError(f"GraphML file not found: {graphml_path}")
        region = graphml_path.stem

    # Set default output directory
    if output_dir is None:
        output_dir = Path("solutions") / region
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find Rust binary
    rust_binary = _find_rust_binary()

    if not rust_binary.exists():
        raise RuntimeError(
            "Rust binary not found. Please ensure bloomr is installed correctly.\n"
            "If you're developing locally, build it first:\n"
            "  cd bloomr-rust\n"
            "  cargo build --release"
        )

    # Prepare command
    cmd = [
        str(rust_binary),
        "--graphml",
        str(graphml_path),
        "--output-dir",
        str(output_dir),
        "--region",
        region,
        "--method",
        method,
    ]

    if verbose:
        cmd.append("--verbose")

    # Run Rust solver
    print("Running Bloomr CPP solver...")
    print(f"Using graph: {graphml_path}")
    print(f"Output directory: {output_dir}")
    print()  # Blank line before Rust output

    try:
        # Run without capturing output so progress bars show in real-time
        subprocess.run(
            cmd,
            check=True,
        )

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Rust solver failed with exit code {e.returncode}") from e

    # Load results
    gpx_path = output_dir / f"{region}_cpp_route.gpx"
    metrics_path = output_dir / f"{region}_metrics.json"

    if not gpx_path.exists():
        raise RuntimeError(f"Expected GPX file not found: {gpx_path}")

    if not metrics_path.exists():
        raise RuntimeError(f"Expected metrics file not found: {metrics_path}")

    # Load metrics
    with open(metrics_path, "r") as f:
        metrics = json.load(f)

    # Generate visualization if requested
    map_path = None
    if visualize:
        try:
            from .visualize import plot_route_map

            map_path = output_dir / f"{region}_route_map.png"
            print("\nGenerating route visualization...")
            plot_route_map(
                graphml_path=graphml_path,
                gpx_path=gpx_path,
                output_path=map_path,
            )
        except ImportError:
            print(
                "\nWarning: Could not generate visualization. "
                "Install visualization dependencies with:\n"
                "  pip install 'bloomr[viz]'"
            )
        except Exception as e:
            print(f"\nWarning: Could not generate visualization: {e}")

    # Create result object
    cpp_result = CPPResult(
        graphml_path=graphml_path,
        gpx_path=gpx_path,
        metrics_path=metrics_path,
        metrics=metrics,
        region=region,
        map_path=map_path,
    )

    print("\nSolution completed successfully!")
    print(cpp_result.summary())

    return cpp_result
