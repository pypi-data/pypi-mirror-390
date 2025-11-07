"""simplify_geojson.py.

Command-line utility to simplify the geometry of one or more GeoJSON files.

Reduces geometry complexity using a specified tolerance and saves the simplified output
to a new file. When given a directory with --all-files, all `.geojson` files will be processed.

Usage:
    civic-geo simplify path/to/file.geojson
    civic-geo simplify path/to/folder --all-files
"""

from pathlib import Path

from civic_lib_core import log_utils

from civic_lib_geo.geojson_utils import (
    apply_to_geojson_folder,
    load_geojson,
    save_geojson,
    simplify_geojson,
)

logger = log_utils.logger


def simplify_one(path: Path, tolerance: float, output: Path):
    """Simplify a single GeoJSON file and write the output.

    Args:
        path (Path): Path to the original GeoJSON file.
        tolerance (float): Tolerance for simplification.
        output (Path): Output path for the simplified file.
    """
    try:
        gdf = load_geojson(path)
        logger.info(f"Loaded {len(gdf)} features from {path}")
        simplified = simplify_geojson(gdf, tolerance)
        save_geojson(simplified, output)
        logger.info(f"Simplified saved to: {output}")
    except Exception as e:
        logger.error(f"Error simplifying {path}: {e}")
        raise SystemExit(1) from e


def main(
    path: Path,
    tolerance: float = 0.01,
    output: Path | None = None,
    all_files: bool = False,
):
    """Simplify a single file or all .geojson files in a folder.

    Args:
        path (Path): Input file or folder.
        tolerance (float): Simplification tolerance.
        output (Path | None): Output file path for single file use.
        all_files (bool): If True and path is a folder, simplify all .geojson files.
    """
    if path.is_dir():
        if not all_files:
            logger.error(
                "Provided path is a directory. Use --all-files to process all files in it."
            )
            raise SystemExit(1)
        apply_to_geojson_folder(
            folder=path,
            action_fn=simplify_one,
            suffix="_simplified.geojson",
            tolerance=tolerance,
        )
    else:
        out = output or path.with_name(path.stem + "_simplified.geojson")
        simplify_one(path, tolerance, out)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python simplify_geojson.py <path-to-geojson> [--all-files]")
        raise SystemExit(1)

    main(Path(sys.argv[1]))
