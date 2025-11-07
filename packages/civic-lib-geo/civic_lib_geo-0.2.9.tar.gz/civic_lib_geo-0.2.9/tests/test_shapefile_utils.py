"""tests/test_shapefile_utils.py

Test suite for shapefile utility functions in civic_lib_geo.shapefile_utils.
"""

from pathlib import Path

import geopandas as gpd

from civic_lib_geo.shapefile_utils import (
    convert_shapefile_to_geojson,
    load_shapefile,
)

TEST_SHP = Path(__file__).parent / "data" / "test_shapefile.shp"
OUTPUT_GEOJSON = Path(__file__).parent / "output.geojson"


def test_load_shapefile():
    gdf = load_shapefile(TEST_SHP)
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty


def test_convert_shapefile_to_geojson(tmp_path):
    output_path = tmp_path / "converted.geojson"
    result_path = convert_shapefile_to_geojson(TEST_SHP, output_path)
    assert result_path.exists()
    assert result_path.suffix == ".geojson"
