"""Test that the package can be imported."""

import pytest


def test_import_bloomr():
    """Test that bloomr package can be imported."""
    import bloomr

    assert bloomr is not None


def test_import_main_functions():
    """Test that main functions can be imported."""
    from bloomr import download_graph, sanitize_filename, solve_cpp, CPPResult

    assert solve_cpp is not None
    assert download_graph is not None
    assert sanitize_filename is not None
    assert CPPResult is not None


def test_sanitize_filename():
    """Test the sanitize_filename function."""
    from bloomr import sanitize_filename

    # Test basic sanitization (function converts to lowercase)
    assert sanitize_filename("Jersey, Channel Islands") == "jersey_channel_islands"
    assert sanitize_filename("San Francisco, CA") == "san_francisco_ca"

    # Test special characters (only handles: lowercase, spaces->_, remove commas, /-_)
    assert sanitize_filename("Test/Path") == "test_path"  # Forward slash
    assert sanitize_filename("With, Comma") == "with_comma"  # Comma removal

    # Test spaces
    assert sanitize_filename("Multiple   Spaces") == "multiple___spaces"


def test_cpp_result_structure():
    """Test CPPResult dataclass structure."""
    from bloomr import CPPResult
    from pathlib import Path

    # Test that CPPResult has expected attributes
    result = CPPResult(
        graphml_path=Path("test.graphml"),
        gpx_path=Path("test.gpx"),
        metrics_path=Path("test_metrics.json"),
        metrics={"test": 1.0},
        region="test_region",
        map_path=None,
    )

    assert result.graphml_path == Path("test.graphml")
    assert result.gpx_path == Path("test.gpx")
    assert result.metrics_path == Path("test_metrics.json")
    assert result.metrics == {"test": 1.0}
    assert result.region == "test_region"
    assert result.map_path is None


def test_cpp_result_summary():
    """Test CPPResult summary method."""
    from bloomr import CPPResult
    from pathlib import Path

    result = CPPResult(
        graphml_path=Path("test.graphml"),
        gpx_path=Path("test.gpx"),
        metrics_path=Path("test_metrics.json"),
        metrics={
            "unique_road_segments": 80,
            "bidirectional_edge_pairs": 60,
            "one_way_edges": 20,
            "base_graph_edges": 140,
            "circuit_length": 120,
            "total_original_distance_km": 10.5,
            "total_circuit_distance_km": 12.0,
            "distance_efficiency": 0.875,
            "time_efficiency": 0.90,
            "duplication_ratio": 1.5,
            "deadhead_percentage": 14.3,
        },
        region="test_region",
        map_path=None,
    )

    summary = result.summary()
    assert isinstance(summary, str)
    assert "test_region" in summary
    assert "10.5" in summary  # total original distance
    assert "12.0" in summary  # circuit distance
    assert "87.5%" in summary  # distance efficiency
    assert "1.5000" in summary  # duplication ratio


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
