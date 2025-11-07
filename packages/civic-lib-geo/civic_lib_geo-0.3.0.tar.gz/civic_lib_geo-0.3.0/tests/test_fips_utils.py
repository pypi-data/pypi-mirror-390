"""tests/test_fips_utils.py

Test suite for FIPS utility functions in civic_lib_geo.fips_utils.
"""

from pathlib import Path

import pandas as pd
import pytest

from civic_lib_geo.fips_utils import (
    get_fips_by_state_code,
    get_state_fips_df,
    get_state_name_by_code,
    read_csv_from_path,
)


@pytest.fixture
def mock_fips_csv(tmp_path) -> Path:
    content = "state_code,state_name,fips_code\nMN,Minnesota,27\nCA,California,06\nTX,Texas,48\n"
    f = tmp_path / "mock-fips.csv"
    f.write_text(content)
    return f


def test_read_csv_from_path(mock_fips_csv):
    df = read_csv_from_path(mock_fips_csv)
    assert isinstance(df, pd.DataFrame)
    assert "state_code" in df.columns
    assert len(df) == 3


def test_get_state_fips_df(mock_fips_csv):
    df = get_state_fips_df(mock_fips_csv)
    assert "state_code" in df.columns
    assert "state_name" in df.columns
    assert "fips_code" in df.columns
    assert df.loc[df["state_code"] == "MN", "fips_code"].values[0] == "27"


def test_get_fips_by_state_code(mock_fips_csv):
    fips = get_fips_by_state_code("CA", source=mock_fips_csv)
    assert fips == "06"

    with pytest.raises(ValueError):
        get_fips_by_state_code("XX", source=mock_fips_csv)


def test_get_state_name_by_code(mock_fips_csv):
    name = get_state_name_by_code("TX", source=mock_fips_csv)
    assert name == "Texas"

    with pytest.raises(ValueError):
        get_state_name_by_code("ZZ", source=mock_fips_csv)
