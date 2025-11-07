"""shapefile_to_geojson.py.

Command-line utility to convert a shapefile to GeoJSON.

Used by:
    civic-geo shapefile-to-geojson SHAPEFILE_PATH GEOJSON_PATH
"""

from pathlib import Path
import sys

from civic_lib_core import log_utils

from civic_lib_geo import shapefile_utils

logger = log_utils.logger


def main(shp_path: Path, geojson_path: Path) -> int:
    """Convert a shapefile to GeoJSON.

    Args:
        shp_path (Path): Input .shp file path.
        geojson_path (Path): Output .geojson file path.

    Returns:
        int: 0 if success, 1 on error.
    """
    try:
        shapefile_utils.convert_shapefile_to_geojson(shp_path, geojson_path)
        logger.info(f"Converted {shp_path} to {geojson_path}")
        return 0
    except Exception as e:
        logger.error(f"Error converting shapefile: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python shapefile_to_geojson.py input.shp output.geojson")
        sys.exit(1)

    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
