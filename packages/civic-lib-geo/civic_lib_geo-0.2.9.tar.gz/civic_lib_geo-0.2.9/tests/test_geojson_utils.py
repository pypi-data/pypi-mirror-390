"""
tests/test_geojson_utils.py
Test suite for GeoJSON utility functions in civic_lib_geo.geojson_utils.
"""

from pathlib import Path

import geopandas as gpd
import pytest

from civic_lib_geo.geojson_utils import (
    load_geojson,
    read_geojson_props,
    simplify_geojson,
)

TEST_DATA = Path(__file__).parent / "data" / "test.geojson"
CHUNK_DIR = Path(__file__).parent / "temp_chunks"


def test_load_geojson():
    gdf = load_geojson(TEST_DATA)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty


def test_read_geojson_props():
    props = read_geojson_props(TEST_DATA)
    assert isinstance(props, list)
    assert isinstance(props[0], dict)


def test_simplify_geojson():
    gdf = load_geojson(TEST_DATA)
    simplified = simplify_geojson(gdf, tolerance=0.01)
    assert isinstance(simplified, gpd.GeoDataFrame)
    assert len(simplified) == len(gdf)


def test_load_geojson_invalid_path():
    with pytest.raises(Exception) as exc:
        load_geojson(Path("nonexistent.geojson"))
    assert "No such file or directory" in str(exc.value)


def test_simplify_changes_geometry():
    gdf = load_geojson(TEST_DATA)
    simplified = simplify_geojson(gdf, tolerance=0.1)
    # Should still match original row count
    assert len(simplified) == len(gdf)
    # Geometry should differ (not always, but often)
    assert not gdf.geometry.equals(simplified.geometry)


def test_read_props_has_expected_keys():
    props = read_geojson_props(TEST_DATA)
    assert isinstance(props, list)
    assert isinstance(props[0], dict)
    # Example: Check for presence of a known key
    assert "name" in props[0] or "NAME" in props[0]  # Adjust as needed


def test_save_and_reload(tmp_path):
    gdf = load_geojson(TEST_DATA)
    out_path = tmp_path / "out.geojson"
    gdf.to_file(out_path, driver="GeoJSON")

    gdf2 = load_geojson(out_path)
    assert len(gdf2) == len(gdf)


def test_simplify_with_zero_tolerance():
    gdf = load_geojson(TEST_DATA)
    simplified = simplify_geojson(gdf, tolerance=0.0)
    assert gdf.geometry.equals(simplified.geometry)
