"""check_size.py.

Check the size of a GeoJSON file and whether it exceeds GitHub Pages limits.

Used by civic-geo CLI:
    civic-geo check-size <path>
"""

from pathlib import Path
import sys

from civic_lib_core import log_utils

from civic_lib_geo.geojson_utils import get_file_size_mb, needs_chunking

logger = log_utils.logger


def main(path: Path) -> int:
    """Print the size of a GeoJSON file and whether it exceeds GitHub Pages limits.

    Args:
        path (Path): Path to the GeoJSON file to inspect.

    Returns:
        int: 0 if OK, 1 if an error occurs.
    """
    try:
        path = Path(path)  # Defensive cast
        size_mb = get_file_size_mb(path)
        logger.info(f"File size: {size_mb:.2f} MB")

        if needs_chunking(path):
            logger.warning("File exceeds 25MB GitHub Pages limit. Consider chunking.")
        else:
            logger.info("File is within acceptable size limits.")
        return 0
    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_size.py <path-to-geojson>")
        sys.exit(1)

    sys.exit(main(Path(sys.argv[1])))
