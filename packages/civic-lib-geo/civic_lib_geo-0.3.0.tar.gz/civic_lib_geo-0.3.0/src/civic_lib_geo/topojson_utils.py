"""civic_lib_geo/topojson_utils.py.

TopoJSON utility functions for Civic Interconnect.

MIT License — maintained by Civic Interconnect
"""

from pathlib import Path

from civic_lib_core import log_utils
import geopandas as gpd

__all__ = [
    "convert_topojson_to_geojson",
]

logger = log_utils.logger


def convert_topojson_to_geojson(topojson_path: Path, geojson_path: Path) -> Path:
    """Convert a TopoJSON file to a GeoJSON file using geopandas or CLI tools."""
    gdf = gpd.read_file(topojson_path)
    gdf.to_file(geojson_path, driver="GeoJSON")
    return geojson_path
