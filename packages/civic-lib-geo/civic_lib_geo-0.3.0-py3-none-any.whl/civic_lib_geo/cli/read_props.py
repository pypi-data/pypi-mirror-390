"""read_props.py.

Command-line utility to preview feature properties in one or more GeoJSON files.

Displays the `.properties` dictionary for the first few features in each file.
Useful for inspecting available fields before cleaning, chunking, or simplifying.

Supports:
- A single file: `civic-geo read-props file.geojson`
- A folder of files: `civic-geo read-props data/ --all-files`
"""

from pathlib import Path
import sys

from civic_lib_core import log_utils

from civic_lib_geo.geojson_utils import apply_to_geojson_folder, read_geojson_props

logger = log_utils.logger


def read_props_one(path: Path, output: Path | None = None, max_rows: int = 5):
    """Print properties from the first few features in a GeoJSON file.

    Args:
        path (Path): Path to the GeoJSON file.
        output (Path | None): Ignored in this function (kept for compatibility).
        max_rows (int): Number of feature properties to preview.
    """
    try:
        props = read_geojson_props(path)
        logger.info(f"{path.name}: {len(props)} features loaded")

        for i, row in enumerate(props[:max_rows], 1):
            print(f"\nFeature {i}:")
            for key, value in row.items():
                print(f"  {key}: {value}")
        if len(props) > max_rows:
            print(f"\n... and {len(props) - max_rows} more.")
    except Exception as e:
        logger.error(f"Error reading properties from {path}: {e}")
        raise


def main(path: Path, all_files: bool = False) -> int:
    """Display feature properties for a single file or all .geojson files in a folder.

    Args:
        path (Path): File or folder path.
        all_files (bool): If True and path is a folder, process all .geojson files inside.

    Returns:
        int: 0 if success, 1 on error.
    """
    try:
        if path.is_dir():
            if not all_files:
                logger.error(
                    "Provided path is a directory. Use --all-files to process all files in it."
                )
                return 1
            apply_to_geojson_folder(
                folder=path,
                action_fn=read_props_one,
                suffix="",  # No new file written
            )
        else:
            read_props_one(path)
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python read_props.py <path> [--all-files]")
        sys.exit(1)

    sys.exit(main(Path(sys.argv[1])))
