"""civic_lib_geo/fips_utils.py.

Utilities for working with FIPS codes.

MIT License — maintained by Civic Interconnect
"""

from pathlib import Path

import pandas as pd

__all__ = [
    "read_csv_from_path",
    "get_state_fips_df",
    "get_fips_by_state_code",
    "get_state_name_by_code",
]


def read_csv_from_path(source: Path) -> pd.DataFrame:
    """Read a CSV file from the given path and returns a DataFrame.

    Args:
        source (Path): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.
    """
    return pd.read_csv(source, dtype=str)


def get_state_fips_df(source: Path | None = None) -> pd.DataFrame:
    """Load and return a DataFrame of US state FIPS codes.

    Args:
        source (Path | None): Path to a CSV file. If None, uses the default embedded CSV.

    Returns:
        pd.DataFrame: A DataFrame with columns ['state_code', 'state_name', 'fips_code'].
    """
    if source is None:
        source = Path(__file__).parent / "data" / "us-state-fips.csv"
    df = read_csv_from_path(source)
    df.columns = [col.strip().lower() for col in df.columns]

    expected = {"state_code", "state_name", "fips_code"}
    if not expected.issubset(df.columns):
        raise ValueError(f"Missing expected columns. Found: {df.columns}")

    return df


def get_fips_by_state_code(state_code: str, source: Path | None = None) -> str:
    """Return the FIPS code for a given 2-letter state code.

    Args:
        state_code (str): A 2-letter state abbreviation (e.g., 'MN').
        source (Path | None): Optional override path to a custom CSV file.

    Returns:
        str: Corresponding FIPS code (e.g., '27').

    Raises:
        ValueError: If the state code is not found.
    """
    df = get_state_fips_df(source)
    result = df[df["state_code"].str.upper() == state_code.upper()]
    if result.empty:
        raise ValueError(f"State code '{state_code}' not found in FIPS data.")
    return result.iloc[0]["fips_code"]


def get_state_name_by_code(state_code: str, source: Path | None = None) -> str:
    """Return the full state name for a given 2-letter state code.

    Args:
        state_code (str): A 2-letter state abbreviation.
        source (Path | None): Optional override path to a custom CSV file.

    Returns:
        str: Full state name (e.g., 'Minnesota').

    Raises:
        ValueError: If the state code is not found.
    """
    df = get_state_fips_df(source)
    result = df[df["state_code"].str.upper() == state_code.upper()]
    if result.empty:
        raise ValueError(f"State code '{state_code}' not found in FIPS data.")
    return result.iloc[0]["state_name"]
