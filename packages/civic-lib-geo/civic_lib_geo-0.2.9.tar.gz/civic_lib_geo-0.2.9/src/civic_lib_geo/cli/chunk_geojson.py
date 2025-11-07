"""chunk_geojson.py.

Utility to split a GeoJSON FeatureCollection into smaller files.

Used by civic-geo CLI:
    civic-geo chunk path/to/file.geojson --max-features 500
    civic-geo chunk path/to/folder --all-files
"""

import json
from pathlib import Path
import sys

from civic_lib_core import log_utils

from civic_lib_geo.geojson_utils import apply_to_geojson_folder, chunk_geojson_features

logger = log_utils.logger


def chunk_one(path: Path, max_features: int, output_dir: Path):
    """Chunk a single GeoJSON file and write the output files.

    Args:
        path (Path): Path to input GeoJSON file.
        max_features (int): Max features per chunk.
        output_dir (Path): Output folder to store chunks.
    """
    try:
        geojson_dict = json.loads(path.read_text(encoding="utf-8"))
        chunk_paths = chunk_geojson_features(
            geojson=geojson_dict,
            max_features=max_features,
            output_dir=output_dir,
            base_name=path.stem + "_chunk",
        )
        logger.info(f"Wrote {len(chunk_paths)} chunks to {output_dir}")
    except Exception as e:
        logger.error(f"Error chunking {path}: {e}")
        raise


def main(
    path: Path,
    max_features: int = 500,
    output_dir: Path = Path("chunks"),
    all_files: bool = False,
) -> int:
    """Chunk a single file or all .geojson files in a folder.

    Args:
        path (Path): Input file or folder path.
        max_features (int): Max features per chunk.
        output_dir (Path): Directory to store chunks.
        all_files (bool): If True and path is a folder, chunk all files in it.

    Returns:
        int: Exit code, 0 if success, 1 if failure.
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
                action_fn=chunk_one,
                suffix="_chunked.geojson",
                max_features=max_features,
            )
        else:
            chunk_one(path, max_features, output_dir)

        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chunk_geojson.py <path> [--all-files]")
        sys.exit(1)

    sys.exit(main(Path(sys.argv[1])))
