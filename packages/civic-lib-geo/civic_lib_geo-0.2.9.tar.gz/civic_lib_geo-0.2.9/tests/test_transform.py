# Test cases for the transform module

"""Test suite for transform functions in civic_lib_geo.transform."""

from pathlib import Path

import geopandas as gpd

from civic_lib_geo.transform import add_fields, keep_columns, normalize_columns, rename_columns

TEST_DATA_DIR = Path(__file__).parent / "data"
TEST_GEOJSON = TEST_DATA_DIR / "test.geojson"


def test_add_fields():
    gdf = gpd.read_file(TEST_GEOJSON)
    constants = {"country": "USA", "source": "test_data"}
    gdf_with_constants = add_fields(gdf, constants)

    for key, value in constants.items():
        assert key in gdf_with_constants.columns
        assert all(gdf_with_constants[key] == value)


def test_keep_columns():
    gdf = gpd.read_file(TEST_GEOJSON)
    columns_to_keep = ["name", "geometry"]
    gdf_subset = keep_columns(gdf, columns_to_keep)

    assert set(gdf_subset.columns) == set(columns_to_keep)
    assert isinstance(gdf_subset, gpd.GeoDataFrame)
    assert gdf_subset.geometry.crs == gdf.geometry.crs  # CRS should be preserved


def test_normalize_columns():
    gdf = gpd.read_file(TEST_GEOJSON)
    gdf_normalized = normalize_columns(gdf, to_lower=True, trim=True)

    for col in gdf_normalized.columns:
        assert col == col.lower()
        assert col == col.strip()


def test_rename_columns():
    gdf = gpd.read_file(TEST_GEOJSON)
    rename_map = {"name": "place_name", "type": "place_type"}
    gdf_renamed = rename_columns(gdf, rename_map)

    for old_name, new_name in rename_map.items():
        assert new_name in gdf_renamed.columns
        assert old_name not in gdf_renamed.columns
    assert isinstance(gdf_renamed, gpd.GeoDataFrame)
