"""civic_lib_geo/shapefile_utils.py.

Shapefile utility functions for Civic Interconnect.

MIT License — maintained by Civic Interconnect
"""

from pathlib import Path

from civic_lib_core import log_utils
import geopandas as gpd

__all__ = [
    "convert_shapefile_to_geojson",
    "load_shapefile",
]
logger = log_utils.logger


def convert_shapefile_to_geojson(shp_path: Path, geojson_path: Path) -> Path:
    """Convert a shapefile to a GeoJSON file.

    Args:
        shp_path (Path): Path to the source shapefile (.shp).
        geojson_path (Path): Path to the output GeoJSON file.

    Returns:
        Path: The path to the saved GeoJSON file.
    """
    gdf = load_shapefile(shp_path)
    gdf.to_file(geojson_path, driver="GeoJSON")
    return geojson_path


def load_shapefile(path: Path) -> gpd.GeoDataFrame:
    """Load a shapefile into a GeoDataFrame.

    Args:
        path (Path): Path to the shapefile (.shp).

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with geometries and attributes.
    """
    return gpd.read_file(path)
