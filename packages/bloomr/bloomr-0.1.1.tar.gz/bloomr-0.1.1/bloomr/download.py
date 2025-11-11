"""
Graph downloading functionality using OSMnx.

This module provides functions to download road network data from OpenStreetMap
and save it as GraphML files for use with the Bloomr CPP solver.
"""

from pathlib import Path
from typing import Optional, Union

try:
    import osmnx as ox
except ImportError as e:
    raise ImportError(
        "OSMnx is required for downloading graphs. " "Install with: pip install bloomr"
    ) from e


def sanitize_filename(name: str) -> str:
    """
    Convert a place name to a valid filename.

    Args:
        name: Place name (e.g., "Jersey, Channel Islands")

    Returns:
        Sanitized filename (e.g., "jersey_channel_islands")
    """
    return name.lower().replace(" ", "_").replace(",", "").replace("/", "_")


def download_graph(
    place: str,
    *,
    output_dir: Optional[Union[Path, str]] = None,
    network_type: str = "drive_service",
    simplify: bool = False,
    force: bool = False,
) -> Path:
    """
    Download road network from OpenStreetMap and save as GraphML.

    This function downloads a road network for a specified place using OSMnx,
    adds edge speeds and travel times, and saves it as a GraphML file that
    can be used with the Bloomr CPP solver.

    Args:
        place: OSMnx place query (e.g., "Jersey, Channel Islands",
               "San Francisco, California")
        output_dir: Output directory for GraphML file. Defaults to "graphml_data"
        network_type: Type of network to download. Options:
                     - "drive": Car-navigable roads
                     - "drive_service": Drive + service roads (default)
                     - "walk": Walkable paths
                     - "bike": Bikeable paths
                     - "all": All streets and paths
        simplify: Whether to simplify the graph by merging nodes and removing
                 interstitial nodes. Default False.
        force: Force re-download even if file exists. Default False.

    Returns:
        Path to the saved GraphML file

    Raises:
        ValueError: If the place cannot be found or network_type is invalid
        RuntimeError: If the download or save operation fails

    Example:
        >>> from bloomr import download_graph
        >>> graph_path = download_graph("Jersey, Channel Islands")
        >>> print(graph_path)
        graphml_data/jersey_channel_islands.graphml
    """
    # Set default output directory
    if output_dir is None:
        output_dir = Path("graphml_data")
    else:
        output_dir = Path(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename
    filename = sanitize_filename(place)
    graphml_path = output_dir / f"{filename}.graphml"

    # Check if file exists
    if graphml_path.exists() and not force:
        print(f"GraphML file already exists: {graphml_path}")
        print("Use force=True to re-download")
        return graphml_path

    # Configure OSMnx
    ox.settings.use_cache = True
    ox.settings.log_console = False

    print(f"Downloading road network for: {place}")
    print(f"Network type: {network_type}")
    print("This may take several minutes for large regions...")

    try:
        # Download graph from OpenStreetMap
        G = ox.graph_from_place(place, network_type=network_type, simplify=simplify)

        print(f"Downloaded: {len(G.nodes)} nodes, {len(G.edges)} edges")

        # Add speeds and travel times to edges
        print("Adding edge speeds and travel times...")
        G = ox.add_edge_speeds(G)
        G = ox.add_edge_travel_times(G)

        # Save to GraphML format
        print(f"Saving to: {graphml_path}")
        ox.save_graphml(G, filepath=graphml_path)

        print(f"Successfully saved GraphML file: {graphml_path}")
        return graphml_path

    except Exception as e:
        raise RuntimeError(f"Failed to download or save graph: {e}") from e
