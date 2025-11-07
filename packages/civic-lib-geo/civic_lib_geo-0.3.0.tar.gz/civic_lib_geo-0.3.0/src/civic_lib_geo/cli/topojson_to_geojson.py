"""topojson_to_geojson.py.

Command-line utility to convert a TopoJSON file to GeoJSON.

Used by:
    civic-geo topojson-to-geojson TOPOJSON_PATH GEOJSON_PATH
"""

from pathlib import Path
import sys

from civic_lib_core import log_utils

logger = log_utils.logger


def main(topo_path: Path, geojson_path: Path) -> int:
    """Convert a TopoJSON file to GeoJSON using GeoPandas (if supported).

    Args:
        topo_path (Path): Input .topojson file path.
        geojson_path (Path): Output .geojson file path.

    Returns:
        int: 0 if success, 1 if failure.
    """
    try:
        import geopandas as gpd

        gdf = gpd.read_file(topo_path)
        gdf.to_file(geojson_path, driver="GeoJSON")
        logger.info(f"Converted {topo_path} to {geojson_path}")
        return 0
    except Exception as e:
        logger.error(f"TopoJSON conversion failed: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python topojson_to_geojson.py input.topojson output.geojson")
        sys.exit(1)

    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
