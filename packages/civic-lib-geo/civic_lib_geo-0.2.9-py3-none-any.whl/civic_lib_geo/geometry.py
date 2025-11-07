"""Geometry validation and repair utilities.

File: civic_lib_geo/geometry.py
"""

import geopandas as gpd
from shapely import make_valid
from shapely.geometry import MultiPolygon, Polygon

__all__ = [
    "repair_geometries",
    "validate_geometries",
]


def repair_geometries(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Repair invalid geometries in a GeoDataFrame and normalize to MultiPolygon format.

    This function performs a multi-step repair process:
    1. Applies make_valid() to invalid geometries
    2. Falls back to buffer(0) for any remaining invalid geometries
    3. Normalizes all Polygon geometries to MultiPolygon format
    4. Removes any empty geometries that may result from the repair process
    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        Input GeoDataFrame containing geometries that may be invalid

    Returns:
    -------
    gpd.GeoDataFrame
        GeoDataFrame with repaired and normalized geometries, excluding any
        empty geometries that resulted from the repair process

    Notes:
    -----
    - The function modifies geometries in-place during processing
    - All valid Polygon geometries are converted to MultiPolygon for consistency
    - Empty geometries are filtered out in the final result
    - The buffer(0) fallback is particularly effective for self-intersection issues
    """
    # Try make_valid on invalid rows only
    invalid_mask = ~gdf.geometry.is_valid
    if invalid_mask.any():
        gdf.loc[invalid_mask, "geometry"] = gdf.loc[invalid_mask, "geometry"].map(make_valid)

    # Fallback: buffer(0) for any remaining invalids (handles self-intersections)
    invalid_mask = ~gdf.geometry.is_valid
    if invalid_mask.any():
        gdf.loc[invalid_mask, "geometry"] = gdf.loc[invalid_mask, "geometry"].buffer(0)

    # Normalize to Polygon/MultiPolygon to avoid mixed types
    def _to_multi(geom):
        if geom is None or geom.is_empty:
            return geom
        if isinstance(geom, Polygon):
            return MultiPolygon([geom])
        return geom

    gdf["geometry"] = gdf.geometry.map(_to_multi)

    # Drop empties if any got nuked during repair (rare but possible)
    return gdf[~gdf.geometry.is_empty]


def validate_geometries(gdf: gpd.GeoDataFrame) -> bool:
    """Check if all geometries are valid."""
    return bool(gdf.geometry.is_valid.all())
