"""Geographic data transformation utilities.

File: civic_lib_geo/transform.py
"""

from typing import Any, cast

import geopandas as gpd

__all__ = [
    "add_fields",
    "keep_columns",
    "normalize_columns",
    "rename_columns",
]


def add_fields(df: gpd.GeoDataFrame, add_fields: dict[str, Any]) -> gpd.GeoDataFrame:
    """Assign constant fields and keep GeoDataFrame typing."""
    if add_fields:
        for k, v in add_fields.items():
            df[k] = v
    # Explicit cast to satisfy static type checker that df remains a GeoDataFrame.
    return cast("gpd.GeoDataFrame", df)


def keep_columns(df: gpd.GeoDataFrame, keep: list[str]) -> gpd.GeoDataFrame:
    """Column subset while preserving GeoDataFrame type and geometry CRS."""
    if not keep:
        return df
    cols = [c for c in keep if c in df.columns]
    if "geometry" not in cols:
        cols.append("geometry")

    subset: Any = df.loc[:, cols]  # pandas-typed, not a GeoDataFrame
    gdf_out = gpd.GeoDataFrame(subset, geometry="geometry", crs=df.crs)
    return cast("gpd.GeoDataFrame", gdf_out)  # make the promise explicit
    # return cast(gpd.GeoDataFrame, gpd.GeoDataFrame(subset, geometry="geometry", crs=df.crs))  # type: ignore[reportReturnType]


def normalize_columns(df: gpd.GeoDataFrame, to_lower: bool, trim: bool) -> gpd.GeoDataFrame:
    """Normalize column names."""
    cols = []
    for c in df.columns:
        nc = c
        if to_lower:
            nc = nc.lower()
        if trim:
            nc = nc.strip()
        cols.append(nc)
    df.columns = cols
    return df


def rename_columns(df: gpd.GeoDataFrame, mapping: dict[str, str]) -> gpd.GeoDataFrame:
    """Rename columns while preserving GeoDataFrame type."""
    if not mapping:
        return df
    renamed = df.rename(columns=mapping)
    # Pyright: rename returns a DataFrame | GeoDataFrame; cast it back.
    return cast("gpd.GeoDataFrame", renamed)
