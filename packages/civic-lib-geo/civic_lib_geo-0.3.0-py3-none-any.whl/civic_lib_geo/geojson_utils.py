"""civic_lib_geo/geojson_utils.py.

GeoJSON utility functions for Civic Interconnect.

MIT License — maintained by Civic Interconnect
"""

from collections.abc import Callable
import json
from pathlib import Path
from typing import Any

from civic_lib_core import log_utils
import geopandas as gpd

__all__ = [
    "apply_to_geojson_folder",
    "chunk_geojson_features",
    "get_file_size_mb",
    "is_valid_geojson_feature_collection",
    "list_geojson_files",
    "load_geojson",
    "needs_chunking",
    "read_geojson_props",
    "save_geojson",
    "simplify_geojson",
]


logger = log_utils.logger


def apply_to_geojson_folder(
    folder: Path,
    action_fn: Callable,
    *,
    suffix: str = "_processed.geojson",
    tolerance: float | None = None,
    max_features: int | None = None,
):
    """Apply an action to every .geojson file in a folder.

    Args:
        folder (Path): Path to folder containing .geojson files.
        action_fn (Callable): Function to apply to each file.
        suffix (str): Suffix to add to output filenames.
        tolerance (float | None): Optional tolerance value for simplification.
        max_features (int | None): Optional limit for chunking.
    """
    files = list(folder.glob("*.geojson"))
    if not files:
        logger.warning(f"No .geojson files found in {folder}")
        return

    logger.info(f"Found {len(files)} GeoJSON file(s) in {folder}")
    for file in files:
        output_path = file.with_name(file.stem + suffix)
        try:
            logger.info(f"Processing {file.name}")
            if tolerance is not None:
                action_fn(file, tolerance, output_path)
            elif max_features is not None:
                action_fn(file, max_features, output_path)
            else:
                action_fn(file, output_path)
        except Exception as e:
            logger.error(f"Failed to process {file.name}: {e}")


def chunk_geojson_features(
    geojson: dict,
    max_features: int = 500,
    output_dir: str | Path = "chunks",
    base_name: str = "chunk",
) -> list[Path]:
    """Split a GeoJSON FeatureCollection into multiple smaller files.

    Args:
        geojson: Loaded GeoJSON dictionary (must contain a 'features' list).
        max_features: Maximum number of features per chunk.
        output_dir: Directory to write chunked files to.
        base_name: Base filename prefix for each chunk.

    Returns:
        List of Paths to chunked files.

    Raises:
        ValueError: If 'features' is missing or not a list.
    """
    if "features" not in geojson or not isinstance(geojson["features"], list):
        raise ValueError("Invalid GeoJSON: missing or malformed 'features' array.")

    features = geojson["features"]
    total = len(features)
    logger.info(f"Splitting {total} features into chunks of {max_features}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    chunks_written = []
    for i in range(0, total, max_features):
        chunk = {"type": "FeatureCollection", "features": features[i : i + max_features]}
        chunk_path = output_dir / f"{base_name}_{i // max_features + 1}.geojson"
        try:
            with chunk_path.open("w", encoding="utf-8") as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)
            logger.info(f"Wrote {len(chunk['features'])} features to {chunk_path}")
            chunks_written.append(chunk_path)
        except Exception as e:
            logger.error(f"Failed to write chunk to {chunk_path}: {e}")
            raise

    return chunks_written


def get_file_size_mb(path: str | Path) -> float:
    """Return the file size in megabytes (MB).

    Args:
        path: Path to the file.

    Returns:
        File size in megabytes.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    size_mb = path.stat().st_size / (1024 * 1024)
    logger.debug(f"File size of '{path}': {size_mb:.2f} MB")
    return size_mb


def is_valid_geojson_feature_collection(obj: dict) -> bool:
    """Quick check if an object looks like a valid GeoJSON FeatureCollection.

    Args:
        obj: Dictionary to check.

    Returns:
        True if valid structure, else False.
    """
    return (
        isinstance(obj, dict)
        and obj.get("type") == "FeatureCollection"
        and isinstance(obj.get("features"), list)
    )


def list_geojson_files(folder: Path) -> list[Path]:
    """Return a list of .geojson files in the specified folder.

    Args:
        folder (Path): Directory to search.

    Returns:
        list[Path]: List of .geojson file paths.
    """
    return list(folder.glob("*.geojson"))


def load_geojson(path: Path) -> gpd.GeoDataFrame:
    """Load a GeoJSON file into a GeoDataFrame.

    Args:
        path (Path): Path to the GeoJSON file.

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame with geometries and attributes.
    """
    import geopandas as gpd

    return gpd.read_file(path)


def needs_chunking(path: str | Path, max_mb: float = 25.0) -> bool:
    """Determine whether the GeoJSON file exceeds the size threshold.

    Args:
        path: Path to the file.
        max_mb: Maximum file size before chunking is recommended.

    Returns:
        True if file exceeds max_mb, else False.
    """
    size_mb = get_file_size_mb(path)
    needs_split = size_mb > max_mb
    logger.debug(f"Needs chunking: {needs_split} (size: {size_mb:.2f} MB, limit: {max_mb} MB)")
    return needs_split


def read_geojson_props(path: Path) -> list[dict[str, Any]]:
    """Load only the properties from a GeoJSON file.

    Args:
        path (Path): Path to the GeoJSON file.

    Returns:
        list[dict[str, Any]]: A list of property dictionaries from each feature.
    """
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    return [feature["properties"] for feature in data["features"]]


def save_geojson(gdf: "gpd.GeoDataFrame", path: Path, indent: int = 2) -> Path:
    """Save a GeoDataFrame to GeoJSON format.

    Args:
        gdf (gpd.GeoDataFrame): The GeoDataFrame to save.
        path (Path): Output file path.
        indent (int): Indentation level for formatting (unused by GeoPandas but included for consistency).

    Returns:
        Path: The path to the saved file.
    """
    gdf.to_file(path, driver="GeoJSON")
    return path


def simplify_geojson(gdf: gpd.GeoDataFrame, tolerance: float) -> gpd.GeoDataFrame:
    """Return a simplified copy of the GeoDataFrame using the given tolerance.

    Args:
        gdf (gpd.GeoDataFrame): The input GeoDataFrame.
        tolerance (float): Tolerance for simplification (smaller values retain more detail).

    Returns:
        gpd.GeoDataFrame: A new GeoDataFrame with simplified geometry.
    """
    return gdf.copy().assign(geometry=gdf.geometry.simplify(tolerance, preserve_topology=True))
