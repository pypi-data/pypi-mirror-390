"""Tests for geometry module."""

from pathlib import Path

import geopandas as gpd

from civic_lib_geo.geometry import repair_geometries, validate_geometries

TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_GEOJSON = TEST_DATA_DIR / "test_invalid_geometries.geojson"


def test_repair_geometries():
    gdf = gpd.read_file(TEST_GEOJSON)
    assert not validate_geometries(gdf), "Input geometries should be invalid"

    repaired_gdf = repair_geometries(gdf)
    assert validate_geometries(repaired_gdf), "Repaired geometries should be valid"
    assert len(repaired_gdf) <= len(gdf), "Repaired GeoDataFrame should not have more rows"


def test_repair_geometries_noop():
    gdf = gpd.read_file(TEST_GEOJSON)
    repaired_gdf = repair_geometries(gdf)
    # Running repair on already valid geometries should not change them
    repaired_again_gdf = repair_geometries(repaired_gdf)
    assert repaired_gdf.equals(repaired_again_gdf), "Re-repairing should not change geometries"


def test_validate_geometries():
    gdf = gpd.read_file(TEST_GEOJSON)
    assert not validate_geometries(gdf), "Input geometries should be invalid"

    repaired_gdf = repair_geometries(gdf)
    assert validate_geometries(repaired_gdf), "Repaired geometries should be valid"
