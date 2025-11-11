"""
Visualization utilities for CPP solutions.

This module provides functions to visualize CPP routes on maps.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

import networkx as nx


def plot_route_map(
    graphml_path: Path,
    gpx_path: Path,
    output_path: Path,
    *,
    figsize: Tuple[int, int] = (15, 15),
    show_basemap: bool = True,
    route_color: str = "#FF0000",
    route_alpha: float = 0.6,
    route_width: float = 1.5,
    network_color: str = "#CCCCCC",
    network_alpha: float = 0.3,
    network_width: float = 0.5,
    dpi: int = 150,
) -> Path:
    """
    Create a map visualization of the CPP route.

    This function reads the GraphML road network and GPX route file,
    then creates a visualization showing the route overlaid on the road network
    with an optional basemap.

    Args:
        graphml_path: Path to the GraphML file containing the road network
        gpx_path: Path to the GPX file containing the route
        output_path: Path where the PNG image will be saved
        figsize: Figure size in inches (width, height)
        show_basemap: Whether to show a basemap (requires contextily)
        route_color: Color for the route line
        route_alpha: Transparency of the route line (0-1)
        route_width: Width of the route line
        network_color: Color for the underlying road network
        network_alpha: Transparency of the road network (0-1)
        network_width: Width of the road network lines
        dpi: Dots per inch for the output image

    Returns:
        Path to the saved PNG file

    Raises:
        ImportError: If required visualization dependencies are not installed
        FileNotFoundError: If input files don't exist

    Examples:
        >>> from bloomr.visualize import plot_route_map
        >>> from pathlib import Path
        >>>
        >>> plot_route_map(
        ...     graphml_path=Path("graphml_data/jersey.graphml"),
        ...     gpx_path=Path("solutions/jersey/jersey_cpp_route.gpx"),
        ...     output_path=Path("solutions/jersey/jersey_route_map.png"),
        ... )
    """
    try:
        import matplotlib.patches as mpatches
        import matplotlib.pyplot as plt
    except ImportError as e:
        raise ImportError(
            "Visualization requires matplotlib. Install with:\n" "  pip install 'bloomr[viz]'"
        ) from e

    if show_basemap:
        try:
            import contextily as ctx
        except ImportError as e:
            raise ImportError(
                "Basemap visualization requires contextily. Install with:\n"
                "  pip install 'bloomr[viz]'"
            ) from e

    # Verify input files exist
    if not graphml_path.exists():
        raise FileNotFoundError(f"GraphML file not found: {graphml_path}")
    if not gpx_path.exists():
        raise FileNotFoundError(f"GPX file not found: {gpx_path}")

    # Load the road network
    print(f"Loading road network from {graphml_path.name}...")
    G = nx.read_graphml(graphml_path)

    # Extract coordinates from the graph
    node_positions = {}
    for node, data in G.nodes(data=True):
        try:
            lon = float(data.get("x", data.get("d4", 0)))
            lat = float(data.get("y", data.get("d3", 0)))
            node_positions[node] = (lon, lat)
        except (ValueError, TypeError):
            continue

    # Parse GPX file to get route coordinates
    print(f"Loading route from {gpx_path.name}...")
    route_coords = _parse_gpx(gpx_path)

    if not route_coords:
        raise ValueError(f"No route coordinates found in GPX file: {gpx_path}")

    print(f"Creating visualization with {len(route_coords)} route points...")

    # Create figure
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)

    # Plot road network edges
    for u, v in G.edges():
        if u in node_positions and v in node_positions:
            x_coords = [node_positions[u][0], node_positions[v][0]]
            y_coords = [node_positions[u][1], node_positions[v][1]]
            ax.plot(
                x_coords,
                y_coords,
                color=network_color,
                alpha=network_alpha,
                linewidth=network_width,
                zorder=1,
            )

    # Plot route
    route_lons = [coord[0] for coord in route_coords]
    route_lats = [coord[1] for coord in route_coords]
    ax.plot(
        route_lons,
        route_lats,
        color=route_color,
        alpha=route_alpha,
        linewidth=route_width,
        zorder=2,
        label="CPP Route",
    )

    # Mark start/end points
    if route_coords:
        start = route_coords[0]
        end = route_coords[-1]
        ax.plot(start[0], start[1], "go", markersize=10, zorder=3, label="Start")
        ax.plot(end[0], end[1], "rs", markersize=10, zorder=3, label="End")

    # Add basemap if requested
    if show_basemap:
        try:
            print("Adding basemap (this may take a moment)...")
            ctx.add_basemap(
                ax,
                crs="EPSG:4326",
                source=ctx.providers.CartoDB.Positron,
                attribution=False,
            )
        except Exception as e:
            print(f"Warning: Could not add basemap: {e}")
            print("Continuing without basemap...")

    # Set labels and title
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.set_title("Chinese Postman Problem Solution", fontsize=16, fontweight="bold")

    # Add legend
    legend_elements = [
        mpatches.Patch(color=route_color, alpha=route_alpha, label="CPP Route"),
        mpatches.Patch(color=network_color, alpha=network_alpha, label="Road Network"),
        plt.Line2D(
            [0], [0], marker="o", color="w", markerfacecolor="g", markersize=8, label="Start"
        ),
        plt.Line2D([0], [0], marker="s", color="w", markerfacecolor="r", markersize=8, label="End"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)

    # Adjust layout and save
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Saving map to {output_path}...")
    plt.savefig(output_path, dpi=dpi, bbox_inches="tight")
    plt.close()

    print(f"Map saved successfully: {output_path}")
    return output_path


def _parse_gpx(gpx_path: Path) -> List[Tuple[float, float]]:
    """
    Parse GPX file and extract route coordinates.

    Args:
        gpx_path: Path to GPX file

    Returns:
        List of (lon, lat) tuples
    """
    # GPX files are generated by our own Rust backend, not untrusted external sources
    tree = ET.parse(gpx_path)  # nosec B314
    root = tree.getroot()

    # GPX namespace
    ns = {"gpx": "http://www.topografix.com/GPX/1/1"}

    coords = []

    # Try to find track points
    for trkpt in root.findall(".//gpx:trkpt", ns):
        lat_str = trkpt.get("lat")
        lon_str = trkpt.get("lon")
        if lat_str is not None and lon_str is not None:
            lat = float(lat_str)
            lon = float(lon_str)
            coords.append((lon, lat))

    # If no track points, try route points
    if not coords:
        for rtept in root.findall(".//gpx:rtept", ns):
            lat_str = rtept.get("lat")
            lon_str = rtept.get("lon")
            if lat_str is not None and lon_str is not None:
                lat = float(lat_str)
                lon = float(lon_str)
                coords.append((lon, lat))

    # If still no points, try waypoints
    if not coords:
        for wpt in root.findall(".//gpx:wpt", ns):
            lat_str = wpt.get("lat")
            lon_str = wpt.get("lon")
            if lat_str is not None and lon_str is not None:
                lat = float(lat_str)
                lon = float(lon_str)
                coords.append((lon, lat))

    return coords
